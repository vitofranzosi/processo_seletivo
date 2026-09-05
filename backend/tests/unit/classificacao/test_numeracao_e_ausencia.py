"""A numeração da ordem e o que a ausência de pontuação significa (015, FR-023, FR-026).

Duas garantias que parecem detalhe e não são. A numeração é o número que o candidato lê, sobre o
qual recorre, e que o corte da 014 vai contar. E ausência tratada como zero afirmaria uma nota que
ninguém atribuiu — num lugar onde a nota decide quem passa.
"""

from decimal import Decimal

import pytest

from processo_seletivo.classificacao.domain.combinacao import (
    SEM_PONTUACAO,
    RegraIncompleta,
    combinar,
    peso_da_etapa,
)
from processo_seletivo.classificacao.domain.desempate import ordenar

ETAPA_A = "00000000-0000-0000-0000-0000000000a1"
ETAPA_B = "00000000-0000-0000-0000-0000000000b1"

ETAPAS = {ETAPA_A: {"weight": "2.0000"}, ETAPA_B: {"weight": "1.0000"}}
MARCO = {
    "stages": [ETAPA_A, ETAPA_B],
    "operation": "SOMA_PONDERADA",
    "normalization": "NENHUMA",
    # Escala 4 para que estes testes falem de combinação, e não de arredondamento: o que eles
    # verificam é a conta, e os modos têm arquivo próprio.
    "rounding": {"scale": 4, "mode": "MEIO_PARA_CIMA"},
}


def participante(nome, pontuacao):
    return {"nome": nome, "pontuacao": pontuacao, "pontuacoes": {}, "fatos": {}}


# --- a numeração: quantos estão à frente, mais um ----------------------------------------------


def test_a_posicao_e_o_numero_de_participantes_a_frente_mais_um():
    ordenados = ordenar(
        [
            participante(nome, Decimal(nota))
            for nome, nota in (("a", "10"), ("b", "9"), ("c", "9"), ("d", "8"))
        ],
        [],
    )

    assert [(item["nome"], item["posicao"]) for item in ordenados] == [
        ("a", 1),
        ("b", 2),
        ("c", 2),
        ("d", 4),
    ]


def test_o_empate_na_primeira_posicao_pula_a_segunda():
    """`1, 1, 3` — a numeração padrão, e não a densa."""
    ordenados = ordenar(
        [participante(nome, Decimal(nota)) for nome, nota in (("a", "9"), ("b", "9"), ("c", "8"))],
        [],
    )

    assert [item["posicao"] for item in ordenados] == [1, 1, 3]


def test_os_n_primeiros_selecionam_n_pessoas_quando_o_empate_nao_atravessa():
    """A propriedade que o corte da 014 vai depender: contar posições é contar gente."""
    ordenados = ordenar(
        [
            participante(nome, Decimal(nota))
            for nome, nota in (("a", "10"), ("b", "9"), ("c", "8"), ("d", "8"))
        ],
        [],
    )

    dentro = [item for item in ordenados if item["posicao"] <= 2]

    assert len(dentro) == 2
    assert [item["nome"] for item in dentro] == ["a", "b"]


def test_todos_empatados_compartilham_a_primeira_posicao():
    ordenados = ordenar([participante(n, Decimal("7")) for n in "abc"], [])

    assert [item["posicao"] for item in ordenados] == [1, 1, 1]
    assert all(item["empate_residual"] for item in ordenados)


# --- ausência nunca vira zero -------------------------------------------------------------------


def test_a_ausencia_de_pontuacao_nao_vira_zero():
    """`SEM_PONTUACAO` é irredutível a `Decimal(0)`, e é essa a garantia."""
    sem = combinar(MARCO, ETAPAS, {ETAPA_A: Decimal("8"), ETAPA_B: None})

    assert sem is SEM_PONTUACAO
    assert sem != Decimal("0")


def test_pontuacao_zero_e_diferente_de_ausencia():
    """Zero é nota atribuída; ausência é a falta dela — e o resultado precisa distingui-las."""
    com_zero = combinar(MARCO, ETAPAS, {ETAPA_A: Decimal("0"), ETAPA_B: Decimal("0")})

    assert com_zero == Decimal("0")
    assert com_zero is not SEM_PONTUACAO


def test_etapa_enumerada_que_nao_existe_no_conteudo_nao_vira_zero():
    marco = {**MARCO, "stages": [ETAPA_A, "00000000-0000-0000-0000-0000000000ff"]}

    assert combinar(marco, ETAPAS, {ETAPA_A: Decimal("8")}) is SEM_PONTUACAO


# --- o peso vem da Etapa, e ausência de peso é "pesa como as outras" ---------------------------


def test_o_peso_vem_da_etapa_publicada():
    assert combinar(MARCO, ETAPAS, {ETAPA_A: Decimal("8"), ETAPA_B: Decimal("5")}) == Decimal("21")


def test_etapa_sem_peso_declarado_nao_e_interpretada():
    """A redação anterior devolvia 1 e chamava isso de equivalência (FR-067).

    Era decisão do código escrita como se fosse norma. Quem enumera a Etapa declara o peso, e a
    falta é recusada na publicação — não completada no cálculo.
    """
    with pytest.raises(RegraIncompleta):
        peso_da_etapa({})

    with pytest.raises(RegraIncompleta):
        peso_da_etapa({"weight": None})


@pytest.mark.parametrize(
    ("operacao", "normalizacao", "esperado"),
    [
        ("SOMA_PONDERADA", "NENHUMA", Decimal("21")),
        ("SOMA_PONDERADA", "PELA_SOMA_DOS_PESOS", Decimal("7")),
        ("MEDIA_PONDERADA", "NENHUMA", Decimal("7")),
    ],
)
def test_a_operacao_declarada_governa_a_combinacao(operacao, normalizacao, esperado):
    """Os pesos não precisam somar 1: é a normalização declarada que responde por isso (FR-012)."""
    marco = {**MARCO, "operation": operacao, "normalization": normalizacao}

    assert combinar(marco, ETAPAS, {ETAPA_A: Decimal("8"), ETAPA_B: Decimal("5")}) == esperado
