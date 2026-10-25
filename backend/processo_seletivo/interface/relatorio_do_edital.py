"""O relatório do Edital: uma leitura derivada, para quem não opera a seleção (099).

**Uma derivação, duas saídas** (D-001). A página de gestão e o PDF leem o mesmo `Relatorio`;
nenhum dos dois calcula número. É a regra que a `040` escreveu para a Visão Geral (FR-582 da
`040`), e pela mesma razão: duas derivações do mesmo número divergem na primeira mudança.

**Nada aqui é regra nova.** Cada número é a leitura que uma tela de gestão já faz — vagas e razão
da Visão Geral, série da Supervisão, resultado vigente da divulgação, recortes da ocupação, cadeia
da convocação —, e o que esta feature acrescenta é reuni-los, dizer a espécie e escrever a visão
geral por regras. Por isso mora em `interface/`, ao lado da Visão Geral e da Supervisão (R-001): é
dali que vêm as leituras, e nenhum app de domínio importa de `interface`.

**Um instante só** (FR-2519, R-002). Lido em `READ COMMITTED`, cada consulta veria o banco do
próprio começo, e um desfecho gravado entre a contagem das convocações e a das vagas produziria um
relatório que nunca existiu. `leitura_consistente` põe a transação de fora em `REPEATABLE READ`.

**O que não é público só aparece por Perfil** (FR-2550, D-006). Eliminação, ocorrência, recurso,
convocação, ocupação e rascunho nunca são desdobrados por lista de concorrência: a convocação da
única vaga reservada, dita por lista, apontaria a primeira pessoa da lista publicada. E em Perfil
com menos de cinco inscrições enviadas esses fatos somem com o motivo dito.
"""

import contextlib
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.db import connection, transaction
from django.db.models import Count

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.convocacao.application import selectors as convocacao
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
from processo_seletivo.divulgacao.models import (
    DocumentoDoResultado,
    Natureza,
    PublicacaoResultado,
    SituacaoDivulgada,
)
from processo_seletivo.inscricoes.domain.periodo import periodo_de_inscricoes
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import relatorio_trilha, supervisao, visao_geral
from processo_seletivo.interface.visao_geral import (
    NAO_APLICAVEL,
    NAO_DISPONIVEL,
    Ausencia,
    Numero,
)
from processo_seletivo.ocupacao.application.selectors import recortes_do_marco
from processo_seletivo.ocupacao.domain import nomes as nomes_da_ocupacao
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
from processo_seletivo.portal.situacao import DESFECHOS
from processo_seletivo.processos.application.selectors import desfechos
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.recursos.application import selectors as recursos
from processo_seletivo.recursos.models import DecisaoRecurso, Recurso
from processo_seletivo.resultados.models import ResultadoEtapa

ZONA = ZoneInfo("America/Sao_Paulo")

# --- Espécies -------------------------------------------------------------------------------------
ACOMPANHAMENTO = "ACOMPANHAMENTO"
ENCERRAMENTO = "ENCERRAMENTO"
INTERRUPCAO = "INTERRUPCAO"

#: Os estados em que o relatório existe (FR-2513): antes da publicação não há fato público.
ESTADOS_COM_RELATORIO = frozenset(
    {Edital.Status.PUBLICADO, Edital.Status.ENCERRADO, Edital.Status.CANCELADO}
)

# --- As duas ausências que a `040` não tinha ------------------------------------------------------
#: O fato pode ter acontecido, e o GPS não o controla (matrícula, presença, homologação).
NAO_REGISTRADO = "nao-registrado"
#: O fato existe e não é dito por privacidade (D-006).
OMITIDO = "omitido"

#: O limiar de D-006, revisável pelo usuário e pelo encarregado de dados.
MINIMO_PARA_DETALHAR = 5
FRASE_DE_PRIVACIDADE = f"detalhe omitido: menos de {MINIMO_PARA_DETALHAR} inscrições neste perfil"
#: O Perfil grande omitido só para que o pequeno não se deduza dos totais (100, FR-2587): a frase do
#: pequeno seria falsa nele.
FRASE_COMPLEMENTAR = (
    f"detalhe omitido para que o de perfil com menos de {MINIMO_PARA_DETALHAR} inscrições não se "
    "deduza dos totais"
)
#: O Edital inteiro abaixo do limiar: os totais não públicos dele também somem.
FRASE_DO_EDITAL = f"detalhe omitido: menos de {MINIMO_PARA_DETALHAR} inscrições neste Edital"

#: O rótulo de cada desfecho é o que o candidato já lê no portal (FR-2545), **com uma troca**: o
#: candidato lê "Vaga aceita", e quem dirige leria vaga preenchida. Para a gestão, o aceite é da
#: convocação (decisão do usuário de 24/10/2026, ajuste C).
ROTULOS_DOS_DESFECHOS = {**DESFECHOS, nomes_da_convocacao.ACEITE: "Convocação aceita"}

OPERACAO_DA_EMISSAO = "EMITIR_RELATORIO"


# --- A forma do relatório ------------------------------------------------------------------------


@dataclass(frozen=True)
class Indicador:
    rotulo: str
    numero: Numero
    base: str
    #: "de N", quando o número é parte de um todo dito.
    de: int | None = None


@dataclass(frozen=True)
class Data:
    dia: datetime
    texto: str
    #: publicação · registrado · previsto · prazo (FR-2538).
    natureza: str
    ate: datetime | None = None


@dataclass(frozen=True)
class LinhaDaEtapa:
    nome: str
    regra: str
    avaliadas: int
    habilitadas: int
    eliminadas: int
    por_ocorrencia: int
    elimina: bool
    #: Se a Etapa tem algum resultado registrado. Sem nenhum, os números são ausência, e não 0.
    registrada: bool


@dataclass(frozen=True)
class LinhaDaLista:
    marco: str
    lista: str
    classificadas: Numero
    vagas: Numero
    natureza: str


@dataclass(frozen=True)
class Convocacoes:
    realizadas: int
    aceitas: int
    aguardando: int
    aguardando_ate: datetime | None
    vencidas: int
    outros: tuple = ()


@dataclass(frozen=True)
class Recursos:
    apresentados: int
    nao_admitidos: int
    indeferidos: int
    deferidos: int
    aguardando: int


@dataclass(frozen=True)
class LinhaDoPerfil:
    id: str
    nome: str
    local: str
    vagas: Numero
    vagas_por_lista: tuple
    reserva: str
    inscricoes: Numero
    rascunhos: Numero
    por_vaga: Numero
    classificadas: Numero
    natureza_do_resultado: str
    habilitadas_nas_vagas: Numero
    convocacoes: Convocacoes | None
    recursos: Recursos | None
    situacao_das_vagas: str
    etapas: tuple
    listas: tuple
    omitido: bool
    #: A frase da omissão, quando há: a do Perfil pequeno ou a do complemento (100, FR-2587).
    motivo_da_omissao: str = ""


@dataclass(frozen=True)
class Retificacao_:
    numero: int
    publicada_em: datetime
    justificativa: str
    alteracoes: tuple


@dataclass(frozen=True)
class Documento:
    titulo: str
    publicado_em: datetime
    sha256: str
    endereco: str
    #: Resultado sem publicação sucessora: o que a camada executiva aponta (FR-2539). O Edital e as
    #: Retificações ficam fora, porque a referência deles é a página da seleção.
    resultado_vigente: bool = False


@dataclass(frozen=True)
class LinhaDoCronograma:
    evento: str
    previsto: str
    retificado: str
    registrado: str


@dataclass
class Relatorio:
    referencia: datetime
    edital: Edital
    unidade: dict
    especie: str
    situacao_no_gps: str
    providencias: str
    pendencias: list
    posteriores: list
    frases: list
    indicadores: list
    perfis: list
    serie: tuple
    termino_original: datetime | None
    no_periodo_acrescentado: int
    periodo_aberto: bool
    retificacoes: list
    recursos: Recursos
    datas: list
    documentos: list
    endereco_da_selecao: str
    cronograma: list
    cadastros_distintos: int
    desfecho_em: datetime | None
    pontos_de_atencao: list = field(default_factory=list)
    #: Edital com menos inscrições que o limiar: os totais não públicos dele não são ditos (100).
    total_omitido: bool = False

    @property
    def titulo(self):
        return f"Relatório do Edital {self.edital.number}/{self.edital.year}"

    @property
    def especie_por_extenso(self):
        return {
            ACOMPANHAMENTO: "Relatório de acompanhamento",
            ENCERRAMENTO: "Relatório de encerramento",
            INTERRUPCAO: "Relatório de interrupção",
        }[self.especie]

    @property
    def especie_explicada(self):
        if self.especie == ENCERRAMENTO:
            return (
                "não há providência pendente registrada no GPS. Atividades que o GPS não "
                "acompanha, como a matrícula, não estão refletidas aqui."
            )
        if self.especie == INTERRUPCAO:
            quando = f" em {data_curta(self.desfecho_em)}" if self.desfecho_em else ""
            return f"Edital cancelado{quando}."
        if self.pendencias:
            return "ainda há providência em curso."
        return "o Edital segue publicado."


# --- O instante único ----------------------------------------------------------------------------


@contextlib.contextmanager
def leitura_consistente():
    """A transação em que toda a leitura vê o mesmo instante (R-002).

    O nível só pode ser trocado antes da primeira consulta da transação, e só na transação de
    fora: dentro de um bloco já aberto — os casos de `TestCase` — o comando falharia, e a leitura já
    é da transação do caso.
    """
    de_fora = not connection.in_atomic_block
    with transaction.atomic():
        if de_fora and connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        yield


def ler(edital, *, agora, enderecos):
    """O relatório do Edital no instante `agora`, numa leitura só."""
    with leitura_consistente():
        return montar(edital, agora=agora, enderecos=enderecos)


def proxima_emissao(edital):
    """O número da emissão seguinte: as anteriores, contadas na trilha (FR-2517, R-003)."""
    return (
        RegistroAuditoria.objects.filter(
            aggregate_type="Edital", aggregate_id=edital.pk, operation=OPERACAO_DA_EMISSAO
        ).count()
        + 1
    )


# --- Formatação -----------------------------------------------------------------------------


def data_curta(instante):
    return instante.astimezone(ZONA).strftime("%d/%m/%Y") if instante else ""


def dia_e_mes(instante):
    return instante.astimezone(ZONA).strftime("%d/%m") if instante else ""


def instante_por_extenso(instante):
    local = instante.astimezone(ZONA)
    return f"{local.strftime('%d/%m/%Y')}, {local.strftime('%H')}h{local.strftime('%M')}"


def _plural(n, singular, plural):
    return singular if n == 1 else plural


def _decimal_br(valor):
    return f"{valor}".replace(".", ",")


def _minuscula(texto):
    return texto[:1].lower() + texto[1:] if texto else texto


# --- A montagem -----------------------------------------------------------------------------


def _versoes(edital, agora):
    versoes = list(
        VersaoConsolidada.objects.filter(edital=edital, valid_from__lte=agora).order_by(
            "valid_from", "materialized_at"
        )
    )
    return (versoes[0].content, versoes[-1].content) if versoes else (None, None)


def _evento_das_inscricoes(conteudo):
    for evento in (conteudo or {}).get("schedule") or []:
        if evento.get("isRegistrationPeriod"):
            return evento
    return None


def _quando(valor):
    if not valor:
        return None
    if isinstance(valor, datetime):
        return valor
    return datetime.fromisoformat(str(valor))


def _nome_da_lista(perfil, lista_id):
    if not lista_id:
        return "Ampla concorrência"
    for modalidade in perfil.get("competitionModalities") or []:
        if str(modalidade.get("id")) == str(lista_id):
            return modalidade.get("name") or "Lista reservada"
    return "Lista reservada"


def _vagas_por_lista(perfil):
    tabela = perfil.get("vacancyTable") or []
    linhas = []
    for linha in tabela:
        quantidade = linha.get("immediateVacancies") or 0
        if quantidade:
            linhas.append((_nome_da_lista(perfil, linha.get("modalityId")), quantidade))
    return tuple(linhas)


def _vagas_da_lista(perfil, lista, total):
    """As vagas imediatas de uma lista; sem quadro, todas são da ampla (`025`)."""
    tabela = perfil.get("vacancyTable")
    if not tabela:
        return total if lista is None else 0
    return sum(
        linha.get("immediateVacancies") or 0
        for linha in tabela
        if (str(linha["modalityId"]) if linha.get("modalityId") else None) == lista
    )


def _etapas_do_perfil(perfil, etapas):
    """As Etapas dos marcos do Perfil, mais a governada pelo corte, na ordem do Edital."""
    ids = set()
    for marco in perfil.get("classificationMilestones") or []:
        ids.update(str(e) for e in marco.get("stages") or [])
        governada = (marco.get("cutRule") or {}).get("governedStage")
        if governada and governada != "NONE":
            ids.add(str(governada))
    return [e for e in sorted(etapas, key=lambda e: e.get("order") or 0) if str(e["id"]) in ids]


def _regra_da_etapa(etapa):
    partes = []
    if etapa.get("eliminatory") and etapa.get("classificatory"):
        partes.append("eliminatória e classificatória")
    elif etapa.get("eliminatory"):
        partes.append("eliminatória")
    elif etapa.get("classificatory"):
        partes.append("classificatória")
    if etapa.get("forma") == "DECISORIA":
        partes.append("por decisão")
    if etapa.get("minimumScore") not in (None, ""):
        partes.append(f"nota mínima {_decimal_br(Decimal(str(etapa['minimumScore'])).normalize())}")
    if etapa.get("weight") not in (None, ""):
        partes.append(f"peso {_decimal_br(Decimal(str(etapa['weight'])).normalize())}")
    return "; ".join(partes)


# --- Os fatos, separados da redação (100) ---------------------------------------------------------
#
# **Uma regra num lugar só** (100, D-002). As pendências saíam daqui já redigidas, e somá-las entre
# Editais exigiria ler a frase — decidir situação por texto, que a FR-2547 proíbe. Agora a regra
# produz o tipo, e a frase sai de uma função que só o redige. O relatório do Edital continua o mesmo
# documento; o consolidado da unidade lê os tipos.

RESULTADO_NAO_DIVULGADO = "RESULTADO_NAO_DIVULGADO"
DEFINITIVO_NAO_PUBLICADO = "DEFINITIVO_NAO_PUBLICADO"
REAVALIACAO_PENDENTE = "REAVALIACAO_PENDENTE"
PROVIDENCIA_PENDENTE = "PROVIDENCIA_PENDENTE"
APURACAO_DESATUALIZADA = "APURACAO_DESATUALIZADA"
CONVOCACAO_AGUARDANDO = "CONVOCACAO_AGUARDANDO"
CONVOCACAO_VENCIDA = "CONVOCACAO_VENCIDA"
RECURSO_AGUARDANDO = "RECURSO_AGUARDANDO"

#: O que é público por ato: que um resultado previsto ainda não saiu está na página da seleção. O
#: resto é fato não público, e obedece à privacidade (FR-2550).
PENDENCIAS_PUBLICAS = frozenset({RESULTADO_NAO_DIVULGADO, DEFINITIVO_NAO_PUBLICADO})


@dataclass(frozen=True)
class Pendencia:
    tipo: str
    #: `None` só no recurso aguardando decisão, que o relatório diz do Edital inteiro.
    perfil_id: str | None
    quantidade: int = 1
    #: O nome publicado do marco, nas duas pendências de resultado.
    marco: str = ""
    #: O prazo mais distante, na convocação aguardando resposta.
    ate: datetime | None = None

    @property
    def publica(self):
        return self.tipo in PENDENCIAS_PUBLICAS


@dataclass
class FatosDoEdital:
    """O que a leitura do Edital produz antes de qualquer frase (100, FR-2570).

    Os campos de cima são o que o consolidado da unidade soma; os de baixo, com `_`, são o que só o
    documento individual consome — mantê-los aqui evita ler duas vezes o que a regra já leu.
    """

    edital: Edital
    referencia: datetime
    unidade: dict
    especie: str
    desfecho_em: datetime | None
    perfis: list
    pendencias: tuple
    vagas: int
    inscricoes: int
    rascunhos: int
    periodo_aberto: bool
    prorrogado: bool
    envios: tuple
    marcos_declarados: int
    marcos_definitivos: int
    datas_definitivas: tuple
    #: Soma das apurações vigentes e atualizadas; `None` quando nenhum Perfil foi apurado.
    vagas_habilitadas: int | None
    #: As vagas imediatas dos Perfis com apuração atualizada, e com apuração desatualizada (100).
    vagas_apuradas: int
    vagas_desatualizadas: int
    retificacoes: int
    #: `(nome, inscrições, vagas, espécies)` dos Perfis com marca de procura da Visão Geral (040).
    perfis_com_marca: tuple
    convocacoes: Convocacoes
    recursos: Recursos
    posteriores: list
    cadastros_distintos: int
    #: Os Perfis com detalhe não público omitido — os pequenos e os do complemento (FR-2587).
    omitidos: frozenset
    complementares: frozenset
    total_omitido: bool
    _perfis_publicados: list = field(repr=False, default_factory=list)
    _etapas: list = field(repr=False, default_factory=list)
    _original: dict | None = field(repr=False, default=None)
    _vigente: dict = field(repr=False, default_factory=dict)
    _primeira: object = field(repr=False, default=None)
    _periodo: object = field(repr=False, default=None)
    _evento_vigente: dict | None = field(repr=False, default=None)
    _termino_original: datetime | None = field(repr=False, default=None)
    _no_periodo_acrescentado: int = field(repr=False, default=0)
    _por_etapa: dict = field(repr=False, default_factory=dict)
    _prazos_em_curso: list = field(repr=False, default_factory=list)
    _retificacoes_lidas: list = field(repr=False, default_factory=list)


def fatos_do_edital(edital, *, agora):
    """Leituras e regras do relatório do Edital, sem redação. Supõe `leitura_consistente` aberta.

    **`agora` é o instante da leitura, e não uma data de retrato** (FR-2521). Ele decide o que é
    prazo em curso, período aberto e versão vigente; os fatos são os gravados até a leitura.
    """
    original, vigente = _versoes(edital, agora)
    vigente = vigente or {}
    perfis_publicados = [p for p in vigente.get("profiles") or [] if isinstance(p, dict)]
    etapas = [e for e in vigente.get("stages") or [] if isinstance(e, dict)]
    primeira = Publicacao.objects.filter(edital=edital).order_by("publication_order").first()
    unidade = {
        "nome": getattr(primeira, "unidade_nome", "") or "",
        "cabecalho": tuple(getattr(primeira, "unidade_cabecalho", None) or ()),
        "local": getattr(primeira, "unidade_local", "") or "",
    }
    desfecho = desfechos([edital]).get(edital.id)
    desfecho_em = desfecho.em if desfecho and desfecho.do_edital else None

    # Inscrições — a leitura da Visão Geral (040), uma consulta.
    contagem = visao_geral.contagens_por_edital([edital]).get(
        edital.id, {"submetidas": {}, "rascunhos": {}}
    )
    enviadas = Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA)
    cadastros = enviadas.values("identity_subject").distinct().count()
    instantes = list(enviadas.order_by("submitted_at").values_list("submitted_at", flat=True))
    periodo = periodo_de_inscricoes(vigente, agora)
    evento_original = _evento_das_inscricoes(original)
    evento_vigente = _evento_das_inscricoes(vigente)
    termino_original = _quando((evento_original or {}).get("endAt"))
    termino_vigente = _quando((evento_vigente or {}).get("endAt"))
    prorrogado = bool(termino_original and termino_vigente and termino_vigente > termino_original)
    no_periodo_acrescentado = (
        sum(1 for instante in instantes if instante > termino_original) if prorrogado else 0
    )

    # Resultados vigentes, por marco e lista — a leitura da divulgação.
    publicacoes = list(
        PublicacaoResultado.objects.filter(edital=edital).values_list(
            "perfil_id", "marco_id", "lista_id"
        )
    )
    listas_por_marco = defaultdict(set)
    for perfil_id, marco_id, lista_id in publicacoes:
        listas_por_marco[(str(perfil_id), str(marco_id))].add(str(lista_id) if lista_id else None)
    atos = list(
        AtoDeOrdenacao.objects.filter(edital=edital, sucessores__isnull=True).values_list(
            "perfil_id", "marco_id", "lista_id"
        )
    )
    atos_por_marco = defaultdict(set)
    for perfil_id, marco_id, lista_id in atos:
        atos_por_marco[(str(perfil_id), str(marco_id))].add(str(lista_id) if lista_id else None)

    resultados = list(
        ResultadoEtapa.vigentes.filter(inscricao__edital=edital)
        .values("inscricao__profile_id", "etapa_id", "consequencia", "origem")
        .annotate(n=Count("id"))
    )
    por_etapa = defaultdict(Counter)
    for linha in resultados:
        chave = (str(linha["inscricao__profile_id"]), str(linha["etapa_id"]))
        sufixo = (
            "ocorrencia" if linha["origem"] == ResultadoEtapa.Origem.OCORRENCIA else "avaliacao"
        )
        por_etapa[chave][f"{linha['consequencia']}:{sufixo}"] += linha["n"]

    recursos_por_perfil, recursos_total = _recursos(edital)
    convocacoes_por_perfil, pendencias_de_convocacao, prazos_em_curso = _convocacoes(edital, agora)
    retificacoes_lidas = _retificacoes_publicadas(edital, agora)

    pendencias_de_resultado = []
    nao_publicas = []
    # Perfil sem inscrição enviada e sem rascunho não tem fato não público a proteger, e por isso
    # não entra na regra: ele mostraria só zeros, e o complemento esconderia outro Perfil à toa.
    populacoes = {
        str(p["id"]): contagem["submetidas"].get(str(p["id"]), 0)
        for p in perfis_publicados
        if contagem["submetidas"].get(str(p["id"]), 0) or contagem["rascunhos"].get(str(p["id"]), 0)
    }
    primarios, complementares, total_omitido = omitidos_por_complemento(
        populacoes, MINIMO_PARA_DETALHAR
    )
    omitidos = primarios | complementares
    linhas = []
    datas_definitivas = []
    marcos_declarados = 0
    marcos_definitivos = 0
    vagas_total = 0
    vagas_habilitadas = 0
    vagas_apuradas_algum = False
    vagas_apuradas = 0
    vagas_desatualizadas = 0
    perfis_com_marca = []
    # As marcas de procura são as da Visão Geral, pela regra dela — período encerrado, sem
    # inscrição ou razão abaixo de 1 —, e não uma segunda (040, FR-602).
    periodo_da_visao = visao_geral.situacao_do_periodo(vigente or None, agora)
    for perfil in perfis_publicados:
        perfil_id = str(perfil["id"])
        nome = perfil.get("name") or perfil.get("code") or "Perfil"
        inscricoes = contagem["submetidas"].get(perfil_id, 0)
        rascunhos = contagem["rascunhos"].get(perfil_id, 0)
        omitido = perfil_id in omitidos
        motivo = (
            FRASE_COMPLEMENTAR
            if perfil_id in complementares
            else FRASE_DE_PRIVACIDADE
            if omitido
            else ""
        )
        # Sem inscrição enviada e com o período fechado, não há o que classificar nem divulgar: o
        # marco não é previsto nem pendente, e nenhum ato o cumpriria (100, FR-2589, D-007).
        sem_inscricao = inscricoes == 0 and not periodo.aberto
        vagas = visao_geral.vagas_do_conteudo({"profiles": [perfil]}).total
        vagas_total += vagas

        # Classificação publicada e natureza, por marco e lista.
        classificadas = set()
        naturezas = set()
        linhas_das_listas = []
        tem_publicacao = False
        for marco in perfil.get("classificationMilestones") or []:
            marco_id = str(marco["id"])
            listas = listas_por_marco.get((perfil_id, marco_id), set())
            emitidas = atos_por_marco.get((perfil_id, marco_id), set())
            if sem_inscricao and not listas and not emitidas:
                continue
            marcos_declarados += 1
            definitivo_em_todas = bool(listas)
            for lista in sorted(listas | emitidas, key=lambda x: x or ""):
                publicacao = (
                    vigente_do_marco(edital=edital, marco_id=marco_id, lista_id=lista)
                    if lista in listas
                    else None
                )
                if publicacao is None:
                    definitivo_em_todas = False
                    continue
                tem_publicacao = True
                naturezas.add(publicacao.natureza)
                if publicacao.natureza != Natureza.DEFINITIVA:
                    definitivo_em_todas = False
                else:
                    datas_definitivas.append(publicacao.publicado_em)
                da_lista = set(
                    SituacaoDivulgada.objects.filter(
                        publicacao=publicacao, situacao=SituacaoDivulgada.Situacao.CLASSIFICADA
                    ).values_list("inscricao_id", flat=True)
                )
                classificadas |= da_lista
                vagas_da_lista = _vagas_da_lista(perfil, lista, vagas)
                linhas_das_listas.append(
                    LinhaDaLista(
                        marco=marco.get("name") or "",
                        lista=_nome_da_lista(perfil, lista),
                        classificadas=Numero.de(len(da_lista)),
                        vagas=Numero.de(vagas_da_lista),
                        natureza=publicacao.get_natureza_display(),
                    )
                )
            if definitivo_em_todas:
                marcos_definitivos += 1
            elif not listas:
                pendencias_de_resultado.append(
                    Pendencia(RESULTADO_NAO_DIVULGADO, perfil_id, marco=marco.get("name"))
                )
            else:
                pendencias_de_resultado.append(
                    Pendencia(DEFINITIVO_NAO_PUBLICADO, perfil_id, marco=marco.get("name"))
                )
            nao_publicas.extend(_pendencias_de_recurso(edital, marco, perfil_id))

        if tem_publicacao:
            numero_classificadas = Numero.de(len(classificadas))
            natureza = (
                "definitivo"
                if naturezas == {Natureza.DEFINITIVA}
                else "preliminar"
                if naturezas == {Natureza.PRELIMINAR}
                else "preliminar e definitivo"
            )
        elif sem_inscricao:
            numero_classificadas = Numero.nao_aplicavel("não se aplica: nenhuma inscrição enviada")
            natureza = ""
        else:
            numero_classificadas = Numero.nao_disponivel("ainda não divulgado")
            natureza = ""

        # Vagas com inscrição classificada e habilitada — a apuração vigente, por recorte.
        habilitadas, apurada, obsoleta = _ocupacao(edital, perfil)
        if obsoleta:
            nao_publicas.append(Pendencia(APURACAO_DESATUALIZADA, perfil_id))
        if vagas == 0:
            numero_habilitadas = Numero.nao_aplicavel("só cadastro de reserva")
        elif omitido:
            numero_habilitadas = Numero(ausencia=Ausencia(OMITIDO, motivo))
        elif obsoleta:
            numero_habilitadas = Numero.nao_disponivel("apuração desatualizada")
        elif not apurada:
            numero_habilitadas = Numero.nao_disponivel("ainda não apurada")
        else:
            numero_habilitadas = Numero.de(habilitadas)
        if apurada and not obsoleta:
            vagas_habilitadas += habilitadas
            vagas_apuradas_algum = True
        if vagas and obsoleta:
            vagas_desatualizadas += vagas
        elif vagas and apurada:
            vagas_apuradas += vagas
        marcas = visao_geral._marcas(
            periodo_da_visao,
            Numero.de(inscricoes),
            Numero.de(visao_geral._razao(inscricoes, vagas))
            if vagas
            else Numero.nao_aplicavel("só cadastro de reserva"),
        )
        if marcas:
            perfis_com_marca.append(
                (nome, inscricoes, vagas, tuple(marca.especie for marca in marcas))
            )

        convocacoes_do_perfil = convocacoes_por_perfil.get(perfil_id)
        recursos_do_perfil = recursos_por_perfil.get(perfil_id)
        linhas.append(
            LinhaDoPerfil(
                id=perfil_id,
                nome=nome,
                local=perfil.get("locality") or "",
                vagas=Numero.de(vagas),
                vagas_por_lista=_vagas_por_lista(perfil),
                reserva=_reserva(perfil),
                inscricoes=Numero.de(inscricoes, parcial=periodo.aberto),
                rascunhos=(
                    Numero(ausencia=Ausencia(OMITIDO, motivo)) if omitido else Numero.de(rascunhos)
                ),
                por_vaga=(
                    Numero.de(visao_geral._razao(inscricoes, vagas), parcial=periodo.aberto)
                    if vagas
                    else Numero.nao_aplicavel("só cadastro de reserva")
                ),
                classificadas=numero_classificadas,
                natureza_do_resultado=natureza,
                habilitadas_nas_vagas=numero_habilitadas,
                convocacoes=None if omitido else convocacoes_do_perfil,
                recursos=None if omitido else recursos_do_perfil,
                situacao_das_vagas=_situacao_das_vagas(
                    vagas, numero_habilitadas, convocacoes_do_perfil, motivo, perfil
                ),
                etapas=()
                if omitido
                else _linhas_das_etapas(perfil_id, _etapas_do_perfil(perfil, etapas), por_etapa),
                listas=tuple(linhas_das_listas),
                omitido=omitido,
                motivo_da_omissao=motivo,
            )
        )

    # Edital cancelado não terá resultado: o que falta divulgar deixou de ser providência.
    pendencias = [] if edital.status == Edital.Status.CANCELADO else list(pendencias_de_resultado)
    pendencias.extend(nao_publicas)
    pendencias.extend(pendencias_de_convocacao)
    if recursos_total.aguardando:
        pendencias.append(Pendencia(RECURSO_AGUARDANDO, None, recursos_total.aguardando))

    if edital.status == Edital.Status.CANCELADO:
        especie = INTERRUPCAO
    elif edital.status == Edital.Status.ENCERRADO and not pendencias:
        especie = ENCERRAMENTO
    else:
        especie = ACOMPANHAMENTO

    return FatosDoEdital(
        edital=edital,
        referencia=agora,
        unidade=unidade,
        especie=especie,
        desfecho_em=desfecho_em,
        perfis=linhas,
        pendencias=tuple(pendencias),
        vagas=vagas_total,
        inscricoes=sum(contagem["submetidas"].values()),
        rascunhos=sum(contagem["rascunhos"].values()),
        periodo_aberto=periodo.aberto,
        prorrogado=prorrogado,
        envios=tuple(instantes),
        marcos_declarados=marcos_declarados,
        marcos_definitivos=marcos_definitivos,
        datas_definitivas=tuple(datas_definitivas),
        vagas_habilitadas=vagas_habilitadas if vagas_apuradas_algum else None,
        vagas_apuradas=vagas_apuradas,
        vagas_desatualizadas=vagas_desatualizadas,
        retificacoes=len(retificacoes_lidas),
        perfis_com_marca=tuple(perfis_com_marca),
        convocacoes=_somar_convocacoes(convocacoes_por_perfil.values()),
        recursos=recursos_total,
        posteriores=(
            relatorio_trilha.posteriores(edital, desfecho_em, agora) if desfecho_em else []
        ),
        cadastros_distintos=cadastros,
        omitidos=frozenset(omitidos),
        complementares=frozenset(complementares),
        total_omitido=total_omitido,
        _perfis_publicados=perfis_publicados,
        _etapas=etapas,
        _original=original,
        _vigente=vigente,
        _primeira=primeira,
        _periodo=periodo,
        _evento_vigente=evento_vigente,
        _termino_original=termino_original if prorrogado else None,
        _no_periodo_acrescentado=no_periodo_acrescentado,
        _por_etapa=por_etapa,
        _prazos_em_curso=prazos_em_curso,
        _retificacoes_lidas=retificacoes_lidas,
    )


def omitidos_por_complemento(populacoes, limiar):
    """`(pequenos, complemento, total_omitido)` da supressão complementar (100, FR-2587, D-006).

    Omitir só o grupo pequeno deixava o fato voltar por subtração: total menos as linhas dos
    outros. Por isso, enquanto os omitidos somam menos que o limiar, entra também o grupo de menor
    população — desempate pelo identificador, para a mesma entrada dar sempre a mesma saída. Se
    nem todos juntos chegam ao limiar, o próprio total é omitido.
    """
    pequenos = frozenset(k for k, n in populacoes.items() if n < limiar)
    omitidos = set(pequenos)
    soma = sum(populacoes[k] for k in omitidos)
    restantes = sorted((n, k) for k, n in populacoes.items() if k not in omitidos)
    while omitidos and soma < limiar and restantes:
        n, k = restantes.pop(0)
        omitidos.add(k)
        soma += n
    return pequenos, frozenset(omitidos - pequenos), bool(omitidos) and soma < limiar


def texto_da_pendencia(pendencia):
    """A frase de uma pendência, sem o nome do Perfil — que a redação acrescenta ou cala."""
    n = pendencia.quantidade
    if pendencia.tipo == RESULTADO_NAO_DIVULGADO:
        return f"resultado de “{pendencia.marco}” ainda não divulgado"
    if pendencia.tipo == DEFINITIVO_NAO_PUBLICADO:
        return f"resultado definitivo de “{pendencia.marco}” ainda não publicado"
    if pendencia.tipo == REAVALIACAO_PENDENTE:
        return "reavaliação determinada por recurso ainda não concluída"
    if pendencia.tipo == PROVIDENCIA_PENDENTE:
        return "providência determinada por recurso ainda não cumprida"
    if pendencia.tipo == APURACAO_DESATUALIZADA:
        return "apuração das vagas desatualizada"
    if pendencia.tipo == CONVOCACAO_AGUARDANDO:
        ate = f", até {data_curta(pendencia.ate)}" if pendencia.ate else ""
        return f"{n} {_plural(n, 'convocação aguardando', 'convocações aguardando')} resposta{ate}"
    if pendencia.tipo == CONVOCACAO_VENCIDA:
        return (
            f"{n} {_plural(n, 'convocação', 'convocações')} com prazo encerrado sem registro de "
            "resposta"
        )
    if pendencia.tipo == RECURSO_AGUARDANDO:
        return f"{n} {_plural(n, 'recurso aguarda', 'recursos aguardam')} decisão"
    raise ValueError(pendencia.tipo)


def redigir_pendencias(fatos):
    """As frases das pendências, na ordem e com a privacidade do relatório do Edital (D-006)."""
    perfis = fatos._perfis_publicados
    nomes = {str(p["id"]): p.get("name") or p.get("code") or "Perfil" for p in perfis}
    redigidas = [
        f"{nomes.get(p.perfil_id, 'Perfil')}: {texto_da_pendencia(p)}"
        for p in fatos.pendencias
        if p.publica
    ]
    nao_publicas = [
        (p.perfil_id, texto_da_pendencia(p))
        for p in fatos.pendencias
        if not p.publica and p.tipo != RECURSO_AGUARDANDO
    ]
    if fatos.total_omitido:
        # Nem a quantidade: num Edital abaixo do limiar, quantas providências não públicas há já é
        # o fato que se protege (FR-2587).
        if any(not p.publica for p in fatos.pendencias):
            redigidas.append(f"providência pendente com {FRASE_DO_EDITAL}")
        return redigidas
    redigidas.extend(_redigir(nao_publicas, perfis, fatos.omitidos, fatos.complementares))
    redigidas.extend(
        texto_da_pendencia(p) for p in fatos.pendencias if p.tipo == RECURSO_AGUARDANDO
    )
    return redigidas


def montar(edital, *, agora, enderecos):
    """Os fatos, as leituras que só o documento individual usa, e a redação.

    Supõe a transação de `leitura_consistente` aberta por quem chama. Os testes passam `agora` fixo
    porque o relógio da suíte anda, e os fatos da fixture são todos anteriores a ele.
    """
    fatos = fatos_do_edital(edital, agora=agora)
    periodo = fatos._periodo
    serie = supervisao.serie_do_edital(edital, periodo, agora) if periodo.designado else ()
    pendencias = redigir_pendencias(fatos)
    posteriores = fatos.posteriores
    if fatos.total_omitido and posteriores:
        # O tipo de cada registro diria qual fato não público houve; fica a quantidade.
        posteriores = [
            (
                "registros na trilha",
                sum(n for _, n, _ in posteriores),
                min(primeira for _, _, primeira in posteriores),
            )
        ]
    retificacoes = _retificacoes(fatos._retificacoes_lidas)
    documentos = _documentos(edital, fatos._perfis_publicados, enderecos)
    publicados = _resultados_publicados(edital, agora)
    datas = _datas(
        edital,
        publicados,
        fatos._primeira,
        retificacoes,
        fatos._evento_vigente,
        fatos._termino_original,
        posteriores,
        fatos.desfecho_em,
        fatos.especie,
        agora,
        fatos._prazos_em_curso,
        fatos.total_omitido,
    )

    situacao_no_gps = {
        Edital.Status.PUBLICADO: "Publicado",
        Edital.Status.ENCERRADO: "Encerrado"
        + (f" em {data_curta(fatos.desfecho_em)}" if fatos.desfecho_em else ""),
        Edital.Status.CANCELADO: "Cancelado"
        + (f" em {data_curta(fatos.desfecho_em)}" if fatos.desfecho_em else ""),
    }.get(edital.status, edital.get_status_display())
    if pendencias:
        providencias = "; ".join(pendencias[:2]) + (
            f"; e mais {len(pendencias) - 2}" if len(pendencias) > 2 else ""
        )
    else:
        providencias = "nenhuma providência pendente registrada no GPS"

    relatorio = Relatorio(
        referencia=agora,
        edital=edital,
        unidade=fatos.unidade,
        especie=fatos.especie,
        situacao_no_gps=situacao_no_gps,
        providencias=providencias,
        pendencias=pendencias,
        posteriores=posteriores,
        frases=[],
        indicadores=[],
        perfis=fatos.perfis,
        serie=tuple(serie),
        termino_original=fatos._termino_original,
        no_periodo_acrescentado=fatos._no_periodo_acrescentado,
        periodo_aberto=fatos.periodo_aberto,
        retificacoes=retificacoes,
        recursos=fatos.recursos,
        datas=datas,
        documentos=documentos,
        endereco_da_selecao=enderecos.selecao(),
        cronograma=_cronograma(
            fatos._original,
            fatos._vigente,
            retificacoes,
            list(fatos.envios),
            fatos._por_etapa,
            fatos._etapas,
            publicados,
        ),
        cadastros_distintos=fatos.cadastros_distintos,
        desfecho_em=fatos.desfecho_em,
        total_omitido=fatos.total_omitido,
    )
    marcos = (fatos.marcos_definitivos, fatos.marcos_declarados, list(fatos.datas_definitivas))
    relatorio.indicadores = _indicadores(
        relatorio,
        vagas_total=fatos.vagas,
        inscricoes=fatos.inscricoes,
        rascunhos=fatos.rascunhos,
        marcos=marcos,
        vagas_habilitadas=fatos.vagas_habilitadas,
        convocacoes=fatos.convocacoes,
    )
    relatorio.frases = _frases(
        relatorio,
        vagas_total=fatos.vagas,
        inscricoes=fatos.inscricoes,
        instantes=list(fatos.envios),
        marcos=marcos,
        vagas_habilitadas=fatos.vagas_habilitadas,
        convocacoes=fatos.convocacoes,
    )
    relatorio.pontos_de_atencao = _pontos_de_atencao(relatorio, fatos.convocacoes)
    return relatorio


def _reserva(perfil):
    especie = perfil.get("reserveType") or "NONE"
    if especie == "UNLIMITED":
        return "sem limite"
    if especie == "LIMITED":
        return f"até {perfil.get('reserveLimit')}"
    return "não há"


def _linhas_das_etapas(perfil_id, etapas_do_perfil, por_etapa):
    linhas = []
    for etapa in etapas_do_perfil:
        contagem = por_etapa.get((perfil_id, str(etapa["id"])), Counter())
        habilitadas = contagem["HABILITADA:avaliacao"]
        eliminadas = contagem["ELIMINADA:avaliacao"]
        linhas.append(
            LinhaDaEtapa(
                nome=etapa.get("name") or "",
                regra=_regra_da_etapa(etapa),
                avaliadas=habilitadas + eliminadas,
                habilitadas=habilitadas + contagem["HABILITADA:ocorrencia"],
                eliminadas=eliminadas,
                por_ocorrencia=contagem["ELIMINADA:ocorrencia"],
                elimina=bool(etapa.get("eliminatory")),
                registrada=sum(contagem.values()) > 0,
            )
        )
    return tuple(linhas)


def _recursos(edital):
    """Por Perfil, pela situação — sem a listagem nominal de `recursos_do_edital` (R-007)."""
    contagem = defaultdict(Counter)
    for peca in (
        Recurso.objects.filter(inscricao__edital=edital)
        .prefetch_related("juizos", "decisoes")
        .select_related("inscricao")
    ):
        juizo = next(iter(peca.juizos.all()), None)
        decisao = next(iter(peca.decisoes.all()), None)
        perfil_id = str(peca.inscricao.profile_id)
        contagem[perfil_id]["apresentados"] += 1
        if decisao is not None:
            if decisao.especie == DecisaoRecurso.Especie.INDEFERIDO:
                contagem[perfil_id]["indeferidos"] += 1
            else:
                contagem[perfil_id]["deferidos"] += 1
        elif juizo is not None and not juizo.admitido:
            contagem[perfil_id]["nao_admitidos"] += 1
        else:
            contagem[perfil_id]["aguardando"] += 1

    def recursos_de(c):
        return Recursos(
            apresentados=c["apresentados"],
            nao_admitidos=c["nao_admitidos"],
            indeferidos=c["indeferidos"],
            deferidos=c["deferidos"],
            aguardando=c["aguardando"],
        )

    total = Counter()
    for c in contagem.values():
        total.update(c)
    return {k: recursos_de(c) for k, c in contagem.items()}, recursos_de(total)


def _pendencias_de_recurso(edital, marco, perfil_id):
    """Reavaliação e providência pendentes do marco — as perguntas da publicabilidade (R-006)."""
    marco_id = str(marco["id"])
    publicacoes = list(
        PublicacaoResultado.objects.filter(edital=edital, marco_id=marco_id).values_list(
            "id", flat=True
        )
    )
    pendencias = []
    if not publicacoes:
        return pendencias
    if recursos.reavaliacoes_pendentes_do_marco(edital=edital, marco=marco):
        pendencias.append(Pendencia(REAVALIACAO_PENDENTE, perfil_id))
    if recursos.providencias_pendentes_do_marco(
        edital=edital, marco_id=marco_id, marco=marco, publicacoes_do_marco=publicacoes
    ):
        pendencias.append(Pendencia(PROVIDENCIA_PENDENTE, perfil_id))
    return pendencias


def _ocupacao(edital, perfil):
    """`(habilitadas, apurada, obsoleta)` das apurações vigentes do Perfil.

    **Do último marco com apuração**, porque um Perfil com marco intermediário e final teria duas
    apurações da mesma vaga, e somá-las contaria a vaga duas vezes.
    """
    perfil_id = str(perfil["id"])
    marcos_apurados = set(
        str(m)
        for m in ApuracaoDeOcupacao.objects.filter(edital=edital, perfil_id=perfil_id).values_list(
            "marco_id", flat=True
        )
    )
    marco = None
    for candidato in perfil.get("classificationMilestones") or []:
        if str(candidato["id"]) in marcos_apurados:
            marco = candidato
    if marco is None:
        return 0, False, False
    habilitadas = 0
    apurada = False
    obsoleta = False
    for recorte in recortes_do_marco(edital=edital, perfil_id=perfil_id, marco_id=str(marco["id"])):
        if not recorte.get("publicadas"):
            continue
        if recorte["estado"] == nomes_da_ocupacao.OBSOLETO:
            obsoleta = True
        elif recorte["estado"] == nomes_da_ocupacao.VIGENTE:
            apurada = True
            habilitadas += recorte.get("ocupadas") or 0
    return habilitadas, apurada, obsoleta


def _convocacoes(edital, agora):
    """A cadeia por Perfil, as pendências de convocação e os prazos em curso (D-006).

    Nunca por lista: a convocação da única vaga reservada, dita por lista, apontaria a primeira
    pessoa da lista publicada. Os prazos são os das convocações **vigentes** sem desfecho — as
    mesmas que viram pendência —, para que as datas principais não digam outro número.
    """
    todas = list(
        Convocacao.objects.filter(edital=edital).prefetch_related(
            "sucessoras", "desfechos__sucessores"
        )
    )
    por_perfil = defaultdict(list)
    for c in convocacao.vigentes(todas):
        por_perfil[str(c.perfil_id)].append(c)
    resultado = {}
    pendencias = []
    prazos = []
    for perfil_id, lista in por_perfil.items():
        aceitas = aguardando = vencidas = 0
        prazo = None
        outros = Counter()
        for c in lista:
            desfecho = _desfecho_vigente(c)
            if desfecho is not None:
                if desfecho.especie == nomes_da_convocacao.ACEITE:
                    aceitas += 1
                else:
                    outros[ROTULOS_DOS_DESFECHOS.get(desfecho.especie, desfecho.especie)] += 1
            elif c.vencimento is not None and c.vencimento <= agora:
                vencidas += 1
            else:
                aguardando += 1
                if c.vencimento:
                    prazos.append(c.vencimento)
                if c.vencimento and (prazo is None or c.vencimento > prazo):
                    prazo = c.vencimento
        resultado[perfil_id] = Convocacoes(
            realizadas=len(lista),
            aceitas=aceitas,
            aguardando=aguardando,
            aguardando_ate=prazo,
            vencidas=vencidas,
            outros=tuple(sorted(outros.items())),
        )
        if aguardando:
            pendencias.append(Pendencia(CONVOCACAO_AGUARDANDO, perfil_id, aguardando, ate=prazo))
        if vencidas:
            pendencias.append(Pendencia(CONVOCACAO_VENCIDA, perfil_id, vencidas))
    return resultado, pendencias, sorted(prazos)


def _redigir(nao_publicas, perfis, omitidos, complementares=frozenset()):
    """As pendências de fato não público, com o nome do Perfil — menos o do Perfil omitido.

    O Perfil com menos de cinco inscrições tem o detalhe não público omitido (D-006); nomeá-lo aqui
    devolveria à primeira página o que a tabela esconde. As dele viram uma linha só, sem nome, e
    continuam contando para a espécie.
    """
    nomes = {str(p["id"]): p.get("name") or "Perfil" for p in perfis}
    redigidas = [
        f"{nomes.get(pid, 'Perfil')}: {texto}" for pid, texto in nao_publicas if pid not in omitidos
    ]
    escondidas = sum(1 for pid, _ in nao_publicas if pid in omitidos)
    if escondidas:
        onde = (
            "em perfis com detalhe omitido por privacidade"
            if complementares
            else f"em perfil com menos de {MINIMO_PARA_DETALHAR} inscrições (detalhe omitido)"
        )
        redigidas.append(
            f"{escondidas} {_plural(escondidas, 'providência pendente', 'providências pendentes')}"
            f" {onde}"
        )
    return redigidas


def _desfecho_vigente(c):
    for desfecho in c.desfechos.all():
        if not desfecho.sucessores.all():
            return desfecho
    return None


def _somar_convocacoes(itens):
    itens = list(itens)
    prazos = [c.aguardando_ate for c in itens if c.aguardando_ate]
    return Convocacoes(
        realizadas=sum(c.realizadas for c in itens),
        aceitas=sum(c.aceitas for c in itens),
        aguardando=sum(c.aguardando for c in itens),
        aguardando_ate=max(prazos) if prazos else None,
        vencidas=sum(c.vencidas for c in itens),
    )


def _situacao_das_vagas(vagas, habilitadas, convocacoes, motivo_da_omissao, perfil):
    if vagas == 0:
        if (perfil.get("reserveType") or "NONE") != "NONE":
            return "Sem vaga imediata; os classificados podem ser chamados se surgir vaga"
        return "Sem vaga imediata"
    if motivo_da_omissao:
        return motivo_da_omissao
    if not habilitadas.existe:
        return f"Vagas: {habilitadas.ausencia.motivo}"
    partes = [f"{habilitadas.valor} de {vagas} com inscrição classificada e habilitada"]
    if convocacoes:
        if convocacoes.aceitas:
            partes.append(
                f"{convocacoes.aceitas} "
                f"{_plural(convocacoes.aceitas, 'convocação aceita', 'convocações aceitas')}"
            )
        if convocacoes.aguardando:
            ate = (
                f" até {dia_e_mes(convocacoes.aguardando_ate)}"
                if convocacoes.aguardando_ate
                else ""
            )
            partes.append(f"{convocacoes.aguardando} aguardando resposta{ate}")
        if convocacoes.vencidas:
            partes.append(f"{convocacoes.vencidas} com prazo encerrado sem registro")
        for rotulo, n in convocacoes.outros:
            partes.append(f"{n} {_minuscula(rotulo)}")
    return "; ".join(partes)


def _retificacoes_publicadas(edital, agora):
    """As Retificações publicadas até `agora`, em ordem — lidas uma vez, nos fatos (100)."""
    return list(
        Retificacao.objects.filter(
            edital=edital,
            status=Retificacao.Status.PUBLICADA,
            publication__published_at__lte=agora,
        )
        .select_related("base_snapshot", "publication")
        .prefetch_related("alteracoes")
        .order_by("publication__published_at")
    )


def _retificacoes(publicadas):
    from processo_seletivo.interface.views import _alteracoes_legiveis

    lidas = []
    for numero, retificacao in enumerate(publicadas, 1):
        lidas.append(
            Retificacao_(
                numero=numero,
                publicada_em=retificacao.publication.published_at,
                justificativa=retificacao.justification,
                alteracoes=tuple(_alteracoes_legiveis(retificacao)),
            )
        )
    return lidas


def _rotulo_do_resultado(perfis, publicacao):
    for perfil in perfis:
        if str(perfil["id"]) == str(publicacao.perfil_id):
            lista = _nome_da_lista(perfil, publicacao.lista_id)
            return f"{perfil.get('name')}, {_minuscula(lista)}"
    return "Perfil"


def _documentos(edital, perfis, enderecos):
    """Os documentos publicados, com o endereço público e o resumo (FR-2539, FR-2543)."""
    lista = []
    selecao = enderecos.selecao()
    for documento in (
        DocumentoPublicado.objects.filter(publicacao__edital=edital)
        .select_related("publicacao")
        .order_by("publicacao__publication_order")
    ):
        ordem = documento.publicacao.publication_order
        lista.append(
            Documento(
                titulo=f"Edital {edital.number}/{edital.year}"
                if ordem == 1
                else f"Retificação nº {ordem - 1}",
                publicado_em=documento.publicacao.published_at,
                sha256=documento.document_hash,
                endereco=selecao,
            )
        )
    for documento in (
        DocumentoDoResultado.objects.filter(publicacao__edital=edital)
        .select_related("publicacao")
        .prefetch_related("publicacao__sucessoras")
        .order_by("publicacao__publicado_em", "publicacao__perfil_id", "publicacao__lista_id")
    ):
        publicacao = documento.publicacao
        lista.append(
            Documento(
                titulo=f"{publicacao.get_natureza_display()} — "
                f"{_rotulo_do_resultado(perfis, publicacao)}",
                publicado_em=publicacao.publicado_em,
                sha256=documento.documento_hash,
                endereco=enderecos.resultado(publicacao.pk),
                resultado_vigente=not publicacao.sucessoras.all(),
            )
        )
    return lista


def _datas(
    edital,
    publicados,
    primeira,
    retificacoes,
    evento,
    termino_original,
    posteriores,
    desfecho_em,
    especie,
    agora,
    prazos_em_curso,
    total_omitido=False,
):
    """As datas principais, cada uma com a natureza (FR-2538).

    Com o Edital abaixo do limiar, saem as datas de julgamento e de convocação: elas diriam que
    houve recurso e convocação, que é o fato não público que se protege (100, FR-2587).
    """
    datas = []
    if primeira is not None:
        datas.append(Data(primeira.published_at, "Edital publicado", "publicação"))
    for r in retificacoes:
        datas.append(Data(r.publicada_em, f"Retificação nº {r.numero} publicada", "publicação"))
    if evento:
        inicio, fim = _quando(evento.get("startAt")), _quando(evento.get("endAt"))
        texto = "Período de inscrições"
        if termino_original:
            texto += f"; o Edital previa o fim em {dia_e_mes(termino_original)}"
        if inicio:
            datas.append(Data(inicio, texto, "previsto", ate=fim))
    # Os demais eventos previstos ficam no cronograma do anexo: aqui, ao lado dos atos, eles
    # pareceriam ter acontecido na data (FR-2538).
    for natureza, texto in (
        (Natureza.PRELIMINAR, "Resultado preliminar publicado"),
        (Natureza.DEFINITIVA, "Resultado definitivo publicado"),
    ):
        for instante in publicados.get(natureza, ()):
            datas.append(Data(instante, texto, "publicação"))
    julgados = (
        []
        if total_omitido
        else sorted(
            DecisaoRecurso.objects.filter(
                recurso__inscricao__edital=edital, decidido_em__lte=agora
            ).values_list("decidido_em", flat=True)
        )
    )
    if julgados:
        datas.append(
            Data(
                julgados[0],
                "Recursos julgados",
                "registrado",
                ate=julgados[-1] if julgados[-1].date() != julgados[0].date() else None,
            )
        )
    convocadas = (
        []
        if total_omitido
        else sorted(
            Convocacao.objects.filter(
                inscricao__edital=edital, criado_em__lte=agora, convocacao_anterior__isnull=True
            ).values_list("criado_em", flat=True)
        )
    )
    if convocadas:
        datas.append(Data(convocadas[0], "Convocações para as vagas", "registrado"))
    if desfecho_em:
        texto = "Edital cancelado no GPS" if especie == INTERRUPCAO else "Edital encerrado no GPS"
        datas.append(Data(desfecho_em, texto, "registrado"))
        for rotulo, _, primeira in posteriores:
            datas.append(
                Data(
                    primeira,
                    f"{rotulo[:1].upper()}{rotulo[1:]}, depois do encerramento",
                    "registrado",
                )
            )
    for vencimento in [] if total_omitido else prazos_em_curso:
        if vencimento > agora:
            datas.append(Data(vencimento, "Fim de prazo de resposta a convocação", "prazo"))
    return sorted(datas, key=lambda d: d.dia)


def _resultados_publicados(edital, agora):
    """Os dias com publicação de resultado até `agora`, por natureza — uma consulta, um por dia."""
    por_natureza = defaultdict(dict)
    for natureza, instante in PublicacaoResultado.objects.filter(
        edital=edital, publicado_em__lte=agora
    ).values_list("natureza", "publicado_em"):
        dia = instante.astimezone(ZONA).date()
        por_natureza[natureza][dia] = min(instante, por_natureza[natureza].get(dia, instante))
    return {natureza: sorted(dias.values()) for natureza, dias in por_natureza.items()}


def _natureza_do_evento(evento):
    """A natureza de resultado que o evento do cronograma anuncia, pelo nome que o Edital lhe deu.

    O cronograma do Edital é texto livre, sem ligação estrutural com o marco nem com a publicação.
    O nome do evento é comparado ao rótulo que o próprio domínio dá às naturezas ("Resultado
    preliminar", "Resultado definitivo"), sem acento e sem caixa; "resultado final" é o sinônimo
    que os Editais usam para o definitivo. Evento de outro nome fica sem ato registrado, como antes.
    """
    nome = unicodedata.normalize("NFKD", str(evento.get("type") or "")).lower()
    nome = "".join(c for c in nome if not unicodedata.combining(c))
    if "resultado" not in nome:
        return None
    if "preliminar" in nome:
        return Natureza.PRELIMINAR
    if "definitiv" in nome or "final" in nome:
        return Natureza.DEFINITIVA
    return None


def _publicacao_registrada(dias):
    """A publicação como ato registrado — e não como execução: a avaliação pode ter sido antes."""
    if not dias:
        return "nenhuma publicação até a data dos dados"
    if len(dias) == 1:
        return f"publicado em {dia_e_mes(dias[0])}"
    return f"publicado de {dia_e_mes(dias[0])} a {dia_e_mes(dias[-1])}"


def _cronograma(original, vigente, retificacoes, instantes, por_etapa, etapas, publicados=None):
    """Previsto no Edital × após as Retificações × ato registrado, por evento (FR-2542).

    O ato registrado de um evento de resultado é a publicação daquela natureza, que a linha do
    tempo da camada executiva também lista: sem isso, a coluna dizia "—" ao lado de um resultado
    que o próprio relatório mostrava publicado (homologação de 24/10/2026).
    """
    publicados = publicados or {}

    def periodo(evento):
        if not evento:
            return "—"
        inicio, fim = _quando(evento.get("startAt")), _quando(evento.get("endAt"))
        if inicio and fim and inicio.date() != fim.date():
            return f"{dia_e_mes(inicio)} a {dia_e_mes(fim)}"
        return dia_e_mes(inicio) if inicio else "—"

    originais = {str(e["id"]): e for e in (original or {}).get("schedule") or []}
    linhas = []
    etapa_do_evento = {str(e.get("scheduleEventId")): e for e in etapas if e.get("scheduleEventId")}
    for evento in sorted(vigente.get("schedule") or [], key=lambda e: e.get("order") or 0):
        identidade = str(evento["id"])
        previsto = periodo(originais.get(identidade))
        agora_e = periodo(evento)
        if evento.get("status") == "CANCELADO":
            agora_e = "cancelado"
        retificado = agora_e if agora_e != previsto else "sem alteração"
        registrado = "—"
        if evento.get("isRegistrationPeriod") and instantes:
            registrado = f"envios de {dia_e_mes(instantes[0])} a {dia_e_mes(instantes[-1])}"
        elif identidade in etapa_do_evento:
            etapa = etapa_do_evento[identidade]
            consolidados = [
                n for (perfil, etapa_id), n in por_etapa.items() if etapa_id == str(etapa["id"])
            ]
            if consolidados:
                registrado = "resultados da etapa consolidados"
        elif (natureza := _natureza_do_evento(evento)) is not None:
            registrado = _publicacao_registrada(publicados.get(natureza, ()))
        linhas.append(
            LinhaDoCronograma(
                evento=evento.get("type") or evento.get("description") or "",
                previsto=previsto,
                retificado=retificado,
                registrado=registrado,
            )
        )
    return linhas


# --- Indicadores, frases e pontos de atenção ------------------------------------------------------


def _indicadores(
    relatorio, *, vagas_total, inscricoes, rascunhos, marcos, vagas_habilitadas, convocacoes
):
    perfis = relatorio.perfis
    com_vaga = [p for p in perfis if p.vagas.valor]
    so_reserva = [p.nome for p in perfis if not p.vagas.valor]
    base_vagas = (
        f"em {len(com_vaga)} de {len(perfis)} {_plural(len(perfis), 'perfil', 'perfis')}"
        + (f"; {', '.join(so_reserva)}: só cadastro de reserva" if so_reserva else "")
    )
    inscricoes_com_vaga = sum(p.inscricoes.valor for p in com_vaga)
    if vagas_total:
        por_vaga = Numero.de(
            visao_geral._razao(inscricoes_com_vaga, vagas_total), parcial=relatorio.periodo_aberto
        )
        base_por_vaga = (
            f"{inscricoes_com_vaga} {_plural(inscricoes_com_vaga, 'inscrição', 'inscrições')} "
            f"para {vagas_total} {_plural(vagas_total, 'vaga', 'vagas')}, nos perfis com vaga "
            "imediata"
        )
    else:
        por_vaga = Numero.nao_aplicavel("não há vaga imediata")
        base_por_vaga = "só cadastro de reserva"
    definitivos, declarados, datas = marcos
    base_resultados = (
        f"publicados em {data_curta(min(datas))}"
        if datas and min(datas).date() == max(datas).date()
        else f"publicados de {data_curta(min(datas))} a {data_curta(max(datas))}"
        if datas
        else "nenhum resultado definitivo publicado ainda"
    )
    omitido = Numero(ausencia=Ausencia(OMITIDO, FRASE_DO_EDITAL))
    if vagas_total == 0:
        habilitadas = Numero.nao_aplicavel("não há vaga imediata")
    elif relatorio.total_omitido:
        habilitadas = omitido
    elif vagas_habilitadas is None:
        habilitadas = Numero.nao_disponivel("ainda não apurada")
    else:
        habilitadas = Numero.de(vagas_habilitadas)
    if relatorio.total_omitido:
        aceitas = omitido
        base_aceitas = FRASE_DO_EDITAL
    elif convocacoes.realizadas:
        aceitas = Numero.de(convocacoes.aceitas)
        partes = []
        if convocacoes.aguardando:
            ate = (
                f" até {data_curta(convocacoes.aguardando_ate)}"
                if convocacoes.aguardando_ate
                else ""
            )
            partes.append(f"{convocacoes.aguardando} aguardando resposta{ate}")
        if convocacoes.vencidas:
            partes.append(f"{convocacoes.vencidas} com prazo encerrado sem registro")
        base_aceitas = "; ".join(partes) or "todas com resposta registrada"
    else:
        aceitas = Numero.nao_disponivel("nenhuma convocação registrada")
        base_aceitas = "nenhuma convocação registrada"
    return [
        Indicador("vagas imediatas", Numero.de(vagas_total), base_vagas),
        Indicador(
            "inscrições enviadas",
            Numero.de(inscricoes, parcial=relatorio.periodo_aberto),
            f"outras {rascunhos} iniciadas e não enviadas"
            + ("; o período de inscrições segue aberto" if relatorio.periodo_aberto else ""),
        ),
        Indicador("inscrições por vaga", por_vaga, base_por_vaga),
        Indicador(
            "resultados definitivos publicados",
            Numero.de(definitivos),
            base_resultados,
            de=declarados,
        ),
        Indicador(
            "vagas com inscrição classificada e habilitada",
            habilitadas,
            "dentro do número de vagas e habilitada em todas as etapas. Não é matrícula",
            de=vagas_total if vagas_total and not relatorio.total_omitido else None,
        ),
        Indicador(
            "convocações aceitas",
            aceitas,
            base_aceitas,
            de=None if relatorio.total_omitido else convocacoes.realizadas or None,
        ),
    ]


def _frases(
    relatorio, *, vagas_total, inscricoes, instantes, marcos, vagas_habilitadas, convocacoes
):
    """A visão geral, frase a frase: cada uma com condição e fonte (FR-2527)."""
    frases = []
    perfis = relatorio.perfis
    if relatorio.especie == INTERRUPCAO:
        quando = f" em {data_curta(relatorio.desfecho_em)}" if relatorio.desfecho_em else ""
        frases.append(f"O Edital foi cancelado{quando}.")
    com_vaga = [p for p in perfis if p.vagas.valor]
    so_reserva = [p for p in perfis if so_cadastro_de_reserva(p)]
    if com_vaga:
        if len(com_vaga) == 1:
            p = com_vaga[0]
            desdobramento = ""
            if len(p.vagas_por_lista) > 1:
                partes = []
                for lista, n in p.vagas_por_lista:
                    if lista == "Ampla concorrência":
                        partes.append(f"{n} de ampla concorrência")
                    else:
                        partes.append(f"{n} reservada{'s' if n > 1 else ''} a {_minuscula(lista)}")
                desdobramento = " — " + " e ".join(partes) + " —"
            frase = (
                f"O Edital ofereceu {vagas_total} "
                f"{_plural(vagas_total, 'vaga imediata', 'vagas imediatas')} para "
                f"{p.nome}{desdobramento}"
            )
        else:
            frase = (
                f"O Edital ofereceu {vagas_total} vagas imediatas em {len(com_vaga)} perfis de vaga"
            )
        if so_reserva:
            frase += f" e abriu cadastro de reserva para {', '.join(p.nome for p in so_reserva)}"
        frases.append(frase + ".")
    elif so_reserva:
        frases.append(
            f"O Edital abriu cadastro de reserva para {', '.join(p.nome for p in so_reserva)}, "
            "sem vaga imediata."
        )
    if inscricoes:
        frase = (
            f"Recebeu {inscricoes} {_plural(inscricoes, 'inscrição', 'inscrições')}"
            f" entre {data_curta(instantes[0])} e {data_curta(instantes[-1])}"
        )
        if relatorio.periodo_aberto:
            frase += ", e o período de inscrições segue aberto"
        frases.append(frase + ".")
    elif relatorio.periodo_aberto:
        frases.append("Ainda não recebeu inscrição enviada, e o período segue aberto.")
    else:
        frases.append("Não recebeu inscrição enviada.")
    if relatorio.termino_original:
        n = relatorio.no_periodo_acrescentado
        chegaram = _plural(n, "inscrição chegou", "inscrições chegaram")
        frases.append(
            f"O prazo de inscrição foi prorrogado, e {n} {chegaram} no período acrescentado."
        )
    definitivos, declarados, datas = marcos
    rec = relatorio.recursos
    if definitivos and declarados:
        quando = (
            f"em {data_curta(min(datas))}"
            if min(datas).date() == max(datas).date()
            else f"entre {data_curta(min(datas))} e {data_curta(max(datas))}"
        )
        alcance = (
            "Os resultados definitivos de todos os perfis saíram"
            if definitivos == declarados and len(perfis) > 1
            else "O resultado definitivo saiu"
            if definitivos == declarados
            else f"Saíram {definitivos} dos {declarados} resultados definitivos previstos,"
        )
        frase = f"{alcance} {quando}"
        if rec.apresentados and not rec.aguardando and not relatorio.total_omitido:
            deferidos = (
                "nenhum deles deferido"
                if not rec.deferidos
                else f"{rec.deferidos} {_plural(rec.deferidos, 'deferido', 'deferidos')}"
            )
            frase += (
                f", depois do julgamento de {rec.apresentados} "
                f"{_plural(rec.apresentados, 'recurso', 'recursos')}, {deferidos}"
            )
        frases.append(frase + ".")
    if rec.aguardando and not relatorio.total_omitido:
        frases.append(
            f"{rec.aguardando} {_plural(rec.aguardando, 'recurso aguarda', 'recursos aguardam')} "
            "decisão."
        )
    if vagas_total and vagas_habilitadas is not None and not relatorio.total_omitido:
        if vagas_habilitadas == vagas_total:
            sujeito = _plural(vagas_total, "A vaga imediata tem", f"As {vagas_total} vagas têm")
            frase = f"{sujeito} inscrição classificada e habilitada"
        else:
            frase = (
                f"{vagas_habilitadas} das {vagas_total} vagas imediatas têm inscrição classificada "
                "e habilitada"
            )
        if convocacoes.realizadas:
            partes = []
            if convocacoes.aceitas:
                aceitas = _plural(
                    convocacoes.aceitas, "convocação foi aceita", "convocações foram aceitas"
                )
                partes.append(f"{convocacoes.aceitas} {aceitas}")
            if convocacoes.aguardando:
                ate = (
                    f" até {data_curta(convocacoes.aguardando_ate)}"
                    if convocacoes.aguardando_ate
                    else ""
                )
                partes.append(
                    f"{convocacoes.aguardando} "
                    f"{_plural(convocacoes.aguardando, 'aguarda', 'aguardam')} resposta{ate}"
                )
            if convocacoes.vencidas:
                partes.append(
                    f"{convocacoes.vencidas} "
                    f"{_plural(convocacoes.vencidas, 'teve', 'tiveram')} o prazo encerrado sem "
                    "registro de resposta"
                )
            if partes:
                frase += ": " + ", e ".join(partes)
        frases.append(frase + ".")
    return frases


def _pontos_de_atencao(relatorio, convocacoes):
    """No máximo três, nesta ordem (FR-2534)."""
    pontos = []
    if relatorio.edital.status == Edital.Status.ENCERRADO and relatorio.pendencias:
        pontos.append(
            (
                "O Edital está encerrado no GPS, mas ainda há providência pendente.",
                "; ".join(relatorio.pendencias) + ".",
            )
        )
    elif relatorio.pendencias:
        pontos.append(("Providências em curso.", "; ".join(relatorio.pendencias) + "."))
    if relatorio.posteriores:
        total = sum(n for _, n, _ in relatorio.posteriores)
        itens = ", ".join(
            f"{n} {rotulo} em {data_curta(primeira)}"
            for rotulo, n, primeira in relatorio.posteriores
        )
        pontos.append(
            (
                f"A trilha de auditoria tem {total} {_plural(total, 'registro', 'registros')} "
                "depois do encerramento.",
                f"{itens}. Um relatório emitido antes disso mostraria outros números.",
            )
        )
    if relatorio.total_omitido or convocacoes.realizadas or relatorio.especie == ENCERRAMENTO:
        pontos.append(
            (
                "O GPS não registra matrículas.",
                "Este relatório mostra convocações aceitas, e não matrículas efetivadas. A "
                "confirmação vem do registro acadêmico.",
            )
        )
    return pontos[:3]


@dataclass(frozen=True)
class Semana:
    inicio: object
    fim: object
    envios: int
    #: A semana em que terminava o prazo original, quando houve prorrogação (FR-2536).
    termino_original: bool = False
    #: Inteiramente depois do término original: o período acrescentado.
    acrescentada: bool = False


def semanas(relatorio):
    """A série diária em blocos de sete dias, a contar do primeiro dia do período (FR-2536)."""
    pontos = list(relatorio.serie)
    original = (
        relatorio.termino_original.astimezone(ZONA).date() if relatorio.termino_original else None
    )
    blocos = []
    for indice in range(0, len(pontos), 7):
        bloco = pontos[indice : indice + 7]
        inicio, fim = bloco[0].dia, bloco[-1].dia
        blocos.append(
            Semana(
                inicio=inicio,
                fim=fim,
                envios=sum(p.quantidade for p in bloco),
                termino_original=bool(original and inicio <= original <= fim),
                acrescentada=bool(original and inicio > original),
            )
        )
    return blocos


def texto_do_indicador(indicador):
    """O valor como a página e o PDF o escrevem: "2 de 2", "13,0", ou o motivo da ausência."""
    valor = interpretar(indicador.numero)
    if indicador.numero.existe and indicador.de is not None:
        valor = f"{valor} de {indicador.de}"
    if indicador.numero.existe and indicador.numero.parcial:
        valor = f"{valor} (parcial)"
    return valor


def reservadas_do_perfil(perfil):
    """As vagas imediatas do Perfil em listas reservadas — o resto é da ampla concorrência."""
    return sum(n for lista, n in perfil.vagas_por_lista if lista != "Ampla concorrência")


def so_cadastro_de_reserva(perfil):
    """Sem vaga imediata e com cadastro de reserva declarado."""
    return not perfil.vagas.valor and perfil.reserva != "não há"


def texto_das_vagas(perfil):
    """A célula de vagas do Perfil: o total e quantas são reservadas, ou o cadastro de reserva."""
    if not perfil.vagas.valor:
        return f"cadastro de reserva, {perfil.reserva}"
    reservadas = reservadas_do_perfil(perfil)
    if not reservadas:
        return str(perfil.vagas.valor)
    ampla = perfil.vagas.valor - reservadas
    rotulo = _plural(reservadas, "reservada", "reservadas")
    return f"{perfil.vagas.valor} ({ampla} ampla, {reservadas} {rotulo})"


def interpretar(numero):
    """O número como texto, ou o motivo da ausência — nunca 0 no lugar do que não existe."""
    if numero.existe:
        valor = numero.valor
        if isinstance(valor, Decimal):
            return _decimal_br(valor)
        return str(valor)
    return numero.ausencia.motivo


__all__ = [
    "ACOMPANHAMENTO",
    "ENCERRAMENTO",
    "ESTADOS_COM_RELATORIO",
    "INTERRUPCAO",
    "NAO_APLICAVEL",
    "NAO_DISPONIVEL",
    "NAO_REGISTRADO",
    "OMITIDO",
    "Relatorio",
    "interpretar",
    "leitura_consistente",
    "ler",
    "montar",
    "proxima_emissao",
]
