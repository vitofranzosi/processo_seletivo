"""O que é só da família Aperfeiçoamento (119, T050).

As regras gerais dos templates rodam nela pelo registro (`test_peca_das_familias.py`,
`test_familias.py`, `test_referencias.py`); aqui fica o que a declaração dela tem de próprio.
"""

import dataclasses

import pytest

from processo_seletivo.interface import kit_fontes, kit_peca
from processo_seletivo.interface.kit_familias import aperfeicoamento
from tests.unit.kit import geometria
from tests.unit.kit.test_textos import _ficha, _oferta


def _com_oferta(nome):
    ofertas = (dataclasses.replace(_oferta("1", nome, "", 40), carga_horaria="180h"),)
    return _ficha(ofertas=ofertas, nomes_iguais=False, total_de_vagas=40)


def _compor(ficha, template):
    escolha = kit_peca.Escolha(imagem=aperfeicoamento.IMAGENS[0].chave)
    return kit_peca.compor_template(ficha, template, escolha)


def test_a_unica_lacuna_da_unbounded_e_o_micro():
    """A Unbounded de origem não desenha «µ»; o registro o declara, e só ele (FR-3823)."""
    assert aperfeicoamento.FONTES["destaque"] == "unbounded-regular"
    assert kit_fontes.FONTES["unbounded-regular"].sem_grafia == "µ"


@pytest.mark.parametrize("template", [aperfeicoamento.POST, aperfeicoamento.STORY])
def test_micro_numa_oferta_recusa_nomeando_a_unbounded(template):
    """EC-13: a oferta é desenhada em Unbounded, que não tem o glifo; a peça não troca de fonte."""
    with pytest.raises(kit_peca.PecaRecusada) as recusa:
        _compor(_com_oferta("Microscopia em µm"), template)
    assert "Unbounded" in recusa.value.motivo and "«µ»" in recusa.value.motivo


def test_o_banner_nao_lista_ofertas_e_o_micro_nao_o_alcanca():
    """EC-6: sem bloco de ofertas no banner, o nome da oferta não passa pela Unbounded."""
    peca = _compor(_com_oferta("Microscopia em µm"), aperfeicoamento.BANNER)
    assert geometria.problemas(peca) == []
    assert all("µ" not in texto.conteudo for texto in peca.textos)


@pytest.mark.parametrize("template", [aperfeicoamento.POST, aperfeicoamento.STORY])
def test_a_oferta_sai_em_unbounded_verde_sobre_o_painel(template):
    """A lista do slide: Unbounded verde; o prazo, em Lexend, como o cabeçalho."""
    peca = _compor(_com_oferta("Formação Docente para EaD"), template)
    assert geometria.problemas(peca) == []
    oferta = next(t for t in peca.textos if t.campo == "oferta:1")
    periodo = next(t for t in peca.textos if t.campo == "periodo_curto")
    assert oferta.fonte == "unbounded-regular" and oferta.cor == aperfeicoamento.PALETA["verde"]
    assert oferta.fundo == aperfeicoamento.PALETA["azul_escuro"]
    assert periodo.fonte == "lexend-extranegrito"
