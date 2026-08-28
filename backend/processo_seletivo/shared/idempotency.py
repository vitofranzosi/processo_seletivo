from processo_seletivo.auditoria.models import IdempotencyRecord
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256


def reserve(*, actor, operation: str, key: str, payload) -> IdempotencyRecord:
    digest = canonical_sha256(payload)
    record, created = IdempotencyRecord.objects.get_or_create(
        institution_scope=actor.institution_scope,
        actor_subject=actor.subject,
        operation=operation,
        key=key,
        defaults={"request_hash": digest},
    )
    if not created and record.request_hash != digest:
        raise DomainError("idempotency_conflict", "A chave foi usada com outro conteúdo.", 409)
    return record
