from rest_framework.response import Response
from rest_framework.views import APIView

from processo_seletivo.editais.api.serializers import EditalDraftSerializer
from processo_seletivo.editais.application.draft import replace_draft
from processo_seletivo.processos.api.serializers import EditalResponseSerializer
from processo_seletivo.shared.concurrency import etag, parse_if_match


class EditalDraftView(APIView):
    def put(self, request, edital_id):
        serializer = EditalDraftSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        edital = replace_draft(
            actor=request.user,
            edital_id=edital_id,
            expected_revision=parse_if_match(request.headers.get("If-Match")),
            profiles=serializer.validated_data["profiles"],
            schedule=serializer.validated_data["schedule"],
            stages=serializer.validated_data.get("stages", []),
            sections=serializer.validated_data.get("sections", []),
            document_requirements=serializer.validated_data.get("documentRequirements", []),
            correlation_id=request.correlation_id,
        )
        response = Response(EditalResponseSerializer(edital).data)
        response["ETag"] = etag(edital.revision)
        return response
