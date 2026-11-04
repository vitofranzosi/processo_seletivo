import sys, pathlib
from playwright.sync_api import sync_playwright
d = pathlib.Path(sys.argv[1])
with sync_playwright() as p:
    b = p.chromium.launch()
    for f in sorted(d.glob("*-depois.html")):
        for nome, vp in (("375", {"width": 375, "height": 812}), ("desktop", {"width": 1280, "height": 900})):
            pg = b.new_page(viewport=vp)
            pg.goto(f.as_uri())
            pg.screenshot(path=str(d / f"{f.stem}-{nome}.png"), full_page=True)
            print(f.stem, nome, pg.evaluate("document.documentElement.scrollWidth"), pg.evaluate("document.documentElement.scrollHeight"))
            pg.close()
    b.close()
