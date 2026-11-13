"""A coerência entre a espécie do cadastro e o corte do marco que convoca (162, T007).

As cinco recusas da tabela R de `contracts/telas.md`, o recorte pelo ato da T-004 e os pares
coerentes que não podem ser recusados (SC-2300). A conta mora em `cadastro_de_reserva`; aqui se
prende também que `validate_for_publication` a chama, com a severidade e o caminho certos.
"""

import pytest

from processo_seletivo.editais.domain import cadastro_de_reserva as cadastro
from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    validate_for_publication,
)

from .test_cadastro_de_reserva import marco, perfil, regra, tres_listas

CODIGOS = {
    cadastro.LIMITADO_COM_CONTINUACAO,
    cadastro.ILIMITADO_SEM_CONTINUACAO,
    cadastro.LIMITADO_SEM_CORTE,
    cadastro.LIMITADO_A_NINGUEM,
    cadastro.LIMITADO_COM_MARCOS_DIVERGENTES,
}


def codigos(montado, *, na_publicacao=True):
    return [
        codigo
        for codigo, _ in cadastro.incoerencias(
            cadastro.do_perfil(montado), rotulo="P1", na_publicacao=na_publicacao
        )
    ]


def frases(montado, *, na_publicacao=True):
    return [
        frase
        for _, frase in cadastro.incoerencias(
            cadastro.do_perfil(montado), rotulo="P1", na_publicacao=na_publicacao
        )
    ]


# --- As cinco recusas (FR-6933 a FR-6937, FR-6939) -----------------------------------------------


def test_limitado_com_continuacao():
    montado = perfil(marcos=[marco(corte=regra(excedente=3, continuacao="ALLOWED"))])
    assert codigos(montado) == [cadastro.LIMITADO_COM_CONTINUACAO]
    (frase,) = frases(montado)
    assert "O Perfil 'P1'" in frase
    assert "o marco “Classificação final” admite chamar candidatos além da faixa" in frase
    assert "Retire a continuação do corte do marco “Classificação final”" in frase


def test_ilimitado_sem_continuacao():
    montado = perfil(especie="UNLIMITED", vagas=0, marcos=[marco(corte=regra(alvo=3))])
    assert codigos(montado) == [cadastro.ILIMITADO_SEM_CONTINUACAO]
    (frase,) = frases(montado)
    assert (
        "sem limite, e o corte do marco “Classificação final” não admite chamar além da faixa"
        in frase
    )


def test_limitado_sem_corte():
    assert codigos(perfil(marcos=[marco()])) == [cadastro.LIMITADO_SEM_CORTE]
    assert (
        "o marco “Classificação final” não tem regra de corte"
        in frases(perfil(marcos=[marco()]))[0]
    )
    sem_marco = perfil(marcos=[])
    assert codigos(sem_marco) == [cadastro.LIMITADO_SEM_CORTE]
    assert "nenhum marco de classificação deste Perfil convoca" in frases(sem_marco)[0]


@pytest.mark.parametrize(("alvo", "vagas"), [(2, 2), (1, 2)])
def test_limitado_a_ninguem(alvo, vagas):
    montado = perfil(vagas=vagas, marcos=[marco(corte=regra(alvo=alvo))])
    assert codigos(montado) == [cadastro.LIMITADO_A_NINGUEM]
    assert "o cadastro seria de zero classificados" in frases(montado)[0]


def test_limitado_a_ninguem_nomeia_a_lista():
    modalidades, quadro = tres_listas()
    montado = perfil(
        vagas=4, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(alvo=2))]
    )
    assert codigos(montado) == [cadastro.LIMITADO_A_NINGUEM]
    assert "além das vagas na ampla concorrência" in frases(montado)[0]


def test_marcos_que_convocam_com_numeros_diferentes():
    montado = perfil(
        marcos=[
            marco("m1", corte=regra(excedente=3)),
            marco("m2", nome="Outra classificação", etapas=("x",), corte=regra(excedente=5)),
        ]
    )
    assert codigos(montado) == [cadastro.LIMITADO_COM_MARCOS_DIVERGENTES]
    assert "dão números diferentes (3 e 5)" in frases(montado)[0]


# --- Os pares coerentes (SC-2300) e o 77/2026 (`D-006`) -------------------------------------------


@pytest.mark.parametrize(
    "montado",
    [
        perfil(marcos=[marco(corte=regra(excedente=3))]),
        perfil(vagas=0, marcos=[marco(corte=regra(alvo=6))]),
        perfil(especie="UNLIMITED", marcos=[marco(corte=regra(alvo=3, continuacao="ALLOWED"))]),
        perfil(especie="UNLIMITED", marcos=[marco()]),
        perfil(especie="NONE", marcos=[marco(corte=regra(excedente=30, continuacao="ALLOWED"))]),
        perfil(
            marcos=[
                marco("m1", corte=regra(excedente=3)),
                marco("m2", nome="Outra", etapas=("x",), corte=regra(excedente=3)),
            ]
        ),
    ],
    ids=[
        "limitado-coerente",
        "so-reserva-limitado",
        "ilimitado-com-continuacao",
        "ilimitado-sem-corte",
        "nao-ha-com-suplentes-e-continuacao-o-77",
        "dois-marcos-iguais",
    ],
)
def test_par_coerente_nao_e_recusado(montado):
    assert codigos(montado) == []


# --- O recorte pelo ato (T-004, FR-6948, FR-6951) -----------------------------------------------


def test_na_retificacao_so_o_zero_e_a_divergencia():
    continuacao = perfil(marcos=[marco(corte=regra(excedente=3, continuacao="ALLOWED"))])
    assert codigos(continuacao, na_publicacao=False) == []
    ilimitado = perfil(especie="UNLIMITED", marcos=[marco(corte=regra(alvo=3))])
    assert codigos(ilimitado, na_publicacao=False) == []
    assert codigos(perfil(marcos=[marco()]), na_publicacao=False) == []
    zero = perfil(marcos=[marco(corte=regra(alvo=2))])
    assert codigos(zero, na_publicacao=False) == [cadastro.LIMITADO_A_NINGUEM]


def test_o_legado_nunca_e_recusado():
    for na_publicacao in (True, False):
        assert codigos(perfil(limite=6, marcos=[marco()]), na_publicacao=na_publicacao) == []
        assert (
            codigos(
                perfil(limite=6, marcos=[marco(corte=regra(alvo=2, continuacao="ALLOWED"))]),
                na_publicacao=na_publicacao,
            )
            == []
        )


# --- A chamada em `validate_for_publication` -----------------------------------------------------


def _snapshot(montado):
    return {"title": "x", "profiles": [montado], "schedule": [], "stages": []}


@pytest.mark.parametrize("ato", [ATO_DE_PUBLICACAO, ATO_DE_RETIFICACAO])
def test_validate_for_publication_recusa_com_o_caminho_do_perfil(ato):
    montado = perfil(marcos=[marco(corte=regra(alvo=2))])
    achados = [
        item
        for item in validate_for_publication(_snapshot(montado), ato=ato)
        if item.code in CODIGOS
    ]
    assert [(item.code, item.severity, item.path) for item in achados] == [
        (cadastro.LIMITADO_A_NINGUEM, Severity.BLOCKING_ERROR, "/profiles/id=p1/reserveType")
    ]


def test_validate_for_publication_nao_confere_continuacao_na_retificacao():
    montado = perfil(marcos=[marco(corte=regra(excedente=3, continuacao="ALLOWED"))])
    publicacao = {i.code for i in validate_for_publication(_snapshot(montado))}
    retificacao = {
        i.code for i in validate_for_publication(_snapshot(montado), ato=ATO_DE_RETIFICACAO)
    }
    assert cadastro.LIMITADO_COM_CONTINUACAO in publicacao
    assert cadastro.LIMITADO_COM_CONTINUACAO not in retificacao
