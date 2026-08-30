import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.editais.models.cronograma import EventoCronograma
from processo_seletivo.processos.models import Edital


class EtapaAvaliacao(models.Model):
    """Fase pela qual os candidatos passam.

    Pertence ao **Edital** e vale para todos os seus Perfis. A Constituição admite que Perfis
    possuam Etapas distintas, e admitir não é exigir: nada está publicado, então mover a coleção
    para dentro do Perfil depois custa uma migration e um caminho de snapshot — preço que se paga
    quando houver um Edital real que precise disso.

    A forma de identidade e de ordenação é a de `EventoCronograma`, do qual esta entidade herda o
    padrão: `id` recebido e preservado na gravação, `order` único por Edital.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name="etapas")
    name = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    eliminatory = models.BooleanField(default=False)
    classificatory = models.BooleanField(default=False)
    minimum_score = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    # A Etapa referencia o Evento; as datas são do Evento e não são copiadas. `SET_NULL` porque
    # remover o Evento não pode remover a Etapa — o que não pode é o vínculo sobreviver a ele.
    evento = models.ForeignKey(
        EventoCronograma,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="etapas",
    )

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["edital", "order"], name="uq_etapa_edital_order"),
            models.CheckConstraint(
                condition=Q(minimum_score__isnull=True) | Q(minimum_score__gte=0),
                name="ck_etapa_minimum_score_nao_negativa",
            ),
            # Peso zero afirmaria uma ponderação que não pondera; a ausência é que exprime
            # "esta Etapa não pondera".
            models.CheckConstraint(
                condition=Q(weight__isnull=True) | Q(weight__gt=0),
                name="ck_etapa_weight_positivo",
            ),
        ]

    def __str__(self):
        return f"{self.order} — {self.name}"
