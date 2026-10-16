from playwright.sync_api import sync_playwright
from as_flow import BASE, E01
Q="Preciso ter mestrado para a vaga de professor?"
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    pg=b.new_context(viewport={"width":1440,"height":1150}, device_scale_factor=2, locale="pt-BR").new_page()
    pg.goto(BASE+f"/selecoes/{E01}/", wait_until="networkidle")
    pg.click("text=Dúvidas sobre este Edital"); pg.wait_for_timeout(900)
    ta=pg.query_selector("textarea"); ta.click()
    steps=[0,8,16,24,32,40,len(Q)]
    for i,n in enumerate(steps):
        ta.fill(Q[:n]); pg.wait_for_timeout(150)
        pg.screenshot(path=f"cap/al1_typ{i}.png", clip={"x":993,"y":1000,"width":447,"height":150})
    b.close()
