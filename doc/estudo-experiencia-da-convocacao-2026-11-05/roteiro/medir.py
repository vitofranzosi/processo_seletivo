import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
M = Path(sys.argv[1]).resolve()
with sync_playwright() as p:
    b = p.chromium.launch()
    for nome in ["convocacao", "convocacao-apos-envio", "convocacao-pendencia", "convocacao-sucessora", "acesso-1-email", "acesso-2-codigo", "email"]:
        pg = b.new_page(viewport={"width": 375, "height": 812}); pg.goto((M / f"{nome}.html").as_uri())
        sw = pg.evaluate("document.documentElement.scrollWidth")
        fim = pg.evaluate("(() => { const a = document.querySelector('.progresso-das-obrigacoes a.principal, .confirmacao-do-envio a'); return a ? Math.round(a.getBoundingClientRect().bottom) : null })()")
        print(nome, "scrollWidth", sw, "fim da acao", fim)
    b.close()
