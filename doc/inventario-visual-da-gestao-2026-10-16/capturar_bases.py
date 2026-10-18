"""As bases fora da gestão que dividem os tokens com ela: o portal e a página de erro (089).

    capturar_bases.py <saida>

A página de acesso da gestão já está no `capturar.py` (`identificar`). Esta captura a vitrine e a
entrada do portal e a página de erro, a 1280 e a 375 px, no formato do inventário (`png/` e
`resultados.json`), para o `pixels.py` e o `comparar.py`. Roda com o ambiente do backend, como o
`capturar.py`.

`DEBUG` desligado neste processo: com ele ligado, o Django responde a rota inexistente com a página de
depuração, e não com o `404.html` do sistema, que é o que usa os tokens.
"""

import json
import os
import sys
import threading
from pathlib import Path

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
sys.path.insert(0, os.getcwd())

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.staticfiles.handlers import StaticFilesHandler  # noqa: E402
from django.core.servers.basehttp import ThreadedWSGIServer, WSGIRequestHandler  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from estilos import ESTILOS  # noqa: E402

settings.DEBUG = False


class Quieto(WSGIRequestHandler):
    def log_message(self, *a):
        pass


PORTA = int(os.environ.get("PORTA", "8098"))
BASE = f"http://localhost:{PORTA}"
SAIDA = Path(sys.argv[1])
(SAIDA / "png").mkdir(parents=True, exist_ok=True)

servidor = ThreadedWSGIServer(("localhost", PORTA), Quieto)
servidor.set_app(StaticFilesHandler(get_wsgi_application()))
threading.Thread(target=servidor.serve_forever, daemon=True).start()

ROTAS = [
    ("portal-vitrine", "/selecoes/", 200),
    ("portal-acesso", "/selecoes/acesso", 200),
    ("pagina-de-erro", "/selecoes/nao-existe", 404),
]

MEDIR = """() => {
  const de = document.documentElement;
  const folhas = [...document.styleSheets].map(f => f.href ? 'link ' + f.cssRules.length : 'style ' + f.cssRules.length);
  return {scrollWidth: de.scrollWidth, clientWidth: de.clientWidth, altura: de.scrollHeight,
          titulo: document.title, h1: (document.querySelector('h1')||{}).textContent?.trim().slice(0,120) || '',
          folhas};
}"""

resultados = []
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
    for rid, caminho, esperado in ROTAS:
        pg = ctx.new_page()
        resp = pg.goto(BASE + caminho, wait_until="load")
        linha = {"id": rid, "caminho": caminho, "status": resp.status if resp else 0}
        assert linha["status"] == esperado, linha
        for largura, altura in ((1280, 900), (375, 812)):
            pg.set_viewport_size({"width": largura, "height": altura})
            pg.wait_for_timeout(150)
            linha[str(largura)] = pg.evaluate(MEDIR)
            # O mesmo resumo das regras do `capturar.py`, sempre ligado aqui.
            linha[str(largura)]["estilos"] = pg.evaluate(ESTILOS)
            pg.screenshot(path=str(SAIDA / "png" / f"{rid}--{largura}.png"), full_page=True)
        resultados.append(linha)
        print(rid, linha["status"], linha["375"]["folhas"], flush=True)
        pg.close()
    browser.close()

(SAIDA / "resultados.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1))
servidor.shutdown()
