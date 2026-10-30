import re

from django.http import HttpResponse
from django.utils import timezone
from django.utils.http import content_disposition_header
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
    return_edital_to_drafting,
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


class ReturnEditalView(APIView):
    def post(self, request, edital_id):
        serializer = MotivoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        edital, _ = return_edital_to_drafting(
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
            autoridade_id=serializer.validated_data["signatory"]["authorityId"],
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
            document = DocumentoPublicado.objects.select_related("publicacao__edital").get(
                publicacao_id=publicacao_id
            )
        except DocumentoPublicado.DoesNotExist as exc:
            raise DomainError("not_found", "Documento não encontrado.", 404) from exc
        response = HttpResponse(bytes(document.bytes), content_type=document.content_type)
        response["ETag"] = f'"{document.document_hash}"'
        # O número do Edital é texto livre: aspas e caracteres fora do ASCII vão pela forma que o
        # navegador lê (`filename*`, RFC 6266), e não crus dentro de `filename="…"`.
        response["Content-Disposition"] = content_disposition_header(
            as_attachment=False, filename=nome_do_documento(document.publicacao)
        )
        return response


def nome_do_documento(publicacao):
    """`edital-«n»-«ano».pdf`, ou `…-retificado-«AAAA-MM-DD».pdf` (069, FR-1387, R-012).

    A data é a da publicação **no fuso institucional**: em UTC, a Retificação publicada às 23h de
    Vitória sairia com o dia seguinte no nome. A barra do número vira hífen — "01/2026" não cabe
    num nome de arquivo.
    """
    edital = publicacao.edital
    nome = f"edital-{edital.number}-{edital.year}".replace("/", "-")
    # O que nenhum sistema de arquivos aceita no nome, e o espaço, também viram hífen.
    nome = re.sub(r'[\x00-\x1f\\:*?"<>|\s-]+', "-", nome)
    if publicacao.publication_order > 1:
        dia = timezone.localtime(publicacao.published_at).date().isoformat()
        nome += f"-retificado-{dia}"
    return f"{nome}.pdf"


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
            correlation_id=request.correlation_id,
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
            autoridade_id=serializer.validated_data["signatory"]["authorityId"],
            idempotency_key=idempotency_key(request),
            correlation_id=request.correlation_id,
        )
        response = Response(PublicacaoResponseSerializer(publication).data, status=http_status)
        response["Location"] = f"/api/v1/public/publicacoes/{publication.id}"
        return response
