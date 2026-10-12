"""A navegação no arquivo do Edital (069, FR-1384 a FR-1388, R-012, SC-520, SC-523).

Título e autor no `/Info`, idioma e preferências no catálogo, marcadores de cada seção e subseção
apontando para a página em que ela começa, links do sumário e dos endereços que o texto escreve.
Sem data e sem `/ID`: o mesmo snapshot dá os mesmos bytes. Sem `/StructTreeRoot`: o PDF continua sem
marcação, e isso é limitação declarada, e não promessa.

Os objetos são lidos pela própria gramática do arquivo, sem biblioteca: o guardião de
`test_leitura_do_documento_submetido.py` não deixa entrar leitor de PDF no produto.
"""

import re

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.cenarios_da_auditoria import (
    composto,
    congelado,
    levado_ao_catalogo_novo,
    por_perguntas,
    variante_de_b,
)
from tests.unit.publicacoes.test_pdf import paginas_de

OBJETO = re.compile(rb"(\d+) 0 obj\n(.*?)\nendobj\n", re.DOTALL)


DOCUMENTOS = {
    "A": lambda: por_perguntas("A"),
    "B": lambda: por_perguntas("B"),
    "variante de B": lambda: por_perguntas("B", variante_de_b()),
    "A na apresentação plana": lambda: composto("A"),
}


def _objetos(documento):
    return {int(numero): corpo for numero, corpo in OBJETO.findall(documento)}


def _texto_pdf(valor):
    """Uma cadeia do PDF: `<FEFF…>` em UTF-16BE, ou `( … )` literal."""
    if valor.startswith(b"<FEFF"):
        return bytes.fromhex(valor[1:-1].decode()).decode("utf-16-be").lstrip("﻿")
    return valor[1:-1].replace(b"\\(", b"(").replace(b"\\)", b")").decode("latin-1")


def _cadeia(corpo, chave):
    casado = re.search(rb"/" + chave + rb" (<FEFF[0-9A-F]*>|\((?:\\.|[^\\)])*\))", corpo)
    return _texto_pdf(casado[1]) if casado else None


def _referencia(corpo, chave):
    casado = re.search(rb"/" + chave + rb" (\d+) 0 R", corpo)
    return int(casado[1]) if casado else None


def _paginas_do_arquivo(objetos):
    raiz = objetos[2]
    return [int(n) for n in re.findall(rb"(\d+) 0 R", raiz.split(b"/Kids [")[1].split(b"]")[0])]


def _marcadores(objetos):
    """`[(nível, título, página)]`, na ordem, percorrendo `/First` e `/Next`."""
    catalogo = objetos[1]
    paginas = _paginas_do_arquivo(objetos)
    saida = []

    def percorrer(primeiro, nivel):
        atual = primeiro
        while atual:
            corpo = objetos[atual]
            destino = int(re.search(rb"/Dest \[(\d+) 0 R", corpo)[1])
            saida.append((nivel, _cadeia(corpo, b"Title"), paginas.index(destino) + 1))
            if filho := _referencia(corpo, b"First"):
                percorrer(filho, nivel + 1)
            atual = _referencia(corpo, b"Next")

    raiz = objetos[_referencia(catalogo, b"Outlines")]
    percorrer(_referencia(raiz, b"First"), 1)
    return saida


@pytest.fixture(scope="module", params=sorted(DOCUMENTOS))
def caso(request):
    documento = DOCUMENTOS[request.param]()
    return request.param, documento, _objetos(documento)


def test_info_tem_titulo_e_autor_sem_data(caso):
    nome, documento, objetos = caso
    trailer = documento.split(b"trailer", 1)[1]
    info = objetos[int(re.search(rb"/Info (\d+) 0 R", trailer)[1])]
    titulo = _cadeia(info, b"Title")
    assert titulo.startswith("Edital nº 9"), titulo
    assert titulo != titulo.upper(), "o título em caixa mista, e não o anúncio em caixa alta"
    assert _cadeia(info, b"Author") == "Ifes — Cefor"
    for data in (b"/CreationDate", b"/ModDate"):
        assert data not in info


def test_o_catalogo_declara_idioma_titulo_na_janela_e_marcadores(caso):
    _, _, objetos = caso
    catalogo = objetos[1]
    assert b"/Lang (pt-BR)" in catalogo
    assert b"/ViewerPreferences << /DisplayDocTitle true >>" in catalogo
    assert b"/PageMode /UseOutlines" in catalogo
    assert _referencia(catalogo, b"Outlines")


def test_os_marcadores_sao_as_secoes_e_subsecoes_na_pagina_em_que_comecam(caso):
    """SC-520: toda seção e subseção, em dois níveis, cada uma na página em que começa."""
    nome, documento, objetos = caso
    marcadores = _marcadores(objetos)
    itens = pdf.itens_do_documento(_conteudo_de(nome))
    secoes = [item for item in itens if item.natureza == "secao"]
    assert [titulo for nivel, titulo, _ in marcadores if nivel == 1] == [
        f"{item.numero}. {item.descricao}" for item in secoes
    ]
    assert len(marcadores) == len(itens)
    assert {nivel for nivel, _, _ in marcadores} <= {1, 2}
    paginas = paginas_de(documento)
    for _, titulo, pagina in marcadores:
        numero = titulo.split(" ", 1)[0]
        assert any(
            linha.startswith(f"{numero} ") and " . ." not in linha for linha in paginas[pagina - 1]
        ), (titulo, pagina)


def _conteudo_de(nome):
    if nome == "variante de B":
        return variante_de_b()
    cenario = nome[0]
    conteudo = congelado(cenario)["content"]
    return conteudo if "plana" in nome else levado_ao_catalogo_novo(conteudo)


def test_o_sumario_diz_a_pagina_em_que_cada_secao_comeca_e_leva_ate_ela(caso):
    """FR-1372 e SC-520: o número impresso no sumário e o link são os da página real."""
    _, documento, objetos = caso
    paginas = paginas_de(documento)
    ids = _paginas_do_arquivo(objetos)
    sumario = paginas[[i for i, p in enumerate(paginas) if "Sumário" in p][0]]
    entradas = [
        (linha.split(" . .")[0], sumario[indice + 1])
        for indice, linha in enumerate(sumario)
        if " . ." in linha
    ]
    assert entradas
    links = [
        corpo for corpo in objetos.values() if b"/Subtype /Link" in corpo and b"/Dest" in corpo
    ]
    assert len(links) == len(entradas)
    for rotulo, impresso in entradas:
        real = next(
            numero
            for numero, pagina in enumerate(paginas, 1)
            if any(
                (linha == rotulo or rotulo.startswith(f"{linha} ")) and " . ." not in linha
                for linha in pagina
            )
        )
        assert int(impresso) == real, rotulo
    destinos = sorted(
        ids.index(int(re.search(rb"/Dest \[(\d+) 0 R", link)[1])) + 1 for link in links
    )
    assert destinos == sorted(int(impresso) for _, impresso in entradas)


def test_os_enderecos_do_texto_viram_link_e_nenhum_e_acrescentado():
    documento = por_perguntas("A")
    objetos = _objetos(documento)
    uris = sorted(
        _texto_pdf(re.search(rb"/URI (\((?:\\.|[^\\)])*\))", corpo)[1])
        for corpo in objetos.values()
        if b"/URI" in corpo
    )
    assert uris == ["mailto:selecao.demo@exemplo.ifes.edu.br"]


def test_sem_identificador_nem_marcacao():
    documento = por_perguntas("B")
    assert b"/ID" not in documento.split(b"trailer", 1)[1]
    assert b"/StructTreeRoot" not in documento
    assert b"/MarkInfo" not in documento


@pytest.mark.parametrize("nome", sorted(DOCUMENTOS))
def test_os_mesmos_bytes_em_duas_composicoes(nome):
    assert DOCUMENTOS[nome]() == DOCUMENTOS[nome]()


def test_os_fluxos_de_pagina_continuam_sem_compactacao():
    objetos = _objetos(por_perguntas("A"))
    for numero in _paginas_do_arquivo(objetos):
        conteudo = objetos[_referencia(objetos[numero], b"Contents")]
        assert re.match(rb"<< /Length \d+ >>\nstream\n", conteudo)


def test_o_pedaco_de_um_endereco_partido_nao_vira_link():
    """A palavra mais larga que a coluna se parte; o primeiro pedaço casaria como endereço."""
    from types import SimpleNamespace

    navegacao = SimpleNamespace(marcadores=[], sumario=[])
    pagina = (
        [
            ("https://selecao.cefor.ifes.ed", pdf.REGULAR, 9.0, 60.0, 600.0, 0.0),
            ("u.br/edital", pdf.REGULAR, 9.0, 60.0, 588.0, 0.0),
            ("e fulano@ifes.ed", pdf.REGULAR, 9.0, 60.0, 576.0, 0.0),
        ],
        [],
    )
    composicao = pdf.Composicao()
    pdf._registrar_enderecos(composicao, "Ver https://selecao.cefor.ifes.edu.br/edital.")
    pdf._registrar_enderecos(composicao, "Escreva a fulano@ifes.edu.br.")
    anotacoes = pdf._anotacoes([pagina], navegacao, pdf.HELVETICA, [], composicao.enderecos)
    assert anotacoes == [[]]


def test_o_endereco_com_acento_vai_em_ascii_no_link():
    assert pdf._uri("https://ifes.edu.br/seleção") == "https://ifes.edu.br/sele%C3%A7%C3%A3o"
    assert pdf._uri("mailto:a@ifes.edu.br") == "mailto:a@ifes.edu.br"
