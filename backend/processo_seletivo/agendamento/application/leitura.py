"""O que a agenda lê: a agenda, a Etapa, o período, a participação e quem está em cada horário.

**A participação é a da prontidão** (`participacao_detalhada`, T-007, `D-002`), lida **uma vez por
requisição** e passada adiante: a montagem de 3 dias × 2 bancas × 32 horários lê os agendamentos
numa consulta e a participação noutra, e não por célula. A agenda não guarda lista própria.

**Quem tem horário e não participa mais aparece**, com o motivo (FR-7217): por isso esta leitura
não usa `restringir_a_participantes` sobre os agendamentos, que esconderia justamente essas pessoas.
O motivo vem da mesma partição de `participacao_detalhada` — eliminada antes, aguardando a anterior,
fora do corte, fora do alcance —, que é a fonte única da participação, em vez de uma frase genérica
para o conjunto: a comissão libera o horário de uma pessoa, e precisa saber o porquê daquela.

**Toda consulta tem `ORDER BY` completo**: a limpeza dos casos transacionais apaga por `DELETE`, e a
ordem física das linhas deixa de ser a de inserção (CLAUDE.md, *A limpeza depois de cada caso*).
"""

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

from django.utils.dateparse import parse_datetime

from processo_seletivo.agendamento.domain import recusas
from processo_seletivo.agendamento.domain.horarios import Banca, Configuracao, derivar, zona
from processo_seletivo.agendamento.domain.preenchimento import Pessoa, chave_da_pessoa
from processo_seletivo.agendamento.models import AgendaDaEtapa, Agendamento
from processo_seletivo.comissoes.domain.etapas import conteudo_vigente, evento_vigente
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.resultados.application import prontidao
from processo_seletivo.resultados.application.selectors import ha_resultado_em
from processo_seletivo.resultados.domain.progressao import etapas_anteriores

CONFIGURACAO_SALVA = "agenda.configuracao_salva"

# Os motivos de quem não participa, um por causa da partição (FR-7217).
ELIMINADA = "foi eliminada numa Etapa anterior"
AGUARDANDO = "aguarda o Resultado da Etapa anterior"
FORA_DO_CORTE = "ficou fora do corte que a norma publicada fixou para esta Etapa"
FORA_DO_ALCANCE = "a Modalidade da inscrição está fora do alcance desta Etapa"
NAO_ENVIADA = "a inscrição não está mais enviada"


def agenda_da_etapa(edital, etapa_id, *, travar=False):
    """A agenda, com as janelas e as bancas já em ordem, ou `None`."""
    consulta = AgendaDaEtapa.objects.filter(edital=edital, etapa_id=etapa_id)
    if travar:
        consulta = consulta.select_for_update()
    agenda = consulta.first()
    if agenda is None:
        return None
    # Duas consultas, e não `prefetch_related`: sob `select_for_update` o prefetch roda depois, e
    # é a mesma coisa — mas aqui a ordem é escrita, e não herdada do `Meta`.
    agenda.janelas_em_ordem = list(agenda.janelas.order_by("dia", "inicio", "id"))
    agenda.bancas_em_ordem = list(agenda.bancas.order_by("ordem", "id"))
    return agenda


def configuracao_da_agenda(agenda) -> Configuracao:
    dias = {}
    for janela in agenda.janelas_em_ordem:
        dias.setdefault(janela.dia, []).append((janela.inicio, janela.fim))
    return Configuracao(
        forma=agenda.forma,
        duracao=agenda.duracao_minutos,
        intervalo=agenda.intervalo_minutos,
        dias=tuple((dia, tuple(pares)) for dia, pares in sorted(dias.items())),
        bancas=tuple(
            Banca(str(banca.id), banca.nome, banca.acesso, banca.ordem)
            for banca in agenda.bancas_em_ordem
        ),
        orientacoes=agenda.orientacoes,
    )


def periodo_da_etapa(edital, etapa):
    """`(primeiro dia, último dia)` do Evento vigente da Etapa, em datas locais, ou `None`.

    O Evento é relido da Versão Consolidada a cada vez, e nunca copiado para a agenda (T-002): é
    retificável nas datas. Evento com início e sem fim é um dia só.
    """
    evento = evento_vigente(edital, (etapa or {}).get("scheduleEventId"))
    if not evento or not evento.get("startAt"):
        return None
    inicio = parse_datetime(evento["startAt"])
    fim = parse_datetime(evento["endAt"]) if evento.get("endAt") else inicio
    if inicio is None or fim is None:
        return None
    return (inicio.astimezone(zona()).date(), fim.astimezone(zona()).date())


@dataclass
class Participacao:
    """Quem participa hoje, e por que cada um dos outros não participa."""

    participantes: set
    motivos: dict = field(default_factory=dict)
    lista_aberta: bool = False

    def motivo(self, inscricao_id):
        return self.motivos.get(str(inscricao_id), NAO_ENVIADA)


def participacao(edital, etapa_id):
    """A participação da Etapa, de `participacao_detalhada`, e o fato "lista ainda aberta".

    **Lista aberta** é a Etapa anterior sem Resultado — o mesmo fato que faz a prontidão não aplicar
    ainda a exigência de habilitação (`_exige_habilitacao_da_anterior`), perguntado à mesma função
    (`ha_resultado_em`), e não uma segunda leitura (T011, US1 cenário 7).
    """
    conteudo = conteudo_vigente(edital)
    vigentes = {UUID(str(etapa["id"])): etapa for etapa in conteudo.get("stages") or []}
    participantes, eliminadas, aguardando, fora, _corte, alcance = prontidao.participacao_detalhada(
        edital=edital, etapa_id=etapa_id, vigentes=vigentes, conteudo=conteudo
    )
    motivos = {}
    for conjunto, motivo in (
        (eliminadas, ELIMINADA),
        (aguardando, AGUARDANDO),
        (fora, FORA_DO_CORTE),
        (alcance, FORA_DO_ALCANCE),
    ):
        motivos.update(dict.fromkeys((str(identidade) for identidade in conjunto), motivo))
    anteriores = etapas_anteriores(vigentes, etapa_id)
    aberta = bool(anteriores) and not ha_resultado_em(edital=edital, etapa_id=anteriores[0][0])
    return Participacao(
        participantes={str(identidade) for identidade in participantes},
        motivos=motivos,
        lista_aberta=aberta,
    )


def pessoas(inscricao_ids):
    """`{id: Pessoa}`, numa consulta."""
    if not inscricao_ids:
        return {}
    return {
        str(identidade): Pessoa(str(identidade), nome or protocolo or "", protocolo or "")
        for identidade, nome, protocolo in Inscricao.objects.filter(pk__in=list(inscricao_ids))
        .order_by("protocolo", "id")
        .values_list("id", "nome", "protocolo")
    }


def agendamentos(agenda):
    """Os agendamentos com a inscrição e a banca, do mais cedo ao mais tarde."""
    return list(
        Agendamento.objects.filter(agenda=agenda)
        .select_related("inscricao", "banca")
        .order_by("inicio", "banca__ordem", "id")
    )


def pessoa_do_agendamento(agendamento):
    inscricao = agendamento.inscricao
    return Pessoa(
        str(inscricao.id), inscricao.nome or inscricao.protocolo, inscricao.protocolo or ""
    )


@dataclass
class Montagem:
    """Tudo o que a tela de montar precisa, lido uma vez (T-007, Performance Goals)."""

    agenda: object
    configuracao: Configuracao
    horarios: tuple
    ocupados: dict  # chave do horário → agendamento
    por_inscricao: dict  # inscrição → agendamento
    sem_horario: list  # Pessoa, em ordem de nome
    nao_participam: list  # (agendamento, motivo)
    participacao: Participacao

    @property
    def livres(self):
        return [horario for horario in self.horarios if horario.chave not in self.ocupados]

    @property
    def participantes(self):
        return len(self.participacao.participantes)

    @property
    def com_horario(self):
        return self.participantes - len(self.sem_horario)

    @property
    def dias(self):
        return sorted({horario.dia for horario in self.horarios})

    def ocupados_no_dia(self, dia):
        return sum(1 for chave in self.ocupados if chave[1].astimezone(zona()).date() == dia)

    def horarios_no_dia(self, dia):
        return [horario for horario in self.horarios if horario.dia == dia]


def montagem(edital, etapa_id, agenda, *, participacao_=None):
    configuracao = configuracao_da_agenda(agenda)
    horarios = derivar(configuracao)
    participacao_ = participacao_ or participacao(edital, etapa_id)
    lista = agendamentos(agenda)
    ocupados = {(str(item.banca_id), item.inicio): item for item in lista}
    por_inscricao = {str(item.inscricao_id): item for item in lista}
    faltantes = participacao_.participantes - set(por_inscricao)
    sem_horario = sorted(pessoas(faltantes).values(), key=chave_da_pessoa)
    nao_participam = [
        (item, participacao_.motivo(item.inscricao_id))
        for item in lista
        if str(item.inscricao_id) not in participacao_.participantes
    ]
    return Montagem(
        agenda=agenda,
        configuracao=configuracao,
        horarios=horarios,
        ocupados=ocupados,
        por_inscricao=por_inscricao,
        sem_horario=sem_horario,
        nao_participam=nao_participam,
        participacao=participacao_,
    )


def devolvidos_pela_ultima_configuracao(agenda, montagem_):
    """A frase de quem voltou para "Sem horário" pela última configuração salva (US2, cenário 9).

    Lida da trilha, e não da sessão de quem salvou: outra pessoa da comissão que abre a montagem
    depois também precisa saber quem voltou e por quê. Só quem **continua** sem horário entra; quem
    já foi agendado de novo não precisa de aviso.
    """
    from processo_seletivo.auditoria.models import RegistroAuditoria

    registro = (
        RegistroAuditoria.objects.filter(operation=CONFIGURACAO_SALVA, aggregate_id=agenda.id)
        .order_by("-occurred_at", "-event_id")
        .values("occurred_at", "detalhe")
        .first()
    )
    if not registro or not (registro["detalhe"] or {}).get("devolvidos"):
        return ""
    # A trilha guarda o protocolo e a identidade, e não o nome (T-019); o nome vem da leitura que a
    # montagem já fez de quem está sem horário.
    sem_horario = {pessoa.inscricao_id: pessoa.nome for pessoa in montagem_.sem_horario}
    nomes = [
        sem_horario[item["inscricao"]]
        for item in registro["detalhe"]["devolvidos"]
        if item.get("inscricao") in sem_horario
    ]
    if not nomes:
        return ""
    return recusas.devolvidos_pela_configuracao(nomes, registro["occurred_at"].astimezone(zona()))


def dia_valido(texto, dias):
    """O dia pedido na aba (`?dia=`), se for um dos dias da agenda; senão, o primeiro."""
    try:
        pedido = date.fromisoformat(texto or "")
    except ValueError:
        pedido = None
    if pedido in dias:
        return pedido
    return dias[0] if dias else None
