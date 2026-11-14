import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.avaliacoes.domain.formas import Forma
from processo_seletivo.editais.models.cronograma import EventoCronograma
from processo_seletivo.processos.models import Edital

# Os dois efeitos que um Edital escreve para o desfecho desfavorável (164, D-001): o 28/2026 e o
# 57/2026, 8.10, tiram da reserva; o 57/2026, 8.11, e a Res. CS 61/2019, art. 16, eliminam.
EFEITOS_DO_DESFECHO = [
    ("RETIRA_DA_RESERVA", "Deixa de concorrer pela reserva e continua na ampla concorrência"),
    ("ELIMINA", "É eliminado do processo seletivo"),
]

# As três regras de deliberação que a P-3 oferece (165, D-001): o Edital escolhe uma, sem padrão.
REGRAS_DE_DELIBERACAO = [
    ("MAIORIA", "Favorável quando a maioria dos pareceres é favorável"),
    ("UNANIMIDADE_PARA_O_FAVORAVEL", "Favorável só quando todos os pareceres são favoráveis"),
    (
        "UNANIMIDADE_PARA_O_DESFAVORAVEL",
        "Desfavorável só quando todos os pareceres são desfavoráveis",
    ),
]


class EtapaAvaliacao(models.Model):
    """Fase pela qual os candidatos passam.

    Pertence ao **Edital** e vale para todos os seus Perfis. A Constituição admite que Perfis
    possuam Etapas distintas, e admitir não é exigir: a coleção continua no Edital.

    **Mas nem toda Etapa alcança toda inscrição** (163, D-001). A heteroidentificação dos Editais
    28/2026 e 57/2026 só avalia quem se inscreveu numa Modalidade reservada, e era a lacuna L-2 que
    a mantinha fora do sistema. O `alcance` diz quais códigos de Modalidade a Etapa alcança, em
    todos os Perfis que os têm; quem responde se uma inscrição é alcançada é
    `editais/domain/alcance.py`.

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
    # **O alcance** (163, FR-6960, D-002): `NULL` é "todas as inscrições", que é o que toda Etapa
    # significava antes desta coluna — por isso ela nasce sem preenchimento. A forma restrita é a
    # lista dos **códigos** de Modalidade, e não das identidades: a Modalidade é do Perfil, e o que
    # a `PPI` do C1 e a do C2 têm em comum é o código, como no recorte transversal da `044`. Lista,
    # e não tabela filha, porque nada endereça um item do alcance sozinho (T-001).
    alcance = models.JSONField(null=True, blank=True)
    # **O efeito do desfecho** (164, FR-7000, FR-7004). Só a Etapa restrita e eliminatória o
    # declara, e o vazio é "não declarado": no desfavorável, a publicação o lê como "retira da
    # reserva" (FR-7001); na ausência, como "o mesmo efeito". O padrão é aplicado na publicação, e
    # não aqui, porque só ali a Etapa é conhecida inteira — alcance e caráter — e um default de
    # coluna afirmaria um efeito na Etapa que não tem reserva de onde tirar ninguém (T-001).
    efeito_desfavoravel = models.CharField(
        max_length=20, blank=True, default="", choices=EFEITOS_DO_DESFECHO
    )
    efeito_da_ausencia = models.CharField(
        max_length=20, blank=True, default="", choices=EFEITOS_DO_DESFECHO
    )
    # **A regra de deliberação** (165, FR-7050). Só a Etapa decisória com mais de uma avaliação por
    # inscrição a declara, e o vazio é "não declarada" — **sem padrão** (D-002): a escolha entre as
    # três é da CPVA, e a coluna não responde por ela. A publicação recusa a Etapa colegiada sem
    # regra, e não grava regra nas demais (research T-002).
    regra_de_deliberacao = models.CharField(
        max_length=40, blank=True, default="", choices=REGRAS_DE_DELIBERACAO
    )
    # **A admissão do vídeo gravado pelo candidato** (166, FR-7102, D-001). Só a Etapa decisória e
    # colegiada, com alcance e período, a declara, e só com a chave `VERIFICACAO_POR_VIDEO` ligada;
    # quem recusa o resto é a publicação (FR-7103, FR-7104). `False` é o que toda Etapa significava.
    admite_video = models.BooleanField(default=False)
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
            # Alcance vazio não é "nenhuma Modalidade": é contradição, pela razão das avaliações
            # positivas acima. A recusa com mensagem é de `validate_stage` (FR-6962).
            models.CheckConstraint(
                condition=Q(alcance__isnull=True) | ~Q(alcance=[]),
                name="ck_etapa_alcance_nao_vazio",
            ),
            # Literais, como as demais: o valor fora das escolhas entraria por `bulk_create` ou SQL,
            # e a publicação o leria como "não declarado" sem que ninguém percebesse.
            models.CheckConstraint(
                condition=Q(efeito_desfavoravel__in=("", "RETIRA_DA_RESERVA", "ELIMINA")),
                name="ck_etapa_efeito_desfavoravel",
            ),
            models.CheckConstraint(
                condition=Q(efeito_da_ausencia__in=("", "RETIRA_DA_RESERVA", "ELIMINA")),
                name="ck_etapa_efeito_da_ausencia",
            ),
            models.CheckConstraint(
                condition=Q(
                    regra_de_deliberacao__in=(
                        "",
                        "MAIORIA",
                        "UNANIMIDADE_PARA_O_FAVORAVEL",
                        "UNANIMIDADE_PARA_O_DESFAVORAVEL",
                    )
                ),
                name="ck_etapa_regra_de_deliberacao",
            ),
        ]

    def __str__(self):
        return f"{self.order} — {self.name}"


class CriterioAvaliacao(models.Model):
    """Uma linha do barema de uma Etapa pontuada (146, D-001, FR-5200, FR-5201).

    **Mora na Etapa, e não no Perfil nem numa biblioteca.** A Etapa já é do Edital e vale para todos
    os Perfis, e é por isso que a mesma ficha serve às vagas de um Edital de três Perfis sem cópia
    (SC-1625). No Perfil, multiplicaria a configuração no caso comum e anteciparia a decisão do
    alcance da Etapa (P-5); numa biblioteca, não haveria caso que reusasse entre Editais — o
    reaproveitamento do Edital inteiro já copia.

    **Elaboração, como a Etapa**: muda até publicar, e depois só por Retificação. Não é append-only,
    e por isso não entra na contagem das tabelas protegidas. O molde é o de `CriterioDesempate`:
    `id` recebido e preservado na gravação, `ordem` única dentro do contêiner.

    **Duas formas de pontuar, sem campo de tipo** (D-002, FR-5202). Com `pontos_por_unidade`, a
    comissão informa a quantidade e a parcela é `min(quantidade × pontos, máxima)`; sem eles, a
    comissão atribui os pontos, de zero à máxima. "Doutorado, 20 pontos" é por quantidade, com os
    pontos iguais à máxima. Um campo de tipo diria de novo o que a ausência já diz.

    **`documento` é UUID, e não chave estrangeira.** `replace_draft` apaga e recria os Documentos
    Exigidos a cada gravação de etapa, e uma FK com `SET_NULL` desfaria o vínculo em toda gravação
    — o barema perderia a comprovação sem que ninguém tocasse nele. O vínculo é conferido pelo
    domínio contra os documentos da mesma gravação (FR-5205).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa = models.ForeignKey(EtapaAvaliacao, on_delete=models.CASCADE, related_name="criterios")
    ordem = models.PositiveIntegerField()
    nome = models.CharField(max_length=200)
    # Onde vão as exigências que o Edital escreve junto do título — "na área da Educação", "só
    # experiência em EaD" — e as observações com asterisco. Texto livre, que o sistema não avalia.
    descricao = models.TextField(blank=True, default="")
    maxima = models.DecimalField(max_digits=7, decimal_places=4)
    pontos_por_unidade = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    # "certificado", "mês", "diploma". Obrigatória com pontos por unidade, porque "5 pontos por"
    # não se lê; vazia sem eles, porque a pontuação direta não tem unidade.
    unidade = models.CharField(max_length=60, blank=True, default="")
    documento = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["ordem", "id"]
        constraints = [
            models.UniqueConstraint(fields=["etapa", "ordem"], name="uq_criterio_avaliacao_ordem"),
            models.UniqueConstraint(fields=["etapa", "nome"], name="uq_criterio_avaliacao_nome"),
            # Máxima zero afirmaria um critério que não pontua, pela razão da máxima da Etapa.
            models.CheckConstraint(
                condition=Q(maxima__gt=0), name="ck_criterio_avaliacao_maxima_positiva"
            ),
            models.CheckConstraint(
                condition=Q(pontos_por_unidade__isnull=True)
                | (Q(pontos_por_unidade__gt=0) & Q(pontos_por_unidade__lte=models.F("maxima"))),
                name="ck_criterio_avaliacao_pontos_na_faixa",
            ),
            models.CheckConstraint(
                condition=(Q(pontos_por_unidade__isnull=True) & Q(unidade=""))
                | (Q(pontos_por_unidade__isnull=False) & ~Q(unidade="")),
                name="ck_criterio_avaliacao_unidade_com_pontos",
            ),
        ]

    def __str__(self):
        return f"{self.ordem}. {self.nome}"
