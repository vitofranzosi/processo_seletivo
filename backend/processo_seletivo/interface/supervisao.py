"""A supervisão do Processo: as formas de leitura e as derivações que as preenchem.

**Este módulo só lê.** Nenhum `save`, `create`, `update` ou `delete` nasce aqui, e a ausência é o
invariante da feature: a `022` é composição de leituras que sete apps já persistem, e a necessidade
de gravar estado é motivo para revisar a spec, não para escrever migration (`D-007`, `FR-007`).

Ele fica fora de `views.py` de propósito. Aqui vivem as derivações, e mantê-las separadas da
montagem de contexto é o que permite testá-las como domínio de leitura, sem requisição.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.avaliacoes.application.selectors import resumo_da_etapa
from processo_seletivo.avaliacoes.models import Impedimento
from processo_seletivo.classificacao.application.selectors import (
    ORIGEM_SORTEIO,
    ato_vigente,
    estado_do_marco,
)
from processo_seletivo.comissoes.application import selectors as comissao_selectors
from processo_seletivo.comissoes.domain.autorizacao import pode_gerir_comissao
from processo_seletivo.comissoes.domain.etapas import conteudo_vigente
from processo_seletivo.divulgacao.application.selectors import (
    divulgacao_do_ato,
    historico_do_marco,
)
from processo_seletivo.editais.domain import calendario
from processo_seletivo.editais.models.cronograma import EventoCronograma
from processo_seletivo.inscricoes.domain.periodo import (
    ABERTO,
    ENCERRADO,
    FUTURO,
    periodo_de_inscricoes,
)
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface.conducao import CONDUCAO_DA_RETIFICACAO
from processo_seletivo.ocupacao.application.selectors import apuracao_vigente
from processo_seletivo.processos.domain.finalizacao import PROCESSO_FINAL
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.recursos.application import admitir as recursos_admitir
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

# A janela da leitura recente (`FR-013`). Vinte e quatro horas **abertas no início**: a submissão de
# exatamente 24 h fica de fora, porque incluí-la contaria um dia e um instante.
#
# **Os artefatos divergem neste ponto, e a escolha é registrada.** `data-model.md` §3.1 escreve
# `submitted_at ≥ agora − 24h`; a T018 da `tasks.md` manda excluir "a de exatamente 24 h", com a
# razão dita — "a borda é onde o fora-por-um mora". Vale a segunda, porque ela é a única das duas
# que raciocina sobre a borda. Fechar a divergência no `data-model.md` é governança do usuário.
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
    # A fase **derivada** do relógio (045, `FR-735`), e não mais o `status` declarado: ele nascia
    # planejado e ficava, e a tela escrevia *"declarado planejado"* ao lado de todo marco de todo
    # Edital composto pela tela. Só *planejado* e *em andamento* chegam aqui — o concluído sai.
    fase: str

    @property
    def em_andamento(self) -> bool:
        """O marco em curso é o único que ganha marca: o futuro, a data já diz (`UX-088`)."""
        return self.fase == calendario.EM_ANDAMENTO


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
    # **O que se conta** (045, `FR-743`, `UX-087`). *"2 de 5"* não dizia se eram inscrições,
    # avaliações ou recortes. Declarada por quem monta o sinal — é da espécie, e não do template —,
    # no singular; o plural sai do denominador. Fora da comparação: duas medidas do mesmo par são a
    # mesma medida, e a unidade é como ela se lê.
    unidade: str = field(default="", compare=False)

    @property
    def unidade_legivel(self) -> str:
        return self.unidade if self.denominador == 1 else PLURAIS.get(self.unidade, self.unidade)


# As unidades que as medidas da Atenção contam. Poucas e fixas: uma tabela lê melhor que uma regra
# de plural, e "inscrição" → "inscrições" não sai de acrescentar um `s`.
INSCRICAO, RECURSO, RECORTE = "inscrição", "recurso", "recorte"
PLURAIS = {INSCRICAO: "inscrições", RECURSO: "recursos", RECORTE: "recortes"}


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
    # Ausente quando o leitor não pratica o ato para onde o sinal encaminharia (`FR-036`). Sinal
    # cujo **destino o ator não alcança** não chega a ser montado (`FR-004`), e por isso a ausência
    # aqui nunca significa supressão por alcance.
    destino: Destino | None = None
    # **A quem pedir**, quando o sinal fica sem caminho porque o ato não é do leitor (045,
    # `FR-740`). Vazio quando há caminho: dizer "peça a alguém" a quem tem o formulário à frente é
    # falso (037, `FR-544`). Sai do mecanismo único (`interface/conducao.py`), nunca redigido aqui.
    conducao: str = ""


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
        # **O teto é o instante declarado da leitura**, e não "agora" de novo. Sem ele a janela
        # ficava aberta para o futuro: uma submissão concorrente, gravada entre a montagem do
        # `Pulso` e esta contagem, entrava nas 24 horas e ficava **fora** da série — que sempre
        # teve teto. A página declara `lido_em` e contava um ato posterior a ele; e uma chamada com
        # `agora=` explícito, que existe para ser determinística, não era.
        submitted_at__lte=agora,
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


# A fase do período de inscrições sai do **estado do período**, e não da régua geral: sem
# término, o período segue aberto (FR-347), e a régua geral o venceria pelo início (045, `R-3`).
FASE_DO_PERIODO = {
    FUTURO: calendario.PLANEJADO,
    ABERTO: calendario.EM_ANDAMENTO,
    ENCERRADO: calendario.CONCLUIDO,
}


def fase_do_evento(evento, conteudo, agora):
    """A fase ordinária de um Evento publicado, ou `None` para o cancelado e o sem início.

    **O `status` publicado só responde se o Evento foi cancelado** (045, `FR-736`). Qualquer outro
    valor — o `PLANEJADO` que todo Evento carrega, ou um `EM_ANDAMENTO` que a API aceitava antes
    — é lido como *não cancelado*, e a fase vem das datas. O conteúdo publicado não é reescrito.

    **Duas réguas, e nenhuma nova**: a do período de inscrições para o Evento marcado como tal, e
    a do vencido (`calendario.fase`) para os demais.
    """
    if evento.get("status") == EventoCronograma.Status.CANCELADO:
        return None
    if evento.get("isRegistrationPeriod") is True:
        return FASE_DO_PERIODO.get(periodo_de_inscricoes(conteudo, agora).estado)
    inicio, fim = instantes_do_evento(evento)
    return calendario.fase(inicio, fim, agora=agora)


def marcos_do_edital(edital, conteudo, agora):
    """Os marcos que ainda vêm, em ordem cronológica e sem os cancelados (`FR-021`).

    **O marco em curso ainda é próximo.** O corte é a fase **concluída**, e não o início: tirar da
    lista o que está acontecendo esconderia justamente o prazo que corre.

    **E o corte é o da régua, e não um quarto critério** (045, `R-3`). A lista cortava por
    `término or início <= agora` — com `<=` onde a régua usa `<`, e tirando da lista o período de
    inscrições sem término no instante em que ele abria, enquanto o período continuava recebendo
    inscrição. Passa a sair o marco concluído, e só ele.

    `CANCELADO` sai da leitura temporal: o Evento deixou o cronograma efetivo, e cobrar prazo dele
    seria cobrar de quem já foi cancelado.
    """
    marcos = []
    for evento in eventos_do_conteudo(conteudo):
        fase = fase_do_evento(evento, conteudo, agora)
        if fase is None or fase == calendario.CONCLUIDO:
            continue
        inicio, fim = instantes_do_evento(evento)
        marcos.append(
            Marco(
                edital=edital,
                descricao=descricao_do_evento(evento),
                inicio=inicio,
                fim=fim,
                fase=fase,
            )
        )
    marcos.sort(key=lambda marco: (marco.inicio or marco.fim, marco.descricao))
    return tuple(marcos)


def descricao_do_evento(evento):
    return evento.get("description") or evento.get("type") or ""


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
# 7. Atenção — o catálogo fechado dos sinais
#
# Perguntas nomeadas, e nenhum mecanismo genérico. Acrescentar uma é revisar a spec, e
# `tests/unit/interface/test_supervisao.py` é o que torna essa regra cobrável (`D-002`, `FR-565`).
#
# **O número saiu deste cabeçalho de propósito** (038). Ele dizia "cinco" desde a `022`, e continuou
# dizendo depois de a `027` acrescentar a sexta: um comentário que conta é um segundo catálogo, e
# ele envelhece sem que nada fique vermelho. Quem conta é `ESPECIES`, e o guarda que o prende é o
# teste nomeado acima.
# ---------------------------------------------------------------------------

# **O `UX-001` e o `UX-002` saíram do catálogo** (045, `FR-738`, `FR-739`, `FR-744`). O primeiro —
# a Etapa sem marco no cronograma — é imperfeição de **composição**, e passou a aviso da validação
# do conteúdo, onde tem remédio; na condução ele levava a uma Retificação que não alcança o vínculo.
# O segundo comparava o `status` declarado com o relógio, e o `status` deixou de ser declarado: a
# fase é derivada, e declarado e relógio não têm mais como discordar. Os identificadores não são
# reaproveitados — citados em spec e em teste, voltariam a significar outra coisa.
UX_003 = "UX-003"
UX_004 = "UX-004"
UX_005 = "UX-005"
# A sexta espécie é da `027`, e por isso carrega o identificador dela: o acervo publicado que
# declara vaga imediata e não declara a linha do quadro — e que, por isso, não tem quantidade a
# apurar nem a convocar.
UX_046 = "UX-046"

# As espécies da `038`, que levam a Atenção à **cauda** do certame — o que para depois da
# avaliação. Cada uma carrega o identificador daquela feature, e cada uma é a **negação ou a
# vizinha** de uma que já existia: ler a mensagem da vizinha em vez da condição é o que faria as
# duas dispararem pelo mesmo fato (`R-1`).
#
# `UX-063` não é o `UX-003`: aquele mede **cobertura** — se há avaliador suficiente —, este mede se
# o trabalho **andou**.
UX_063 = "UX-063"
# `UX-064` é a **negação da condição** do `UX-005`, e os dois nascem do mesmo cálculo. Nenhuma peça
# cai nos dois (`FR-561`).
UX_064 = "UX-064"
# `UX-065` é ordem emitida cuja ocupação ninguém apurou.
UX_065 = "UX-065"
# `UX-066` não é o `UX-004`: aquele fala da ordem que **ficou para trás**, este da ordem que
# **ninguém publicou**. Um mesmo marco pode ter os dois, e deve — são dois fatos sobre o mesmo ato,
# e cada um se resolve numa tela diferente.
UX_066 = "UX-066"

ESPECIES = (
    UX_003,
    UX_004,
    UX_005,
    UX_046,
    UX_063,
    UX_064,
    UX_065,
    UX_066,
)

# As quatro espécies da `038` falam de **trabalho pendente** — coisa parada que alguém retoma.
TRABALHO_PENDENTE = frozenset({UX_063, UX_064, UX_065, UX_066})

# Os dois estados em que o Edital **parou por ato**. Depois deles não há trabalho a retomar: o que
# parou, parou porque alguém o encerrou ou o cancelou, e apontar avaliação pendente num Edital
# encerrado mandaria concluir o que a instituição decidiu não concluir.
EDITAL_PAROU_POR_ATO = frozenset({Edital.Status.ENCERRADO, Edital.Status.CANCELADO})


def alcance_no_edital(alcancadas, edital):
    """O alcance do ator **neste** Edital — o geral, menos o que o estado dele já respondeu.

    **Só as espécies de trabalho pendente são retiradas, e a assimetria é deliberada** (`038`). O
    `UX-004` fala de ordem que envelheceu, e ela envelhece depois do encerramento como antes — e
    reemitir a ordem continua possível enquanto o **Processo** não termina; o `UX-005` fala de peça
    que continua podendo ser decidida (045, `research.md`, `R-7`).

    *A premissa que a `038` escreveu aqui para o `UX-001` e o `UX-002` — "um Edital encerrado
    continua podendo Retificar" — era falsa*: a Retificação só incide sobre Edital publicado. Os
    dois saíram do catálogo, e o `UX-046`, que leva à Retificação, sai da Atenção onde ela não é
    possível (`admite_encaminhamento`, 045, `FR-741`).

    As quatro da `038` são outra coisa: cada uma aponta trabalho a **retomar**, e trabalho não se
    retoma num Edital que parou por ato.
    """
    if edital.status not in EDITAL_PAROU_POR_ATO:
        return alcancadas
    return {
        especie: valor and especie not in TRABALHO_PENDENTE for especie, valor in alcancadas.items()
    }


def rotulo_do_edital(edital):
    return f"{edital.number}/{edital.year}"


def nome_da_etapa(etapa):
    return etapa.get("name") or str(etapa.get("id") or "")


def _citado(texto):
    """O nome de uma Etapa ou de um Evento, encaixado no meio de uma frase.

    A descrição publicada costuma ser uma frase inteira, com ponto final — *"Inscrições pelo
    sistema, com isenção de taxa até o 5º dia."* Encaixá-la crua produzia *"… 5º dia., do Edital
    01/2026:"*, com o ponto no meio da oração. Tirar a pontuação terminal é a mesma coisa que se
    faz ao citar uma frase dentro de outra.
    """
    return (texto or "").strip().rstrip(".;,")


# --- A Etapa: **uma leitura, duas perguntas** (`UX-003` e `UX-063`) --------------------------


def sinais_da_etapa(edital, conteudo, encaminhar, alcancadas):
    """As duas perguntas que se fazem sobre a mesma Etapa, com **uma** chamada de `resumo_da_etapa`.

    **Ter avaliador não é ter avaliação**, e as duas perguntas são distintas: a cobertura pergunta
    se há quem avalie, o trabalho parado pergunta se quem tem avaliador já foi avaliado. Uma Etapa
    coberta com cinquenta avaliações paradas responde "sim" à primeira e "não" à segunda.

    **A leitura é uma só, e é por isso que esta função existe** (`FR-557`, `038`). Escrever a
    espécie nova como um gerador ao lado custaria **uma agregação a mais por Etapa** — o mesmo
    número, buscado duas vezes, que é exatamente a segunda verdade que este projeto vem removendo.
    O `resumo` desce como argumento para que cada espécie continue tendo a função dela.

    O alcance entra aqui, e não na porta, porque a leitura serve às duas: suprimir a espécie que o
    ator não alcança é decisão **por sinal** (`FR-004`), e não motivo para deixar de ler.
    """
    if not (alcancadas[UX_003] or alcancadas[UX_063]):
        return
    for etapa in etapas_do_conteudo(conteudo):
        # O conteúdo publicado já está na mão, e vai junto: dele saem as Etapas anteriores, o gate
        # e o corte que decidem quem participa — uma versão só, sem reler (045, `FR-742`).
        resumo = resumo_da_etapa(edital=edital, etapa=etapa, conteudo=conteudo)
        if alcancadas[UX_003]:
            yield from cobertura_insuficiente(edital, etapa, resumo, encaminhar)
        if alcancadas[UX_063]:
            yield from avaliacao_parada(edital, etapa, resumo, encaminhar)


def cobertura_insuficiente(edital, etapa, resumo, encaminhar):
    """Etapa com inscrição carente de avaliador, com numerador e denominador (`FR-028`).

    Reusa `resumo_da_etapa` **como está**: uma agregação por Etapa, e não um laço sobre inscrições.
    A unidade sem nenhum avaliador é carente e permanece no denominador — retirá-la faria a
    cobertura parecer completa justamente onde ela não começou (`FR-033`).

    **O denominador é de participantes** (045, `FR-742`): a inscrição eliminada antes, à espera da
    Etapa anterior ou fora do corte não é trabalho esperado aqui, e contá-la dizia *"2 de 5"* sobre
    uma lista de quatro. Quem escolhe a população é o resumo, e não este sinal.

    O `resumo` chega pronto de `sinais_da_etapa`, que o lê uma vez para as duas espécies.
    """
    if not resumo["carentes"]:
        return
    nome = nome_da_etapa(etapa)
    yield Sinal(
        especie=UX_003,
        edital=edital,
        alvo=nome,
        medida=Medida(
            numerador=resumo["carentes"], denominador=resumo["inscricoes"], unidade=INSCRICAO
        ),
        mensagem=(
            f"A Etapa {_citado(nome)}, do Edital {rotulo_do_edital(edital)}, "
            f"tem inscrição sem avaliador suficiente."
        ),
        destino=encaminhar(UX_003, edital, etapa.get("id")),
    )


def avaliacao_parada(edital, etapa, resumo, encaminhar):
    """Inscrição com avaliação **distribuída e não concluída** (`FR-560`, `UX-063`).

    **A condição é a distribuída que não andou**, e não a que nunca foi distribuída: a segunda é o
    `UX-003`, que mede cobertura. Uma Etapa sem distribuição nenhuma tem `completas` zerado, e esta
    espécie não dispara nela — é o que impede os dois sinais de saírem pelo mesmo fato.

    **`resumo_da_etapa` não devolve `avaliadas`**, e a medição desta feature foi encontrá-lo: o que
    ele devolve é `sem_conclusao = inscricoes − avaliadas`. A conta é a mesma, e escrevê-la com o
    nome que existe é o que impede o próximo leitor de procurar uma chave que não está lá.

    A medida é **paradas sobre distribuídas** (`FR-032`): o denominador é o universo que já tem
    avaliador, porque é sobre ele que a pergunta do progresso se faz. Usar o total de inscrições
    diluiria a parada num universo que ainda nem começou a ser distribuído.
    """
    avaliadas = resumo["inscricoes"] - resumo["sem_conclusao"]
    paradas = resumo["completas"] - avaliadas
    if paradas <= 0:
        return
    nome = nome_da_etapa(etapa)
    yield Sinal(
        especie=UX_063,
        edital=edital,
        alvo=nome,
        medida=Medida(numerador=paradas, denominador=resumo["completas"], unidade=INSCRICAO),
        mensagem=(
            f"A Etapa {_citado(nome)}, do Edital {rotulo_do_edital(edital)}, tem avaliação "
            f"distribuída e não concluída."
        ),
        destino=encaminhar(UX_063, edital, etapa.get("id")),
    )


# --- `UX-046` — o Edital publica vaga e não publica quadro (027) -----------------------------


def acervo_sem_quadro(edital, conteudo, encaminhar):
    """Perfil publicado que declara vaga imediata e não declara a linha do quadro (027, FR-331).

    **É a metade que faz a US4 ser praticada, e não só possível.** A advertência da Retificação só
    aparece para quem já abriu a Retificação daquele Edital; quem supervisiona não tem como saber
    quais Editais precisam do ato sem abrir um por um. Sem esta leitura, o caminho existe e ninguém
    o encontra.

    A medida é **recortes sem quantidade sobre recortes publicados**, e não Perfis: é o recorte que
    a Ocupação apura, e é nele que a ausência dói. Um Perfil com ampla e duas reservadas declaradas,
    e nenhuma linha, conta três.

    Lê o conteúdo vigente que a supervisão **já** carregou por Edital — nenhuma consulta nova.
    """
    for posicao, perfil in enumerate(conteudo.get("profiles") or []):
        if not isinstance(perfil, dict):
            continue
        # **Zero é uma declaração, e ausência não é zero** (025, D-005). Um Perfil legado que
        # publica `0` vaga imediata e nenhuma linha continua sem dizer quanto a ampla concorrência
        # tem: a Ocupação responde "não publicou quadro", e não "zero". Excluir o `0` daqui faria a
        # FR-331 alcançar quase todo o acervo em vez de todo ele — e o `TEC-LAB` da demonstração é
        # exatamente essa forma. Negativo continua de fora porque a conferência de forma já o
        # recusa, e empilhar duas acusações sobre a mesma causa esconde a que resolve.
        total = perfil.get("immediateVacancies")
        if isinstance(total, bool) or not isinstance(total, int) or total < 0:
            continue
        recortes, sem_linha = _recortes_do_perfil(perfil)
        if not sem_linha:
            continue
        rotulo = perfil.get("code") or perfil.get("name") or f"Perfil {posicao + 1}"
        destino = encaminhar(UX_046, edital)
        yield Sinal(
            especie=UX_046,
            edital=edital,
            alvo=rotulo,
            medida=Medida(numerador=sem_linha, denominador=recortes, unidade=RECORTE),
            # **A mensagem não repete a medida** (045, `UX-087`): ela dizia "para 1 de 2
            # recorte(s)", e a medida logo abaixo dizia "1 de 2" de novo. O número fica na medida,
            # com a unidade; a frase diz o que ele significa.
            mensagem=(
                f"O Perfil {_citado(rotulo)}, do Edital {rotulo_do_edital(edital)}, publica "
                f"{total} vaga(s) imediata(s) e não publica quantidade para todos os seus "
                f"recortes: a ocupação e a convocação não têm o que apurar nos que ficaram sem."
            ),
            destino=destino,
            # Sem caminho aqui é **falta de permissão**, e nunca situação: onde a Retificação não
            # é possível o sinal nem é montado (`situacao_admite_retificacao`, 045, `FR-741`).
            conducao="" if destino is not None else CONDUCAO_DA_RETIFICACAO,
        )


def _recortes_do_perfil(perfil):
    """Quantos recortes o Perfil publica, e quantos deles não têm linha no quadro.

    **A ampla concorrência é sempre um recorte**, tenha ou não Modalidade homônima declarada: é o
    recorte de que todos participam, e a quantidade dele mora na linha geral. As reservadas são as
    demais Modalidades — descontada a que o Perfil declara ser a da ampla, que não tem linha
    própria por norma (`025`, D-004).
    """
    ampla = perfil.get("generalCompetitionModalityId")
    ampla = str(ampla) if ampla else None
    reservadas = {
        str(modalidade["id"])
        for modalidade in perfil.get("competitionModalities") or []
        if isinstance(modalidade, dict) and modalidade.get("id") and str(modalidade["id"]) != ampla
    }
    linhas = [linha for linha in perfil.get("vacancyTable") or [] if isinstance(linha, dict)]
    com_linha = {str(linha["modalityId"]) for linha in linhas if linha.get("modalityId")}
    tem_geral = any(not linha.get("modalityId") for linha in linhas)
    sem_linha = len(reservadas - com_linha) + (0 if tem_geral else 1)
    return len(reservadas) + 1, sem_linha


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


def sorteado(ato):
    """Se o ato veio de sorteio. A marca está no universo que ele gravou (`021`, `FR-069`)."""
    return (ato.universo or {}).get("origem") == ORIGEM_SORTEIO


def listas_do_marco(perfil, marco, conteudo=None):
    """Os recortes daquele marco: `[(lista_id, nome)]`, ampla concorrência primeiro.

    **Só o sorteio emite ato por lista** (`021`, `D-006`): um marco de cotas produz três atos raiz
    — ampla, e uma por modalidade de reserva —, e perguntar pelo "ato vigente do marco" sem dizer
    de qual lista devolveria um dos três pela ordem de emissão. Um marco computado tem um recorte
    só, e percorrer as modalidades dele custaria uma consulta por modalidade para não encontrar ato
    nenhum.

    `conteudo` é o da versão vigente, e existe porque a pergunta "este marco sorteia" passou a ter
    resolução própria (030, FR-429): o marco pode referenciar o método comum do Edital, e ler só a
    chave dele responderia que não. Sem o conteúdo, a leitura cai na chave — que é o que todo
    Edital publicado antes desta feature carrega, e sobre ele a resposta é a mesma.
    """
    from processo_seletivo.editais.domain import marcos

    sorteia = (
        marcos.marco_ordena_por_sorteio(
            conteudo, perfil_id=perfil.get("id"), marco_id=marco.get("id")
        )
        if conteudo is not None
        else bool(marco.get("drawMethod"))
    )
    if not sorteia:
        return [(None, "")]
    return [(None, "")] + [
        (modalidade.get("id"), modalidade.get("name") or "")
        for modalidade in perfil.get("competitionModalities") or []
        if modalidade.get("id")
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
    if sorteado(ato):
        # **O ato sorteado escapa das duas condições**, e escaparia em silêncio: ele fica obsoleto
        # quando a relação de habilitados que o originou ganha sucessora, e uma relação nova não
        # muda a versão do Edital nem produz `ResultadoEtapa`. O filtro se afasta em vez de ganhar
        # uma terceira condição porque a confirmação exata **dele já é barata**: aferir um ato de
        # sorteio é ler a sucessão da relação, e não recalcular a ordem — a razão de existir do
        # filtro não se aplica aqui (`T-003`, `021`, `FR-069`).
        return True
    if versao_vigente is None or ato.versao_id != versao_vigente.id:
        return True
    etapas = [str(item) for item in marco.get("stages") or []]
    if not etapas:
        return False
    return ResultadoEtapa.vigentes.filter(
        edital=edital, etapa_id__in=etapas, consolidado_em__gt=ato.emitido_em
    ).exists()


def sinais_do_marco(edital, conteudo, versao_vigente, encaminhar, alcancadas):
    """As duas perguntas sobre o **ato vigente de cada recorte**, com uma leitura dele só.

    **O ato é lido uma vez e serve às duas** (`FR-557`, `038`): a obsolescência pergunta se a ordem
    ficou para trás, a ocupação pergunta se alguém apurou o que ela produziu. Um gerador ao lado
    releria `ato_vigente` por recorte, e o custo da espécie nova dobraria antes de ela existir.

    **Uma leitura por recorte, e nunca uma visita por lista** — é a forma que a `034` adotou, e a
    razão é a mesma: são no máximo as listas que o Perfil declara, e é a mesma pergunta que a tela
    da ocupação faz para uma delas. `recortes_do_marco` responderia mais, e custaria os quatro
    números de cada recorte para decidir uma pergunta de sim ou não.
    """
    if not (alcancadas[UX_004] or alcancadas[UX_065] or alcancadas[UX_066]):
        return
    for perfil, marco in marcos_do_conteudo(conteudo):
        marco_id = marco.get("id")
        # **A cadeia de publicações é do marco, e não do recorte**, e por isso é lida uma vez para
        # todas as listas dele. Relê-la por recorte custaria uma consulta por lista para devolver
        # exatamente as mesmas linhas — e o filtro por lista é feito sobre elas, em memória.
        #
        # Preguiçosa de propósito: um marco cujos recortes não têm ato não chega a pagá-la.
        historico = None
        for lista_id, nome_da_lista in listas_do_marco(perfil, marco, conteudo):
            ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
            # **As três espécies falam de um ato que existe.** Sem ato não há ordem que envelheça,
            # ocupação a apurar nem resultado a divulgar: o recorte ainda não chegou lá, e isso não
            # é sinal.
            if ato is None:
                continue
            if alcancadas[UX_004]:
                yield from atos_obsoletos(
                    edital,
                    marco,
                    marco_id,
                    lista_id,
                    nome_da_lista,
                    ato,
                    versao_vigente,
                    encaminhar,
                )
            if alcancadas[UX_065]:
                yield from recorte_sem_ocupacao(
                    edital, perfil, marco, marco_id, lista_id, nome_da_lista, encaminhar
                )
            if alcancadas[UX_066]:
                if historico is None:
                    historico = historico_do_marco(edital=edital, marco_id=marco_id)
                yield from ato_sem_divulgacao(
                    edital, marco, marco_id, lista_id, nome_da_lista, ato, historico, encaminhar
                )


def recorte_sem_ocupacao(edital, perfil, marco, marco_id, lista_id, nome_da_lista, encaminhar):
    """Recorte com ordem vigente e **sem apuração vigente** (`FR-563`, `UX-065`).

    **Esta é a única das três espécies da `US2a` que acrescenta consulta**, e o custo foi medido
    antes de ser pago: a Supervisão já lia `ato_vigente` para o `UX-004`, mas não lia nada de
    `ocupacao` — `apuracao_vigente` não aparecia neste módulo. É **uma leitura por recorte**, e
    nenhuma por participante.

    **Não é obsolescência**: o `UX-004` fala da ordem que ficou para trás, e esta fala da ordem que
    ninguém apurou. Um recorte pode disparar os dois, e deve: são dois fatos sobre o mesmo ato — a
    ordem envelheceu **e** a ocupação nunca foi feita —, e cada um se resolve numa tela diferente.
    """
    if (
        apuracao_vigente(
            edital=edital, perfil_id=perfil["id"], marco_id=marco_id, lista_id=lista_id
        )
        is not None
    ):
        return
    nome = marco.get("name") or str(marco_id)
    alvo = f"{nome} — {nome_da_lista}" if nome_da_lista else nome
    yield Sinal(
        especie=UX_065,
        edital=edital,
        alvo=alvo,
        mensagem=(
            f"O marco {_citado(alvo)}, do Edital {rotulo_do_edital(edital)}, tem ordem vigente e "
            f"nenhuma apuração de ocupação."
        ),
        destino=encaminhar(UX_065, edital, marco_id),
    )


def ato_sem_divulgacao(
    edital, marco, marco_id, lista_id, nome_da_lista, ato, historico, encaminhar
):
    """Ato de ordenação vigente **sem divulgação vigente** (`FR-562`, `UX-066`).

    **A derivação não é escrita aqui: é lida de onde a tela de destino a lê** (`FR-557`). Ela vivia
    dentro de `interface/views.py`, num ajudante privado, e foi **extraída** para
    `divulgacao.application.selectors`. Reescrevê-la neste sinal daria duas respostas para a mesma
    pergunta, e a primeira a mudar deixaria a outra para trás sem que nada ficasse vermelho.

    **Duas formas de não estar divulgado, e o mesmo destino.** Ou ninguém publicou aquele ato, ou o
    que está publicado é de um ato anterior — e nos dois casos o resultado que o público lê não é o
    que vale. A frase distingue as duas porque quem conduz age diferente: a primeira é uma
    divulgação que falta, a segunda é uma que ficou para trás.

    **Não é o `UX-004`.** Aquele diz que a ordem envelheceu; este, que ela não foi publicada. Um
    marco pode ter os dois, e os dois se resolvem em telas diferentes — suprimir um deles aqui
    esconderia trabalho que ninguém mais apontaria.
    """
    estado = divulgacao_do_ato(
        edital=edital, marco_id=marco_id, ato=ato, lista_id=lista_id, historico=historico
    )
    if estado is None or not (estado["nunca_divulgado"] or estado["defasadas"]):
        return
    nome = marco.get("name") or str(marco_id)
    alvo = f"{nome} — {nome_da_lista}" if nome_da_lista else nome
    razao = (
        "não foi divulgado"
        if estado["nunca_divulgado"]
        else "não é o que está divulgado: o público lê um ato anterior"
    )
    yield Sinal(
        especie=UX_066,
        edital=edital,
        alvo=alvo,
        mensagem=(
            f"O ato de ordenação vigente do marco {_citado(alvo)}, do Edital "
            f"{rotulo_do_edital(edital)}, {razao}."
        ),
        destino=encaminhar(UX_066, edital, marco_id, ato=ato),
    )


def atos_obsoletos(
    edital, marco, marco_id, lista_id, nome_da_lista, ato, versao_vigente, encaminhar
):
    """Ato vigente **confirmado** obsoleto (`FR-029`).

    Duas passagens, e a segunda só onde a primeira acusar. Chamar `estado_do_marco` para todos os
    marcos de todos os Editais a cada abertura repetiria o erro que a `018` recusou: usar a
    verificação do ponto como varredura de listagem.

    O sinal nasce da **confirmação**. Parar na primeira passagem exibiria candidato como sinal, e
    fato posterior não implica divergência — um painel que erra uma vez deixa de ser lido.

    O ato e o recorte chegam prontos de `sinais_do_marco`, que os lê uma vez para as duas espécies.
    """
    if not candidato_a_obsoleto(edital, ato, marco, versao_vigente):
        return
    try:
        estado = estado_do_marco(edital=edital, marco_id=marco_id, lista_id=lista_id)
    except DomainError:
        # Marco que a norma vigente não conhece e ato que não existe: a leitura recusa, e a
        # supervisão não inventa sinal a partir de uma recusa.
        return
    if not estado["obsoleto"]:
        return
    nome = (estado["marco"] or {}).get("name") or marco.get("name") or str(marco_id)
    # O recorte entra no alvo porque um marco de cotas tem três atos: sem ele os três sinais
    # sairiam com a mesma frase, e quem lesse não saberia qual lista abrir.
    alvo = f"{nome} — {nome_da_lista}" if nome_da_lista else nome
    yield Sinal(
        especie=UX_004,
        edital=edital,
        alvo=alvo,
        mensagem=(
            f"O ato de ordenação vigente do marco {alvo}, do Edital "
            f"{rotulo_do_edital(edital)}, está obsoleto."
        ),
        # A dona não é a mesma nos dois casos: a ordenação diagnostica a divergência de um ato
        # computado, e o sorteio é onde uma ordem sorteada se refaz — com relação nova e
        # ocorrência nova. Mandar um sorteio para a ordenação levaria a uma tela que oferece
        # recalcular o que só uma semente nova produz.
        destino=encaminhar(UX_004, edital, marco_id, sorteio=sorteado(ato)),
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


# As duas fases em que uma peça **espera decisão** de quem tem a permissão de julgar (`045`,
# `FR-732`). Admitir e julgar exigem a mesma permissão e a mesma regra de impedimento, e para quem
# conduz as duas são o mesmo fato — por isso uma espécie cobre as duas, e a mensagem diz qual.
AGUARDANDO_DECISAO = (
    recursos_selectors.AGUARDANDO_ADMISSIBILIDADE,
    recursos_selectors.AGUARDANDO_JULGAMENTO,
)


def fase_das_pecas(situacoes):
    """A fase que a mensagem nomeia, para as peças que **aquele** sinal conta (`UX-085`).

    Um sinal pode contar peças nas duas fases; dizer só uma delas faria quem abre a tela procurar a
    fase errada. A distinção fina continua sendo da tela dos recursos: aqui ela só é nomeada.
    """
    fases = set(situacoes)
    if fases == {recursos_selectors.AGUARDANDO_ADMISSIBILIDADE}:
        return "admissibilidade"
    if fases == {recursos_selectors.AGUARDANDO_JULGAMENTO}:
        return "julgamento"
    return "decisão — admissibilidade ou julgamento"


def sinais_do_recurso(processo, editais, encaminhar, alcancadas):
    """As peças que esperam decisão, **partidas em dois desfechos por um cálculo só** (`FR-561`).

    **Um fato, um sinal.** A peça cujos membros estão todos impedidos é o `UX-005`; a que tem ao
    menos um livre é o `UX-064`. A partição é por construção — as duas listas saem do **mesmo**
    conjunto `membros - impedidos`, e nenhuma peça cai nas duas.

    **É por isso que isto é um ato só, e não duas funções.** Calculadas em lugares separados, uma
    mudança na regra de impedimento moveria um sinal e deixaria o outro para trás, e os dois
    passariam a discordar sobre a mesma peça sem que nada ficasse vermelho.

    **A peça recém-interposta também espera** (`045`, `FR-732`). A `038` lia só as admitidas, e o
    recurso ficava invisível na condução, para todo papel, justamente até alguém o admitir — e só
    o admitia quem o achava por outro caminho. A mesma partição vale para a admissibilidade sem
    mudar o cálculo: admitir confere o impedimento **sem** Etapa, sobre o Resultado atacado
    (`recursos/application/admitir.py`), que é exatamente o alcance de `impedidos_por_recurso`.

    **A mensagem se limita ao que verifica.** Decidir exige também a permissão sistêmica de julgar
    recurso, e o sistema não sabe quem a possui: os papéis vêm da sessão, e não há registro que
    ligue identidade a papel. Afirmar que a decisão é impossível seria afirmar o que os dados não
    sustentam — alguém de fora da comissão pode detê-la (`FR-030a`, `T-004`). Pela mesma razão o
    `UX-064` diz que **há** recurso esperando, e não quem deveria decidi-lo (`FR-564`). E não diz
    prazo: o domínio não modela prazo de resposta, e o sinal não o inventa.
    """
    if not (alcancadas[UX_005] or alcancadas[UX_064]):
        return
    membros = {membro.identity_subject for membro in comissao_selectors.membros(processo)}
    if not membros:
        # Sem comissão ativa não há "comissão inteira impedida": há ausência de comissão, que é
        # outra condição e não está no catálogo. **E não há `UX-064` tampouco**: "ao menos um
        # membro livre" é falso quando não há membro nenhum, e a partição continua exaustiva sem
        # precisar de um terceiro caso.
        return
    for edital in editais:
        # A fila é por Edital, e o estado dele também: um Edital encerrado não tem decisão a
        # retomar, mas continua tendo peça cuja comissão está impedida — que é fato do `UX-005`.
        deste = alcance_no_edital(alcancadas, edital)
        if not (deste[UX_005] or deste[UX_064]):
            continue
        # **Uma leitura, as duas fases**: `recursos_do_edital` já traz toda peça do Edital e
        # filtra em Python, de modo que pedir as duas situações não custa consulta a mais.
        linhas = [
            linha
            for linha in recursos_selectors.recursos_do_edital(edital)
            if linha["situacao"] in AGUARDANDO_DECISAO
        ]
        pendentes = [linha["recurso"] for linha in linhas]
        situacao = {linha["recurso"].id: linha["situacao"] for linha in linhas}
        impedidos = impedidos_por_recurso(pendentes)
        # O **mesmo** conjunto responde as duas perguntas, e é a razão de ele ser calculado aqui e
        # não dentro de cada desfecho.
        livres = {peca.id: membros - impedidos.get(peca.id, set()) for peca in pendentes}
        travadas = [peca for peca in pendentes if not livres[peca.id]]
        soltas = [peca for peca in pendentes if livres[peca.id]]
        if deste[UX_005] and travadas:
            fase = fase_das_pecas(situacao[peca.id] for peca in travadas)
            yield Sinal(
                especie=UX_005,
                edital=edital,
                alvo=rotulo_do_edital(edital),
                mensagem=(
                    f"Há recurso aguardando {fase} no Edital {rotulo_do_edital(edital)} para o "
                    f"qual todos os membros da comissão estão impedidos de julgar."
                ),
                destino=encaminhar(UX_005, edital),
            )
        if deste[UX_064] and soltas:
            fase = fase_das_pecas(situacao[peca.id] for peca in soltas)
            yield Sinal(
                especie=UX_064,
                edital=edital,
                alvo=rotulo_do_edital(edital),
                # A medida é **esperando sobre pendentes**: as travadas estão no denominador
                # porque também aguardam decisão, e retirá-las faria o número dizer que o Edital
                # tem menos recurso parado do que tem.
                medida=Medida(numerador=len(soltas), denominador=len(pendentes), unidade=RECURSO),
                mensagem=(
                    f"Há recurso aguardando {fase} no Edital {rotulo_do_edital(edital)} com "
                    f"membro da comissão desimpedido para decidi-lo."
                ),
                destino=encaminhar(UX_064, edital),
            )


# ---------------------------------------------------------------------------
# 8. Encaminhamento — do sinal ao lugar onde ele se resolve
# ---------------------------------------------------------------------------

# Os dois encaminhamentos que levam a **alterar conteúdo já publicado**. Num Processo em estado
# final o domínio recusa alteração dos seus Editais, e um Edital que não está publicado não admite
# Retificação: nos dois casos oferecer o caminho seria oferecer um beco — o mesmo que a `007`
# passou uma feature inteira tirando (`FR-036`).
ENCAMINHAMENTOS_QUE_ALTERAM_O_EDITAL = frozenset({UX_046})

# A permissão que **pratica** a Retificação. Ela não decide se o sinal aparece — a tela de destino
# é legível por quem alcança o Edital —, e sim se o caminho é oferecido: o catálogo de ações do
# Edital já pratica a mesma distinção, e oferecer um formulário cujo envio será recusado é o beco
# que ele existe para não oferecer.
PERMISSAO_DE_RETIFICAR = "retificacao:elaborar"

# Onde cada sinal se resolve: a tela **dona** daquele fato, e nunca uma segunda implementação dele
# (`FR-035`, `D-009`). O rótulo diz o que se vai encontrar lá, e não o que se vai fazer: a decisão
# de agir é de quem chega.
ROTULOS_DO_DESTINO = {
    UX_003: "Abrir a distribuição da Etapa",
    UX_004: "Abrir a ordenação do marco",
    # O rótulo do mesmo sinal quando o ato veio de sorteio: "ordenação" nomearia uma tela que
    # aquele ato não usa, e quem lesse esperaria encontrar um recálculo que não existe ali.
    (UX_004, "sorteio"): "Abrir o sorteio do marco",
    UX_005: "Abrir os recursos do Edital",
    UX_046: "Retificar o quadro de vagas do Edital",
    # As três da `038`. O rótulo diz **o que se vai encontrar**, e não o que se vai fazer: a
    # decisão de agir é de quem chega (`FR-035`). Nenhum deles nomeia pessoa (`FR-564`).
    UX_063: "Abrir a distribuição da Etapa",
    UX_064: "Abrir os recursos do Edital",
    UX_065: "Abrir a ocupação do marco",
    UX_066: "Abrir a divulgação do resultado",
}


def situacao_admite_retificacao(processo, edital):
    """Se **alguém** pode retificar este Edital agora — a situação, e não a permissão.

    Processo em estado final não admite alteração dos seus Editais, e Retificação incide sobre
    Edital **publicado**. Faltando qualquer das duas, ninguém pratica o ato, e o sinal que leva a
    ele é condição sem destino operacional: não pertence à Atenção (045, `FR-741`, `D-003`).

    **Separada da permissão de propósito.** As duas caíam no mesmo `None` de
    `admite_encaminhamento`, e a Atenção não distinguia *"este leitor não pratica o ato"* — que
    pede a condução, a quem pedir — de *"ninguém pratica o ato"* — que não pede nada, porque não
    há a quem pedir.
    """
    return processo.status not in PROCESSO_FINAL and edital.status == Edital.Status.PUBLICADO


def admite_encaminhamento(processo, especie, edital, ator):
    """Se a **situação** admite o ato para onde o sinal encaminharia, e se este ator o pratica.

    Não é autorização — quem recusa continua sendo a tela de destino (`FR-036`). É a mesma
    distinção que o catálogo de ações do Edital já pratica: prever a recusa é conveniência; decidir
    a autorização é da dona.
    """
    if especie not in ENCAMINHAMENTOS_QUE_ALTERAM_O_EDITAL:
        return True
    return situacao_admite_retificacao(processo, edital) and bool(
        ator and ator.can(PERMISSAO_DE_RETIFICAR)
    )


def destino_de(processo, especie, edital, referencia=None, *, ator=None, sorteio=False, ato=None):
    """A tela dona daquele sinal, ou `None` quando a situação não admite o encaminhamento."""
    if not admite_encaminhamento(processo, especie, edital, ator):
        return None
    caminhos = {
        UX_003: lambda: reverse("interface:distribuicao", args=[edital.id, referencia]),
        UX_004: lambda: reverse(
            "interface:sorteio" if sorteio else "interface:ordenacao",
            args=[edital.id, referencia],
        ),
        UX_005: lambda: reverse("interface:recursos", args=[edital.id]),
        UX_046: lambda: reverse("interface:retificar", args=[edital.id]),
        # **A mesma tela dona, e nunca uma segunda implementação do fato** (`FR-557`). O `UX-063`
        # leva à distribuição da Etapa, que é onde o trabalho está; o `UX-064` aos recursos do
        # Edital, exatamente como o `UX-005` — os dois falam de peças da mesma fila, e mandá-los a
        # telas diferentes faria a fronteira entre eles parecer maior do que é.
        UX_063: lambda: reverse("interface:distribuicao", args=[edital.id, referencia]),
        UX_064: lambda: reverse("interface:recursos", args=[edital.id]),
        # A ocupação é por **marco**, e mostra os recortes dele: a referência é o marco, e o
        # recorte que produziu o sinal está nomeado no alvo.
        UX_065: lambda: reverse("interface:ocupacao", args=[edital.id, referencia]),
        # **A rota da divulgação pende do ato, e não do marco** (`017`): é o ato que a autorização
        # qualifica, e é dele que a prévia é composta. Um marco de cotas tem três atos, e mandar o
        # sinal ao marco obrigaria quem chega a adivinhar qual deles publicar.
        UX_066: lambda: reverse(
            "interface:previa-de-publicacao", args=[edital.id, referencia, ato.id]
        ),
    }
    rotulo = ROTULOS_DO_DESTINO.get((especie, "sorteio") if sorteio else especie)
    return Destino(rotulo=rotulo or ROTULOS_DO_DESTINO[especie], url=caminhos[especie]())


def alcance(ator, processo):
    """Quais espécies este ator alcança — **uma decisão por espécie**, e não uma na porta.

    Menor privilégio levado até o elemento (`FR-004`, `T-008`). A supressão é silenciosa: anunciar
    que existe um sinal suprimido diria a quem não pode vê-lo que **há** algo para ver, que é
    vazamento por agregação.

    Escrever cada linha por extenso, mesmo quando coincide com a porta vizinha, é o ponto: o dia
    em que a tela dona mudar de porta, o lugar de mudar é este.
    """
    gere = pode_gerir_comissao(ator, processo) is not None
    return {
        UX_003: gere,
        UX_004: gere or bool(ator and ator.can("auditoria:consultar")),
        UX_005: bool(ator and ator.can(recursos_admitir.PERMISSAO)),
        # Mesma porta da supervisão: o sinal fala do conteúdo **publicado** do Edital, que é
        # legível por quem alcança o Processo. Quem pratica o ato é outra decisão, e ela é do
        # encaminhamento — não da visibilidade.
        UX_046: pode_supervisionar(ator, processo) is not None,
        # As três da `038` repetem a porta da espécie **vizinha**, e repeti-la por extenso é o
        # ponto: o dia em que a tela dona mudar de porta, o lugar de mudar é este.
        #
        # O `UX-063` leva à mesma tela do `UX-003`. O `UX-064` exige a mesma permissão do `UX-005`,
        # porque é a mesma fila de peças. O `UX-065` leva à ocupação, cuja consulta aceita as duas
        # bases que a ordenação aceita — é a porta do `UX-004`, e não uma mais estreita.
        UX_063: gere,
        UX_064: bool(ator and ator.can(recursos_admitir.PERMISSAO)),
        UX_065: gere or bool(ator and ator.can("auditoria:consultar")),
        # A divulgação tem porta própria — `resultado:publicar` —, e ela não decorre das outras: a
        # presidência que conduz o certame pode não ser quem divulga, na configuração segregada que
        # a `033` nomeou. Oferecer o sinal a quem não abre a tela seria o beco que a `FR-558`
        # recusa.
        UX_066: bool(ator and ator.can("resultado:publicar")),
    }


# As duas formas da linha de ausência (`045`, `UX-084`). A relativa é a variante da global, e não
# outra frase: quem lê as duas precisa reconhecer que falam da mesma coisa, com alcance diferente.
AUSENCIA_GLOBAL = "Nenhuma condição de atenção neste Processo."
AUSENCIA_RELATIVA = "Nenhuma condição de atenção entre as que você acompanha neste Processo."


def frase_de_ausencia(alcancadas):
    """A linha que a Atenção diz quando não tem sinal, ou `None` quando a região não aparece.

    **"Não encontrei no que consigo ver" não é "não existe"** (`045`, `FR-730`, `D-004`). A frase
    global era dita a quem alcança uma espécie e não vê as outras — a publicadora lia *"nenhuma
    condição neste Processo"* enquanto o gestor via quinze. Ela passa a ser de quem alcança o
    catálogo inteiro; e nenhum papel sozinho o alcança, de modo que é frase de quem acumula papéis.

    **Só o alcance entra, e é isso que fecha o vazamento** (`FR-731`). A escolha é tomada sobre
    permissões, antes de sinal algum ser montado: não há caminho de dado entre o que o leitor não
    alcança e a frase que ele lê, e por isso ela é a mesma havendo ou não o que ele não vê. Nem
    `alcance_no_edital` entra: o estado do Edital retira espécies do **Edital**, e não do leitor —
    quem alcança tudo, num Processo de Editais encerrados, leu tudo o que havia para ler.
    """
    if not any(alcancadas.values()):
        return None
    return AUSENCIA_GLOBAL if all(alcancadas.values()) else AUSENCIA_RELATIVA


# --- A região inteira ------------------------------------------------------------------------


def sinais(processo, ator, *, alcancadas=None):
    """Os sinais deste Processo, na ordem do catálogo — e nada além deles.

    A ordem é a de `ESPECIES`, e não uma de gravidade: as espécies são igualmente acionáveis, e
    ordená-las por severidade pediria um juízo que o domínio não determina (`D-002`).

    O sinal que o ator não alcança **não é montado** (`FR-004`): a detecção nem chega a rodar, o
    que é ao mesmo tempo a supressão silenciosa e a leitura mais barata.

    **Nenhum sinal lê o relógio desde a `045`**: o único que o lia era o `UX-002`, que comparava o
    `status` declarado com a posição no tempo. Por isso `agora` saiu da assinatura.
    """
    # `alcancadas` entra pronto quando quem chama já o leu. A página do Processo precisa saber,
    # **antes** de montar a região, se este ator alcança alguma espécie — e `pode_gerir_comissao`
    # consulta a comissão, de modo que recalculá-lo aqui custaria a mesma leitura duas vezes.
    if alcancadas is None:
        alcancadas = alcance(ator, processo)

    def encaminhar(especie, edital, referencia=None, *, sorteio=False, ato=None):
        return destino_de(
            processo, especie, edital, referencia, ator=ator, sorteio=sorteio, ato=ato
        )

    leitura = leitura_dos_editais(processo)
    publicados = [(edital, conteudo) for edital, conteudo in leitura if conteudo is not None]
    achados = []
    for edital, conteudo in publicados:
        # **As leituras partilhadas recebem o alcance inteiro, e não um `if` na chamada** (`038`).
        # Cada uma serve a duas espécies com uma consulta só, e decidir aqui qual delas o ator
        # alcança obrigaria a escolher entre ler duas vezes e suprimir demais. A supressão continua
        # sendo por sinal, dentro delas (`FR-004`).
        # **O estado do Edital entra aqui, e por espécie** (`038`): o que parou por ato não tem
        # trabalho a retomar, e as seis espécies anteriores não se movem.
        deste = alcance_no_edital(alcancadas, edital)
        achados += list(sinais_da_etapa(edital, conteudo, encaminhar, deste))
        achados += list(
            sinais_do_marco(edital, conteudo, versao_vigente_do_edital(edital), encaminhar, deste)
        )
        # **Onde ninguém pode retificar, o `UX-046` não é condição de Atenção** (045, `FR-741`):
        # Edital encerrado ou cancelado, ou Processo em estado final. O fato continua no conteúdo
        # publicado; o que sai é a pendência que nenhuma tela resolve.
        if deste[UX_046] and situacao_admite_retificacao(processo, edital):
            achados += list(acervo_sem_quadro(edital, conteudo, encaminhar))
    achados += list(
        sinais_do_recurso(processo, [edital for edital, _ in publicados], encaminhar, alcancadas)
    )
    # Espécie, depois **Edital**, depois alvo. O Edital entra no meio porque a leitura da região é
    # feita por Edital: ordenar só pelo nome do alvo intercalava dois Editais com Etapas homônimas
    # — "Análise documental" de um, depois a do outro —, e quem lê perdia a conta de onde estava.
    achados.sort(
        key=lambda sinal: (
            ESPECIES.index(sinal.especie),
            sinal.edital.year,
            sinal.edital.number,
            sinal.alvo,
        )
    )
    return tuple(achados)


__all__ = [
    "ENCAMINHAMENTOS_QUE_ALTERAM_O_EDITAL",
    "PERMISSAO_DE_RETIFICAR",
    "ESPECIES",
    "EDITAL_PAROU_POR_ATO",
    "ROTULOS_DO_DESTINO",
    "TRABALHO_PENDENTE",
    "alcance_no_edital",
    "AGUARDANDO_DECISAO",
    "fase_das_pecas",
    "UX_003",
    "UX_004",
    "UX_005",
    "UX_046",
    "UX_063",
    "UX_064",
    "UX_065",
    "UX_066",
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
    "descricao_do_evento",
    "editais_do_processo",
    "etapas_do_conteudo",
    "eventos_do_conteudo",
    "instantes_do_evento",
    "leitura_dos_editais",
    "listas_do_marco",
    "fase_do_evento",
    "marcos_do_edital",
    "periodo_do_edital",
    "pode_supervisionar",
    "admite_encaminhamento",
    "situacao_admite_retificacao",
    "INSCRICAO",
    "RECURSO",
    "RECORTE",
    "PLURAIS",
    "alcance",
    "AUSENCIA_GLOBAL",
    "AUSENCIA_RELATIVA",
    "frase_de_ausencia",
    "destino_de",
    "pulso",
    "serie_do_edital",
    "sorteado",
    "sinais",
    "submetidas_nas_ultimas_24h",
]
