"""Do HTML montado, o CSV tela a tela e a tabela por família do README.

    python resumir.py <antes-e-depois.html> <telas-comparadas.csv>
"""
import collections, csv, json, re, sys

html, saida = sys.argv[1:3]
est = json.loads(re.search(r"const ESTADOS = (\[.*?\]);\n", open(html).read(), re.S).group(1))
with open(saida, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["tela", "familia", "area", "identidade", "situacao", "pixels_mudados_pct",
                "altura_1440_antes", "altura_1440_depois", "altura_375_antes", "altura_375_depois",
                "cpl_1920_antes", "cpl_1920_depois"])
    for e in est:
        m = e["medidas"]
        w.writerow([e["tela"], e["familia"], e["area"], e["identidade"], e["situacao"],
                    round((e["diferenca"] or 0) * 100, 2), *m["altura"], *m["altura375"], *m["cpl1920"]])
fam = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
for e in est:
    (a, d), (a3, d3), f = e["medidas"]["altura"], e["medidas"]["altura375"], fam[e["familia"]]
    f[0] += 1; f[1] += e["situacao"] != "igual"; f[2] += a; f[3] += d; f[4] += (d3 - a3) > 40
print("| Família | Telas | Mudaram | Altura somada a 1440 px | Mais altas no celular |")
print("|---|---:|---:|---|---:|")
for k, (n, mud, a, d, cel) in fam.items():
    pt = lambda v: f"{v:,}".replace(",", ".")
    dif = f"{(d - a) / a * 100:+.1f}".replace(".", ",")
    print(f"| {k} | {n} | {mud} | {pt(a)} → {pt(d)} px ({dif}%) | {cel} |")
