"""A tabela-verdade do desempate, sem banco (015, D-004, D-005).

Três famílias, e as três existem porque a spec nomeia um defeito que elas impedem: aplicar
critérios fora da ordem publicada; tratar ausência como se fosse valor; e inventar ordem onde o
Edital não a declarou.
"""

from decimal import Decimal

import pytest

from processo_seletivo.classificacao.domain.desempate import comparar, ordenar

ETAPA = "00000000-0000-0000-0000-0000000000e1"
FATO = "00000000-0000-0000-0000-0000000000f1"


def participante(nome, pontuacao=None, *, na_etapa=None, fato=None):
    return {
        "nome": nome,
        "pontuacao": pontuacao,
        "pontuacoes": {} if na_etapa is None else {ETAPA: na_etapa},
        "fatos": {} if fato is None else {FATO: fato},
    }


def criterio(ordem, tipo, *, quando_ausente="ULTIMO_NO_CRITERIO", **parametros):
    return {
        "id": f"c{ordem}",
        "order": ordem,
        "type": tipo,
        "parameters": parametros,
        "whenMissing": quando_ausente,
    }


# --- a pontuação decide antes de qualquer critério -------------------------------------------


def test_a_pontuacao_maior_vem_primeiro_sem_consultar_criterio():
    ordem, separou = comparar([], participante("a", Decimal("9")), participante("b", Decimal("8")))

    assert ordem == -1
    assert separou is None, "quem separou foi a pontuação, e não um critério"


# --- os critérios são aplicados na ordem publicada --------------------------------------------


def test_o_criterio_de_ordem_menor_decide_primeiro():
    """Aplicar fora da ordem publicada é aplicar outra regra."""
    criterios = [
        criterio(2, "MAIOR_VALOR_DE_FATO", factId=FATO),
        criterio(1, "MAIOR_PONTUACAO_NA_ETAPA", stageId=ETAPA),
    ]
    # Na Etapa, `a` ganha; no fato, `b` ganha. O de ordem 1 é o da Etapa.
    esquerda = participante("a", Decimal("8"), na_etapa=Decimal("9"), fato=1)
    direita = participante("b", Decimal("8"), na_etapa=Decimal("7"), fato=9)

    ordem, separou = comparar(criterios, esquerda, direita)

    assert ordem == -1
    assert separou["order"] == 1


def test_o_segundo_criterio_so_decide_quando_o_primeiro_empata():
    criterios = [
        criterio(1, "MAIOR_PONTUACAO_NA_ETAPA", stageId=ETAPA),
        criterio(2, "MAIOR_VALOR_DE_FATO", factId=FATO),
    ]
    esquerda = participante("a", Decimal("8"), na_etapa=Decimal("7"), fato=1)
    direita = participante("b", Decimal("8"), na_etapa=Decimal("7"), fato=9)

    ordem, separou = comparar(criterios, esquerda, direita)

    assert ordem == 1, "b tem o fato maior"
    assert separou["order"] == 2


def test_menor_valor_de_fato_inverte_o_sentido():
    criterios = [criterio(1, "MENOR_VALOR_DE_FATO", factId=FATO)]

    ordem, _ = comparar(
        criterios,
        participante("a", Decimal("8"), fato=30),
        participante("b", Decimal("8"), fato=10),
    )

    assert ordem == 1, "menor valor vem primeiro"


# --- valor ausente: declarado, nunca inferido -------------------------------------------------


@pytest.mark.parametrize(
    ("quando_ausente", "esperado"),
    [("ULTIMO_NO_CRITERIO", -1), ("CRITERIO_NAO_SE_APLICA", 0)],
)
def test_o_comportamento_para_valor_ausente_e_o_que_o_edital_declarou(quando_ausente, esperado):
    """Quem não tem valor fica por último **naquele critério**, ou o critério não separa o par."""
    criterios = [criterio(1, "MAIOR_VALOR_DE_FATO", factId=FATO, quando_ausente=quando_ausente)]

    ordem, _ = comparar(
        criterios, participante("a", Decimal("8"), fato=5), participante("b", Decimal("8"))
    )

    assert ordem == esperado


def test_ausencia_nos_dois_lados_nao_separa():
    criterios = [criterio(1, "MAIOR_VALOR_DE_FATO", factId=FATO)]

    ordem, separou = comparar(
        criterios, participante("a", Decimal("8")), participante("b", Decimal("8"))
    )

    assert (ordem, separou) == (0, None)


def test_o_valor_ausente_nao_e_tratado_como_zero():
    """Zero é uma nota; ausência não é. Tratá-los igual afirmaria o que ninguém atribuiu."""
    criterios = [criterio(1, "MAIOR_VALOR_DE_FATO", factId=FATO)]
    com_zero = participante("a", Decimal("8"), fato=0)
    sem_valor = participante("b", Decimal("8"))

    ordem, _ = comparar(criterios, com_zero, sem_valor)

    assert ordem == -1, "quem tem zero vem antes de quem não tem valor algum"


# --- o empate que sobrevive a tudo -------------------------------------------------------------


def test_o_empate_residual_nao_e_desfeito_por_criterio_inventado():
    """Nem por identificador, nem por nome, nem por ordem de chegada."""
    ordem, separou = comparar(
        [], participante("zebra", Decimal("8")), participante("abelha", Decimal("8"))
    )

    assert (ordem, separou) == (0, None)


def test_o_grupo_empatado_e_marcado_dos_dois_lados():
    """Um empate é do grupo: marcar só quem chega depois faria o primeiro parecer sozinho."""
    ordenados = ordenar(
        [
            participante("a", Decimal("9")),
            participante("b", Decimal("8")),
            participante("c", Decimal("8")),
        ],
        [],
    )

    assert [item["empate_residual"] for item in ordenados] == [False, True, True]
