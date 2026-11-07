"""Leituras administrativas de Processos e Editais.

A API da 001 não expõe listagem — todos os endpoints administrativos são commands. A interface
precisa de uma, então ela nasce aqui, na camada de aplicação, e não como consulta solta na view:
o escopo institucional precisa ser aplicado no mesmo lugar em que os commands o aplicam, senão a
listagem vira a brecha por onde se enxerga o que não se pode alcançar.
"""

import re
from dataclasses import dataclass
from datetime import datetime

from django.db.models import (
    BooleanField,
    Case,
    CharField,
    Count,
    Exists,
    ExpressionWrapper,
    F,
    Func,
    IntegerField,
    OuterRef,
    Q,
    Value,
    When,
)

from processo_seletivo.processos.models import AtoAdministrativo, Edital, ProcessoSeletivo

# ---------------------------------------------------------------------------
# O recorte da lista de Processos (129)
# ---------------------------------------------------------------------------

#: Os grupos da lista, na ordem em que a busca os apresenta (FR-4308). Cada Processo cai em
#: exatamente um (FR-4302): o grupo é uma anotação, e não três filtros que precisariam coincidir.
ANDAMENTO, ENCERRADOS, CANCELADOS = 0, 1, 2
GRUPOS = (ANDAMENTO, ENCERRADOS, CANCELADOS)
FINAIS = (Edital.Status.ENCERRADO, Edital.Status.CANCELADO)

#: A ordem estável das abas e de cada grupo da busca: do mais recente ao mais antigo. O `-id`
#: desempata Processos criados no mesmo instante — sem ele, a paginação por deslocamento podia
#: repetir um e pular outro entre duas páginas do mesmo recorte.
ORDEM = ("-created_at", "-id")

#: "N/AAAA", como o Edital é citado (D-004). Espaços em volta da barra são tolerados; "90/" e
#: "/2026" não casam e se buscam como texto.
NUMERO_E_ANO = re.compile(r"^(\d+)\s*/\s*(\d{4})$")


def _sem_zeros(numero):
    """O número sem os zeros à esquerda: "1/2026" acha o "01/2026", e "90/2026" não acha o
    "190/2026"."""
    return numero.lstrip("0")


def _editais_do_processo():
    return Edital.objects.filter(processo=OuterRef("pk"))


def grupo_do_processo():
    """O grupo, pela situação **do Processo** e pela existência de Edital não final (D-001).

    Nunca pela situação do Edital sozinha, nem por data: Edital encerrado ainda convoca, recebe
    documento e recurso. E o Processo final com Edital não final — o acervo anterior à regra de
    28/09 — vai para "Em andamento": o recorte fica estritamente mais seguro que o critério puro,
    sem depender de conferir o banco de produção.
    """
    nao_final = Exists(_editais_do_processo().exclude(status__in=FINAIS))
    return Case(
        When(nao_final, then=Value(ANDAMENTO)),
        When(status=ProcessoSeletivo.Status.ENCERRADO, then=Value(ENCERRADOS)),
        When(status=ProcessoSeletivo.Status.CANCELADO, then=Value(CANCELADOS)),
        default=Value(ANDAMENTO),
        output_field=IntegerField(),
    )


def busca_de_processos(termo):
    """A condição da busca sobre o Processo, ou `None` sem termo (FR-4306).

    Título e código do Processo, título de qualquer Edital dele e o número de qualquer Edital dele.
    As condições de Edital são `Exists`, e não junção: a busca escolhe Processos, e um Processo com
    três Editais que casam não sai três vezes, nem precisa de `distinct`.

    **"N/AAAA" é identificador, e só** (D-004): é como o Edital é citado, e quem o digita procura
    aquele Edital. Somado ao texto, "90/2026" trazia também o Processo do Edital 190/2026, cujo
    título — "Edital 190/2026 — …", a forma que a elaboração costuma dar — contém a citação. "N"
    sozinho casa o número em qualquer ano **e** o texto (FR-4306): pode ser parte de um código ou de
    um título, e é pedido mais vago por natureza.
    """
    termo = (termo or "").strip()
    if not termo:
        return None
    numero_sem_zeros = Func(F("number"), Value("0"), function="LTRIM", output_field=CharField())
    if casado := NUMERO_E_ANO.match(termo):
        numero, ano = casado.groups()
        return Q(
            Exists(
                _editais_do_processo()
                .annotate(numero_sem_zeros=numero_sem_zeros)
                .filter(numero_sem_zeros=_sem_zeros(numero), year=int(ano))
            )
        )
    condicao = (
        Q(title__icontains=termo)
        | Q(institutional_code__icontains=termo)
        | Q(Exists(_editais_do_processo().filter(title__icontains=termo)))
    )
    if termo.isdigit():
        condicao |= Q(
            Exists(
                _editais_do_processo()
                .annotate(numero_sem_zeros=numero_sem_zeros)
                .filter(numero_sem_zeros=_sem_zeros(termo))
            )
        )
    return condicao


def listar_processos(*, actor, grupo=None, busca=""):
    """Processos do escopo do ator, anotados com o grupo, na ordem da lista.

    Com `busca`, o grupo não filtra e passa a ordenar: em andamento, depois encerrados, depois
    cancelados (FR-4305, FR-4308). Sem ela, `grupo=None` é "Todos". **Sem os Editais**: a lista os
    lê para a unidade inteira, uma vez, porque a faixa precisa de todos (FR-4323).
    """
    consulta = ProcessoSeletivo.objects.filter(institution_scope=actor.institution_scope).annotate(
        grupo=grupo_do_processo()
    )
    condicao = busca_de_processos(busca)
    if condicao is not None:
        return consulta.filter(condicao).order_by("grupo", *ORDEM)
    if grupo is not None:
        consulta = consulta.filter(grupo=grupo)
    return consulta.order_by(*ORDEM)


@dataclass(frozen=True)
class Contagem:
    """Processos por grupo na unidade, e os que a busca encontrou (FR-4303, FR-4309)."""

    por_grupo: dict
    encontrados: dict

    @property
    def todos(self):
        return sum(self.por_grupo.values())

    @property
    def encontrados_no_total(self):
        return sum(self.encontrados.values())

    @property
    def encontrados_finais(self):
        return self.encontrados[ENCERRADOS] + self.encontrados[CANCELADOS]


def contar_por_situacao(*, actor, busca=""):
    """Os Processos de cada grupo, e os da busca, numa **só** consulta (R-3).

    Sem busca, os dois lados coincidem. A consulta é a mesma nos dois casos, de propósito: a lista
    não pode custar mais com a busca do que sem ela (FR-4327).

    A condição da busca entra como **anotação**, e não direto no `filter` do `Count`: dentro do
    `aggregate`, o `OuterRef` dos `Exists` de Edital não se resolve contra a consulta de fora, e o
    PostgreSQL recusa a referência ("missing FROM-clause entry"). O grupo já é anotação pelo mesmo
    motivo.
    """
    condicao = busca_de_processos(busca)
    casa = (
        Value(True)
        if condicao is None
        else Case(When(condicao, then=Value(True)), default=Value(False))
    )
    agregados = {}
    for grupo in GRUPOS:
        agregados[f"g{grupo}"] = Count("id", filter=Q(grupo=grupo))
        agregados[f"b{grupo}"] = Count("id", filter=Q(grupo=grupo, casa=True))
    linha = (
        ProcessoSeletivo.objects.filter(institution_scope=actor.institution_scope)
        .annotate(grupo=grupo_do_processo(), casa=ExpressionWrapper(casa, BooleanField()))
        .aggregate(**agregados)
    )
    return Contagem(
        {grupo: linha[f"g{grupo}"] for grupo in GRUPOS},
        {grupo: linha[f"b{grupo}"] for grupo in GRUPOS},
    )


def editais_da_unidade(*, actor):
    """Todos os Editais do escopo, na ordem da lista: o Processo mais recente primeiro, e dentro
    dele por ano e número (R-5). Servem à faixa e às linhas da página.

    **O escopo é o do Processo**, o mesmo filtro da lista: o Edital carrega uma cópia do escopo, e
    um Edital legado com cópia divergente faria o Processo dele dizer "Nenhum Edital" enquanto a
    busca o achava pelo título. Era o que a leitura antiga, por `processo.editais`, garantia.
    """
    return (
        Edital.objects.filter(processo__institution_scope=actor.institution_scope)
        .select_related("processo")
        .order_by("-processo__created_at", "-processo_id", "year", "number")
    )


def obter_edital(*, actor, edital_id):
    """Edital do escopo do ator, ou None. O escopo é aplicado aqui, como nos commands."""
    return (
        Edital.objects.filter(pk=edital_id, institution_scope=actor.institution_scope)
        .select_related("processo")
        .first()
    )


# ---------------------------------------------------------------------------
# O desfecho, para quem lê de fora (047, `FR-760` a `FR-762`)
# ---------------------------------------------------------------------------

EDITAL, PROCESSO = "EDITAL", "PROCESSO"
ENCERRADO, CANCELADO = "ENCERRADO", "CANCELADO"
# O estado final e a operação do ato que o produziu (`processos/application/finalizacao.py`).
OPERACAO_DO_DESFECHO = {ENCERRADO: "ENCERRAR", CANCELADO: "CANCELAR"}


@dataclass(frozen=True)
class Desfecho:
    """O fim de um Edital, ou do Processo dele, como a página pública o diz.

    `em` é o instante do ato imutável que registrou o desfecho, e `None` quando ele não é
    encontrado: a página diz o desfecho sem data, e não inventa uma (`FR-775`). Motivo e autor do
    ato **não** viajam aqui — a página não os diz (`FR-764`, `FR-776`), e minimização estrutural
    é não carregar o que não se mostra.
    """

    alcance: str
    operacao: str
    em: datetime | None

    @property
    def do_edital(self):
        """O desfecho é do próprio Edital — e só esse fecha o recebimento de inscrições.

        **O do Processo não fecha** (047, correção da revisão). `recebe_inscricoes` lê o status do
        Edital, e não o do Processo. Até 28/09 o encerramento do Processo não exigia os Editais em
        estado final, e um Edital publicado de Processo encerrado continuava recebendo inscrição
        dentro do período; a página diz o fato do encerramento, e não o que o sistema não faz.
        Desde a decisão de 28/09 sobre o RC-118, encerrar o Processo exige os Editais finais, e o
        caso só sobrevive no Processo encerrado antes dela — que é para quem esta regra continua.
        """
        return self.alcance == EDITAL


def desfechos(editais):
    """`{edital_id: Desfecho | None}` — o desfecho aplicável a cada Edital (047, `D-003`).

    **O estado diz se; o ato diz quando** (`research.md`, `R-2`). Os estados finais são terminais e
    mudam por CAS, e já vêm carregados com o Edital e o Processo: decidem sem consulta nenhuma na
    imensa maioria dos casos. A data vem do `AtoAdministrativo`, que é append-only nas duas camadas;
    `last_changed_at` seria a data da última transição, sobrescrita a cada uma.

    **Precedência**: o desfecho do Edital vence o do Processo, porque é o mais específico. Sem
    ele, o do Processo é devolvido para ser **dito como fato**, e não para decidir a situação das
    inscrições (`Desfecho.do_edital`).

    **Uma consulta, e só quando há estado final**: a vitrine chama isto uma vez para todos os
    cartões, e o número de idas ao banco não cresce com eles.
    """
    # `(alcance, operação, agregado)`: de quem é o desfecho, qual foi, e onde procurar o ato.
    aplicaveis = {}
    for edital in editais:
        if edital.status in (Edital.Status.ENCERRADO, Edital.Status.CANCELADO):
            aplicaveis[edital.id] = (EDITAL, str(edital.status), edital.id)
        elif edital.processo.status in (
            ProcessoSeletivo.Status.ENCERRADO,
            ProcessoSeletivo.Status.CANCELADO,
        ):
            aplicaveis[edital.id] = (PROCESSO, str(edital.processo.status), edital.processo_id)
    resultado = {edital.id: None for edital in editais}
    if not aplicaveis:
        return resultado

    instantes = {}
    for agregado, operacao, ocorrido in (
        AtoAdministrativo.objects.filter(
            aggregate_id__in={agregado for _, _, agregado in aplicaveis.values()},
            operation__in=OPERACAO_DO_DESFECHO.values(),
        )
        .order_by("occurred_at")
        .values_list("aggregate_id", "operation", "occurred_at")
    ):
        # Em ordem cronológica, o último vence. Há um só por agregado — o estado final não admite
        # transição —, e a ordem existe para não depender disso.
        instantes[(agregado, operacao)] = ocorrido

    for edital_id, (alcance, operacao, agregado) in aplicaveis.items():
        resultado[edital_id] = Desfecho(
            alcance=alcance,
            operacao=operacao,
            em=instantes.get((agregado, OPERACAO_DO_DESFECHO[operacao])),
        )
    return resultado
