"""Quem tem `material:gerar`, e o que ela não concede (111, `D-012`, `FR-3403`).

A permissão é escrita literalmente em `interface/identidade.py`, como todas as do mapa de papéis, e
a concordância com quem a consome precisa de teste: nada no código as liga.
"""

from processo_seletivo.interface import kit_de_divulgacao
from processo_seletivo.interface.identidade import DESCRICOES, PAPEIS, permissoes_de


def test_a_grafia_e_a_mesma_nos_dois_lugares():
    assert kit_de_divulgacao.PERMISSAO == "material:gerar"


def test_so_o_papel_da_comunicacao_tem_a_permissao():
    """Nenhum papel existente a ganha: quem divulga não é quem pratica o ato."""
    com_a_permissao = {
        papel for papel, (_, lista) in PAPEIS.items() if kit_de_divulgacao.PERMISSAO in lista
    }

    assert com_a_permissao == {"comunicacao"}


def test_o_papel_da_comunicacao_nao_concede_mais_nada():
    assert permissoes_de(["comunicacao"]) == {kit_de_divulgacao.PERMISSAO}


def test_o_papel_tem_descricao():
    assert DESCRICOES["comunicacao"]
