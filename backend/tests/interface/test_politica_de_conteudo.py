"""A política de segurança de conteúdo, e o que ela exige dos modelos e dos scripts (091).

O cabeçalho é conferido aqui por resposta; a prova de que nenhuma tela registra violação no
navegador é do inventário (`doc/inventario-visual-da-gestao-2026-10-16/depois-da-091/`), que lê o
evento `securitypolicyviolation` de cada variante. Os guardiões de embutido existem para a política
não virar surpresa: quem escreve o primeiro `<style>`, `style=""`, `onclick` ou script embutido num
modelo vê um teste reprovar antes de ver a tela sem desenho.
"""

import re
from pathlib import Path

import pytest
from django.http import HttpResponse, JsonResponse
from django.urls import reverse

from processo_seletivo.shared import politica_de_conteudo as politica
from tests.interface.conftest import identificar
from tests.interface.folha import ESTATICOS, sem_comentarios

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo"
MODELOS_DA_GESTAO = sorted(
    [*RAIZ.glob("interface/templates/**/*.html"), *RAIZ.glob("shared/templates/**/*.html")]
)
TODOS_OS_MODELOS = sorted(RAIZ.glob("*/templates/**/*.html"))
SCRIPTS = sorted(
    script for script in RAIZ.glob("*/static/**/*.js") if not script.name.endswith(".min.js")
)

RECUSA = "Content-Security-Policy"
OBSERVACAO = "Content-Security-Policy-Report-Only"


def _texto(modelo):
    """O modelo sem os comentários de modelo: eles citam `<style>` e `style=""` para explicar."""
    return re.sub(
        r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", "", modelo.read_text(), flags=re.S
    )


def _nome(caminho):
    return str(caminho.relative_to(RAIZ))


# ---- a política --------------------------------------------------------------------------------


def test_a_politica_so_permite_a_propria_origem_e_nada_embutido():
    """`FR-2103`: estilo e script só da própria origem, sem `unsafe-` de espécie nenhuma."""
    diretivas = dict(item.split(" ", 1) for item in politica.POLITICA.split("; "))

    assert diretivas["style-src"] == "'self'"
    assert diretivas["script-src"] == "'self'"
    assert diretivas["default-src"] == "'self'"
    assert diretivas["base-uri"] == "'self'" and diretivas["form-action"] == "'self'"
    assert "unsafe" not in politica.POLITICA
    # A moldura continua com o `X-Frame-Options` (`FR-2109`, D-010).
    assert "frame-ancestors" not in diretivas


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("caminho", "status"),
    [
        ("interface:lista", 200),
        ("interface:identificar", 200),
        ("interface:minhas-etapas", 200),
    ],
)
def test_toda_tela_da_gestao_recebe_a_politica_em_recusa(client, seletor_ligado, caminho, status):
    """`FR-2103`: as telas e a página de acesso da gestão, em recusa — e nunca em observação."""
    identificar(client, "carlos", ["gestor"])
    resposta = client.get(reverse(caminho))

    assert resposta.status_code == status
    assert resposta[RECUSA] == politica.POLITICA
    assert OBSERVACAO not in resposta
    # A moldura por outra origem continua recusada pelo cabeçalho de antes (`FR-2109`).
    assert resposta["X-Frame-Options"] == "DENY"


@pytest.mark.django_db
def test_o_fragmento_do_htmx_tambem_recebe_a_politica(client, seletor_ligado):
    """`FR-2103`: o fragmento entra numa página que já tem a política; o cabeçalho dele não muda o
    documento, mas a regra é uma só para todo HTML sob a gestão, e o fragmento aberto sozinho —
    num endereço colado — também fica sob ela."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.get(reverse("interface:fragmento-evento"), {"indice": "3"})

    assert resposta.status_code == 200
    assert resposta[RECUSA] == politica.POLITICA


@pytest.mark.django_db
def test_a_pagina_de_erro_sob_a_gestao_recebe_a_politica_em_recusa(client):
    """`FR-2103`: o `404.html` do sistema, servido sob a gestão, sem estilo embutido (`FR-2100`)."""
    resposta = client.get("/gestao/nao-existe")

    assert resposta.status_code == 404
    assert resposta[RECUSA] == politica.POLITICA
    assert "<style" not in resposta.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize("caminho", ["/selecoes/", "/selecoes/acesso", "/selecoes/nao-existe"])
def test_o_portal_recebe_a_politica_em_observacao(client, caminho):
    """`FR-2104`, D-007: o portal ainda tem a folha no documento; em recusa, ficaria sem desenho."""
    resposta = client.get(caminho)

    assert resposta[OBSERVACAO] == politica.POLITICA
    assert RECUSA not in resposta


@pytest.mark.django_db
def test_resposta_que_nao_e_html_nao_recebe_a_politica(client):
    """`FR-2105`: JSON, PDF e estático não são documento; a política não tem efeito neles."""
    resposta = client.get("/health")

    assert not resposta["Content-Type"].startswith("text/html")
    assert RECUSA not in resposta and OBSERVACAO not in resposta


@pytest.mark.parametrize(
    ("resposta", "esperado"),
    [
        (JsonResponse({"ok": True}), None),
        (HttpResponse(b"%PDF-1.7", content_type="application/pdf"), None),
        (HttpResponse("<p>x</p>"), RECUSA),
    ],
    ids=["json", "pdf", "html"],
)
def test_o_cabecalho_depende_do_tipo_da_resposta(resposta, esperado):
    assert politica.cabecalho_para("/gestao/x", resposta) == esperado


def test_resposta_que_ja_traz_politica_fica_como_esta():
    resposta = HttpResponse("<p>x</p>")
    resposta[RECUSA] = "default-src 'none'"

    assert politica.cabecalho_para("/gestao/x", resposta) is None


DEPURACAO = (
    '<!DOCTYPE html><html lang="en"><head><meta http-equiv="content-type" '
    'content="text/html; charset=utf-8"><meta name="robots" content="NONE,NOARCHIVE">'
    "<style>body{}</style></head><body></body></html>"
)


@pytest.mark.parametrize("status", [404, 500])
def test_a_pagina_de_depuracao_fica_fora_so_com_debug(settings, status):
    """`FR-2108`, D-010: a página do Django com `DEBUG` traz estilo e script embutidos. Sem `DEBUG`,
    o mesmo texto recebe a política — a exceção não vale em produção."""
    settings.DEBUG = True
    assert politica.cabecalho_para("/gestao/x", HttpResponse(DEPURACAO, status=status)) is None

    settings.DEBUG = False
    assert politica.cabecalho_para("/gestao/x", HttpResponse(DEPURACAO, status=status)) == RECUSA


def test_a_recusa_da_propria_gestao_recebe_a_politica_mesmo_com_debug(settings):
    """A gestão serve as próprias recusas com 404; com `DEBUG`, elas não viram página de depuração.
    Reconhecer a depuração pelo status as deixaria sem política no servidor local."""
    settings.DEBUG = True
    recusa = HttpResponse(
        "<!DOCTYPE html><html><head></head><body>Recurso</body></html>", status=404
    )

    assert politica.cabecalho_para("/gestao/recursos/x", recusa) == RECUSA


@pytest.mark.django_db
def test_com_debug_a_pagina_de_depuracao_do_django_sai_sem_politica(client, settings):
    """O caminho de verdade: endereço inexistente com `DEBUG` é a página técnica do Django."""
    settings.DEBUG = True
    resposta = client.get("/gestao/nao-existe")

    assert resposta.status_code == 404
    assert RECUSA not in resposta and OBSERVACAO not in resposta


def test_o_middleware_e_o_primeiro_da_lista(settings):
    """Na volta, ele é o último a tocar a resposta: as recusas montadas por middleware de dentro
    (`erros.py`) também levam a política."""
    assert settings.MIDDLEWARE[0].endswith("PoliticaDeConteudoMiddleware")


# ---- o que a política recusaria, e por isso não pode existir ----------------------------------


@pytest.mark.parametrize("modelo", MODELOS_DA_GESTAO, ids=_nome)
def test_nenhum_modelo_da_gestao_tem_estilo_embutido(modelo):
    """`FR-2097`, `FR-2101`, `SC-811`: nem `<style>`, nem atributo `style`."""
    texto = _texto(modelo)

    assert not re.search(r"<style\b", texto), "<style> no modelo"
    assert not re.search(r"\sstyle\s*=", texto), 'atributo style="" no modelo'


@pytest.mark.parametrize("modelo", TODOS_OS_MODELOS, ids=_nome)
def test_nenhum_modelo_tem_script_embutido_nem_atributo_de_evento(modelo):
    """`FR-2106`, D-008: script só de arquivo — no portal também, que entra em recusa depois."""
    texto = _texto(modelo)

    sem_src = [tag for tag in re.findall(r"<script\b[^>]*>", texto) if "src=" not in tag]
    assert sem_src == [], sem_src
    assert not re.search(r"""\son[a-z]+\s*=\s*["']""", texto), "atributo de evento"
    assert "javascript:" not in texto.lower()
    assert "hx-on" not in texto and "js:" not in texto.replace("js:{...}", "")


@pytest.mark.parametrize("script", SCRIPTS, ids=_nome)
def test_nenhum_script_escreve_estilo_que_a_politica_recusaria(script):
    """`FR-2106`: mudar `elemento.style.x` é CSSOM, e a política deixa; escrever o atributo
    `style`, ou marcação com ele, ou criar um `<style>`, não."""
    texto = re.sub(r"//[^\n]*|/\*.*?\*/", "", script.read_text(), flags=re.S)

    assert not re.search(r"""setAttribute\(\s*["']style""", texto)
    assert not re.search(r"""style\s*=\s*\\?["']""", texto)
    assert not re.search(r"""createElement\(\s*["']style""", texto)
    assert "eval(" not in texto and "new Function" not in texto


def _raiz_do_modelo(modelo):
    """O modelo base de onde a página herda, seguindo os `{% extends %}`."""
    atual = modelo
    while achado := re.match(r"""\s*\{%\s*extends\s+["']([^"']+)["']""", atual.read_text()):
        app, nome = achado.group(1).split("/", 1)
        atual = next(RAIZ.glob(f"*/templates/{app}/{nome}"))
    return atual


def test_toda_pagina_com_htmx_herda_a_configuracao_que_o_desarma():
    """`FR-2107`, D-009: o htmx não injeta `<style>` nem avalia código em página nenhuma."""
    com_htmx = [m for m in TODOS_OS_MODELOS if "htmx.min.js" in m.read_text()]
    assert len(com_htmx) >= 6, com_htmx

    for modelo in com_htmx:
        base = _raiz_do_modelo(modelo)
        meta = re.search(r"""<meta name="htmx-config" content='([^']*)'>""", base.read_text())
        assert meta, f"{_nome(modelo)} herda de {_nome(base)}, sem a configuração do htmx"
        assert '"includeIndicatorStyles":false' in meta.group(1)
        assert '"allowEval":false' in meta.group(1)


# ---- as medidas que vêm do dado (D-005) --------------------------------------------------------


@pytest.mark.parametrize(
    ("arquivo", "prefixo", "propriedade"),
    [
        ("interface/telas/minhas-etapas.css", "largura", "width"),
        ("interface/grupos/serie.css", "altura", "height"),
    ],
)
def test_uma_classe_por_valor_de_zero_a_cem(arquivo, prefixo, propriedade):
    """A barra de Minhas Etapas e a da série saíram do `style=""` para classe: cada percentual
    inteiro de 0 a 100 tem a sua regra, com o mesmo valor que o atributo dava."""
    regras = sem_comentarios((ESTATICOS / arquivo).read_text())
    for valor in range(101):
        assert f".{prefixo}-{valor}{{{propriedade}:{valor}%;}}" in regras, valor
    assert f".{prefixo}-101" not in regras
