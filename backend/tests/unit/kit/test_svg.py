"""O SVG e o PNG da peça (111, FR-3422, FR-3433, FR-3438, D-007, D-008, D-009, D-021).

Os cabeçalhos da exportação (política própria, `nosniff`, anexo) estão nos testes da interface;
aqui, o arquivo: bem formado, com cada texto escapado e marcado pelo campo, a fonte embutida só
quando pedida, nenhum recurso fora de `data:`, e os mesmos bytes a cada geração.
"""

import base64
import re
import struct
import xml.etree.ElementTree as ET

import pytest

from processo_seletivo.interface import kit_pacote, kit_peca
from processo_seletivo.publicacoes.infrastructure import fonte
from tests.unit.kit.test_textos import _ficha

SVG = "{http://www.w3.org/2000/svg}"


def _svg(ficha=None, **kwargs):
    ficha = ficha or _ficha()
    return kit_peca.svg(kit_peca.compor(ficha), ficha, **kwargs)


def test_bem_formado_com_titulo_e_descricao():
    ficha = _ficha()
    peca = kit_peca.compor(ficha)
    raiz = ET.fromstring(kit_peca.svg(peca, ficha))
    assert (raiz.get("width"), raiz.get("height")) == ("1080", "1350")
    assert raiz.get("role") == "img"
    assert raiz.find(f"{SVG}title").text.startswith("Edital nº 91/2026")
    assert raiz.find(f"{SVG}desc").text == peca.alternativo


def test_cada_texto_leva_o_campo_e_o_conteudo_medido():
    ficha = _ficha()
    peca = kit_peca.compor(ficha)
    raiz = ET.fromstring(kit_peca.svg(peca, ficha))
    desenhados = [(t.get("data-campo"), t.text) for t in raiz.iter(f"{SVG}text")]
    assert desenhados == [(t.campo, t.conteudo) for t in peca.textos]


def test_valor_entra_escapado_como_no_de_texto():
    ficha = _ficha(titulo_sem_numero='Curso <b>"A&B"</b> onload=x')
    svg = _svg(ficha)
    assert "<b>" not in svg
    raiz = ET.fromstring(svg)
    titulo = [t.text for t in raiz.iter(f"{SVG}text") if t.get("data-campo") == "titulo_sem_numero"]
    assert " ".join(titulo) == 'Curso <b>"A&B"</b> onload=x'
    assert not any(a.startswith("on") for e in raiz.iter() for a in e.attrib)


def test_nenhum_recurso_fora_de_data():
    svg = _svg(fonte_embutida=True)
    referencias = re.findall(r'href="([^"]+)"', svg) + re.findall(r"url\(([^)]+)\)", svg)
    assert referencias
    assert all(ref.startswith("data:") for ref in referencias)
    assert "<script" not in svg and "xlink:href" not in svg


def test_fonte_embutida_so_na_exportacao():
    assert "@font-face" not in _svg()
    embutido = _svg(fonte_embutida=True)
    faces = re.findall(r"font-weight:(\d+);src:url\(data:font/ttf;base64,([^)]+)\)", embutido)
    assert [peso for peso, _ in faces] == ["400", "700"]
    for (_, dados), recurso in zip(faces, (fonte.REGULAR, fonte.NEGRITO), strict=True):
        assert base64.b64decode(dados) == fonte.fontes()[recurso].dados


def test_mesma_ficha_mesmo_svg():
    assert _svg() == _svg()
    assert _svg(fonte_embutida=True) == _svg(fonte_embutida=True)


# ---- PNG (D-007) ----------------------------------------------------------------------------

sem_rasterizador = pytest.mark.skipif(
    not kit_pacote.disponivel(), reason="o `resvg-py` não está instalado neste ambiente"
)


@sem_rasterizador
def test_png_1080_por_1350_e_os_mesmos_bytes():
    svg = _svg()
    png = kit_pacote.rasterizar(svg)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", png[16:24]) == (1080, 1350)
    assert kit_pacote.rasterizar(svg) == png


@sem_rasterizador
def test_o_rasterizador_ignora_a_fonte_embutida():
    """O PNG sai das fontes passadas por arquivo; o `<style>` do anexo não muda nenhum pixel."""
    assert kit_pacote.rasterizar(_svg(fonte_embutida=True)) == kit_pacote.rasterizar(_svg())


@sem_rasterizador
def test_versao_do_rasterizador():
    assert kit_pacote.versao_do_rasterizador() == "resvg-py 0.5.0"
