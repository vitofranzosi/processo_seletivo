"""A folha comum da gestão e os tokens, para os guardiões que os leem (089).

Até a `089` a folha comum era o `<style>` do `interface/base.html`, e os guardiões a liam de dois
jeitos: o texto do modelo, ou o primeiro `<style>` da página renderizada. Ela saiu para
`interface/static/interface/gestao.css`, e os tokens para `shared/static/shared/tokens.css`. No
modelo e na página ficou um `<style>` só com o estilo da página — na lista, duas regras.

**É aí que mora o perigo.** Um guardião que continuasse lendo o modelo ou o primeiro `<style>` não
quebraria: as afirmações negativas — "esta regra não existe", "nenhuma largura em pixel" — passariam
sobre um resto quase vazio, sem examinar nada. Daí uma fonte só para os dois jeitos de ler, aqui.
"""

import re
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo"
GESTAO_CSS = RAIZ / "interface/static/interface/gestao.css"
TOKENS_CSS = RAIZ / "shared/static/shared/tokens.css"

# O texto dos arquivos, com os comentários — como os guardiões de texto liam o modelo, com os
# `{% comment %}`. Quem descontava comentário continua descontando (`sem_prosa`).
FOLHA_COMUM = GESTAO_CSS.read_text()
TOKENS = TOKENS_CSS.read_text()

_FOLHA_OU_ESTILO = re.compile(
    r'<link rel="stylesheet" href="(?P<href>[^"?]+)(?:\?[^"]*)?">|<style>(?P<estilo>.*?)</style>',
    re.S,
)
_COMENTARIO = re.compile(r"/\*.*?\*/", re.S)


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
    for achado in _FOLHA_OU_ESTILO.finditer(cabeca):
        if achado.group("href") is None:
            partes.append(achado.group("estilo"))
            continue
        caminho = achado.group("href").removeprefix("/" + settings.STATIC_URL.strip("/") + "/")
        arquivo = finders.find(caminho)
        assert arquivo, f"folha carregada e inexistente: {achado.group('href')}"
        partes.append(_COMENTARIO.sub("", Path(arquivo).read_text()))
    assert partes, "a página não carrega folha nenhuma"
    return "\n".join(partes)
