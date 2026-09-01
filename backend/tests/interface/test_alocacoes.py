"""T038 — a organização por Edital, os dois estados vazios e as Etapas homônimas."""

import pytest
from django.urls import reverse

from tests.fixtures.comissao import alocar_em
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def url(processo):
    return reverse("interface:alocacoes", args=[processo.id])


def test_a_etapa_sem_membros_e_identificavel_sem_depender_de_cor(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """SC-014 e FR-076: a marca é texto."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a)).content.decode()

    assert "Sem membros alocados" in corpo
    assert "1 alocado" in corpo


def test_a_organizacao_nomeia_o_edital_antes_da_etapa(
    client, seletor_ligado, processo_a, edital_a, comissao_de_a
):
    """EC-012: dois Editais podem ter Etapas homônimas, e elas são objetos distintos."""
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a)).content.decode()

    assert f"Edital {edital_a.number}/{edital_a.year}" in corpo


def test_edital_nao_publicado_explica_por_que_nao_ha_o_que_alocar(
    client, seletor_ligado, api_client, manager_headers, processo_a, comissao_de_a
):
    """EC-014, o primeiro dos dois estados vazios."""
    api_client.post(
        f"/api/v1/admin/processos/{processo_a.id}/editais",
        {"number": "88", "year": 2026, "title": "Em elaboração"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "interface-edital-88-0001"},
    )
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a)).content.decode()

    assert "ainda não foi publicado" in corpo


def test_edital_publicado_sem_etapas_tem_estado_vazio_proprio(
    client, seletor_ligado, api_client, manager_headers, processo_a, comissao_de_a
):
    """EC-008, o segundo estado vazio — e ele não pode ser confundido com o primeiro."""
    from tests.fixtures.edital import complete_draft
    from tests.fixtures.publicacao import publish_original

    outro = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "interface-sem-etapas-0001"},
        {
            "institutionalCode": "PS-2026-777",
            "title": "Sem Etapas",
            "firstEdital": {"number": "77", "year": 2026, "title": "Sem Etapas"},
        },
        draft=complete_draft(2),
    )
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(outro.processo)).content.decode()

    assert "não declara Etapas de Avaliação" in corpo
    assert "ainda não foi publicado" not in corpo


def test_comissao_sem_presidente_nao_oferece_alocacao(client, seletor_ligado, gestor, processo_a):
    from tests.fixtures.comissao import constituir

    constituir(gestor, processo_a, [("joao", "MEMBRO")])
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a)).content.decode()

    assert "Nenhuma Etapa pode receber alocação" in corpo
    assert "Alocar nesta Etapa" not in corpo
