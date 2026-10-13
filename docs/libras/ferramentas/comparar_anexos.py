"""Compara os anexos publicados à parte com os de dentro do PDF inventariado, palavra a palavra.

Rodada 4. Entradas: os PDFs de `editais/<edital>/fonte/consulta-2026-10-11/` e as linhas de cobertura (`corpus.py`).
A comparação ignora caixa e pontuação; os traços dos campos em branco aparecem como diferença, e são só leiaute.

Uso, da raiz do repositório:  python3 docs/libras/ferramentas/comparar_anexos.py
"""

import difflib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus import RAIZ, carregar  # noqa: E402

CASOS = [
    ("E28", "edital-28-2026", "anexo-I-cronograma.pdf", "Anexo I"),
    ("E28", "edital-28-2026", "anexo-II-requerimento.pdf", "Anexo II"),
    ("E28", "edital-28-2026", "anexo-III-autodeclaracao-etnico-racial.pdf", "Anexo III"),
    ("E28", "edital-28-2026", "anexo-IV-autodeclaracao-pcd.pdf", "Anexo IV"),
    ("E28", "edital-28-2026", "anexo-V-pertencimento-etnico.pdf", "Anexo V"),
    ("E28", "edital-28-2026", "anexo-VI-consentimento-dados.pdf", "Anexo VI"),
    ("E59", "edital-59-2026", "anexo-I-cronograma.pdf", "Anexo I"),
    ("E59", "edital-59-2026", "anexo-II-requerimento.pdf", "Anexo II"),
]


def palavras(t):
    return re.sub(r"[^\w\s]", " ", t.lower()).split()


def texto_pdf(caminho):
    saida = subprocess.run(["pdftotext", "-layout", str(caminho), "-"], capture_output=True, text=True, check=True)
    return saida.stdout


linhas = carregar()[0]
for chave, slug, arquivo, rotulo in CASOS:
    dentro = " ".join(o["texto"] for o in linhas[chave] if o["item"] == rotulo or o["item"].startswith(rotulo + ","))
    a = palavras(dentro)
    b = palavras(texto_pdf(RAIZ / "editais" / slug / "fonte" / "consulta-2026-10-11" / arquivo))
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    print(f"== {chave} {rotulo}: no PDF {len(a)} palavras, à parte {len(b)}; razão {sm.ratio():.3f}")
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != "equal" and not all(set(x) <= {"_"} for x in a[i1:i2] + b[j1:j2]):
            print(f"   {op}: «{' '.join(a[i1:i2])[:120]}» → «{' '.join(b[j1:j2])[:120]}»")
