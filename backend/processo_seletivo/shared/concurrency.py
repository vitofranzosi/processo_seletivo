import hashlib
import re

from django.db import connection
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


def travar_consultivamente(material: str, *, esperar: bool = True) -> bool:
    """A trava consultiva da transação sobre `material`, liberada no commit ou no rollback.

    **Serializa sem travar linha.** Travar linhas não serializa a ausência delas, e as tabelas
    append-only não dão à role de runtime o `UPDATE` que `FOR UPDATE` exige. A chave é
    determinística: o mesmo material produz sempre o mesmo inteiro, e colidir custaria serialização
    desnecessária entre dois atos, nunca correção.

    `esperar=False` não fica na fila: devolve `False` se outra transação já a tem. É o que serve a
    quem faz trabalho lento sob a trava — uma conversa com o servidor de correio — e prefere não
    empilhar requisições atrás dela (181).

    Fora do PostgreSQL é no-op e devolve `True`: o SQLite serializa a escrita inteira, e a corrida
    que a trava impede não existe lá.
    """
    if connection.vendor != "postgresql":
        return True
    chave = int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big", signed=True)
    with connection.cursor() as cursor:
        if esperar:
            cursor.execute("SELECT pg_advisory_xact_lock(%s)", [chave])
            return True
        cursor.execute("SELECT pg_try_advisory_xact_lock(%s)", [chave])
        return bool(cursor.fetchone()[0])
