import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.processos.models import Edital


class PerfilVaga(models.Model):
    class ReserveType(models.TextChoices):
        NONE = "NONE"
        LIMITED = "LIMITED"
        UNLIMITED = "UNLIMITED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="perfis")
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    requirements = models.JSONField(default=list, blank=True)
    immediate_vacancies = models.PositiveIntegerField(default=0)
    reserve_type = models.CharField(
        max_length=10, choices=ReserveType.choices, default=ReserveType.NONE
    )
    reserve_limit = models.PositiveIntegerField(null=True, blank=True)
    locality = models.CharField(max_length=255, blank=True)
    # O que um Edital real diz sobre a vaga e que o sistema ainda não dizia (FR-012). Os três são
    # texto descritivo e opcionais: um Edital descreve remuneração em prosa — "R$ 4.200,00 mensais,
    # acrescidos de auxílio-alimentação" —, e modelar isso como objeto de moeda ou tabela salarial
    # construiria a estrutura antes de existir a regra que a consome (FR-013).
    # `blank=True` e nunca `null`, como `description` e `locality` acima: a ausência de um texto é a
    # string vazia, e ter duas formas de dizer "não informado" na mesma linha seria o defeito.
    duties = models.TextField(blank=True)
    workload = models.CharField(max_length=255, blank=True)
    compensation = models.CharField(max_length=255, blank=True)
    classification_information = models.JSONField(default=dict, blank=True)
    call_information = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["edital", "code"], name="uq_perfil_edital_code"),
            models.CheckConstraint(
                condition=(
                    Q(reserve_type="NONE", reserve_limit__isnull=True)
                    | Q(reserve_type="LIMITED", reserve_limit__isnull=False)
                    | Q(reserve_type="UNLIMITED", reserve_limit__isnull=True)
                ),
                name="ck_perfil_reserve_limit_compatible",
            ),
        ]

    def __str__(self):
        return f"{self.code} — {self.name}"


class ModalidadeConcorrencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    perfil = models.ForeignKey(PerfilVaga, on_delete=models.CASCADE, related_name="modalidades")
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["perfil", "code"], name="uq_modalidade_perfil_code")
        ]

    def __str__(self):
        return f"{self.code} — {self.name}"


class RegraNormativa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    modalidade = models.OneToOneField(
        ModalidadeConcorrencia, on_delete=models.CASCADE, related_name="regra_normativa"
    )
    foundation = models.TextField()
    version = models.CharField(max_length=50)
    percentage = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    calculation = models.JSONField(default=dict, blank=True)
    rounding = models.JSONField(default=dict, blank=True)
    distribution = models.JSONField(default=dict, blank=True)
    call_rules = models.JSONField(default=dict, blank=True)
    effective_from = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Regra {self.version} — {self.modalidade.code}"
