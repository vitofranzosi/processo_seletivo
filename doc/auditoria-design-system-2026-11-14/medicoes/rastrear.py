"""Rastreia a aplicação por GET, mede cada tela e grava capturas. Só leitura: nenhum POST além do login."""
import json, re, sys, time, pathlib, collections
from playwright.sync_api import sync_playwright
S = pathlib.Path(sys.argv[1]); BASE = "http://localhost:8165"
ident, papeis, inicio, limite = sys.argv[2], [p for p in sys.argv[3].split(",") if p], sys.argv[4].split(","), int(sys.argv[5])
POR_PADRAO = int(sys.argv[6]) if len(sys.argv) > 6 else 3
JS = (S / "metricas.js").read_text()
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
EVITAR = re.compile(r"/sair|\.pdf|/pdf$|/exportar|/baixar|/arquivo|\.png|\.json|/documento$|/documentos/[^/]+/[0-9a-f-]{36}$|/apresentacoes/|/instrucao/|/api/|/static/|/health|/metrics|/readiness|/unidade-ativa|/anexos/")
def padrao(u):
    path, _, q = u.partition("?")
    path = UUID.sub("<id>", path)
    chaves = sorted({kv.split("=")[0] for kv in q.split("&") if kv}) if q else []
    return path + ("?" + "&".join(chaves) if chaves else "")
out = S / "cap" / ident.replace(".", "_"); out.mkdir(parents=True, exist_ok=True)
res, vistos, por_padrao = [], set(), collections.Counter()
fila = collections.deque(inicio)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1, locale="pt-BR")
    pg = ctx.new_page()
    if ident != "anonimo":
        pg.goto(BASE + "/gestao/identificar/demonstracao")
        pg.evaluate("document.querySelector('details.avancado').open = true")
        pg.fill("#subject", ident)
        for pp in papeis: pg.check(f"input[type=checkbox][name=papeis][value='{pp}']")
        pg.locator("#subject").locator("xpath=ancestor::form").locator("button[type=submit]").click()
        pg.wait_for_load_state("networkidle"); print("login ->", pg.url, file=sys.stderr)
    while fila and len(res) < limite:
        u = fila.popleft()
        if u in vistos or EVITAR.search(u): continue
        vistos.add(u); k = padrao(u)
        if por_padrao[k] >= (40 if k.endswith("/centro/") or "/compor/" in k else POR_PADRAO): continue
        try:
            r = pg.goto(BASE + u, wait_until="load", timeout=20000)
        except Exception as e:
            res.append({"url": u, "padrao": k, "erro": str(e)[:120]}); continue
        st = r.status if r else None
        final = pg.url.replace(BASE, "")
        ct = (r.headers.get("content-type", "") if r else "")
        if "html" not in ct: res.append({"url": u, "padrao": k, "status": st, "naoHtml": ct}); continue
        kf = padrao(final)
        if kf != k and por_padrao[kf] >= POR_PADRAO: continue
        try: m = pg.evaluate(JS)
        except Exception as e: res.append({"url": u, "padrao": k, "erro": "js " + str(e)[:160]}); continue
        por_padrao[kf] += 1; n = por_padrao[kf]
        m.update(padrao=kf, pedido=u, status=st, ident=ident, n=n)
        nome = re.sub(r"[^a-z0-9]+", "-", kf.lower()).strip("-")[:90] or "raiz"
        m["captura"] = f"{out.name}/{nome}--{n}.png"
        try: pg.screenshot(path=str(out / f"{nome}--{n}.png"), full_page=True)
        except Exception as e: m["captura"] = None
        res.append(m)
        if st and st < 400:
            for h in m.pop("linksAbs", []):
                h = h.split("#")[0]
                if h and h not in vistos and (h.startswith("/gestao") or h.startswith("/selecoes")): fila.append(h)
        m.pop("links", None)
    b.close()
json.dump(res, open(S / f"rastreio-{ident.replace('.', '_')}.json", "w"), ensure_ascii=False)
ok = [r for r in res if r.get("status")]
print(len(res), "visitas;", len({r["padrao"] for r in ok}), "padrões;", collections.Counter(r.get("status") for r in res), "fila restante", len(fila))
