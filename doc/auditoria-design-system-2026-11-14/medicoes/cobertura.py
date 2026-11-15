import json, glob, os, collections
from django.urls import resolve
S = os.environ["SCR"]
inv = json.load(open(f"{S}/inventario.json"))
vis = []
for f in sorted(glob.glob(f"{S}/rastreio-*.json")): vis += [r for r in json.load(open(f)) if r.get("status") == 200 and "main" in r]
vistas = collections.defaultdict(lambda: collections.defaultdict(set))
for r in vis:
    try: m = resolve(r["url"].split("?")[0])
    except Exception: continue
    vistas[m.route][r["ident"]].add(r["padrao"])
out = []
for o in inv:
    rota = o["rota"].lstrip("/")
    v = vistas.get(rota, {})
    o["vista_por"] = sorted(v); o["estados"] = sorted({p for s in v.values() for p in s})
    out.append(o)
json.dump(out, open(f"{S}/inventario-coberto.json", "w"), ensure_ascii=False, indent=1)
tela = [o for o in out if o["templates"] and not all(t.split("/")[-1].startswith("_") for t in o["templates"]) and "api" not in o["modulo"]]
ok = [o for o in tela if o["vista_por"]]
print(len(out), "rotas;", len(tela), "rotas que rendem tela;", len(ok), "vistas no navegador")
print("\nNÃO VISTAS:")
for o in tela:
    if not o["vista_por"]: print("  ", o["rota"], "→", ",".join(t.split("/")[-1] for t in o["templates"]))
tv = {t for o in ok for t in o["templates"]}; tn = {t for o in tela for t in o["templates"]} - tv
print("\ntemplates só em rotas não vistas:", sorted(t.split("/")[-1] for t in tn))
