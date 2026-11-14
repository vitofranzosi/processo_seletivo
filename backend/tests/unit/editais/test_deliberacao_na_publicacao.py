"""A regra de deliberação na gravação e na publicação (165, US1, FR-7051 a FR-7053).

Puro, sobre o conteúdo do exemplo da `163`: a Heteroidentificação, agora com três pareceres.
"""

import pytest

from processo_seletivo.editais.domain.etapas import StageValidationError, validate_stage
from processo_seletivo.editais.domain.validation import (
    ATO_DE_RETIFICACAO,
    blocking_findings,
    validate_for_publication,
)
from tests.unit.editais.test_alcance_da_etapa import _conteudo, _etapa

CODIGOS = (
    "deliberacao_sem_regra",
    "regra_invalida",
    "regra_sem_colegiado",
    "maioria_com_numero_par",
)


def _codigos(conteudo, **ato):
    return sorted(
        achado.code
        for achado in blocking_findings(validate_for_publication(conteudo, **ato))
        if achado.code in CODIGOS
    )


def _colegiada(**campos):
    return _etapa(**{"evaluationsPerRegistration": 3, "deliberationRule": "MAJORITY", **campos})


def test_a_etapa_colegiada_com_regra_publica():
    assert _codigos(_conteudo(etapa=_colegiada())) == []


def test_sem_regra_a_publicacao_e_impedida():
    """FR-7051: sem padrão, a Etapa colegiada precisa declarar a regra."""
    achados = blocking_findings(
        validate_for_publication(_conteudo(etapa=_colegiada(deliberationRule=None)))
    )
    sem_regra = [a for a in achados if a.code == "deliberacao_sem_regra"]

    assert len(sem_regra) == 1
    assert "prevê 3 pareceres por inscrição e não declara" in sem_regra[0].message


def test_sem_regra_nao_e_achado_na_retificacao():
    """FR-7051, T-003: na Retificação, a falta de regra é do comando, que sabe o que mudou."""
    conteudo = _conteudo(etapa=_colegiada(deliberationRule=None))

    assert _codigos(conteudo, ato=ATO_DE_RETIFICACAO) == []


@pytest.mark.parametrize(
    "campos, motivo",
    [
        ({"forma": "PONTUADA", "rotuloFavoravel": None, "rotuloDesfavoravel": None}, "é pontuada"),
        ({"evaluationsPerRegistration": 1}, "prevê uma avaliação por inscrição"),
    ],
)
def test_regra_fora_da_colegiada_e_impedida(campos, motivo):
    """FR-7053, nos dois atos."""
    conteudo = _conteudo(etapa=_colegiada(**campos))
    achados = blocking_findings(validate_for_publication(conteudo, ato=ATO_DE_RETIFICACAO))
    regra = [a for a in achados if a.code == "regra_sem_colegiado"]

    assert len(regra) == 1
    assert motivo in regra[0].message


def test_maioria_com_numero_par_e_impedida():
    """FR-7052, D-003: o empate não tem regra publicada."""
    conteudo = _conteudo(etapa=_colegiada(evaluationsPerRegistration=4))

    assert _codigos(conteudo) == ["maioria_com_numero_par"]
    assert _codigos(conteudo, ato=ATO_DE_RETIFICACAO) == ["maioria_com_numero_par"]


@pytest.mark.parametrize("regra", ["UNANIMOUS_FOR_FAVORABLE", "UNANIMOUS_FOR_UNFAVORABLE"])
def test_unanimidade_com_numero_par_publica(regra):
    assert (
        _codigos(_conteudo(etapa=_colegiada(evaluationsPerRegistration=4, deliberationRule=regra)))
        == []
    )


def test_a_gravacao_recusa_o_valor_fora_das_escolhas():
    with pytest.raises(StageValidationError) as recusa:
        validate_stage(_colegiada(deliberationRule="SORTEIO"), event_ids=frozenset())

    assert "regra de deliberação" in str(recusa.value)
    assert "não é uma das previstas" in str(recusa.value)
