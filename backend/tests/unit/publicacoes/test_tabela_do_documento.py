"""Dois defeitos da tabela do documento que o estudo de esforço mediu no papel (§12, itens 7 e 14).

Os dois estavam no Cronograma do 78/2026 e do 140/2025 publicados, e só se viam na página
renderizada: o `pdftotext` lia o texto certo.
"""

from processo_seletivo.publicacoes.infrastructure.pdf import (
    CORPO_TABELA,
    LARGURA,
    MARGEM,
    NEGRITO,
    PADDING_DA_COLUNA,
    REGULAR,
    Composicao,
    _larguras_das_colunas,
    _tabela,
    largura,
)

CABECALHO = ["Nº", "Evento", "Início", "Término", "Onde"]


def _evento(numero, descricao, onde="—"):
    return [str(numero), descricao, "05/08/2026, às 00h", "11/09/2026, às 23h59", onde]


def _naturais(linhas):
    """O que cada coluna pede, sem teto — a medida que `_larguras_das_colunas` parte."""
    return [
        max(
            largura(CABECALHO[c], CORPO_TABELA, NEGRITO),
            *(largura(linha[c], CORPO_TABELA, REGULAR) for linha in linhas),
        )
        + PADDING_DA_COLUNA
        for c in range(len(CABECALHO))
    ]


def test_duas_colunas_longas_nao_espremem_as_curtas():
    """Com Evento **e** Onde longos, "Nº" saía cortado e cada data ocupava três linhas.

    O excesso era tirado da mais larga até ela não caber no piso — e então todas encolhiam na
    mesma proporção, inclusive o número e as datas, que eram as que cabiam.
    """
    linhas = [
        _evento(
            1, "Realização do Sorteio das vagas — transmissão no canal do Ifes/Cefor no YouTube"
        ),
        _evento(
            2,
            "Classificação Preliminar (resultado do sorteio)",
            "Salão de Reuniões, terceiro piso, prédio do Cefor; transmissão pelo YouTube",
        ),
        _evento(10, "Publicação do Resultado Final e homologação das matrículas"),
    ]
    disponivel = LARGURA - 2 * MARGEM
    naturais = _naturais(linhas)

    colunas = _larguras_das_colunas(CABECALHO, linhas, CORPO_TABELA, disponivel)

    assert abs(sum(colunas) - disponivel) < 0.01, "a tabela ocupa a área útil, nem mais nem menos"
    for indice in (0, 2, 3):
        assert colunas[indice] >= naturais[indice] - 0.01, (
            f"a coluna {CABECALHO[indice]!r} foi espremida abaixo do que o conteúdo dela pede"
        )


def test_uma_coluna_longa_continua_cedendo_sozinha():
    """O caso que a regra anterior já resolvia: quem estoura a linha é quem cede."""
    linhas = [_evento(1, "D" * 400)]
    disponivel = LARGURA - 2 * MARGEM
    naturais = _naturais(linhas)

    colunas = _larguras_das_colunas(CABECALHO, linhas, CORPO_TABELA, disponivel)

    assert colunas[1] < naturais[1]
    for indice in (0, 2, 3, 4):
        assert colunas[indice] >= naturais[indice] - 0.01


def _fios_horizontais(fios):
    return [fio for fio in fios if fio[0] == "seg" and fio[2] == fio[4]]


def test_a_linha_que_abre_a_pagina_seguinte_ganha_o_seu_fio():
    """No 78/2026 as linhas 7 e 8 saíam fundidas; no 140/2025, as 6 e 7.

    O estudo leu nisso "células iguais", e não era: nos dois casos a primeira das duas é a linha
    que a quebra levou para a página seguinte. O início dela era anotado antes da quebra, e a
    quebra recomeçava o quadro sem ele — a linha não entrava na grade, e o fio abaixo dela sumia.
    """
    composicao = Composicao()
    # Texto bastante para que a tabela comece perto do pé da página e se parta.
    for _ in range(40):
        composicao.escrever("Parágrafo de enchimento.", tamanho=10)
    linhas = [
        _evento(n, f"Evento de número {n}, com descrição em duas linhas " * 2) for n in range(1, 13)
    ]
    _tabela(composicao, CABECALHO, linhas, recuo=0.0)

    paginas = composicao.paginar()
    com_tabela = [(textos, fios) for textos, fios in paginas if any(t[0] == "Nº" for t in textos)]
    assert len(com_tabela) >= 2, "o cenário precisa partir a tabela entre páginas"

    for textos, fios in com_tabela:
        numeros = [t[0] for t in textos if t[0].isdigit()]
        # Cabeçalho + as linhas da página: um fio abaixo de cada uma, menos a última, que fecha
        # no contorno.
        assert len(_fios_horizontais(fios)) == len(numeros), (
            f"linhas {numeros}: {len(_fios_horizontais(fios))} fios"
        )
