"""Sondagem de recorrência de frases entre editais reais (viabilidade.md, §3).

Entrada: os PDFs listados em `referencia/sondagem-entrada.json`, procurados na pasta dada como argumento
(padrão: ~/Downloads). **Não estão no repositório.** Dependência: `pdftotext` (poppler).
Uso:  python3 docs/libras/ferramentas/sondagem_editais_reais.py [pasta-dos-pdfs]

Método: frases de 6 ou mais palavras, normalizadas (minúsculas, algarismos trocados por #, pontuação
retirada); uma frase é “recorrente” se ≥ 80% das suas sequências de quatro palavras aparecem em outro
edital, e “exata” se todas aparecem. Repetido excluindo editais da mesma família. Mede texto, não sentido.
"""

import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENTRADA = json.loads((AQUI / "referencia" / "sondagem-entrada.json").read_text(encoding="utf-8"))["editais"]
PASTA = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path("~/Downloads").expanduser()


def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"\d+", "#", s)
    s = re.sub(r"[^\wà-ú# ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def frases(txt):
    txt = re.sub(r"\s+", " ", re.sub(r"-\n", "", txt))
    partes = re.split(r"(?<=[.;:])\s+(?=[A-ZÀ-Ú0-9a-z(])", txt)
    return [(p.strip(), n) for p in partes if len((n := norm(p)).split()) >= 6]


def quadrigramas(n, k=4):
    w = n.split()
    return {tuple(w[i : i + k]) for i in range(max(1, len(w) - k + 1))}


docs, familia, faltam = {}, {}, []
for item in ENTRADA:
    arquivo = PASTA / item["arquivo"]
    if not arquivo.exists():
        faltam.append(item["arquivo"])
        continue
    texto = subprocess.run(["pdftotext", "-layout", str(arquivo), "-"], capture_output=True, text=True).stdout
    if len(texto.split()) < 200:  # digitalização sem camada de texto
        print(f"fora (sem texto extraível): {item['edital']}")
        continue
    docs[item["edital"]], familia[item["edital"]] = frases(texto), item["familia"]
if faltam:
    print("arquivos não encontrados:", *faltam, sep="\n  ")

indice, sh = defaultdict(set), {}
for d, fs in docs.items():
    for i, (_, n) in enumerate(fs):
        sh[(d, i)] = quadrigramas(n)
        for g in sh[(d, i)]:
            indice[g].add(d)

print("| Edital | Palavras | Exata em outro | ≥ 80% em outro | ≥ 80% em outra família |")
print("|---|---|---|---|---|")
somas = Counter()
for d, fs in docs.items():
    tot = exata = aprox = outra = 0
    for i, (_, n) in enumerate(fs):
        w, s = len(n.split()), sh[(d, i)]
        cand = Counter(o for g in s for o in indice[g] if o != d)
        melhor = max((c / len(s) for c in cand.values()), default=0)
        melhor_outra = max(
            (c / len(s) for o, c in cand.items() if familia[o] is None or familia[o] != familia[d]), default=0
        )
        tot += w
        exata += w if melhor >= 0.999 else 0
        aprox += w if melhor >= 0.8 else 0
        outra += w if melhor_outra >= 0.8 else 0
    somas.update(tot=tot, exata=exata, aprox=aprox, outra=outra)
    print(f"| {d} | {tot} | {exata / tot:.0%} | {aprox / tot:.0%} | {outra / tot:.0%} |")
t = somas["tot"]
print(
    f"| **Total ({len(docs)} editais)** | **{t}** | **{somas['exata'] / t:.0%}** | **{somas['aprox'] / t:.0%}** | **{somas['outra'] / t:.0%}** |"
)
