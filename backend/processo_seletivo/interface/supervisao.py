"""A supervisão do Processo: as formas de leitura e as derivações que as preenchem.

**Este módulo só lê.** Nenhum `save`, `create`, `update` ou `delete` nasce aqui, e a ausência é o
invariante da feature: a `022` é composição de leituras que sete apps já persistem, e a necessidade
de gravar estado é motivo para revisar a spec, não para escrever migration (`D-007`, `FR-007`).

Ele fica fora de `views.py` de propósito. Aqui vivem as derivações, e mantê-las separadas da
montagem de contexto é o que permite testá-las como domínio de leitura, sem requisição.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.avaliacoes.application.selectors import resumo_da_etapa
from processo_seletivo.avaliacoes.models import Impedimento
from processo_seletivo.classificacao.application.selectors import ato_vigente, estado_do_marco
from processo_seletivo.comissoes.application import selectors as comissao_selectors
from processo_seletivo.comissoes.domain.autorizacao import pode_gerir_comissao
from processo_seletivo.comissoes.domain.etapas import conteudo_vigente
from processo_seletivo.editais.models.cronograma import EventoCronograma
from processo_seletivo.inscricoes.domain.periodo import (
    ABERTO,
    ENCERRADO,
    FUTURO,
    periodo_de_inscricoes,
)
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.recursos.application import selectors as recursos_selectors
from processo_seletivo.recursos.models import Recurso
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.tempo import ZONA

# ---------------------------------------------------------------------------
# 1. As formas de leitura (data-model §2)
#
# Estruturas de transporte, montadas na requisição e descartadas com ela. Não são modelos: não têm
# identidade, não têm persistência, e nenhuma delas conhece o banco.
# ---------------------------------------------------------------------------

# As três posições do período, e a ausência de designação. Vêm do domínio da `009` em vez de
# nascerem aqui: o candidato e a supervisão precisam responder a mesma pergunta, e dois vocabulários
# para "as inscrições estão abertas" é o que o Princípio I recusa.
SITUACOES_DO_PERIODO = (FUTURO, ABERTO, ENCERRADO)

# O que se declara quando não há prazo a apresentar (`FR-022`). Os dois casos são distintos para
# quem lê: um Edital sem cronograma vigente ainda não chegou lá; um cronograma sem Evento marcado
# chegou e não designou o período.
SEM_CRONOGRAMA = "sem-cronograma"
SEM_PERIODO = "sem-periodo"

# Como o Evento **declara** o próprio estado, dito para quem lê a tela. Não é vocabulário novo:
# são os quatro valores que `EventoCronograma.Status` já declara. Fica aqui, e não no filtro
# compartilhado de situações, porque ali o mesmo nome significa a situação do Edital e do Processo —
# e "Concluído" de um Evento não é "Encerrado" de um Edital.
DECLARACOES = {
    EventoCronograma.Status.PLANEJADO: "planejado",
    EventoCronograma.Status.EM_ANDAMENTO: "em andamento",
    EventoCronograma.Status.CONCLUIDO: "concluído",
    EventoCronograma.Status.CANCELADO: "cancelado",
}

# A janela da leitura recente (`FR-013`). Vinte e quatro horas **abertas no início**: a submissão de
# exatamente 24 h fica de fora, porque incluí-la contaria um dia e um instante.
JANELA_RECENTE = timedelta(hours=24)


@dataclass(frozen=True)
class PeriodoDeInscricoes:
    """O Evento marcado como período, e a posição do instante da leitura dentro dele.

    `situacao` é derivada e nunca gravada: ela é a resposta de agora sobre datas que o Edital
    publicou, e persistí-la criaria estado a manter coerente com o relógio.
    """

    inicio: datetime | None
    fim: datetime | None
    situacao: str
    restante: timedelta | None = None

    @property
    def em_curso(self) -> bool:
        return self.situacao == ABERTO


@dataclass(frozen=True)
class Marco:
    """Um Evento do cronograma vigente, apresentado como marco que ainda vem.

    `edital` é obrigatório, e a obrigação é `D-005` expressa na forma: não existe marco do
    Processo, e uma data sem o Edital que a sustenta seria a tela inventando um.
    """

    edital: object
    descricao: str
    inicio: datetime | None
    fim: datetime | None
    # O `status` do Evento, apresentado como **declaração** e nunca corrigido (`FR-023`, `D-004`).
    declarado: str

    @property
    def declarado_legivel(self) -> str:
        """O estado declarado em português, ou o próprio código quando ele não é dos quatro."""
        return DECLARACOES.get(self.declarado, self.declarado)


@dataclass(frozen=True)
class PontoDaSerie:
    dia: date
    quantidade: int


@dataclass(frozen=True)
class PulsoDoEdital:
    edital: object
    submetidas: int
    rascunhos: int
    periodo: PeriodoDeInscricoes | None = None
    # `SEM_CRONOGRAMA`, `SEM_PERIODO`, ou vazio quando há período declarado (`FR-022`).
    ausencia: str = ""
    serie: tuple[PontoDaSerie, ...] = ()
    proximos_marcos: tuple[Marco, ...] = ()

    @property
    def pico(self) -> int:
        """O maior valor da série — denominador da altura da barra, e nada além disso.

        Fica aqui, e não no template, porque `widthratio` precisa de um denominador e o template
        não sabe percorrer a série duas vezes. Não é dado do domínio: é a escala do desenho, e por
        isso não entra em nenhuma leitura textual.
        """
        return max((ponto.quantidade for ponto in self.serie), default=0)


@dataclass(frozen=True)
class Pulso:
    submetidas_no_processo: int
    rascunhos_no_processo: int
    # `None` — e não zero — quando nenhum Edital tem período em curso: fora da janela o número é
    # sempre zero, e zero apresentado como notícia é ruído (`FR-013`).
    ultimas_24h: int | None
    por_edital: tuple[PulsoDoEdital, ...]
    lido_em: datetime

    @property
    def algum_periodo_em_curso(self) -> bool:
        return any(item.periodo is not None and item.periodo.em_curso for item in self.por_edital)


@dataclass(frozen=True)
class Medida:
    """Numerador e denominador, sempre os dois (`FR-032`).

    Par completo ou ausente, e não dois campos opcionais: é o requisito expresso na forma, e não
    confiado à disciplina de quem escreve o template.
    """

    numerador: int
    denominador: int


@dataclass(frozen=True)
class Destino:
    rotulo: str
    url: str


@dataclass(frozen=True)
class Sinal:
    """Uma forma só para os cinco. O que muda entre eles é o conteúdo, não a estrutura.

    **Não existe `gravidade`.** Os cinco são igualmente acionáveis, e introduzir severidade pediria
    uma ordenação que o domínio não determina e que viraria juízo da tela (`D-002`).
    """

    especie: str
    edital: object
    alvo: str
    mensagem: str
    medida: Medida | None = None
    # Ausente quando a situação do Processo não admite o encaminhamento (`FR-036`). Sinal cujo
    # **destino o ator não alcança** não chega a ser montado (`FR-004`), e por isso a ausência aqui
    # nunca significa supressão por alcance.
    destino: Destino | None = None


# ---------------------------------------------------------------------------
# 2. A porta
# ---------------------------------------------------------------------------


def pode_supervisionar(ator, processo):
    """A base que autoriza supervisionar este Processo, ou `None`.

    **É a mesma pergunta que governa a página do Processo**, e não uma segunda (`FR-002`): as duas
    bases que a `011` reconhece — a permissão sistêmica de gerir comissão ou a presidência deste
    Processo —, cada uma suficiente sozinha. Nenhum papel novo, nenhuma permissão nova, nenhum
    vínculo novo.

    Existe como função própria, e não como chamada direta na view, porque é o nome da regra nesta
    feature: quem lê `supervisao.py` encontra a porta declarada, e o dia em que a base mudar há um
    lugar só onde mudá-la.
    """
    return pode_gerir_comissao(ator, processo)


# ---------------------------------------------------------------------------
# 3. O que o Processo publica — Editais, conteúdo vigente e Etapas
# ---------------------------------------------------------------------------


def editais_do_processo(processo):
    """Os Editais do Processo, na ordem em que a tela os lê."""
    return list(processo.editais.order_by("year", "number"))


def conteudo_ou_nada(edital):
    """O conteúdo vigente do Edital, ou `None` quando ele ainda não foi publicado.

    **Pelo resolvedor que a `011` já usa** (`FR-005`). Ler `edital.cronograma` ou `edital.etapas`
    daria a coleção de elaboração, que diverge do conteúdo vigente depois de uma Retificação — ela
    remove Etapa e acrescenta Evento sem escrever de volta nas linhas.
    """
    try:
        return conteudo_vigente(edital)
    except DomainError:
        return None


def etapas_do_conteudo(conteudo):
    """As Etapas da versão publicada, em ordem, como a versão as declara."""
    etapas = [item for item in (conteudo or {}).get("stages") or [] if isinstance(item, dict)]
    return sorted(etapas, key=lambda etapa: (etapa.get("order") or 0, etapa.get("name") or ""))


def eventos_do_conteudo(conteudo):
    """Os Eventos da versão publicada, na ordem do cronograma."""
    eventos = [item for item in (conteudo or {}).get("schedule") or [] if isinstance(item, dict)]
    return sorted(eventos, key=lambda evento: (evento.get("order") or 0))


def leitura_dos_editais(processo):
    """`[(edital, conteudo|None)]` — uma leitura da versão vigente por Edital, e nunca por Etapa."""
    return [(edital, conteudo_ou_nada(edital)) for edital in editais_do_processo(processo)]


# ---------------------------------------------------------------------------
# 4. O Pulso — inscrições
# ---------------------------------------------------------------------------


def contagens_por_edital(processo):
    """`{edital_id: {status: quantidade}}` — **uma** consulta para o Processo inteiro.

    Submetidas e rascunhos saem da mesma agregação e ficam em chaves distintas; somá-los seria
    contrariar `FR-012` no lugar mais barato de contrariá-lo. Uma consulta por Edital pareceria
    inofensiva com dois e cresceria com o Processo, que é justamente o que `T-002` recusa.
    """
    contagens = {}
    for linha in (
        Inscricao.objects.filter(edital__processo=processo)
        .values("edital_id", "status")
        .annotate(quantidade=Count("id"))
    ):
        contagens.setdefault(linha["edital_id"], {})[linha["status"]] = linha["quantidade"]
    return contagens


def submetidas_nas_ultimas_24h(processo, agora):
    """A contagem recente, **no Processo** (`FR-013`).

    Contagem soma, e por isso este número é do Processo enquanto a série é do Edital: a série é
    recortada por um período, e período é do Edital (`D-005`, `FR-014`).
    """
    return Inscricao.objects.filter(
        edital__processo=processo,
        status=Inscricao.Status.SUBMETIDA,
        submitted_at__gt=agora - JANELA_RECENTE,
    ).count()


# ---------------------------------------------------------------------------
# 5. O Pulso — cronograma
# ---------------------------------------------------------------------------


def periodo_do_edital(conteudo, agora):
    """`(PeriodoDeInscricoes | None, ausência)` — o prazo daquele Edital, ou o que falta dele.

    A leitura é a da `009`, e não uma segunda: o Evento **marcado** é quem diz qual é o período, e
    procurar texto em `type` seria decidir uma regra de direito lendo o que alguém digitou.
    """
    if conteudo is None:
        return None, SEM_CRONOGRAMA
    lido = periodo_de_inscricoes(conteudo, agora)
    if not lido.designado:
        return None, SEM_PERIODO
    # Sem término declarado não há contagem regressiva: inventar um fechamento seria o sistema
    # fixando prazo que o Edital não fixou.
    restante = lido.fim - agora if lido.fim is not None and lido.estado != ENCERRADO else None
    return (
        PeriodoDeInscricoes(
            inicio=lido.inicio, fim=lido.fim, situacao=lido.estado, restante=restante
        ),
        "",
    )


def marcos_do_edital(edital, conteudo, agora):
    """Os marcos que ainda vêm, em ordem cronológica e sem os cancelados (`FR-021`).

    **O marco em curso ainda é próximo.** O corte é o término, e não o início: tirar da lista o que
    está acontecendo esconderia justamente o prazo que corre.

    `CANCELADO` sai da leitura temporal pela mesma razão que sai de `UX-002` — o Evento deixou o
    cronograma efetivo, e cobrar prazo dele seria cobrar de quem já foi cancelado.
    """
    marcos = []
    for evento in eventos_do_conteudo(conteudo):
        if evento.get("status") == EventoCronograma.Status.CANCELADO:
            continue
        inicio, fim = instantes_do_evento(evento)
        termina = fim or inicio
        if termina is None or termina <= agora:
            continue
        marcos.append(
            Marco(
                edital=edital,
                descricao=evento.get("description") or evento.get("type") or "",
                inicio=inicio,
                fim=fim,
                # Apresentado como declaração, e nunca corrigido (`FR-023`, `D-004`).
                declarado=evento.get("status") or "",
            )
        )
    marcos.sort(key=lambda marco: (marco.inicio or marco.fim, marco.descricao))
    return tuple(marcos)


def instantes_do_evento(evento):
    """`(início, término)` do Evento publicado. O término é anulável, e a ausência é legítima."""
    inicio = parse_datetime(evento.get("startAt") or "")
    fim = parse_datetime(evento.get("endAt") or "") if evento.get("endAt") else None
    return inicio, fim


def serie_do_edital(edital, periodo, agora):
    """A série **diária** de submissões daquele Edital, com os dias de zero preenchidos.

    Uma agregação por Edital, pelo instante de **submissão** e por mais nada (`FR-015`). O recorte
    é o período declarado, e o dia sem submissão entra com zero: a ausência de um dia faria a
    leitura supor uma continuidade que não houve.

    A janela termina no menor entre o fim declarado e o instante da leitura, porque um dia que
    ainda não aconteceu não é um dia com zero — é um dia que não houve.
    """
    if periodo is None or periodo.inicio is None:
        return ()
    limite = agora if periodo.fim is None or periodo.fim > agora else periodo.fim
    if limite < periodo.inicio:
        return ()
    contagens = dict(
        Inscricao.objects.filter(
            edital=edital,
            status=Inscricao.Status.SUBMETIDA,
            submitted_at__gte=periodo.inicio,
            submitted_at__lte=limite,
        )
        .annotate(dia=TruncDate("submitted_at", tzinfo=ZONA))
        .values("dia")
        .annotate(quantidade=Count("id"))
        .values_list("dia", "quantidade")
    )
    primeiro = periodo.inicio.astimezone(ZONA).date()
    ultimo = limite.astimezone(ZONA).date()
    dias = (primeiro + timedelta(days=passo) for passo in range((ultimo - primeiro).days + 1))
    return tuple(PontoDaSerie(dia=dia, quantidade=contagens.get(dia, 0)) for dia in dias)


# ---------------------------------------------------------------------------
# 6. O Pulso inteiro
# ---------------------------------------------------------------------------


def pulso(processo, *, agora=None):
    """A leitura do Processo num instante: quanto chegou, quando encerra, e o que ainda vem.

    O instante viaja na forma (`FR-009`) porque é ele que qualifica todo o resto: o tempo restante,
    a série e as últimas 24 horas são respostas sobre um agora, e uma página que não o declara pede
    que quem lê adivinhe de quando ela fala.
    """
    agora = agora or timezone.now()
    contagens = contagens_por_edital(processo)
    por_edital = []
    for edital, conteudo in leitura_dos_editais(processo):
        periodo, ausencia = periodo_do_edital(conteudo, agora)
        por_edital.append(
            PulsoDoEdital(
                edital=edital,
                submetidas=contagens.get(edital.id, {}).get(Inscricao.Status.SUBMETIDA, 0),
                rascunhos=contagens.get(edital.id, {}).get(Inscricao.Status.RASCUNHO, 0),
                periodo=periodo,
                ausencia=ausencia,
                serie=serie_do_edital(edital, periodo, agora),
                proximos_marcos=marcos_do_edital(edital, conteudo, agora),
            )
        )
    por_edital = tuple(por_edital)
    em_curso = any(item.periodo is not None and item.periodo.em_curso for item in por_edital)
    return Pulso(
        submetidas_no_processo=sum(item.submetidas for item in por_edital),
        rascunhos_no_processo=sum(item.rascunhos for item in por_edital),
        # Encerrados todos os períodos o número não é apresentado: fora da janela ele é sempre
        # zero, e zero apresentado como notícia é ruído — a ausência de período já é dita.
        ultimas_24h=submetidas_nas_ultimas_24h(processo, agora) if em_curso else None,
        por_edital=por_edital,
        lido_em=agora,
    )


# ---------------------------------------------------------------------------
# 7. Atenção — o catálogo fechado dos cinco sinais
#
# Cinco perguntas nomeadas, e nenhum mecanismo genérico. Acrescentar uma sexta é revisar a spec, e
# `tests/unit/interface/test_supervisao.py` é o que torna essa regra cobrável (`D-002`, `FR-024`).
# ---------------------------------------------------------------------------

UX_001 = "UX-001"
UX_002 = "UX-002"
UX_003 = "UX-003"
UX_004 = "UX-004"
UX_005 = "UX-005"

ESPECIES = (UX_001, UX_002, UX_003, UX_004, UX_005)

# As três posições determináveis do instante da leitura dentro de um Evento. A quarta —
# indeterminada — é a ausência de término, e ela não é posição: é a impossibilidade de haver um
# "depois" (`T-005`).
ANTES_DO_INICIO = "antes"
DENTRO_DO_INTERVALO = "dentro"
DEPOIS_DO_TERMINO = "depois"

# As três combinações coerentes da tabela-verdade de `T-005`. O que **não** está aqui, e não é
# excluído pelas duas regras acima, diverge — e escrever as coerentes em vez das divergentes é o
# que impede uma combinação de ficar implícita.
COERENTES = frozenset(
    {
        (EventoCronograma.Status.PLANEJADO, ANTES_DO_INICIO),
        (EventoCronograma.Status.EM_ANDAMENTO, DENTRO_DO_INTERVALO),
        (EventoCronograma.Status.CONCLUIDO, DEPOIS_DO_TERMINO),
    }
)

# Como cada posição é dita ao lado da declaração, na forma de `UX-002`: *declarado X · prazo …*.
FRASES_DA_POSICAO = {
    ANTES_DO_INICIO: "prazo começa em",
    DENTRO_DO_INTERVALO: "prazo em curso até",
    DEPOIS_DO_TERMINO: "prazo encerrado em",
}


def rotulo_do_edital(edital):
    return f"{edital.number}/{edital.year}"


def nome_da_etapa(etapa):
    return etapa.get("name") or str(etapa.get("id") or "")


def _dia(instante):
    return instante.astimezone(ZONA).strftime("%d/%m/%Y") if instante is not None else ""


def posicao_temporal(inicio, fim, agora):
    """Onde o instante da leitura cai dentro do Evento, ou `None` quando não é determinável.

    Sem término declarado só *antes* e *dentro* seriam determináveis, e nenhum dos dois basta
    sozinho para acusar incoerência: Evento sem término é marco instantâneo, forma normal do dado.
    Tratar a ausência como divergência encheria o painel de sinal sobre o que é legítimo.
    """
    if fim is None:
        return None
    if inicio is not None and agora < inicio:
        return ANTES_DO_INICIO
    if agora > fim:
        return DEPOIS_DO_TERMINO
    return DENTRO_DO_INTERVALO


# --- `UX-001` — Etapa sem marco no cronograma -----------------------------------------------


def etapas_sem_marco(edital, conteudo):
    """Etapa que não referencia Evento algum (`FR-026`).

    É publicável e legítimo — a validação recusa referência a Evento **inexistente** e admite a
    ausência de referência —, e por isso vira sinal e não impeditivo: transformá-lo em erro de
    publicação mudaria o que o sistema aceita publicar, decisão normativa que não cabe a um painel
    (`T-006`).

    A ausência é dita nesses termos, e **nunca** como atraso, espera ou progresso zero: a Etapa não
    tem situação temporal alguma a receber, e atribuir-lhe uma seria inventar o estado que `D-003`
    recusa criar.
    """
    for etapa in etapas_do_conteudo(conteudo):
        if etapa.get("scheduleEventId"):
            continue
        nome = nome_da_etapa(etapa)
        yield Sinal(
            especie=UX_001,
            edital=edital,
            alvo=nome,
            mensagem=(
                f"A Etapa {nome}, do Edital {rotulo_do_edital(edital)}, "
                f"está sem marco no cronograma."
            ),
        )


# --- `UX-002` — declarado × posição temporal ------------------------------------------------


def divergencias_temporais(edital, conteudo, agora):
    """Evento cujo estado declarado é incompatível com a posição observável (`FR-027`).

    **As duas informações são apresentadas, e nenhuma é arbitrada** (`FR-023`, `D-004`): a tela não
    corrige o `status` nem recalcula as datas. Quando os dois discordam, quem discorda é o
    cronograma, e quem decide é quem preside.
    """
    for evento in eventos_do_conteudo(conteudo):
        declarado = evento.get("status")
        if declarado == EventoCronograma.Status.CANCELADO or declarado not in DECLARACOES:
            continue
        inicio, fim = instantes_do_evento(evento)
        posicao = posicao_temporal(inicio, fim, agora)
        if posicao is None or (declarado, posicao) in COERENTES:
            continue
        descricao = evento.get("description") or evento.get("type") or ""
        referencia = inicio if posicao == ANTES_DO_INICIO else fim
        yield Sinal(
            especie=UX_002,
            edital=edital,
            alvo=descricao,
            mensagem=(
                f"{descricao}, do Edital {rotulo_do_edital(edital)}: "
                f"declarado {DECLARACOES[declarado]} · "
                f"{FRASES_DA_POSICAO[posicao]} {_dia(referencia)}."
            ),
        )


# --- `UX-003` — cobertura de avaliação insuficiente -----------------------------------------


def cobertura_insuficiente(edital, conteudo):
    """Etapa com inscrição carente de avaliador, com numerador e denominador (`FR-028`).

    Reusa `resumo_da_etapa` **como está**: uma agregação por Etapa, e não um laço sobre inscrições.
    A unidade sem nenhum avaliador é carente e permanece no denominador — retirá-la faria a
    cobertura parecer completa justamente onde ela não começou (`FR-033`).
    """
    for etapa in etapas_do_conteudo(conteudo):
        resumo = resumo_da_etapa(edital=edital, etapa=etapa)
        if not resumo["carentes"]:
            continue
        nome = nome_da_etapa(etapa)
        yield Sinal(
            especie=UX_003,
            edital=edital,
            alvo=nome,
            medida=Medida(numerador=resumo["carentes"], denominador=resumo["inscricoes"]),
            mensagem=(
                f"A Etapa {nome}, do Edital {rotulo_do_edital(edital)}, "
                f"tem inscrição sem avaliador suficiente."
            ),
        )


# --- `UX-004` — ato de ordenação vigente obsoleto -------------------------------------------


def versao_vigente_do_edital(edital):
    """A Versão Consolidada vigente, ou `None` quando o Edital não foi publicado.

    O **conteúdo** vem pelo resolvedor da `011`; a **identidade** da versão vem daqui, porque
    `UX-004` compara a versão que o ato cita com a que vige e o conteúdo não a carrega. A fonte é a
    mesma dos dois lados.
    """
    try:
        return effective_version(edital_id=edital.id)
    except DomainError:
        return None


def marcos_do_conteudo(conteudo):
    """`[(perfil, marco)]` — os marcos classificatórios que a versão vigente publica."""
    return [
        (perfil, marco)
        for perfil in (conteudo or {}).get("profiles") or []
        for marco in perfil.get("classificationMilestones") or []
    ]


def candidato_a_obsoleto(edital, ato, marco, versao_vigente):
    """O filtro barato de `T-003`: as duas causas das quatro divergências que `comparar` produz.

    ```text
    versão diferente da citada pelo ato   →  regra_ausente, regra_alterada
    Resultado vigente mais novo que o ato →  participantes_alterados, resultados_alterados
    ```

    **Conservador por construção, e a assimetria é deliberada**: ele admite candidato que a
    confirmação descarta, e nunca o contrário. Errar para mais custa uma chamada que devolve falso;
    errar para menos perde o sinal em silêncio, que é o defeito que ninguém descobre.
    """
    if versao_vigente is None or ato.versao_id != versao_vigente.id:
        return True
    etapas = [str(item) for item in marco.get("stages") or []]
    if not etapas:
        return False
    return ResultadoEtapa.vigentes.filter(
        edital=edital, etapa_id__in=etapas, consolidado_em__gt=ato.emitido_em
    ).exists()


def atos_obsoletos(edital, conteudo, versao_vigente):
    """Ato vigente **confirmado** obsoleto (`FR-029`).

    Duas passagens, e a segunda só onde a primeira acusar. Chamar `estado_do_marco` para todos os
    marcos de todos os Editais a cada abertura repetiria o erro que a `018` recusou: usar a
    verificação do ponto como varredura de listagem.

    O sinal nasce da **confirmação**. Parar na primeira passagem exibiria candidato como sinal, e
    fato posterior não implica divergência — um painel que erra uma vez deixa de ser lido.
    """
    for _, marco in marcos_do_conteudo(conteudo):
        marco_id = marco.get("id")
        ato = ato_vigente(edital=edital, marco_id=marco_id)
        if ato is None or not candidato_a_obsoleto(edital, ato, marco, versao_vigente):
            continue
        try:
            estado = estado_do_marco(edital=edital, marco_id=marco_id)
        except DomainError:
            # Marco que a norma vigente não conhece e ato que não existe: a leitura recusa, e a
            # supervisão não inventa sinal a partir de uma recusa.
            continue
        if not estado["obsoleto"]:
            continue
        nome = (estado["marco"] or {}).get("name") or marco.get("name") or str(marco_id)
        yield Sinal(
            especie=UX_004,
            edital=edital,
            alvo=nome,
            mensagem=(
                f"O ato de ordenação vigente do marco {nome}, do Edital "
                f"{rotulo_do_edital(edital)}, está obsoleto."
            ),
        )


# --- `UX-005` — recurso sem membro desimpedido ----------------------------------------------


def impedidos_por_recurso(pendentes):
    """`{recurso_id: {subject}}` — as cinco origens de `T-004`, por álgebra sobre autorias.

    **Sem uma verificação por par.** Iterar o guardião individual sobre `recursos × membros`
    reintroduziria o custo por linha que a `018` recusou: são cinco perguntas por par, e a pergunta
    da supervisão não é "este ator pode?", é "existe alguém?" (`FR-031`, `D-008`).

    Duas consultas, e as duas independentes do número de recursos: uma traz as autorias alcançadas
    pelas peças, outra os impedimentos declarados nas inscrições delas.
    """
    if not pendentes:
        return {}
    detalhados = Recurso.objects.filter(id__in=[peca.id for peca in pendentes]).select_related(
        "resultado_atacado",
        "resultado_atacado__avaliacao",
        "publicacao_atacada",
        "publicacao_atacada__ato",
    )
    declarados = {}
    for inscricao_id, subject in Impedimento.objects.filter(
        inscricao_id__in={peca.inscricao_id for peca in pendentes}
    ).values_list("inscricao_id", "identity_subject"):
        declarados.setdefault(inscricao_id, set()).add(subject)

    impedidos = {}
    for peca in detalhados:
        conjunto = set()
        # O alcance é o mesmo que o domínio define para leitura de listagem — o Resultado atacado
        # quando existe —, e não a cadeia histórica do par.
        resultado = peca.resultado_atacado
        if resultado is not None:
            if resultado.avaliacao_id is not None:
                conjunto.add(resultado.avaliacao.concluida_por)
            conjunto.add(resultado.consolidado_por)
        publicacao = peca.publicacao_atacada
        if publicacao is not None:
            conjunto.add(publicacao.ato.emitido_por)
            conjunto.add(publicacao.publicado_por)
        conjunto |= declarados.get(peca.inscricao_id, set())
        impedidos[peca.id] = {subject for subject in conjunto if subject}
    return impedidos


def comissao_impedida(processo, editais):
    """Recurso aguardando julgamento para o qual nenhum membro ativo está desimpedido (`FR-030`).

    **A mensagem se limita ao que verifica.** Julgar exige também a permissão sistêmica de julgar
    recurso, e o sistema não sabe quem a possui: os papéis vêm da sessão, e não há registro que
    ligue identidade a papel. Afirmar que o julgamento é impossível seria afirmar o que os dados
    não sustentam — alguém de fora da comissão pode detê-la (`FR-030a`, `T-004`).
    """
    membros = {membro.identity_subject for membro in comissao_selectors.membros(processo)}
    if not membros:
        # Sem comissão ativa não há "comissão inteira impedida": há ausência de comissão, que é
        # outra condição e não está no catálogo.
        return
    for edital in editais:
        pendentes = [
            linha["recurso"]
            for linha in recursos_selectors.recursos_do_edital(
                edital, situacao=recursos_selectors.AGUARDANDO_JULGAMENTO
            )
        ]
        impedidos = impedidos_por_recurso(pendentes)
        if not any(not (membros - impedidos.get(peca.id, set())) for peca in pendentes):
            continue
        yield Sinal(
            especie=UX_005,
            edital=edital,
            alvo=rotulo_do_edital(edital),
            mensagem=(
                f"Há recurso aguardando julgamento no Edital {rotulo_do_edital(edital)} para o "
                f"qual todos os membros da comissão estão impedidos de julgar."
            ),
        )


# --- A região inteira ------------------------------------------------------------------------


def sinais(processo, ator, *, agora=None):
    """Os sinais deste Processo, na ordem do catálogo — e nada além deles.

    A ordem é a de `ESPECIES`, e não uma de gravidade: os cinco são igualmente acionáveis, e
    ordená-los por severidade pediria um juízo que o domínio não determina (`D-002`).
    """
    agora = agora or timezone.now()
    leitura = leitura_dos_editais(processo)
    publicados = [(edital, conteudo) for edital, conteudo in leitura if conteudo is not None]
    achados = []
    for edital, conteudo in publicados:
        achados += list(etapas_sem_marco(edital, conteudo))
        achados += list(divergencias_temporais(edital, conteudo, agora))
        achados += list(cobertura_insuficiente(edital, conteudo))
        achados += list(atos_obsoletos(edital, conteudo, versao_vigente_do_edital(edital)))
    achados += list(comissao_impedida(processo, [edital for edital, _ in publicados]))
    achados.sort(key=lambda sinal: (ESPECIES.index(sinal.especie), sinal.alvo))
    return tuple(achados)


__all__ = [
    "ANTES_DO_INICIO",
    "COERENTES",
    "DECLARACOES",
    "DENTRO_DO_INTERVALO",
    "DEPOIS_DO_TERMINO",
    "ESPECIES",
    "UX_001",
    "UX_002",
    "UX_003",
    "UX_004",
    "UX_005",
    "Destino",
    "Marco",
    "Medida",
    "PeriodoDeInscricoes",
    "PontoDaSerie",
    "Pulso",
    "PulsoDoEdital",
    "SEM_CRONOGRAMA",
    "SEM_PERIODO",
    "Sinal",
    "JANELA_RECENTE",
    "contagens_por_edital",
    "conteudo_ou_nada",
    "editais_do_processo",
    "etapas_do_conteudo",
    "eventos_do_conteudo",
    "instantes_do_evento",
    "leitura_dos_editais",
    "marcos_do_edital",
    "periodo_do_edital",
    "pode_supervisionar",
    "posicao_temporal",
    "pulso",
    "serie_do_edital",
    "sinais",
    "submetidas_nas_ultimas_24h",
]
