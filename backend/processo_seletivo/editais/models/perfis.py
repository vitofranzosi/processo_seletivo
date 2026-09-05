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
