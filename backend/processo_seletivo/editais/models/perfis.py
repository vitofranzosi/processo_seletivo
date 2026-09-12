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

    # **Qual das Modalidades declaradas é a ampla concorrência** (014, D-014). `None` significa que
    # o Perfil não declarou nenhuma — o formato em que a ampla concorrência existe só como a linha
    # geral do quadro, sem Modalidade homônima.
    #
    # **Por que a declaração é necessária.** A `025` deixou registrado que o Edital normal declara
    # *também* uma Modalidade chamada "Ampla concorrência", e que a quantidade dela mora na **linha
    # geral** — a de `modalidade` nula —, porque é o recorte que o sorteio consulta. Sem dizer qual
    # é, o sistema não tem como distinguir a Modalidade que corresponde à linha geral daquela que
    # exige linha própria: a `R-006` daquela feature recusou, por escrito, identificá-la casando o
    # nome, e continua certa em recusar. O que faltava era o Edital **dizê-lo**, e é o que este
    # campo é.
    #
    # **Ela não recebe linha no quadro**, e a conferência recusa quem lhe der uma: a quantidade dela
    # já está na linha geral, e duas linhas para o mesmo recorte é a contradição que a `025`
    # proíbe.
    modalidade_ampla_concorrencia = models.UUIDField(null=True, blank=True)
    # A espécie do gatilho da reversão de vaga reservada (016, D-007). **Nula significa "este
    # Edital não declara reversão"** — nunca "reverte do jeito comum": o 57/2026 proíbe por escrito
    # o remanejamento entre cursos, e reverter por conta própria produziria ali o que ele veda.
    #
    # **Uma coluna, e não duas**, porque o objeto publicado tem um campo só. No conteúdo publicado a
    # forma é objeto (`vacancyReversion`), para que um campo novo da mesma decisão entre sem um
    # segundo degrau canônico (016, R-005).
    #
    # **Vazio, e não nulo**: é a grafia que este repositório usa para texto ausente — `null` em
    # `CharField` daria duas formas de dizer a mesma coisa, e o `DJ001` cobra isso. Os dois valores
    # declaráveis são não vazios, então vazio é inequivocamente "não declarou".
    especie_de_reversao = models.CharField(
        max_length=32,
        blank=True,
        default="",
        choices=[
            ("ON_EXHAUSTION", "Só quando a lista reservada esgota"),
            ("ON_BALANCE", "A quantidade que ficou sem preencher"),
        ],
    )

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


class LinhaDoQuadroDeVagas(models.Model):
    """Uma quantidade de vagas imediatas com identidade própria, dentro do Perfil (025, D-002).

    **`modalidade` nula É a ampla concorrência, e não ausência.** O recorte sem lista de
    concorrência não filtra por Modalidade nenhuma: entram todas as inscrições submetidas do Perfil,
    que é o que a cláusula da ampla concorrência dos Editais reais manda. Guardar `AC 56` na
    Modalidade chamada "Ampla concorrência" — quando ela existe — seria escrever o número no lugar
    que o sorteio não consulta (D-004). A grafia não é inventada aqui: `Inscricao.modality_id`,
    `PosicaoNaOrdem.modalidade_id` e `AtoDeOrdenacao.lista_id` já são anuláveis com este mesmo
    sentido, e `classificacao/models.py` escreve a frase.

    **`PROTECT` é a D-008 escrita no banco.** Remover a Modalidade não pode fazer a quantidade sumir
    como efeito colateral de outro movimento: quem retifica declara os dois movimentos. Para o
    conteúdo publicado a mesma regra é um achado impeditivo — banco e conteúdo publicado são duas
    camadas independentes, como a Constituição pede para tudo o que é normativo.

    **A quantidade é a fonte, e nunca é derivada de percentual** (D-003, FR-157). O percentual da
    Regra Normativa fundamenta a cota e não a calcula: `Q 1` e `PCD 1` de um Edital real saem de
    arredondamento sobre censo e não são geráveis por percentual algum.

    **`ordem` existe por determinismo, e não por norma** (D-009). Sem ela a emissão sairia em ordem
    indefinida e dois snapshots do mesmo conteúdo teriam resumos canônicos diferentes (FR-168). Ela
    **não é publicada**: publicá-la faria o quadro afirmar uma precedência entre listas que é de
    outra feature.

    **A linha carrega vaga imediata, e só ela** (D-011). O cadastro de reserva não é repartido por
    esta feature, e o campo para isso não é admitido de antemão: estrutura antes de existir regra
    que a consuma é o que este repositório já recusou ao modelar os campos descritivos do Perfil.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    perfil = models.ForeignKey(PerfilVaga, on_delete=models.CASCADE, related_name="quadro_de_vagas")
    modalidade = models.ForeignKey(
        ModalidadeConcorrencia,
        on_delete=models.PROTECT,
        related_name="linhas_do_quadro",
        null=True,
        blank=True,
    )
    vagas_imediatas = models.PositiveIntegerField()
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "id"]
        constraints = [
            # **As duas não são redundantes, e uma só seria mais fraca.** No PostgreSQL dois `NULL`
            # não colidem: `UniqueConstraint(perfil, modalidade)` sozinha deixaria passar duas
            # linhas gerais no mesmo Perfil, que é exatamente o que a FR-154 proíbe. É a mesma
            # cirurgia de `uq_ato_raiz_por_marco`, em `classificacao/models.py`, e pela mesma razão.
            models.UniqueConstraint(
                fields=["perfil", "modalidade"],
                name="uq_linha_por_modalidade",
                condition=Q(modalidade__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["perfil"],
                name="uq_linha_geral_por_perfil",
                condition=Q(modalidade__isnull=True),
            ),
        ]

    def __str__(self):
        recorte = self.modalidade.code if self.modalidade_id else "Ampla concorrência"
        return f"{recorte}: {self.vagas_imediatas}"


class FatoDeclarado(models.Model):
    """Um fato que o Edital exige do candidato, para que uma regra publicada possa consumi-lo.

    **Não é construtor de formulário** — a recusa da `009` era de configuração de tela. Isto é
    conteúdo normativo: o campo existe porque uma regra publicada o consome, viaja no snapshot, é
    retificável e responde pela mesma cadeia de vigência que peso e nota mínima. Um Edital que não
    declara fato nenhum continua sem campo nenhum (D-2).

    **O tipo não é editável.** Um fato declarado como data que virasse número não seria o mesmo
    fato: reinterpretar o valor já congelado seria o sistema decidindo o que a pessoa quis dizer. A
    Retificação remove um e acrescenta outro, e o que foi congelado sob o primeiro permanece legível
    sob a norma que o governou (015, FR-058).

    **Os dois tipos são os que os Editais lidos de fato usam** — idade sai de data de nascimento,
    tempo de experiência sai de meses. O terceiro entra quando aparecer o Edital que o exija.
    """

    class Tipo(models.TextChoices):
        DATA = "DATA"
        INTEIRO = "INTEIRO"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    perfil = models.ForeignKey(PerfilVaga, on_delete=models.CASCADE, related_name="fatos")
    code = models.CharField(max_length=100)
    label = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["perfil", "code"], name="uq_fato_perfil_code")
        ]

    def __str__(self):
        return f"{self.code} — {self.label}"


class MarcoClassificatorio(models.Model):
    """O ponto do certame em que uma ordem entre participantes é produzida (015, D-001).

    **Ordenar é uma capacidade só, exercida em marcos identificáveis.** Não existem "ranking
    intermediário" e "classificação de verdade" como coisas de naturezas diferentes: é o mesmo ato,
    com regras de origem distintas — sobre uma Etapa, ou sobre a combinação de várias. Sem
    identidade estável do marco não há unicidade do ato vigente, não há sucessão entre emissões e
    não há sobre o que a publicação e o recurso agirem depois.

    **O peso não mora aqui.** `etapas` enumera quais Etapas entram, e o peso de cada uma é lido do
    `weight` que a própria Etapa já publica desde sempre — que continua sendo a fonte autoritativa
    (FR-009). Copiá-lo criaria duas respostas para a mesma pergunta.

    **`etapas` guarda identidade publicada, e não chave estrangeira**, pela mesma razão que
    `ResultadoEtapa.etapa_id`: existe Etapa real no Edital vigente sem linha correspondente em
    elaboração, porque a Retificação sabe acrescentar item a coleção e não escreve de volta aqui.
    """

    class Operacao(models.TextChoices):
        SOMA_PONDERADA = "SOMA_PONDERADA"
        MEDIA_PONDERADA = "MEDIA_PONDERADA"

    class Normalizacao(models.TextChoices):
        NENHUMA = "NENHUMA"
        PELA_SOMA_DOS_PESOS = "PELA_SOMA_DOS_PESOS"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    perfil = models.ForeignKey(PerfilVaga, on_delete=models.CASCADE, related_name="marcos")
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    etapas = models.JSONField(default=list, blank=True)
    operacao = models.CharField(max_length=30, choices=Operacao.choices)
    normalizacao = models.CharField(max_length=30, choices=Normalizacao.choices)
    arredondamento = models.JSONField(default=dict, blank=True)
    # A janela recursal do marco (018, degrau 8). **Vazio significa não declarada** — e não janela
    # de zero dias: sem declaração o sistema não inventa prazo, e a tempestividade volta a ser juízo
    # de admissibilidade motivado (FR-020, FR-028). Marcos diferentes admitem recurso ou não, e por
    # prazos diferentes, e é por isso que ela mora aqui e não no Edital.
    janela_recursal = models.JSONField(default=dict, blank=True)
    # O método do sorteio deste marco (021, degrau 10, D-013). **Vazio significa não declarado** —
    # e o marco sem método não congela relação (FR-066): congelar sob método indefinido seria
    # escolher o método depois.
    #
    # **Mora aqui, e não numa tabela de sorteio**, porque a FR-014 exige que alterá-lo seja
    # Retificação. Uma tabela própria seria registro operacional que se diz normativo: sem versão
    # consolidada, sem autoridade signatária, fora do snapshot e fora da gramática de
    # endereçamento. Aqui ele é conteúdo publicado como qualquer outro, e
    # `/profiles/id=…/classificationMilestones/id=…/drawMethod/…` já resolve — é objeto, e em
    # objeto o segmento do caminho é nome de chave literal.
    #
    # **É do marco, e não da lista.** Um sorteio é um evento: a mesma extração da mesma fonte
    # semeia as três listas do recorte, e é o `relationHash` que as separa. Método por lista
    # reabriria a porta que a D-014 fechou, e não atenderia Edital nenhum da amostra.
    metodo_de_sorteio = models.JSONField(default=dict, blank=True)
    # A regra de corte deste marco (014, degrau 13, D-011 a D-014, FR-178). **Vazio significa não
    # declarada** — e não regra padrão: o marco sem regra não corta, e a Etapa que ele alimentaria
    # continua recebendo o conjunto que a progressão da 013 já entrega (FR-214). É o que todo
    # Edital publicado antes deste degrau afirma, e é verdade sobre todos eles.
    #
    # **Mora aqui pelo mesmo motivo que os dois vizinhos acima**: alterá-la é Retificação (FR-184),
    # e `/profiles/id=…/classificationMilestones/id=…/cutRule/targetCount` já resolve — é objeto, e
    # em objeto o segmento do caminho é nome de chave literal. Na Etapa ela ficaria longe da ordem
    # que lê, e a `EtapaAvaliacao` é do Edital e não do Perfil; no Edital, não saberia de qual
    # Perfil falar.
    #
    # **Quatro dos seis campos existem porque o sistema não pode concluí-los** (FR-182, FR-224,
    # FR-226): o desfecho do empate na fronteira, a Etapa governada — ou a declaração explícita de
    # que não governa nenhuma —, e se aquele Edital admite continuação. A ausência de qualquer um
    # deles impede a publicação, em vez de virar padrão.
    regra_de_corte = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["perfil", "code"], name="uq_marco_perfil_code")
        ]

    def __str__(self):
        return f"{self.code} — {self.name}"


class CriterioDesempate(models.Model):
    """Um critério de desempate do marco, na posição que a norma lhe deu (015, D-004).

    **A ordem é a norma.** Aplicar os critérios fora da ordem publicada é aplicar outra regra, e por
    isso `ordem` é campo, único dentro do marco, e não posição no array: o catálogo de Retificação
    endereça por identidade, nunca por índice, e reordenar substituindo a lista inteira perderia os
    identificadores que a própria Retificação usa (FR-015).

    **O motor conhece tipos executáveis; ele não escolhe quais existem.** Não há como executar o que
    não se sabe interpretar — o que o código não pode é decidir quais critérios existem, em que
    ordem se aplicam ou qual parâmetro cada um recebe. Isso viaja no snapshot e é retificável.

    **`quando_ausente` não é anulável, e é essa a diferença entre a regra estar declarada e o
    cálculo inventar semântica.** Uma inscrição submetida antes de o Edital declarar um fato não o
    congelou, e uma Etapa decisória não produz número: o silêncio não vira zero, não vira último
    lugar e não vira critério pulado — ele impede a publicação da regra (FR-018).
    """

    class Tipo(models.TextChoices):
        MAIOR_PONTUACAO_NA_ETAPA = "MAIOR_PONTUACAO_NA_ETAPA"
        MAIOR_VALOR_DE_FATO = "MAIOR_VALOR_DE_FATO"
        MENOR_VALOR_DE_FATO = "MENOR_VALOR_DE_FATO"

    class QuandoAusente(models.TextChoices):
        ULTIMO_NO_CRITERIO = "ULTIMO_NO_CRITERIO"
        CRITERIO_NAO_SE_APLICA = "CRITERIO_NAO_SE_APLICA"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    marco = models.ForeignKey(
        MarcoClassificatorio, on_delete=models.CASCADE, related_name="criterios"
    )
    ordem = models.PositiveIntegerField()
    tipo = models.CharField(max_length=40, choices=Tipo.choices)
    parametros = models.JSONField(default=dict, blank=True)
    quando_ausente = models.CharField(max_length=30, choices=QuandoAusente.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["marco", "ordem"], name="uq_criterio_marco_ordem")
        ]

    def __str__(self):
        return f"{self.ordem}. {self.tipo}"


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
