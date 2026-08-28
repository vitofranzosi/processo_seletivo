import pytest

from processo_seletivo.editais.domain.perfis import ProfileValidationError, validate_profile


def profile(**overrides):
    data = {
        "code": "DOCENTE-1",
        "name": "Docente",
        "immediateVacancies": 1,
        "reserveType": "NONE",
        "reserveLimit": None,
        "competitionModalities": [],
    }
    return {**data, **overrides}


def test_allows_immediate_vacancies_without_reserve():
    validate_profile(profile())


def test_allows_limited_and_unlimited_reserve_without_immediate_vacancies():
    validate_profile(profile(immediateVacancies=0, reserveType="LIMITED", reserveLimit=10))
    validate_profile(profile(immediateVacancies=0, reserveType="UNLIMITED"))


@pytest.mark.parametrize(
    "payload",
    [
        profile(reserveType="NONE", reserveLimit=1),
        profile(reserveType="LIMITED", reserveLimit=None),
        profile(reserveType="UNLIMITED", reserveLimit=1),
        profile(immediateVacancies=-1),
    ],
)
def test_rejects_incompatible_reserve_configuration(payload):
    with pytest.raises(ProfileValidationError):
        validate_profile(payload)


def test_rejects_duplicate_competition_modality_codes():
    payload = profile(
        competitionModalities=[
            {"code": "AC", "name": "Ampla concorrência"},
            {"code": "AC", "name": "Duplicada"},
        ]
    )
    with pytest.raises(ProfileValidationError):
        validate_profile(payload)
