import json
from capture import *
from playwright.sync_api import sync_playwright
E02="e84bb828-29fb-4914-a1d6-06ce9e6aa7e4"
FORMS="""[...document.querySelectorAll('main form')].map(f=>({action:f.getAttribute('action'),fields:[...f.elements].filter(e=>e.name&&e.type!='hidden').map(e=>e.tagName+':'+e.type+':'+e.name+'='+(e.value||'').slice(0,30)), buttons:[...f.querySelectorAll('button')].map(b=>b.name+'='+b.value+' «'+b.innerText.slice(0,40)+'»')}))"""
def ato(pg, who, papeis, acao, pref):
    login_gestao(pg, who, papeis)
    pg.goto(BASE+f"/gestao/editais/{E02}/atos/{acao}", wait_until="networkidle")
    print(acao, pg.url, json.dumps(pg.evaluate(FORMS), ensure_ascii=False)[:900])
    shoot(pg, f"{pref}_{acao}_confirmar", None, {"h1":"h1","btn":"main form button"})
    for f in pg.query_selector_all("main textarea, main input[type=text]"):
        f.fill("Conferido; segue para a próxima etapa.")
    for cb in pg.query_selector_all("main input[type=checkbox]"):
        cb.check()
    btn=pg.query_selector("main form button[type=submit]:not(.secundario)") or pg.query_selector("main form button")
    btn.click(); pg.wait_for_load_state("networkidle")
    print("  ->", pg.url, pg.title())
    shoot(pg, f"{pref}_{acao}_feito", None, {"h1":"h1"})
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    pg=b.new_page(viewport={"width":1440,"height":900}, device_scale_factor=2)
    shoot(pg, "pub_portal_antes", "/selecoes/", {"h1":"h1","cards":"article"})
    login_gestao(pg, "ana.elaboradora", ["elaborador"])
    shoot(pg, "pub_gestao_antes", f"/gestao/editais/{E02}/", {"h1":"h1"})
    ato(pg, "ana.elaboradora", ["elaborador"], "submeter", "pub")
    ato(pg, "bruno.homologador", ["homologador"], "homologar", "pub")
    ato(pg, "carla.publicadora", ["publicador"], "publicar", "pub")
    shoot(pg, "pub_gestao_depois", f"/gestao/editais/{E02}/", {"h1":"h1"})
    ctx2=b.new_context(viewport={"width":1440,"height":900}, device_scale_factor=2)
    q=ctx2.new_page()
    shoot(q, "pub_portal_depois", "/selecoes/", {"h1":"h1","cards":"article"})
    shoot(q, "pub_portal_edital02", f"/selecoes/{E02}/", {"h1":"h1"})
    b.close()
