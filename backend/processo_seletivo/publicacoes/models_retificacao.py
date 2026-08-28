import uuid

from django.db import models

from processo_seletivo.processos.models import Edital


class VersaoConsolidada(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(
        Edital, on_delete=models.PROTECT, related_name="versoes_consolidadas"
    )
    valid_from = models.DateTimeField()
    materialized_at = models.DateTimeField()
    source_publication = models.ForeignKey("publicacoes.Publicacao", on_delete=models.PROTECT)
    content = models.JSONField()
    canonical_content = models.BinaryField()
    content_hash = models.CharField(max_length=64)
    applied_publications = models.JSONField(default=list)

    class Meta:
        indexes = [models.Index(fields=["edital", "valid_from", "materialized_at"])]

    def __str__(self):
        return f"Versão consolidada {self.valid_from} — {self.edital}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("VersaoConsolidada é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("VersaoConsolidada é append-only")


class Retificacao(models.Model):
    class Status(models.TextChoices):
        EM_ELABORACAO = "EM_ELABORACAO"
        EM_REVISAO = "EM_REVISAO"
        HOMOLOGADA = "HOMOLOGADA"
        PUBLICADA = "PUBLICADA"
        CANCELADA = "CANCELADA"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="retificacoes")
    base_snapshot = models.ForeignKey(VersaoConsolidada, on_delete=models.PROTECT)
    publication = models.OneToOneField(
        "publicacoes.Publicacao",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="retificacao",
    )
    justification = models.TextField()
    effective_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EM_ELABORACAO)
    revision = models.PositiveBigIntegerField(default=1)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    prepared_by = models.CharField(max_length=255, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    homologated_by = models.CharField(max_length=255, blank=True)
    homologated_at = models.DateTimeField(null=True, blank=True)
    homologation_reason = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)

    def __str__(self):
        return f"Retificação {self.id} — {self.edital}"


class AlteracaoNormativa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    retificacao = models.ForeignKey(
        Retificacao, on_delete=models.CASCADE, related_name="alteracoes"
    )
    target_path = models.CharField(max_length=1000)
    operation = models.CharField(max_length=10)
    new_value = models.JSONField(null=True, blank=True)
    expected_previous_hash = models.CharField(max_length=64, blank=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["retificacao", "order"], name="uq_alteracao_order")
        ]

    def __str__(self):
        return f"{self.operation} {self.target_path}"


class ProvenienciaConteudo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="proveniencias"
    )
    target_path = models.CharField(max_length=1000)
    publicacao = models.ForeignKey("publicacoes.Publicacao", on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["versao", "target_path"], name="uq_proveniencia_path")
        ]

    def __str__(self):
        return f"{self.target_path} — {self.publicacao}"
