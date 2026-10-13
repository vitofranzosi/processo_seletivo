"""O Edital embute a fonte e mede o texto pelas larguras dela (069, FR-1380, FR-1381, R-006, R-007).

Antes, o documento declarava a Helvetica sem arquivo, e cada leitor a trocava pela que tinha: o
poppler desenhava o negrito como regular (ED-14), e a tabela de larguras do `pdf.py` subestimava
"í", "ì", "î", "ï" e, no negrito, "ª" e "º" — a linha justificada com muitos deles passava da margem
no papel, sem que a composição soubesse.

A fonte embutida é a Edital Sans, subconjunto WinAnsi da Liberation Sans 2.1.5 sob a SIL OFL 1.1
(`fontes/ORIGEM.md`). Só o Edital a usa: o comprovante e a divulgação continuam com a Helvetica,
byte a byte (`tests/contract/test_comprovante_e_divulgacao_byte_a_byte.py`).
"""

import re
import zlib

import pytest

from processo_seletivo.publicacoes.domain import grafia
from processo_seletivo.publicacoes.infrastructure import fonte, pdf
from tests.unit.publicacoes.cenarios_da_auditoria import composto
from tests.unit.publicacoes.test_pdf import documento, snapshot

OBJETO = re.compile(rb"(\d+) 0 obj\n(.*?)\nendobj\n", re.DOTALL)
# Uma linha desenhada, com o espaçamento da justificação quando há.
DESENHADA = re.compile(
    rb"BT (?:([\d.]+) Tw )?/(F\d) ([\d.]+) Tf ([\d.]+) ([\d.]+) Td \((.*?)\) Tj", re.DOTALL
)


def _objetos(pdf_):
    return {int(numero): corpo for numero, corpo in OBJETO.findall(pdf_)}


def _edital():
    return documento(snapshot())


# ---------------------------------------------------------------------------
# T026 — a fonte embutida e a licença
# ---------------------------------------------------------------------------


def test_o_edital_declara_as_duas_fontes_embutidas_nos_recursos_de_sempre():
    objetos = _objetos(_edital())
    paginas = [corpo for corpo in objetos.values() if corpo.startswith(b"<< /Type /Page /Parent")]
    assert paginas
    for pagina in paginas:
        recursos = re.search(rb"/Font << /F1 (\d+) 0 R /F2 (\d+) 0 R >>", pagina)
        assert recursos, pagina[:120]
        for recurso, numero in zip((b"F1", b"F2"), recursos.groups(), strict=True):
            dicionario = objetos[int(numero)]
            assert b"/Subtype /TrueType" in dicionario, recurso
            assert b"/Encoding /WinAnsiEncoding" in dicionario
            descritor = objetos[int(re.search(rb"/FontDescriptor (\d+) 0 R", dicionario)[1])]
            arquivo = objetos[int(re.search(rb"/FontFile2 (\d+) 0 R", descritor)[1])]
            assert arquivo.startswith(b"<< /Filter /FlateDecode /Length1 ")
    assert b"/BaseFont /Helvetica" not in _edital()


def test_o_arquivo_embutido_e_o_ttf_versionado():
    """O fluxo comprimido descomprime no TrueType versionado, byte a byte."""
    for recurso, arquivo in fonte.ARQUIVOS.items():
        lida = fonte.fontes()[recurso]
        assert zlib.decompress(lida.comprimido) == lida.dados, arquivo
        assert lida.dados == (fonte.PASTA / arquivo).read_bytes()


def test_o_subconjunto_cobre_todo_caractere_que_a_grafia_aceita():
    """O que `grafia` aceita é o WinAnsi; tudo isso tem de ter glifo e largura."""
    for byte in range(256):
        try:
            caractere = bytes([byte]).decode("cp1252")
        except UnicodeDecodeError:
            continue
        if not grafia.representavel(caractere) or caractere in "\t\n\r":
            continue
        for recurso in (fonte.REGULAR, fonte.NEGRITO):
            assert byte in fonte.fontes()[recurso].larguras, (recurso, hex(byte), caractere)


def test_os_arquivos_versionados_sao_os_registrados_na_origem():
    assert fonte.conferir() == {}
    origem = (fonte.PASTA / "ORIGEM.md").read_text("utf-8")
    for resumo in fonte.SHA256.values():
        assert resumo in origem


def test_a_licenca_acompanha_os_arquivos():
    """FR-1380: a licença da versão distribuída, verificada e junto da fonte."""
    licenca = (fonte.PASTA / "LICENSE").read_text("utf-8")
    assert "SIL OPEN FONT LICENSE Version 1.1" in licenca
    assert "Reserved Font Name Liberation" in licenca


def test_o_subconjunto_nao_usa_nome_reservado():
    """A OFL não deixa versão modificada usar nome reservado: a família é a Edital Sans."""
    documento_ = _edital()
    assert b"/BaseFont /EDITAA+EditalSans-Regular" in documento_
    assert b"/BaseFont /EDITAB+EditalSans-Bold" in documento_
    for reservado in (b"Liberation", b"Arimo", b"Tinos", b"Cousine"):
        assert b"/BaseFont /" + reservado not in documento_


# ---------------------------------------------------------------------------
# T027 — a medição
# ---------------------------------------------------------------------------


def _linhas(pdf_):
    for espaco, recurso, tamanho, x, _, texto in DESENHADA.findall(pdf_):
        yield (
            float(espaco or 0),
            recurso.decode(),
            float(tamanho),
            float(x),
            texto.replace(b"\\(", b"(")
            .replace(b"\\)", b")")
            .replace(b"\\\\", b"\\")
            .decode("cp1252"),
        )


def _com_acentos():
    """Um parágrafo justificado de "í", "ª" e "º" — os que a tabela da Helvetica subestimava."""
    conteudo = snapshot()
    for secao in conteudo["sections"]:
        if secao["key"] == "disposicoes-finais":
            secao["content"] = " ".join(
                f"Íris píí íí ªª ºº {n}ª e {n}º índice íntegro" for n in range(1, 40)
            )
    perfil = conteudo["profiles"][0]
    perfil["requirements"] = ["ª º í " * 40]
    return conteudo


@pytest.mark.parametrize("caso", ["A", "B", "acentos"])
def test_nenhuma_linha_passa_da_margem_pela_metrica_da_fonte_embutida(caso):
    """FR-1381 e SC-519: medida pela fonte que o arquivo embute, nenhuma linha passa da margem."""
    pdf_ = documento(_com_acentos()) if caso == "acentos" else composto(caso)
    margem_direita = pdf.LARGURA - pdf.MARGEM
    for espaco, recurso, tamanho, x, texto in _linhas(pdf_):
        largura = fonte.METRICA.largura(texto, tamanho, recurso) + espaco * texto.count(" ")
        assert x + largura <= margem_direita + 0.5, (texto, x + largura)


def test_a_helvetica_do_comprovante_continua_medindo_como_antes():
    """O comprovante não muda (FR-1383): a Helvetica mede "í" como 222, como sempre mediu."""
    assert pdf.largura("í", 1000) == 222
    assert pdf.HELVETICA.largura("í", 1000) == 222
    assert fonte.METRICA.largura("í", 1000) == 278


def test_os_fluxos_de_pagina_continuam_sem_compactacao():
    """R-006: só o arquivo da fonte é comprimido; cada página é `<< /Length N >>`."""
    objetos = _objetos(_edital())
    for corpo in objetos.values():
        if not corpo.startswith(b"<< /Type /Page /Parent"):
            continue
        conteudo = objetos[int(re.search(rb"/Contents (\d+) 0 R", corpo)[1])]
        assert re.match(rb"<< /Length \d+ >>\nstream\n", conteudo), conteudo[:60]
