"""As telas do portal do candidato, antes e depois de a folha dele sair do documento (092).

    capturar_portal.py <saida>               # rastreia, grava `rotas.json` e captura
    capturar_portal.py <saida> <rotas.json>  # captura as mesmas rotas de outra passada

O `capturar_bases.py` da 089 captura três páginas do portal. A 092 muda a folha de todas, e o
portal não tem um inventário de rotas como o da gestão: aqui elas são achadas seguindo os links, a
partir da vitrine (sem sessão) e da área de cada candidata do seed — a sessão é aberta direto no
banco, com a chave do `portal/identidade.py`, sem código de acesso. A lista sai da passada de antes e
é reusada na de depois, para as duas capturarem as mesmas páginas.

Só `GET`, e só o que responde `text/html`. Rode cada passada numa cópia nova do mesmo banco: um GET
que gravasse alguma coisa mudaria a página seguinte da outra passada.

Também captura o protótipo do painel de dúvidas, que é a página pública da seleção servida pela
gestão (`interface/prototipo_do_assistente.py`), com a identidade de piloto do `capturar.py`.

Roda com o ambiente do backend, como o `capturar.py`; `DEBUG` desligado, como no `capturar_bases.py`.

`IMPRESSAO=1` troca a tela pelo papel: cada rota (só as que casam com `SO=<regex>`, se dada) é
capturada com a mídia de impressão emulada, em `<id>--papel.png`, e o número de páginas do PDF que o
navegador gera vai para o `resultados.json`. É a prova da FR-2143: o comprovante é salvo em PDF pelo
candidato, e as regras de `@media print` têm de valer no papel como antes.
"""

import json
import os
import re
import sys
import threading
from collections import deque
from importlib import import_module
from pathlib import Path
from urllib.parse import urlencode, urlsplit

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
sys.path.insert(0, os.getcwd())

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.staticfiles.handlers import StaticFilesHandler  # noqa: E402
from django.core.servers.basehttp import ThreadedWSGIServer, WSGIRequestHandler  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from processo_seletivo.identidade.models import CandidateIdentity  # noqa: E402
from processo_seletivo.portal.identidade import CHAVE_SESSAO  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent.parent))
from estilos import CONJUNTO, ESCUTAR_VIOLACOES, ESTILOS, VIOLACOES  # noqa: E402

settings.DEBUG = False


class Quieto(WSGIRequestHandler):
    def log_message(self, *a):
        pass


PORTA = int(os.environ.get("PORTA", "8099"))
BASE = f"http://localhost:{PORTA}"
SAIDA = Path(sys.argv[1])
(SAIDA / "png").mkdir(parents=True, exist_ok=True)

servidor = ThreadedWSGIServer(("localhost", PORTA), Quieto)
servidor.set_app(StaticFilesHandler(get_wsgi_application()))
threading.Thread(target=servidor.serve_forever, daemon=True).start()

CANDIDATAS = [
    "ana@exemplo.test",
    "bruno@exemplo.test",
    "clara@exemplo.test",
    "daniel@exemplo.test",
    "elisa@exemplo.test",
    "amanda.sorteio@exemplo.test",
]
E01 = "ec6018d1-6970-4bfb-8697-350922669a20"  # 01/2026, retificado (o do `capturar.py`)
PROTOTIPO = f"/gestao/editais/{E01}/assistente/prototipo/"

# Quantas páginas de um mesmo desenho de endereço (os UUID trocados por `{id}`): a vitrine leva a
# dezenas de seleções iguais na forma, e três de cada bastam para ver a folha em cada uma.
POR_FORMA = int(os.environ.get("POR_FORMA", "3"))
NUNCA = re.compile(r"/sair$|/assistente/(sugestao|nova)")
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

MEDIR = """() => {
  const de = document.documentElement;
  const folhas = [...document.styleSheets].map(f => (f.href ? 'link ' : 'style ') + f.cssRules.length);
  return {scrollWidth: de.scrollWidth, clientWidth: de.clientWidth, altura: de.scrollHeight,
          titulo: document.title, h1: (document.querySelector('h1')||{}).textContent?.trim().slice(0,120) || '',
          folhas};
}"""
LINKS = """() => [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))"""


def contexto(browser, quem):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
    ctx.add_init_script(ESCUTAR_VIOLACOES)
    if quem is None:
        return ctx
    if quem == "inventario.piloto":
        pg = ctx.new_page()
        pg.goto(f"{BASE}/gestao/identificar/demonstracao")
        token = next(c["value"] for c in ctx.cookies() if c["name"] == "csrftoken")
        pares = [("csrfmiddlewaretoken", token), ("identidade_sugerida", quem)]
        pares += [("papeis", "gestor"), ("papeis", "participante-piloto-assistente")]
        r = ctx.request.post(
            f"{BASE}/gestao/identificar",
            data=urlencode(pares),
            headers={"Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": token,
                     "Referer": f"{BASE}/gestao/identificar"},
        )
        assert r.ok, (quem, r.status)
        pg.close()
        return ctx
    registro = CandidateIdentity.objects.get(credenciais__email_como_informado=quem)
    sessao = import_module(settings.SESSION_ENGINE).SessionStore()
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()
    ctx.add_cookies([{"name": settings.SESSION_COOKIE_NAME, "value": sessao.session_key,
                      "domain": "localhost", "path": "/"}])
    return ctx


def forma(caminho):
    return UUID.sub("{id}", caminho)


def rastrear(browser):
    """As rotas, em ordem de descoberta, a partir da vitrine e da área de cada candidata."""
    rotas, vistas, por_forma = [], set(), {}
    for quem in [None, *CANDIDATAS]:
        ctx = contexto(browser, quem)
        fila = deque(["/selecoes/", "/selecoes/acesso"] if quem is None else ["/selecoes/inscricoes/"])
        while fila:
            caminho = fila.popleft()
            chave = (quem, caminho)
            if chave in vistas or NUNCA.search(caminho):
                continue
            vistas.add(chave)
            if por_forma.get((quem, forma(caminho)), 0) >= POR_FORMA:
                continue
            resposta = ctx.request.get(BASE + caminho, max_redirects=0)
            tipo = resposta.headers.get("content-type", "")
            if resposta.status != 200 or not tipo.startswith("text/html"):
                continue
            por_forma[(quem, forma(caminho))] = por_forma.get((quem, forma(caminho)), 0) + 1
            rotas.append({"quem": quem, "caminho": caminho})
            pg = ctx.new_page()
            pg.goto(BASE + caminho, wait_until="load")
            for href in pg.evaluate(LINKS):
                partes = urlsplit(href)
                if partes.netloc and partes.netloc != f"localhost:{PORTA}":
                    continue
                destino = partes.path + (f"?{partes.query}" if partes.query else "")
                if destino.startswith("/selecoes/"):
                    fila.append(destino)
            pg.close()
        ctx.close()
    rotas.append({"quem": "inventario.piloto", "caminho": PROTOTIPO})
    return rotas


def nome(i, rota):
    quem = (rota["quem"] or "anonimo").split("@")[0]
    resto = forma(rota["caminho"]).strip("/").replace("/", "-").replace("{id}", "id") or "raiz"
    return f"{i:02d}-{quem}-{re.sub(r'[^a-z0-9-]', '-', resto)}"[:90]


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    if len(sys.argv) > 2:
        rotas = json.loads(Path(sys.argv[2]).read_text())
    else:
        rotas = rastrear(browser)
        (SAIDA / "rotas.json").write_text(json.dumps(rotas, ensure_ascii=False, indent=1))
    contextos, resultados = {}, []
    impressao, so = os.environ.get("IMPRESSAO"), re.compile(os.environ.get("SO", ""))
    for i, rota in enumerate(rotas):
        if impressao and not so.search(rota["caminho"]):
            continue
        quem = rota["quem"]
        if quem not in contextos:
            contextos[quem] = contexto(browser, quem)
        rid = nome(i, rota)
        pg = contextos[quem].new_page()
        resp = pg.goto(BASE + rota["caminho"], wait_until="load")
        linha = {"id": rid, **rota, "status": resp.status if resp else 0,
                 "politica": {k: v for k, v in (resp.headers if resp else {}).items()
                              if k.startswith("content-security-policy")}}
        if impressao:
            pg.emulate_media(media="print")
            pg.screenshot(path=str(SAIDA / "png" / f"{rid}--papel.png"), full_page=True)
            linha["paginas_do_pdf"] = len(re.findall(rb"/Type\s*/Page\b(?!s)", pg.pdf(format="A4")))
            resultados.append(linha)
            print(rid, linha["status"], linha["paginas_do_pdf"], flush=True)
            pg.close()
            continue
        for largura, altura in ((1280, 900), (375, 812)):
            pg.set_viewport_size({"width": largura, "height": altura})
            pg.wait_for_timeout(150)
            medida = pg.evaluate(MEDIR)
            medida["estilos"] = pg.evaluate(ESTILOS)
            medida["conjunto"] = pg.evaluate(CONJUNTO)
            medida["violacoes"] = pg.evaluate(VIOLACOES)
            pg.screenshot(path=str(SAIDA / "png" / f"{rid}--{largura}.png"), full_page=True)
            linha[str(largura)] = medida
        resultados.append(linha)
        print(rid, linha["status"], linha["375"]["scrollWidth"], len(linha["375"]["violacoes"]), flush=True)
        pg.close()
    browser.close()

(SAIDA / "resultados.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1))
servidor.shutdown()
