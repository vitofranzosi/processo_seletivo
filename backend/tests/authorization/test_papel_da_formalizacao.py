"""Quem tem `formalizacao:acessar`, e o que ela não concede (117, `FR-3661`, `D-013`).

A permissão é escrita literalmente em `interface/identidade.py`, como todas as do mapa de papéis, e
a concordância com quem a consome precisa de teste: nada no código as liga.
"""

from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.interface.identidade import DESCRICOES, PAPEIS, permissoes_de
from processo_seletivo.seguranca.application.acessos import catalogo


def test_a_grafia_e_a_mesma_nos_dois_lugares():
    assert nomes.CAPACIDADE == "formalizacao:acessar"
    assert nomes.PAPEL in PAPEIS
    assert PAPEIS[nomes.PAPEL][0] == nomes.NOME_DO_PAPEL


def test_so_o_papel_da_formalizacao_tem_a_permissao():
    """Nenhum papel existente a ganha: quem conduz a seleção não exporta por conduzir (FR-3661)."""
    com_a_permissao = {
        papel for papel, (_, lista) in catalogo().items() if nomes.CAPACIDADE in lista
    }

    assert com_a_permissao == {nomes.PAPEL}


def test_o_papel_da_formalizacao_nao_concede_mais_nada():
    """Uma capacidade só: nem consultar inscrições, nem conferir, nem exportar matrícula."""
    assert permissoes_de([nomes.PAPEL]) == {nomes.CAPACIDADE}


def test_o_papel_tem_descricao():
    assert DESCRICOES[nomes.PAPEL]
