from datetime import UTC, datetime

import pytest

from processo_seletivo.editais.domain.cronograma import ScheduleValidationError, validate_event


def event(**overrides):
    data = {
        "id": "00000000-0000-0000-0000-000000000301",
        "type": "INSCRICAO",
        "description": "Inscrições",
        "startAt": datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        "endAt": None,
        "order": 1,
    }
    return {**data, **overrides}


def test_accepts_point_and_period_events():
    validate_event(event())
    validate_event(event(endAt=datetime(2026, 9, 2, 12, 0, tzinfo=UTC)))


def test_rejects_inverted_period():
    with pytest.raises(ScheduleValidationError):
        validate_event(event(endAt=datetime(2026, 8, 31, 12, 0, tzinfo=UTC)))


def test_rejects_naive_datetime():
    with pytest.raises(ScheduleValidationError):
        validate_event(event(startAt=datetime(2026, 9, 1, 12, 0)))
