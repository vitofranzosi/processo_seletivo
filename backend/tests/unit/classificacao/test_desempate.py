"""A tabela-verdade do desempate, sem banco (015, D-004, D-005, FR-070 a FR-072).

**A comparação par a par não existe mais, e a ausência dela é a correção.** A primeira redação
comparava dois participantes de cada vez, e com `CRITERIO_NAO_SE_APLICA` isso produzia ciclo: A
vencia B, B vencia C e C vencia A, de modo que as seis permutações dos mesmos três participantes
davam três ordens diferentes — sob a mesma regra publicada. O motor agora **particiona grupos**, e
por isso não pode ter ciclo.
"""

import itertools
from decimal import Decimal

import pytest

from processo_seletivo.classificacao.domain.desempate import ordenar, particiona_o_grupo

ETAPA = "00000000-0000-0000-0000-0000000000e1"
FATO = "00000000-0000-0000-0000-0000000000f1"
OUTRO = "00000000-0000-0000-0000-0000000000f2"


def participante(nome, pontuacao="8", *, na_etapa=None, fato=None, outro=None):
    fatos = {}
    if fato is not None:
        fatos[FATO] = fato
    if outro is not None:
        fatos[OUTRO] = outro
    return {
        "nome": nome,
        "pontuacao": Decimal(pontuacao),
        "pontuacoes": {} if na_etapa is None else {ETAPA: Decimal(na_etapa)},
        "fatos": fatos,
    }


def criterio(ordem, tipo, *, quando_ausente="ULTIMO_NO_CRITERIO", **parametros):
    return {
        "id": f"c{ordem}",
        "order": ordem,
        "type": tipo,
        "parameters": parametros,
        "whenMissing": quando_ausente,
    }


def posicoes(ordenados):
    return [(item["nome"], item["posicao"]) for item in ordenados]


# --- a pontuação separa antes de qualquer critério ---------------------------------------------


def test_a_pontuacao_maior_vem_primeiro():
    resultado = ordenar([participante("a", "8"), participante("b", "9")], [])

    assert posicoes(resultado) == [("b", 1), ("a", 2)]
    assert resultado[0]["separado_por"] is None, "quem separou foi a pontuação"


# --- os critérios são oferecidos na ordem publicada ---------------------------------------------


def test_o_criterio_de_ordem_menor_particiona_primeiro():
    criterios = [
        criterio(2, "MAIOR_VALOR_DE_FATO", factId=FATO),
        criterio(1, "MAIOR_PONTUACAO_NA_ETAPA", stageId=ETAPA),
    ]
    resultado = ordenar(
        [
            participante("a", na_etapa="9", fato=1),
            participante("b", na_etapa="7", fato=9),
        ],
        criterios,
    )

    assert posicoes(resultado) == [("a", 1), ("b", 2)]
    assert resultado[0]["separado_por"]["order"] == 1


def test_o_segundo_criterio_particiona_o_que_o_primeiro_deixou_empatado():
    criterios = [
        criterio(1, "MAIOR_PONTUACAO_NA_ETAPA", stageId=ETAPA),
        criterio(2, "MAIOR_VALOR_DE_FATO", factId=FATO),
    ]
    resultado = ordenar(
        [
            participante("a", na_etapa="7", fato=1),
            participante("b", na_etapa="7", fato=9),
        ],
        criterios,
    )

    assert posicoes(resultado) == [("b", 1), ("a", 2)]
    assert resultado[0]["separado_por"]["order"] == 2


def test_menor_valor_de_fato_inverte_o_sentido():
    resultado = ordenar(
        [participante("a", fato=30), participante("b", fato=10)],
        [criterio(1, "MENOR_VALOR_DE_FATO", factId=FATO)],
    )

    assert posicoes(resultado) == [("b", 1), ("a", 2)]


# --- valor ausente: o escopo é o grupo, e não o par ----------------------------------------------


def test_ultimo_no_criterio_poe_quem_nao_tem_atras_de_quem_tem():
    resultado = ordenar(
        [participante("sem"), participante("com", fato=5)],
        [criterio(1, "MAIOR_VALOR_DE_FATO", factId=FATO)],
    )

    assert posicoes(resultado) == [("com", 1), ("sem", 2)]


def test_criterio_nao_se_aplica_desliga_o_criterio_para_o_grupo_inteiro():
    """Um membro sem o valor tira o critério **daquele** grupo — e de nenhum outro (FR-071)."""
    criterios = [
        criterio(1, "MAIOR_VALOR_DE_FATO", factId=FATO, quando_ausente="CRITERIO_NAO_SE_APLICA")
    ]

    assert particiona_o_grupo(criterios[0], [participante("a", fato=5), participante("b")]) is False
    assert (
        particiona_o_grupo(criterios[0], [participante("a", fato=5), participante("b", fato=1)])
        is True
    )


def test_a_ausencia_num_grupo_nao_desativa_o_criterio_de_outro_grupo():
    """A diferença entre o escopo por grupo e o escopo global, dita em teste."""
    criterios = [
        criterio(1, "MAIOR_VALOR_DE_FATO", factId=FATO, quando_ausente="CRITERIO_NAO_SE_APLICA")
    ]
    resultado = ordenar(
        [
            participante("alto_sem", "9"),
            participante("alto_com", "9", fato=5),
            participante("baixo_a", "7", fato=1),
            participante("baixo_b", "7", fato=9),
        ],
        criterios,
    )

    # No grupo de 9 alguém não tem o fato: o critério não particiona, e os dois empatam em 1.
    assert [item["posicao"] for item in resultado[:2]] == [1, 1]
    # No grupo de 7 todos têm: o critério particiona normalmente.
    assert posicoes(resultado[2:]) == [("baixo_b", 3), ("baixo_a", 4)]


def test_um_criterio_que_nao_particiona_nao_encerra_a_sequencia():
    """O próximo critério é oferecido ao mesmo grupo (FR-072)."""
    criterios = [
        criterio(1, "MAIOR_VALOR_DE_FATO", factId=FATO, quando_ausente="CRITERIO_NAO_SE_APLICA"),
        criterio(2, "MAIOR_VALOR_DE_FATO", factId=OUTRO),
    ]
    resultado = ordenar(
        [participante("a", fato=5, outro=1), participante("b", outro=9)],
        criterios,
    )

    assert posicoes(resultado) == [("b", 1), ("a", 2)]
    assert resultado[0]["separado_por"]["order"] == 2


def test_o_valor_ausente_nao_e_tratado_como_zero():
    resultado = ordenar(
        [participante("sem"), participante("zero", fato=0)],
        [criterio(1, "MAIOR_VALOR_DE_FATO", factId=FATO)],
    )

    assert posicoes(resultado) == [("zero", 1), ("sem", 2)]


# --- transitividade: a propriedade, e não mais um caso ------------------------------------------


def test_o_ciclo_que_a_revisao_encontrou_nao_existe_mais():
    """O caso exato que produzia A > B > C > A, e três ordens em seis permutações.

    Com o escopo por grupo, o primeiro critério não particiona o grupo — porque B não tem o valor —,
    o segundo particiona, e a ordem passa a ser função só das entradas e da norma.
    """
    criterios = [
        criterio(1, "MAIOR_VALOR_DE_FATO", factId=FATO, quando_ausente="CRITERIO_NAO_SE_APLICA"),
        criterio(2, "MAIOR_VALOR_DE_FATO", factId=OUTRO, quando_ausente="CRITERIO_NAO_SE_APLICA"),
    ]
    trio = [
        participante("A", fato=1, outro=3),
        participante("B", outro=2),
        participante("C", fato=2, outro=1),
    ]

    ordens = {
        tuple(posicoes(ordenar(list(perm), criterios))) for perm in itertools.permutations(trio)
    }

    assert len(ordens) == 1, f"as permutações produziram {len(ordens)} ordens: {ordens}"
    assert ordens.pop() == (("A", 1), ("B", 2), ("C", 3))


@pytest.mark.parametrize("quantos", [4, 5])
def test_toda_permutacao_da_entrada_produz_a_mesma_ordem(quantos):
    """A propriedade em si, sobre um conjunto com empates, ausências e critérios encadeados."""
    criterios = [
        criterio(1, "MAIOR_VALOR_DE_FATO", factId=FATO, quando_ausente="CRITERIO_NAO_SE_APLICA"),
        criterio(2, "MAIOR_VALOR_DE_FATO", factId=OUTRO),
    ]
    universo = [
        participante("a", "9", fato=1, outro=5),
        participante("b", "9", outro=7),
        participante("c", "8", fato=3, outro=2),
        participante("d", "8", fato=3, outro=9),
        participante("e", "7", fato=1, outro=1),
    ][:quantos]

    ordens = {
        tuple(posicoes(ordenar(list(perm), criterios))) for perm in itertools.permutations(universo)
    }

    assert len(ordens) == 1, f"{len(ordens)} ordens distintas para {quantos} participantes"


# --- a numeração e o empate residual ------------------------------------------------------------


def test_o_empate_residual_nao_e_desfeito_por_criterio_inventado():
    resultado = ordenar([participante("zebra"), participante("abelha")], [])

    assert [item["posicao"] for item in resultado] == [1, 1]
    assert all(item["empate_residual"] for item in resultado)


def test_o_grupo_empatado_e_marcado_por_inteiro():
    resultado = ordenar(
        [participante("a", "9"), participante("b", "8"), participante("c", "8")], []
    )

    assert [item["empate_residual"] for item in resultado] == [False, True, True]
    assert [item["posicao"] for item in resultado] == [1, 2, 2]
