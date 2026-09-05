"""O arredondamento da pontuação combinada: uma vez, no fim, na forma publicada (015, FR-068, FR-069).

Três provas que a spec pede por nome, e uma quarta que decorre delas: o arredondamento **cria**
empate, e criar empate é criar trabalho para os critérios de desempate. Isso não é defeito — é a
consequência de publicar escala, e precisa estar visível.
"""

from decimal import Decimal

import pytest

from processo_seletivo.classificacao.domain.combinacao import (
    RegraIncompleta,
    arredondar,
    combinar,
    peso_da_etapa,
)
from processo_seletivo.classificacao.domain.desempate import ordenar

A = "00000000-0000-0000-0000-0000000000a1"
B = "00000000-0000-0000-0000-0000000000b1"


def marco(*, escala=2, modo="MEIO_PARA_CIMA", operacao="SOMA_PONDERADA", normalizacao="NENHUMA"):
    return {
        "stages": [A, B],
        "operation": operacao,
        "normalization": normalizacao,
        "rounding": {"scale": escala, "mode": modo},
    }


def etapas(peso_a="1.0000", peso_b="1.0000"):
    return {A: {"weight": peso_a}, B: {"weight": peso_b}}


# --- os três modos ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("modo", "esperado"),
    [("MEIO_PARA_CIMA", "3"), ("MEIO_PARA_PAR", "2"), ("TRUNCAR", "2")],
)
def test_os_tres_modos_separam_no_meio_exato(modo, esperado):
    """2,5 é onde os três discordam — e por isso é o único caso que os distingue."""
    combinada = combinar(
        marco(escala=0, modo=modo, operacao="MEDIA_PONDERADA"),
        etapas(),
        {A: Decimal("2"), B: Decimal("3")},
    )

    assert combinada == Decimal(esperado)


@pytest.mark.parametrize(
    ("modo", "esperado"),
    [("MEIO_PARA_CIMA", "4"), ("MEIO_PARA_PAR", "4"), ("TRUNCAR", "3")],
)
def test_meio_para_par_arredonda_para_cima_quando_o_par_esta_acima(modo, esperado):
    """3,5 vai para 4 nos dois modos de meio — é 2,5 que os separa, e não todo meio."""
    combinada = combinar(
        marco(escala=0, modo=modo, operacao="MEDIA_PONDERADA"),
        etapas(),
        {A: Decimal("3"), B: Decimal("4")},
    )

    assert combinada == Decimal(esperado)


def test_truncar_nao_olha_o_que_vem_depois():
    assert arredondar(Decimal("2.999999"), marco(escala=2, modo="TRUNCAR")) == Decimal("2.99")


def test_a_escala_publicada_governa_as_casas():
    assert arredondar(Decimal("7.123456"), marco(escala=4)) == Decimal("7.1235")
    assert arredondar(Decimal("7.123456"), marco(escala=0)) == Decimal("7")


# --- uma vez, e no fim ---------------------------------------------------------------------------


def test_arredondar_parcelas_daria_resultado_diferente():
    """O caso que justifica a regra, e não só a ilustra.

    Duas parcelas de 0,005 com escala 2: arredondadas antes, viram 0,01 cada e somam 0,02.
    Combinadas em precisão plena, somam 0,01 e arredondam para 0,01. A diferença é o dobro — e a
    pontuação decide quem passa.
    """
    combinada = combinar(marco(escala=2), etapas(), {A: Decimal("0.005"), B: Decimal("0.005")})

    parcela = arredondar(Decimal("0.005"), marco(escala=2))
    somando_parcelas_arredondadas = parcela + parcela

    assert combinada == Decimal("0.01")
    assert somando_parcelas_arredondadas == Decimal("0.02")
    assert combinada != somando_parcelas_arredondadas


def test_a_normalizacao_acontece_antes_do_arredondamento():
    """Arredondar antes de dividir daria outro número, e a ordem dos passos é publicada."""
    combinada = combinar(
        marco(escala=2, normalizacao="PELA_SOMA_DOS_PESOS"),
        etapas(peso_a="2.0000", peso_b="1.0000"),
        {A: Decimal("8"), B: Decimal("5")},
    )

    assert combinada == Decimal("7.00"), "21 / 3, arredondado uma vez"


# --- o arredondamento cria empate, e o empate é trabalho do desempate ---------------------------


def test_o_arredondamento_cria_empate_que_nao_existia():
    """Duas pontuações distintas em precisão plena viram a mesma na escala publicada.

    A consequência precisa estar visível: quem publica escala baixa cria empates, e empates são
    resolvidos pelos critérios — ou sobrevivem como empate residual.
    """
    um = combinar(marco(escala=1), etapas(), {A: Decimal("3.04"), B: Decimal("4.00")})
    outro = combinar(marco(escala=1), etapas(), {A: Decimal("3.00"), B: Decimal("4.03")})

    assert um == outro == Decimal("7.0")

    ordenados = ordenar(
        [
            {"nome": "a", "pontuacao": um, "pontuacoes": {}, "fatos": {}},
            {"nome": "b", "pontuacao": outro, "pontuacoes": {}, "fatos": {}},
        ],
        [],
    )

    assert [item["posicao"] for item in ordenados] == [1, 1]
    assert all(item["empate_residual"] for item in ordenados)


# --- a regra incompleta é recusada, e não completada --------------------------------------------


def test_o_calculo_nao_escolhe_arredondamento_por_conta_propria():
    """Se escolhesse, o padrão seria do código e não do Edital."""
    sem_arredondamento = {k: v for k, v in marco().items() if k != "rounding"}

    with pytest.raises(RegraIncompleta):
        combinar(sem_arredondamento, etapas(), {A: Decimal("8"), B: Decimal("5")})


def test_o_calculo_nao_interpreta_peso_ausente():
    with pytest.raises(RegraIncompleta):
        peso_da_etapa({"weight": None})

    with pytest.raises(RegraIncompleta):
        combinar(
            marco(), {A: {"weight": None}, B: {"weight": "1.0"}}, {A: Decimal("8"), B: Decimal("5")}
        )
