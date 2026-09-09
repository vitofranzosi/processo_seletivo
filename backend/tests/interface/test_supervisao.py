"""A página da supervisão: o que ela apresenta, o que ela recusa apresentar, e para onde encaminha.

Os testes de derivação vivem em `tests/integration/supervisao/`; aqui ficam os que só existem no
canal — a região anunciada, o equivalente textual da série, e as proibições de apresentação.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.supervisao import rascunhar, submeter
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def url(processo):
    return reverse("interface:supervisao", args=[processo.id])


def abrir(client, processo, subject="maria", papeis=()):
    identificar(client, subject, list(papeis))
    resposta = client.get(url(processo))
    assert resposta.status_code == 200, resposta.content
    return resposta.content.decode()


def regiao(corpo, ancora):
    """O trecho de uma das duas regiões, delimitado pelo `<section>` que a anuncia.

    Procurar no documento inteiro faria uma asserção sobre o Pulso passar ou falhar por causa de
    algo escrito na Atenção — e as duas regiões existem justamente porque são coisas diferentes.
    """
    achado = re.search(rf'<section[^>]*aria-labelledby="{ancora}".*?</section>', corpo, re.DOTALL)
    assert achado is not None, f"a região {ancora} não foi anunciada como região"
    return achado.group(0)


def test_as_duas_regioes_sao_anunciadas_com_titulo_proprio(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`UX-006`: quem navega por marcos salta de uma para a outra sem varrer a página."""
    corpo = abrir(client, processo_a)

    assert 'id="pulso-titulo"' in corpo
    assert 'id="atencao-titulo"' in corpo


def test_nenhum_percentual_e_apresentado_sobre_inscricao(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-017` e `SC-005`: não há denominador normativo para inscrição.

    Um percentual de avanço aqui responderia "quanto falta" a uma pergunta que ninguém pode
    responder — não existe o número de inscrições que o Edital espera receber.
    """
    submeter(edital_a, 7)
    rascunhar(edital_a, 2)

    corpo = abrir(client, processo_a)

    assert "%" not in regiao(corpo, "pulso-titulo")


def test_o_pulso_nomeia_o_edital_de_cada_contagem(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-011`, `FR-020` e `UX-007`: nenhuma linha do Edital aparece sem dizer de qual Edital é."""
    submeter(edital_a, 3)
    submeter(edital_c, 1, seed=2)

    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert f"{edital_a.number}/{edital_a.year}" in pulso
    assert f"{edital_c.number}/{edital_c.year}" in pulso


def test_o_rascunho_usa_o_termo_que_a_tela_de_inscricoes_ja_usa(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`Princípio I`: dois termos para o mesmo conceito é o que a linguagem ubíqua recusa.

    A tela da `009` chama o rascunho de **em preenchimento**. Enquanto não houver decisão de
    vocabulário que valha para as duas telas, a supervisão adota o termo vigente — e não inventa
    um segundo.
    """
    rascunhar(edital_a, 2)

    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert "preenchimento" in pulso.lower()
