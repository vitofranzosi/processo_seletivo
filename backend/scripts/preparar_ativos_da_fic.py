#!/usr/bin/env python3
"""Prepara as imagens e os ativos da família FIC do kit de divulgação (119, T047, FR-3826).

Roteiro de desenvolvimento, e não do produto: rodou **uma vez**, e o resultado é versionado em
`processo_seletivo/interface/kit_ativos/fic/`, com a origem e o tratamento no `ORIGEM.md` de lá. O
Pillow só existe aqui.

Uso, a partir de `backend/`, com os três PPTX de `Editais FIC/` descompactados em `post/`, `story/`
e `site/` de uma pasta qualquer:

    uv run --no-project --with pillow python -I scripts/preparar_ativos_da_fic.py \\
        <pasta com post/ story/ site/> processo_seletivo/interface/kit_ativos/fic

O megafone (`site/ppt/media/image5.png`) e o balão (`image1.png`, o mesmo nos três) entram sem
alteração, copiados à mão.
"""

import hashlib
import sys

from PIL import Image, ImageDraw

AMARELO = (251, 197, 2)
MAPA = {
    "mesa": {"post": 3, "story": 2, "banner": 2},
    "prancheta": {"post": 2, "story": 4, "banner": 6},
    "poltrona": {"post": 5, "story": 6, "banner": 4},
    "foguete": {"post": 6, "story": 5, "banner": 3},
}
PASTA = {"post": "post", "story": "story", "banner": "site"}
TAMANHO = {"post": (1080, 1350), "story": (1080, 1920), "banner": (1500, 850)}
# O contato do Cefor desenhado no fundo, em px do original: sai, e o da ficha entra no lugar.
APAGAR = {"post": (100, 1740, 860, 1845), "story": (85, 1535, 450, 1665)}
# A bolha branca de cada fundo, em px do original: muda de lugar de uma foto para outra, e o número
# do Edital tem de ficar no mesmo lugar em todas. Sai do fundo e volta como ativo fixo.
BOLHA = {
    ("mesa", "post"): (1227, 1287, 1590, 1533),
    ("mesa", "story"): (804, 1305, 1118, 1518),
    ("mesa", "banner"): (1233, 251, 1501, 432),
    ("prancheta", "post"): (1197, 1181, 1559, 1427),
    ("prancheta", "story"): (772, 1252, 1086, 1465),
    ("prancheta", "banner"): (1233, 251, 1501, 432),
    ("poltrona", "post"): (1247, 1165, 1610, 1411),
    ("poltrona", "story"): (804, 1177, 1118, 1390),
    ("poltrona", "banner"): (1233, 168, 1501, 349),
    ("foguete", "post"): (1136, 1151, 1499, 1397),
    ("foguete", "story"): (804, 1241, 1118, 1454),
    ("foguete", "banner"): (1233, 230, 1501, 411),
}
S, DEST = sys.argv[1], sys.argv[2]
for chave, formatos in MAPA.items():
    for formato, n in formatos.items():
        im = Image.open(f"{S}/{PASTA[formato]}/ppt/media/image{n}.png").convert("RGB")
        if formato in APAGAR:
            x0, y0, x1, y1 = APAGAR[formato]
            if formato == "post" and n == 5:
                x0, y0, x1, y1 = x0 + 20, y0 + 14, x1 + 20, y1 + 14
            ImageDraw.Draw(im).rectangle((x0, y0, x1, y1), fill=AMARELO)
        x0, y0, x1, y1 = BOLHA[(chave, formato)]
        ImageDraw.Draw(im).rectangle((x0 - 4, y0 - 4, x1 + 4, y1 + 3), fill=AMARELO)
        im = im.resize(TAMANHO[formato], Image.LANCZOS)
        destino = f"{DEST}/{chave}-{formato}.jpg"
        im.save(destino, "JPEG", quality=60, optimize=True)
        dados = open(destino, "rb").read()
        print(chave, formato, f"image{n}.png", len(dados), hashlib.sha256(dados).hexdigest())

# A bolha, recortada do post da prancheta: branco, com a transparência do quanto o pixel se afasta
# do amarelo na direção do branco.
im = Image.open(f"{S}/post/ppt/media/image2.png").convert("RGB")
x0, y0, x1, y1 = BOLHA[("prancheta", "post")]
recorte = im.crop((x0, y0, x1 + 1, y1 + 1))
saida = Image.new("RGBA", recorte.size)
for y in range(recorte.height):
    for x in range(recorte.width):
        r, g, b = recorte.getpixel((x, y))
        alfa = max(0.0, min(1.0, (b - 2) / 253))
        saida.putpixel((x, y), (255, 255, 255, round(alfa * 255)))
saida.save(f"{DEST}/bolha.png", optimize=True)
dados = open(f"{DEST}/bolha.png", "rb").read()
print("bolha", saida.size, len(dados), hashlib.sha256(dados).hexdigest())
