"""A folha comum da gestão em arquivo estático, sem mudar regra nenhuma (089).

Até a 089 a folha comum era o `<style>` do `interface/base.html`: 53 KB de regras em toda
resposta HTML da gestão, sem cache, e o obstáculo maior a uma política de segurança de conteúdo.
Ela saiu para `interface/static/interface/gestao.css`, e os tokens para
`shared/static/shared/tokens.css`. Na 091 a folha comum se dividiu por área, nos arquivos de
`FOLHAS_DA_GESTAO` (`interface/gestao/`), e o estilo de cada tela saiu para `interface/telas/` e
`interface/grupos/`.

A equivalência das regras é provada uma vez, pelos scripts do inventário (`depois-da-089/` e
`depois-da-091/`, em `doc/inventario-visual-da-gestao-2026-10-16/`), contra a folha de antes. Aqui
fica o que tem de continuar verdade daqui em diante.
"""

import re
from pathlib import Path

import pytest
from django.contrib.staticfiles import finders
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template
from django.urls import reverse

from processo_seletivo.shared import estaticos
from tests.interface.conftest import identificar
from tests.interface.folha import (
    ARQUIVOS_DA_FOLHA_COMUM,
    TOKENS,
    TOKENS_CSS,
    folha_aplicada,
    sem_comentarios,
)

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


def test_os_arquivos_sao_achados_pelos_finders():
    """`FR-2035`: o runserver e o guia de produção servem o que os *finders* acham. Os tokens moram
    em `shared/`, que não é app, e só são achados porque `STATICFILES_DIRS` os declara. Desde a 091
    a folha comum são os arquivos de `FOLHAS_DA_GESTAO`, e o `gestao.css` de um arquivo só saiu."""
    assert [Path(finders.find(c)) for c in estaticos.FOLHAS_DA_GESTAO] == ARQUIVOS_DA_FOLHA_COMUM
    assert Path(finders.find("shared/tokens.css")) == TOKENS_CSS
    assert finders.find("interface/gestao.css") is None


def test_o_endereco_leva_o_resumo_do_conteudo():
    endereco = renderizar("interface/gestao/base.css")

    assert re.fullmatch(r"/static/interface/gestao/base\.css\?v=[0-9a-f]{12}", endereco), endereco
    assert renderizar("interface/gestao/base.css") == endereco


def test_o_endereco_muda_quando_o_arquivo_muda(tmp_path, monkeypatch):
    """`FR-2034`: a folha editada ganha endereço novo na página seguinte, sem reiniciar o servidor —
    e o navegador não serve a velha do cache (a armadilha da `053`, com a `shell.js`). Desfeita a
    edição, o endereço volta: é o conteúdo que decide, e não a data."""
    folha = tmp_path / "gestao.css"
    monkeypatch.setattr(estaticos.finders, "find", lambda caminho: str(folha))

    folha.write_text("a{color:red}")
    primeiro = renderizar("interface/gestao/base.css")
    folha.write_text("a{color:blue}")
    segundo = renderizar("interface/gestao/base.css")
    folha.write_text("a{color:red}")
    terceiro = renderizar("interface/gestao/base.css")

    assert primeiro != segundo
    assert terceiro == primeiro


def test_a_folha_so_e_relida_quando_muda(tmp_path, monkeypatch):
    """O resumo fica memorizado pelo arquivo, pela data e pelo tamanho: as páginas pagam um `stat`,
    e não a leitura de 106 KB a cada pedido."""
    folha = tmp_path / "gestao.css"
    monkeypatch.setattr(estaticos.finders, "find", lambda caminho: str(folha))
    folha.write_text("a{color:red}")

    leituras = estaticos._resumo_do_arquivo.cache_info().misses
    renderizar("interface/gestao/base.css")
    renderizar("interface/gestao/base.css")
    assert estaticos._resumo_do_arquivo.cache_info().misses == leituras + 1

    folha.write_text("a{color:blue}")
    renderizar("interface/gestao/base.css")
    assert estaticos._resumo_do_arquivo.cache_info().misses == leituras + 2


def test_estatico_inexistente_e_erro_e_nao_link_quebrado():
    """Uma folha que não carrega deixa a página sem estilo, e ninguém vê o 404 do estático."""
    with pytest.raises(ImproperlyConfigured, match="estático inexistente"):
        renderizar("interface/nao-existe.css")


def test_a_verificacao_de_sistema_acusa_a_folha_que_falta(monkeypatch):
    """O `check` (e o `migrate` da implantação) recusa subir sem as folhas, em vez de cada página
    virar 500 — a de erro inclusive, que também carrega os tokens."""
    assert estaticos.verificar_folhas() == []

    monkeypatch.setattr(estaticos.finders, "find", lambda caminho: None)
    erros = estaticos.verificar_folhas()

    # As folhas das bases e, desde a 091, toda folha que um modelo cita pela tag.
    exigidas = dict.fromkeys(estaticos.FOLHAS) | estaticos.folhas_citadas()
    assert [erro.id for erro in erros] == ["estaticos.E001"] * len(exigidas)
    assert set(estaticos.FOLHAS) == {
        "shared/tokens.css",
        *estaticos.FOLHAS_DA_GESTAO,
        "shared/erro.css",
        "portal/portal.css",
    }
    assert "interface/telas/visao-geral.css" in exigidas


@pytest.mark.django_db
def test_a_gestao_carrega_tokens_folha_comum_e_so_entao_o_estilo_da_pagina(client, seletor_ligado):
    """`FR-2031`: a ordem do documento é a da cascata de antes — no mesmo `<style>`, os tokens,
    as regras comuns e o bloco da página, nessa ordem. Com a mesma especificidade, vence quem vem
    depois."""
    identificar(client, "carlos", ["gestor"])
    corpo = client.get(reverse("interface:lista")).content

    # Desde a 091 a folha comum são os arquivos de `FOLHAS_DA_GESTAO`, e o estilo da página é o
    # arquivo da tela, por último; nenhum `<style>`.
    assert ordem_das_folhas(corpo) == [
        "/static/shared/tokens.css",
        *(f"/static/{caminho}" for caminho in estaticos.FOLHAS_DA_GESTAO),
        "/static/interface/telas/lista.css",
    ]


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
    # O portal teve a folha no documento até a 092 (`FR-2130`); a página de acesso e a de erro, até
    # a 091.
    assert ordem_das_folhas(resposta.content) == [
        "/static/shared/tokens.css",
        {
            "acesso da gestão": "/static/interface/grupos/acesso.css",
            "vitrine do portal": "/static/portal/portal.css",
            "página de erro": "/static/shared/erro.css",
        }[pagina],
    ]
    assert "--verde:" in folha_aplicada(resposta.content)


def test_o_modelo_da_gestao_nao_tem_regra_da_folha_comum():
    """`SC-795`: de 1.471 linhas de estilo para nenhuma regra comum. No modelo resta o ponto de
    extensão do estilo por página, com o comentário que o explica — e, desde a 091, nem o `<style>`
    em volta dele: o bloco carrega `<link>`."""
    modelo = sem_comentarios(BASE.read_text())
    assert "{% block estilo_da_pagina %}{% endblock %}" in modelo
    assert "<style" not in modelo


def test_os_tokens_tem_um_lugar_so():
    """`FR-2032`, D-001: o parcial de tokens saiu, e o arquivo estático é a fonte única. Duas cópias
    da paleta divergiriam na primeira mudança de cor — foi para impedir isso que ela se juntou.

    Todos os nomes, e não um representante: uma tela que redeclarasse `--pagina` no próprio
    `<style>` devolveria as medidas a duas fontes, com a paleta intacta.
    """
    assert not (RAIZ / "shared/templates/shared/_tokens.css.html").exists()
    nomes = set(re.findall(r"(--[\w-]+)\s*:", sem_comentarios(TOKENS)))
    assert {"--verde", "--texto", "--leitura", "--pagina"} <= nomes

    redeclarados = {
        (str(caminho.relative_to(RAIZ)), nome)
        for caminho in sorted(RAIZ.rglob("*"))
        if caminho.suffix in {".html", ".css"} and caminho != TOKENS_CSS
        for nome in re.findall(r"(--[\w-]+)\s*:", sem_comentarios(caminho.read_text()))
        if nome in nomes
    }
    assert redeclarados == set(), sorted(redeclarados)


def test_a_folha_aplicada_le_o_link_escrito_de_qualquer_jeito():
    """O apoio dos guardiões lê toda folha do `<head>`, com os atributos em qualquer ordem: um
    padrão preso à grafia de hoje deixaria de fora a primeira folha escrita de outro jeito, e o
    guardião aprovaria uma regra que não leu."""
    cabeca_ = (
        "<head>"
        '<link href="/static/shared/tokens.css?v=1" rel="stylesheet">'
        "<link rel='stylesheet' media=\"print\" href='/static/interface/gestao/tabelas.css'>"
        '<link rel="icon" href="/favicon.ico">'
        '<style media="screen">.da-pagina{color:red}</style>'
        "</head><body><style>.do-corpo{}</style></body>"
    )
    folha = folha_aplicada(cabeca_)

    assert folha.index("--verde:") < folha.index(".tabela-rolavel{") < folha.index(".da-pagina{")
    assert ".do-corpo" not in folha
    assert "/*" not in folha.split(".da-pagina")[0]


# ---- o estilo de cada tela em arquivo (091) ----------------------------------------------------

MODELOS = RAIZ / "interface/templates/interface"

# Quem carrega cada arquivo de `telas/` e de `grupos/`. Escrito à mão, e não derivado dos modelos: é
# a afirmação que o teste confere — "o estilo de uma tela não viaja nas outras" (040, FR-2096).
QUEM_CARREGA = {
    "interface/grupos/acesso.css": {
        "base_de_acesso.html",
        "identificar.html",
        "identificar_demonstracao.html",
        "sem_autenticacao.html",
        # Quem entrou pelo provedor e não tem acesso vigente (107): a moldura da página de acesso.
        "sem_acesso.html",
    },
    "interface/grupos/assistente.css": {"assistente.html", "duvidas.html"},
    "interface/grupos/aviso.css": {"aviso.html", "aviso_previa.html", "modelo_de_aviso.html"},
    "interface/grupos/lista-exigida.css": {"inscricao_detalhe.html", "mesa_inscricao.html"},
    "interface/grupos/serie.css": {"processo_detalhe.html", "supervisao.html"},
    "interface/grupos/terminais.css": {
        "detalhe.html",
        "processo_detalhe.html",
        "retificacao_detalhe.html",
    },
    "interface/grupos/vista.css": {"compor_classificacao.html", "compor_perfis.html"},
    # O relatório consolidado (100): a escolha do conjunto e a camada executiva dividem a folha.
    "interface/telas/relatorio-consolidado.css": {
        "relatorio_consolidado.html",
        "relatorio_consolidado_escolha.html",
    },
    # A gestão de acessos (107): a lista, a busca e a confirmação dividem a folha.
    "interface/telas/acessos.css": {
        "acessos.html",
        "acessos_conceder.html",
        "acessos_confirmar.html",
        # A suspensão e a reativação, do incremento 2.
        "acessos_pessoas.html",
        "acessos_suspensao.html",
    },
    # O registro de Unidades (110): a lista, a ficha, o formulário, a conferência e a situação.
    "interface/telas/unidades.css": {
        "unidades.html",
        "unidades_ficha.html",
        "unidades_formulario.html",
        "unidades_conferencia.html",
        "unidades_situacao.html",
    },
    # A prévia da classificação (094): o painel só existe na etapa Classificação.
    "interface/telas/previa-da-classificacao.css": {"compor_classificacao.html"},
    **{
        f"interface/telas/{tela}.css": {f"{tela.replace('-', '_')}.html"}
        for tela in (
            "agenda",
            "alocacoes",
            "assistente",
            "comissao",
            "compor-anexos",
            "compor-conteudo",
            "compor-cronograma",
            "compor-revisao",
            "duvidas",
            "inscricao-detalhe",
            "lista",
            "marco",
            "minhas-etapas",
            "prototipo-do-assistente",
            "relatorio-do-edital",
            "retificar",
            "sorteio",
            # A trilha da unidade (108).
            "trilha-da-unidade",
            "visao-geral",
        )
    },
}


def test_cada_folha_de_tela_e_carregada_so_por_quem_a_usa():
    """`FR-2096`, `SC-815`: nenhum arquivo de tela viaja numa tela que não o usa, e nenhuma tela
    que tinha estilo deixa de carregá-lo. A base nunca cita arquivo de tela, que iria em todas."""
    citacoes = {}
    for modelo in sorted(MODELOS.glob("*.html")):
        for caminho in re.findall(
            r"""\{%\s*estatico\s+'(interface/(?:telas|grupos)/[^']+)'""", modelo.read_text()
        ):
            citacoes.setdefault(caminho, set()).add(modelo.name)

    assert citacoes == QUEM_CARREGA
    arquivos = {
        str(p.relative_to(RAIZ / "interface/static"))
        for p in (RAIZ / "interface/static/interface").glob("*/*.css")
        if p.parent.name in ("telas", "grupos")
    }
    assert arquivos == set(QUEM_CARREGA), "arquivo de tela que ninguém carrega, ou o contrário"
    assert "base.html" not in set().union(*QUEM_CARREGA.values())


def test_os_parciais_de_estilo_sairam():
    """`FR-2095`: os cinco parciais viraram arquivos de `grupos/`; o `include` não tem mais alvo."""
    assert list(MODELOS.glob("_estilo_*.html")) == []


@pytest.mark.django_db
def test_a_pagina_da_tela_carrega_o_grupo_antes_do_proprio(client, seletor_ligado):
    """`FR-2096`: na ordem de antes — o parcial vinha antes das regras próprias no bloco."""
    identificar(client, "carlos", ["gestor", "participante-piloto-assistente"])
    corpo = client.get(reverse("interface:visao-geral")).content
    folhas = ordem_das_folhas(corpo)

    assert folhas[: 1 + len(estaticos.FOLHAS_DA_GESTAO)] == [
        "/static/shared/tokens.css",
        *(f"/static/{c}" for c in estaticos.FOLHAS_DA_GESTAO),
    ]
    assert folhas[-1] == "/static/interface/telas/visao-geral.css"


def test_o_fragmento_do_prototipo_carrega_a_folha_dele():
    """`FR-2099`: no corpo da página pública, por `<link>`, e sem `<style>`."""
    modelo = sem_comentarios((MODELOS / "prototipo_do_assistente.html").read_text())

    assert "{% estatico 'interface/telas/prototipo-do-assistente.css' %}" in modelo
    assert "<style" not in modelo


def test_a_pagina_de_erro_carrega_a_folha_dela():
    """`FR-2100`: o estilo do `404.html` em `shared/erro.css`, como os tokens."""
    modelo = sem_comentarios((RAIZ / "shared/templates/404.html").read_text())

    assert "{% estatico 'shared/erro.css' %}" in modelo
    assert "<style" not in modelo
    assert finders.find("shared/erro.css")


def test_a_base_do_portal_carrega_a_folha_dele():
    """`FR-2130`, `FR-2133`, `FR-2134`: a folha do portal saiu do `<style>` do `base.html` na 092,
    para um arquivo achado pelos finders e conferido pela verificação de sistema."""
    modelo = sem_comentarios((RAIZ / "portal/templates/portal/base.html").read_text())

    assert "{% estatico 'portal/portal.css' %}" in modelo
    assert "<style" not in modelo
    assert finders.find("portal/portal.css")
    assert "portal/portal.css" in estaticos.FOLHAS
