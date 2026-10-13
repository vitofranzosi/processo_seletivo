"""Quem tem `aviso:enviar`, e o que ela **não** concede (066, `D-004`, `FR-1275`).

A capacidade é escrita literalmente em `interface/identidade.py`, como todas as do mapa de papéis, e
a concordância com quem a consome precisa de teste: nada no código as liga.
"""

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.interface.identidade import PAPEIS, permissoes_de


def test_a_grafia_e_a_mesma_nos_dois_lugares():
    assert nomes.PERMISSAO == "aviso:enviar"


def test_publicador_e_gestor_tem_a_capacidade():
    assert nomes.PERMISSAO in permissoes_de(["publicador"])
    assert nomes.PERMISSAO in permissoes_de(["gestor"])


def test_nenhum_outro_papel_a_tem():
    """A presidência entra pelo vínculo, objeto a objeto, e não por papel."""
    com_a_capacidade = {papel for papel, (_, lista) in PAPEIS.items() if nomes.PERMISSAO in lista}

    assert com_a_capacidade == {"publicador", "gestor"}


def test_avisar_nao_e_publicar_nem_conduzir():
    """Quem só tem a capacidade de avisar não publica, não gere a comissão, não convoca."""
    somente = frozenset({nomes.PERMISSAO})

    assert "resultado:publicar" not in somente
    assert "comissao:gerir" not in somente
    assert nomes.PERMISSAO not in permissoes_de(["julgador", "auditor", "elaborador"])
