"""O teste geométrico da peça, sobre o modelo de caixas (111, FR-3428, FR-3429, D-008, D-016).

Aritmética, e não pixel: as caixas são as que o compositor mediu com a fonte que o rasterizador
desenha. Na POC, as conferências sobre o SVG ficaram verdes com o endereço fora da margem e a
quantidade dentro do rótulo; é isso que esta função pega. Os cenários de referência (integração)
e os sintéticos no limite (unitários) passam pela mesma função.
"""

from processo_seletivo.interface import kit_familias, kit_peca
from processo_seletivo.interface.kit_peca import Figura, Imagem, Linha, Retangulo, Texto

AREA_UTIL = (
    kit_peca.MARGEM,
    kit_peca.MARGEM,
    kit_peca.LARGURA - kit_peca.MARGEM,
    kit_peca.ALTURA - kit_peca.MARGEM,
)
# Meio pixel de tolerância: a caixa vem de medida em ponto flutuante, e a posição, arredondada.
TOLERANCIA = 0.5


def _dentro(caixa, area):
    esquerda, topo, direita, base = caixa
    return (
        esquerda >= area[0] - TOLERANCIA
        and topo >= area[1] - TOLERANCIA
        and direita <= area[2] + TOLERANCIA
        and base <= area[3] + TOLERANCIA
    )


def _cruzam(uma, outra):
    return not (
        uma[2] <= outra[0] + TOLERANCIA
        or outra[2] <= uma[0] + TOLERANCIA
        or uma[3] <= outra[1] + TOLERANCIA
        or outra[3] <= uma[1] + TOLERANCIA
    )


def _luminancia(cor):
    canais = [int(cor[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    lineares = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
    return 0.2126 * lineares[0] + 0.7152 * lineares[1] + 0.0722 * lineares[2]


def contraste(cor, fundo):
    claro, escuro = sorted((_luminancia(cor), _luminancia(fundo)), reverse=True)
    return (claro + 0.05) / (escuro + 0.05)


def _fundo_da_pagina(template):
    """A cor sobre a qual o texto fica fora de todo bloco: o branco da Institucional, ou o tom do
    fundo da imagem que a família declara (D-011)."""
    nome = template.dimensoes.get("fundo")
    return kit_familias.familia(template.familia).cor(nome) if nome else kit_peca.BRANCO


def problemas(peca):
    """Tudo o que a FR-3428, a FR-3429 e a FR-3822/FR-3824 proíbem, por extenso, no template da
    peça. Vazio é peça bem composta."""
    achados = []
    template = peca.template
    formato = template.formato
    area_util = formato.area_util
    fundo_da_pagina = _fundo_da_pagina(template)
    textos = [e for e in peca.elementos if isinstance(e, Texto)]
    blocos = [e for e in peca.elementos if isinstance(e, Retangulo)]
    linhas = [e for e in peca.elementos if isinstance(e, Linha)]
    marcas = [e for e in peca.elementos if isinstance(e, Imagem)]
    opacas = [e for e in peca.elementos if isinstance(e, Figura) and e.opaca]
    obstaculos = dict(template.dimensoes.get("obstaculos", {}))
    if template.area_da_imagem:
        obstaculos["imagem"] = template.area_da_imagem
    # Os ativos posicionados que não recebem texto são obstáculo (D-011).
    opacos = template.dimensoes.get("opacos", {})
    for nome, (x, y, largura, altura) in template.ativos_posicionados.items():
        if nome not in opacos:
            obstaculos[nome] = (x, y, x + largura, y + altura)

    for texto in textos:
        nome = f"{texto.campo} {texto.conteudo!r}"
        if texto.tamanho < formato.corpo_minimo:
            achados.append(f"{nome}: corpo {texto.tamanho} px, abaixo do mínimo")
        if not _dentro(texto.caixa, area_util):
            achados.append(f"{nome}: fora da área útil, em {tuple(round(v) for v in texto.caixa)}")
        for zona in formato.zonas_reservadas:
            if _cruzam(texto.caixa, zona):
                achados.append(f"{nome}: invade a zona reservada {zona}")
        if contraste(texto.cor, texto.fundo) < 4.5:
            achados.append(
                f"{nome}: contraste {contraste(texto.cor, texto.fundo):.2f} abaixo do AA"
            )
        dentro_de_bloco = any(_dentro(texto.caixa, b.caixa) for b in [*blocos, *opacas])
        if not dentro_de_bloco:
            for chave, area in obstaculos.items():
                if _cruzam(texto.caixa, area):
                    achados.append(f"{nome}: sobre {chave}, em {area}")
        for figura in opacas:
            if _cruzam(texto.caixa, figura.caixa) and not _dentro(texto.caixa, figura.caixa):
                achados.append(f"{nome}: cortado pelo {figura.campo}")
        if texto.fundo != fundo_da_pagina and any(
            _dentro(texto.caixa, f.caixa) and texto.fundo == (f.cor or kit_peca.BRANCO)
            for f in opacas
        ):
            continue
        if texto.fundo != fundo_da_pagina:
            # O bloco que o contém: o retângulo da cor do fundo sob a origem do texto, e o último
            # desenhado, que é o de cima.
            sob = [
                bloco
                for bloco in blocos
                if bloco.cor == texto.fundo
                and _dentro((texto.x, texto.y, texto.x, texto.y), bloco.caixa)
            ]
            if not sob:
                achados.append(f"{nome}: sem o bloco de fundo {texto.fundo}")
            elif not _dentro(texto.caixa, sob[-1].caixa):
                achados.append(f"{nome}: passa da borda do bloco que o contém")

    for posicao, texto in enumerate(textos):
        for outro in textos[posicao + 1 :]:
            if _cruzam(texto.caixa, outro.caixa):
                achados.append(f"{texto.conteudo!r} e {outro.conteudo!r} se sobrepõem")
        for linha in linhas:
            esquerda, topo, direita, base = texto.caixa
            if topo < linha.y < base and esquerda < linha.x2 and direita > linha.x1:
                achados.append(f"{texto.conteudo!r} cortado pela linha em {linha.y} px")

    for marca in marcas:
        if not _dentro(marca.caixa_visivel, AREA_UTIL):
            achados.append("a marca sai da área útil")
        altura_visivel = marca.caixa_visivel[3] - marca.caixa_visivel[1]
        # O manual (p. 13): o símbolo nunca menor que 30 px. A parte visível é a que o tem.
        if altura_visivel < 30:
            achados.append(f"a marca tem {altura_visivel:.0f} px de altura visível")
        for texto in textos:
            if _cruzam(marca.caixa_visivel, texto.caixa):
                achados.append(f"a marca e {texto.conteudo!r} se sobrepõem")
    return achados
