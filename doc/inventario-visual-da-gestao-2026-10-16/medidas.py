"""Diferenças campo a campo entre dois resultados.json: largura, altura, título e h1.

O `comparar.py` só acusa `status` e estouro. A 078 e a 079 precisavam provar também que fora das
telas delas nenhuma variante mudou de medida, e faziam a conta à mão; esta é a conta, escrita.
"""

import json
import os
import sys

# `estilos` (089) é o resumo das regras que a página aplica, quando a captura rodou com `ESTILOS=1`.
# `CAMPOS` pode ser trocado por `MEDIDAS_CAMPOS=scrollWidth,altura,conjunto` (091): a divisão da
# folha muda a sequência das regras (`estilos`) de propósito, e o que tem de ficar igual é o conjunto.
CAMPOS = tuple(
    filter(None, os.environ.get("MEDIDAS_CAMPOS", "").split(","))
) or ("scrollWidth", "altura", "titulo", "h1", "estilos", "conjunto", "violacoes")

base = {r["id"]: r for r in json.load(open(sys.argv[1]))}
nova = {r["id"]: r for r in json.load(open(sys.argv[2]))}

mudou = []
for rid in sorted(set(base) & set(nova)):
    for largura in ("375", "1280"):
        a, b = base[rid].get(largura) or {}, nova[rid].get(largura) or {}
        diferencas = {k: (a.get(k), b.get(k)) for k in CAMPOS if a.get(k) != b.get(k)}
        if diferencas:
            mudou.append((rid, largura, diferencas))

for linha in mudou:
    print(*linha)
print("variantes que mudaram:", len(mudou), sorted({rid for rid, _, _ in mudou}))
