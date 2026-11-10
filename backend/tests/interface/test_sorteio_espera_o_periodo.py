"""A tela do sorteio anuncia que a relação espera o fim das inscrições (021, US1).

A publicação da relação é recusada com o período correndo (`tests/integration/sorteios/
test_relacao_espera_o_periodo.py`). A tela oferecia o botão sem dizer nada, e a frase só apareceria
depois do clique — como a Mesa fazia com a distribuição, antes de passar a anunciá-la.
"""

import pytest
from django.urls import reverse

from tests.fixtures.sorteio import certame_de_sorteio
from tests.interface.conftest import identificar

# O botão de fixar desde a `142`: "Fixar os N participantes desta lista" (no GPS: publicar e
# congelar a relação). O rótulo antigo, procurado com `not in`, passaria calado.
BOTAO_DE_FIXAR = "participantes desta lista</button>"

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _abrir(client, certame):
    identificar(client, "maria", [])
    return client.get(
        reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]])
    ).content.decode()


def test_com_o_periodo_correndo_a_tela_diz_por_que_e_nao_oferece_o_botao(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, periodo_aberto=True
    )

    corpo = _abrir(client, certame)

    assert "Ainda não é possível publicar a relação." in corpo
    assert "deixaria fora do sorteio quem se inscrever depois" in corpo
    assert BOTAO_DE_FIXAR not in corpo
    assert (
        reverse(
            "interface:publicar-relacao-do-sorteio", args=[certame["edital"].id, certame["marco"]]
        )
        not in corpo
    )


def test_sem_periodo_correndo_o_botao_continua_e_o_aviso_nao_aparece(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    certame = certame_de_sorteio(gestor, api_client, manager_headers, process_payload)

    corpo = _abrir(client, certame)

    assert BOTAO_DE_FIXAR in corpo
    assert "Ainda não é possível publicar a relação." not in corpo
