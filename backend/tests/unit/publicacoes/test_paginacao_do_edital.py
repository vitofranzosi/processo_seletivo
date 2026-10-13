"""A paginação do Edital (069, FR-1389 a FR-1392, contrato do documento §7, R-011, SC-521).

Varre as páginas compostas de A, B, da variante de B e de sintéticos, e afirma a ausência dos
defeitos que a auditoria e a amostra mostraram: título, subseção, rótulo ou legenda no pé da página
sem a linha seguinte; cabeçalho de tabela que não se repete; página só com o fecho; página — salvo a
última — com mais da metade da área útil em branco. O número de páginas não é meta.

A forma é afirmada sobre o arquivo composto: o corpo e a fonte de cada linha, e a posição dela.
"""

import copy
import re

import pytest

from processo_seletivo.editais.domain import secoes as catalogo
from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.cenarios_da_auditoria import (
    composto,
    por_perguntas,
    variante_de_b,
)
from tests.unit.publicacoes.test_pdf import documento, secoes, snapshot

DESENHADA = re.compile(rb"BT (?:[\d.]+ Tw )?/(F\d) ([\d.]+) Tf ([\d.]+) ([\d.]+) Td \((.*?)\) Tj")
FLUXO = re.compile(rb"<< /Length \d+ >>\nstream\n(.*?)\nendstream", re.DOTALL)
CORPO_DO_RODAPE = 7.5
# A área útil: do topo ao limite de baixo que o paginador respeita.
UTIL = pdf.TOPO - (pdf.RODAPE + 24)
INICIO_DO_FECHO = re.compile(r"^.+, \d{1,2} de \w+ de \d{4}\.$")


def _paginas(documento_):
    """Por página, as linhas do corpo: `(texto, fonte, corpo, x, y)`, sem o rodapé nem a marca."""
    paginas = []
    for fluxo in FLUXO.findall(documento_):
        linhas = []
        for recurso, corpo, x, y, texto in DESENHADA.findall(fluxo):
            corpo = float(corpo)
            if corpo <= CORPO_DO_RODAPE or float(y) > pdf.TOPO + 1:
                continue
            texto = (
                texto.replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\")
            ).decode("cp1252")
            linhas.append((texto, recurso.decode(), corpo, float(x), float(y)))
        paginas.append(linhas)
    return paginas


def _e_titulo(linha):
    """Título de seção ou de subseção, rótulo de grupo em negrito, ou legenda de tabela."""
    texto, fonte, corpo, _, _ = linha
    if fonte != pdf.NEGRITO:
        return False
    if corpo in (pdf.CORPO_TITULO_DE_SECAO, pdf.CORPO_SUBSECAO):
        return True
    return texto.endswith(":") or texto.startswith("Tabela ")


def _cronograma_longo():
    conteudo = snapshot(sections=secoes(catalogo_=catalogo.CATALOGO_DA_069))
    base = conteudo["schedule"][0]
    conteudo["schedule"] = [
        {
            **copy.deepcopy(base),
            "id": f"77777777-7777-7777-7777-{indice:012d}",
            "description": f"Evento {indice} do processo seletivo, com descrição que reflui",
            "order": indice,
            "isRegistrationPeriod": indice == 1,
        }
        for indice in range(1, 19)
    ]
    return conteudo


def _requisito_maior_que_a_pagina():
    conteudo = snapshot(sections=secoes(catalogo_=catalogo.CATALOGO_DA_069))
    conteudo["profiles"][0]["requirements"] = [
        " ".join(f"Exigência {n} de experiência comprovada em docência." for n in range(1, 160)),
        "Disponibilidade de horário.",
    ]
    return conteudo


DOCUMENTOS = {
    "A": lambda: por_perguntas("A"),
    "B": lambda: por_perguntas("B"),
    "variante de B": lambda: por_perguntas("B", variante_de_b()),
    "A na apresentação plana": lambda: composto("A"),
    "cronograma de 18 linhas": lambda: documento(_cronograma_longo()),
    "requisito maior que a página": lambda: documento(_requisito_maior_que_a_pagina()),
}


@pytest.fixture(scope="module", params=sorted(DOCUMENTOS))
def paginas(request):
    return request.param, _paginas(DOCUMENTOS[request.param]())


def test_nenhum_titulo_no_pe_da_pagina(paginas):
    """FR-1389: título, subseção, rótulo ou legenda nunca fecham a página."""
    caso, todas = paginas
    for numero, linhas in enumerate(todas[:-1], 1):
        assert linhas, f"{caso}: página {numero} vazia"
        assert not _e_titulo(linhas[-1]), f"{caso}: página {numero} termina em {linhas[-1][0]!r}"


def test_nenhuma_pagina_so_com_o_fecho(paginas):
    """A última seção vai com o fecho quando cabem juntas; o fecho nunca sai sozinho."""
    caso, todas = paginas
    for numero, linhas in enumerate(todas, 1):
        if linhas and INICIO_DO_FECHO.match(linhas[0][0]):
            pytest.fail(f"{caso}: a página {numero} começa pelo fecho")


def test_nenhuma_pagina_quase_vazia_salvo_a_ultima(paginas):
    """FR-1392: equilíbrio — mais da metade da área útil em branco só na última página."""
    caso, todas = paginas
    for numero, linhas in enumerate(todas[:-1], 1):
        ocupado = pdf.TOPO - min(y for *_, y in linhas)
        assert ocupado >= UTIL / 2, f"{caso}: página {numero} ocupa só {ocupado / UTIL:.0%}"


def test_a_continuacao_da_tabela_repete_o_cabecalho():
    """FR-1390: o cronograma de 18 linhas quebra com o cabeçalho na página seguinte."""
    todas = _paginas(documento(_cronograma_longo()))
    com_eventos = [
        linhas for linhas in todas if any(texto.startswith("Evento ") for texto, *_ in linhas)
    ]
    assert len(com_eventos) >= 2, "o caso precisa quebrar a tabela"
    primeira = [texto for texto, *_ in com_eventos[0]]
    legenda = next(i for i, texto in enumerate(primeira) if texto.endswith("— Cronograma"))
    cabecalho = primeira[legenda + 1 : primeira.index("1", legenda)]
    assert cabecalho[:3] == ["Nº", "Evento", "Quando"]
    for linhas in com_eventos[1:]:
        assert [texto for texto, *_ in linhas[: len(cabecalho)]] == cabecalho


def test_a_tabela_que_quebra_deixa_ao_menos_duas_linhas_de_cada_lado():
    todas = _paginas(documento(_cronograma_longo()))
    for linhas in todas:
        eventos = {texto for texto, *_ in linhas if re.match(r"^Evento \d+ ", texto)}
        assert len(eventos) != 1, "uma linha só da tabela numa página"


def test_o_item_maior_que_a_pagina_se_parte_sem_pagina_vazia():
    todas = _paginas(documento(_requisito_maior_que_a_pagina()))
    assert all(todas)
    com_o_item = [
        numero
        for numero, linhas in enumerate(todas, 1)
        if any("Exigência" in texto for texto, *_ in linhas)
    ]
    assert len(com_o_item) >= 2, "o item maior que a página se parte entre páginas"
    assert com_o_item == list(range(com_o_item[0], com_o_item[-1] + 1))


def test_a_secao_que_termina_numa_tabela_nao_manda_a_celula_sozinha_para_o_fecho():
    """O `junto` da última linha não vale dentro de um quadro: a quebra levava a célula, e não a
    grade, e ela saía no alto da página do fecho, fora da tabela."""
    for paragrafos in range(18, 34):
        composicao = pdf.Composicao(metrica=pdf.METRICA_DO_EDITAL, equilibrio=True)
        with pdf.com_o_fecho(composicao, lambda c=composicao: c.escrever("FECHO DO ATO")):
            for indice in range(paragrafos):
                composicao.escrever(f"Parágrafo {indice} da última seção do Edital.", antes=6.0)
            pdf._tabela(composicao, ["Coluna A", "Coluna B"], [["a1", "b1"], ["a2", "b2"]])
        paginas = [[linha[0] for linha in pagina[0]] for pagina in composicao.paginar()]
        onde = {texto: numero for numero, pagina in enumerate(paginas) for texto in pagina}
        assert onde["a2"] == onde["b2"], f"com {paragrafos} parágrafos, a linha da tabela se partiu"


def test_o_equilibrio_nao_divide_o_sumario():
    """O sumário salta inteiro, mesmo deixando mais da metade da página em branco."""
    composicao = pdf.Composicao(metrica=pdf.METRICA_DO_EDITAL, equilibrio=True)
    for indice in range(12):
        composicao.escrever(f"Parágrafo {indice} do preâmbulo.", antes=6.0)
    rotulos = [f"{numero}. Seção {numero}" for numero in range(1, 26)]
    pdf.sumario(composicao, rotulos, {rotulo: 1 for rotulo in rotulos})
    paginas = [[linha[0] for linha in pagina[0]] for pagina in composicao.paginar()]
    com_sumario = [numero for numero, pagina in enumerate(paginas) if "Sumário" in pagina]
    assert com_sumario == [1]
    assert all(not linha.startswith("1. Seção") for linha in paginas[0])
