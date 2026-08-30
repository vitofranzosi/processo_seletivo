"""Projeções públicas: derivam somente de atos publicados, nunca do rascunho em elaboração."""

import json

from rest_framework import serializers

from processo_seletivo.publicacoes.application import selectors

DOCUMENT_URL = "/api/v1/public/publicacoes/{}/documento"


def publicacao_content(publicacao):
    return json.loads(bytes(publicacao.canonical_content).decode("utf-8"))


def publicacao_source(publicacao):
    """Identifica o ato de origem sem revelar a revisão de elaboração (FR-031)."""
    retificacao = getattr(publicacao, "retificacao", None)
    if retificacao is not None:
        return "RETIFICACAO", retificacao.id
    return "EDITAL", publicacao.edital_id


class NormativeChangeSerializer(serializers.Serializer):
    targetPath = serializers.CharField(source="target_path")
    operation = serializers.CharField()
    newValue = serializers.JSONField(source="new_value")


class PublicacaoPublicaSerializer(serializers.Serializer):
    kind = serializers.SerializerMethodField()
    id = serializers.UUIDField()
    editalId = serializers.UUIDField(source="edital_id")
    publicationOrder = serializers.IntegerField(source="publication_order")
    publishedAt = serializers.DateTimeField(source="published_at")
    effectiveAt = serializers.DateTimeField(source="effective_at")
    contentHash = serializers.CharField(source="content_hash")
    documentHash = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return selectors.PUBLICACAO

    def get_documentHash(self, obj):
        return obj.documento.document_hash


class PublicacaoDetalheSerializer(PublicacaoPublicaSerializer):
    sourceType = serializers.SerializerMethodField()
    sourceId = serializers.SerializerMethodField()
    signatory = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    documentUrl = serializers.SerializerMethodField()

    def get_sourceType(self, obj):
        return publicacao_source(obj)[0]

    def get_sourceId(self, obj):
        return str(publicacao_source(obj)[1])

    def get_signatory(self, obj):
        return {
            "authorityId": str(obj.signatory_id),
            "name": obj.signatory_name,
            "role": obj.signatory_role,
        }

    def get_content(self, obj):
        return publicacao_content(obj)

    def get_documentUrl(self, obj):
        return DOCUMENT_URL.format(obj.id)


class RetificacaoPublicaSerializer(serializers.Serializer):
    kind = serializers.SerializerMethodField()
    id = serializers.UUIDField()
    editalId = serializers.UUIDField(source="edital_id")
    publicationId = serializers.UUIDField(source="publication_id")
    justification = serializers.CharField()
    publishedAt = serializers.DateTimeField(source="publication.published_at")
    effectiveAt = serializers.DateTimeField(source="publication.effective_at")
    changes = NormativeChangeSerializer(many=True, source="alteracoes")

    def get_kind(self, obj):
        return selectors.RETIFICACAO


class VersaoConsolidadaSerializer(serializers.Serializer):
    kind = serializers.SerializerMethodField()
    id = serializers.UUIDField()
    editalId = serializers.UUIDField(source="edital_id")
    validFrom = serializers.DateTimeField(source="valid_from")
    contentHash = serializers.CharField(source="content_hash")
    content = serializers.JSONField()
    appliedPublications = serializers.JSONField(source="applied_publications")
    provenance = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return selectors.VERSAO_CONSOLIDADA

    def get_provenance(self, obj):
        """FR-030: identifica qual Publicação produziu cada caminho alterado."""
        return [
            {"targetPath": item.target_path, "publicationId": str(item.publicacao_id)}
            for item in sorted(obj.proveniencias.all(), key=lambda item: item.target_path)
        ]


HISTORY_SERIALIZERS = {
    selectors.PUBLICACAO: PublicacaoPublicaSerializer,
    selectors.RETIFICACAO: RetificacaoPublicaSerializer,
    selectors.VERSAO_CONSOLIDADA: VersaoConsolidadaSerializer,
}


def serialize_history(entries):
    return [HISTORY_SERIALIZERS[entry["kind"]](entry["item"]).data for entry in entries]
