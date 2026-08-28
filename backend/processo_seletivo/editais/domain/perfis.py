class ProfileValidationError(ValueError):
    pass


def validate_profile(profile: dict) -> None:
    immediate = profile.get("immediateVacancies", 0)
    reserve_type = profile.get("reserveType")
    reserve_limit = profile.get("reserveLimit")
    if immediate < 0:
        raise ProfileValidationError("Vagas imediatas não podem ser negativas.")
    if reserve_type == "NONE" and reserve_limit is not None:
        raise ProfileValidationError("Cadastro Reserva inexistente não admite limite.")
    if reserve_type == "LIMITED" and (reserve_limit is None or reserve_limit < 0):
        raise ProfileValidationError("Cadastro Reserva limitado exige limite não negativo.")
    if reserve_type == "UNLIMITED" and reserve_limit is not None:
        raise ProfileValidationError("Cadastro Reserva ilimitado não admite limite.")
    if reserve_type not in {"NONE", "LIMITED", "UNLIMITED"}:
        raise ProfileValidationError("Tipo de Cadastro Reserva inválido.")
    modality_codes = [item["code"] for item in profile.get("competitionModalities", [])]
    if len(modality_codes) != len(set(modality_codes)):
        raise ProfileValidationError("Modalidades de Concorrência não podem se repetir no Perfil.")


def validate_profiles(profiles: list[dict]) -> None:
    if not profiles:
        raise ProfileValidationError("O Edital deve possuir ao menos um Perfil.")
    codes = [profile["code"] for profile in profiles]
    if len(codes) != len(set(codes)):
        raise ProfileValidationError("Códigos de Perfil não podem se repetir no Edital.")
    for profile in profiles:
        validate_profile(profile)
