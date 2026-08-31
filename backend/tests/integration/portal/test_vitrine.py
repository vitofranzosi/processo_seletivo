"""A porta: quem é de fora encontra a seleção sem passar pela gestão (US1, FR-012 a FR-014).

Os testes afirmam duas coisas de naturezas diferentes: que o que deve aparecer aparece, e que o
que é de dentro não vaza. A segunda é a que ninguém percebe quebrada — uma página pública com
nome de quem elaborou continua parecendo certa.
"""

import pytest
from django.urls import reverse

from tests.fixtures.selecao import publicar_selecao


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_vitrine_abre_sem_identificacao(client, api_client, manager_headers, process_payload):
    publicar_selecao(api_client, manager_headers, process_payload)

    resposta = client.get(reverse("portal:vitrine"))

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "Processo Seletivo 2026" in corpo
    assert "PS-2026-001" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_vitrine_leva_ao_detalhe_da_selecao(client, api_client, manager_headers, process_payload):
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:vitrine")).content.decode()

    assert reverse("portal:selecao", args=[edital.id]) in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_edital_nao_publicado_nao_aparece(client, api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)

    corpo = client.get(reverse("portal:vitrine")).content.decode()

    assert "Processo Seletivo 2026" not in corpo
    assert "Nenhuma seleção" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_vitrine_nao_expoe_dado_de_gestao(client, api_client, manager_headers, process_payload):
    """Quem elaborou, quem publicou e o estado interno do Edital são de dentro.

    Nenhum deles é segredo — a auditoria os publica a quem tem permissão. Mas a vitrine é uma
    página de oportunidade, e cada um deles ali é dado de gestão sem finalidade para quem lê.
    """
    publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:vitrine")).content.decode()

    for de_dentro in ("preparador", "homologador", "publicador", "PUBLICADO", "EM_ELABORACAO"):
        assert de_dentro not in corpo, f"{de_dentro} é dado de gestão e não pertence à vitrine"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_vitrine_e_cacheavel(client, api_client, manager_headers, process_payload):
    """Contraponto de FR-075a: a vitrine **não** carrega dado pessoal, e não é marcada como
    privada. Marcar tudo seria perder a distinção que a marcação existe para fazer."""
    publicar_selecao(api_client, manager_headers, process_payload)

    resposta = client.get(reverse("portal:vitrine"))

    assert "no-store" not in resposta.headers.get("Cache-Control", "")
