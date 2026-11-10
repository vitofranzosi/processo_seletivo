# ruff: noqa: E501 — roteiro de estudo, fora do lint do backend: as linhas longas são
# descrições de página e frases de asserção, que se leem melhor inteiras.
"""Serve o protótipo do estudo, estático, com a mesma CSP da gestão.

    python3 doc/estudo-continuidade-operacional-2026-11-10/prototipo/servidor.py 8171

Abra <http://localhost:8171/>. O "antes" é o HTML real salvo por `capturar_antes.py`; o "depois" é o
mesmo HTML transformado por `montar_depois.py`. Nenhum dos dois fala com o GPS: os botões que levam
adiante no percurso são links entre as páginas do protótipo, e os demais não gravam nada.

**A CSP é a de produção** (`shared/politica_de_conteudo.py`: `style-src 'self'`, `script-src 'self'`,
sem `unsafe-inline`). Sem ela, um `style=""` escrito no "depois" funcionaria aqui e sumiria em
silêncio na implementação — a armadilha que o CLAUDE.md registra.
"""

import functools
import http.server
import sys
from pathlib import Path

SITIO = Path(__file__).resolve().parent / "sitio"
CSP = "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:"


class Manipulador(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


def servir(porta):
    manipulador = functools.partial(Manipulador, directory=str(SITIO))
    return http.server.ThreadingHTTPServer(("127.0.0.1", porta), manipulador)


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8171
    print(f"Protótipo em http://localhost:{porta}/")
    servir(porta).serve_forever()
