import json
from capture import *
from domboxes import JS
from playwright.sync_api import sync_playwright
URL=f"/gestao/minhas-etapas/{E51}/00000000-0000-0000-0051-0000000000d1/inscricoes/4a64c39e-e9de-468f-a477-6de0d28cb69d"
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    pg=b.new_page(viewport={"width":1440,"height":900}, device_scale_factor=2)
    login_gestao(pg, "joana.avaliadora", [])
    pg.goto(BASE+URL, wait_until="networkidle")
    shoot(pg, "av_doc_0_fechado", None, {"h1":"h1"})
    links=pg.evaluate("[...document.querySelectorAll('main a, main button')].map(a=>[a.innerText.trim(), a.getAttribute('href')||'', a.closest('li')?a.closest('li').innerText.slice(0,40):''])")
    print([l for l in links if 'Abrir' in l[0]])
    btn=pg.query_selector("li:has-text('Diploma de graduação') >> text=Abrir")
    btn.click(); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2500)
    pg.goto(BASE+URL, wait_until="networkidle")   # a consulta fica registrada: "1 de 2 abertos", "aberto"
    pg.query_selector("li:has-text('Diploma de graduação') >> text=Abrir").click()
    pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2500)
    print("url", pg.url)
    shoot(pg, "av_doc_1_aberto", None, {"h1":"h1"}, full=True, wait=1500)
    d=json.load(open("dom.json")); d["av_doc_1_aberto"]=pg.evaluate(JS); json.dump(d,open("dom.json","w"),ensure_ascii=False)
    b.close()
