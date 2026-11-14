"""A presidência vê a deliberação antes de confirmar, e quantas esperam pareceres (165, UX-752).

O Edital de `tests/fixtures/deliberacao.py`: a Heteroidentificação colegiada, três pareceres.
"""

import pytest
from django.urls import reverse

from tests.fixtures.deliberacao import concluir_pareceres, distribuir_na_hetero, montar_colegiada
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

F, D = "FAVORAVEL", "DESFAVORAVEL"


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    cenario = montar_colegiada(gestor, api_client, manager_headers, seed=1671)
    maria, joana, _ = cenario["inscricoes"]
    distribuir_na_hetero(cenario, gestor, [maria, joana], chave="hetero-1671")
    concluir_pareceres(cenario, maria, {"ana": D, "bruno": D, "carla": F})
    concluir_pareceres(cenario, joana, {"ana": F})
    return cenario


def test_a_conferencia_mostra_a_deliberacao(client, seletor_ligado, cenario):
    """UX-752, FR-7067."""
    identificar(client, "maria", ["gestor"])
    maria = cenario["inscricoes"][0]
    url = reverse(
        "interface:consolidar-resultados", args=[cenario["edital"].id, cenario["hetero"]]
    )

    corpo = client.post(url, {"inscricao_id": [str(maria.id)]}).content.decode()

    assert "Indeferido — 2 de 3 pareceres Indeferido, por maioria" in corpo
    assert "a comissão deliberou Indeferido por maioria" in corpo


def test_a_organizacao_conta_quem_espera_pareceres(client, seletor_ligado, cenario):
    """FR-7079: dentro das não consolidáveis, as que só esperam pareceres."""
    identificar(client, "maria", ["gestor"])
    url = reverse("interface:distribuicao", args=[cenario["edital"].id, cenario["hetero"]])

    corpo = client.get(url).content.decode()

    # Joana tem um de três; a terceira inscrição, nenhum.
    assert "2 aguardando pareceres" in corpo
