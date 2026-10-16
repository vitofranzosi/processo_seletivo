from capture import *
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":900}, device_scale_factor=2, accept_downloads=True)
    pg=ctx.new_page()
    login_gestao(pg, "gustavo.gestor", ["gestor","exportador"])
    pg.goto(BASE+f"/gestao/editais/{E51}/matriculas?populacao=CONVOCACAO%3A{M51}", wait_until="networkidle")
    with pg.expect_download() as d:
        pg.click("button:has-text('Baixar o arquivo')")
    d.value.save_as("matriculas51.xlsx"); print(d.value.suggested_filename)
    b.close()
