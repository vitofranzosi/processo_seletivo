"""A tela da Etapa: a prontidão sobrevive à paginação, e a ação existe.

Um filtro que se perde ao avançar a página é pior que um filtro ausente: quem tinha 27 impedidas
diante de si volta à população inteira sem entender por quê, e o trabalho de triagem recomeça.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.comissao import inscrever
from tests.fixtures.resultado import montar_etapa_de_leitura_unica
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def com_muitas(gestor, api_client, manager_headers):
    """Mais inscrições que o tamanho da página, para que a paginação exista de verdade."""
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1490, codigo="1490"
    )
    inscrever(cenario["edital"], 30, primeiro=1)
    return cenario


def organizacao(cenario, consulta=""):
    return (
        reverse("interface:distribuicao", args=[cenario["edital"].id, cenario["primeira"]])
        + consulta
    )


def test_a_paginacao_preserva_o_filtro_de_prontidao(client, seletor_ligado, com_muitas):
    identificar(client, "maria", ["gestor"])
    corpo = client.get(organizacao(com_muitas, "?prontidao=impedida")).content.decode()

    seguintes = re.findall(r'<a href="(\?pagina=[^"]*)">Próxima</a>', corpo)
    assert seguintes, "a paginação não apareceu"
    assert all("prontidao=impedida" in href for href in seguintes), seguintes


def test_a_segunda_pagina_filtrada_continua_filtrada(client, seletor_ligado, com_muitas):
    identificar(client, "maria", ["gestor"])
    resposta = client.get(organizacao(com_muitas, "?prontidao=impedida&pagina=2"))
    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    # 30 impedidas, 25 por página: a segunda tem exatamente cinco linhas de inscrição.
    assert corpo.count('name="inscricao_id"') == 5


def test_a_acao_de_consolidar_esta_na_tela(client, seletor_ligado, com_muitas):
    identificar(client, "maria", ["gestor"])
    corpo = client.get(organizacao(com_muitas)).content.decode()
    assert "Consolidar as selecionadas" in corpo
    assert (
        reverse(
            "interface:consolidar-resultados",
            args=[com_muitas["edital"].id, com_muitas["primeira"]],
        )
        in corpo
    )
