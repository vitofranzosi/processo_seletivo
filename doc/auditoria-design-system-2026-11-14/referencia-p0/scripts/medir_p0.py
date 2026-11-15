"""Sonda da P0: Visão Geral e as confirmações de ato, nas cinco larguras do estudo.
Usa metricas.js e largura.js do estudo sem alteração; acrescenta só um diagnóstico de qual
elemento dá a linha mais longa. Só GET, além do POST da entrada."""
import json, re, sys, pathlib, collections
from playwright.sync_api import sync_playwright
M = pathlib.Path(sys.argv[1]); IDS = json.load(open(sys.argv[2])); SAIDA = pathlib.Path(sys.argv[3])
BASE = "http://localhost:8165"
METRICAS = (M / "metricas.js").read_text(); LARGURA = (M / "largura.js").read_text()
DIAG = """() => [...document.querySelectorAll('main p, main li, main dd, main td, main .sub, main .ajuda, main .nota, main .explicacao')]
  .filter(e => e.getBoundingClientRect().width > 1 && e.innerText && e.innerText.length > 160 && !e.querySelector('p, ul, table, input, select'))
  .map(e => { const s = getComputedStyle(e); const lh = parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.5;
    const l = Math.max(1, Math.round(e.getBoundingClientRect().height / lh));
    let p = e, cam = []; while (p && p.tagName !== 'MAIN') { cam.unshift(p.tagName.toLowerCase() + (p.className ? '.' + String(p.className).trim().split(/\\s+/).join('.') : '')); p = p.parentElement; }
    return [Math.round(e.innerText.length / l), cam.join('>'), e.innerText.slice(0, 50)]; })
  .filter(x => x[0] > 100).sort((a, b) => b[0] - a[0]).slice(0, 4)"""
T = "elaborador,homologador,publicador,gestor,julgador,auditor,exportador,comunicacao,formalizacao,participante-piloto-assistente".split(",")
urls = ["/gestao/visao-geral", "/gestao/visao-geral?ano=todos"]
for e in IDS["editais"]:
    urls += [f"/gestao/editais/{e}/atos/{a}" for a in ("submeter", "homologar", "devolver", "publicar", "encerrar", "cancelar")]
for p in IDS["processos"]:
    urls += [f"/gestao/processos/{p}/atos/{a}" for a in ("encerrar", "cancelar", "ativar")]
for r in IDS["retificacoes"]:
    urls += [f"/gestao/retificacoes/{r}/atos/{a}" for a in ("submeter", "cancelar", "homologar", "publicar")]
LARG = [(375, 812), (768, 1024), (1280, 800), (1440, 900), (1920, 1080)]
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
res = []
with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="pt-BR"); pg = ctx.new_page()
    pg.goto(BASE + "/gestao/identificar/demonstracao"); pg.evaluate("document.querySelector('details.avancado').open = true"); pg.fill("#subject", "treino.presidencia")
    for pp in T: pg.check(f"input[type=checkbox][name=papeis][value='{pp}']")
    pg.locator("#subject").locator("xpath=ancestor::form").locator("button[type=submit]").click(); pg.wait_for_load_state("load")
    for u in urls:
        item = {"url": u, "padrao": re.sub(UUID, "<id>", u), "w": {}}
        for (w, h) in LARG:
            pg.set_viewport_size({"width": w, "height": h})
            r = pg.goto(BASE + u, wait_until="load", timeout=20000)
            item["status"] = r.status if r else None
            if not r or "html" not in r.headers.get("content-type", ""): break
            m = pg.evaluate(LARGURA) or {}
            m["diag"] = pg.evaluate(DIAG)
            if w == 1440:
                mm = pg.evaluate(METRICAS); m["contraste"] = mm["contrasteBaixo"]; m["linhasLongas"] = mm["linhasLongas"]
                m["avisos"] = mm["avisos"]
            item["w"][w] = m
        res.append(item)
    b.close()
json.dump(res, open(SAIDA, "w"), ensure_ascii=False, indent=1)
por = collections.defaultdict(list)
for r in res:
    if r.get("status") == 200 and r["w"]: por[r["padrao"]].append(r)
print(f"{'padrão':55} n  contr  transb768 transb375  cpl1280 cpl1440 cpl1920")
for k, rs in sorted(por.items()):
    g = lambda w, f: max((x["w"].get(w, {}).get(f) or 0) for x in rs)
    t = lambda w: sum(1 for x in rs if x["w"].get(w, {}).get("overflowX"))
    print(f"{k[:55]:55} {len(rs):2} {g(1440,'contraste') if False else max(x['w'][1440]['contraste']['n'] for x in rs):5}  {t(768):9} {t(375):9}  {g(1280,'cplMax'):7} {g(1440,'cplMax'):7} {g(1920,'cplMax'):7}")
