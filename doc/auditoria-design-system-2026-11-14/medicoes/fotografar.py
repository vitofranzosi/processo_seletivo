import sys, pathlib
from playwright.sync_api import sync_playwright
D = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2]); out.mkdir(exist_ok=True); paginas = sys.argv[3:]
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in ((1440, 900), (1920, 1080), (375, 812)):
        pg = b.new_page(viewport={"width": w, "height": h})
        for n in paginas:
            pg.goto((D / "prototipos" / f"{n}.html").as_uri()); m = pg.evaluate("() => ({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, h: document.documentElement.scrollHeight})")
            pg.set_viewport_size({"width": w, "height": max(h, m["h"])}); pg.screenshot(path=str(out / f"{n}-{w}.png")); pg.set_viewport_size({"width": w, "height": h})
            print(n, w, m)
        pg.close()
    b.close()
