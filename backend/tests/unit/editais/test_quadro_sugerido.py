"""A quantidade que o percentual produz, e o arredondamento que escolhe entre piso e teto (051).

A sugestão é o consumidor que o `rounding` da regra normativa não tinha (FR-932, FR-933). O que
estes casos prendem é a escolha: exata quando a conta é inteira, a do arredondamento declarado
quando não é, e nenhuma quando nada decide — a faixa sem regra não escolhe por ninguém.
"""

import pytest

from processo_seletivo.editais.domain import quadro


def test_conta_inteira_sugere_o_numero_sem_arredondamento():
    sugestao = quadro.sugestao(percentual="25", vagas_imediatas=40)

    assert (sugestao.valor, sugestao.piso, sugestao.teto) == (10, 10, 10)
    assert sugestao.conta == "25% de 40 = 10"


@pytest.mark.parametrize(
    ("modo", "esperado"),
    [(quadro.PARA_CIMA, 2), (quadro.PARA_BAIXO, 1), (quadro.MEIO_PARA_CIMA, 2)],
)
def test_o_arredondamento_declarado_escolhe(modo, esperado):
    sugestao = quadro.sugestao(percentual="25", vagas_imediatas=7, rounding={"mode": modo})

    assert sugestao.valor == esperado
    assert sugestao.conta == "25% de 7 = 1,75"


def test_meio_para_cima_abaixo_do_meio_fica_no_piso():
    sugestao = quadro.sugestao(
        percentual="5", vagas_imediatas=7, rounding={"mode": quadro.MEIO_PARA_CIMA}
    )

    assert sugestao.valor == 0


def test_sem_arredondamento_a_faixa_nao_escolhe():
    sugestao = quadro.sugestao(percentual="25", vagas_imediatas=7)

    assert sugestao.valor is None
    assert (sugestao.piso, sugestao.teto) == (1, 2)


def test_fora_da_lista_e_preservado_e_nao_sugere():
    fora = {"mode": "BANCARIO", "casas": 0}

    assert quadro.modo_declarado(fora) is None
    assert quadro.em_palavras(fora) == "declarado fora da lista"
    assert quadro.sugestao(percentual="25", vagas_imediatas=7, rounding=fora).valor is None


@pytest.mark.parametrize(("percentual", "vagas"), [(None, 7), ("x", 7), ("0", 7), ("5", None)])
def test_sem_o_que_calcular_nao_ha_sugestao(percentual, vagas):
    assert quadro.sugestao(percentual=percentual, vagas_imediatas=vagas) is None
