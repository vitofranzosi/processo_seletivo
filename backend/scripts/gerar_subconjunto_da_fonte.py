#!/usr/bin/env python3
"""Gera o subconjunto da fonte que o Edital embute (069, D-002, R-007, T029).

Roteiro de desenvolvimento, e não do produto: roda **uma vez**, quando a fonte de origem muda, e o
resultado é versionado em `processo_seletivo/publicacoes/infrastructure/fontes/`. O `fontTools` só
existe aqui, pela linha de comando — o produto lê os arquivos gerados com o próprio leitor
(`fonte.py`), e o guardião de dependências não precisa abrir exceção.

Uso, a partir de `backend/`, com o pacote oficial já extraído:

    uv run --no-project --with fonttools python scripts/gerar_subconjunto_da_fonte.py \\
        <pasta com LiberationSans-Regular.ttf e LiberationSans-Bold.ttf>

**O subconjunto cobre o WinAnsi inteiro**, e não só o que um Edital usa hoje: o documento escreve
em `cp1252`, e o que `grafia` aceita é exatamente esse repertório. Um teste confere a cobertura.

**Determinístico.** `recalcTimestamp=False` e `recalc_timestamp=False` mantêm a data do `head` de
origem; sem eles, cada execução mudaria os bytes do subconjunto, e com eles os bytes de todo Edital
composto depois.

**O fluxo comprimido também é versionado** (`.ttf.zlib`). O PDF embute a fonte comprimida, e
comprimir na hora de compor faria os bytes do Edital dependerem da biblioteca `zlib` da máquina —
uma variante dela (a `zlib-ng`, por exemplo) comprime diferente, e a fixture de bytes reprovaria no
CI sem que nada no documento tivesse mudado. Descomprimir é determinístico; um teste confere que o
comprimido é o TTF versionado.

**O nome é outro, de propósito.** A Liberation Sans 2.x é distribuída sob a SIL Open Font License
1.1, com os nomes "Liberation", "Arimo", "Tinos" e "Cousine" reservados. Um subconjunto é uma versão
modificada, e a OFL não deixa versão modificada usar nome reservado. O subconjunto se chama
**Edital Sans**; o aviso de direitos autorais e a licença de origem vão com ele, e `ORIGEM.md` diz
de onde ele veio.
"""

import hashlib
import sys
import zlib
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

DESTINO = (
    Path(__file__).resolve().parents[1]
    / "processo_seletivo"
    / "publicacoes"
    / "infrastructure"
    / "fontes"
)
ESTILOS = {
    "Regular": ("LiberationSans-Regular.ttf", "EditalSans-Regular.ttf"),
    "Bold": ("LiberationSans-Bold.ttf", "EditalSans-Bold.ttf"),
}
FAMILIA = "Edital Sans"


def _winansi():
    """Os pontos de código que o `cp1252` representa, do espaço em diante."""
    pontos = set()
    for byte in range(32, 256):
        try:
            pontos.add(ord(bytes([byte]).decode("cp1252")))
        except UnicodeDecodeError:
            continue
    return sorted(pontos)


def _renomear(fonte, estilo):
    """Troca os nomes da família, e só eles; o direito autoral e a licença ficam (nameID 0, 13, 14).

    `nameID` 1 e 2: família e estilo; 3: identificador único; 4: nome completo; 6: nome PostScript;
    16 e 17: família e estilo tipográficos.
    """
    nomes = {
        1: FAMILIA,
        2: estilo,
        3: f"{FAMILIA} {estilo}: subconjunto WinAnsi",
        4: f"{FAMILIA} {estilo}",
        6: f"EditalSans-{estilo}",
        16: FAMILIA,
        17: estilo,
    }
    tabela = fonte["name"]
    for registro in list(tabela.names):
        if registro.nameID in nomes:
            tabela.setName(
                nomes[registro.nameID],
                registro.nameID,
                registro.platformID,
                registro.platEncID,
                registro.langID,
            )
    # Nome reservado em qualquer outro registro que reste — descrição, marca do fabricante — sai.
    for registro in list(tabela.names):
        texto = registro.toUnicode()
        if registro.nameID not in (0, 7, 13, 14) and any(
            reservado in texto for reservado in ("Liberation", "Arimo", "Tinos", "Cousine")
        ):
            tabela.removeNames(nameID=registro.nameID)


def _sha256(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def gerar(pasta_de_origem):
    opcoes = subset.Options()
    opcoes.recalc_timestamp = False
    opcoes.name_IDs = ["*"]
    opcoes.name_languages = ["*"]
    opcoes.notdef_outline = True
    opcoes.glyph_names = False
    # O compositor não aplica kerning nem substituição: o que o PDF desenha é o glifo de cada byte.
    opcoes.layout_features = []
    opcoes.drop_tables += ["GSUB", "GPOS", "GDEF", "kern", "DSIG"]
    DESTINO.mkdir(parents=True, exist_ok=True)
    for estilo, (origem, destino) in ESTILOS.items():
        caminho_de_origem = Path(pasta_de_origem) / origem
        fonte = TTFont(caminho_de_origem, recalcTimestamp=False)
        subconjunto = subset.Subsetter(opcoes)
        subconjunto.populate(unicodes=_winansi())
        subconjunto.subset(fonte)
        _renomear(fonte, estilo)
        fonte.save(DESTINO / destino, reorderTables=True)
        dados = (DESTINO / destino).read_bytes()
        (DESTINO / f"{destino}.zlib").write_bytes(zlib.compress(dados, 9))
        print(
            f"{origem}  sha256 {_sha256(caminho_de_origem)}\n"
            f"  → {destino}  sha256 {_sha256(DESTINO / destino)}  "
            f"{(DESTINO / destino).stat().st_size} bytes"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    gerar(sys.argv[1])
