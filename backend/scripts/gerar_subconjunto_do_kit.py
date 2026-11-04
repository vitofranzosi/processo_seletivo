#!/usr/bin/env python3
"""Gera o subconjunto de uma fonte livre para a peça do kit de divulgação (119, D-005, FR-3823).

Roteiro de desenvolvimento, e não do produto: roda **uma vez** por fonte, e o resultado é versionado
em `processo_seletivo/interface/kit_ativos/fontes/`, com a linha no `ORIGEM.md` de lá. O `fontTools`
só existe aqui, como no roteiro da Edital Sans (`gerar_subconjunto_da_fonte.py`); o produto lê os
arquivos gerados com o próprio leitor (`kit_fontes.py`).

Uso, a partir de `backend/`:

    uv run --no-project --with fonttools python scripts/gerar_subconjunto_do_kit.py \\
        <arquivo de origem .ttf> <arquivo de destino .ttf>

**O subconjunto cobre o WinAnsi inteiro**, o repertório que a `grafia` deixa chegar à peça, e um
teste confere a cobertura.

**Sem kerning nem substituição.** O compositor mede pela largura de avanço de cada glifo; uma
tabela `kern` ou `GPOS` faria o rasterizador desenhar outra largura, e a caixa medida não seria a
desenhada.

**Determinístico**: `recalc_timestamp=False` mantém a data do `head` de origem.

**O nome continua o da origem** quando a licença não reserva nenhum: a Poppins é OFL sem "Reserved
Font Name". Fonte com nome reservado precisa ser renomeada, como a Edital Sans.
"""

import hashlib
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

DESTINO = Path(__file__).resolve().parents[1] / "processo_seletivo/interface/kit_ativos/fontes"


def _winansi():
    pontos = set()
    for byte in range(32, 256):
        try:
            pontos.add(ord(bytes([byte]).decode("cp1252")))
        except UnicodeDecodeError:
            continue
    return sorted(pontos)


def _sha256(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def gerar(origem, destino):
    opcoes = subset.Options()
    opcoes.recalc_timestamp = False
    opcoes.name_IDs = ["*"]
    opcoes.name_languages = ["*"]
    opcoes.notdef_outline = True
    opcoes.glyph_names = False
    opcoes.layout_features = []
    opcoes.drop_tables += ["GSUB", "GPOS", "GDEF", "kern", "DSIG"]
    fonte = TTFont(origem, recalcTimestamp=False)
    subconjunto = subset.Subsetter(opcoes)
    subconjunto.populate(unicodes=_winansi())
    subconjunto.subset(fonte)
    DESTINO.mkdir(parents=True, exist_ok=True)
    caminho = DESTINO / destino
    fonte.save(caminho, reorderTables=True)
    print(
        f"{Path(origem).name}  sha256 {_sha256(origem)}\n"
        f"  → {destino}  sha256 {_sha256(caminho)}  {caminho.stat().st_size} bytes"
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    gerar(sys.argv[1], sys.argv[2])
