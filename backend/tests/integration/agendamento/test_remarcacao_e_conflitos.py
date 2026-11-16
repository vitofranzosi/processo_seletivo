"""A remarcação confere, sob a trava, que os conflitos anunciados são os de agora (179, T-006).

Entre a tela e a confirmação, uma distribuição pode mudar quem fica em conflito no horário
escolhido. O comando recalcula depois da trava do Processo e recusa com `conflitos_mudaram`, sem
ato; sem mudança, a remarcação passa. A remarcação nunca é recusada só por haver conflito.
"""

import pytest
from django.utils import timezone

from processo_seletivo.agendamento.application import atos_individuais, leitura
from processo_seletivo.agendamento.domain.horarios import zona
from processo_seletivo.agendamento.domain.nomes import CONFLITOS_MUDARAM
from processo_seletivo.agendamento.models import AtoDaAgenda
from processo_seletivo.avaliacoes.application import programacao
from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.avaliacoes_com_agenda import agenda, atribuir, comissao, por_sessao
from tests.fixtures.comissao import inscrever

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def cenario(gestor, edital_a, etapa_a2):
    """Duas bancas; a Ana avalia as quatro da Banca 01 (08:00–08:45), o Bruno as da Banca 02. A
    última da Ana vai para as 09:00 da Banca 01: a Ana passa a ter entrevista às 09:00, e as 09:00
    da Banca 02 continuam livres."""
    inscrever(edital_a, 8)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana", "bruno"])
    banca1, banca2 = (v for _, v in sorted(por_sessao(edital_a, etapa_a2).items()))
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1, chave="ana")
    atribuir(gestor, edital_a, etapa_a2, [membros["bruno"]], banca2, chave="bruno")
    banca01, banca02 = _bancas(edital_a, etapa_a2)
    # Sem assinatura: o preparo do cenário não passa pela tela, e por isso não confere anúncio.
    _remarcar(
        gestor, edital_a, etapa_a2, banca1[3], _livre(edital_a, etapa_a2, banca01, 9), None, "9h"
    )
    return membros, banca1, banca2, banca02


def _bancas(edital, etapa):
    agenda_ = leitura.agenda_da_etapa(edital, etapa)
    return [str(b.id) for b in agenda_.bancas_em_ordem]


def _livre(edital, etapa, banca_id, hora):
    agenda_ = leitura.agenda_da_etapa(edital, etapa)
    return next(
        h
        for h in leitura.montagem(edital, etapa, agenda_).livres
        if h.banca_id == banca_id and h.inicio.astimezone(zona()).hour == hora
    )


def _remarcar(gestor, edital, etapa, pessoa, livre, assinatura, chave):
    return atos_individuais.remarcar(
        actor=gestor,
        edital=edital,
        etapa_id=etapa,
        inscricao_id=pessoa.id,
        inicio=livre.inicio,
        banca_id=livre.banca_id,
        motivo="falha de conexão",
        idempotency_key=chave,
        conflitos_no_horario=programacao.conflitos_no_horario,
        assinatura_dos_conflitos=assinatura,
    )


def test_a_distribuicao_entre_a_tela_e_a_confirmacao_e_recusada(
    gestor, edital_a, etapa_a2, cenario
):
    membros, _, banca2, banca02 = cenario
    pessoa = banca2[0]
    alvo = _livre(edital_a, etapa_a2, banca02, 9)
    # A tela: o Bruno, único avaliador da pessoa, está livre às 09:00.
    assinatura, anunciados = programacao.conflitos_no_horario(
        edital_a, etapa_a2, pessoa.id, alvo.inicio, alvo.fim
    )
    assert anunciados == []
    # Antes da confirmação, a Ana — que tem entrevista às 09:00 — passa a avaliar a pessoa também.
    Atribuicao.objects.create(
        membro=membros["ana"],
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao=pessoa,
        criado_em=timezone.now(),
        criado_por=gestor.subject,
    )
    antes = AtoDaAgenda.objects.count()
    with pytest.raises(DomainError) as recusa:
        _remarcar(gestor, edital_a, etapa_a2, pessoa, alvo, assinatura, "confirmar")
    assert recusa.value.code == CONFLITOS_MUDARAM
    assert recusa.value.status == 409
    assert AtoDaAgenda.objects.count() == antes


def test_sem_mudanca_a_remarcacao_passa(gestor, edital_a, etapa_a2, cenario):
    _, _, banca2, banca02 = cenario
    pessoa = banca2[0]
    alvo = _livre(edital_a, etapa_a2, banca02, 9)
    assinatura, _ = programacao.conflitos_no_horario(
        edital_a, etapa_a2, pessoa.id, alvo.inicio, alvo.fim
    )
    ato = _remarcar(gestor, edital_a, etapa_a2, pessoa, alvo, assinatura, "passa")
    assert ato.especie == "REMARCACAO"


def test_com_o_conflito_anunciado_a_remarcacao_acontece(gestor, edital_a, etapa_a2, cenario):
    """Q-A: haver conflito não impede; o que impede é ele não ter sido dito."""
    membros, _, banca2, banca02 = cenario
    pessoa = banca2[0]
    Atribuicao.objects.create(
        membro=membros["ana"],
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao=pessoa,
        criado_em=timezone.now(),
        criado_por=gestor.subject,
    )
    alvo = _livre(edital_a, etapa_a2, banca02, 9)
    assinatura, anunciados = programacao.conflitos_no_horario(
        edital_a, etapa_a2, pessoa.id, alvo.inicio, alvo.fim
    )
    assert [a.subject for a in anunciados] == ["ana"]
    ato = _remarcar(gestor, edital_a, etapa_a2, pessoa, alvo, assinatura, "anunciado")
    assert ato.especie == "REMARCACAO"
    assert programacao.conflitos_da_etapa(edital_a, etapa_a2)
