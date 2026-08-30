"""T087 — consulta administrativa da trilha de auditoria.

Exige permissão explícita, restringe ao escopo institucional do ator e não devolve
`idempotency_key` nem qualquer conteúdo normativo, para não transformar a trilha em
via alternativa de leitura dos agregados (III da Constituição).
"""

import base64
import binascii

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError

DEFAULT_LIMIT = 20
MAX_LIMIT = 100
PERMISSION = "auditoria:consultar"


class RegistroAuditoriaSerializer(serializers.Serializer):
    eventId = serializers.UUIDField(source="event_id")
    occurredAt = serializers.DateTimeField(source="occurred_at")
    actorSubject = serializers.CharField(source="actor_subject")
    permission = serializers.CharField()
    operation = serializers.CharField()
    aggregateType = serializers.CharField(source="aggregate_type")
    aggregateId = serializers.UUIDField(source="aggregate_id")
    previousState = serializers.CharField(source="previous_state")
    newState = serializers.CharField(source="new_state")
    previousRevision = serializers.IntegerField(source="previous_revision", allow_null=True)
    newRevision = serializers.IntegerField(source="new_revision", allow_null=True)
    reason = serializers.CharField()
    correlationId = serializers.CharField(source="correlation_id")


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


def _encode_cursor(registro):
    raw = f"{registro.occurred_at.isoformat()}|{registro.event_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _decode_cursor(cursor):
    try:
        occurred_at, event_id = (
            base64.urlsafe_b64decode(cursor.encode()).decode().split("|", 1)
        )
        return occurred_at, event_id
    except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
        raise DomainError("invalid_cursor", "O cursor informado é inválido.", 400) from exc


class AuditoriaView(APIView):
    def get(self, request):
        require_permission(request.user, PERMISSION)
        registros = RegistroAuditoria.objects.filter(
            institution_scope=request.user.institution_scope
        )
        aggregate_type = request.query_params.get("aggregateType")
        if aggregate_type:
            registros = registros.filter(aggregate_type=aggregate_type)
        aggregate_id = request.query_params.get("aggregateId")
        if aggregate_id:
            try:
                registros = registros.filter(aggregate_id=aggregate_id)
            except (ValueError, TypeError) as exc:
                raise DomainError("invalid_filter", "aggregateId deve ser um UUID.", 400) from exc
        cursor = request.query_params.get("cursor")
        if cursor:
            occurred_at, event_id = _decode_cursor(cursor)
            # Ordem decrescente estável: o cursor aponta para o último item já entregue.
            registros = registros.filter(occurred_at__lte=occurred_at).exclude(
                occurred_at=occurred_at, event_id__gte=event_id
            )
        limit = parse_limit(request.query_params.get("limit"))
        pagina = list(registros.order_by("-occurred_at", "-event_id")[: limit + 1])
        tem_mais = len(pagina) > limit
        pagina = pagina[:limit]
        return Response(
            {
                "items": RegistroAuditoriaSerializer(pagina, many=True).data,
                "nextCursor": _encode_cursor(pagina[-1]) if pagina and tem_mais else None,
            }
        )
