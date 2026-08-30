from rest_framework.response import Response
from rest_framework.views import APIView

from processo_seletivo.processos.api.serializers import (
    AdministrativeActSerializer,
    CreateEditalSerializer,
    CreateProcessSerializer,
    EditalResponseSerializer,
    ProcessoResponseSerializer,
)
from processo_seletivo.processos.application.commands import (
    activate_process,
    add_edital,
    create_process_with_first_edital,
)
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.concurrency import etag, parse_if_match


def idempotency_key(request) -> str:
    value = request.headers.get("Idempotency-Key", "")
    if not 16 <= len(value) <= 128:
        raise DomainError(
            "idempotency_key_required",
            "Idempotency-Key deve possuir entre 16 e 128 caracteres.",
            400,
        )
    return value


class ProcessCollectionView(APIView):
    def post(self, request):
        serializer = CreateProcessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        processo, http_status = create_process_with_first_edital(
            actor=request.user,
            data=serializer.validated_data,
            idempotency_key=idempotency_key(request),
            correlation_id=request.correlation_id,
        )
        response = Response(ProcessoResponseSerializer(processo).data, status=http_status)
        response["ETag"] = etag(processo.revision)
        return response


class EditalCollectionView(APIView):
    def post(self, request, processo_id):
        serializer = CreateEditalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        edital, http_status = add_edital(
            actor=request.user,
            processo_id=processo_id,
            data=serializer.validated_data,
            idempotency_key=idempotency_key(request),
            correlation_id=request.correlation_id,
        )
        response = Response(EditalResponseSerializer(edital).data, status=http_status)
        response["ETag"] = etag(edital.revision)
        return response


class ActivateProcessView(APIView):
    def post(self, request, processo_id):
        serializer = AdministrativeActSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        processo, _ = activate_process(
            actor=request.user,
            processo_id=processo_id,
            expected_revision=parse_if_match(request.headers.get("If-Match")),
            reason=serializer.validated_data["reason"],
            idempotency_key=idempotency_key(request),
            correlation_id=request.correlation_id,
        )
        response = Response(ProcessoResponseSerializer(processo).data)
        response["ETag"] = etag(processo.revision)
        return response
