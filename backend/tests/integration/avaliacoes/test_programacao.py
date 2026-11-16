"""A programação e a coerência, derivadas da Atribuição e do horário (179, FR-8200, FR-8202).

Nada é gravado: a programação de uma pessoa é o cruzamento de quem ela avalia com quando cada
inscrição é atendida. O conflito atravessa as Etapas do Edital, e a pessoa é o identificador.
"""

from datetime import date, timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.agendamento.application.leitura import horarios_do_edital
from processo_seletivo.avaliacoes.application import programacao
from processo_seletivo.avaliacoes.models import Atribuicao
from tests.fixtures.avaliacoes_com_agenda import agenda, atribuir, comissao, por_sessao
from tests.fixtures.comissao import inscrever

pytestmark = [pytest.mark.django_db]

DIA_DA_A1 = date(2026, 9, 1)
ANTES = timezone.make_aware(timezone.datetime(2026, 1, 1))


@pytest.fixture
def cenario(gestor, edital_a, etapa_a2):
    """Seis pessoas em duas bancas num dia (três horários cada), Ana e Bruno na comissão."""
    pessoas = inscrever(edital_a, 6)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana", "bruno"])
    return pessoas, membros


def test_a_programacao_tem_so_as_entrevistas_da_pessoa_em_ordem(
    gestor, edital_a, etapa_a2, cenario
):
    _, membros = cenario
    sessoes = por_sessao(edital_a, etapa_a2)
    (banca1, banca2) = sorted(sessoes)
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], sessoes[banca1], chave="b1")
    atribuir(gestor, edital_a, etapa_a2, [membros["bruno"]], sessoes[banca2], chave="b2")
    da_ana = Atribuicao.objects.filter(membro=membros["ana"]).select_related("inscricao")
    prog = programacao.programacao(da_ana, edital_a, etapa_a2, agora=ANTES)
    entrevistas = [e for d in prog.dias for e in d.entrevistas]
    assert {e.inscricao.id for e in entrevistas} == {i.id for i in sessoes[banca1]}
    assert [e.inicio for e in entrevistas] == sorted(e.inicio for e in entrevistas)
    assert {e.banca_nome for e in entrevistas} == {banca1[1]}
    assert all(e.sala.startswith("https://") for e in entrevistas)
    assert prog.sem_horario == []


def test_sem_publicacao_a_programacao_nao_tem_dias(gestor, edital_a, etapa_a2):
    inscrever(edital_a, 2)
    agenda(gestor, edital_a, etapa_a2, publicar=False)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana"])
    pessoas = list(por_sessao(edital_a, etapa_a2).values())[0]
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], pessoas, chave="antes")
    da_ana = Atribuicao.objects.filter(membro=membros["ana"]).select_related("inscricao")
    prog = programacao.programacao(da_ana, edital_a, etapa_a2, agora=ANTES)
    assert prog.dias == []
    assert len(prog.sem_horario) == 2


def test_o_conflito_e_por_pessoa_e_atravessa_etapas_do_edital(gestor, edital_a, etapa_a1, etapa_a2):
    pessoas = inscrever(edital_a, 2)
    agenda(gestor, edital_a, etapa_a2)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana"])
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], pessoas[:1], chave="a2")
    horarios = horarios_do_edital(edital_a)
    compromissos = programacao.compromissos(edital_a, horarios=horarios)
    assert list(compromissos) == ["ana"]
    assert len(compromissos["ana"]) == 1
    assert programacao.conflitos_da_etapa(edital_a, etapa_a2, horarios=horarios) == []


def test_a_coerencia_conta_quem_falta_e_o_conflito(gestor, edital_a, etapa_a2, cenario):
    pessoas, membros = cenario
    sessoes = por_sessao(edital_a, etapa_a2)
    (banca1, banca2) = sorted(sessoes)
    # Ana fica com as duas bancas: os três horários se repetem nas duas, e são três conflitos.
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], sessoes[banca1], chave="b1")
    _forcar_atribuicao(gestor, edital_a, etapa_a2, membros["ana"], sessoes[banca2])
    resultado = programacao.coerencia(edital_a, etapa_a2, previstas=2, agora=ANTES)
    assert resultado.com_horario == 6
    assert len(resultado.sem_avaliador_suficiente) == 6
    assert len(resultado.conflitos_vigentes) == 3
    assert not resultado.em_ordem
    frase = resultado.frase_do_conflito(resultado.conflitos[0])
    assert frase.startswith("ana, às ") and "Banca 01 e Banca 02" in frase


def test_conflito_passado_nao_e_vigente(gestor, edital_a, etapa_a2, cenario):
    _, membros = cenario
    sessoes = por_sessao(edital_a, etapa_a2)
    (banca1, banca2) = sorted(sessoes)
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], sessoes[banca1], chave="b1")
    _forcar_atribuicao(gestor, edital_a, etapa_a2, membros["ana"], sessoes[banca2])
    depois = timezone.make_aware(timezone.datetime(2027, 1, 1))
    resultado = programacao.coerencia(edital_a, etapa_a2, previstas=1, agora=depois)
    assert resultado.conflitos and resultado.conflitos_vigentes == []


def test_avaliadores_da_pessoa_anunciam_quem_ficaria_em_conflito(
    gestor, edital_a, etapa_a2, cenario
):
    _, membros = cenario
    sessoes = por_sessao(edital_a, etapa_a2)
    (banca1, banca2) = sorted(sessoes)
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], sessoes[banca1], chave="b1")
    _forcar_atribuicao(gestor, edital_a, etapa_a2, membros["ana"], sessoes[banca2][:1])
    horarios = horarios_do_edital(edital_a)
    movida = sessoes[banca2][0]
    da_pessoa = programacao.avaliadores_da_pessoa(edital_a, etapa_a2, movida.id)
    assert da_pessoa.nomes == ["ana"]
    # O horário da segunda pessoa da Banca 01 está ocupado por Ana.
    alvo = horarios[(str(etapa_a2), sessoes[banca1][1].id)]
    anunciados = da_pessoa.conflitos_em(alvo.inicio, alvo.fim)
    assert [a.subject for a in anunciados] == ["ana"]
    assert anunciados[0].outro.inscricao_id == sessoes[banca1][1].id
    # O próprio horário da pessoa movida não conta contra ela.
    proprio = horarios[(str(etapa_a2), movida.id)]
    assert [a.outro.inscricao_id for a in da_pessoa.conflitos_em(proprio.inicio, proprio.fim)] == [
        sessoes[banca1][0].id
    ]
    assinatura, lista = programacao.conflitos_no_horario(
        edital_a, etapa_a2, movida.id, alvo.inicio, alvo.fim
    )
    assert assinatura == programacao.assinatura_dos_conflitos(anunciados) and lista


def test_proximas_numa_consulta_e_ignora_as_passadas(gestor, edital_a, etapa_a2, cenario):
    _, membros = cenario
    sessoes = por_sessao(edital_a, etapa_a2)
    (banca1, _) = sorted(sessoes)
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], sessoes[banca1], chave="b1")
    horarios = horarios_do_edital(edital_a)
    primeiros = sorted(horarios[(str(etapa_a2), i.id)].inicio for i in sessoes[banca1])
    with CaptureQueriesContext(connection) as consultas:
        achadas = programacao.proximas("ana", agora=ANTES)
    assert len(consultas) == 1
    assert achadas[(edital_a.id, str(etapa_a2))][0] == primeiros[0]
    depois_da_primeira = programacao.proximas("ana", agora=primeiros[0] + timedelta(minutes=1))
    assert depois_da_primeira[(edital_a.id, str(etapa_a2))][0] == primeiros[1]
    assert programacao.proximas("bruno", agora=ANTES) == {}


def _forcar_atribuicao(gestor, edital, etapa, membro, inscricoes):
    """Grava Atribuição por fora do comando: só os testes da coerência precisam do conflito
    que a Distribuição, depois desta feature, não deixa nascer."""
    for inscricao in inscricoes:
        Atribuicao.objects.create(
            membro=membro,
            edital=edital,
            etapa_id=etapa,
            inscricao=inscricao,
            criado_em=timezone.now(),
            criado_por=gestor.subject,
        )
