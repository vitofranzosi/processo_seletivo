import uuid

from django.db import models


class ProcessoSeletivo(models.Model):
    class Status(models.TextChoices):
        EM_ELABORACAO = "EM_ELABORACAO"
        ATIVO = "ATIVO"
        ENCERRADO = "ENCERRADO"
        CANCELADO = "CANCELADO"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution_scope = models.CharField(max_length=100)
    institutional_code = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EM_ELABORACAO)
    revision = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=255)
    last_changed_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["institution_scope", "institutional_code"],
                name="uq_processo_scope_institutional_code",
            )
        ]

    def __str__(self):
        return f"{self.institutional_code} — {self.title}"


class Edital(models.Model):
    class Status(models.TextChoices):
        EM_ELABORACAO = "EM_ELABORACAO"
        EM_REVISAO = "EM_REVISAO"
        HOMOLOGADO = "HOMOLOGADO"
        PUBLICADO = "PUBLICADO"
        ENCERRADO = "ENCERRADO"
        CANCELADO = "CANCELADO"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    processo = models.ForeignKey(ProcessoSeletivo, on_delete=models.PROTECT, related_name="editais")
    institution_scope = models.CharField(max_length=100)
    number = models.CharField(max_length=50)
    year = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EM_ELABORACAO)
    revision = models.PositiveBigIntegerField(default=1)
    next_publication_order = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=255)
    last_edited_by = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["institution_scope", "number", "year"],
                name="uq_edital_scope_number_year",
            )
        ]
        indexes = [models.Index(fields=["processo", "status"])]

    def __str__(self):
        return f"Edital {self.number}/{self.year}"


class AtoAdministrativo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aggregate_type = models.CharField(max_length=50)
    aggregate_id = models.UUIDField()
    operation = models.CharField(max_length=50)
    actor_subject = models.CharField(max_length=255)
    reason = models.TextField()
    occurred_at = models.DateTimeField()

    def __str__(self):
        return f"{self.operation}:{self.aggregate_type}:{self.aggregate_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("AtoAdministrativo é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("AtoAdministrativo é append-only")
