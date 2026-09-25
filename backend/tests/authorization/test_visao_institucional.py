"""Quem alcança a visão institucional, e o que a recusa diz (040).

Três garantias, e a terceira é a que some sem ninguém notar: **quem não tem a capacidade não vê o
caminho**. As duas primeiras — a rota recusada e o escopo alheio invisível — quebram alto quando
regridem; a terceira volta a oferecer um destino que a autorização recusa, que foi o defeito `N-03`
da `038`.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface import identidade
from processo_seletivo.interface import visao_geral as visao
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

URL = reverse("interface:visao-geral")


@pytest.fixture(autouse=True)
def _seletor(seletor_ligado):
    """Sem o seletor de identidade, `/gestao/` devolve 503 antes de qualquer autorização."""


# ---------------------------------------------------------------------------
# A grafia — as duas pontas precisam concordar
# ---------------------------------------------------------------------------


def test_a_grafia_da_capacidade_e_a_mesma_nos_dois_lugares():
    """`identidade.py` escreve a permissão **literalmente**, e não a importa de quem a consome.

    A duplicação é deliberada — aquele módulo é a fronteira de identidade —, e é por isso que a
    concordância entre as duas pontas precisa de teste: nada no código as liga.
    """
    assert visao.CONSULTAR == "visao:consultar"
    assert visao.CONSULTAR in identidade.PAPEIS["gestor"][1]


def test_nenhum_outro_papel_recebe_a_capacidade():
    """Negar por padrão: quem não é Gestor não lê o panorama por caminho nenhum.

    Reusar `inscricao:consultar` ou `auditoria:consultar` concederia o panorama como efeito
    colateral de outro ato — é a recusa que a `031` já registrou ao criar `matricula:exportar`.
    """
    outros = {
        papel: permissoes
        for papel, (_, permissoes) in identidade.PAPEIS.items()
        if papel != "gestor"
    }

    assert not [papel for papel, p in outros.items() if visao.CONSULTAR in p]


# ---------------------------------------------------------------------------
# T-12 — a rota recusa, e a recusa é explicada
# ---------------------------------------------------------------------------


def test_t12_sem_a_capacidade_a_rota_devolve_403_explicado(client):
    identificar(client, "elias", ["elaborador"])

    resposta = client.get(URL)

    # **403, e não 404**: a recusa é sobre o ator, e escondê-la atrás de "não encontrado" faria a
    # tela mentir sobre por que não abre.
    assert resposta.status_code == 403, resposta.content
    corpo = resposta.content.decode()
    # E ela **nomeia o que falta e a quem pedir** (033, `FR-481`). *"A operação não é permitida"*
    # é verdade e não é acionável — quem lê não sabe o que pedir nem para quem.
    assert "consultar a visão institucional" in corpo
    assert "Peça a alguém com a permissão de" in corpo


def test_sem_identificacao_o_caminho_leva_a_identificar(client):
    resposta = client.get(URL)

    assert resposta.status_code == 302
    assert reverse("interface:identificar") in resposta["Location"]


def test_com_a_capacidade_a_rota_abre(client):
    identificar(client, "carlos", ["gestor"])

    assert client.get(URL).status_code == 200


# ---------------------------------------------------------------------------
# SC-211 — a outra metade: o caminho não é oferecido a quem não o abre
# ---------------------------------------------------------------------------


def _tem_caminho(corpo):
    return re.search(rf'href="{re.escape(URL)}"', corpo) is not None


def test_sc211_quem_nao_tem_a_capacidade_nao_ve_o_caminho(client):
    identificar(client, "elias", ["elaborador"])

    lista = client.get(reverse("interface:lista"))

    assert lista.status_code == 200
    assert not _tem_caminho(lista.content.decode())


def test_sc211_quem_tem_a_capacidade_ve_o_caminho(client):
    identificar(client, "carlos", ["gestor"])

    lista = client.get(reverse("interface:lista"))

    assert _tem_caminho(lista.content.decode())


# ---------------------------------------------------------------------------
# T-19 — o escopo institucional filtra, e não devolve 404
# ---------------------------------------------------------------------------


def test_t19_ator_de_outro_escopo_nao_ve_processo_algum_do_escopo_alheio(
    client, api_client, manager_headers
):
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.supervisao import rascunho_com_periodo

    edital = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "visao-escopo-alheio-0001"},
        {
            "institutionalCode": "PS-2026-041",
            "title": "Processo de outra unidade",
            "firstEdital": {"number": "42", "year": 2026, "title": "Edital alheio"},
        },
        draft=rascunho_com_periodo(7),
    )
    identificar(client, "carlos", ["gestor"], escopo="outra-unidade")

    resposta = client.get(URL)
    corpo = resposta.content.decode()

    # **Não é 404**: a página é listagem, e listagem de escopo alheio não existe — o ator vê o seu
    # escopo, sempre, porque o filtro é da consulta.
    assert resposta.status_code == 200
    # A asserção é sobre o **caminho até o objeto**, e não sobre o número do Edital: `"42"` casa
    # dentro da folha de estilo de `base.html`, que é prosa densa. Foi assim que a primeira versão
    # deste teste falhou por uma medida em pixels escrita num comentário de CSS.
    assert reverse("interface:detalhe", args=[edital.id]) not in corpo
    assert "Processo de outra unidade" not in corpo
