"""Atos de encerramento e cancelamento: explícitos, motivados, auditados e sem exclusão.

Nenhum ato propaga desfecho automaticamente. Cancelar o Processo exige que cada Edital já
esteja Encerrado ou Cancelado por ato próprio (FR-034).
"""

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.processos.domain import finalizacao
from processo_seletivo.processos.models import AtoAdministrativo, Edital, ProcessoSeletivo
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.concurrency import compare_and_swap
from processo_seletivo.shared.idempotency import finish as _finish_idempotency
from processo_seletivo.shared.idempotency import reserve


def _not_found():
    return DomainError("not_found", "Recurso não encontrado.", 404)


def _lock_processo(actor, processo_id):
    try:
        return ProcessoSeletivo.objects.select_for_update().get(
            pk=processo_id, institution_scope=actor.institution_scope
        )
    except ProcessoSeletivo.DoesNotExist as exc:
        raise _not_found() from exc


def _lock_edital(actor, edital_id):
    try:
        return Edital.objects.select_for_update().get(
            pk=edital_id, institution_scope=actor.institution_scope
        )
    except Edital.DoesNotExist as exc:
        raise _not_found() from exc


def _lock_edital_sob_o_processo(actor, edital_id):
    """Trava o Processo e, depois, o Edital — a ordem de `close_process` (113, R-004).

    **Por que o Processo.** Os atos que criam ou resolvem o que impede encerrar — interpor, admitir
    e julgar recurso, publicar resultado, convocar — se serializam na linha do Processo; os da
    Retificação travam Retificação, Edital e Processo juntos; o envio de inscrição espera pelo
    Edital. Travando os dois, a conferência dos impedimentos vê tudo o que confirmou antes, e o
    que vier depois espera o encerramento terminar (FR-3543). Nenhuma trava nova.

    O `processo_id` é lido sem trava porque a trava do Processo precisa dele. Nenhum caminho da
    aplicação troca o Processo de um Edital, mas nenhum gatilho o prende; por isso ele é relido
    sob a trava, e a divergência é recusada em vez de conferida contra o Processo errado.
    """
    processo_id = (
        Edital.objects.filter(pk=edital_id, institution_scope=actor.institution_scope)
        .values_list("processo_id", flat=True)
        .first()
    )
    if processo_id is None:
        raise _not_found()
    ProcessoSeletivo.objects.select_for_update().filter(pk=processo_id).first()
    edital = _lock_edital(actor, edital_id)
    if edital.processo_id != processo_id:
        raise DomainError(
            "invalid_state", "O Edital mudou de Processo durante o ato. Tente de novo.", 409
        )
    return edital


def _register(
    *,
    actor,
    aggregate,
    operation,
    permission,
    reason,
    previous,
    now,
    correlation_id,
    idempotency_key,
):
    AtoAdministrativo.objects.create(
        aggregate_type=aggregate.__class__.__name__,
        aggregate_id=aggregate.pk,
        operation=operation,
        actor_subject=actor.subject,
        reason=reason,
        occurred_at=now,
    )
    record_event(
        actor=actor,
        permission=permission,
        operation=operation,
        aggregate=aggregate,
        now=now,
        correlation_id=correlation_id,
        reason=reason,
        previous_state=previous.status,
        previous_revision=previous.revision,
        idempotency_key=idempotency_key,
    )


class _Previous:
    def __init__(self, aggregate):
        self.status = aggregate.status
        self.revision = aggregate.revision


def _finalize_processo(
    *,
    actor,
    processo_id,
    expected_revision,
    reason,
    idempotency_key,
    correlation_id,
    permission,
    operation,
    target_status,
    check,
):
    require_permission(actor, permission)
    with command_context() as now:
        processo = _lock_processo(actor, processo_id)
        idem = reserve(
            actor=actor,
            operation=f"{permission}:{processo_id}",
            key=idempotency_key,
            payload={"reason": reason},
        )
        if idem.result_id:
            return ProcessoSeletivo.objects.get(pk=idem.result_id), idem.response_status
        check(processo)
        previous = _Previous(processo)
        compare_and_swap(
            ProcessoSeletivo.objects,
            pk=processo.pk,
            expected_revision=expected_revision,
            status=target_status,
            last_changed_at=now,
        )
        processo.refresh_from_db()
        _register(
            actor=actor,
            aggregate=processo,
            operation=operation,
            permission=permission,
            reason=reason,
            previous=previous,
            now=now,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        _finish_idempotency(idem, processo, 200)
        return processo, 200


def _editais_pendentes_travados(processo):
    """Os Editais fora de estado final, travados, na ordem em que a recusa os nomeia.

    Locks em ordem estável de id evitam deadlock e fecham a janela TOCTOU entre a verificação dos
    Editais pendentes e a gravação do desfecho.
    """
    pendentes = list(
        processo.editais.select_for_update()
        .exclude(status__in=finalizacao.EDITAL_FINAL)
        .order_by("id")
    )
    pendentes.sort(key=lambda edital: (edital.year, edital.number, str(edital.id)))
    return pendentes


def close_process(
    *, actor, processo_id, expected_revision, reason, idempotency_key, correlation_id
):
    """Encerrar exige os Editais em estado final, como cancelar (RC-118, decisão de 28/09)."""

    def check(processo):
        finalizacao.ensure_processo_can_be_closed(processo, _editais_pendentes_travados(processo))

    return _finalize_processo(
        actor=actor,
        processo_id=processo_id,
        expected_revision=expected_revision,
        reason=reason,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        permission="processo:encerrar",
        operation="ENCERRAR",
        target_status=ProcessoSeletivo.Status.ENCERRADO,
        check=check,
    )


def cancel_process(
    *, actor, processo_id, expected_revision, reason, idempotency_key, correlation_id
):
    """Bloqueia o cancelamento sob concorrência travando o Processo e depois seus Editais."""

    def check(processo):
        finalizacao.ensure_processo_can_be_cancelled(
            processo, _editais_pendentes_travados(processo)
        )

    return _finalize_processo(
        actor=actor,
        processo_id=processo_id,
        expected_revision=expected_revision,
        reason=reason,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        permission="processo:cancelar",
        operation="CANCELAR",
        target_status=ProcessoSeletivo.Status.CANCELADO,
        check=check,
    )


def _finalize_edital(
    *,
    actor,
    edital_id,
    expected_revision,
    reason,
    idempotency_key,
    correlation_id,
    permission,
    operation,
    target_status,
    check,
):
    require_permission(actor, permission)
    with command_context() as now:
        edital = _lock_edital_sob_o_processo(actor, edital_id)
        idem = reserve(
            actor=actor,
            operation=f"{permission}:{edital_id}",
            key=idempotency_key,
            payload={"reason": reason},
        )
        if idem.result_id:
            return Edital.objects.get(pk=idem.result_id), idem.response_status
        finalizacao.ensure_processo_accepts_changes(edital.processo)
        check(edital, now)
        previous = _Previous(edital)
        compare_and_swap(
            Edital.objects,
            pk=edital.pk,
            expected_revision=expected_revision,
            status=target_status,
            last_edited_by=actor.subject,
        )
        edital.refresh_from_db()
        _register(
            actor=actor,
            aggregate=edital,
            operation=operation,
            permission=permission,
            reason=reason,
            previous=previous,
            now=now,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        _finish_idempotency(idem, edital, 200)
        return edital, 200


def close_edital(*, actor, edital_id, expected_revision, reason, idempotency_key, correlation_id):
    return _finalize_edital(
        actor=actor,
        edital_id=edital_id,
        expected_revision=expected_revision,
        reason=reason,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        permission="edital:encerrar",
        operation="ENCERRAR",
        target_status=Edital.Status.ENCERRADO,
        check=_conferir_o_encerramento,
    )


def _conferir_o_encerramento(edital, agora):
    """O estado primeiro; os impedimentos só de Edital publicado, sob as travas (113, FR-3528).

    Conferir o estado antes evita ler o conteúdo vigente de um Edital que nem poderia ser
    encerrado — e que, antes da publicação, nem tem conteúdo vigente.
    """
    from processo_seletivo.processos.application import pendencias_do_edital

    impedimentos = ()
    if edital.status in finalizacao.EDITAL_ENCERRAVEL:
        impedimentos = [
            pendencias_do_edital.frase(situacao)
            for situacao in pendencias_do_edital.impedimentos(edital, agora=agora)
        ]
    finalizacao.ensure_edital_can_be_closed(edital, impedimentos)


def cancel_edital(*, actor, edital_id, expected_revision, reason, idempotency_key, correlation_id):
    return _finalize_edital(
        actor=actor,
        edital_id=edital_id,
        expected_revision=expected_revision,
        reason=reason,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        permission="edital:cancelar",
        operation="CANCELAR",
        target_status=Edital.Status.CANCELADO,
        check=lambda edital, _agora: finalizacao.ensure_edital_can_be_cancelled(edital),
    )
