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

import json
from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

from django.utils.dateparse import parse_datetime

from processo_seletivo.agendamento.domain import recusas
from processo_seletivo.agendamento.domain.horarios import (
    Banca,
    Configuracao,
    derivar,
    dia_por_extenso,
    horario_curto,
    periodo_por_extenso,
    zona,
)
from processo_seletivo.agendamento.domain.nomes import (
    AGENDADO,
    CANCELAMENTO,
    CONFIGURACAO_SALVA,
    INCLUSAO,
    PROTOCOLO,
    PUBLICACAO,
    REMARCACAO,
)
from processo_seletivo.agendamento.domain.preenchimento import Pessoa, chave_da_pessoa
from processo_seletivo.agendamento.models import (
    AgendaDaEtapa,
    Agendamento,
    AtoDaAgenda,
    HorarioPublicado,
)
from processo_seletivo.comissoes.domain.etapas import conteudo_vigente, evento_vigente
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.resultados.application import prontidao
from processo_seletivo.resultados.application.selectors import ha_resultado_em
from processo_seletivo.resultados.domain.progressao import etapas_anteriores

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


# --- o que foi publicado (entrega B) --------------------------------------------------------------

DOCUMENTOS = {
    PUBLICACAO: "Documento da publicação",
    REMARCACAO: "Documento da remarcação",
    INCLUSAO: "Documento da inclusão",
    CANCELAMENTO: "Documento do cancelamento",
}


def publicacao(agenda):
    """O ato de publicação da agenda, ou `None`. "Publicada" é existir esta linha (data-model)."""
    if agenda is None:
        return None
    return AtoDaAgenda.objects.filter(agenda=agenda, especie=PUBLICACAO).first()


def conteudo_do_ato(ato):
    """O conteúdo como foi publicado, dos bytes do ato — nunca recomposto."""
    return json.loads(bytes(ato.conteudo_publico).decode("utf-8"))


def _vigentes(consulta):
    """Os itens não substituídos e no horário (data-model, *Vigente*), com a marca "remarcado em".

    O não substituído é o que nenhuma linha aponta em `substitui` — um `LEFT JOIN` só, e não uma
    consulta por pessoa. "Remarcado em" é o instante do ato do vigente quando ele é remarcação
    (FR-7245): o que mudou foi o horário daquela pessoa, e só dela.
    """
    itens = list(
        consulta.filter(situacao=AGENDADO, substituicoes__isnull=True)
        .select_related("inscricao", "banca", "ato")
        .order_by("inicio", "banca__ordem", "inscricao__protocolo", "id")
    )
    for item in itens:
        item.remarcado_em = item.ato.praticado_em if item.ato.especie == REMARCACAO else None
    return itens


def vigentes_da_agenda(agenda):
    """A agenda vigente: o que a página pública e a gestão mostram depois da publicação (T-016)."""
    return _vigentes(HorarioPublicado.objects.filter(ato__agenda=agenda))


@dataclass
class HorarioDaInscricao:
    """O bloco "Seu horário" de uma Etapa com agenda, na área do candidato (T-017)."""

    etapa: str
    agenda: object
    vigente: object = None  # o `HorarioPublicado` vigente, quando a agenda está publicada
    periodo: tuple | None = None  # o período do Evento, quando ainda não está
    varias_bancas: bool = False

    @property
    def publicado(self):
        return self.vigente is not None

    @property
    def quando(self):
        """`Terça-feira, 24/11/2026` — o dia em destaque, na zona institucional."""
        return dia_por_extenso(self.vigente.inicio.astimezone(zona()).date())

    @property
    def hora(self):
        return f"{self.vigente.inicio.astimezone(zona()):%H:%M}"

    @property
    def periodo_por_extenso(self):
        return periodo_por_extenso(self.periodo) if self.periodo else ""

    @property
    def sala(self):
        """O endereço da sala, só quando é um endereço: o botão não leva a texto solto."""
        acesso = (self.vigente.banca.acesso or "").strip() if self.vigente else ""
        return acesso if acesso.startswith(("https://", "http://")) else ""


def horarios_da_inscricao(inscricao):
    """O horário de cada Etapa com agenda em que a inscrição está, em número fixo de consultas.

    **Publicada a agenda, o que vale é o publicado**: o vigente desta inscrição, com a banca da qual
    sai o endereço da sala — que só esta tela, da própria pessoa, mostra (FR-7229). **Antes**, só
    quem participa da Etapa lê "ainda não foi publicado", com o período do Evento; a agenda de uma
    Etapa em que a pessoa não está não lhe diz respeito.

    Uma consulta para as agendas, uma para as publicadas e uma para os vigentes desta inscrição;
    a agenda ainda não publicada custa a participação daquela Etapa, a mesma leitura da montagem.
    """
    agendas = list(
        AgendaDaEtapa.objects.filter(edital_id=inscricao.edital_id).order_by("criada_em", "id")
    )
    if not agendas:
        return []
    publicadas = {
        ato.agenda_id: ato
        for ato in AtoDaAgenda.objects.filter(agenda__in=agendas, especie=PUBLICACAO)
    }
    vigentes = {
        item.ato.agenda_id: item
        for item in _vigentes(
            HorarioPublicado.objects.filter(ato__agenda_id__in=publicadas, inscricao=inscricao)
        )
    }
    nao_publicadas = [agenda for agenda in agendas if agenda.id not in publicadas]
    conteudo = conteudo_vigente(inscricao.edital) if nao_publicadas or vigentes else {}
    etapas = {str(etapa.get("id")): etapa for etapa in conteudo.get("stages") or []}
    blocos = []
    for agenda in agendas:
        etapa = etapas.get(str(agenda.etapa_id)) or {}
        nome = etapa.get("name") or "Etapa"
        if agenda.id in publicadas:
            vigente = vigentes.get(agenda.id)
            if vigente is not None:
                # A banca se diz quando a agenda publicada tem mais de uma, como na página pública;
                # a contagem é a do ato, e não a da configuração de hoje.
                bancas = [b["nome"] for b in conteudo_do_ato(publicadas[agenda.id])["bancas"]]
                blocos.append(
                    HorarioDaInscricao(
                        etapa=nome,
                        agenda=agenda,
                        vigente=vigente,
                        varias_bancas=len(bancas) > 1 or vigente.banca_nome not in bancas,
                    )
                )
            continue
        if str(inscricao.id) in participacao(inscricao.edital, agenda.etapa_id).participantes:
            blocos.append(
                HorarioDaInscricao(
                    etapa=nome, agenda=agenda, periodo=periodo_da_etapa(inscricao.edital, etapa)
                )
            )
    return blocos


def agenda_e_publicacao(edital, etapa_id):
    """`(agenda, publicada)` numa consulta só, sem janelas nem bancas (179, research T-007).

    É o que a Mesa pergunta a cada abertura — a Etapa tem agenda? está publicada? —, e o orçamento
    de consulta dela não comporta as três leituras de `agenda_da_etapa`.
    """
    from django.db.models import Exists, OuterRef

    agenda = (
        AgendaDaEtapa.objects.filter(edital=edital, etapa_id=etapa_id)
        .annotate(
            publicada=Exists(
                AtoDaAgenda.objects.filter(agenda_id=OuterRef("pk"), especie=PUBLICACAO)
            )
        )
        .first()
    )
    return agenda, bool(agenda is not None and agenda.publicada)


# --- o horário de cada inscrição, para quem cruza a agenda com a distribuição (179) -------------

#: As duas fontes de um horário (179, FR-8201): o publicado vigente, e o da montagem antes dele.
PUBLICADO = "PUBLICADO"
MONTAGEM = "MONTAGEM"


@dataclass(frozen=True)
class HorarioMarcado:
    """Quando e onde uma inscrição é atendida numa Etapa, e de qual fonte isso vem (179, T-002)."""

    etapa_id: str
    inscricao_id: UUID
    inicio: object
    fim: object
    banca_id: UUID
    banca_nome: str
    fonte: str
    remarcado_em: object = None


def horarios_do_edital(edital, *, so_publicados=False):
    """`{(etapa_id, inscricao_id): HorarioMarcado}` de todas as agendas do Edital (179, T-002).

    **A Etapa vai na chave como texto.** Ela chega como `UUID` da rota e como texto do conteúdo
    publicado e das fixtures; comparar sem normalizar responderia "sem horário" em silêncio.

    **Uma fonte por agenda, nunca as duas.** Publicada a agenda, o que vale é o vigente, e o
    agendamento da montagem deixa de ser horário de alguém; antes, só ele existe. A Distribuição e o
    conflito leem as duas fontes; a Programação de quem avalia e o aviso, só a publicada
    (`so_publicados`), porque horário que ainda pode mudar não é compromisso de ninguém.

    **Quatro consultas, e nenhuma por pessoa**: as agendas, as publicações, os vigentes e os
    agendamentos. Esta função não sabe quem avalia: quem cruza é `avaliacoes`, que a chama
    (`agendamento` não importa `avaliacoes`, research T-001).
    """
    agendas = {
        agenda.id: agenda
        for agenda in AgendaDaEtapa.objects.filter(edital=edital).order_by("criada_em", "id")
    }
    if not agendas:
        return {}
    publicadas = set(
        AtoDaAgenda.objects.filter(agenda_id__in=agendas, especie=PUBLICACAO).values_list(
            "agenda_id", flat=True
        )
    )
    horarios = {}
    if publicadas:
        for item in _vigentes(HorarioPublicado.objects.filter(ato__agenda_id__in=publicadas)):
            etapa_id = str(agendas[item.ato.agenda_id].etapa_id)
            horarios[(etapa_id, item.inscricao_id)] = HorarioMarcado(
                etapa_id=etapa_id,
                inscricao_id=item.inscricao_id,
                inicio=item.inicio,
                fim=item.fim,
                banca_id=item.banca_id,
                banca_nome=item.banca_nome,
                fonte=PUBLICADO,
                remarcado_em=item.remarcado_em,
            )
    em_montagem = [agenda_id for agenda_id in agendas if agenda_id not in publicadas]
    if em_montagem and not so_publicados:
        for agendamento in (
            Agendamento.objects.filter(agenda_id__in=em_montagem)
            .select_related("banca")
            .order_by("inicio", "banca__ordem", "inscricao_id", "id")
        ):
            etapa_id = str(agendas[agendamento.agenda_id].etapa_id)
            horarios[(etapa_id, agendamento.inscricao_id)] = HorarioMarcado(
                etapa_id=etapa_id,
                inscricao_id=agendamento.inscricao_id,
                inicio=agendamento.inicio,
                fim=agendamento.fim,
                banca_id=agendamento.banca_id,
                banca_nome=agendamento.banca.nome,
                fonte=MONTAGEM,
            )
    return horarios


def agendas_publicadas_do_edital(edital_id):
    """As agendas publicadas do Edital, para a seção "Agendas" da seleção (T-016).

    O nome da Etapa e os dias saem dos bytes de cada publicação: a seção diz o que foi publicado, e
    uma Retificação que renomeasse a Etapa não reescreve o ato.
    """
    linhas = []
    for ato in AtoDaAgenda.objects.filter(edital_id=edital_id, especie=PUBLICACAO).order_by(
        "praticado_em", "id"
    ):
        conteudo = conteudo_do_ato(ato)
        dias = [date.fromisoformat(dia["dia"]) for dia in conteudo.get("dias") or []]
        linhas.append(
            {
                "ato": ato,
                "agenda_id": ato.agenda_id,
                "etapa": conteudo["cabecalho"].get("etapa", ""),
                "periodo": periodo_por_extenso((dias[0], dias[-1])) if dias else "",
            }
        )
    return linhas


def documentos_da_agenda(agenda):
    """Os documentos dos atos da agenda, em ordem — o da publicação primeiro (`D-012`, FR-7248).

    Só os atos com documento gravado: a página não recompõe o que faltasse. Aceita a agenda ou a
    identidade dela, porque a página pública só tem a identidade da rota.
    """
    agenda_id = getattr(agenda, "id", agenda)
    return [
        {"ato": item, "titulo": DOCUMENTOS.get(item.especie, "Documento")}
        for item in AtoDaAgenda.objects.filter(
            agenda_id=agenda_id, documento__isnull=False
        ).order_by("praticado_em", "id")
    ]


def agenda_publica(agenda_id, busca=""):
    """A página pública de uma agenda publicada, ou `None` (T-016, FR-7227, FR-7245).

    **Lê só o append-only**: o cabeçalho, dos bytes da publicação; a lista, dos horários publicados
    vigentes. Nunca o `Agendamento`, que é rascunho, nem a banca além do nome congelado — o endereço
    da sala não chega a esta função, e por isso não chega à página (FR-7226).

    **A busca é no servidor**, sem JavaScript: casa o protocolo inteiro ou o fim dele, e o nome sem
    acento e sem caixa só quando o nome é público (`D-009`). Na Etapa restrita por Modalidade,
    buscar pelo nome não acha ninguém — e não diz se a pessoa está na lista.
    """
    from processo_seletivo.shared.texto import dobrar

    ato = (
        AtoDaAgenda.objects.filter(agenda_id=agenda_id, especie=PUBLICACAO)
        .select_related("edital", "agenda")
        .first()
    )
    if ato is None:
        return None
    conteudo = conteudo_do_ato(ato)
    cabecalho = conteudo["cabecalho"]
    com_nome = cabecalho.get("identificacao") != PROTOCOLO
    vigentes = _vigentes(HorarioPublicado.objects.filter(ato__agenda_id=agenda_id))
    varias = len(conteudo.get("bancas") or []) > 1 or len({i.banca_nome for i in vigentes}) > 1
    termo = (busca or "").strip()
    alvo = dobrar(termo)

    def casa(item):
        if not termo:
            return True
        protocolo = (item.inscricao.protocolo or "").casefold()
        if protocolo == termo.casefold() or protocolo.endswith(termo.casefold()):
            return True
        return com_nome and alvo in dobrar(item.inscricao.nome or "")

    dias = {}
    achados = 0
    for item in vigentes:
        if not casa(item):
            continue
        achados += 1
        local = item.inicio.astimezone(zona())
        dias.setdefault(local.date(), []).append(
            {
                "hora": f"{local:%H:%M}",
                "banca": item.banca_nome if varias else "",
                "nome": (item.inscricao.nome or "") if com_nome else "",
                "protocolo": item.inscricao.protocolo or "",
                "remarcado_em": item.remarcado_em,
            }
        )
    # Os documentos dos atos, em ordem — o da publicação primeiro e intacto (`D-012`). Só os que têm
    # documento gravado; a página não recompõe o que faltasse.
    documentos = documentos_da_agenda(agenda_id)
    return {
        "ato": ato,
        "documentos": documentos,
        "edital": ato.edital,
        "cabecalho": cabecalho,
        "com_nome": com_nome,
        "busca": termo,
        "achados": achados,
        "dias": [
            {"dia": dia_por_extenso(dia), "horarios": horarios}
            for dia, horarios in sorted(dias.items())
        ],
        "remarcacoes": sum(1 for item in vigentes if item.remarcado_em),
    }


# --- a orientação (entrega D) ---------------------------------------------------------------------


@dataclass(frozen=True)
class EstadoDaAgenda:
    """O que a orientação precisa saber de uma agenda: publicada, e quem já tem horário nela."""

    publicada: bool
    #: As inscrições com `Agendamento`, só enquanto a agenda não está publicada; depois, vazio — o
    #: que vale é o publicado, e a orientação não o lê.
    agendados: frozenset = frozenset()


def estado_das_agendas(edital):
    """`{etapa_id: EstadoDaAgenda}` das agendas do Edital, em duas consultas no máximo (T-023).

    É o que o Centro e Minhas atividades leem para dizer "Montar a agenda" e "Publicar a agenda".
    **A participação não é lida aqui**: quem chama já tem a da Etapa, pelo panorama da distribuição,
    que é a mesma `participacao_detalhada` da montagem. Lê-la de novo custaria a partição inteira
    por Etapa, num Centro que tem orçamento de consultas por Edital.

    Uma consulta para as agendas, com "publicada" ao lado; a segunda, só se alguma não estiver
    publicada, para os agendamentos dela.
    """
    from django.db.models import Exists, OuterRef

    agendas = list(
        AgendaDaEtapa.objects.filter(edital=edital)
        .annotate(
            publicada=Exists(AtoDaAgenda.objects.filter(agenda=OuterRef("pk"), especie=PUBLICACAO))
        )
        .order_by("criada_em", "id")
        .values_list("id", "etapa_id", "publicada")
    )
    abertas = [identidade for identidade, _etapa, publicada in agendas if not publicada]
    agendados = {}
    if abertas:
        for agenda_id, inscricao_id in (
            Agendamento.objects.filter(agenda_id__in=abertas)
            .order_by("agenda_id", "inicio", "id")
            .values_list("agenda_id", "inscricao_id")
        ):
            agendados.setdefault(agenda_id, set()).add(str(inscricao_id))
    return {
        str(etapa_id): EstadoDaAgenda(
            publicada=publicada, agendados=frozenset(agendados.get(identidade, ()))
        )
        for identidade, etapa_id, publicada in agendas
    }


@dataclass(frozen=True)
class HorarioNaOcorrencia:
    """O horário publicado de uma pessoa, como a tela da Ocorrência o mostra (R-23, FR-7250)."""

    quando: str
    banca: str


def horarios_na_ocorrencia(edital, etapa_id, inscricao_ids):
    """`None` sem agenda publicada nesta Etapa; senão, `{inscricao_id: HorarioNaOcorrencia}`.

    **Só informação** (FR-7250): a ausência continua sendo a Ocorrência, e nada aqui decide quem
    pode tê-la. Quem não aparece no dicionário não tem horário vigente — nunca teve, ou teve o
    horário cancelado. Duas consultas, e nenhuma por pessoa: a agenda publicada e os vigentes das
    inscrições da página.
    """
    publicacao_ = (
        AtoDaAgenda.objects.filter(
            agenda__edital=edital, agenda__etapa_id=etapa_id, especie=PUBLICACAO
        )
        .order_by("praticado_em", "id")
        .first()
    )
    if publicacao_ is None:
        return None
    agenda_id = publicacao_.agenda_id
    # A banca se diz quando a agenda publicada tem mais de uma, como na página pública e na área do
    # candidato; a contagem é a do ato, e não a da configuração de hoje.
    varias = len(conteudo_do_ato(publicacao_).get("bancas") or []) > 1
    if not inscricao_ids:
        return {}
    vigentes = (
        HorarioPublicado.objects.filter(
            ato__agenda_id=agenda_id,
            inscricao_id__in=list(inscricao_ids),
            situacao=AGENDADO,
            substituicoes__isnull=True,
        )
        .order_by("inicio", "inscricao_id", "id")
        .values_list("inscricao_id", "inicio", "banca_nome")
    )
    return {
        str(inscricao_id): HorarioNaOcorrencia(horario_curto(inicio), banca_nome if varias else "")
        for inscricao_id, inicio, banca_nome in vigentes
    }
