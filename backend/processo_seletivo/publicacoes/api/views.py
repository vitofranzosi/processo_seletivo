from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from processo_seletivo.processos.api.serializers import EditalResponseSerializer
from processo_seletivo.processos.api.views import idempotency_key
from processo_seletivo.publicacoes.api.serializers import (
    CriarRetificacaoSerializer,
    HomologacaoSerializer,
    MotivoSerializer,
    PublicacaoRequestSerializer,
    PublicacaoResponseSerializer,
    RetificacaoDraftSerializer,
    RetificacaoResponseSerializer,
    TransicaoSerializer,
)
from processo_seletivo.publicacoes.application.publish_edital import (
    homologate_edital,
    publish_edital,
    revoke_homologation,
    submit_edital,
)
from processo_seletivo.publicacoes.application.retificacoes import (
    create_retification,
    edit_retification,
    publish_retification,
    transition_retification,
)
from processo_seletivo.publicacoes.models import DocumentoPublicado
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.concurrency import etag, parse_if_match


class SubmitEditalView(APIView):
    def post(self, request, edital_id):
        edital, findings, _ = submit_edital(
            actor=request.user,
            edital_id=edital_id,
            expected_revision=parse_if_match(request.headers.get("If-Match")),
            idempotency_key=idempotency_key(request),
            correlation_id=request.correlation_id,
        )
        edital.validation_findings = findings
        response = Response(EditalResponseSerializer(edital).data)
        response["ETag"] = etag(edital.revision)
        return response


class HomologateEditalView(APIView):
    def post(self, request, edital_id):
        serializer = HomologacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        edital, _ = homologate_edital(
            actor=request.user,
            edital_id=edital_id,
            expected_revision=parse_if_match(request.headers.get("If-Match")),
            reason=serializer.validated_data["reason"],
            idempotency_key=idempotency_key(request),
            correlation_id=request.correlation_id,
        )
        response = Response(EditalResponseSerializer(edital).data)
        response["ETag"] = etag(edital.revision)
        return response


class RevokeHomologationView(APIView):
    def post(self, request, edital_id):
        serializer = MotivoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        edital, _ = revoke_homologation(
            actor=request.user,
            edital_id=edital_id,
            expected_revision=parse_if_match(request.headers.get("If-Match")),
            reason=serializer.validated_data["reason"],
            idempotency_key=idempotency_key(request),
            correlation_id=request.correlation_id,
        )
        response = Response(EditalResponseSerializer(edital).data)
        response["ETag"] = etag(edital.revision)
        return response


class PublishEditalView(APIView):
    def post(self, request, edital_id):
        serializer = PublicacaoRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        publication, http_status = publish_edital(
            actor=request.user,
            edital_id=edital_id,
            expected_revision=parse_if_match(request.headers.get("If-Match")),
            signatory=serializer.validated_data["signatory"],
            reason=serializer.validated_data["reason"],
            idempotency_key=idempotency_key(request),
            correlation_id=request.correlation_id,
        )
        response = Response(PublicacaoResponseSerializer(publication).data, status=http_status)
        response["Location"] = f"/api/v1/public/publicacoes/{publication.id}"
        return response


class PublishedDocumentView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, publicacao_id):
        try:
            document = DocumentoPublicado.objects.select_related("publicacao").get(
                publicacao_id=publicacao_id
            )
        except DocumentoPublicado.DoesNotExist as exc:
            raise DomainError("not_found", "Documento não encontrado.", 404) from exc
        response = HttpResponse(bytes(document.bytes), content_type=document.content_type)
        response["ETag"] = f'"{document.document_hash}"'
        return response


class CreateRetificationView(APIView):
    def post(self, request, edital_id):
        serializer = CriarRetificacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item, http_status = create_retification(
            actor=request.user,
            edital_id=edital_id,
            data=serializer.validated_data,
            idempotency_key=idempotency_key(request),
            correlation_id=request.correlation_id,
        )
        response = Response(RetificacaoResponseSerializer(item).data, status=http_status)
        response["ETag"] = etag(item.revision)
        return response


class EditRetificationView(APIView):
    def put(self, request, retificacao_id):
        serializer = RetificacaoDraftSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = edit_retification(
            actor=request.user,
            retificacao_id=retificacao_id,
            expected_revision=parse_if_match(request.headers.get("If-Match")),
            data=serializer.validated_data,
        )
        response = Response(RetificacaoResponseSerializer(item).data)
        response["ETag"] = etag(item.revision)
        return response


class RetificationTransitionView(APIView):
    action = None

    def post(self, request, retificacao_id):
        serializer = TransicaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item, _ = transition_retification(
            actor=request.user,
            retificacao_id=retificacao_id,
            expected_revision=parse_if_match(request.headers.get("If-Match")),
            action=self.action,
            reason=serializer.validated_data["reason"],
            idempotency_key=idempotency_key(request),
            correlation_id=request.correlation_id,
        )
        response = Response(RetificacaoResponseSerializer(item).data)
        response["ETag"] = etag(item.revision)
        return response


class SubmitRetificationView(RetificationTransitionView):
    action = "submeter"


class HomologateRetificationView(RetificationTransitionView):
    action = "homologar"


class ReturnRetificationView(RetificationTransitionView):
    action = "devolver"


class CancelRetificationView(RetificationTransitionView):
    action = "cancelar"


class PublishRetificationView(APIView):
    def post(self, request, retificacao_id):
        serializer = PublicacaoRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        publication, http_status = publish_retification(
            actor=request.user,
            retificacao_id=retificacao_id,
            expected_revision=parse_if_match(request.headers.get("If-Match")),
            signatory=serializer.validated_data["signatory"],
            idempotency_key=idempotency_key(request),
            correlation_id=request.correlation_id,
        )
        response = Response(PublicacaoResponseSerializer(publication).data, status=http_status)
        response["Location"] = f"/api/v1/public/publicacoes/{publication.id}"
        return response
