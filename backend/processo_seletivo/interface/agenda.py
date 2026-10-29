"""A Agenda dos Editais: os cronogramas publicados e vigentes da unidade, no tempo (101).

**Este módulo só lê.** Nenhum `save`, `create`, `update` ou `delete` nasce aqui. A agenda é uma
**projeção** da versão consolidada vigente de cada Edital, montada a cada leitura e descartada
depois dela (`D-001`): uma tabela de datas seria uma segunda fonte para o que o Edital publicou, e
teria de acompanhar o relógio e as Retificações.

**A fonte não é `EventoCronograma`.** Aquela é a linha de elaboração: a Retificação grava na versão
consolidada sem escrever de volta, e o Evento acrescentado por Retificação nem tem linha. A leitura
é a de `versoes_vigentes`, a forma em lote do resolvedor que a supervisão e o portal já usam.

**A régua de fase não é copiada.** A fase de cada Evento vem de `editais/domain/fase_do_evento.py`
e de `calendario.py`; o que este módulo faz é dizê-la sem afirmar execução (`D-006`): a régua chama
de concluído o que tem data passada, e a agenda lê o cronograma, e não os atos.

As derivações são funções puras sobre o conteúdo publicado, para que se testem sem banco; só `ler`
consulta, e num número fixo de consultas (`FR-2646`).
"""

from calendar import Calendar
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from uuid import UUID

from django.db.models import Min
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode

from processo_seletivo.editais.domain import calendario
from processo_seletivo.editais.domain.fase_do_evento import (
    descricao_do_evento,
    esta_cancelado,
    eventos_do_conteudo,
    fase_do_evento,
    instantes_do_evento,
)
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import versoes_vigentes
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.tempo import ZONA

MES, PROXIMOS = "mes", "proximos"
VISOES = (MES, PROXIMOS)
JANELAS = (7, 30)

# As três espécies do filtro (`D-007`). Saem de marcas estruturais publicadas — a do período de
# inscrições e o vínculo de uma Etapa —, e nunca do texto da espécie, que é livre.
INSCRICOES, ETAPA, DEMAIS = "inscricoes", "etapa", "demais"
ESPECIES = {
    INSCRICOES: "Período de inscrições",
    ETAPA: "Ligados a uma Etapa",
    DEMAIS: "Demais Eventos",
}

PONTUAL, ABERTURA, ENCERRAMENTO = "pontual", "abertura", "encerramento"

# A fase, dita pela agenda (`D-006`). *Data passada*, e não *concluído*: um *Resultado preliminar*
# com data passada não prova que o resultado saiu.
POR_VIR, EM_CURSO, PASSADA = "por_vir", "em_curso", "passada"
#
# *Em curso* só se diz do que corre no instante da leitura (`FR-2671`): de um dia qualquer, o
# período o *abrange*.
ROTULO_DA_FASE = {POR_VIR: "", EM_CURSO: "em curso agora, pelo cronograma", PASSADA: "data passada"}
ROTULO_DA_FASE_DO_PERIODO = {
    POR_VIR: "ainda não começou",
    EM_CURSO: "em curso hoje, pelo cronograma",
    PASSADA: "já passou",
}
FASE_DA_REGUA = {
    calendario.PLANEJADO: POR_VIR,
    calendario.EM_ANDAMENTO: EM_CURSO,
    calendario.CONCLUIDO: PASSADA,
}

# Publicado e encerrado; o cancelado sai, como na vitrine (`D-009`).
SITUACOES_NA_AGENDA = (Edital.Status.PUBLICADO, Edital.Status.ENCERRADO)

NOMES_NA_CELULA = 2
# Acima disto o dia se agrupa por Edital (`FR-2630`): dez descrições soltas não dizem de quem são.
AGRUPAR_ACIMA_DE = 8

MESES = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)
# Na ordem de `date.weekday()`, que começa na segunda.
DIAS_DA_SEMANA = (
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
)
# A ordem das colunas da grade: domingo primeiro, como os calendários brasileiros (`D-010`).
COLUNAS = (
    ("dom", "domingo"),
    ("seg", "segunda-feira"),
    ("ter", "terça-feira"),
    ("qua", "quarta-feira"),
    ("qui", "quinta-feira"),
    ("sex", "sexta-feira"),
    ("sáb", "sábado"),
)


# ---------------------------------------------------------------------------
# As formas
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EditalDaAgenda:
    id: str
    numero: str
    ano: int
    processo: str
    status: str

    @classmethod
    def de(cls, edital):
        return cls(
            id=str(edital.pk),
            numero=edital.number,
            ano=edital.year,
            processo=edital.processo.title,
            status=edital.status,
        )

    @property
    def rotulo(self):
        return f"Edital {self.numero}/{self.ano}"

    @property
    def encerrado(self):
        return self.status == Edital.Status.ENCERRADO

    @property
    def chave_de_ordem(self):
        # O número é texto, e há Edital cujo número não é só dígito: a ordem numérica vale onde
        # ela existe, e o texto desempata o resto.
        numerico = self.numero.isdigit()
        return (self.ano, 0 if numerico else 1, int(self.numero) if numerico else 0, self.numero)


@dataclass(frozen=True)
class Marco:
    """Um ponto da agenda: o Evento pontual, ou a abertura ou o encerramento de um período."""

    dia: date
    instante: datetime
    hora: str
    tipo: str
    evento_id: str
    nome: str
    local: str
    intervalo: str
    especie: str
    fase: str
    cancelado: bool
    edital: EditalDaAgenda

    @property
    def rotulo_da_fase(self):
        return ROTULO_DA_FASE[self.fase]

    @property
    def de_periodo(self):
        return self.tipo != PONTUAL


@dataclass(frozen=True)
class Periodo:
    """Um intervalo, dito uma vez (`D-002`)."""

    evento_id: str
    nome: str
    edital: EditalDaAgenda
    dia_inicio: date
    dia_fim: date | None
    intervalo: str
    especie: str
    fase: str

    @property
    def rotulo_da_fase(self):
        return ROTULO_DA_FASE_DO_PERIODO[self.fase]

    def toca(self, janela):
        return self.dia_inicio <= janela.fim and (
            self.dia_fim is None or self.dia_fim >= janela.inicio
        )

    def abrange(self, dia):
        """Do dia da abertura ao do encerramento, inclusive; sem término, do início em diante.

        É a pertinência do indicador da célula **e** do dia consultado (`FR-2669`, `FR-2628`): uma
        função só, para que o número da grade e a lista do dia não tenham como divergir (`SC-959`).
        """
        return self.dia_inicio <= dia and (self.dia_fim is None or dia <= self.dia_fim)

    def restante(self, hoje):
        """O tempo até o encerramento previsto, em dias corridos na zona institucional (`FR-2633`).

        Sem término não há contagem: inventar um fechamento seria o sistema fixando prazo que o
        Edital não fixou.
        """
        if self.dia_fim is None:
            return "sem término declarado"
        dias = (self.dia_fim - hoje).days
        if dias <= 0:
            return "encerra hoje"
        return f"encerra em {dias} {'dia' if dias == 1 else 'dias'}"


@dataclass(frozen=True)
class Janela:
    inicio: date
    fim: date
    rotulo: str

    def contem(self, dia):
        return self.inicio <= dia <= self.fim


@dataclass(frozen=True)
class DiaDaGrade:
    data: date | None
    quantidade: int = 0
    # Quantos períodos abrangem o dia (`FR-2669`). Outra dimensão, e não parte da `quantidade`: o
    # período não vira marco nos dias do meio, e não pesa no destaque nem na síntese (`D-002`).
    periodos: int = 0
    nomeados: tuple = ()
    mais: int = 0
    destaque: bool = False
    hoje: bool = False
    por_extenso: str = ""
    endereco: str = ""


@dataclass(frozen=True)
class Sintese:
    marcos: int
    editais: int
    encerramentos: int
    dias_com_varios: int
    dia_mais_carregado: tuple | None


@dataclass(frozen=True)
class AvisoDeRetificacao:
    edital: EditalDaAgenda
    vigora_em: datetime


@dataclass(frozen=True)
class Filtros:
    edital: str | None = None
    especie: str | None = None

    @property
    def ativos(self):
        return bool(self.edital or self.especie)

    def como_parametros(self):
        return {
            chave: valor
            for chave, valor in (("edital", self.edital), ("especie", self.especie))
            if valor
        }


@dataclass(frozen=True)
class DiaDaAgenda:
    """Um dia com marcos, na lista — agrupados por Edital quando são muitos (`FR-2630`)."""

    data: date
    rotulo: str
    marcos: tuple
    grupos: tuple = ()

    @property
    def quantidade(self):
        return sum(1 for marco in self.marcos if not marco.cancelado)

    @property
    def cancelados(self):
        # Dito no título, e não só no item: "0 marcos" acima de uma prova cancelada se
        # contradiz à leitura, porque a quantidade não conta o cancelado (`FR-2632`).
        return sum(1 for marco in self.marcos if marco.cancelado)


@dataclass(frozen=True)
class Leitura:
    visao: str
    janela: Janela
    hoje: date
    lido_em: datetime
    filtros: Filtros
    opcoes_de_edital: tuple
    dia: date | None = None
    janela_em_dias: int = 7
    dias: tuple = ()
    periodos: tuple = ()
    em_curso: tuple = ()
    periodos_no_dia: tuple = ()
    semanas: tuple = ()
    sintese: Sintese | None = None
    avisos: tuple = ()
    proximo: Marco | None = None
    tem_editais: bool = False
    rotulo_do_mes: str = ""
    # O que o formulário de filtros devolve sem mostrar: a visualização e a janela em que a pessoa
    # está, para que filtrar não a tire de onde estava (`FR-2638`).
    ocultos: tuple = ()
    enderecos: dict = field(default_factory=dict)

    @property
    def vazia(self):
        return not any(not marco.cancelado for dia in self.dias for marco in dia.marcos)

    @property
    def colunas(self):
        return COLUNAS

    @property
    def especies(self):
        return tuple(ESPECIES.items())


# ---------------------------------------------------------------------------
# Instantes e rótulos — sempre na zona institucional (`FR-2616`)
# ---------------------------------------------------------------------------


def no_dia(instante):
    return instante.astimezone(ZONA).date()


def dia_e_mes(dia):
    return f"{dia.day:02d}/{dia.month:02d}"


def por_extenso(dia):
    return f"{DIAS_DA_SEMANA[dia.weekday()]}, {dia.day} de {MESES[dia.month - 1]} de {dia.year}"


def rotulo_do_dia(dia):
    return f"{DIAS_DA_SEMANA[dia.weekday()]}, {dia_e_mes(dia)}"


def _hora(instante):
    local = instante.astimezone(ZONA)
    return f"{local.hour}h{local.minute:02d}" if local.minute else f"{local.hour}h"


def _meia_noite(instante):
    local = instante.astimezone(ZONA)
    return (local.hour, local.minute, local.second) == (0, 0, 0)


def _hora_do_pontual(inicio, fim):
    """A hora do marco pontual — ou nenhuma, quando o Edital declarou só a data (`FR-2618`)."""
    if fim is None:
        return "" if _meia_noite(inicio) else _hora(inicio)
    if fim == inicio:
        return _hora(inicio)
    return f"{_hora(inicio)}–{_hora(fim)}"


# ---------------------------------------------------------------------------
# A projeção: do conteúdo publicado aos marcos e aos períodos
# ---------------------------------------------------------------------------


def _ligados_a_etapa(conteudo):
    return {
        str(etapa.get("scheduleEventId"))
        for etapa in (conteudo or {}).get("stages") or []
        if isinstance(etapa, dict) and etapa.get("scheduleEventId")
    }


def especie_do_evento(evento, ligados):
    """Uma espécie por Evento; o período de inscrições prevalece sobre o vínculo com Etapa."""
    if evento.get("isRegistrationPeriod") is True:
        return INSCRICOES
    if str(evento.get("id")) in ligados:
        return ETAPA
    return DEMAIS


def _e_periodo(evento, inicio, fim):
    """Término em outro dia faz período (a régua do relatório do Edital, `099`).

    O período de inscrições sem término também é período — aberto, pela régua do período (`009`):
    ele segue recebendo, e é dito como intervalo que começou e não fechou.
    """
    if fim is None:
        return evento.get("isRegistrationPeriod") is True
    return no_dia(fim) != no_dia(inicio)


def _fase_do_ponto(instante, agora):
    return FASE_DA_REGUA[calendario.fase(instante, None, agora=agora)]


def _considerado(edital, evento, conteudo, agora):
    """O Edital encerrado só mostra o Evento que já passou inteiro (`D-009`)."""
    if not edital.encerrado:
        return True
    return fase_do_evento(evento, conteudo, agora) == calendario.CONCLUIDO


def _intervalo(inicio, fim):
    if fim is None:
        return f"desde {dia_e_mes(no_dia(inicio))}"
    return f"{dia_e_mes(no_dia(inicio))} a {dia_e_mes(no_dia(fim))}"


def marcos_do_conteudo(edital, conteudo, agora):
    """Os marcos que o cronograma vigente de um Edital produz (`FR-2618` a `FR-2622`).

    O Evento pontual é um marco; o período, dois — e nenhum nos dias do meio (`D-002`). Os
    cancelados continuam aqui, marcados: quem os esconde da grade e dos números é quem conta.
    """
    ligados = _ligados_a_etapa(conteudo)
    marcos = []
    for evento in eventos_do_conteudo(conteudo):
        inicio, fim = instantes_do_evento(evento)
        if inicio is None or not _considerado(edital, evento, conteudo, agora):
            continue
        comum = {
            "evento_id": str(evento.get("id")),
            "nome": descricao_do_evento(evento),
            "local": (evento.get("location") or "").strip(),
            "especie": especie_do_evento(evento, ligados),
            "cancelado": esta_cancelado(evento),
            "edital": edital,
        }
        if _e_periodo(evento, inicio, fim):
            intervalo = _intervalo(inicio, fim)
            marcos.append(
                Marco(
                    dia=no_dia(inicio),
                    instante=inicio,
                    hora=_hora_do_pontual(inicio, None),
                    tipo=ABERTURA,
                    intervalo=intervalo,
                    fase=_fase_do_ponto(inicio, agora),
                    **comum,
                )
            )
            if fim is not None:
                marcos.append(
                    Marco(
                        dia=no_dia(fim),
                        instante=fim,
                        hora=_hora_do_pontual(fim, None),
                        tipo=ENCERRAMENTO,
                        intervalo=intervalo,
                        fase=_fase_do_ponto(fim, agora),
                        **comum,
                    )
                )
            continue
        marcos.append(
            Marco(
                dia=no_dia(inicio),
                instante=inicio,
                hora=_hora_do_pontual(inicio, fim),
                tipo=PONTUAL,
                intervalo="",
                fase=FASE_DA_REGUA[calendario.fase(inicio, fim, agora=agora)],
                **comum,
            )
        )
    return marcos


def periodos_do_conteudo(edital, conteudo, agora):
    """Os períodos do cronograma vigente, ditos uma vez (`FR-2627`, `FR-2633`).

    A fase é a do **Evento**, pela régua com o período de inscrições (`fase_do_evento`). O período
    cancelado não entra: ele não está correndo, e os marcos dele já se dizem cancelados.
    """
    ligados = _ligados_a_etapa(conteudo)
    periodos = []
    for evento in eventos_do_conteudo(conteudo):
        inicio, fim = instantes_do_evento(evento)
        if inicio is None or esta_cancelado(evento) or not _e_periodo(evento, inicio, fim):
            continue
        if not _considerado(edital, evento, conteudo, agora):
            continue
        fase = fase_do_evento(evento, conteudo, agora)
        if fase is None:
            continue
        periodos.append(
            Periodo(
                evento_id=str(evento.get("id")),
                nome=descricao_do_evento(evento),
                edital=edital,
                dia_inicio=no_dia(inicio),
                dia_fim=no_dia(fim) if fim is not None else None,
                intervalo=_intervalo(inicio, fim),
                especie=especie_do_evento(evento, ligados),
                fase=FASE_DA_REGUA[fase],
            )
        )
    return periodos


# ---------------------------------------------------------------------------
# Janelas, ordem, filtros e síntese
# ---------------------------------------------------------------------------


def janela_do_mes(ano, mes):
    inicio = date(ano, mes, 1)
    seguinte = date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)
    return Janela(inicio, seguinte - timedelta(days=1), f"{MESES[mes - 1]} de {ano}")


def janela_proxima(hoje, dias):
    """Hoje inteiro e os dias seguintes: o marco de hoje que já passou continua sendo de hoje."""
    fim = hoje + timedelta(days=dias - 1)
    return Janela(hoje, fim, f"{dia_e_mes(hoje)} a {dia_e_mes(fim)}")


def janela_do_dia(dia):
    return Janela(dia, dia, por_extenso(dia))


def na_janela(marcos, janela):
    return [marco for marco in marcos if janela.contem(marco.dia)]


def ordenar(marcos):
    """Pelo instante, depois pelo Edital (ano e número), depois pelo nome (`FR-2632`)."""
    return sorted(marcos, key=lambda m: (m.instante, m.edital.chave_de_ordem, m.nome, m.tipo))


def filtrar(itens, filtros):
    return [
        item
        for item in itens
        if (not filtros.edital or item.edital.id == filtros.edital)
        and (not filtros.especie or item.especie == filtros.especie)
    ]


def sintese(marcos):
    """Os números da janela, sobre os marcos exibidos e sem os cancelados (`FR-2634`).

    A concentração **nomeia o máximo**, e não aplica limiar: "mais carregado" só existe quando algum
    dia tem mais de um marco, porque com um em cada dia não há concentração a apontar.
    """
    ativos = [marco for marco in marcos if not marco.cancelado]
    por_dia = Counter(marco.dia for marco in ativos)
    varios = {dia: quantidade for dia, quantidade in por_dia.items() if quantidade >= 2}
    mais_carregado = None
    if varios:
        mais_carregado = min(varios.items(), key=lambda item: (-item[1], item[0]))
    return Sintese(
        marcos=len(ativos),
        editais=len({marco.edital.id for marco in ativos}),
        encerramentos=sum(1 for marco in ativos if marco.tipo == ENCERRAMENTO),
        dias_com_varios=len(varios),
        dia_mais_carregado=mais_carregado,
    )


def dias_da_lista(marcos):
    """Os dias com marco, em ordem, cada um com os seus marcos na ordem do dia (`FR-2632`)."""
    por_dia = {}
    for marco in ordenar(marcos):
        por_dia.setdefault(marco.dia, []).append(marco)
    dias = []
    for dia, do_dia in sorted(por_dia.items()):
        grupos = ()
        if len(do_dia) > AGRUPAR_ACIMA_DE:
            por_edital = {}
            for marco in do_dia:
                por_edital.setdefault(marco.edital, []).append(marco)
            grupos = tuple(
                (edital, tuple(itens))
                for edital, itens in sorted(
                    por_edital.items(), key=lambda par: par[0].chave_de_ordem
                )
            )
        dias.append(
            DiaDaAgenda(data=dia, rotulo=rotulo_do_dia(dia), marcos=tuple(do_dia), grupos=grupos)
        )
    return tuple(dias)


def semanas_do_mes(ano, mes, marcos, hoje, endereco_do_dia=None, *, periodos=()):
    """A grade do mês: domingo primeiro, de quatro a seis semanas, dias de fora vazios (`D-010`).

    A célula conta os marcos não cancelados, destaca a partir de dois e nomeia os dois primeiros na
    ordem do dia (`FR-2625`, `FR-2626`). Os dias do mês vizinho ficam vazios: mostrá-los contaria o
    mesmo marco em duas páginas, e a soma das células deixaria de ser a síntese (`FR-2635`).

    `periodos` são os já projetados e filtrados — os mesmos da lista do mês. Cada célula conta os
    que a abrangem: contagem derivada, sem item por dia (`FR-2669`, research R-013).
    """
    ativos = {}
    for marco in ordenar(marcos):
        if not marco.cancelado:
            ativos.setdefault(marco.dia, []).append(marco)
    semanas = []
    for semana in Calendar(firstweekday=6).monthdatescalendar(ano, mes):
        linha = []
        for dia in semana:
            if dia.month != mes:
                linha.append(DiaDaGrade(data=None))
                continue
            do_dia = ativos.get(dia, [])
            linha.append(
                DiaDaGrade(
                    data=dia,
                    quantidade=len(do_dia),
                    periodos=sum(1 for periodo in periodos if periodo.abrange(dia)),
                    nomeados=tuple(do_dia[:NOMES_NA_CELULA]),
                    mais=max(0, len(do_dia) - NOMES_NA_CELULA),
                    destaque=len(do_dia) >= 2,
                    hoje=dia == hoje,
                    por_extenso=por_extenso(dia),
                    endereco=endereco_do_dia(dia) if endereco_do_dia else "",
                )
            )
        semanas.append(tuple(linha))
    return tuple(semanas)


# ---------------------------------------------------------------------------
# A leitura
# ---------------------------------------------------------------------------


def _mes_pedido(valor, hoje):
    try:
        ano, mes = (int(parte) for parte in str(valor).split("-"))
        return date(ano, mes, 1)
    except (TypeError, ValueError):
        return date(hoje.year, hoje.month, 1)


def _dia_pedido(valor):
    try:
        return date.fromisoformat(str(valor)) if valor else None
    except ValueError:
        return None


def _uuid_pedido(valor):
    try:
        return str(UUID(str(valor))) if valor else None
    except ValueError:
        return None


def _mes_vizinho(primeiro, passo):
    mes = primeiro.month + passo
    ano = primeiro.year + (mes - 1) // 12
    return date(ano, (mes - 1) % 12 + 1, 1)


def _endereco(**parametros):
    limpos = {chave: valor for chave, valor in parametros.items() if valor not in (None, "")}
    base = reverse("interface:agenda")
    return f"{base}?{urlencode(limpos)}" if limpos else base


def editais_da_agenda(ator):
    """Os Editais do escopo do ator que a agenda considera — uma consulta (`FR-2610`, `D-009`).

    O escopo vem da consulta, como em toda listagem da gestão: Edital de outra unidade não é
    recusado, ele simplesmente não existe aqui.
    """
    return list(
        Edital.objects.filter(
            institution_scope=ator.institution_scope, status__in=SITUACOES_NA_AGENDA
        ).select_related("processo")
    )


def retificacoes_a_vigorar(edital_ids, agora):
    """`{edital_id: vigora_em}` — a primeira versão de vigência futura de cada Edital (`D-008`).

    Uma consulta agregada, sem materializar conteúdo: a agenda anuncia a Retificação e não a
    aplica, então não precisa saber o que ela muda.
    """
    if not edital_ids:
        return {}
    return {
        linha["edital_id"]: linha["vigora_em"]
        for linha in VersaoConsolidada.objects.filter(
            edital_id__in=edital_ids, valid_from__gt=agora
        )
        .values("edital_id")
        .annotate(vigora_em=Min("valid_from"))
    }


def ler(ator, parametros, *, agora=None):
    """A página inteira, num número fixo de consultas (`FR-2646`).

    Uma para os Editais do escopo, duas para a versão vigente de cada um, uma para as Retificações
    a vigorar; o resto é derivação em memória. As duas visualizações leem o mesmo conjunto e diferem
    só na janela aplicada sobre ele.
    """
    agora = agora or timezone.now()
    hoje = agora.astimezone(ZONA).date()

    editais = editais_da_agenda(ator)
    versoes = versoes_vigentes(edital_ids=[edital.pk for edital in editais], at=agora)
    a_vigorar = retificacoes_a_vigorar([edital.pk for edital in editais], agora)

    considerados, todos_marcos, todos_periodos, opcoes = [], [], [], []
    for edital in editais:
        versao = versoes.get(edital.pk)
        if versao is None:
            continue
        da_agenda = EditalDaAgenda.de(edital)
        considerados.append((edital.pk, da_agenda))
        todos_marcos.extend(marcos_do_conteudo(da_agenda, versao.content, agora))
        todos_periodos.extend(periodos_do_conteudo(da_agenda, versao.content, agora))
        # Edital sem Evento não é opção de filtro: escolhê-lo só produziria uma página vazia.
        if eventos_do_conteudo(versao.content):
            opcoes.append(da_agenda)
    opcoes.sort(key=lambda edital: edital.chave_de_ordem)

    # Identificador que não está entre os carregados — de outro escopo, inexistente ou mal
    # escrito — é ignorado, sem distinção entre os três (`FR-2610`).
    edital_pedido = _uuid_pedido(parametros.get("edital"))
    filtros = Filtros(
        edital=edital_pedido if edital_pedido in {edital.id for edital in opcoes} else None,
        especie=parametros.get("especie") if parametros.get("especie") in ESPECIES else None,
    )
    marcos = filtrar(todos_marcos, filtros)
    periodos = filtrar(todos_periodos, filtros)

    visao = parametros.get("visao") if parametros.get("visao") in VISOES else MES
    dia = _dia_pedido(parametros.get("dia")) if visao == MES else None
    primeiro = date(dia.year, dia.month, 1) if dia else _mes_pedido(parametros.get("mes"), hoje)
    em_dias = 30 if str(parametros.get("janela")) == "30" else 7
    mes_texto = f"{primeiro.year:04d}-{primeiro.month:02d}"
    preservados = filtros.como_parametros()

    def endereco_do_dia(alvo):
        return _endereco(visao=MES, dia=alvo.isoformat(), **preservados)

    enderecos = {
        "aba_mes": _endereco(visao=MES, mes=mes_texto, **preservados),
        "aba_proximos": _endereco(visao=PROXIMOS, **preservados),
        "mes_anterior": _endereco(
            visao=MES, mes=_mes_vizinho(primeiro, -1).strftime("%Y-%m"), **preservados
        ),
        "mes_seguinte": _endereco(
            visao=MES, mes=_mes_vizinho(primeiro, 1).strftime("%Y-%m"), **preservados
        ),
        "mes_corrente": _endereco(visao=MES, **preservados),
        "janela_7": _endereco(visao=PROXIMOS, **preservados),
        "janela_30": _endereco(visao=PROXIMOS, janela=30, **preservados),
        "voltar_ao_mes": _endereco(visao=MES, mes=mes_texto, **preservados),
        "limpar_filtros": _endereco(
            visao=visao,
            mes=mes_texto if visao == MES and not dia else None,
            dia=dia.isoformat() if dia else None,
            janela=30 if visao == PROXIMOS and em_dias == 30 else None,
        ),
    }

    if visao == PROXIMOS:
        janela = janela_proxima(hoje, em_dias)
    elif dia:
        janela = janela_do_dia(dia)
    else:
        janela = janela_do_mes(primeiro.year, primeiro.month)

    na = ordenar(na_janela(marcos, janela))
    depois = [m for m in ordenar(marcos) if m.dia > janela.fim and not m.cancelado]
    pedidos = {pk for pk, _ in considerados if not filtros.edital or str(pk) == filtros.edital}

    leitura = {
        "visao": visao,
        "janela": janela,
        "hoje": hoje,
        "lido_em": agora,
        "filtros": filtros,
        "opcoes_de_edital": tuple(opcoes),
        "dia": dia,
        "janela_em_dias": em_dias,
        "dias": dias_da_lista(na),
        "avisos": tuple(
            AvisoDeRetificacao(edital=da_agenda, vigora_em=a_vigorar[pk])
            for pk, da_agenda in considerados
            if pk in pedidos and pk in a_vigorar
        ),
        "proximo": depois[0] if not any(not m.cancelado for m in na) and depois else None,
        "tem_editais": bool(considerados),
        "rotulo_do_mes": janela_do_mes(primeiro.year, primeiro.month).rotulo,
        "ocultos": tuple(
            (chave, valor)
            for chave, valor in (
                ("visao", visao),
                ("mes", mes_texto if visao == MES and not dia else None),
                ("dia", dia.isoformat() if dia else None),
                ("janela", "30" if visao == PROXIMOS and em_dias == 30 else None),
            )
            if valor
        ),
        "enderecos": enderecos,
    }
    if visao == PROXIMOS:
        # O tempo que falta vai pronto, com o `hoje` da leitura: o template não o calcula.
        leitura["em_curso"] = tuple(
            (periodo, periodo.restante(hoje))
            for periodo in sorted(
                (p for p in periodos if p.fase == EM_CURSO),
                key=lambda p: (p.dia_fim or date.max, p.dia_inicio, p.nome),
            )
        )
        leitura["sintese"] = sintese(na)
    elif dia:
        leitura["periodos_no_dia"] = tuple(
            sorted(
                (p for p in periodos if p.abrange(dia)),
                key=lambda p: (p.dia_inicio, p.edital.chave_de_ordem, p.nome),
            )
        )
    else:
        leitura["periodos"] = tuple(
            sorted(
                (p for p in periodos if p.toca(janela)),
                key=lambda p: (p.dia_inicio, p.edital.chave_de_ordem, p.nome),
            )
        )
        leitura["semanas"] = semanas_do_mes(
            primeiro.year, primeiro.month, na, hoje, endereco_do_dia, periodos=periodos
        )
        leitura["sintese"] = sintese(na)
    return Leitura(**leitura)
