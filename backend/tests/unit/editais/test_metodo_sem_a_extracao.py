"""O método que espera a extração: o rascunho o admite, e o ato o recusa (116, FR-3716, D-009).

**A extração é o concurso e o instante dele** — `occurrence` e `occurrenceAt`. É o que aconteceu no
certame anterior, e o Edital reaproveitado não a traz. O rascunho grava o método sem **os dois**;
sem um só, é método pela metade, e a gravação recusa como sempre (a FR-013 da `021`). A submissão,
a publicação e a Retificação continuam exigindo o método inteiro, e dizem o que falta e onde
(FR-3717).
"""

import copy

import pytest

from processo_seletivo.editais.domain.perfis import (
    ProfileValidationError,
    validate_classification_milestones,
    validate_common_draw_method,
)
from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    blocking_findings,
    validate_for_publication,
)
from processo_seletivo.sorteios.application import conferencia
from tests.fixtures.edital import DRAW_METHOD, complete_draft

INDICACAO = ("ainda não declara a extração", "etapa Classificação", "calendário oficial")


def _sem(*campos, fonte="Loteria Federal", vazio=False):
    metodo = copy.deepcopy(DRAW_METHOD)
    metodo.update({"source": fonte, "occurrence": "6116"})
    for campo in campos:
        if vazio:
            metodo[campo] = ""
        else:
            metodo.pop(campo)
    return metodo


def _marco(metodo):
    return {
        "id": "aaaaaaaa-0000-4000-8000-000000001171",
        "code": "SORTEIO",
        "name": "Sorteio público",
        "orderProduction": "POR_SORTEIO",
        "stages": [],
        "tiebreakers": [],
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "cutRule": {
            "targetKind": "FIXED",
            "targetCount": 2,
            "surplusCount": 0,
            "tieOutcome": "STRICT",
            "governedStage": "NONE",
            "continuation": "NONE",
        },
        "drawMethod": metodo,
    }


# --- a gravação -------------------------------------------------------------------------------


@pytest.mark.parametrize("vazio", [False, True])
@pytest.mark.parametrize("fonte", ["Loteria Federal", "Fonte de demonstração"])
def test_a_gravacao_admite_o_metodo_sem_a_extracao(vazio, fonte):
    """Ausentes ou vazios, como o formulário os envia: os dois juntos são a extração a declarar."""
    metodo = _sem("occurrence", "occurrenceAt", fonte=fonte, vazio=vazio)
    validate_classification_milestones([_marco(metodo)])
    validate_common_draw_method(metodo, exigir_a_extracao=False)


@pytest.mark.parametrize(
    ("falta", "o_que_e"),
    [
        ("occurrence", "a ocorrência concreta que fixará a semente"),
        ("occurrenceAt", "o instante publicado em que a ocorrência acontece"),
    ],
)
def test_um_sem_o_outro_continua_pela_metade(falta, o_que_e):
    with pytest.raises(ProfileValidationError) as recusa:
        validate_classification_milestones([_marco(_sem(falta))])
    assert o_que_e in str(recusa.value)


def test_o_resto_do_metodo_continua_exigido_na_gravacao():
    """A admissão é estreita: sem a extração **e** sem a substituição não é a mesma coisa."""
    metodo = _sem("occurrence", "occurrenceAt", "substitutionRule")
    with pytest.raises(ProfileValidationError) as recusa:
        validate_classification_milestones([_marco(metodo)])
    assert "substitutionRule" in str(recusa.value)


def test_o_padrao_do_metodo_comum_exige_a_extracao():
    """O padrão erra pelo lado que recusa: quem não diz que é rascunho não ganha a admissão."""
    with pytest.raises(ProfileValidationError) as recusa:
        validate_common_draw_method(_sem("occurrence", "occurrenceAt"))
    for parte in INDICACAO:
        assert parte in str(recusa.value)


# --- os atos ----------------------------------------------------------------------------------


@pytest.mark.parametrize("ato", [ATO_DE_PUBLICACAO, ATO_DE_RETIFICACAO])
def test_os_atos_recusam_o_metodo_do_marco_sem_a_extracao(ato):
    conteudo = complete_draft()
    marco = conteudo["profiles"][0]["classificationMilestones"][0]
    marco["drawMethod"] = _sem("occurrence", "occurrenceAt")

    (achado,) = [
        a
        for a in blocking_findings(validate_for_publication(conteudo, ato=ato))
        if a.code == "draw_method_invalid"
    ]

    assert achado.severity == Severity.BLOCKING_ERROR
    for parte in INDICACAO:
        assert parte in achado.message
    assert achado.path.endswith(f"/classificationMilestones/id={marco['id']}/drawMethod")


@pytest.mark.parametrize("ato", [ATO_DE_PUBLICACAO, ATO_DE_RETIFICACAO])
def test_os_atos_recusam_o_metodo_comum_sem_a_extracao(ato):
    conteudo = complete_draft()
    conteudo["profiles"][0]["classificationMilestones"][0].pop("drawMethod")
    conteudo["drawMethod"] = _sem("occurrence", "occurrenceAt")

    (achado,) = [
        a
        for a in blocking_findings(validate_for_publication(conteudo, ato=ato))
        if a.code == "common_draw_method_invalid"
    ]

    for parte in INDICACAO:
        assert parte in achado.message


def test_a_caixa_nao_e_consultada_sobre_o_metodo_sem_a_extracao():
    """Não há o que perguntar: a referência não existe, e o impeditivo já é do método (FR-3717)."""
    conteudo = complete_draft()
    conteudo["profiles"][0]["classificationMilestones"][0]["drawMethod"] = _sem(
        "occurrence", "occurrenceAt"
    )
    assert conferencia.referencias_a_conferir(conteudo) == []
