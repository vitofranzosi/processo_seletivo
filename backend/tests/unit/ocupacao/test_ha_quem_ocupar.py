"""Se a ordem do recorte ainda tem quem ocupar, sem banco (095, T005, D-005).

A função saiu de `movimento.ha_quem_ocupar` e conta como ela contava: toda posição da ordem
contra as vagas ocupadas. A DP-2 da `095` registra o que isso faz quando todos os autodeclarados
ocupam pela ampla — e o último teste prende esse caso como ele é.
"""

from processo_seletivo.ocupacao.domain import nomes, reversao
from processo_seletivo.ocupacao.domain.reversao import ha_quem_ocupar


def test_mais_posicoes_que_ocupadas():
    assert ha_quem_ocupar(posicoes=[1, 2, 3], ja_ocupadas=2)


def test_tantas_ocupadas_quantas_posicoes():
    assert not ha_quem_ocupar(posicoes=[1, 2, 3], ja_ocupadas=3)


def test_sem_posicao_nao_conta():
    """Quem ficou sem posição na ordem — eliminado, sem nota — não é quem ocupar."""
    assert not ha_quem_ocupar(posicoes=[1, None, None], ja_ocupadas=1)


def test_ordem_vazia():
    assert not ha_quem_ocupar(posicoes=[], ja_ocupadas=0)


def test_posicoes_divididas_contam_uma_por_pessoa():
    assert ha_quem_ocupar(posicoes=[1, 1, 3], ja_ocupadas=2)


def test_a_reservada_toda_ocupando_pela_ampla_nao_esgota():
    """**DP-2 da `095`, presa como está.** Duas autodeclaradas, as duas ocupando pela ampla: a
    reservada apura zero ocupadas, e as duas posições ainda contam como quem ocupar — sob
    esgotamento, nada é cedido."""
    assert ha_quem_ocupar(posicoes=[1, 2], ja_ocupadas=0)
    assert (
        reversao.quantidade_a_reverter(
            especie=nomes.REVERSAO_POR_ESGOTAMENTO,
            efetivas=2,
            ocupadas=0,
            ha_quem_ocupar=ha_quem_ocupar(posicoes=[1, 2], ja_ocupadas=0),
        )
        == 0
    )
