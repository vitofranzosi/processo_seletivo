"""Compara uma seção do Edital 19/2026 com a mesma seção do 46/2026 (comparação focalizada, rodada 4).

O `pdftotext` perde espaços em parte do 19/2026; por isso a comparação é feita sem espaços e sem caixa. O resultado
diz onde a letra difere; o que a diferença significa está em `comparacao-focalizada/`.

Uso, da raiz do repositório:  python3 docs/libras/ferramentas/comparar_secoes.py
"""

import difflib
import re
import subprocess
from pathlib import Path

FONTES = Path(__file__).resolve().parent.parent / "comparacao-focalizada" / "fontes"
E19 = FONTES / "edital-19-2026" / "edital-2026-04-01.pdf"
E46 = FONTES / "edital-46-2026" / "edital-consolidado-2026-09-14.pdf"
SECOES = [
    ("3 — Etapa Inscrição", r"\n\s*3\.\s*ETAPA INSCRI", r"\n\s*4\.\s*PROVA"),
    ("9 — Eliminação", r"\n\s*9\.\s*ELIMINA", r"\n\s*10\.\s*MATR"),
]


def texto(pdf):
    t = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    return t.replace("​", "")


def secao(t, ini, fim):
    a = re.search(ini, t).start()
    b = re.search(fim, t[a + 5 :]).start() + a + 5
    return re.sub(r"\s", "", t[a:b].lower())


t19, t46 = texto(E19), texto(E46)
for nome, ini, fim in SECOES:
    a, b = secao(t19, ini, fim), secao(t46, ini, fim)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    print(f"== §{nome}: razão (sem espaços) {sm.ratio():.3f}")
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != "equal":
            print(f"   {op}: «{a[max(0, i1 - 40) : i2 + 20]}» → «{b[max(0, j1 - 40) : j2 + 20]}»")
