"""Conferência de impressão da gestão (088): o que cada tela põe no papel.

Roda como o `capturar.py`, com o ambiente do backend e o mesmo banco. Para cada tela, emula a mídia
de impressão, lê o que fica visível do cabeçalho de contexto e da barra, guarda a captura da página
impressa e imprime em PDF pelo Chrome sem interface (`page.pdf`, o mesmo motor do
`--print-to-pdf`). A saída é `impressao.json`, os PNG e os PDF no diretório pedido.

    uv run --with playwright python ../doc/inventario-visual-da-gestao-2026-10-16/imprimir.py SAIDA
"""

import json
import os
import sys
import threading
from pathlib import Path
from urllib.parse import urlencode

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
sys.path.insert(0, os.getcwd())

import django  # noqa: E402

django.setup()

from django.contrib.staticfiles.handlers import StaticFilesHandler  # noqa: E402
from django.core.servers.basehttp import ThreadedWSGIServer, WSGIRequestHandler  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


class Quieto(WSGIRequestHandler):
    def log_message(self, *a):
        pass


PORTA = int(os.environ.get("PORTA", "8098"))
BASE = f"http://localhost:{PORTA}"
SAIDA = Path(sys.argv[1])
SAIDA.mkdir(parents=True, exist_ok=True)

servidor = ThreadedWSGIServer(("localhost", PORTA), Quieto)
servidor.set_app(StaticFilesHandler(get_wsgi_application()))
threading.Thread(target=servidor.serve_forever, daemon=True).start()

# Os objetos do seed, os mesmos do `capturar.py`.
E51 = "af86be76-27f3-4e6a-b621-2b0771c323b2"
ETAPA = "00000000-0000-0000-0051-0000000000d1"
M51 = "00000000-0000-0000-0051-0000000000a1"
ATO51 = "ac2080d5-e5a7-47ac-b251-246e03fbde81"
INSC = "3cd5294d-bbf6-4fbe-88fc-95c3a62b927b"
REC_ADMITIDO = "c7b47be9-fdcd-488d-8e3d-fe6be445072e"
AVISO = os.environ.get("AVISO")

TELAS = [
    ("mesa-inscricao", f"/gestao/minhas-etapas/{E51}/{ETAPA}/inscricoes/{INSC}",
     "joana.avaliadora", []),
    ("ato-de-ordenacao", f"/gestao/editais/{E51}/marcos/{M51}/atos/{ATO51}",
     "paulo.presidente", []),
    ("inscricao-recebida", f"/gestao/inscricoes/{INSC}/", "gustavo.gestor", ["gestor"]),
    ("recurso-admitido", f"/gestao/recursos/{REC_ADMITIDO}", "inventario.julgadora", ["julgador"]),
    # A recusa é a última tela com o cabeçalho da 076, o caminho até a seção.
    ("recusa", "/gestao/inscricoes/00000000-0000-0000-0000-000000000000/", "gustavo.gestor",
     ["gestor"]),
]
if AVISO:
    TELAS.append(("aviso", f"/gestao/avisos/{AVISO}", "gustavo.gestor", ["gestor"]))

LER = """() => {
  const visivel = el => !!el && getComputedStyle(el).display !== 'none'
    && el.getBoundingClientRect().height > 0;
  const cab = document.querySelector('.cabecalho-de-contexto');
  const trocar = cab && cab.querySelector(':scope > a');
  const h1 = document.querySelector('h1');
  return {
    cabecalho_visivel: visivel(cab),
    texto_do_cabecalho: visivel(cab) ? cab.innerText.trim() : '',
    trocar_identidade_visivel: visivel(trocar),
    barra_visivel: visivel(document.querySelector('.barra-lateral')),
    cabecalho_antes_do_titulo: !!(cab && h1 && visivel(cab)
      && cab.getBoundingClientRect().bottom <= h1.getBoundingClientRect().top),
    h1: h1 ? h1.innerText.trim() : '',
  };
}"""


def entrar(browser, quem, papeis):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
    pg = ctx.new_page()
    pg.goto(f"{BASE}/gestao/identificar/demonstracao")
    token = next(c["value"] for c in ctx.cookies() if c["name"] == "csrftoken")
    pares = [("csrfmiddlewaretoken", token), ("identidade_sugerida", quem)]
    pares += [("papeis", p) for p in papeis]
    r = ctx.request.post(f"{BASE}/gestao/identificar", data=urlencode(pares),
                         headers={"Content-Type": "application/x-www-form-urlencoded",
                                  "X-CSRFToken": token, "Referer": f"{BASE}/gestao/identificar"})
    assert r.ok, (quem, r.status)
    pg.close()
    return ctx


resultados = []
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    for rid, caminho, quem, papeis in TELAS:
        ctx = entrar(browser, quem, papeis)
        pg = ctx.new_page()
        resp = pg.goto(BASE + caminho, wait_until="load")
        na_tela = pg.evaluate(LER)
        pg.emulate_media(media="print")
        no_papel = pg.evaluate(LER)
        pg.screenshot(path=str(SAIDA / f"{rid}--papel.png"), full_page=False)
        pg.pdf(path=str(SAIDA / f"{rid}.pdf"), format="A4", print_background=False)
        resultados.append({"id": rid, "status": resp.status, "tela": na_tela, "papel": no_papel})
        print(rid, resp.status, json.dumps(no_papel, ensure_ascii=False))
        ctx.close()
    browser.close()

(SAIDA / "impressao.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1))
servidor.shutdown()
