"""Quem vê o quê na Programação (179, FR-8213, FR-8230, FR-8231, `D-006`).

Todas e somente as entrevistas da própria pessoa; a sala só a quem avalia aquela entrevista, na
resposta privada; sem alocação, a recusa de hoje.
"""

import pytest
from django.urls import reverse

from tests.fixtures.avaliacoes_com_agenda import agenda, atribuir, comissao, por_sessao
from tests.fixtures.comissao import inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def duas_bancas(gestor, edital_a, etapa_a2):
    inscrever(edital_a, 4)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana", "bruno"])
    banca1, banca2 = (v for _, v in sorted(por_sessao(edital_a, etapa_a2).items()))
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1, chave="ana")
    atribuir(gestor, edital_a, etapa_a2, [membros["bruno"]], banca2, chave="bruno")
    return banca1, banca2


def _mesa(edital, etapa):
    return reverse("interface:minha-etapa", args=[edital.id, etapa])


def test_bruno_nao_ve_a_entrevista_nem_a_sala_da_ana(
    client, seletor_ligado, edital_a, etapa_a2, duas_bancas
):
    banca1, banca2 = duas_bancas
    identificar(client, "bruno", [])
    corpo = client.get(_mesa(edital_a, etapa_a2)).content.decode()
    assert "https://sala.exemplo/2" in corpo
    assert "https://sala.exemplo/1" not in corpo
    assert all(p.protocolo not in corpo for p in banca1)


def test_a_resposta_e_privada(client, seletor_ligado, edital_a, etapa_a2, duas_bancas):
    identificar(client, "ana", [])
    resposta = client.get(_mesa(edital_a, etapa_a2))
    assert "no-store" in resposta["Cache-Control"]


def test_sem_alocacao_a_recusa_de_hoje(client, seletor_ligado, edital_a, etapa_a2, duas_bancas):
    identificar(client, "estranha", [])
    assert client.get(_mesa(edital_a, etapa_a2)).status_code == 404


def test_a_gestao_nao_tem_programacao_nem_sala(
    client, seletor_ligado, edital_a, etapa_a2, duas_bancas
):
    """Quem chega pela gestão organiza o trabalho e não o executa: não há Mesa, nem sala."""
    identificar(client, "carlos", ["gestor"])
    corpo = client.get(_mesa(edital_a, etapa_a2)).content.decode()
    assert "Entrar na sala" not in corpo and "sala.exemplo" not in corpo
