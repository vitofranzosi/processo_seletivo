"""O que faz de cada documento composto pelo GPS um PDF/A-2, conferido sem o validador (178).

O veraPDF roda só no CI (job `pdfa`), sobre os exemplares de `tests/pdfa/exemplares.py`. Estes casos
conferem, em todo ambiente, que cada exemplar traz os acréscimos que o validador cobra (FR-8171): o
identificador derivado do corpo, os metadados que declaram a parte e o nível e repetem o `/Info`, o
perfil de cor versionado, as anotações imprimíveis e a fonte embutida. Uma regressão aparece aqui
antes de chegar ao CI — e o que o validador acrescenta é a leitura independente da norma.
"""

import hashlib
import re
import tomllib
from pathlib import Path

import pytest

from processo_seletivo.publicacoes.infrastructure import pdfa
from processo_seletivo.publicacoes.infrastructure.pdf import (
    CORPO_TEXTO,
    METRICA_DO_EDITAL,
    MODO_PREVIA,
    Composicao,
    render_documento,
    render_edital_pdf,
)
from processo_seletivo.shared.canonical import canonical_sha256
from tests.pdfa import leitura
from tests.pdfa.exemplares import EXEMPLARES, _json

POR_NOME = {exemplar.nome: exemplar for exemplar in EXEMPLARES}


@pytest.fixture(scope="module")
def compostos():
    return {exemplar.nome: exemplar.compor() for exemplar in EXEMPLARES}


def _xmp(documento):
    todos = leitura.objetos(documento)
    return leitura.fluxo(todos[leitura.referencia(leitura.catalogo(documento), b"Metadata")])


# --- O perfil de cor ------------------------------------------------------------------------------


def test_o_perfil_e_o_que_a_origem_registra():
    """FR-8156: o resumo do arquivo versionado é o de `cor/ORIGEM.md`, e a licença está ao lado."""
    assert pdfa.conferir() is None
    origem = (pdfa.PASTA / "ORIGEM.md").read_text(encoding="utf-8")
    assert pdfa.SHA256_DO_PERFIL in origem
    assert "without restriction" in (pdfa.PASTA / "LICENSE").read_text(encoding="utf-8")


def test_o_perfil_e_um_icc_rgb_de_monitor():
    """O cabeçalho que a ISO 19005-2 lê: classe `mntr`, espaço `RGB `, e três componentes."""
    perfil = pdfa.perfil()
    assert int.from_bytes(perfil[:4], "big") == len(perfil)
    assert perfil[12:16] == b"mntr"
    assert perfil[16:20] == b"RGB "
    assert perfil[36:40] == b"acsp"


# --- Cada exemplar --------------------------------------------------------------------------------


def test_sao_os_nove_tipos_da_fr_8150():
    assert len(EXEMPLARES) == 9
    assert len(POR_NOME) == 9


# O que cada exemplar tem de continuar exercitando. Os exemplares saem dos cenários de outros
# testes (`tests/pdfa/exemplares.py`), e um cenário reduzido lá esvaziaria em silêncio o que o
# veraPDF valida aqui: sem links, a regra das anotações imprimíveis nem é testada.
EXERCITA = {
    "edital": {b"/Subtype /Link": 1, b"/Type /Outlines": 1},
    "retificacao": {b"/Subtype /Link": 1, b"/Type /Outlines": 1},
    "relatorio-do-edital": {b"/Subtype /Link": 1, b"/S /Table": 1, b"/S /Figure": 1},
    "relatorio-consolidado": {b"/S /Table": 1, b"/S /Figure": 1, b"/Type /Outlines": 1},
}
# E a lista que atravessa páginas, com o cabeçalho repetido, na família.
PAGINAS_NO_MINIMO = {"resultado": 2, "edital": 2, "relatorio-do-edital": 2}


@pytest.mark.parametrize("nome", sorted(EXERCITA))
def test_o_exemplar_continua_exercitando_o_que_a_norma_cobra(compostos, nome):
    for marca, minimo in EXERCITA[nome].items():
        assert leitura.contagem(compostos[nome], marca) >= minimo, marca


@pytest.mark.parametrize("nome", sorted(PAGINAS_NO_MINIMO))
def test_o_exemplar_continua_com_mais_de_uma_pagina(compostos, nome):
    assert len(leitura.paginas(compostos[nome])) >= PAGINAS_NO_MINIMO[nome]


@pytest.mark.parametrize("nome", sorted(POR_NOME))
def test_o_identificador_e_derivado_do_corpo(compostos, nome):
    """FR-8154: o `/ID` é o resumo de tudo o que vem antes do trailer."""
    documento = compostos[nome]
    corpo, trailer = documento.rsplit(b"trailer", 1)
    assert pdfa.identificador(corpo).encode() in trailer


@pytest.mark.parametrize("nome", sorted(POR_NOME))
def test_os_metadados_declaram_a_parte_e_o_nivel_esperados(compostos, nome):
    """FR-8151, FR-8152: 2u em todos, 2a nos relatórios — e a declaração é a esperada."""
    xmp = _xmp(compostos[nome]).decode("utf-8")
    assert "<pdfaid:part>2</pdfaid:part>" in xmp
    assert f"<pdfaid:conformance>{POR_NOME[nome].nivel}</pdfaid:conformance>" in xmp


@pytest.mark.parametrize("nome", sorted(POR_NOME))
def test_os_metadados_repetem_o_info_e_nada_mais(compostos, nome):
    """FR-8153: o título e o autor do `/Info`, com o mesmo texto; nenhuma data, nenhum produtor."""
    documento = compostos[nome]
    xmp = _xmp(documento).decode("utf-8")
    trailer = documento.rsplit(b"trailer", 1)[1]
    id_info = leitura.referencia(trailer, b"Info")
    titulo = re.search(r'<rdf:li xml:lang="x-default">(.*?)</rdf:li>', xmp)
    autor = re.search(r"<dc:creator><rdf:Seq><rdf:li>(.*?)</rdf:li>", xmp)
    if id_info is None:
        assert titulo is None
        assert autor is None
    else:
        info = leitura.objetos(documento)[id_info]
        # Cada um presente nos dois, ou ausente nos dois — o relatório de unidade sem nome não tem
        # autor em nenhum.
        assert (titulo and _desescapar(titulo[1])) == (leitura.cadeia(info, b"Title") or None)
        assert (autor and _desescapar(autor[1])) == (leitura.cadeia(info, b"Author") or None)
    for proibido in ("CreateDate", "ModifyDate", "MetadataDate", "Producer", "CreatorTool"):
        assert proibido not in xmp
        assert proibido.encode() not in documento.replace(_xmp(documento), b"")


def _desescapar(texto):
    return texto.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


@pytest.mark.parametrize("nome", sorted(POR_NOME))
def test_a_condicao_de_saida_aponta_o_perfil_versionado(compostos, nome):
    """FR-8156: o catálogo declara sRGB, e o perfil embutido é o arquivo versionado, inalterado."""
    documento = compostos[nome]
    catalogo = leitura.catalogo(documento)
    assert b"/OutputIntents [<< /Type /OutputIntent /S /GTS_PDFA1 " in catalogo
    perfil = leitura.objetos(documento)[leitura.referencia(catalogo, b"DestOutputProfile")]
    assert perfil.startswith(b"<< /N 3 /Length ")
    assert leitura.fluxo(perfil) == pdfa.perfil()


@pytest.mark.parametrize("nome", sorted(POR_NOME))
def test_toda_anotacao_e_imprimivel(compostos, nome):
    """FR-8157."""
    for anotacao in leitura.anotacoes(compostos[nome]):
        assert b"/F 4 " in anotacao


@pytest.mark.parametrize("nome", sorted(POR_NOME))
def test_toda_fonte_e_embutida(compostos, nome):
    """FR-8158: nenhuma fonte declarada sem arquivo — a Helvetica saiu de todos."""
    documento = compostos[nome]
    todos = leitura.objetos(documento)
    fontes = [corpo for corpo in todos.values() if corpo.startswith(b"<< /Type /Font ")]
    assert fontes
    for fonte in fontes:
        descritor = todos[leitura.referencia(fonte, b"FontDescriptor")]
        assert leitura.referencia(descritor, b"FontFile2") is not None
    assert b"/BaseFont /Helvetica" not in documento


@pytest.mark.parametrize("nome", sorted(POR_NOME))
def test_o_mesmo_conteudo_da_os_mesmos_bytes(compostos, nome):
    """FR-8155, SC-2821."""
    assert POR_NOME[nome].compor() == compostos[nome]


def test_os_relatorios_continuam_marcados():
    """O nível A se apoia na marcação que a `diagramacao` já fazia (FR-8151)."""
    for nome in ("relatorio-do-edital", "relatorio-consolidado"):
        catalogo = leitura.catalogo(POR_NOME[nome].compor())
        assert b"/MarkInfo << /Marked true >>" in catalogo
        assert b"/StructTreeRoot " in catalogo
        assert b"/Lang (pt-BR)" in catalogo


# --- O que não é PDF/A ----------------------------------------------------------------------------


def test_a_previa_nao_declara_pdfa():
    """FR-8162, D-003: nem metadados, nem condição de saída, nem identificador."""
    snapshot = _json("snapshot_publicado.json")
    from tests.pdfa.exemplares import _contexto_do_edital

    contexto = _contexto_do_edital()
    previa = render_edital_pdf(
        snapshot, canonical_sha256(snapshot), MODO_PREVIA, unidade=contexto["unidade"]
    )
    assert b"/Metadata" not in previa
    assert b"/OutputIntents" not in previa
    assert b"/ID [" not in previa.rsplit(b"trailer", 1)[1]
    assert b"/F 4 " not in previa


def test_a_composicao_medida_pela_helvetica_e_recusada():
    """O arquivo embute a Edital Sans: medir por outra fonte justificaria pela largura errada."""
    composicao = Composicao()
    composicao.escrever("Texto", tamanho=CORPO_TEXTO)
    with pytest.raises(ValueError, match="METRICA_DO_EDITAL"):
        render_documento(composicao, identificacao="Documento")


def test_o_escritor_antigo_continua_sem_pdfa():
    """D-002: `pdfa=False` é o escritor de antes, que só o comprovante antigo pede."""
    composicao = Composicao()
    composicao.escrever("Texto", tamanho=CORPO_TEXTO)
    documento = render_documento(composicao, identificacao="Documento", pdfa=False)
    assert b"/BaseFont /Helvetica " in documento
    assert b"/Metadata" not in documento
    assert b"/ID [" not in documento


def test_a_composicao_medida_pela_fonte_embutida_passa():
    composicao = Composicao(metrica=METRICA_DO_EDITAL)
    composicao.escrever("Texto", tamanho=CORPO_TEXTO)
    assert b"<pdfaid:conformance>U</pdfaid:conformance>" in render_documento(
        composicao, identificacao="Documento"
    )


# --- Os metadados ---------------------------------------------------------------------------------


def test_o_xmp_escapa_o_texto_e_recusa_nivel_desconhecido():
    descricao = pdfa.descricao("Edital nº 1 <A & B>", "Ifes — Cefor")
    xmp = pdfa.xmp(pdfa.NIVEL_U, descricao).decode()
    assert "Edital nº 1 &lt;A &amp; B&gt;" in xmp
    assert "<rdf:li>Ifes — Cefor</rdf:li>" in xmp
    with pytest.raises(ValueError):
        pdfa.xmp("B")


def test_a_descricao_tira_o_que_o_xml_nao_admite_e_o_vazio():
    """Um controle colado do Word tornaria o XMP mal-formado; um autor vazio, um criador vazio."""
    descricao = pdfa.descricao("Edital\x0b nº 1\x00", "  ")
    assert descricao == pdfa.Descricao(titulo="Edital nº 1", autor=None)
    xmp = pdfa.xmp(pdfa.NIVEL_A, descricao).decode()
    assert "dc:creator" not in xmp
    assert "\x0b" not in xmp


def test_o_info_e_os_metadados_saem_da_mesma_descricao():
    from processo_seletivo.publicacoes.infrastructure.pdf import _informacao

    descricao = pdfa.descricao("Relatório", "")
    assert (
        _informacao(descricao)
        == b"<< /Title <FEFF" + "Relatório".encode("utf-16-be").hex().upper().encode() + b"> >>"
    )


def test_o_relatorio_de_unidade_sem_nome_nao_declara_autor():
    """O caso que nenhum exemplar cobria: `autor=""` sai do `/Info` e dos metadados juntos."""
    from processo_seletivo.interface import relatorio_pdf
    from tests.unit.interface.test_diagramacao_do_relatorio_do_edital import _relatorio

    relatorio = _relatorio()
    relatorio.unidade["nome"] = ""
    documento = relatorio_pdf.compor(relatorio, emissao=1)
    trailer = documento.rsplit(b"trailer", 1)[1]
    info = leitura.objetos(documento)[leitura.referencia(trailer, b"Info")]
    assert b"/Author" not in info
    assert b"dc:creator" not in _xmp(documento)


def test_o_xmp_sem_info_declara_so_a_conformidade():
    xmp = pdfa.xmp(pdfa.NIVEL_U).decode()
    assert "dc:" not in xmp
    assert xmp.startswith('<?xpacket begin="﻿"')


def test_o_identificador_tem_dezesseis_bytes_e_depende_do_corpo():
    um, outro = pdfa.identificador(b"a"), pdfa.identificador(b"b")
    assert um != outro
    resumo = hashlib.sha256(b"a").hexdigest()[:32].upper()
    assert um == f"/ID [<{resumo}> <{resumo}>]"


# --- Nenhuma dependência nova ---------------------------------------------------------------------


def test_producao_nao_ganha_dependencia():
    """FR-8170, SC-2826: nem biblioteca de PDF, nem validador, nem conversor nas dependências."""
    projeto = tomllib.loads(
        (Path(__file__).resolve().parents[3] / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    nomes = " ".join(projeto["dependencies"]).lower()
    for proibido in ("pikepdf", "pypdf", "reportlab", "verapdf", "ghostscript", "pymupdf", "fitz"):
        assert proibido not in nomes
