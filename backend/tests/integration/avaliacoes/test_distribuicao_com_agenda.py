"""O lote da Distribuição recusa a linha que põe alguém em dois lugares (179, FR-8205, FR-8206).

A recusa é regra sobre a linha, ao lado do impedimento (a FR-085 da `012`): a linha é nomeada, com o
outro compromisso, e o resto do lote é distribuído. Inscrição sem horário não passa pelo teste, e a
distribuição feita antes da agenda continua valendo.
"""

import pytest

from processo_seletivo.agendamento.application.leitura import horarios_do_edital
from processo_seletivo.avaliacoes.application import distribuicao
from processo_seletivo.avaliacoes.models import Atribuicao
from tests.fixtures.avaliacoes_com_agenda import agenda, atribuir, comissao, por_sessao
from tests.fixtures.comissao import inscrever

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def duas_bancas(gestor, edital_a, etapa_a2):
    inscrever(edital_a, 6)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana", "bruno"])
    sessoes = por_sessao(edital_a, etapa_a2)
    banca1, banca2 = sorted(sessoes)
    return membros, sessoes[banca1], sessoes[banca2]


def test_a_linha_em_conflito_e_recusada_e_o_resto_distribuido(
    gestor, edital_a, etapa_a2, duas_bancas
):
    membros, banca1, banca2 = duas_bancas
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1, chave="b1")
    # A primeira da Banca 02 é no mesmo horário que a primeira da Banca 01; Bruno está livre.
    resultado = atribuir(
        gestor, edital_a, etapa_a2, [membros["ana"], membros["bruno"]], banca2[:1], chave="b2"
    )
    assert resultado["feitas"] == 1
    assert resultado["recusadas"] == 1
    motivo = resultado["motivos"][0]["motivo"]
    assert motivo.startswith("ana já tem entrevista das 08:00 às 08:10 de 23/11, na Banca 01.")
    assert "Escolha outro avaliador para esta inscrição" in motivo
    assert not Atribuicao.objects.filter(membro=membros["ana"], inscricao=banca2[0]).exists()
    assert Atribuicao.objects.filter(membro=membros["bruno"], inscricao=banca2[0]).exists()


def test_duas_linhas_simultaneas_do_mesmo_lote_a_mais_tarde_e_recusada(
    gestor, edital_a, etapa_a2, duas_bancas
):
    membros, banca1, banca2 = duas_bancas
    # Mesmo horário nas duas bancas, num lote só, para a mesma pessoa.
    resultado = atribuir(
        gestor, edital_a, etapa_a2, [membros["ana"]], [banca2[0], banca1[0]], chave="lote"
    )
    assert resultado["feitas"] == 1 and resultado["recusadas"] == 1
    # A ordem é a da agenda (horário, banca): a da Banca 01 passa, a da Banca 02 é a recusada.
    assert Atribuicao.objects.filter(membro=membros["ana"], inscricao=banca1[0]).exists()
    assert resultado["motivos"][0]["inscricao"] == banca2[0].protocolo


def test_horarios_que_so_se_tocam_passam(gestor, edital_a, etapa_a2, duas_bancas):
    membros, banca1, _ = duas_bancas
    resultado = atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1, chave="seguidas")
    assert resultado["feitas"] == len(banca1) and resultado["recusadas"] == 0


def test_inscricao_sem_horario_nao_e_recusada_por_conflito(gestor, edital_a, etapa_a2):
    pessoas = inscrever(edital_a, 3)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana"])
    resultado = atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], pessoas, chave="sem")
    assert resultado["feitas"] == 3 and resultado["recusadas"] == 0
    assert horarios_do_edital(edital_a) == {}


def test_a_distribuicao_antes_da_agenda_continua_valendo(gestor, edital_a, etapa_a2):
    pessoas = inscrever(edital_a, 4)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana"])
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], pessoas, chave="antes")
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    assert Atribuicao.objects.filter(membro=membros["ana"], ativo=True).count() == 4


def test_antes_da_publicacao_vale_o_horario_da_montagem(gestor, edital_a, etapa_a2):
    inscrever(edital_a, 4)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2, publicar=False)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana"])
    banca1, banca2 = (v for _, v in sorted(por_sessao(edital_a, etapa_a2).items()))
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1[:1], chave="m1")
    resultado = atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca2[:1], chave="m2")
    assert resultado["recusadas"] == 1


def test_a_trilha_registra_so_as_criadas(gestor, edital_a, etapa_a2, duas_bancas):
    from processo_seletivo.auditoria.models import RegistroAuditoria

    membros, banca1, banca2 = duas_bancas
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1[:1], chave="t1")
    antes = RegistroAuditoria.objects.filter(operation=distribuicao.ATRIBUIR).count()
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca2[:1], chave="t2")
    assert RegistroAuditoria.objects.filter(operation=distribuicao.ATRIBUIR).count() == antes


def test_o_rodizio_com_agenda_nao_propoe_conflito(gestor, edital_a, etapa_a2, duas_bancas):
    membros, banca1, banca2 = duas_bancas
    proposta = distribuicao.propor_rodizio(
        actor=gestor,
        processo=edital_a.processo,
        edital_id=edital_a.id,
        etapa_id=etapa_a2,
        membro_ids=[membros["ana"].id, membros["bruno"].id],
    )
    resultado = distribuicao.confirmar_rodizio(
        actor=gestor,
        processo_id=edital_a.processo_id,
        edital_id=edital_a.id,
        etapa_id=etapa_a2,
        membro_ids=[membros["ana"].id, membros["bruno"].id],
        assinatura=proposta["assinatura"],
        idempotency_key="rodizio-179",
        correlation_id="teste",
    )
    assert resultado["feitas"] > 0
    from processo_seletivo.avaliacoes.application import programacao

    assert programacao.conflitos_da_etapa(edital_a, etapa_a2) == []


def test_entrevista_que_ja_acabou_nao_e_conflito(gestor, edital_a, etapa_a2, duas_bancas):
    """Revisão da 179: depois do dia, redistribuir não esbarra num conflito que só existiu antes."""
    from datetime import datetime, timedelta
    from unittest.mock import patch
    from zoneinfo import ZoneInfo

    membros, banca1, banca2 = duas_bancas
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1, chave="antes")
    depois = datetime(2026, 11, 24, 12, tzinfo=ZoneInfo("America/Sao_Paulo"))
    with patch("processo_seletivo.shared.application.commands.timezone") as relogio:
        relogio.now.return_value = depois
        resultado = atribuir(
            gestor, edital_a, etapa_a2, [membros["ana"]], banca2[:1], chave="depois"
        )
    assert resultado["feitas"] == 1 and resultado["recusadas"] == 0
    assert (
        depois - timedelta(days=1) > horarios_do_edital(edital_a)[(str(etapa_a2), banca2[0].id)].fim
    )


def test_a_recusa_diz_o_nome_e_nao_o_identificador_interno(gestor, edital_a, etapa_a2):
    """Revisão da 179: o membro institucional sem rótulo aparece pelo nome da pessoa (107)."""
    from django.contrib.auth import get_user_model

    inscrever(edital_a, 4)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    get_user_model().objects.create(username="pessoa-179-ana", first_name="Ana Lima")
    membros = comissao(gestor, edital_a, etapa_a2, ["pessoa-179-ana"])
    banca1, banca2 = (v for _, v in sorted(por_sessao(edital_a, etapa_a2).items()))
    atribuir(gestor, edital_a, etapa_a2, [membros["pessoa-179-ana"]], banca1[:1], chave="a")
    resultado = atribuir(
        gestor, edital_a, etapa_a2, [membros["pessoa-179-ana"]], banca2[:1], chave="b"
    )
    motivo = resultado["motivos"][0]["motivo"]
    assert motivo.startswith("Ana Lima já tem entrevista")
    assert "pessoa-179-ana" not in motivo
