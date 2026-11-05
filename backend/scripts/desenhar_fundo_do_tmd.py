#!/usr/bin/env python3
"""Desenha o fundo fixo da família TMD, um por formato (119, T052, EC-20).

Roteiro de desenvolvimento, e não do produto: roda **uma vez**, e o resultado é versionado em
`processo_seletivo/interface/kit_ativos/tmd/`, com a linha no `ORIGEM.md` de lá. Uso, a partir de
`backend/`:

    uv run python scripts/desenhar_fundo_do_tmd.py processo_seletivo/interface/kit_ativos/tmd

**Por que desenho próprio, e não o fundo dos slides.** O fundo dos arquivos da comunicação
(`Editais TMD - …pptx`) traz uma ilustração plana de banco — a pessoa diante do tablet, a
lâmpada — cuja licença ninguém conferiu, e a T052 pede ilustração de licença conferida ou desenho
próprio. Este é o desenho próprio: só formas geométricas, nas cores lidas do pixel do fundo dos
slides — o roxo, o lilás da colina, o turquesa dos asteriscos e o dourado do elo —, e na mesma
disposição: ilustração no alto à direita, colina embaixo, a barra da chamada com o elo, e o rodapé
com os perfis de rede e a marca. Quando a comunicação trouxer a ilustração licenciada (P-1), ela
substitui este arquivo e a versão do template sobe.

**O que é texto no desenho**: só os perfis de rede do rodapé ("ifescefor", "Ifes Cefor"), na Inter
negrito do kit, como no slide; a família os registra nas frases para a varredura os ler. A marca é a
`cefor-horizontal-branco.png` oficial de `kit_ativos/`, sem outra alteração além da escala.

As medidas que a família declara como obstáculo (`kit_familias/tmd.py`) são as daqui: mudar uma
pede mudar a outra.
"""

import base64
import hashlib
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ATIVOS = RAIZ / "processo_seletivo" / "interface" / "kit_ativos"
FONTE = ATIVOS / "fontes" / "Inter-Bold.ttf"
MARCA = ATIVOS / "cefor-horizontal-branco.png"

ROXO = "#5d299c"
LILAS = "#785df5"
VIOLETA = "#a35bfa"
TURQUESA = "#50e3cf"
DOURADO = "#d6d58e"
SOMBRA = "#6a4fe0"
ESCURO = "#2e2457"
TELA = "#b9a9fb"
AMARELO = "#f8b83a"
ROSA = "#f77fa6"
LARANJA = "#f7a14b"
BRANCO = "#ffffff"

#: Por formato: tamanho, a colina (pontos da curva), a barra da chamada, os asteriscos, a
#: ilustração (x, y, escala) e o rodapé (y, ou nada).
FORMATOS = {
    "post": {
        "tamanho": (1080, 1350),
        "colina": ((0, 1130), (180, 1030, 380, 990, 560, 990), (760, 990, 940, 1060, 1080, 1160)),
        "barra": (190, 1095, 700, 82),
        "asteriscos": ((60, 1210, 110), (1060, 1330, 120)),
        "ilustracao": (660, 80, 1.0),
        "rodape": 1270,
    },
    "story": {
        "tamanho": (1080, 1920),
        "colina": (
            (0, 1600),
            (180, 1500, 380, 1460, 560, 1460),
            (760, 1460, 940, 1530, 1080, 1630),
        ),
        "barra": (170, 1540, 740, 90),
        "asteriscos": ((60, 1700, 120), (1050, 1880, 130)),
        "ilustracao": (640, 270, 1.05),
        "rodape": 1800,
    },
    "banner": {
        "tamanho": (1500, 850),
        "colina": ((0, 760), (300, 690, 500, 660, 700, 660), (950, 660, 1200, 720, 1500, 820)),
        "barra": (440, 705, 620, 80),
        "asteriscos": ((40, 800, 110), (1440, 830, 100)),
        "ilustracao": (1000, 60, 1.1),
        "rodape": None,
    },
}


def _colina(largura, altura, pontos):
    (x0, y0), c1, c2 = pontos
    return (
        f'<path fill="{LILAS}" d="M0,{altura} L{x0},{y0} '
        f"C{c1[0]},{c1[1]} {c1[2]},{c1[3]} {c1[4]},{c1[5]} "
        f'C{c2[0]},{c2[1]} {c2[2]},{c2[3]} {c2[4]},{c2[5]} L{largura},{altura} Z"/>'
    )


def _asterisco(cx, cy, raio):
    """Seis braços: três traços grossos pelo centro, como os do slide."""
    tracos = []
    for angulo in (12, 72, 132):
        dx = raio * math.cos(math.radians(angulo))
        dy = raio * math.sin(math.radians(angulo))
        tracos.append(
            f'<line x1="{cx - dx:.1f}" y1="{cy - dy:.1f}" x2="{cx + dx:.1f}" y2="{cy + dy:.1f}" '
            f'stroke="{TURQUESA}" stroke-width="{raio * 0.3:.1f}"/>'
        )
    return "".join(tracos)


def _barra(x, y, largura, altura):
    """A barra da chamada, no roxo do fundo, com a sombra e o elo dourado à esquerda."""
    meio = y + altura / 2
    elo = altura * 0.32
    ex = x + 25 + elo
    return (
        f'<ellipse cx="{x + largura / 2}" cy="{y + altura + 6}" rx="{largura * 0.42}" ry="14" '
        f'fill="{SOMBRA}"/>'
        f'<rect x="{x}" y="{y}" width="{largura}" height="{altura}" fill="{ROXO}"/>'
        f'<g transform="rotate(-45 {ex} {meio})" fill="none" stroke="{DOURADO}" '
        f'stroke-width="{altura * 0.06:.1f}">'
        f'<rect x="{ex - elo * 1.25:.1f}" y="{meio - elo * 0.45:.1f}" width="{elo * 1.3:.1f}" '
        f'height="{elo * 0.9:.1f}" rx="{elo * 0.45:.1f}"/>'
        f'<rect x="{ex - elo * 0.05:.1f}" y="{meio - elo * 0.45:.1f}" width="{elo * 1.3:.1f}" '
        f'height="{elo * 0.9:.1f}" rx="{elo * 0.45:.1f}"/></g>'
    )


def _ilustracao(x, y, escala):
    """O tablet com a aula em vídeo e a lâmpada da ideia, sobre a mancha violeta.

    Desenhada numa caixa de 400 × 440 a partir de (x, y): é o que a família declara de obstáculo.
    """
    partes = [
        f'<circle cx="210" cy="230" r="200" fill="{VIOLETA}"/>',
        # A folha rosa atrás do tablet.
        f'<path d="M70,380 C20,300 40,190 100,150 C130,230 120,320 70,380 Z" fill="{ROSA}"/>',
        # O tablet.
        f'<rect x="120" y="70" width="250" height="350" rx="22" fill="{ESCURO}"/>',
        f'<rect x="136" y="90" width="218" height="310" rx="10" fill="{TELA}"/>',
        f'<rect x="150" y="110" width="190" height="130" rx="6" fill="{BRANCO}"/>',
        # A professora no vídeo: cabeça e ombros.
        f'<path d="M190,240 C190,190 300,190 300,240 Z" fill="{ROSA}"/>',
        f'<circle cx="245" cy="168" r="26" fill="{LARANJA}"/>',
        f'<path d="M216,160 C220,128 272,128 276,160 C262,146 232,146 216,160 Z" fill="{ESCURO}"/>',
        # A barra de progresso e os botões.
        f'<rect x="152" y="270" width="186" height="8" rx="4" fill="{BRANCO}"/>',
        f'<rect x="260" y="270" width="78" height="8" rx="4" fill="{ROSA}"/>',
        f'<circle cx="260" cy="274" r="10" fill="{ESCURO}"/>',
        f'<path d="M262,310 L262,360 L222,335 Z" fill="{BRANCO}"/>',
        f'<path d="M190,322 L190,348 L170,335 Z M206,322 L206,348 L186,335 Z" fill="{BRANCO}"/>',
        f'<path d="M290,322 L290,348 L310,335 Z M306,322 L306,348 L326,335 Z" fill="{BRANCO}"/>',
        # A lâmpada.
        f'<circle cx="95" cy="75" r="48" fill="{AMARELO}"/>',
        f'<path d="M80,90 L95,60 L110,90" fill="none" stroke="{BRANCO}" stroke-width="5"/>',
        f'<rect x="75" y="118" width="40" height="30" rx="6" fill="{ESCURO}"/>',
    ]
    return f'<g transform="translate({x} {y}) scale({escala})">{"".join(partes)}</g>'


def _rodape(largura, y):
    """Os perfis de rede e a marca do Cefor, na largura do post e do story."""
    marca = base64.b64encode(MARCA.read_bytes()).decode("ascii")
    corpo = 34
    instagram = (
        f'<rect x="210" y="{y - 26}" width="52" height="52" rx="14" fill="none" '
        f'stroke="{BRANCO}" stroke-width="5"/>'
        f'<circle cx="236" cy="{y}" r="12" fill="none" stroke="{BRANCO}" stroke-width="5"/>'
        f'<circle cx="251" cy="{y - 15}" r="3.5" fill="{BRANCO}"/>'
        f'<text x="274" y="{y + 12}" font-family="Inter" font-weight="700" '
        f'font-size="{corpo}" fill="{BRANCO}">ifescefor</text>'
    )
    youtube = (
        f'<rect x="460" y="{y - 22}" width="60" height="44" rx="10" fill="none" '
        f'stroke="{BRANCO}" stroke-width="5"/>'
        f'<path d="M482,{y - 12} L482,{y + 12} L502,{y} Z" fill="{BRANCO}"/>'
        f'<text x="532" y="{y + 12}" font-family="Inter" font-weight="700" '
        f'font-size="{corpo}" fill="{BRANCO}">Ifes Cefor</text>'
    )
    # A marca a 210 px de largura (proporção 720 × 288 do arquivo), o símbolo bem acima dos 30 px.
    marca_x = largura - 210 - 150
    return (
        instagram + youtube + f'<image x="{marca_x}" y="{y - 42}" width="210" height="84" '
        f'href="data:image/png;base64,{marca}"/>'
    )


def svg(formato):
    medidas = FORMATOS[formato]
    largura, altura = medidas["tamanho"]
    partes = [
        f'<rect width="{largura}" height="{altura}" fill="{ROXO}"/>',
        _ilustracao(*medidas["ilustracao"]),
        _colina(largura, altura, medidas["colina"]),
        *(_asterisco(*a) for a in medidas["asteriscos"]),
        _barra(*medidas["barra"]),
    ]
    if medidas["rodape"] is not None:
        partes.append(_rodape(largura, medidas["rodape"]))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'viewBox="0 0 {largura} {altura}">{"".join(partes)}</svg>'
    )


def desenhar(destino):
    import resvg_py

    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    for formato in FORMATOS:
        png = bytes(
            resvg_py.svg_to_bytes(
                svg_string=svg(formato), font_files=[str(FONTE)], skip_system_fonts=True
            )
        )
        caminho = destino / f"fundo-{formato}.png"
        caminho.write_bytes(png)
        print(f"{caminho.name}  {len(png)} bytes  {hashlib.sha256(png).hexdigest()}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    desenhar(sys.argv[1])
