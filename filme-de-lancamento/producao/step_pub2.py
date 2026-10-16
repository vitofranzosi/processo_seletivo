from capture import *
from playwright.sync_api import sync_playwright
E02="e84bb828-29fb-4914-a1d6-06ce9e6aa7e4"
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    pg=b.new_page(viewport={"width":1440,"height":900}, device_scale_factor=2)
    login_gestao(pg, "carla.publicadora", ["publicador"])
    pg.goto(BASE+f"/gestao/editais/{E02}/atos/publicar", wait_until="networkidle")
    print(pg.evaluate("[...document.querySelectorAll('select[name=signatario] option')].map(o=>o.value+'|'+o.text)"))
    pg.select_option("select[name=signatario]", index=1)
    shoot(pg, "pub_publicar_confirmar", None, {"h1":"h1","btn":"main form button","sel":"select[name=signatario]"})
    pg.click("button:has-text('Confirmar: Publicar')"); pg.wait_for_load_state("networkidle")
    print("->", pg.url)
    shoot(pg, "pub_publicar_feito", None, {"h1":"h1"})
    shoot(pg, "pub_gestao_depois", f"/gestao/editais/{E02}/", {"h1":"h1"})
    q=b.new_context(viewport={"width":1440,"height":900}, device_scale_factor=2).new_page()
    shoot(q, "pub_portal_depois", "/selecoes/", {"h1":"h1","cards":"article"})
    shoot(q, "pub_portal_edital02", f"/selecoes/{E02}/", {"h1":"h1"})
    b.close()
