"""Capturas das telas do estudo, com Playwright, contra o servidor do estudo já no ar.

    PLANO=plano.json SAIDA=../capturas python capturar.py

`plano.json` é uma lista de capturas: `{"arquivo", "quem", "url", "acao"?, "alvo"?, "altura"?}`.

- `quem` é uma identidade do seletor da demonstração (`demo.presidente`, `demo.julgador`…), ou
  `sessao:<chave>` para entrar no portal com uma sessão de candidato criada à parte;
- `acao` é JavaScript executado antes da captura (abrir a prévia, rolar até uma seção);
- `alvo` é um seletor CSS: captura só aquele elemento;
- `altura` limita a captura da página inteira, em pixels; `janela` captura só a janela visível.

A sessão da gestão é aberta a cada captura: com o relógio da aplicação deslocado, ela não sobrevive
muito tempo, e abrir de novo custa um clique.
"""

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE", "http://localhost:8140")
PLANO = json.loads(Path(os.environ["PLANO"]).read_text())
SAIDA = Path(os.environ.get("SAIDA", "capturas"))
SAIDA.mkdir(parents=True, exist_ok=True)
SO = set(sys.argv[1:])


def entrar(pagina, quem):
    pagina.context.clear_cookies()
    if quem.startswith("sessao:"):
        pagina.context.add_cookies(
            [{"name": "sessionid", "value": quem.split(":", 1)[1], "url": BASE}]
        )
        return
    if quem == "publico":
        return
    pagina.goto(f"{BASE}/gestao/identificar/demonstracao")
    with pagina.expect_navigation():
        pagina.click(f'button[name=identidade_sugerida][value="{quem}"]')


with sync_playwright() as p:
    navegador = p.chromium.launch()
    contexto = navegador.new_context(viewport={"width": 1280, "height": 900}, locale="pt-BR")
    pagina = contexto.new_page()
    for item in PLANO:
        if SO and item["arquivo"] not in SO:
            continue
        entrar(pagina, item["quem"])
        pagina.goto(BASE + item["url"])
        pagina.wait_for_load_state("networkidle")
        if item.get("acao"):
            pagina.evaluate(f"async () => {{ {item['acao']} }}")
            pagina.wait_for_timeout(item.get("espera", 2500))
        destino = SAIDA / item["arquivo"]
        if item.get("janela"):
            # Só o que está na janela, depois de a ação rolar até o trecho que interessa.
            pagina.screenshot(path=destino, type="jpeg", quality=78)
        elif item.get("alvo"):
            pagina.locator(item["alvo"]).first.screenshot(path=destino, type="jpeg", quality=78)
        else:
            altura = item.get("altura", 2600)
            total = pagina.evaluate("document.documentElement.scrollHeight")
            pagina.screenshot(
                path=destino,
                type="jpeg",
                quality=78,
                full_page=True,
                clip=None if total <= altura else {"x": 0, "y": item.get("topo", 0), "width": 1280, "height": altura},
            )
        print("ok", item["arquivo"], pagina.url)
    navegador.close()
