import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
M = Path(sys.argv[1]).resolve(); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
telas = {
  "convocacao": ["desktop", "375"], "convocacao-apos-envio": ["desktop", "375"],
  "convocacao-pendencia": ["desktop", "375"], "convocacao-sucessora": ["375"],
  "acesso-1-email": ["375"], "acesso-2-codigo": ["375"],
  "email": ["desktop", "375", "375-escuro"],
}
tam = {"desktop": (1280, 900), "375": (375, 812), "375-escuro": (375, 812)}
with sync_playwright() as p:
    b = p.chromium.launch()
    for nome, larguras in telas.items():
        for l in larguras:
            w, h = tam[l]
            if nome == "email" and l == "desktop": w = 720
            ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1 if l == "desktop" else 2,
                                color_scheme="dark" if "escuro" in l else "light")
            pg = ctx.new_page(); erros = []
            pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
            pg.goto((M / f"{nome}.html").as_uri())
            larg = pg.evaluate("document.documentElement.scrollWidth")
            pg.screenshot(path=str(OUT / f"{nome}-{l}.png"), full_page=True)
            if l == "375" and nome.startswith("convocacao"):
                pg.screenshot(path=str(OUT / f"{nome}-375-primeira-tela.png"))
            print(nome, l, "scrollWidth", larg, "erros", erros)
            ctx.close()
    b.close()
