import json, re, sys, pathlib, collections, glob
from playwright.sync_api import sync_playwright
S = pathlib.Path(sys.argv[1]); BASE = "http://localhost:8165"; JS = (S / "metricas.js").read_text()
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
urls = set()
for f in glob.glob(str(S / "rastreio-treino_presidencia.json")) + glob.glob(str(S / "rastreio-paulo_presidente.json")):
    for r in json.load(open(f)):
        if r.get("status") == 200: urls.add(r["url"].split("?")[0])
cand = collections.OrderedDict()
def add(u): cand.setdefault(u, None)
for u in sorted(urls):
    m = re.fullmatch(rf"(/gestao/editais/{UUID}/marcos/{UUID})(/.*)?", u)
    if m:
        for s in ["/emitir", "/corte/emitir", "/corte/continuar", "/ocupacao/acrescentar-vagas", "/ocupacao/desfazer-acrescimo", "/ocupacao/declarar-nao-preenchida", "/ocupacao/desfazer-nao-preenchida", "/convocacao/convocar", "/convocacao/titulares", "/convocacao/avisos/novo", "/avisos/novo", "/conducao", "/publicacoes", "/sorteio", "/corte", "/ocupacao", "/convocacao"]: add(m.group(1) + s)
    m = re.fullmatch(rf"(/gestao/editais/{UUID}/distribuicao/{UUID})(/.*)?", u)
    if m:
        for s in ["/consolidar", "/remover"]: add(m.group(1) + s)
    m = re.fullmatch(rf"(/gestao/processos/{UUID})/.*", u) or re.fullmatch(rf"(/gestao/processos/{UUID})/?", u)
    if m:
        for s in ["/atos/encerrar", "/atos/cancelar", "/atos/ativar"]: add(m.group(1) + s)
    m = re.fullmatch(rf"(/gestao/editais/{UUID})/.*", u)
    if m:
        for s in ["/matriculas", "/assistente/", "/atos/homologar", "/atos/publicar", "/atos/devolver", "/formalizacao"]: add(m.group(1) + s)
    m = re.fullmatch(rf"(/gestao/retificacoes/{UUID})/?", u)
    if m:
        for s in ["/editar", "/atos/submeter", "/atos/cancelar", "/atos/homologar", "/atos/publicar"]: add(m.group(1) + s)
    m = re.fullmatch(rf"(/gestao/recursos/{UUID})", u)
    if m:
        for s in ["/admitir", "/julgar", "/instruir"]: add(m.group(1) + s)
for u in ["/gestao/sem-acesso", "/gestao/acessos", "/gestao/administracao-de-acessos", "/gestao/administracao-de-unidades", "/gestao/acessos/formalizacao", "/gestao/visao-geral/relatorio/conjunto", "/selecoes/sorteio/73efe54e-0a5a-4ca2-b9cc-49294412d269/verificar", "/gestao/nao-existe", "/selecoes/00000000-0000-0000-0000-000000000000/"]: add(u)
def padrao(u): return re.sub(UUID, "<id>", u)
T = "elaborador,homologador,publicador,gestor,julgador,auditor,exportador,comunicacao,formalizacao,participante-piloto-assistente".split(",")
res, cont, st = [], collections.Counter(), collections.Counter()
out = S / "cap" / "complemento"; out.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="pt-BR"); pg = ctx.new_page()
    pg.goto(BASE + "/gestao/identificar/demonstracao"); pg.evaluate("document.querySelector('details.avancado').open = true"); pg.fill("#subject", "treino.presidencia")
    for pp in T: pg.check(f"input[type=checkbox][name=papeis][value='{pp}']")
    pg.locator("#subject").locator("xpath=ancestor::form").locator("button[type=submit]").click(); pg.wait_for_load_state("load")
    for u in cand:
        k = padrao(u)
        if cont[k] >= 2: continue
        try: r = pg.goto(BASE + u, wait_until="load", timeout=15000)
        except Exception as e: st[(k, "erro")] += 1; continue
        kf = padrao(pg.url.replace(BASE, "").split("?")[0]); s = r.status if r else None
        st[(k, s, kf if kf != k else "")] += 1
        if not r or "html" not in r.headers.get("content-type", ""): continue
        if s == 200 and kf != k: continue  # redirecionou para tela já vista
        try: m = pg.evaluate(JS)
        except Exception: continue
        if "main" not in m and s == 200: pass
        cont[k] += 1; nome = re.sub(r"[^a-z0-9]+", "-", k.lower()).strip("-")[:90]
        m.update(padrao=k, pedido=u, status=s, ident="complemento", n=cont[k], captura=f"complemento/{nome}--{cont[k]}.png"); m.pop("links", None); m.pop("linksAbs", None)
        pg.screenshot(path=str(out / f"{nome}--{cont[k]}.png"), full_page=True); res.append(m)
    b.close()
json.dump(res, open(S / "rastreio-complemento.json", "w"), ensure_ascii=False)
agg = collections.defaultdict(collections.Counter)
for (k, *rest), n in st.items(): agg[k][tuple(rest)] += n
for k in sorted(agg): print(k, dict(agg[k]))
