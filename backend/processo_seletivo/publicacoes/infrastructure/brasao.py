"""O brasão da República, e o mínimo para pôr uma imagem num PDF artesanal.

**Um asset institucional fixo, e nada além.** Não há branding configurável, imagem por Processo,
tema nem engine de assets: o documento tem um símbolo, ele é o da República, e ele é constante.

A imagem é lida de um PNG versionado ao lado deste módulo — formato padrão, que qualquer pessoa
abre e confere no diff. O leitor abaixo trata **um** caso, que é o do arquivo que existe: 8 bits
por componente, RGB, sem entrelaçamento. Qualquer outra combinação é recusada em vez de produzir
um documento com a imagem errada.

Origem: recortado do cabeçalho do Edital 146/2025 do Cefor, versionado em
`specs/008-composicao-institucional/referencias/`. A resolução é a do original — sessenta pixels
de largura —, e é o mesmo símbolo, no mesmo tamanho, que os Editais publicados usam.
"""

import zlib
from pathlib import Path

ARQUIVO = Path(__file__).with_name("brasao.png")

_ASSINATURA = b"\x89PNG\r\n\x1a\n"
_CANAIS = 3  # RGB, oito bits por componente


def _desfiltrar(dados: bytes, largura: int, altura: int) -> bytes:
    """Desfaz os filtros por linha do PNG (tipos 0 a 4).

    Cada linha do PNG é precedida por um byte que diz como ela foi predita a partir da anterior e
    do pixel à esquerda. Sem desfazê-los, o que sai é ruído — e ruído num brasão é uma imagem
    errada num ato administrativo, não um defeito estético.
    """
    passo = largura * _CANAIS
    saida = bytearray()
    anterior = bytearray(passo)
    posicao = 0
    for _ in range(altura):
        filtro = dados[posicao]
        linha = bytearray(dados[posicao + 1 : posicao + 1 + passo])
        posicao += 1 + passo
        for indice in range(passo):
            esquerda = linha[indice - _CANAIS] if indice >= _CANAIS else 0
            acima = anterior[indice]
            diagonal = anterior[indice - _CANAIS] if indice >= _CANAIS else 0
            if filtro == 0:
                previsto = 0
            elif filtro == 1:
                previsto = esquerda
            elif filtro == 2:
                previsto = acima
            elif filtro == 3:
                previsto = (esquerda + acima) // 2
            elif filtro == 4:
                p = esquerda + acima - diagonal
                pa, pb, pc = abs(p - esquerda), abs(p - acima), abs(p - diagonal)
                previsto = esquerda if pa <= pb and pa <= pc else (acima if pb <= pc else diagonal)
            else:
                raise ValueError(f"Filtro PNG não suportado: {filtro}.")
            linha[indice] = (linha[indice] + previsto) & 0xFF
        saida.extend(linha)
        anterior = linha
    return bytes(saida)


def _carregar():
    dados = ARQUIVO.read_bytes()
    if not dados.startswith(_ASSINATURA):
        raise ValueError("O brasão não é um PNG.")
    partes, posicao = {}, len(_ASSINATURA)
    idat = bytearray()
    while posicao < len(dados):
        tamanho = int.from_bytes(dados[posicao : posicao + 4], "big")
        tipo = dados[posicao + 4 : posicao + 8]
        corpo = dados[posicao + 8 : posicao + 8 + tamanho]
        posicao += 12 + tamanho
        if tipo == b"IHDR":
            partes["ihdr"] = corpo
        elif tipo == b"IDAT":
            idat.extend(corpo)
        elif tipo == b"IEND":
            break
    largura = int.from_bytes(partes["ihdr"][0:4], "big")
    altura = int.from_bytes(partes["ihdr"][4:8], "big")
    profundidade, cor, _, _, entrelacado = partes["ihdr"][8:13]
    if (profundidade, cor, entrelacado) != (8, 2, 0):
        raise ValueError("O brasão precisa ser PNG RGB de 8 bits, sem entrelaçamento.")
    return largura, altura, _desfiltrar(zlib.decompress(bytes(idat)), largura, altura)


LARGURA, ALTURA, PIXELS = _carregar()

# O fluxo já comprimido, pronto para virar objeto do PDF. Comprimir uma vez, na importação, mantém
# a composição determinística e barata: o mesmo conteúdo produz sempre os mesmos bytes.
FLUXO = zlib.compress(PIXELS, 9)
