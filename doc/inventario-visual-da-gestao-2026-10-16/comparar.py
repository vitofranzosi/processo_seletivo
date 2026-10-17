"""Compara dois resultados.json do inventário visual, tela a tela."""

import json
import sys

base = {r["id"]: r for r in json.load(open(sys.argv[1]))}
nova = {r["id"]: r for r in json.load(open(sys.argv[2]))}


def estouro(r, largura):
    m = r.get(largura) or {}
    if "scrollWidth" not in m:
        return None
    return m["scrollWidth"] - m["clientWidth"]


problemas = []
linhas = []
for rid in sorted(set(base) | set(nova)):
    a, b = base.get(rid), nova.get(rid)
    if a is None or b is None:
        problemas.append(f"{rid}: só em {'base' if b is None else 'nova'}")
        continue
    sa, sb = a.get("status"), b.get("status")
    linha = [rid, sa, sb]
    if sa != sb:
        problemas.append(f"{rid}: status {sa} -> {sb}")
    for largura in ("375", "1280"):
        ea, eb = estouro(a, largura), estouro(b, largura)
        linha += [ea, eb]
        if eb is None and ea is not None:
            problemas.append(f"{rid}@{largura}: deixou de medir")
        elif eb is not None and eb > max(ea or 0, 0):
            problemas.append(f"{rid}@{largura}: estouro {ea} -> {eb} {b[largura].get('culpados')}")
    linhas.append(linha)

capturadas = sum(1 for r in nova.values() if (r.get("375") or {}).get("scrollWidth"))
print(f"telas: base {len(base)}, nova {len(nova)}; capturadas na nova: {capturadas}")
estouram = {
    w: [rid for rid, r in nova.items() if (estouro(r, w) or 0) > 0] for w in ("375", "1280")
}
print("estouram na nova:", {w: [(rid, estouro(nova[rid], w)) for rid in v] for w, v in estouram.items()})
print("problemas:", problemas or "nenhum")
