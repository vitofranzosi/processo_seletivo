"""O cenário da 179: uma Etapa com agenda e com comissão alocada a ela.

Sobre o Processo A e a segunda Etapa dele, como as suítes da `167`
(`tests/fixtures/agenda_da_etapa.py`): a primeira Etapa não tem Resultado, e por isso todas as
inscrições enviadas participam. A agenda tem `bancas` × `dias` com oito horários de 10 + 5 minutos
por banca e dia (08:00 a 10:00), preenchida pelo automático da `167` — por nome, horário do mais
cedo ao mais tarde, bancas lado a lado.

`atribuir` passa pelo comando da Distribuição, e não por `create`: a recusa por conflito mora
nele, e um cenário que gravasse Atribuição por fora testaria uma Distribuição que não existe.
"""

from processo_seletivo.agendamento.domain.horarios import Banca
from tests.fixtures.agenda_da_etapa import (
    DUAS_HORAS,
    SEG,
    TER,
    configuracao,
    montar_completa,
    publicar_agenda,
)
from tests.fixtures.comissao import alocar_em, constituir, inscrever

DIAS = (SEG, TER)


def bancas(quantas, *, forma="REMOTA"):
    return tuple(
        Banca(
            f"nova-{n}",
            f"Banca {n:02d}",
            f"https://sala.exemplo/{n}" if forma == "REMOTA" else f"Sala {n}, bloco B",
            n,
        )
        for n in range(1, quantas + 1)
    )


def agenda(
    gestor,
    edital,
    etapa,
    *,
    quantas_bancas=1,
    dias=1,
    publicar=True,
    forma="REMOTA",
    janelas=DUAS_HORAS,
):
    """Configura, preenche e (por padrão) publica a agenda; devolve o ato ou `None`.

    `dias` é quantos dos dias da fixture (23 e 24/11), ou os próprios dias — a primeira Etapa do
    Processo A tem Evento em 01/09/2026, e a configuração recusa dia fora dele.
    """
    lista = DIAS[:dias] if isinstance(dias, int) else tuple(dias)
    config = configuracao(
        dias=tuple((dia, janelas) for dia in lista),
        bancas=bancas(quantas_bancas, forma=forma),
        forma=forma,
    )
    montar_completa(gestor, edital, etapa, config=config)
    return publicar_agenda(gestor, edital, etapa) if publicar else None


def comissao(gestor, edital, etapa, subjects, *, prefixo="comissao-179", com_presidencia=True):
    """Constitui os membros e os aloca à Etapa; devolve `{subject: membro}`.

    A alocação recusa comissão sem presidência; por isso, na primeira chamada, a presidência
    (`presidencia-179`, que não é alocada) entra antes.
    """
    from processo_seletivo.comissoes.models import Funcao, MembroComissao

    processo = edital.processo
    if (
        com_presidencia
        and not MembroComissao.objects.filter(
            processo=processo, funcao=Funcao.PRESIDENTE, ativo=True
        ).exists()
    ):
        constituir(gestor, processo, [("presidencia-179", "PRESIDENTE")], prefixo=f"{prefixo}-p")
    membros = constituir(gestor, processo, [(s, "MEMBRO") for s in subjects], prefixo=prefixo)
    for membro in membros.values():
        alocar_em(gestor, processo, membro, edital, etapa)
    return membros


def atribuir(gestor, edital, etapa, membros, inscricoes, *, chave):
    """Um lote da Distribuição: cada inscrição a cada membro. Devolve o resultado declarado."""
    from processo_seletivo.avaliacoes.application.distribuicao import distribuir

    return distribuir(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa,
        membro_ids=[m.id for m in membros],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste-179",
    )


def por_sessao(edital, etapa):
    """`{(dia, banca_nome): [inscricao, ...]}` do horário de cada inscrição, em ordem de início."""
    from processo_seletivo.agendamento.application.leitura import horarios_do_edital
    from processo_seletivo.agendamento.domain.horarios import zona
    from processo_seletivo.inscricoes.models import Inscricao

    sessoes = {}
    horarios = sorted(
        (h for (e, _), h in horarios_do_edital(edital).items() if e == etapa),
        key=lambda h: (h.inicio, h.banca_nome),
    )
    inscricoes = Inscricao.objects.in_bulk([h.inscricao_id for h in horarios])
    for h in horarios:
        chave = (h.inicio.astimezone(zona()).date(), h.banca_nome)
        sessoes.setdefault(chave, []).append(inscricoes[h.inscricao_id])
    return sessoes


__all__ = ["agenda", "atribuir", "bancas", "comissao", "inscrever", "por_sessao"]
