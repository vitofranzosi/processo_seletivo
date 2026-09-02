"""A porta da distribuição, e as recusas que a definem (FR-044, FR-067).

Distribuir é ato de quem **gere** a comissão — as duas bases que a 011 reconhece. Alocação não
abre esta tela: quem atua na Etapa executa o trabalho, não o organiza.

Toda recusa responde como recurso inexistente, pela convenção do projeto: a existência de uma
Etapa, de um Edital ou de um Processo não é enumerável por quem não os alcança.
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.models import Atribuicao
from tests.fixtures.comissao import alocar_em, inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]


@pytest.fixture
def tela(edital_a, etapa_a1):
    return reverse("interface:distribuicao", args=[edital_a.id, etapa_a1])


@pytest.fixture
def cenario(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    return inscrever(edital_a, 2)


def test_quem_gere_a_comissao_alcanca(client, seletor_ligado, tela, cenario):
    identificar(client, "carlos", ["gestor"])

    assert client.get(tela).status_code == 200


def test_a_presidencia_alcanca_pela_propria_presidencia(
    client, seletor_ligado, tela, cenario, comissao_de_a
):
    """A segunda base da 011: presidir este Processo basta, sem papel sistêmico (FR-067)."""
    identificar(client, "maria", [])

    assert client.get(tela).status_code == 200


def test_quem_apenas_atua_na_etapa_nao_distribui(client, seletor_ligado, tela, cenario):
    """João está alocado — ele executa o trabalho, e não o organiza."""
    identificar(client, "joao", [])

    assert client.get(tela).status_code == 404


def test_quem_nao_tem_vinculo_nenhum_recebe_inexistente(client, seletor_ligado, tela, cenario):
    identificar(client, "estranho", [])

    assert client.get(tela).status_code == 404


def test_etapa_de_outro_edital_nao_e_alcancavel(
    client, seletor_ligado, edital_a, edital_b, etapa_b1, cenario
):
    """Trocar o identificador na URL não atravessa a fronteira do Edital (FR-045)."""
    identificar(client, "carlos", ["gestor"])

    resposta = client.get(reverse("interface:distribuicao", args=[edital_a.id, etapa_b1]))

    assert resposta.status_code == 404


def test_escopo_institucional_divergente_e_inexistente(
    client, seletor_ligado, settings, tela, cenario
):
    identificar(client, "carlos", ["gestor"], escopo="outra-unidade")

    assert client.get(tela).status_code == 404


def test_a_distribuicao_por_post_tambem_e_recusada(client, seletor_ligado, tela, cenario):
    """A recusa é do servidor, e não da tela que esconde o botão."""
    identificar(client, "joao", [])

    resposta = client.post(tela, {"acao": "distribuir", "inscricao_id": [str(cenario[0].id)]})

    assert resposta.status_code == 404
    assert Atribuicao.objects.count() == 0
