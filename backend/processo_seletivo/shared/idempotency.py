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


def finish(record: IdempotencyRecord, result, status: int) -> None:
    """Liga a reserva ao resultado e ao status com que o ato respondeu.

    O status é lido de volta na repetição: o contrato documenta um único código de sucesso por
    operação, e devolver 200 numa repetição de criação seria responder fora do contrato — além
    de sugerir ao cliente que nada foi criado, quando o ato existe e é dele.
    """
    record.result_type = result.__class__.__name__
    record.result_id = result.pk
    record.response_status = status
    record.save(update_fields=["result_type", "result_id", "response_status"])
