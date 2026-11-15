"""Entra no portal como candidato fictício (código lido de um arquivo) e rastreia a área autenticada por GET."""
import json, re, sys, time, pathlib, collections
from playwright.sync_api import sync_playwright
S = pathlib.Path(sys.argv[1]); BASE = "http://localhost:8165"; emails = sys.argv[2:]
JS = (S / "metricas.js").read_text()
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
EVITAR = re.compile(r"/sair|\.pdf|/arquivo|\.json|/apresentacoes/|/documentos/|/remover|/principal|/static/|/gestao|/retomar")
def padrao(u):
    path, _, q = u.partition("?"); path = UUID.sub("<id>", path)
    ch = sorted({kv.split("=")[0] for kv in q.split("&") if kv}) if q else []
    return path + ("?" + "&".join(ch) if ch else "")
with sync_playwright() as p:
    b = p.chromium.launch()
    for i, email in enumerate(emails):
        tag = "cand" + str(i + 1); out = S / "cap" / tag; out.mkdir(parents=True, exist_ok=True)
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="pt-BR"); pg = ctx.new_page()
        pg.goto(BASE + "/selecoes/acesso"); pg.fill("#email", email); pg.locator("#email").locator("xpath=ancestor::form").locator("button[type=submit]").first.click(); pg.wait_for_load_state("load")
        m = pg.evaluate(JS); m.update(padrao="/selecoes/acesso/codigo", ident=tag, status=200, n=1, captura=f"{tag}/selecoes-acesso-codigo--1.png"); pg.screenshot(path=str(out / "selecoes-acesso-codigo--1.png"), full_page=True)
        res = [m]
        (S / f"pedido-{tag}.txt").write_text(email); arq = S / f"codigo-{tag}.txt"
        for _ in range(600):
            if arq.exists(): break
            time.sleep(1)
        pg.fill("#codigo", arq.read_text().strip()); pg.locator("#codigo").locator("xpath=ancestor::form").locator("button[type=submit]").first.click(); pg.wait_for_load_state("load")
        print(tag, email, "->", pg.url, flush=True)
        fila = collections.deque([pg.url.replace(BASE, ""), "/selecoes/inscricoes/", "/selecoes/conta", "/selecoes/meus-dados", "/selecoes/"]); vistos = set(); cont = collections.Counter()
        while fila and len(res) < 45:
            u = fila.popleft()
            if u in vistos or EVITAR.search(u): continue
            vistos.add(u); k = padrao(u)
            if cont[k] >= 2: continue
            try: r = pg.goto(BASE + u, wait_until="load", timeout=20000)
            except Exception as e: continue
            if not r or "html" not in r.headers.get("content-type", ""): continue
            kf = padrao(pg.url.replace(BASE, ""))
            if cont[kf] >= 2: continue
            m = pg.evaluate(JS); cont[kf] += 1; nome = re.sub(r"[^a-z0-9]+", "-", kf.lower()).strip("-")[:90] or "raiz"
            m.update(padrao=kf, pedido=u, status=r.status, ident=tag, n=cont[kf], captura=f"{tag}/{nome}--{cont[kf]}.png")
            pg.screenshot(path=str(out / f"{nome}--{cont[kf]}.png"), full_page=True); res.append(m)
            for h in m.pop("linksAbs", []):
                h = h.split("#")[0]
                if h.startswith("/selecoes") and h not in vistos: fila.append(h)
            m.pop("links", None)
        ctx.storage_state(path=str(S / f"estado-{tag}.json"))
        json.dump(res, open(S / f"rastreio-{tag}.json", "w"), ensure_ascii=False)
        print(tag, len(res), "telas;", sorted(cont), flush=True); ctx.close()
    b.close()
