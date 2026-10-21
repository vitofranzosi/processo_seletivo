"""Servidor do protótipo da 094 — biblioteca padrão, sem Django e sem banco.

Rode de dentro de `backend/`, para que o motor do produto seja importável:

    uv run python ../specs/094-previa-da-classificacao/prototipo/servidor.py 8094

Responde toda página com a mesma política de conteúdo da gestão (`style-src 'self'`,
`script-src 'self'`, sem `unsafe-inline`): o que funciona aqui funciona sob a CSP do produto.
Nada é gravado — não há onde gravar.
"""

from __future__ import annotations

import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

AQUI = Path(__file__).resolve().parent
BACKEND = AQUI.parents[2] / "backend"
sys.path[:0] = [str(AQUI), str(BACKEND)]

import pagina  # noqa: E402

ESTATICOS = {
    "/estatico/htmx.min.js": (
        BACKEND / "processo_seletivo/interface/static/interface/htmx.min.js",
        "text/javascript",
    ),
    "/estatico/prototipo.js": (AQUI / "estatico/prototipo.js", "text/javascript"),
    "/estatico/prototipo.css": (AQUI / "estatico/prototipo.css", "text/css"),
}
CSP = (
    "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self'; "
    "object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
)


class Prototipo(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 — nome da biblioteca padrão
        partes = urlsplit(self.path)
        dados = parse_qs(partes.query, keep_blank_values=True)
        if partes.path in ESTATICOS:
            caminho, tipo = ESTATICOS[partes.path]
            return self._responder(caminho.read_bytes(), tipo)
        if partes.path == "/":
            exemplo = (dados.get("exemplo") or [""])[0]
            return self._responder(pagina.pagina(pagina.configuracao(exemplo), exemplo))
        if partes.path == "/previa":
            return self._responder(pagina.painel(dados))
        if partes.path == "/fechar":
            return self._responder(
                '<p id="anuncio-da-previa" class="oculto" role="status" aria-live="polite" '
                'hx-swap-oob="true">Prévia fechada.</p>'
            )
        if partes.path == "/saude":
            return self._responder("ok", "text/plain")
        self.send_error(404)

    def _responder(self, corpo, tipo="text/html"):
        dados = corpo if isinstance(corpo, bytes) else corpo.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", f"{tipo}; charset=utf-8")
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8094
    print(f"Protótipo da 094 em http://localhost:{porta}/", flush=True)
    ThreadingHTTPServer(("localhost", porta), Prototipo).serve_forever()
