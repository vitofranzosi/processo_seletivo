"""A folha comum da gestão e os tokens, para os guardiões que os leem (089).

Até a `089` a folha comum era o `<style>` do `interface/base.html`, e os guardiões a liam de dois
jeitos: o texto do modelo, ou o primeiro `<style>` da página renderizada. Ela saiu para
`interface/static/interface/gestao.css` — dividida por área na 091, em `interface/gestao/` —, e os
tokens para `shared/static/shared/tokens.css`. No
modelo e na página ficou um `<style>` só com o estilo da página — na lista, duas regras.

**É aí que mora o perigo.** Um guardião que continuasse lendo o modelo ou o primeiro `<style>` não
quebraria: as afirmações negativas — "esta regra não existe", "nenhuma largura em pixel" — passariam
sobre um resto quase vazio, sem examinar nada. Daí uma fonte só para os dois jeitos de ler, aqui.
"""

import re
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders

from processo_seletivo.shared.estaticos import FOLHAS_DA_GESTAO

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo"
ESTATICOS = RAIZ / "interface/static"
# Desde a 091 a folha comum são sete arquivos por área, na ordem de `FOLHAS_DA_GESTAO` — a mesma
# lista com que a base os carrega. E o estilo de cada tela, e de cada grupo de telas, é arquivo.
ARQUIVOS_DA_FOLHA_COMUM = [ESTATICOS / caminho for caminho in FOLHAS_DA_GESTAO]
FOLHAS_DE_TELA = sorted(
    [*ESTATICOS.glob("interface/telas/*.css"), *ESTATICOS.glob("interface/grupos/*.css")]
)
TOKENS_CSS = RAIZ / "shared/static/shared/tokens.css"
ERRO_CSS = RAIZ / "shared/static/shared/erro.css"

# O texto dos arquivos, com os comentários — como os guardiões de texto liam o modelo, com os
# `{% comment %}`. Quem descontava comentário continua descontando (`sem_comentarios`). A folha
# comum é a soma dos arquivos, na ordem de carga: um guardião que lia "a folha" lê todos.
FOLHA_COMUM = "".join(arquivo.read_text() for arquivo in ARQUIVOS_DA_FOLHA_COMUM)
TOKENS = TOKENS_CSS.read_text()

# Qualquer `<link>` e qualquer `<style>`, com os atributos que tiverem e na ordem que tiverem: um
# padrão preso à grafia de hoje deixaria de fora, em silêncio, a primeira folha escrita de outro
# jeito (`media="print"`, `href` antes de `rel`) — e o guardião aprovaria uma regra que não leu.
_LINK_OU_ESTILO = re.compile(r"<link\b(?P<link>[^>]*)>|<style\b[^>]*>(?P<estilo>.*?)</style>", re.S)
_REL = re.compile(r"""\brel\s*=\s*["']?([^"'>]*)""")
_HREF = re.compile(r"""\bhref\s*=\s*["']?([^"'?#>\s]+)""")
_COMENTARIO_CSS = re.compile(r"/\*.*?\*/", re.S)
_COMENTARIO_DE_MODELO = re.compile(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", re.S)


def sem_comentarios(texto, troca=""):
    """O texto de uma folha sem os comentários, de CSS e de modelo.

    Os comentários citam regras e classes o tempo todo, e citar não é definir. Uma remoção só, para
    todos os guardiões: a forma do comentário já mudou uma vez (na 089, de `{% comment %}` para
    `/* */`), e cada cópia da remoção era um lugar a esquecer. `troca` é o que fica no lugar —
    um espaço, para quem não pode deixar dois seletores colarem.
    """
    return _COMENTARIO_DE_MODELO.sub(troca, _COMENTARIO_CSS.sub(troca, texto))


def folha_aplicada(corpo):
    """A folha que a página aplica: as folhas externas do `<head>` e os `<style>` dele, na ordem.

    É o que o primeiro `<style>` da página continha até a `089` — os tokens, a folha comum e o
    estilo da página, nessa ordem. As externas entram **sem** os `/* */`: na página renderizada de
    antes os comentários da folha não apareciam, porque eram de modelo, e dois deles citam regras
    com chave (`thead th>*{display:block}`) que um guardião leria como regra. Os `<style>` do
    documento entram como estão, como antes.

    O arquivo é achado pelos *finders* do `staticfiles`, os mesmos que o servem no runserver: um
    `<link>` para estático inexistente falha aqui, e não passa em branco.
    """
    if isinstance(corpo, bytes):
        corpo = corpo.decode()
    cabeca = corpo[: corpo.index("</head>")]
    partes = []
    for achado in _LINK_OU_ESTILO.finditer(cabeca):
        if achado.group("link") is None:
            partes.append(achado.group("estilo"))
            continue
        rel = _REL.search(achado.group("link"))
        if not rel or "stylesheet" not in rel.group(1).split():
            continue
        href = _HREF.search(achado.group("link"))
        assert href, f"folha sem endereço: <link{achado.group('link')}>"
        caminho = href.group(1).removeprefix("/" + settings.STATIC_URL.lstrip("/"))
        arquivo = finders.find(caminho)
        assert arquivo, f"folha carregada e inexistente: {href.group(1)}"
        partes.append(sem_comentarios(Path(arquivo).read_text()))
    assert partes, "a página não carrega folha nenhuma"
    return "\n".join(partes)


def folha_da_pagina(cliente, url):
    """A folha que a página daquele endereço aplica, pedida pelo cliente já identificado."""
    return folha_aplicada(cliente.get(url).content)


# O endereço que a tag `estatico` recebe, num modelo: `{% estatico 'interface/telas/lista.css' %}`.
_ESTATICO = re.compile(r"""\{%\s*estatico\s+['"]([^'"]+)['"]\s*%\}""")
_BLOCO_DE_ESTILO = re.compile(r"\{%\s*block\s+estilo_da_pagina\s*%\}(.*?)\{%\s*endblock\s*%\}", re.S)


def estilo_do_bloco(modelo):
    """O estilo que o `{% block estilo_da_pagina %}` de um modelo carrega, com os comentários (091).

    Até a `091` o bloco **era** o estilo — regras e `{% comment %}` no próprio modelo, ou o
    `include` de um parcial `_estilo_*`. Desde ela, o bloco só tem `<link>` para arquivos de
    `interface/telas/` e `interface/grupos/`. Um guardião que continuasse lendo o texto do bloco
    acharia só endereços, e a negação — "esta regra não está aqui" — passaria sem ler regra
    nenhuma. Daqui sai o texto dos arquivos, na ordem do bloco, como o bloco era lido.

    `modelo` é o texto do modelo; sem bloco, a resposta é vazia. Arquivo citado e inexistente
    falha aqui, pelos mesmos *finders* que o servem.
    """
    achado = _BLOCO_DE_ESTILO.search(modelo)
    if not achado:
        return ""
    partes = []
    for caminho in _ESTATICO.findall(achado.group(1)):
        arquivo = finders.find(caminho)
        assert arquivo, f"folha citada no bloco e inexistente: {caminho}"
        partes.append(Path(arquivo).read_text())
    return "".join(partes)
