from django.utils import timezone

from processo_seletivo.editais.domain.perfis import RecusaDeCampo


class ScheduleValidationError(RecusaDeCampo):
    pass


# O único estado que um Evento **declara** (045, `FR-736`, `FR-737`). A fase ordinária — planejado,
# em andamento, concluído — é derivada das datas na leitura, e aceitá-la como entrada seria guardar
# uma segunda fonte para o que as datas já dizem, que a Constituição (Princípio II) recusa.
# `PLANEJADO` continua aceito porque é o valor que o próprio sistema grava como *não cancelado*: o
# cliente que devolve o que leu não pode ser recusado por isso.
STATUS_DECLARAVEIS = frozenset({"PLANEJADO", "CANCELADO"})
RECUSA_DA_FASE_DECLARADA = "A fase do Evento é derivada das datas; só o cancelamento é declarado."


def validate_event(event: dict) -> None:
    start = event["startAt"]
    end = event.get("endAt")
    if not timezone.is_aware(start) or (end is not None and not timezone.is_aware(end)):
        raise ScheduleValidationError("Eventos exigem instantes com offset explícito.")
    if end is not None and start > end:
        raise ScheduleValidationError(
            "O início do Evento não pode ser posterior ao término.",
            campo="endAt",
            identidade=event.get("id", ""),
        )
    if event.get("order", 0) < 0:
        raise ScheduleValidationError("A ordem do Evento não pode ser negativa.")
    # **Depois das conferências de forma, e não antes**: o instante que não é instante continua
    # estourando onde estourava — é a contraprova de que o reaproveitamento precisa converter o
    # conteúdo publicado antes de validá-lo (`test_reaproveitamento.py`).
    status = event.get("status")
    if status is not None and status not in STATUS_DECLARAVEIS:
        raise ScheduleValidationError(
            RECUSA_DA_FASE_DECLARADA, campo="status", identidade=str(event.get("id", ""))
        )


def validate_schedule(events: list[dict]) -> None:
    ids = [str(event["id"]) for event in events]
    if len(ids) != len(set(ids)):
        raise ScheduleValidationError("Eventos não podem repetir identidade no Cronograma.")
    orders = [event.get("order", 0) for event in events]
    if len(orders) != len(set(orders)):
        raise ScheduleValidationError("Eventos não podem repetir ordem no Cronograma.")
    for event in events:
        validate_event(event)
