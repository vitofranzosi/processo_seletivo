#!/usr/bin/env python3
"""Gera o subconjunto de uma fonte livre para a peça do kit de divulgação (119, D-005, FR-3823).

Roteiro de desenvolvimento, e não do produto: roda **uma vez** por fonte, e o resultado é versionado
em `processo_seletivo/interface/kit_ativos/fontes/`, com a linha no `ORIGEM.md` de lá. O `fontTools`
só existe aqui, como no roteiro da Edital Sans (`gerar_subconjunto_da_fonte.py`); o produto lê os
arquivos gerados com o próprio leitor (`kit_fontes.py`).

Uso, a partir de `backend/`:

    uv run --no-project --with fonttools python scripts/gerar_subconjunto_do_kit.py \\
        <arquivo de origem .ttf> <arquivo de destino .ttf> [peso]

**Fonte variável pede o peso** (a Unbounded e a Lexend do Google Fonts só existem assim): o eixo
`wght` é fixado nele antes do subconjunto, e o arquivo versionado é estático. O compositor lê um
avanço por glifo, e uma fonte variável desenharia outro conforme o peso que o SVG pedisse.

**O subconjunto cobre o WinAnsi inteiro**, o repertório que a `grafia` deixa chegar à peça, e um
teste confere a cobertura.

**Sem kerning nem substituição.** O compositor mede pela largura de avanço de cada glifo; uma
tabela `kern` ou `GPOS` faria o rasterizador desenhar outra largura, e a caixa medida não seria a
desenhada.

**Determinístico**: `recalc_timestamp=False` mantém a data do `head` de origem.

**O hífen condicional que falta vira o hífen.** A Space Mono (FIC) não mapeia o U+00AD, que o
WinAnsi tem; o subconjunto o aponta para o glifo do U+002D, que é como o hífen condicional aparece
quando aparece. Só se a origem não o tiver: nas outras fontes nada muda, e o resultado delas é o
mesmo de antes.

**O nome continua o da origem** quando a licença não reserva nenhum: a Poppins é OFL sem "Reserved
Font Name". Fonte com nome reservado precisa ser renomeada, como a Edital Sans.
"""

import hashlib
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

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


def _hifen_condicional(fonte):
    for tabela in fonte["cmap"].tables:
        if tabela.isUnicode() and 0x2D in tabela.cmap and 0xAD not in tabela.cmap:
            tabela.cmap[0xAD] = tabela.cmap[0x2D]


def gerar(origem, destino, peso=None):
    opcoes = subset.Options()
    opcoes.recalc_timestamp = False
    opcoes.name_IDs = ["*"]
    opcoes.name_languages = ["*"]
    opcoes.notdef_outline = True
    opcoes.glyph_names = False
    opcoes.layout_features = []
    opcoes.drop_tables += ["GSUB", "GPOS", "GDEF", "kern", "DSIG"]
    fonte = TTFont(origem, recalcTimestamp=False)
    if "fvar" in fonte:
        if peso is None:
            sys.exit(f"{Path(origem).name} é variável: diga o peso.")
        fonte = instancer.instantiateVariableFont(fonte, {"wght": int(peso)}, updateFontNames=True)
    subconjunto = subset.Subsetter(opcoes)
    subconjunto.populate(unicodes=_winansi())
    subconjunto.subset(fonte)
    _hifen_condicional(fonte)
    DESTINO.mkdir(parents=True, exist_ok=True)
    caminho = DESTINO / destino
    fonte.save(caminho, reorderTables=True)
    print(
        f"{Path(origem).name}  sha256 {_sha256(origem)}\n"
        f"  → {destino}  sha256 {_sha256(caminho)}  {caminho.stat().st_size} bytes"
    )


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    gerar(*sys.argv[1:])
