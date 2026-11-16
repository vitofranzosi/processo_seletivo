"""A programação de quem avalia, e a coerência entre a distribuição e a agenda (179).

**Derivada, e nunca gravada** (FR-8200, `D-001`). Quem avalia cada inscrição é a Atribuição;
quando e onde a inscrição é atendida é o horário da agenda. A programação de uma pessoa é o
cruzamento dos dois, e o conflito é o mesmo cruzamento visto de cima. Nenhuma composição de
banca, nenhuma lista de "quem está na Banca 01": a banca continua ponto de atendimento, como a
`167` decidiu.

**A pessoa é o identificador** (research T-003), e não a linha de `MembroComissao`: quem saiu da
comissão e voltou tem duas linhas e uma agenda só — o mesmo critério da conclusão única e do
impedimento da `012`.

**Este módulo lê a agenda; a agenda não o lê** (research T-001). `agendamento` não importa
`avaliacoes`. Onde um comando da agenda precisa saber de conflito — a remarcação —, a interface lhe
entrega `conflitos_no_horario` como função.

**Toda consulta tem `ORDER BY` completo**: a limpeza dos casos transacionais apaga por `DELETE`, e a
ordem física das linhas deixa de ser a de inserção (CLAUDE.md, *A limpeza depois de cada caso*).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from django.db.models import Exists, OuterRef
from django.utils import timezone

from processo_seletivo.agendamento.application.leitura import horarios_do_edital
from processo_seletivo.agendamento.domain.horarios import zona
from processo_seletivo.agendamento.domain.nomes import AGENDADO, REMARCACAO, REMOTA
from processo_seletivo.avaliacoes.domain.conflito import Compromisso, cabe, conflitos
from processo_seletivo.avaliacoes.models import Atribuicao


def rotulos(membros) -> dict:
    """`{subject: nome}` do que a gestão mostra de cada membro, numa consulta no máximo.

    O rótulo de exibição; sem ele, o nome da pessoa institucional, e nunca `pessoa-<uuid>` — a
    mesma tradução que o `rotulo_ou_nome` dos templates faz (107, SC-1020). As frases daqui saem em
    Python, e sem isto a recusa do lote e a marca da remarcação mostrariam o identificador interno.
    """
    from processo_seletivo.seguranca.application.acessos import nomes_dos_autores
    from processo_seletivo.seguranca.autenticacao import PREFIXO_DO_IDENTIFICADOR

    membros = list(membros)
    sem_rotulo = {
        m.identity_subject
        for m in membros
        if not (m.display_label or "").strip()
        and m.identity_subject.startswith(PREFIXO_DO_IDENTIFICADOR)
    }
    nomes = nomes_dos_autores(sem_rotulo) if sem_rotulo else {}
    return {
        m.identity_subject: (m.display_label or "").strip()
        or nomes.get(m.identity_subject, m.identity_subject)
        for m in membros
    }


def _compromisso(horario) -> Compromisso:
    return Compromisso(
        inicio=horario.inicio,
        fim=horario.fim,
        inscricao_id=horario.inscricao_id,
        etapa_id=horario.etapa_id,
        banca_nome=horario.banca_nome,
    )


def _atribuicoes_ativas(edital, *, subjects=None, etapa_id=None, so_membros_ativos=True):
    consulta = Atribuicao.objects.filter(edital=edital, ativo=True)
    if so_membros_ativos:
        consulta = consulta.filter(membro__ativo=True)
    if subjects is not None:
        consulta = consulta.filter(membro__identity_subject__in=list(subjects))
    if etapa_id is not None:
        consulta = consulta.filter(etapa_id=etapa_id)
    return consulta.select_related("membro").order_by(
        "membro__identity_subject", "etapa_id", "inscricao_id", "id"
    )


def compromissos(edital, *, subjects=None, horarios=None) -> dict:
    """`{subject: [Compromisso]}` das Atribuições ativas no Edital que têm horário.

    `horarios` é o de `horarios_do_edital`, quando quem chama já o leu; sem ele, é lido aqui.
    """
    horarios = horarios if horarios is not None else horarios_do_edital(edital)
    por_pessoa: dict[str, list[Compromisso]] = {}
    if not horarios:
        return por_pessoa
    # **Só as Atribuições que podem ter horário**: as das Etapas com agenda e das inscrições
    # marcadas nelas. Sem o recorte, cada abertura da Distribuição leria as Atribuições do Edital
    # inteiro — milhares, em três Etapas de dupla avaliação — para achar conflitos que só existem
    # entre entrevistas (revisão da 179).
    atribuicoes = _atribuicoes_ativas(edital, subjects=subjects).filter(
        etapa_id__in={e for (e, _) in horarios},
        inscricao_id__in={i for (_, i) in horarios},
    )
    for atribuicao in atribuicoes:
        horario = horarios.get((str(atribuicao.etapa_id), atribuicao.inscricao_id))
        if horario is None:
            continue
        por_pessoa.setdefault(atribuicao.membro.identity_subject, []).append(_compromisso(horario))
    return por_pessoa


def conflitos_da_etapa(edital, etapa_id, *, horarios=None, agora=None):
    """Os conflitos em que ao menos uma das entrevistas é desta Etapa (FR-8208)."""
    etapa = str(etapa_id)
    agora = agora or timezone.now()
    todos = conflitos(compromissos(edital, horarios=horarios), agora=agora)
    return [c for c in todos if etapa in {str(c.primeiro.etapa_id), str(c.segundo.etapa_id)}]


# --- a coerência de uma Etapa, para a gestão (FR-8208, FR-8215) -----------------------------------


@dataclass
class Coerencia:
    """O que a comissão precisa saber de uma Etapa com agenda: quem avalia, quem falta, o conflito.

    `avaliadores` é `{inscricao_id: [rotulo, ...]}`; é informação interna da gestão, e nunca chega
    ao que é público (`D-007`).
    """

    previstas: int
    avaliadores: dict = field(default_factory=dict)
    sem_avaliador_suficiente: list = field(default_factory=list)
    conflitos: list = field(default_factory=list)
    rotulos: dict = field(default_factory=dict)  # subject → rótulo
    com_horario: int = 0

    @property
    def conflitos_vigentes(self):
        return [c for c in self.conflitos if not c.passado]

    @property
    def em_ordem(self):
        return not self.sem_avaliador_suficiente and not self.conflitos_vigentes

    @property
    def frases_vigentes(self):
        """`[(frase, dia_iso)]` dos conflitos vigentes — o que a tela mostra e para onde leva."""
        return [
            (self.frase_do_conflito(c), c.segundo.inicio.astimezone(zona()).date().isoformat())
            for c in self.conflitos_vigentes
        ]

    def frase_do_conflito(self, conflito) -> str:
        quando = conflito.segundo.inicio.astimezone(zona())
        bancas = sorted({conflito.primeiro.banca_nome, conflito.segundo.banca_nome})
        return (
            f"{self.rotulos.get(conflito.pessoa, conflito.pessoa)}, às {quando:%H:%M} de "
            f"{quando:%d/%m} ({' e '.join(bancas)})"
        )


def coerencia(
    edital, etapa_id, *, previstas, horarios=None, agora=None, participantes=None
) -> Coerencia:
    """Quem avalia cada inscrição com horário, quem tem menos que o previsto, e os conflitos.

    Três consultas além do horário: as Atribuições da Etapa, as do Edital para o conflito — que
    atravessa Etapas —, e nenhuma por pessoa; uma a mais quando há membro institucional sem
    rótulo, para o nome.

    **A contagem é a da Distribuição**: toda Atribuição ativa, inclusive a de quem saiu da comissão,
    porque é para lá que o link leva, e as duas telas não podem contar diferente. `participantes`
    (identificadores em texto), quando vem, tira da pendência quem tem horário mas não participa
    mais: essa pessoa não se distribui, se cancela — e aparece na seção própria da agenda publicada.
    """
    horarios = horarios if horarios is not None else horarios_do_edital(edital)
    etapa = str(etapa_id)
    resultado = Coerencia(previstas=previstas)
    com_horario = [h for (e, _), h in horarios.items() if e == etapa]
    resultado.com_horario = len(com_horario)
    contagem: dict = {}
    da_etapa = list(_atribuicoes_ativas(edital, etapa_id=etapa_id, so_membros_ativos=False))
    membros = {a.membro.identity_subject: a.membro for a in da_etapa}
    resultado.rotulos.update(rotulos(membros.values()))
    for atribuicao in da_etapa:
        resultado.avaliadores.setdefault(atribuicao.inscricao_id, []).append(
            resultado.rotulos[atribuicao.membro.identity_subject]
        )
        contagem[atribuicao.inscricao_id] = contagem.get(atribuicao.inscricao_id, 0) + 1
    resultado.sem_avaliador_suficiente = [
        h.inscricao_id
        for h in sorted(com_horario, key=lambda h: (h.inicio, h.banca_nome, str(h.inscricao_id)))
        if contagem.get(h.inscricao_id, 0) < previstas
        and (participantes is None or str(h.inscricao_id) in participantes)
    ]
    resultado.conflitos = conflitos_da_etapa(edital, etapa_id, horarios=horarios, agora=agora)
    for c in resultado.conflitos:
        resultado.rotulos.setdefault(c.pessoa, c.pessoa)
    return resultado


# --- a remarcação: quem fica em conflito no horário escolhido (FR-8209, research T-006) -----------


@dataclass(frozen=True)
class ConflitoAnunciado:
    """Um avaliador da pessoa que ficaria com duas entrevistas no horário escolhido."""

    subject: str
    rotulo: str
    outro: Compromisso


def assinatura_dos_conflitos(anunciados) -> str:
    """O resumo do que a tela anuncia, para o comando conferir sob a trava (research T-006)."""
    texto = "|".join(
        sorted(
            f"{a.subject}:{a.outro.inscricao_id}:{a.outro.inicio.isoformat()}" for a in anunciados
        )
    )
    return hashlib.sha256(texto.encode()).hexdigest()[:16]


@dataclass
class AvaliadoresDaPessoa:
    """Quem avalia uma inscrição nesta Etapa, e os compromissos de cada um no Edital."""

    rotulos: dict  # subject → rótulo, na ordem do identificador
    compromissos: dict  # subject → [Compromisso]
    inscricao_id: object
    etapa_id: str

    @property
    def nomes(self):
        return list(self.rotulos.values())

    def conflitos_em(self, inicio, fim) -> list[ConflitoAnunciado]:
        """Quem ficaria em conflito se a pessoa fosse para `[inicio, fim)`."""
        anunciados = []
        for subject, rotulo_ in self.rotulos.items():
            outros = [
                c
                for c in self.compromissos.get(subject, [])
                if not (c.inscricao_id == self.inscricao_id and str(c.etapa_id) == self.etapa_id)
            ]
            impede = cabe(outros, inicio, fim)
            if impede is not None:
                anunciados.append(ConflitoAnunciado(subject, rotulo_, impede))
        return anunciados


def avaliadores_da_pessoa(edital, etapa_id, inscricao_id, *, horarios=None) -> AvaliadoresDaPessoa:
    atribuicoes = list(
        _atribuicoes_ativas(edital, etapa_id=etapa_id).filter(inscricao_id=inscricao_id)
    )
    nomes = rotulos(a.membro for a in atribuicoes)
    return AvaliadoresDaPessoa(
        rotulos=nomes,
        compromissos=compromissos(edital, subjects=nomes, horarios=horarios) if nomes else {},
        inscricao_id=inscricao_id,
        etapa_id=str(etapa_id),
    )


def conflitos_no_horario(edital, etapa_id, inscricao_id, inicio, fim):
    """`(assinatura, anunciados)` para a pessoa em `[inicio, fim)`: a função da remarcação.

    É chamada pelo comando **dentro** da transação, depois da trava do Processo: o que ela lê é o
    estado de agora, e não o da tela (research T-006).
    """
    anunciados = avaliadores_da_pessoa(edital, etapa_id, inscricao_id).conflitos_em(inicio, fim)
    return assinatura_dos_conflitos(anunciados), anunciados


# --- a programação de quem avalia (FR-8211, FR-8214) ----------------------------------------------


@dataclass
class Entrevista:
    """Uma linha da Programação: a Atribuição, o horário publicado e onde acontece."""

    atribuicao: object
    inscricao: object
    inicio: object
    fim: object
    banca_nome: str
    acesso: str
    remota: bool
    remarcado_em: object = None

    @property
    def sala(self):
        """O endereço da sala, só quando é endereço: o botão não leva a texto solto (`D-006`)."""
        acesso = (self.acesso or "").strip()
        return acesso if self.remota and acesso.startswith(("https://", "http://")) else ""

    @property
    def local(self):
        return "" if self.remota else (self.acesso or "").strip()


@dataclass
class DiaDaProgramacao:
    dia: object
    entrevistas: list
    hoje: bool = False
    passado: bool = False


@dataclass
class Programacao:
    dias: list
    sem_horario: list

    @property
    def total(self):
        return sum(len(d.entrevistas) for d in self.dias) + len(self.sem_horario)

    @property
    def futuros(self):
        return [d for d in self.dias if not d.passado]

    @property
    def passados(self):
        return [d for d in self.dias if d.passado]


def programacao(atribuicoes, edital, etapa_id, *, agora=None, agenda=None, publicada=None):
    """As entrevistas destas Atribuições, por dia e em ordem de início (FR-8211).

    `atribuicoes` é a consulta já autorizada da Mesa (a FR-020 da `012`): todas e somente as desta
    pessoa nesta Etapa. Só o horário **publicado** vale (FR-8201): o da montagem ainda pode mudar.
    Duas consultas além das Atribuições — os vigentes desta Etapa, com a banca —, e nenhuma por
    linha.
    """
    from processo_seletivo.agendamento.application.leitura import agenda_e_publicacao
    from processo_seletivo.agendamento.models import HorarioPublicado

    agora = agora or timezone.now()
    lista = list(atribuicoes)
    if publicada is None:
        agenda, publicada = agenda_e_publicacao(edital, etapa_id)
    vigentes = {}
    if publicada and lista:
        for item in (
            HorarioPublicado.objects.filter(
                ato__agenda=agenda,
                situacao=AGENDADO,
                substituicoes__isnull=True,
                inscricao_id__in=[a.inscricao_id for a in lista],
            )
            .select_related("banca", "ato")
            .order_by("inicio", "banca__ordem", "inscricao_id", "id")
        ):
            vigentes[item.inscricao_id] = item
    remota = agenda is not None and agenda.forma == REMOTA
    entrevistas, sem_horario = [], []
    for atribuicao in lista:
        item = vigentes.get(atribuicao.inscricao_id)
        if item is None:
            sem_horario.append(atribuicao)
            continue
        entrevistas.append(
            Entrevista(
                atribuicao=atribuicao,
                inscricao=atribuicao.inscricao,
                inicio=item.inicio,
                fim=item.fim,
                banca_nome=item.banca_nome,
                acesso=item.banca.acesso if item.banca_id else "",
                remota=remota,
                remarcado_em=item.ato.praticado_em if item.ato.especie == REMARCACAO else None,
            )
        )
    entrevistas.sort(key=lambda e: (e.inicio, e.banca_nome, e.inscricao.protocolo or ""))
    hoje = agora.astimezone(zona()).date()
    dias: dict = {}
    for entrevista in entrevistas:
        dias.setdefault(entrevista.inicio.astimezone(zona()).date(), []).append(entrevista)
    sem_horario.sort(key=lambda a: (a.inscricao.protocolo or "", str(a.inscricao_id)))
    return Programacao(
        dias=[
            DiaDaProgramacao(dia=dia, entrevistas=itens, hoje=dia == hoje, passado=dia < hoje)
            for dia, itens in sorted(dias.items())
        ],
        sem_horario=sem_horario,
    )


def proximas(subject, *, agora=None) -> dict:
    """`{(edital_id, etapa_id): (inicio, banca_nome)}` da próxima entrevista de cada Etapa.

    **Uma consulta, qualquer que seja o número de comissões** (research T-009): os vigentes futuros
    das inscrições que têm Atribuição ativa desta pessoa naquela Etapa, em ordem de início; a
    primeira de cada Etapa é a próxima. É o que mantém Minhas atividades no orçamento da `160`.
    """
    from processo_seletivo.agendamento.models import HorarioPublicado

    agora = agora or timezone.now()
    atribuida = Atribuicao.objects.filter(
        membro__identity_subject=subject,
        membro__ativo=True,
        ativo=True,
        inscricao_id=OuterRef("inscricao_id"),
        edital_id=OuterRef("ato__agenda__edital_id"),
        etapa_id=OuterRef("ato__agenda__etapa_id"),
    )
    linhas = (
        HorarioPublicado.objects.filter(
            situacao=AGENDADO, substituicoes__isnull=True, inicio__gte=agora
        )
        .filter(Exists(atribuida))
        .order_by("inicio", "banca_nome", "id")
        .values_list("ato__agenda__edital_id", "ato__agenda__etapa_id", "inicio", "banca_nome")
    )
    resultado = {}
    for edital_id, etapa_id, inicio, banca_nome in linhas:
        resultado.setdefault((edital_id, str(etapa_id)), (inicio, banca_nome))
    return resultado
