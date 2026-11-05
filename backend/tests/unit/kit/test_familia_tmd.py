"""O que é só da família TMD (119, T052).

As regras gerais dos templates rodam nela pelo registro (`test_peca_das_familias.py`,
`test_familias.py`, `test_referencias.py`); aqui fica o que a declaração dela tem de próprio: a
família sem banco de imagens (EC-20), com o fundo fixo desenhado pelo projeto, e a Inter leve no
lugar da Helvetica Neue Light (P-2).
"""

import dataclasses
import importlib.util
from pathlib import Path

import pytest

from processo_seletivo.interface import kit_peca
from processo_seletivo.interface.kit_familias import tmd
from processo_seletivo.interface.kit_peca import Figura
from tests.unit.kit import geometria
from tests.unit.kit.test_textos import _ficha, _oferta

TEMPLATES = [tmd.POST, tmd.STORY, tmd.BANNER]
ROTEIRO = Path(__file__).resolve().parents[3] / "scripts" / "desenhar_fundo_do_tmd.py"


def _roteiro():
    """O roteiro que desenhou os fundos, lido do arquivo: `scripts/` não é pacote."""
    especificacao = importlib.util.spec_from_file_location("desenhar_fundo_do_tmd", ROTEIRO)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def _uma_oferta(nome="Técnico em Multimeios Didáticos"):
    ofertas = (dataclasses.replace(_oferta("1", nome, "", 40), carga_horaria="1200h"),)
    return _ficha(ofertas=ofertas, nomes_iguais=False, total_de_vagas=40)


def test_a_familia_nao_tem_banco_de_imagens():
    """EC-20: a tela não pede imagem, e a escolha sem imagem compõe."""
    assert tmd.FAMILIA.imagens == ()


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.formato.chave)
def test_a_peca_sai_com_o_fundo_fixo_do_formato(template):
    peca = kit_peca.compor_template(_uma_oferta(), template, kit_peca.Escolha())
    assert geometria.problemas(peca) == []
    assert peca.imagem is None
    fundo = peca.elementos[0]
    assert isinstance(fundo, Figura) and fundo.campo == "fundo"
    assert fundo.caixa == (0, 0, template.formato.largura, template.formato.altura)
    assert fundo.arquivo == f"fundo-{template.formato.chave}.png"
    # O fundo não é obstáculo: o teste geométrico confere os de dentro dele, declarados.
    assert "fundo" not in template.ativos_posicionados


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.formato.chave)
def test_o_alternativo_nao_descreve_imagem_escolhida(template):
    peca = kit_peca.compor_template(_uma_oferta(), template, kit_peca.Escolha())
    assert peca.alternativo.startswith("Peça de divulgação do ")
    assert ", na identidade TMD." in peca.alternativo


@pytest.mark.parametrize("template", [tmd.POST, tmd.STORY], ids=lambda t: t.formato.chave)
def test_o_prazo_em_inter_leve_e_o_titulo_em_archivo_black_dourado(template):
    peca = kit_peca.compor_template(_uma_oferta(), template, kit_peca.Escolha())
    por_campo = {t.campo: t for t in peca.textos}
    assert por_campo["periodo_curto"].fonte == "inter-leve"
    assert por_campo["oferta:1"].fonte == "inter-regular"
    titulos = [t for t in peca.textos if t.fonte == "archivo-black"]
    assert titulos and all(t.cor == tmd.PALETA["dourado"] for t in titulos)
    chamada = por_campo["chamada_a_acao"]
    assert chamada.cor == tmd.PALETA["dourado"] and chamada.fundo == tmd.PALETA["fundo"]


def test_as_medidas_do_desenho_sao_as_dos_obstaculos():
    """A barra e a ilustração do roteiro de desenho caem dentro do que a família declara."""
    roteiro = _roteiro()
    for template in TEMPLATES:
        medidas = roteiro.FORMATOS[template.formato.chave]
        obstaculos = template.dimensoes["obstaculos"]
        x, y, largura, altura = medidas["barra"]
        assert obstaculos["colina_a_esquerda"] == (0, y, x, y + altura)
        assert obstaculos["colina_a_direita"][0] == x + largura
        ix, iy, escala = medidas["ilustracao"]
        # A ilustração ocupa 400 × 440 a partir de (ix, iy), mais a lâmpada, que sobe até 27.
        ox0, oy0, ox1, oy1 = obstaculos["ilustracao"]
        assert ox0 <= ix + 10 * escala and oy0 <= iy + 27 * escala
        assert ox1 >= min(ix + 410 * escala, template.formato.largura)
        assert oy1 >= iy + 430 * escala
