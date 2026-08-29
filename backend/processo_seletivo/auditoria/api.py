"""T087 — consulta administrativa da trilha de auditoria.

Exige permissão explícita, restringe ao escopo institucional do ator e não devolve
`idempotency_key` nem qualquer conteúdo normativo, para não transformar a trilha em
via alternativa de leitura dos agregados (III da Constituição).
"""

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from processo_seletivo.auditoria import selectors
from processo_seletivo.seguranca.application.authorization import require_permission

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


class AuditoriaView(APIView):
    def get(self, request):
        require_permission(request.user, PERMISSION)
        identificador = request.query_params.get("aggregateId")
        pagina, proximo = selectors.consultar(
            actor=request.user,
            aggregate_type=request.query_params.get("aggregateType"),
            aggregate_ids=[identificador] if identificador else None,
            cursor=request.query_params.get("cursor"),
            limit=selectors.parse_limit(request.query_params.get("limit")),
        )
        return Response(
            {
                "items": RegistroAuditoriaSerializer(pagina, many=True).data,
                "nextCursor": proximo,
            }
        )
