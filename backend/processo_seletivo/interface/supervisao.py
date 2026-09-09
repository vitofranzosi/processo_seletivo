"""A supervisão do Processo: as formas de leitura e as derivações que as preenchem.

**Este módulo só lê.** Nenhum `save`, `create`, `update` ou `delete` nasce aqui, e a ausência é o
invariante da feature: a `022` é composição de leituras que sete apps já persistem, e a necessidade
de gravar estado é motivo para revisar a spec, não para escrever migration (`D-007`, `FR-007`).

Ele fica fora de `views.py` de propósito. Aqui vivem as derivações, e mantê-las separadas da
montagem de contexto é o que permite testá-las como domínio de leitura, sem requisição.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from processo_seletivo.comissoes.domain.autorizacao import pode_gerir_comissao
from processo_seletivo.comissoes.domain.etapas import conteudo_vigente
from processo_seletivo.inscricoes.domain.periodo import ABERTO, ENCERRADO, FUTURO
from processo_seletivo.shared.api.problems import DomainError

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


@dataclass(frozen=True)
class PontoDaSerie:
    dia: date
    quantidade: int


@dataclass(frozen=True)
class PulsoDoEdital:
    edital: object
    submetidas: int
    rascunhos: int
    periodo: PeriodoDeInscricoes | None
    # `SEM_CRONOGRAMA`, `SEM_PERIODO`, ou vazio quando há período declarado (`FR-022`).
    ausencia: str
    serie: tuple[PontoDaSerie, ...]
    proximos_marcos: tuple[Marco, ...]


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


__all__ = [
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
    "conteudo_ou_nada",
    "editais_do_processo",
    "etapas_do_conteudo",
    "eventos_do_conteudo",
    "leitura_dos_editais",
    "pode_supervisionar",
]
