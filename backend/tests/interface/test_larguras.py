"""Duas larguras, porque são dois trabalhos — e nenhuma delas em pixel cravado.

Um limite só em `main` fazia três coisas ao mesmo tempo: medida de texto, largura de tabela e
largura de painel. Fazia as três mal, e ao mesmo tempo — media-se **84 caracteres por linha no
portal e 147 na gestão**, contra os 65 a 75 confortáveis, enquanto sobravam **412 px de tela** ao
lado de um PDF renderizado a 69% do tamanho.

O que estes testes prendem é a separação: `--pagina` para a estrutura, `--leitura` para o texto. Não
substituem olhar a tela — o que se pode conferir aqui é que a regra existe e que ninguém voltou a
cravar um limite em pixel.
"""

import re

import pytest
from django.urls import reverse

from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


def folha(cliente, url):
    corpo = cliente.get(url).content.decode()
    return corpo[corpo.index("<style>") : corpo.index("</style>")]


@pytest.fixture
def da_gestao(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return folha(client, reverse("interface:lista"))


@pytest.fixture
def do_portal(client):
    return folha(client, reverse("portal:vitrine"))


def test_as_duas_larguras_vivem_nos_tokens(da_gestao, do_portal):
    """Num lugar só, como as cores: é o que impede as duas bases de divergirem."""
    for css in (da_gestao, do_portal):
        assert "--leitura:" in css
        assert "--pagina:" in css


@pytest.mark.parametrize("base", ["gestao", "portal"])
def test_a_pagina_serve_a_estrutura(base, da_gestao, do_portal):
    """`main` deixa de ser o limite do texto e passa a ser o limite da página."""
    css = da_gestao if base == "gestao" else do_portal

    assert re.search(r"main\{max-width:var\(--pagina\)", css), css[:0]
    assert not re.search(r"main\{max-width:\d+px", css)


@pytest.mark.parametrize("base", ["gestao", "portal"])
def test_o_texto_corrido_tem_medida_propria(base, da_gestao, do_portal):
    """Sem isto, alargar a página levaria as linhas de 147 para mais de 200 caracteres."""
    css = da_gestao if base == "gestao" else do_portal

    assert re.search(r"main>p[^{]*\{[^}]*max-width:var\(--leitura\)", css)


def test_o_que_se_escreve_acompanha_o_que_se_le(da_gestao):
    """O parecer de uma avaliação se esticava por 1.052 px, e ninguém redige assim."""
    assert re.search(r"\.campo>textarea[^{]*\{[^}]*max-width:var\(--leitura\)", da_gestao)


def test_a_vitrine_usa_a_tela_em_duas_colunas(do_portal):
    """Cinco seleções ocupavam 1,8 tela com 346 px vazios de cada lado."""
    assert re.search(r"\.selecoes\{[^}]*grid-template-columns:repeat\(auto-fill", do_portal)


def test_nenhuma_das_bases_crava_largura_em_pixel(da_gestao, do_portal):
    """`max-width` em pixel volta a ser um número decidindo por todas as telas."""
    for css in (da_gestao, do_portal):
        cravadas = re.findall(r"(?<!min-)max-width:(\d+)px", css)
        assert cravadas == [], cravadas


def test_o_painel_do_documento_respeita_o_atributo_hidden(da_gestao):
    """`display` de autor vence o `display:none` que o `hidden` traz do navegador.

    Sem a guarda, o painel aparecia vazio no alto de **toda** inscrição, com o botão de fechar,
    antes de qualquer documento ser aberto — e empurrava a avaliação para fora da primeira tela.
    """
    assert re.search(r"\.painel-documento:not\(\[hidden\]\)\{[^}]*display:flex", da_gestao)
    assert not re.search(r"\.painel-documento\{[^}]*display:flex", da_gestao)
