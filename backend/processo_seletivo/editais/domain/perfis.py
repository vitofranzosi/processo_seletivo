from decimal import Decimal, InvalidOperation


class RecusaDeCampo(ValueError):
    """Uma recusa do domínio que sabe **a que campo pertence**.

    FR-033 pede que a recusa apareça em resumo ancorado e junto do campo. A interface não tinha
    como fazer isso porque estas exceções carregavam mensagem e nada mais — e ancorar exige saber
    qual campo, de qual linha.

    `campo` é o nome canônico (`name`, `startAt`, `reserveLimit`); `identidade` é o `id` da entidade
    quando ela tem um, para que a interface encontre a linha certa. Os dois são **opcionais**: as
    regras que valem para a coleção inteira — "o Edital deve possuir ao menos um Perfil" — não
    pertencem a campo nenhum, e forçá-las a apontar um seria pior do que não apontar.
    """

    def __init__(self, mensagem, *, campo="", identidade=""):
        super().__init__(mensagem)
        self.campo = campo
        self.identidade = str(identidade or "")


class ProfileValidationError(RecusaDeCampo):
    pass


def validate_normative_rule(rule: dict) -> None:
    """A faixa do percentual vive aqui, e não no serializer (FR-030).

    A interface administrativa invoca o command diretamente e não atravessa o serializer da API:
    validar apenas ali deixaria sem verificação justamente o canal onde o dado é digitado.

    **Zero não é reserva de nenhuma vaga: é ausência de reserva.** Modalidade sem percentual
    exprime-se pela ausência da regra ou do campo, e um zero afirmaria uma reserva que reserva
    nada. Não se valida soma entre modalidades — cotas não somam cem por cento (PPI 20% e PcD 5%
    convivem), e a regra de composição pertence à jornada do candidato, que está fora de escopo.
    """
    bruto = rule.get("percentage")
    if bruto is None:
        return
    try:
        percentual = Decimal(str(bruto))
    except InvalidOperation as exc:
        raise ProfileValidationError(
            f"'{bruto}' não é um percentual válido para a Regra Normativa."
        ) from exc
    if not 0 < percentual <= 100:
        raise ProfileValidationError(
            "O percentual da Regra Normativa, quando informado, deve ser maior que zero e "
            "menor ou igual a cem."
        )


def validate_profile(profile: dict) -> None:
    immediate = profile.get("immediateVacancies", 0)
    reserve_type = profile.get("reserveType")
    reserve_limit = profile.get("reserveLimit")
    if immediate < 0:
        raise ProfileValidationError(
            "Vagas imediatas não podem ser negativas.",
            campo="immediateVacancies",
            identidade=profile.get("id", ""),
        )
    if reserve_type == "NONE" and reserve_limit is not None:
        raise ProfileValidationError(
            "Cadastro Reserva inexistente não admite limite.",
            campo="reserveLimit",
            identidade=profile.get("id", ""),
        )
    if reserve_type == "LIMITED" and (reserve_limit is None or reserve_limit < 0):
        raise ProfileValidationError(
            "Cadastro Reserva limitado exige limite não negativo.",
            campo="reserveLimit",
            identidade=profile.get("id", ""),
        )
    if reserve_type == "UNLIMITED" and reserve_limit is not None:
        raise ProfileValidationError(
            "Cadastro Reserva ilimitado não admite limite.",
            campo="reserveLimit",
            identidade=profile.get("id", ""),
        )
    if reserve_type not in {"NONE", "LIMITED", "UNLIMITED"}:
        raise ProfileValidationError("Tipo de Cadastro Reserva inválido.")
    modalities = profile.get("competitionModalities", [])
    modality_codes = [item["code"] for item in modalities]
    if len(modality_codes) != len(set(modality_codes)):
        raise ProfileValidationError("Modalidades de Concorrência não podem se repetir no Perfil.")
    for modality in modalities:
        rule = modality.get("normativeRule")
        if rule:
            validate_normative_rule(rule)


def validate_profiles(profiles: list[dict]) -> None:
    if not profiles:
        raise ProfileValidationError("O Edital deve possuir ao menos um Perfil.")
    codes = [profile["code"] for profile in profiles]
    if len(codes) != len(set(codes)):
        raise ProfileValidationError("Códigos de Perfil não podem se repetir no Edital.")
    for profile in profiles:
        validate_profile(profile)
