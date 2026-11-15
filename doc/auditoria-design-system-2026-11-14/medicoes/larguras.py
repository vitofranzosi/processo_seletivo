"""Segunda passada: cada tela representativa em 375, 768, 1280, 1440 e 1920, medindo a extensão do conteúdo."""
import json, sys, pathlib, collections, re
from playwright.sync_api import sync_playwright
S = pathlib.Path(sys.argv[1]); BASE = "http://localhost:8165"; JS = (S / "largura.js").read_text()
rep = json.load(open(S / "representantes.json"))
for f in S.glob("rastreio-cand*.json"):
    for r in json.load(open(f)):
        if r.get("status") == 200 and "main" in r and r["padrao"] not in rep: rep[r["padrao"]] = r
T = "elaborador,homologador,publicador,gestor,julgador,auditor,exportador,comunicacao,formalizacao,participante-piloto-assistente".split(",")
PAPEIS = {"treino.presidencia": T, "paulo.presidente": T, "treino.avaliacao1": [], "treino.formalizacao": ["formalizacao"]}
LARG = [(375, 812), (768, 1024), (1280, 800), (1440, 900), (1920, 1080)]
CAP = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else set()
por_ident = collections.defaultdict(list)
for k, r in rep.items(): por_ident[r["ident"]].append((k, r))
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for ident, itens in por_ident.items():
        est = S / f"estado-{ident}.json"
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="pt-BR", storage_state=str(est) if est.exists() else None); pg = ctx.new_page()
        if ident in PAPEIS:
            pg.goto(BASE + "/gestao/identificar/demonstracao"); pg.evaluate("document.querySelector('details.avancado').open = true"); pg.fill("#subject", ident)
            for pp in PAPEIS[ident]: pg.check(f"input[type=checkbox][name=papeis][value='{pp}']")
            pg.locator("#subject").locator("xpath=ancestor::form").locator("button[type=submit]").click(); pg.wait_for_load_state("load")
        for k, r in itens:
            url = r.get("pedido") or r["url"]; res[k] = {"ident": ident, "url": url, "w": {}}
            for (w, h) in LARG:
                pg.set_viewport_size({"width": w, "height": h})
                try:
                    pg.goto(BASE + url, wait_until="load", timeout=20000); m = pg.evaluate(JS)
                except Exception as e: m = {"erro": str(e)[:100]}
                res[k]["w"][w] = m
                nome = re.sub(r"[^a-z0-9]+", "-", k.lower()).strip("-")[:80] or "raiz"
                if w in (375, 1920) and (not CAP or any(c in k for c in CAP)):
                    d = S / "cap" / f"w{w}"; d.mkdir(exist_ok=True); pg.screenshot(path=str(d / f"{nome}.png"), full_page=(w == 375))
        ctx.close(); print(ident, len(itens), flush=True)
    b.close()
json.dump(res, open(S / "larguras.json", "w"), ensure_ascii=False)
