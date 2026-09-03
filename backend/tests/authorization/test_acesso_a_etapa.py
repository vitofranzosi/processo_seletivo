"""T046, T047 e T053 — a demonstração de segurança da seção 49, pelo canal do ator.

É aqui que a 011 prova o que promete: autorização por objeto, e não por título genérico de
avaliador. Um percurso feliz sem estes 404 não demonstra nada.
"""

import pytest
from django.urls import reverse

from tests.fixtures.comissao import alocar_em
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]


@pytest.fixture
def joao_alocado_em_a1(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    return alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)


def url(edital, etapa_id):
    return reverse("interface:minha-etapa", args=[edital.id, etapa_id])


def test_a_etapa_alocada_abre(client, seletor_ligado, edital_a, etapa_a1, joao_alocado_em_a1):
    identificar(client, "joao", [])

    assert client.get(url(edital_a, etapa_a1)).status_code == 200


def test_a_etapa_vizinha_do_mesmo_edital_devolve_404(
    client, seletor_ligado, edital_a, etapa_a2, joao_alocado_em_a1
):
    """FR-055 e SC-010: alocação numa Etapa não alcança a outra, nem no mesmo Edital."""
    identificar(client, "joao", [])

    assert client.get(url(edital_a, etapa_a2)).status_code == 404


def test_a_etapa_de_outro_processo_devolve_404(
    client, seletor_ligado, edital_b, etapa_b1, joao_alocado_em_a1
):
    identificar(client, "joao", [])

    assert client.get(url(edital_b, etapa_b1)).status_code == 404


def test_uuid_adulterado_devolve_404(client, seletor_ligado, edital_a, joao_alocado_em_a1):
    """FR-057 e SC-009: conhecer o endereço não é autorização, e a recusa é sempre 404."""
    identificar(client, "joao", [])

    resposta = client.get(url(edital_a, "00000000-0000-0000-0000-000000000999"))

    assert resposta.status_code == 404


def test_escopo_alheio_devolve_404(client, seletor_ligado, edital_a, etapa_a1, joao_alocado_em_a1):
    identificar(client, "joao", [], escopo="outra-unidade")

    assert client.get(url(edital_a, etapa_a1)).status_code == 404


def test_privilegio_administrativo_nao_injeta_etapa_em_minhas_etapas(
    client, seletor_ligado, edital_a, joao_alocado_em_a1
):
    """FR-044 e SC-008: `Minhas Etapas` é estritamente por alocação, para qualquer papel."""
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(reverse("interface:minhas-etapas")).content.decode()

    assert "Você não possui Etapas atribuídas" in corpo


def test_remover_a_alocacao_revoga_o_acesso_na_hora(
    client, seletor_ligado, gestor, processo_a, edital_a, etapa_a1, joao_alocado_em_a1
):
    """US6: sem tocar em papel global nenhum."""
    from processo_seletivo.comissoes.application.alocacao import remover_alocacao

    identificar(client, "joao", [])
    assert client.get(url(edital_a, etapa_a1)).status_code == 200

    remover_alocacao(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_id=joao_alocado_em_a1.id,
        idempotency_key="k",
        correlation_id="c",
    )

    assert client.get(url(edital_a, etapa_a1)).status_code == 404
    corpo = client.get(reverse("interface:minhas-etapas")).content.decode()
    assert "Você não possui Etapas atribuídas" in corpo
