"""Consultas públicas: expõem somente atos publicados, nunca material de elaboração."""

import base64
import binascii

from django.utils import timezone

from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError

DEFAULT_LIMIT = 20
MAX_LIMIT = 100
PUBLICACAO = "PUBLICACAO"
RETIFICACAO = "RETIFICACAO"
VERSAO_CONSOLIDADA = "VERSAO_CONSOLIDADA"
_KIND_ORDER = {PUBLICACAO: 0, RETIFICACAO: 1, VERSAO_CONSOLIDADA: 2}


def _not_found():
    return DomainError("not_found", "Recurso não encontrado.", 404)


def effective_version(*, edital_id, at=None):
    """Versão vigente no instante informado, sem aplicar vigências ainda não iniciadas."""
    moment = at or timezone.now()
    version = (
        VersaoConsolidada.objects.filter(edital_id=edital_id, valid_from__lte=moment)
        .order_by("-valid_from", "-materialized_at")
        .first()
    )
    if version is None:
        raise DomainError(
            "no_effective_version",
            "Não havia conteúdo vigente para este Edital no instante consultado.",
            404,
        )
    return version


def consolidated_version(*, versao_id):
    try:
        return VersaoConsolidada.objects.get(pk=versao_id)
    except VersaoConsolidada.DoesNotExist as exc:
        raise _not_found() from exc


def published_publication(*, publicacao_id):
    try:
        return Publicacao.objects.select_related("documento").get(pk=publicacao_id)
    except Publicacao.DoesNotExist as exc:
        raise _not_found() from exc


def published_retification(*, retificacao_id):
    """Retificação ainda não publicada não existe para o público (FR-031)."""
    try:
        return (
            Retificacao.objects.select_related("publication")
            .prefetch_related("alteracoes")
            .get(pk=retificacao_id, status=Retificacao.Status.PUBLICADA)
        )
    except Retificacao.DoesNotExist as exc:
        raise _not_found() from exc


def _sort_key(entry):
    return (entry["occurredAt"], _KIND_ORDER[entry["kind"]], str(entry["item"].id))


def _encode_cursor(entry):
    occurred_at, kind_rank, identifier = _sort_key(entry)
    raw = f"{occurred_at.isoformat()}|{kind_rank}|{identifier}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _decode_cursor(cursor):
    try:
        occurred_at, kind_rank, identifier = (
            base64.urlsafe_b64decode(cursor.encode()).decode().split("|", 2)
        )
        return (occurred_at, int(kind_rank), identifier)
    except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
        raise DomainError("invalid_cursor", "O cursor informado é inválido.", 400) from exc


def parse_limit(value):
    if value in (None, ""):
        return DEFAULT_LIMIT
    try:
        limit = int(value)
    except (TypeError, ValueError) as exc:
        raise DomainError("invalid_limit", "O limite deve ser um inteiro.", 400) from exc
    if not 1 <= limit <= MAX_LIMIT:
        raise DomainError("invalid_limit", f"O limite deve estar entre 1 e {MAX_LIMIT}.", 400)
    return limit


def public_history(*, edital_id, cursor=None, limit=DEFAULT_LIMIT):
    """Edital original, Retificações publicadas e versões consolidadas, em ordem cronológica."""
    entries = [
        {"kind": PUBLICACAO, "item": item, "occurredAt": item.published_at}
        for item in Publicacao.objects.filter(edital_id=edital_id).select_related("documento")
    ]
    entries += [
        {"kind": RETIFICACAO, "item": item, "occurredAt": item.publication.published_at}
        for item in Retificacao.objects.filter(
            edital_id=edital_id, status=Retificacao.Status.PUBLICADA
        )
        .select_related("publication")
        .prefetch_related("alteracoes")
    ]
    entries += [
        {"kind": VERSAO_CONSOLIDADA, "item": item, "occurredAt": item.valid_from}
        for item in VersaoConsolidada.objects.filter(edital_id=edital_id)
    ]
    entries.sort(key=_sort_key)
    if cursor:
        after = _decode_cursor(cursor)
        entries = [
            entry
            for entry in entries
            if (_sort_key(entry)[0].isoformat(), *_sort_key(entry)[1:]) > after
        ]
    page = entries[:limit]
    has_more = len(entries) > limit
    return page, (_encode_cursor(page[-1]) if page and has_more else None)
