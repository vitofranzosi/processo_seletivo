import json
from capture import *
from domboxes import JS
from playwright.sync_api import sync_playwright
E02="e84bb828-29fb-4914-a1d6-06ce9e6aa7e4"
res=json.load(open("dom.json"))
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    pg=b.new_page(viewport={"width":1440,"height":900}, device_scale_factor=2)
    pg.goto(BASE+"/selecoes/", wait_until="networkidle"); res["pub_portal_depois"]=pg.evaluate(JS)
    login_gestao(pg, "carla.publicadora", ["publicador"])
    pg.goto(BASE+f"/gestao/editais/{E02}/", wait_until="networkidle"); res["pub_gestao_depois"]=pg.evaluate(JS)
    b.close()
json.dump(res, open("dom.json","w"), ensure_ascii=False)
