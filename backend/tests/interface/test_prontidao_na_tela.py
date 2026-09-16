"""A tela da Etapa: a prontidão sobrevive à paginação, e a ação existe.

Um filtro que se perde ao avançar a página é pior que um filtro ausente: quem tinha 27 não
consolidáveis diante de si volta à população inteira sem entender por quê, e o trabalho de
triagem recomeça.
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
    corpo = client.get(organizacao(com_muitas, "?prontidao=nao-consolidavel")).content.decode()

    seguintes = re.findall(r'<a href="(\?pagina=[^"]*)">Próxima</a>', corpo)
    assert seguintes, "a paginação não apareceu"
    assert all("prontidao=nao-consolidavel" in href for href in seguintes), seguintes


def test_a_segunda_pagina_filtrada_continua_filtrada(client, seletor_ligado, com_muitas):
    identificar(client, "maria", ["gestor"])
    resposta = client.get(organizacao(com_muitas, "?prontidao=nao-consolidavel&pagina=2"))
    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    # 30 não consolidáveis, 25 por página: a segunda tem exatamente cinco linhas de inscrição.
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


def test_a_conferencia_declara_o_que_fica_de_fora(client, seletor_ligado, com_muitas):
    """Consolidar é irreversível, e a recusa por linha só se lia depois do ato (013, FR-018).

    Trinta inscrições sem avaliação nenhuma: a conferência não tem o que consolidar e diz por quê,
    linha a linha, em vez de oferecer o botão e recusar tudo depois do clique.
    """
    from processo_seletivo.inscricoes.models import Inscricao
    from processo_seletivo.resultados.models import ResultadoEtapa

    identificar(client, "maria", ["gestor"])
    inscricoes = list(Inscricao.objects.filter(edital=com_muitas["edital"])[:3])

    corpo = client.post(
        reverse(
            "interface:consolidar-resultados",
            args=[com_muitas["edital"].id, com_muitas["primeira"]],
        ),
        {"inscricao_id": [str(i.id) for i in inscricoes], "chave_idempotencia": "conferir-1490"},
    ).content.decode()

    assert "Confira antes de consolidar" in corpo
    assert "O que ficará de fora" in corpo
    for inscricao in inscricoes:
        assert (inscricao.protocolo or str(inscricao.id)) in corpo
    assert "Consolidar 3" not in corpo, "não se oferece o ato que recusaria tudo"
    assert ResultadoEtapa.objects.count() == 0
