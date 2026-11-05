"""O que é só da família Libras (119, T048).

As regras gerais dos templates rodam nela pelo registro (`test_peca_das_familias.py`,
`test_familias.py`, `test_referencias.py`); aqui fica o que a declaração dela tem de próprio: a
Inter no lugar da Helvetica Neue (P-2) e a chamada sem balão.
"""

import dataclasses

import pytest

from processo_seletivo.interface import kit_fontes, kit_peca
from processo_seletivo.interface.kit_familias import libras
from tests.unit.kit import geometria
from tests.unit.kit.test_textos import _ficha, _oferta

TEMPLATES = [libras.POST, libras.STORY, libras.BANNER]


def _compor(ficha, template, imagem=0):
    escolha = kit_peca.Escolha(imagem=libras.IMAGENS[imagem].chave)
    return kit_peca.compor_template(ficha, template, escolha)


def _uma_oferta(nome="Libras Básico"):
    ofertas = (dataclasses.replace(_oferta("1", nome, "", 30), carga_horaria="60h"),)
    return _ficha(ofertas=ofertas, nomes_iguais=False, total_de_vagas=30)


def test_a_helvetica_neue_dos_slides_e_a_inter():
    """P-2: o título em Inter negrito e o corpo em Inter regular, as duas sem lacuna na grafia."""
    assert libras.FONTES["titulo"] == "inter-negrito"
    assert libras.FONTES["corpo"] == "inter-regular"
    for chave in ("inter-leve", "inter-regular", "inter-negrito"):
        assert kit_fontes.FONTES[chave].familia == "Inter"
        assert kit_fontes.FONTES[chave].sem_grafia == ""


@pytest.mark.parametrize("caractere", ["º", "ª", "–", "—", "“", "”", "‘", "’", "ç", "ã", "É"])
def test_a_inter_desenha_a_grafia_do_edital(caractere):
    for chave in ("inter-leve", "inter-regular", "inter-negrito"):
        assert kit_fontes.sem_glifo(caractere, chave) == []


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.formato.chave)
@pytest.mark.parametrize("imagem", [0, 1])
def test_a_chamada_fica_sobre_o_amarelo_sem_balao(template, imagem):
    """Sem ativo de balão: a chamada é texto direto no fundo, entre os traços da imagem."""
    peca = _compor(_uma_oferta(), template, imagem)
    assert geometria.problemas(peca) == []
    assert not any(getattr(e, "campo", "") == "balao" for e in peca.elementos)
    chamada = next(t for t in peca.textos if t.campo == "chamada_a_acao")
    assert chamada.conteudo == template.formato.chamada_a_acao
    assert chamada.fonte == "unbounded-regular" and chamada.fundo == libras.PALETA["fundo"]


@pytest.mark.parametrize("template", [libras.POST, libras.STORY], ids=lambda t: t.formato.chave)
def test_numero_e_prazo_em_unbounded_negrito_e_a_oferta_em_inter(template):
    peca = _compor(_uma_oferta(), template)
    por_campo = {t.campo: t for t in peca.textos}
    assert por_campo["identificacao"].fonte == "unbounded-negrito"
    assert por_campo["periodo_curto"].fonte == "unbounded-negrito"
    assert por_campo["oferta:1"].fonte == "inter-regular"
    assert por_campo["oferta:1"].cor == libras.PALETA["preto"]
