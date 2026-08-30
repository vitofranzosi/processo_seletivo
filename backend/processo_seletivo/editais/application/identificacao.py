"""Alterar título e descrição de um Edital em elaboração (FR-006).

O único ato de domínio que nasce nesta feature. Antes dele, a identificação era definida na criação
e nunca mais: a etapa `Identificação` do assistente era somente leitura e uma pendência de título
aparecia como **não corrigível** — o sistema apontava um defeito e informava que não havia caminho.

Não tem chave de idempotência, e a ausência é deliberada: como `replace_draft`, isto edita o
rascunho e não pratica ato irreversível. Repetir a mesma alteração escreve o mesmo valor. O que o
protege de gravação concorrente é o mesmo `compare_and_swap` de sempre.
"""

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.concurrency import compare_and_swap


def update_edital_identification(
    *, actor, edital_id, expected_revision, title, description, correlation_id
):
    require_permission(actor, "edital:elaborar")
    title = (title or "").strip()
    if not title:
        raise DomainError("field_required", "O título do Edital é obrigatório.", 422)
    limite = Edital._meta.get_field("title").max_length
    if len(title) > limite:
        raise DomainError(
            "field_constraint_violated",
            f"O título do Edital admite no máximo {limite} caracteres.",
            422,
        )
    with command_context() as now:
        try:
            edital = (
                Edital.objects.select_for_update()
                .select_related("processo")
                .get(pk=edital_id, institution_scope=actor.institution_scope)
            )
        except Edital.DoesNotExist as exc:
            raise DomainError("not_found", "Recurso não encontrado.", 404) from exc
        ensure_processo_accepts_changes(edital.processo)
        if edital.status != Edital.Status.EM_ELABORACAO:
            raise DomainError(
                "invalid_state",
                "Somente a identificação de Edital em elaboração pode ser alterada.",
                409,
            )
        if edital.revision != expected_revision:
            raise DomainError("stale_revision", "A revisão informada está obsoleta.", 412)
        compare_and_swap(
            Edital.objects,
            pk=edital.pk,
            expected_revision=expected_revision,
            title=title,
            description=(description or "").strip(),
            last_edited_by=actor.subject,
        )
        edital.refresh_from_db()
        record_event(
            actor=actor,
            permission="edital:elaborar",
            operation="ALTERAR_IDENTIFICACAO",
            aggregate=edital,
            now=now,
            correlation_id=correlation_id,
            previous_state=edital.status,
            previous_revision=expected_revision,
        )
        return edital
