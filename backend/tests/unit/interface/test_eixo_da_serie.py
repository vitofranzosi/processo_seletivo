"""Quais dias o eixo do gráfico de submissões nomeia — escala do desenho, sem banco.

O gráfico nasceu sem eixo: as barras diziam "subiu, desceu", e quando e quanto só se lia abrindo a
tabela. Rotular todo dia não cabe — sessenta datas sob sessenta barras de meio rem se sobrepõem —,
então o eixo nomeia alguns, e estes testes fixam quais.
"""

from datetime import date, timedelta

import pytest

from processo_seletivo.interface.supervisao import (
    ROTULOS_NO_EIXO,
    PontoDaSerie,
    PulsoDoEdital,
)


def pulso_de(dias):
    inicio = date(2026, 9, 22)
    serie = tuple(
        PontoDaSerie(dia=inicio + timedelta(days=n), quantidade=n % 4) for n in range(dias)
    )
    return PulsoDoEdital(edital=None, submetidas=0, rascunhos=0, serie=serie)


def rotulados(pulso):
    return [indice for indice, marcado in enumerate(pulso.eixo) if marcado.rotulado]


def test_o_eixo_percorre_a_serie_inteira_na_ordem():
    pulso = pulso_de(15)

    assert [marcado.ponto for marcado in pulso.eixo] == list(pulso.serie)


def test_um_dia_so_e_nomeado():
    assert rotulados(pulso_de(1)) == [0]


def test_serie_vazia_nao_tem_eixo():
    assert pulso_de(0).eixo == ()


@pytest.mark.parametrize("dias", [2, 7, 8, 14, 15, 16, 21, 30, 60, 61])
def test_primeiro_e_ultimo_dia_sempre_nomeados(dias):
    """O primeiro situa o começo; o último é o "hoje" de um período em curso."""
    indices = rotulados(pulso_de(dias))

    assert indices[0] == 0
    assert indices[-1] == dias - 1


@pytest.mark.parametrize("dias", [2, 7, 8, 14, 15, 16, 21, 30, 60, 61])
def test_o_eixo_nao_amontoa_rotulos(dias):
    """Nunca mais rótulos que o teto, e nunca dois rótulos mais próximos que o passo.

    O penúltimo é o que mais arrisca: se ficasse colado ao último, as duas datas se sobreporiam
    sob barras estreitas.
    """
    indices = rotulados(pulso_de(dias))
    passo = -(-dias // ROTULOS_NO_EIXO)

    assert len(indices) <= ROTULOS_NO_EIXO + 1
    assert all(b - a >= passo for a, b in zip(indices, indices[1:], strict=False))
