import uuid

from django.db import models


class RegistroAuditoria(models.Model):
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    occurred_at = models.DateTimeField()
    actor_subject = models.CharField(max_length=255)
    permission = models.CharField(max_length=100)
    institution_scope = models.CharField(max_length=100)
    operation = models.CharField(max_length=100)
    aggregate_type = models.CharField(max_length=100)
    aggregate_id = models.UUIDField()
    previous_state = models.CharField(max_length=50, blank=True)
    new_state = models.CharField(max_length=50, blank=True)
    previous_revision = models.PositiveBigIntegerField(null=True)
    new_revision = models.PositiveBigIntegerField(null=True)
    reason = models.TextField(blank=True)
    correlation_id = models.CharField(max_length=100)
    idempotency_key = models.CharField(max_length=128, blank=True)

    class Meta:
        indexes = [models.Index(fields=["aggregate_type", "aggregate_id", "occurred_at"])]

    def __str__(self):
        return f"{self.operation}:{self.aggregate_type}:{self.aggregate_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("RegistroAuditoria é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("RegistroAuditoria é append-only")


class IdempotencyRecord(models.Model):
    institution_scope = models.CharField(max_length=100)
    actor_subject = models.CharField(max_length=255)
    operation = models.CharField(max_length=100)
    key = models.CharField(max_length=128)
    request_hash = models.CharField(max_length=64)
    result_type = models.CharField(max_length=100, blank=True)
    result_id = models.UUIDField(null=True)
    response_status = models.PositiveSmallIntegerField(null=True)
    # O desfecho de um ato **em lote**, que não cabe num identificador. Distribuir cem inscrições
    # produz um resultado — quantas foram, quantas não e por quê — e a repetição precisa devolver
    # esse resultado, não um vazio: recusa não é reconstruível depois, porque o estado que a
    # produziu mudou (012, FR-084, FR-097). Nulo para todo ato de resultado singular.
    result_payload = models.JSONField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["institution_scope", "actor_subject", "operation", "key"],
                name="uq_idempotency_scope_actor_operation_key",
            )
        ]

    def __str__(self):
        return f"{self.operation}:{self.key}"
