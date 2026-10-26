"""A diagramação do Relatório Consolidado de Gestão: a qualidade editorial verificável (100).

A revisão visual de 24/10/2026 reprovou um PDF que passava em todo teste de número: indicadores em
tabela partida entre páginas, gráfico trocado por duas linhas, título sozinho no pé. Estes casos
prendem o que a maquete aprovada pede — e o fazem pela paginação, que é o que decide onde cada bloco
cai, com conjuntos de 1 a 60 Editais. A inspeção a olho, das páginas renderizadas, está registrada
em `doc/estudo-relatorio-consolidado-de-gestao-2026-10-24/revisao-visual.md`.
"""

import re
from datetime import datetime

import pytest

from processo_seletivo.interface import relatorio_consolidado_pdf as pdf
from processo_seletivo.interface.diagramacao import (
    BASE,
    TOPO,
    Atencao,
    Barras,
    Cartoes,
    Colunas,
    Subtitulo,
    Tabela,
    Texto,
    TituloDeSecao,
)
from processo_seletivo.processos.models import Edital
from tests.interface.test_fluxo import texto_de_pdf_bytes
from tests.unit.interface.test_relatorio_consolidado import ZONA, fatos, perfil, somar

ENVIOS = [datetime(2026, m, 10, tzinfo=ZONA) for m in (3, 3, 4, 5, 5, 5)]


def _conjunto_de(n, *, envios=ENVIOS):
    editais = []
    for i in range(n):
        status = Edital.Status.CANCELADO if i == 2 else Edital.Status.ENCERRADO
        editais.append(
            fatos(
                str(10 + i),
                status=status,
                perfis=[perfil(2 + i % 3, 10 + 3 * i), perfil(0, 4, reserva="sem limite")],
                envios=envios,
                apuradas=2,
                habilitadas=2,
                convocacoes=(3, 2, 1, 0),
                recursos=(2, 1, 1, 0, 0),
            )
        )
    return somar(*editais)


def _documento(c, emissao=1):
    documento = pdf.documento(c, emissao=emissao)
    documento.paginar()
    return documento


def _tipos(pagina):
    return [type(colocacao.bloco) for colocacao in pagina]


@pytest.fixture(params=[1, 5, 12, 60], ids=lambda n: f"{n}-editais")
def documento(request):
    return _documento(_conjunto_de(request.param))


def test_a_primeira_pagina_e_o_painel_inteiro(documento):
    """1. Os seis indicadores e os pontos de atenção estão na primeira página."""
    primeira = documento.paginas[0]
    assert Cartoes in _tipos(primeira)
    assert Atencao in _tipos(primeira)
    cartoes = next(c.bloco for c in primeira if isinstance(c.bloco, Cartoes))
    assert len(cartoes.cartoes) == 6


def test_cartao_e_grupo_nao_se_partem(documento):
    """2. Cartões, atenção e colunas aparecem uma vez só: não se dividem entre páginas."""
    todos = [c.bloco for pagina in documento.paginas for c in pagina]
    assert sum(isinstance(b, Cartoes) for b in todos) == 1
    assert sum(isinstance(b, Atencao) for b in todos) == 1
    assert sum(isinstance(b, Colunas) for b in todos) == 3


def test_titulo_nunca_fica_sozinho_no_pe(documento):
    """3. Título de seção ou subtítulo nunca é o último bloco de uma página com seguinte."""
    for pagina in documento.paginas[:-1]:
        assert not isinstance(pagina[-1].bloco, TituloDeSecao | Subtitulo), pagina[-1].bloco.trechos


def test_blocos_cabem_na_pagina_e_nao_se_sobrepoem(documento):
    """6. Nada sai da área útil e nenhum bloco cobre outro."""
    for pagina in documento.paginas:
        anterior = TOPO + 0.01
        for colocacao in pagina:
            assert colocacao.topo <= anterior + 0.01
            assert colocacao.topo - colocacao.altura >= BASE - 0.01
            anterior = colocacao.topo - colocacao.altura


def test_o_grafico_aparece_quando_ha_meses_para_comparar():
    """4. Barras com dois meses ou mais; frase com um mês; ausência dita sem envio."""

    def blocos(c):
        return [col.bloco for pagina in _documento(c).paginas for col in pagina]

    def colunas(c):
        return [b for b in blocos(c) if isinstance(b, Colunas)][0]

    com_serie = colunas(_conjunto_de(3))
    assert any(isinstance(b, Barras) for b in com_serie.direita)
    barras = next(b for b in com_serie.direita if isinstance(b, Barras))
    assert barras.itens == [("mar/2026", 4), ("abr/2026", 2), ("mai/2026", 6)]
    assert "mar/2026, 4" in barras.alt

    um_mes = colunas(_conjunto_de(3, envios=[datetime(2026, 3, 1, tzinfo=ZONA)]))
    texto = next(b for b in um_mes.direita if isinstance(b, Texto) and not isinstance(b, Subtitulo))
    assert "com um mês só" in texto.trechos[0].texto
    nenhum = colunas(_conjunto_de(3, envios=[]))
    assert any(
        isinstance(b, Texto) and "Nenhuma inscrição enviada" in b.trechos[0].texto
        for b in nenhum.direita
    )


def test_tabela_longa_continua_com_o_cabecalho_repetido():
    """5. Com 60 Editais, a tabela por Edital atravessa páginas — e cada parte tem cabeçalho."""
    documento = _documento(_conjunto_de(60))
    partes = [
        (indice, col.bloco)
        for indice, pagina in enumerate(documento.paginas)
        for col in pagina
        if isinstance(col.bloco, Tabela)
        and (col.bloco.cabecalho or [])[:3] == ["Edital", "Seleção", "Perfis"]
    ]
    assert len({indice for indice, _ in partes}) >= 2
    assert all(tabela.cabecalho == partes[0][1].cabecalho for _, tabela in partes)
    assert sum(len(tabela.linhas) for _, tabela in partes) == 59


def test_links_so_quando_o_endereco_vale_para_quem_recebe():
    """7. Emissão local não imprime endereço; com endereço público, o link abre a seleção."""
    c = _conjunto_de(3)
    c.enderecos_locais = True
    local = pdf.compor(c, emissao=1)
    assert b"/URI" not in local
    assert "ambiente local" in " ".join(texto_de_pdf_bytes(local).split())
    c.enderecos_locais = False
    c.enderecos = {
        linha.edital.pk: f"https://selecao.ifes.edu.br/s/{i}" for i, linha in enumerate(c.relacao)
    }
    publico = pdf.compor(c, emissao=1)
    assert publico.count(b"/S /URI") == 3
    assert b"localhost" not in publico


def test_toda_pagina_diz_o_conjunto_a_data_e_a_emissao():
    """8. A faixa de toda página identifica o documento, o instante e a emissão."""
    c = _conjunto_de(12)
    bytes_ = pdf.compor(c, emissao=7)
    paginas = re.findall(rb"<< /Length \d+ >>\nstream\n(.*?)\nendstream", bytes_, re.DOTALL)
    paginas = [p for p in paginas if b"Tj" in p]
    assert len(paginas) >= 4
    for numero, conteudo in enumerate(paginas, 1):
        texto = texto_de_pdf_bytes(b"<< /Length 1 >>\nstream\n" + conteudo + b"\nendstream")
        assert "Relatório Consolidado de Gestão · 1º semestre de 2026" in texto
        assert "emissão nº 7" in texto
        assert f"página {numero} de {len(paginas)}" in texto


def test_poucos_e_muitos_editais_mantem_o_painel_e_o_anexo_em_pagina_propria():
    """9. Com 1 e com 60 Editais: painel na primeira página, anexo abrindo página."""
    for n in (1, 60):
        documento = _documento(_conjunto_de(n))
        assert Cartoes in _tipos(documento.paginas[0])
        abertura = [
            pagina[0].bloco
            for pagina in documento.paginas
            if isinstance(pagina[0].bloco, TituloDeSecao)
        ]
        assert any(t.trechos[0].texto == "Anexo técnico" for t in abertura), n


def test_a4_marcado_e_deterministico():
    """10. A4; arquivo marcado (estrutura, idioma, figura com texto alternativo); mesmos bytes."""
    c = _conjunto_de(5)
    primeira, segunda = pdf.compor(c, emissao=2), pdf.compor(c, emissao=2)
    assert primeira == segunda
    assert b"/MediaBox [0 0 595 842]" in primeira
    for marca in (
        b"/StructTreeRoot",
        b"/MarkInfo << /Marked true >>",
        b"/Lang (pt-BR)",
        b"/S /Figure",
        b"/S /H1",
        b"/S /Table",
        b"/S /TH",
        b"/Alt ",
    ):
        assert marca in primeira, marca
    assert b"/Artifact BMC" in primeira, "faixa, fios e fundos são artefatos"


def test_o_titulo_e_o_da_finalidade_institucional():
    texto = " ".join(texto_de_pdf_bytes(pdf.compor(_conjunto_de(2), emissao=1)).split())
    assert "Relatório Consolidado de Gestão dos Processos Seletivos" in texto
