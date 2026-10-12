"""Compara, trecho a trecho, o documento de cada Retificação com o original (texto e página).

Uso, da raiz do repositório:  python3 docs/libras/ferramentas/comparar_retificacoes.py
Serve ao 91/2026 e ao 01/2026, cujas âncoras continuam válidas no consolidado. O 92/2026 retirou uma
seção e renumerou as seguintes: as âncoras das seções 7 a 15 deixam de casar, e a comparação dele foi
feita por diferença de texto (`diff` do `pdftotext -layout`), registrada em `editais/edital-92-2026/retificacoes.md`.
"""

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus import RAIZ  # noqa: E402
from fatiar import fatiar  # noqa: E402
from linhas import E01, E91  # noqa: E402


def comparar(chave, slug, linhas_, versao):
    fonte = RAIZ / "editais" / slug / "fonte"
    o1, _ = fatiar(str(fonte / "pub1.pdf"), linhas_)
    ls2 = copy.deepcopy(linhas_)
    ls2.insert(2, dict(ancora="Versão consolidada.", item="Marca de consolidação", unidade="consolidacao"))
    o2, _ = fatiar(str(fonte / f"{versao}.pdf"), ls2)
    marca = o2.pop(2)
    print(f"== {chave} pub1 → {versao} | marca: {marca['texto']}")
    # Python 3.9, sem `strict`: as duas listas têm o mesmo tamanho por construção (mesmas âncoras).
    for i, (x, y) in enumerate(zip(o1, o2), 1):  # noqa: B905
        if x["texto"] != y["texto"] or x["pag_ini"] != y["pag_ini"]:
            muda = "TEXTO MUDOU" if x["texto"] != y["texto"] else "só página"
            print(f"  {chave}-{i:03d} [{x['item']}] p{x['pag_ini']}→{y['pag_ini']} | {muda}")
            if x["texto"] != y["texto"]:
                print("     antes: ", x["texto"][:220])
                print("     depois:", y["texto"][:220])


comparar("E91", "edital-91-2026", E91, "pub2")
comparar("E01", "edital-01-2026", E01, "pub2")
comparar("E01", "edital-01-2026", E01, "pub3")
