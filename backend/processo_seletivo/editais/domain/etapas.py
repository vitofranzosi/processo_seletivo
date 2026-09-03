"""Invariantes da Etapa de Avaliação.

No molde de `editais/domain/cronograma.py`: o que o command atravessa, e não o que o serializer
declara. A interface administrativa invoca o command diretamente e não passa pelo serializer da
API, de modo que validar apenas ali deixaria sem verificação justamente o canal onde o dado é
digitado.
"""

from processo_seletivo.editais.domain.perfis import RecusaDeCampo


class StageValidationError(RecusaDeCampo):
    pass


def validate_stage(stage: dict, *, event_ids: frozenset[str]) -> None:
    if not (stage.get("name") or "").strip():
        raise StageValidationError(
            "A Etapa de Avaliação exige nome.", campo="name", identidade=stage.get("id", "")
        )
    if stage.get("order", 0) < 0:
        raise StageValidationError("A ordem da Etapa não pode ser negativa.")
    peso = stage.get("weight")
    # Peso zero afirmaria uma ponderação que não pondera; "esta Etapa não pondera" exprime-se
    # pela ausência, como o percentual da Regra Normativa (FR-020).
    if peso is not None and peso <= 0:
        raise StageValidationError(
            "O peso da Etapa, quando informado, deve ser maior que zero.",
            campo="weight",
            identidade=stage.get("id", ""),
        )
    nota = stage.get("minimumScore")
    if nota is not None and nota < 0:
        raise StageValidationError(
            "A nota mínima da Etapa não pode ser negativa.",
            campo="minimumScore",
            identidade=stage.get("id", ""),
        )
    # As duas do incremento da `012`, verificadas **aqui** porque é aqui que o command passa: a
    # interface administrativa não atravessa o serializer da API, e deixar a faixa só para o
    # `CheckConstraint` transformaria dado digitado errado em erro de banco (FR-007).
    previstas = stage.get("evaluationsPerRegistration")
    if previstas is not None and previstas < 1:
        raise StageValidationError(
            "A Etapa recebe ao menos uma avaliação por inscrição.",
            campo="evaluationsPerRegistration",
            identidade=stage.get("id", ""),
        )
    maxima = stage.get("maximumScore")
    # Máxima zero afirmaria uma pontuação que não pontua, pelo mesmo motivo do peso. Ausência é
    # que exprime "o Edital não declarou limite".
    if maxima is not None and maxima <= 0:
        raise StageValidationError(
            "A pontuação máxima da Etapa, quando informada, deve ser maior que zero.",
            campo="maximumScore",
            identidade=stage.get("id", ""),
        )
    if nota is not None and maxima is not None and nota > maxima:
        raise StageValidationError(
            "A nota mínima da Etapa não pode superar a pontuação máxima.",
            campo="minimumScore",
            identidade=stage.get("id", ""),
        )
    evento = stage.get("scheduleEventId")
    if evento is not None and str(evento) not in event_ids:
        raise StageValidationError(
            "A Etapa referencia um Evento que não existe no Cronograma deste Edital."
        )


def validate_stages(stages: list[dict], *, schedule: list[dict]) -> None:
    """As Etapas são opcionais; o que não é opcional é a coerência entre elas.

    O Evento referenciado é conferido contra o Cronograma **da mesma gravação**, e não contra o
    banco: `replace_draft` substitui o rascunho inteiro, então um Evento removido no mesmo POST já
    não existe — e um vínculo não pode sobreviver ao Evento que o sustenta.
    """
    ids = [str(stage["id"]) for stage in stages]
    if len(ids) != len(set(ids)):
        raise StageValidationError("Etapas não podem repetir identidade no Edital.")
    orders = [stage.get("order", 0) for stage in stages]
    if len(orders) != len(set(orders)):
        raise StageValidationError("Etapas não podem repetir ordem no Edital.")
    event_ids = frozenset(str(event["id"]) for event in schedule)
    for stage in stages:
        validate_stage(stage, event_ids=event_ids)
