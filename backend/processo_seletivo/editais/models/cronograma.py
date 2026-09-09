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
    # Qual Evento **é** o período de inscrições (FR-001 da 009). Marca no próprio Evento, e não
    # chave estrangeira no Cronograma nem tipo reservado em `type`: aqui o pertencimento é da
    # estrutura — o Evento marcado é, por construção, do Cronograma daquele Edital — e a unicidade
    # cabe numa constraint. `type` é texto livre e nada o valida; inferir o período dali seria
    # decidir uma regra de direito lendo o que alguém digitou.
    is_registration_period = models.BooleanField(default=False)
    # Onde o Evento acontece (021, D-008, FR-056..FR-061). **Um campo de texto, e não dois**: o 76
    # publica naturezas diferentes na mesma coluna LOCAL, e o 77 diz sala física e canal na mesma
    # frase — separar endereço de link inventaria uma distinção que os Editais não fazem.
    #
    # **Não é URL**, e não é validado como tal: *"Página da chamada pública"* não é endereço
    # eletrônico, e recusá-lo obrigaria a instituição a mentir para poder publicar (FR-061).
    #
    # **Sem valor institucional por padrão** (FR-058), pela razão que os rótulos da Etapa já
    # registraram: um default aplicaria ao Edital um dado que ele não publicou. Vazio significa
    # "não declarado", e é o que todo Edital anterior ao degrau 11 afirma. A conveniência vai para
    # a composição, que sugere o valor do evento anterior — sugerir é da tela, presumir é do
    # conteúdo publicado (FR-059).
    location = models.CharField(max_length=255, blank=True, default="")

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
            # Um período de inscrições por Cronograma. Parcial porque a restrição é sobre os
            # marcados: os demais Eventos convivem aos montes, e é só entre os verdadeiros que
            # dois seriam ambíguos.
            models.UniqueConstraint(
                fields=["cronograma"],
                condition=Q(is_registration_period=True),
                name="uq_evento_periodo_de_inscricoes",
            ),
        ]

    def __str__(self):
        return f"{self.order} — {self.description}"
