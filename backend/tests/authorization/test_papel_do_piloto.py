"""Quem tem `assistente:piloto`, e o que ela não concede (071, `D-001`, `FR-1461`).

A permissão é escrita literalmente em `interface/identidade.py`, como todas as do mapa de papéis, e
a concordância com quem a consome precisa de teste: nada no código as liga.
"""

from processo_seletivo.duvidas.application import perguntar
from processo_seletivo.interface.identidade import PAPEIS, permissoes_de


def test_a_grafia_e_a_mesma_nos_dois_lugares():
    assert perguntar.PERMISSAO == "assistente:piloto"


def test_so_o_papel_do_piloto_tem_a_permissao():
    """Nenhum papel existente a ganha: o piloto tem participantes escolhidos."""
    com_a_permissao = {
        papel for papel, (_, lista) in PAPEIS.items() if perguntar.PERMISSAO in lista
    }

    assert com_a_permissao == {"participante-piloto-assistente"}


def test_o_papel_do_piloto_nao_concede_mais_nada():
    assert permissoes_de(["participante-piloto-assistente"]) == {perguntar.PERMISSAO}
