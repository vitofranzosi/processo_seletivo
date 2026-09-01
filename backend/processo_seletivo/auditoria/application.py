from processo_seletivo.auditoria.models import RegistroAuditoria

# Sentinela, e não `None`: `new_revision` é coluna anulável, então `None` é valor legítimo. Usá-lo
# também como marcador de "leia do agregado" tornaria impossível gravar revisão nula de propósito
# — a chamada cairia em `aggregate.revision`, que agregados sem revisão não têm (011, D-014).
_UNSET = object()


def record_event(
    *,
    actor,
    permission,
    operation,
    aggregate,
    now,
    correlation_id,
    reason="",
    previous_state="",
    previous_revision=None,
    idempotency_key="",
    new_state=_UNSET,
    new_revision=_UNSET,
):
    return RegistroAuditoria.objects.create(
        occurred_at=now,
        actor_subject=actor.subject,
        permission=permission,
        institution_scope=actor.institution_scope,
        operation=operation,
        aggregate_type=aggregate.__class__.__name__,
        aggregate_id=aggregate.pk,
        previous_state=previous_state,
        new_state=aggregate.status if new_state is _UNSET else new_state,
        previous_revision=previous_revision,
        new_revision=aggregate.revision if new_revision is _UNSET else new_revision,
        reason=reason,
        correlation_id=correlation_id,
        idempotency_key=idempotency_key,
    )
