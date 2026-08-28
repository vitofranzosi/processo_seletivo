from django.utils import timezone


class ScheduleValidationError(ValueError):
    pass


def validate_event(event: dict) -> None:
    start = event["startAt"]
    end = event.get("endAt")
    if not timezone.is_aware(start) or (end is not None and not timezone.is_aware(end)):
        raise ScheduleValidationError("Eventos exigem instantes com offset explícito.")
    if end is not None and start > end:
        raise ScheduleValidationError("O início do Evento não pode ser posterior ao término.")
    if event.get("order", 0) < 0:
        raise ScheduleValidationError("A ordem do Evento não pode ser negativa.")


def validate_schedule(events: list[dict]) -> None:
    ids = [str(event["id"]) for event in events]
    if len(ids) != len(set(ids)):
        raise ScheduleValidationError("Eventos não podem repetir identidade no Cronograma.")
    orders = [event.get("order", 0) for event in events]
    if len(orders) != len(set(orders)):
        raise ScheduleValidationError("Eventos não podem repetir ordem no Cronograma.")
    for event in events:
        validate_event(event)
