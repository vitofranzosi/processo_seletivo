import json, time, sys
from playwright.sync_api import sync_playwright
from as_flow import BASE, E01, panel_text, boxes
pref, Q = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":1150}, device_scale_factor=2, locale="pt-BR")
    pg=ctx.new_page()
    pg.goto(BASE+f"/selecoes/{E01}/", wait_until="networkidle")
    pg.click("text=Dúvidas sobre este Edital"); pg.wait_for_timeout(1000)
    ta=pg.query_selector("textarea"); ta.click(); ta.type(Q, delay=0)
    pg.screenshot(path=f"cap/{pref}_1_digitada.png"); boxes(pg, f"{pref}_1_digitada")
    pg.click("button:has-text('Enviar') >> nth=-1")
    pg.wait_for_timeout(500); pg.screenshot(path=f"cap/{pref}_2_espera.png"); boxes(pg, f"{pref}_2_espera")
    t0=time.time()
    while time.time()-t0 < 150:
        if "Consultando" not in panel_text(pg): break
        pg.wait_for_timeout(1500)
    pg.wait_for_timeout(1200)
    pg.screenshot(path=f"cap/{pref}_3_resposta.png"); boxes(pg, f"{pref}_3_resposta")
    print(f"== {pref} ({round(time.time()-t0)}s)\n", panel_text(pg).split("Ambiente local de desenvolvimento",1)[-1][:2200])
    det=pg.query_selector("text=Consultar fontes >> nth=-1")
    if det:
        det.click(); pg.wait_for_timeout(800)
        pg.screenshot(path=f"cap/{pref}_4_fontes.png"); boxes(pg, f"{pref}_4_fontes")
    b.close()
