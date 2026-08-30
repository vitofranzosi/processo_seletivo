from rest_framework.response import Response
from rest_framework.views import APIView

from processo_seletivo.processos.api.serializers import (
    AdministrativeActSerializer,
    EditalResponseSerializer,
    ProcessoResponseSerializer,
)
from processo_seletivo.processos.api.views import idempotency_key
from processo_seletivo.processos.application.finalizacao import (
    cancel_edital,
    cancel_process,
    close_edital,
    close_process,
)
from processo_seletivo.shared.concurrency import etag, parse_if_match


class FinalizationView(APIView):
    """Ato final explícito: exige motivo, If-Match e Idempotency-Key."""

    command = None
    id_argument = None
    serializer = None

    def post(self, request, **kwargs):
        payload = AdministrativeActSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        aggregate, _ = type(self).command(
            actor=request.user,
            expected_revision=parse_if_match(request.headers.get("If-Match")),
            reason=payload.validated_data["reason"],
            idempotency_key=idempotency_key(request),
            correlation_id=request.correlation_id,
            **{self.id_argument: kwargs[self.id_argument]},
        )
        response = Response(self.serializer(aggregate).data)
        response["ETag"] = etag(aggregate.revision)
        return response


class CloseProcessView(FinalizationView):
    command = staticmethod(close_process)
    id_argument = "processo_id"
    serializer = ProcessoResponseSerializer


class CancelProcessView(FinalizationView):
    command = staticmethod(cancel_process)
    id_argument = "processo_id"
    serializer = ProcessoResponseSerializer


class CloseEditalView(FinalizationView):
    command = staticmethod(close_edital)
    id_argument = "edital_id"
    serializer = EditalResponseSerializer


class CancelEditalView(FinalizationView):
    command = staticmethod(cancel_edital)
    id_argument = "edital_id"
    serializer = EditalResponseSerializer
