from processo_seletivo.auditoria.models import RegistroAuditoria


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
        new_state=aggregate.status,
        previous_revision=previous_revision,
        new_revision=aggregate.revision,
        reason=reason,
        correlation_id=correlation_id,
        idempotency_key=idempotency_key,
    )
