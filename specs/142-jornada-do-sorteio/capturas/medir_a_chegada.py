import importlib.util, sys
spec = importlib.util.spec_from_file_location("c", sys.argv[1]); c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    n = p.chromium.launch()
    for largura, altura in ((1440, 900), (375, 812)):
        pg = c.entrar(n, c.PRESIDENCIA, largura, altura)
        pg.goto(f"{c.BASE}/gestao/editais/{sys.argv[2]}/centro/")
        hrefs = pg.eval_on_selector_all("a[href*='/sorteio']", "e=>e.map(x=>x.getAttribute('href'))")
        alvo = next(h for h in hrefs if "#sorteio-" in h)
        pg.goto(c.BASE + alvo)
        pg.wait_for_timeout(300)
        y = pg.evaluate("""() => { const b = document.querySelector(location.hash + " form[action$='/sorteio/realizar'] button"); return b ? Math.round(b.getBoundingClientRect().top) : null }""")
        print(largura, alvo.split("#")[1][:20], "botão a", y, "px do topo da janela de", altura)
        pg.screenshot(path=f"{c.SAIDA}/depois-12-c06r2-chegada-do-centro-ao-sorteio-{largura}.png")
    n.close()
