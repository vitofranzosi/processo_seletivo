import json
from playwright.sync_api import sync_playwright
from as_flow import BASE, E01, boxes
OPT="button:has-text('Professor de Informática — Campus Serra')"
def flow(pg, pref, fontes=True):
    pg.goto(BASE+f"/selecoes/{E01}/", wait_until="networkidle")
    pg.screenshot(path=f"cap/{pref}_0_pagina.png")
    pg.click("text=Dúvidas sobre este Edital"); pg.wait_for_timeout(1000)
    pg.screenshot(path=f"cap/{pref}_1_inicio.png"); boxes(pg, f"{pref}_1_inicio")
    pg.click("text=Que documentos preciso enviar?"); pg.wait_for_timeout(1500)
    pg.screenshot(path=f"cap/{pref}_2_opcao.png"); boxes(pg, f"{pref}_2_opcao")
    pg.click(OPT); pg.wait_for_timeout(1800)
    pg.screenshot(path=f"cap/{pref}_3_resposta.png"); boxes(pg, f"{pref}_3_resposta")
    if fontes:
        pg.click("text=Consultar fontes >> nth=-1"); pg.wait_for_timeout(900)
        pg.screenshot(path=f"cap/{pref}_4_fontes.png"); boxes(pg, f"{pref}_4_fontes")
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":1150}, device_scale_factor=2, locale="pt-BR")
    flow(ctx.new_page(), "asd")
    m=b.new_context(viewport={"width":390,"height":844}, device_scale_factor=3, locale="pt-BR", is_mobile=True, has_touch=True)
    flow(m.new_page(), "asm")
    b.close()
