"""A folha comum da gestão em arquivo estático, sem mudar regra nenhuma (089).

Até a 089 a folha comum era o `<style>` do `interface/base.html`: 53 KB de regras em toda
resposta HTML da gestão, sem cache, e o obstáculo maior a uma política de segurança de conteúdo.
Ela saiu para `interface/static/interface/gestao.css`, e os tokens para
`shared/static/shared/tokens.css`.

A equivalência das regras — as mesmas, na mesma ordem — é provada uma vez, pelo script de
`doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/`, contra o modelo de antes. Aqui fica o
que tem de continuar verdade daqui em diante.
"""

import re
from pathlib import Path

import pytest
from django.contrib.staticfiles import finders
from django.template import Context, Template, TemplateSyntaxError
from django.urls import reverse

from processo_seletivo.shared import estaticos
from tests.interface.conftest import identificar
from tests.interface.folha import GESTAO_CSS, TOKENS_CSS, folha_aplicada

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo"
BASE = RAIZ / "interface/templates/interface/base.html"


def cabeca(corpo):
    corpo = corpo.decode() if isinstance(corpo, bytes) else corpo
    return corpo[: corpo.index("</head>")]


def ordem_das_folhas(corpo):
    """As folhas do `<head>`, na ordem: o caminho de cada `<link>`, e `<style>` para cada bloco."""
    return [
        achado.group(1).split("?")[0] if achado.group(1) else "<style>"
        for achado in re.finditer(r'<link rel="stylesheet" href="([^"]+)">|<style>', cabeca(corpo))
    ]


# ---- o endereço versionado (FR-2034, FR-2035) --------------------------------------------------


def renderizar(caminho):
    return Template("{% load estaticos %}{% estatico caminho %}").render(
        Context({"caminho": caminho})
    )


def test_os_dois_arquivos_sao_achados_pelos_finders():
    """`FR-2035`: o runserver e o guia de produção servem o que os *finders* acham. Os tokens moram
    em `shared/`, que não é app, e só são achados porque `STATICFILES_DIRS` os declara."""
    assert Path(finders.find("interface/gestao.css")) == GESTAO_CSS
    assert Path(finders.find("shared/tokens.css")) == TOKENS_CSS


def test_o_endereco_leva_o_resumo_do_conteudo():
    endereco = renderizar("interface/gestao.css")

    assert re.fullmatch(r"/static/interface/gestao\.css\?v=[0-9a-f]{12}", endereco), endereco
    assert renderizar("interface/gestao.css") == endereco


def test_com_debug_o_endereco_muda_quando_o_arquivo_muda(settings, tmp_path, monkeypatch):
    """`FR-2034`: no runserver, a folha editada ganha endereço novo na página seguinte, sem
    reiniciar — e o navegador não serve a velha do cache (a armadilha da `053`, com a
    `shell.js`)."""
    settings.DEBUG = True
    folha = tmp_path / "gestao.css"
    monkeypatch.setattr(estaticos.finders, "find", lambda caminho: str(folha))

    folha.write_text("a{color:red}")
    primeiro = renderizar("interface/gestao.css")
    folha.write_text("a{color:blue}")
    segundo = renderizar("interface/gestao.css")
    folha.write_text("a{color:red}")
    terceiro = renderizar("interface/gestao.css")

    assert primeiro != segundo
    assert terceiro == primeiro


def test_sem_debug_o_resumo_e_do_processo(settings, tmp_path, monkeypatch):
    """Fora do `DEBUG`, um cálculo por processo: a implantação reinicia o processo, e o endereço
    muda se, e só se, o arquivo mudou. Ler o arquivo a cada página seria custo sem ganho."""
    settings.DEBUG = False
    folha = tmp_path / "gestao.css"
    monkeypatch.setattr(estaticos.finders, "find", lambda caminho: str(folha))
    estaticos._resumo_do_processo.cache_clear()
    try:
        folha.write_text("a{color:red}")
        primeiro = renderizar("teste/sem-debug.css")
        folha.write_text("a{color:blue}")
        assert renderizar("teste/sem-debug.css") == primeiro
    finally:
        estaticos._resumo_do_processo.cache_clear()


def test_estatico_inexistente_e_erro_e_nao_link_quebrado():
    """Uma folha que não carrega deixa a página sem estilo, e ninguém vê o 404 do estático."""
    with pytest.raises(TemplateSyntaxError, match="estático inexistente"):
        renderizar("interface/nao-existe.css")


# ---- as quatro bases (FR-2031, FR-2032, SC-795) ------------------------------------------------


@pytest.mark.django_db
def test_a_gestao_carrega_tokens_folha_comum_e_so_entao_o_estilo_da_pagina(client, seletor_ligado):
    """`FR-2031`: a ordem do documento é a da cascata de antes — no mesmo `<style>`, os tokens,
    as regras comuns e o bloco da página, nessa ordem. Com a mesma especificidade, vence quem vem
    depois."""
    identificar(client, "carlos", ["gestor"])
    corpo = client.get(reverse("interface:lista")).content

    assert ordem_das_folhas(corpo) == [
        "/static/shared/tokens.css",
        "/static/interface/gestao.css",
        "<style>",
    ]
    # E o `<style>` que sobra é o da página: na lista, as duas regras da tela, e nada da comum.
    estilo = re.search(r"<style>(.*?)</style>", cabeca(corpo), re.S).group(1)
    assert ".tabela-rolavel" not in estilo and ":root" not in estilo


@pytest.mark.django_db
@pytest.mark.parametrize(
    "pagina",
    ["acesso da gestão", "vitrine do portal", "página de erro"],
)
def test_as_outras_bases_carregam_os_tokens_antes_de_qualquer_regra(client, seletor_ligado, pagina):
    """`FR-2032`: a página de acesso, o portal e a página de erro dividem os tokens com a gestão, e
    os carregam do mesmo arquivo, antes do estilo próprio."""
    caminho = {
        "acesso da gestão": reverse("interface:identificar"),
        "vitrine do portal": reverse("portal:vitrine"),
        "página de erro": "/selecoes/nao-existe",
    }[pagina]
    resposta = client.get(caminho)

    assert resposta.status_code == (404 if pagina == "página de erro" else 200)
    assert ordem_das_folhas(resposta.content) == ["/static/shared/tokens.css", "<style>"]
    assert "--verde:" in folha_aplicada(resposta.content)


def test_o_modelo_da_gestao_nao_tem_regra_da_folha_comum():
    """`SC-795`: de 1.471 linhas de estilo para nenhuma regra comum. No modelo resta o ponto de
    extensão do estilo por página, com o comentário que o explica."""
    modelo = BASE.read_text()
    estilo = re.search(r"<style>(.*?)</style>", modelo, re.S).group(1)
    sem_comentario = re.sub(r"\{% comment %\}.*?\{% endcomment %\}", "", estilo, flags=re.S)

    assert sem_comentario.strip() == "{% block estilo_da_pagina %}{% endblock %}"
    # Um `<style>` só no modelo; o comentário da `040` cita a palavra, e não conta.
    sem_prosa = re.sub(r"\{% comment %\}.*?\{% endcomment %\}", "", modelo, flags=re.S)
    assert sem_prosa.count("<style>") == 1


def test_os_tokens_tem_um_lugar_so():
    """`FR-2032`, D-001: o parcial de tokens saiu, e o arquivo estático é a fonte única. Duas cópias
    da paleta divergiriam na primeira mudança de cor — foi para impedir isso que ela se juntou."""
    assert not (RAIZ / "shared/templates/shared/_tokens.css.html").exists()
    declaram = [
        caminho.relative_to(RAIZ)
        for caminho in sorted(RAIZ.rglob("*"))
        if caminho.suffix in {".html", ".css"} and re.search(r"--verde\s*:", caminho.read_text())
    ]
    assert declaram == [Path("shared/static/shared/tokens.css")]
