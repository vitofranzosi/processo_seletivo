from rest_framework import serializers


class HomologacaoSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=1)


class MotivoSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=1)


class SignatorySerializer(serializers.Serializer):
    authorityId = serializers.UUIDField()
    name = serializers.CharField(min_length=1, max_length=255)
    role = serializers.CharField(min_length=1, max_length=255)


class PublicacaoRequestSerializer(serializers.Serializer):
    signatory = SignatorySerializer()
    reason = serializers.CharField(min_length=1, required=False, allow_blank=True, default="")


class PublicacaoResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    editalId = serializers.UUIDField(source="edital_id")
    publicationOrder = serializers.IntegerField(source="publication_order")
    publishedAt = serializers.DateTimeField(source="published_at")
    effectiveAt = serializers.DateTimeField(source="effective_at")
    contentHash = serializers.CharField(source="content_hash")
    documentHash = serializers.SerializerMethodField()

    def get_documentHash(self, obj):
        return obj.documento.document_hash


class ChangeSerializer(serializers.Serializer):
    targetPath = serializers.CharField()
    operation = serializers.ChoiceField(choices=["ADD", "REPLACE", "REMOVE"])
    newValue = serializers.JSONField(required=False, allow_null=True)
    expectedPreviousHash = serializers.CharField(required=False, allow_blank=True)


class RetificacaoDraftSerializer(serializers.Serializer):
    """Atualização de rascunho: `baseSnapshotId` é opcional e, quando vem, rebaseia."""

    baseSnapshotId = serializers.UUIDField(required=False)
    justification = serializers.CharField(min_length=1)
    effectiveAt = serializers.DateTimeField(required=False, allow_null=True)
    changes = ChangeSerializer(many=True, allow_empty=False)


class CriarRetificacaoSerializer(RetificacaoDraftSerializer):
    """Criação: a versão base é obrigatória, conforme CriarRetificacaoRequest."""

    baseSnapshotId = serializers.UUIDField()


class RetificacaoResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    editalId = serializers.UUIDField(source="edital_id")
    status = serializers.CharField()
    effectiveAt = serializers.DateTimeField(source="effective_at", allow_null=True)
    revision = serializers.IntegerField()
