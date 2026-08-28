import uuid

from django.db import models

from processo_seletivo.processos.models import Edital


class RevisaoEdital(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="revisoes")
    edital_revision = models.PositiveBigIntegerField()
    content = models.JSONField()
    canonical_content = models.BinaryField()
    canonical_schema_version = models.PositiveSmallIntegerField(default=1)
    content_hash = models.CharField(max_length=64)
    prepared_by = models.CharField(max_length=255)
    submitted_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["edital", "edital_revision"], name="uq_revisao_edital_revision"
            )
        ]

    def __str__(self):
        return f"Revisão {self.edital_revision} — {self.edital}"


class Homologacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    revisao = models.ForeignKey(
        RevisaoEdital, on_delete=models.PROTECT, related_name="homologacoes"
    )
    homologated_by = models.CharField(max_length=255)
    reason = models.TextField()
    homologated_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.CharField(max_length=255, blank=True)
    revocation_reason = models.TextField(blank=True)

    def __str__(self):
        return f"Homologação — {self.revisao}"


class Publicacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="publicacoes")
    revisao = models.OneToOneField(
        RevisaoEdital,
        on_delete=models.PROTECT,
        related_name="publicacao",
        null=True,
        blank=True,
    )
    publication_order = models.PositiveBigIntegerField()
    published_at = models.DateTimeField()
    effective_at = models.DateTimeField()
    content_hash = models.CharField(max_length=64)
    canonical_content = models.BinaryField()
    canonical_schema_version = models.PositiveSmallIntegerField(default=1)
    published_by = models.CharField(max_length=255)
    signatory_id = models.UUIDField()
    signatory_name = models.CharField(max_length=255)
    signatory_role = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["edital", "publication_order"], name="uq_publicacao_edital_order"
            )
        ]

    def __str__(self):
        return f"Publicação {self.publication_order} — {self.edital}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("Publicacao é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("Publicacao é append-only")


class DocumentoPublicado(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publicacao = models.OneToOneField(
        Publicacao, on_delete=models.PROTECT, related_name="documento"
    )
    bytes = models.BinaryField()
    content_type = models.CharField(max_length=100, default="application/pdf")
    document_hash = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"Documento — {self.publicacao}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("DocumentoPublicado é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("DocumentoPublicado é append-only")


from processo_seletivo.publicacoes.models_retificacao import (  # noqa: E402,F401
    AlteracaoNormativa,
    ProvenienciaConteudo,
    Retificacao,
    VersaoConsolidada,
)
