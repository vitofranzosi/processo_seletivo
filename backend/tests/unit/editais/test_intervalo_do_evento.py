"""Intervalos são instantes: o dia escrito sozinho não decide a ordem (101, FR-2611)."""

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    validate_for_publication,
)


@pytest.mark.parametrize("ato", [ATO_DE_PUBLICACAO, ATO_DE_RETIFICACAO])
@pytest.mark.parametrize("tipo", ["INSCRICAO", "SORTEIO", "PROVA"])
@pytest.mark.parametrize(
    ("inicio", "termino", "invalido"),
    [
        ("2027-01-01T23:50:00-03:00", "2027-01-02T00:10:00-03:00", False),
        ("2027-01-01T23:50:00-03:00", "2027-01-01T23:49:00-03:00", True),
        ("2027-01-01T23:50:00-03:00", "2027-01-02T02:50:00+00:00", False),
        ("2027-01-01T23:50:00-03:00", "2027-01-02T02:49:00+00:00", True),
        ("2027-01-01T23:50:00-03:00", None, False),
        ("inválido", "2027-01-01T23:49:00-03:00", False),
    ],
)
def test_intervalo_compara_instantes_sem_exigir_duracao_positiva(
    ato, tipo, inicio, termino, invalido
):
    achados = validate_for_publication(
        {
            "schedule": [
                {
                    "type": tipo,
                    "description": "Evento de teste",
                    "startAt": inicio,
                    "endAt": termino,
                }
            ]
        },
        ato=ato,
    )
    intervalos = [a for a in achados if a.code == "schedule_end_before_start"]
    assert bool(intervalos) is invalido
    if invalido:
        assert intervalos[0].severity == Severity.BLOCKING_ERROR
        assert "Evento de teste" in intervalos[0].message
        assert intervalos[0].path.endswith("/endAt")
