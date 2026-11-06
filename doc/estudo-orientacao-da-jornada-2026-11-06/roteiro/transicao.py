"""Pratica UM ato no banco descartável e grava a tela de antes e a que vem depois (06/11/2026).

**Grava no banco.** Só contra o clone `ps_jornada`, nunca contra banco de quem desenvolve.

Uso, do `backend/`:

    uv run python transicao.py <papel> <url> <texto-do-botão> <nome> [campo=valor ...]

Os campos são preenchidos no mesmo formulário do botão. As três transições do estudo foram:

    transicao.py gestor <57>/marcos/<design>/sorteio "Observar a ocorrência 6116 na fonte" t1-semente-57
    transicao.py gestor <26>/marcos/<marco>/corte "Emitir corte" t2-corte-26
    transicao.py gestor <26>/marcos/<marco>/ocupacao "Apurar a ocupação deste recorte" t3-apuracao-26

A primeira consultou a fonte real declarada pelo Edital (Loteria Federal): a Caixa respondeu HTTP 500 e
nada foi gravado. Não a repita sem necessidade.
"""

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("UX_BASE", "http://localhost:8140")
SAIDA = Path(os.environ.get("UX_SAIDA", Path(__file__).parent / "transicoes"))
SAIDA.mkdir(exist_ok=True)
papel, url, botao, nome = sys.argv[1:5]
campos = dict(a.split("=", 1) for a in sys.argv[5:])
TEXTO = "() => (document.querySelector('main')||document.body).innerText"

with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(BASE + "/gestao/identificar/demonstracao")
    with pg.expect_navigation():
        if papel.startswith("@"):
            pg.locator(f"button[name=identidade_sugerida][value='{papel[1:]}']").first.click()
        else:
            pg.locator(f"form:has(input[name=papeis][value='{papel}']) button").first.click()
    pg.goto(BASE + url)
    pg.screenshot(path=str(SAIDA / f"{nome}-antes.png"), full_page=True)
    alvo = pg.get_by_role("button", name=botao).first
    formulario = alvo.locator("xpath=ancestor::form[1]")
    for campo, valor in campos.items():
        formulario.locator(f"[name='{campo}']").first.fill(valor)
    with pg.expect_navigation():
        alvo.click()
    (SAIDA / f"{nome}-depois.txt").write_text(f"URL {pg.url}\n\n" + pg.evaluate(TEXTO))
    pg.screenshot(path=str(SAIDA / f"{nome}-depois.png"), full_page=True)
    print("→", pg.url)
    nav.close()
