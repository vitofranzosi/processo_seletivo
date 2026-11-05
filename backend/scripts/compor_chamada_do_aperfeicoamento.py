#!/usr/bin/env python3
"""Compõe o ativo da chamada da família Aperfeiçoamento, um por formato (119, T050, FR-3826).

Roteiro de desenvolvimento, e não do produto: roda **uma vez**, e o resultado é versionado em
`processo_seletivo/interface/kit_ativos/aperfeicoamento/`, com a linha no `ORIGEM.md` de lá. O
Pillow só existe aqui.

Uso, a partir de `backend/`:

    uv run --no-project --with pillow python scripts/compor_chamada_do_aperfeicoamento.py \\
        <pasta das imagens de fundo, já reduzidas> <pasta dos renders> <pasta de destino>

Os renders são as páginas do PDF que o PowerPoint exporta de cada arquivo da comunicação,
rasterizadas no tamanho do formato (`pdftoppm -png -scale-to-x L -scale-to-y A`): `post-3.png`,
`story-1.png` e `site-1.png`.

**Por que composição, e não recorte.** O botão verde "SE INTERESSOU?" e o contorno ao lado dele são
do fundo, e o texto do botão é uma caixa do slide. No post, o botão está em alturas diferentes em
cada foto — de 1108 a 1128 px —, e um recorte só do texto não cairia dentro do botão em todas. O
ativo cobre por inteiro o botão e o contorno de qualquer uma das cinco: o miolo é o fundo da foto de
referência, com o botão vazio, e o texto do botão é o do render da comunicação, colado no retângulo
interno do botão. A borda esmaece sobre o azul liso, e não deixa emenda. Nada é desenhado: são
pixels dos arquivos da comunicação, recompostos.
"""

import hashlib
import sys
from pathlib import Path

from PIL import Image

#: formato → (fundo de referência, render, miolo, esmaecimento, retângulo interno do botão).
#: O miolo cobre o botão e o contorno de todas as fotos do formato; as medidas são do fundo.
CHAMADAS = {
    "post": ("cachos-post.jpg", "post-3.png", (170, 1080, 906, 1206), 14, (213, 1122, 415, 1189)),
    "story": (
        "fone-branco-story.jpg",
        "story-1.png",
        (100, 1537, 978, 1661),
        14,
        (112, 1571, 432, 1653),
    ),
    "banner": (
        "fone-branco-banner.jpg",
        "site-1.png",
        (826, 667, 1414, 759),
        10,
        (866, 686, 1061, 750),
    ),
}


def compor(fundos, renders, destino):
    for formato, (fundo, render, miolo, borda, botao) in CHAMADAS.items():
        base = Image.open(Path(fundos) / fundo).convert("RGB")
        texto = Image.open(Path(renders) / render).convert("RGB")
        base.paste(texto.crop(botao), botao[:2])
        x0, y0, x1, y1 = miolo
        recorte = base.crop((x0 - borda, y0 - borda, x1 + borda, y1 + borda)).convert("RGBA")
        largura, altura = recorte.size
        alfa = Image.new("L", recorte.size)
        for y in range(altura):
            for x in range(largura):
                dentro = min(x, y, largura - 1 - x, altura - 1 - y)
                alfa.putpixel((x, y), min(255, round(255 * dentro / borda)))
        recorte.putalpha(alfa)
        caminho = Path(destino) / f"chamada-{formato}.png"
        recorte.save(caminho, optimize=True)
        resumo = hashlib.sha256(caminho.read_bytes()).hexdigest()
        print(f"{caminho.name}  {x0 - borda},{y0 - borda} {largura}×{altura}  sha256 {resumo}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    compor(*sys.argv[1:])
