import json, time
from playwright.sync_api import sync_playwright
BASE="http://localhost:8091"
E01="afaf823b-c183-4fd2-bd1a-07672bc3afa7"
PANEL="aside.painel-do-assistente, [class*=assistente][class*=painel], .painel"
def panel_text(pg):
    return pg.evaluate("""() => { const h=[...document.querySelectorAll('h2,h3,strong,p')].find(e=>e.innerText.trim()==='Assistente do edital');
      let p=h; for(let i=0;i<6&&p;i++){ if(p.getBoundingClientRect().height>600) break; p=p.parentElement }
      return p? p.innerText.slice(-1800):'' }""")
def boxes(pg, name):
    js="""() => [...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect(); return r.left>=980 && r.width>40 && r.height>12}).map(e=>{const r=e.getBoundingClientRect(); return [e.tagName.toLowerCase()+'.'+(typeof e.className=='string'?e.className.split(' ')[0]:''), (e.innerText||'').trim().replace(/\\s+/g,' ').slice(0,70), Math.round(r.left*2),Math.round(r.top*2),Math.round(r.width*2),Math.round(r.height*2)]})"""
    json.dump(pg.evaluate(js), open(f"cap/{name}.json","w"), ensure_ascii=False)
if __name__=="__main__":
  with sync_playwright() as p:
      b=p.chromium.launch(channel="chrome", headless=True)
      ctx=b.new_context(viewport={"width":1440,"height":900}, device_scale_factor=2, locale="pt-BR")
      pg=ctx.new_page()
      pg.goto(BASE+f"/selecoes/{E01}/", wait_until="networkidle")
      pg.click("text=Dúvidas sobre este Edital"); pg.wait_for_timeout(1000)
      pg.screenshot(path="cap/as_1_inicio.png"); boxes(pg,"as_1_inicio")
      pg.click("text=Que documentos preciso enviar?"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1200)
      pg.screenshot(path="cap/as_2_sugestao.png"); boxes(pg,"as_2_sugestao")
      print("== após sugestão\n", panel_text(pg)[-1500:])
      ctx.storage_state(path="state_as.json")
      b.close()
