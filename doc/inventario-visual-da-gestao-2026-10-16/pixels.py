"""Compara capturas pixel a pixel, contra uma linha de ruído (089).

    pixels.py <antes> <depois> <ruído-a> <ruído-b> [<ruído-a> <ruído-b> ...]

Cada argumento é uma pasta com os PNGs de uma passada (`<id>--<largura>.png`, direto na pasta ou em
`png/`). Para cada PNG, conta os pixels diferentes e a intensidade máxima da diferença antes→depois, e
a de cada par de ruído — duas capturas do **mesmo** código, que já diferem entre si. Um par só não
basta: a suavização do texto muda de lugar a cada passada, e numa tela ela aparece num par e não no
outro. A linha de ruído de cada variante é o maior dos pares.

O `comparar.py` vê `status` e estouro, e o `medidas.py`, largura e altura: nenhum dos dois vê cor nem
fonte. Uma folha que não carregasse, ou um token perdido, mudaria a cor de tudo sem mudar uma medida.
E o pixel sozinho engana — hora, cursor e a suavização de texto em moldura que rola mudam entre duas
capturas do mesmo código —, daí a linha de ruído.

Uma variante **passa** quando antes→depois é zero, ou quando não é maior que a linha de ruído nem em
pixels nem em intensidade. Tamanhos diferentes reprovam sempre. Sai com código 1 se alguma reprovar.
"""

import sys
from pathlib import Path

from PIL import Image, ImageChops


def pngs(pasta):
    pasta = Path(pasta)
    if (pasta / "png").is_dir():
        pasta = pasta / "png"
    return {p.name: p for p in sorted(pasta.glob("*.png"))}


def diferenca(a, b):
    with Image.open(a) as ia, Image.open(b) as ib:
        ia, ib = ia.convert("RGB"), ib.convert("RGB")
        if ia.size != ib.size:
            return None
        d = ImageChops.difference(ia, ib).convert("L")
        histograma = d.histogram()
        contagem = sum(histograma[1:])
        maximo = max((i for i, n in enumerate(histograma) if n), default=0)
        return contagem, maximo


antes, depois = pngs(sys.argv[1]), pngs(sys.argv[2])
pares = [(pngs(a), pngs(b)) for a, b in zip(sys.argv[3::2], sys.argv[4::2], strict=True)]
nomes = sorted(set(antes) & set(depois))
faltam = sorted(set(antes) ^ set(depois))


def ruido(nome):
    medidas = [diferenca(a[nome], b[nome]) for a, b in pares if nome in a and nome in b]
    if any(m is None for m in medidas):
        return None
    return (max((m[0] for m in medidas), default=0), max((m[1] for m in medidas), default=0))


reprovadas, no_ruido, identicas = [], 0, 0
for nome in nomes:
    dd = diferenca(antes[nome], depois[nome])
    dr = ruido(nome)
    if dd == (0, 0):
        identicas += 1
    elif dd is None or dr is None or dd[0] > dr[0] or dd[1] > dr[1]:
        reprovadas.append(nome)
        print(f"REPROVA   {nome}: depois {dd or 'tamanho diferente'}; ruído {dr}")
    else:
        no_ruido += 1
        print(f"no ruído  {nome}: depois {dd[0]} px, máx {dd[1]}; ruído {dr[0]} px, máx {dr[1]}")

print(
    f"comparadas: {len(nomes)}; idênticas: {identicas}; dentro do ruído: {no_ruido}; "
    f"reprovadas: {len(reprovadas)}; só numa das passadas: {faltam}"
)
sys.exit(1 if reprovadas or faltam else 0)
