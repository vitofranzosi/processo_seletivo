"""A página de autorização do provedor, para os testes de navegador (107, `D-013`).

**Mora no código de teste, e só existe enquanto um teste a sobe.** O adaptador continua o provedor
simulado da `106`; esta página é o lado dele que o navegador vê. O ambiente de testes **prepara**
quem o provedor vai autenticar — `preparar(...)`, antes da ação —, e a página mostra essa pessoa e
um botão "Continuar", que volta ao retorno da gestão com o `state` da ida e um bilhete emitido
naquele instante. O navegador não escolhe ninguém, e nada do que ele enviar vira identidade: o
bilhete é a única coisa que o retorno troca, e só o provedor simulado o resolve.

Por que uma página, e não a interceptação do Playwright: o Chromium não deixa a interceptação
alcançar o destino de um redirecionamento, e `provedor.invalid` não resolve em rede nenhuma.
"""

import html
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlsplit

from tests.fixtures import provedor_simulado


class PaginaDoProvedor:
    """O servidor da página, e a fila de quem ele vai autenticar."""

    def __init__(self):
        self._fila = []
        pagina = self

        class Atendente(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802 — o nome é o do `http.server`
                pagina._atender(self)

            def log_message(self, *args):
                pass

        self._servidor = ThreadingHTTPServer(("localhost", 0), Atendente)
        self._linha = threading.Thread(target=self._servidor.serve_forever, daemon=True)

    @property
    def endereco(self):
        return f"http://localhost:{self._servidor.server_port}/autorizar"

    def subir(self):
        self._linha.start()
        return self

    def derrubar(self):
        self._servidor.shutdown()
        self._servidor.server_close()
        self._linha.join(timeout=5)

    def preparar(self, identificador, *, nome="", email=""):
        """Quem o provedor autentica na próxima ida — a resposta preparada pelo ambiente."""
        self._fila.append((identificador, nome, email))

    def _atender(self, pedido):
        consulta = parse_qs(urlsplit(pedido.path).query)
        estado = consulta.get("state", [""])[0]
        retorno = consulta.get("redirect_uri", [""])[0]
        if not self._fila or not estado or not retorno:
            self._responder(pedido, 400, "<p>Nenhuma identidade preparada para esta ida.</p>")
            return
        identificador, nome, email = self._fila.pop(0)
        bilhete = provedor_simulado.emitir(identificador, nome=nome, email=email)
        volta = f"{retorno}?{urlencode({'state': estado, 'bilhete': bilhete})}"
        corpo = (
            "<h1>Provedor simulado — ambiente de testes</h1>"
            f"<p>Autentica: <strong>{html.escape(nome or identificador)}</strong>"
            f"{(' (' + html.escape(email) + ')') if email else ''}</p>"
            f'<p><a href="{html.escape(volta)}">Continuar</a></p>'
        )
        self._responder(pedido, 200, corpo)

    @staticmethod
    def _responder(pedido, status, corpo):
        dados = f"<!doctype html><meta charset=utf-8><title>Provedor</title>{corpo}".encode()
        pedido.send_response(status)
        pedido.send_header("Content-Type", "text/html; charset=utf-8")
        pedido.send_header("Content-Length", str(len(dados)))
        pedido.end_headers()
        pedido.wfile.write(dados)
