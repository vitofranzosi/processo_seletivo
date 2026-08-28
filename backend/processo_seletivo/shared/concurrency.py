import re

from django.db.models import F

from processo_seletivo.shared.api.problems import DomainError

ETAG_PATTERN = re.compile(r'^(?:W/)?"(?P<revision>\d+)"$')


def etag(revision: int) -> str:
    return f'"{revision}"'


def parse_if_match(value: str | None) -> int:
    if not value:
        raise DomainError("precondition_required", "O header If-Match é obrigatório.", 428)
    match = ETAG_PATTERN.match(value)
    if not match:
        raise DomainError("invalid_etag", "O header If-Match é inválido.", 400)
    return int(match.group("revision"))


def compare_and_swap(queryset, *, pk, expected_revision: int, **changes) -> int:
    updated = queryset.filter(pk=pk, revision=expected_revision).update(
        **changes, revision=F("revision") + 1
    )
    if updated != 1:
        raise DomainError("stale_revision", "A revisão informada está obsoleta.", 412)
    return expected_revision + 1
