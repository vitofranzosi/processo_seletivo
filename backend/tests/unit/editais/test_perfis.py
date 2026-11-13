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
    # Desde a 162 o limitado não traz número: ele vem do corte do marco que convoca (FR-6931).
    validate_profile(profile(immediateVacancies=0, reserveType="LIMITED", reserveLimit=None))
    validate_profile(profile(immediateVacancies=0, reserveType="UNLIMITED"))


def test_rejects_typed_limit_and_says_where_it_comes_from():
    """FR-6931: o número digitado é recusado por qualquer caminho, e a frase diz a origem."""
    for limite in (10, 0):
        with pytest.raises(ProfileValidationError) as recusa:
            validate_profile(profile(reserveType="LIMITED", reserveLimit=limite))
        assert str(recusa.value) == (
            "O número do cadastro de reserva limitado não se digita: ele vem do corte do marco "
            "que convoca deste Perfil."
        )
        assert recusa.value.campo == "reserveLimit"


@pytest.mark.parametrize(
    "payload",
    [
        profile(reserveType="NONE", reserveLimit=1),
        profile(reserveType="LIMITED", reserveLimit=6),
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
