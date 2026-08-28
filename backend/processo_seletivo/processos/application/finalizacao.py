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


def _finish_idempotency(record, result, status):
    record.result_type = result.__class__.__name__
    record.result_id = result.pk
    record.response_status = status
    record.save(update_fields=["result_type", "result_id", "response_status"])


def _register(*, actor, aggregate, operation, permission, reason, previous, now, correlation_id,
              idempotency_key):
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
    *, actor, processo_id, expected_revision, reason, idempotency_key, correlation_id,
    permission, operation, target_status, check,
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
            return ProcessoSeletivo.objects.get(pk=idem.result_id), False
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
        return processo, True


def close_process(*, actor, processo_id, expected_revision, reason, idempotency_key,
                  correlation_id):
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
        check=finalizacao.ensure_processo_can_be_closed,
    )


def cancel_process(*, actor, processo_id, expected_revision, reason, idempotency_key,
                   correlation_id):
    """Bloqueia o cancelamento sob concorrência travando o Processo e depois seus Editais."""

    def check(processo):
        # Locks em ordem estável de id evitam deadlock e fecham a janela TOCTOU entre a
        # verificação dos Editais pendentes e a gravação do cancelamento.
        pendentes = list(
            processo.editais.select_for_update()
            .exclude(status__in=finalizacao.EDITAL_FINAL)
            .order_by("id")
        )
        pendentes.sort(key=lambda edital: (edital.year, edital.number, str(edital.id)))
        finalizacao.ensure_processo_can_be_cancelled(processo, pendentes)

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
    *, actor, edital_id, expected_revision, reason, idempotency_key, correlation_id,
    permission, operation, target_status, check,
):
    require_permission(actor, permission)
    with command_context() as now:
        edital = _lock_edital(actor, edital_id)
        idem = reserve(
            actor=actor,
            operation=f"{permission}:{edital_id}",
            key=idempotency_key,
            payload={"reason": reason},
        )
        if idem.result_id:
            return Edital.objects.get(pk=idem.result_id), False
        finalizacao.ensure_processo_accepts_changes(edital.processo)
        check(edital)
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
        return edital, True


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
        check=finalizacao.ensure_edital_can_be_closed,
    )


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
        check=finalizacao.ensure_edital_can_be_cancelled,
    )
