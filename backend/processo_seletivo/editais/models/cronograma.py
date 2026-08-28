import uuid

from django.db import models
from django.db.models import F, Q

from processo_seletivo.processos.models import Edital


class Cronograma(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.OneToOneField(Edital, on_delete=models.PROTECT, related_name="cronograma")

    def __str__(self):
        return f"Cronograma — {self.edital}"


class EventoCronograma(models.Model):
    class Status(models.TextChoices):
        PLANEJADO = "PLANEJADO"
        EM_ANDAMENTO = "EM_ANDAMENTO"
        CONCLUIDO = "CONCLUIDO"
        CANCELADO = "CANCELADO"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cronograma = models.ForeignKey(Cronograma, on_delete=models.PROTECT, related_name="eventos")
    type = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANEJADO)

    class Meta:
        ordering = ["order", "start_at", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["cronograma", "order"], name="uq_evento_cronograma_order"
            ),
            models.CheckConstraint(
                condition=Q(end_at__isnull=True) | Q(end_at__gte=F("start_at")),
                name="ck_evento_end_not_before_start",
            ),
        ]

    def __str__(self):
        return f"{self.order} — {self.description}"
