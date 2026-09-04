import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.avaliacoes.domain.formas import Forma
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
    # Quantas avaliações cada inscrição recebe nesta Etapa, e qual a pontuação máxima. As duas
    # entram juntas na versão canônica 5 e são **normativas**: a primeira decide se uma nota
    # isolada elimina o candidato ou se há segunda leitura, e a segunda é o limite contra o qual
    # a pontuação é validada — regra que afeta direito não pode ser configuração de tela (012,
    # FR-007, D-001). `null` significa "não declarado", e o que a ausência quer dizer vive num
    # leitor só, em `avaliacoes/domain/previsao.py` (012, FR-009, FR-066).
    evaluations_per_registration = models.PositiveSmallIntegerField(null=True, blank=True)
    maximum_score = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    # A forma de conclusão que a Etapa exige, e os rótulos com que este Edital nomeia o sentido na
    # forma decisória. Entram juntos na versão canônica 6 e são normativos: decidir se o trabalho do
    # avaliador produz nota ou deferimento afeta direito do candidato tanto quanto decidir quantas
    # pessoas o avaliam (012, D-008, FR-119).
    #
    # `forma` **não** é anulável e tem default, ao contrário de todo campo normativo anulável acima,
    # e a razão não é conveniência: não existe estado "ainda não escolhida" para ela, porque a
    # ausência já significa pontuada em todo o resto do sistema — um `NULL` aqui seria uma terceira
    # grafia do mesmo nada. O default é também o que mantém publicável todo Edital **já em
    # elaboração** quando esta coluna nasce: sem ele, o snapshot sairia com `forma: null` e a
    # publicação seria recusada. É o padrão que `eliminatory` e `classificatory` já seguem.
    forma = models.CharField(max_length=20, choices=Forma.choices, default=Forma.PONTUADA)
    # Os rótulos não têm default, e a assimetria é deliberada: neles o "não se aplica" é real, e um
    # default institucional aplicaria ao Edital um rótulo que ele não publicou (012, D-008, P-007).
    rotulo_favoravel = models.CharField(max_length=100, blank=True, default="")
    rotulo_desfavoravel = models.CharField(max_length=100, blank=True, default="")
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
            # Zero avaliações não é declaração, é contradição: a Etapa existe para ser avaliada.
            models.CheckConstraint(
                condition=Q(evaluations_per_registration__isnull=True)
                | Q(evaluations_per_registration__gt=0),
                name="ck_etapa_avaliacoes_positivas",
            ),
            # Máxima zero afirmaria uma pontuação que não pontua, pelo mesmo motivo de `weight`.
            models.CheckConstraint(
                condition=Q(maximum_score__isnull=True) | Q(maximum_score__gt=0),
                name="ck_etapa_maximum_score_positiva",
            ),
        ]

    def __str__(self):
        return f"{self.order} — {self.name}"
