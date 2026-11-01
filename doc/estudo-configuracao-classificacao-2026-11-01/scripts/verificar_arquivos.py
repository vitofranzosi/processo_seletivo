"""Confere destinos locais referenciados nos documentos e HTML do estudo."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

RAIZ = Path(__file__).resolve().parent.parent
falhas = []
verificados = 0


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for chave, valor in attrs:
            if chave in ("href", "src") and valor:
                self.links.append(valor)


for arquivo in [
    *RAIZ.glob("*.md"),
    *RAIZ.glob("*.html"),
    *RAIZ.glob("prototipos/*.html"),
]:
    texto = arquivo.read_text()
    if arquivo.suffix == ".html":
        parser = Links()
        parser.feed(texto)
        links = parser.links
    else:
        links = re.findall(r"\]\(([^)]+)\)", texto)
    for link in links:
        url = urlsplit(link)
        if url.scheme or not url.path or url.path.startswith("/"):
            continue
        destino = (arquivo.parent / unquote(url.path)).resolve()
        verificados += 1
        if not destino.exists():
            falhas.append({"origem": str(arquivo.relative_to(RAIZ)), "link": link})
resultado = {"links_locais_verificados": verificados, "falhas": falhas}
(RAIZ / "verificacao-arquivos.json").write_text(
    json.dumps(resultado, ensure_ascii=False, indent=2)
)
assert not falhas, falhas
print(f"{verificados} referências locais existentes.")
