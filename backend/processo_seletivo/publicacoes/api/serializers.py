from rest_framework import serializers


class HomologacaoSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=1)


class MotivoSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=1)


class TransicaoSerializer(serializers.Serializer):
    """Corpo comum das transições: motivo textual e opcional.

    Quais transições exigem motivo é regra de domínio; aqui só se garante o tipo, para que
    um `reason` não textual seja rejeitado como requisição inválida e não quebre o command.
    """

    reason = serializers.CharField(required=False, allow_blank=True, default="")


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
    """Os limites espelham as colunas que recebem estes campos.

    Sem eles o excesso atravessa a borda e estoura no PostgreSQL como erro interno: 500 não é
    contrato, e a recusa por tamanho é informação que o cliente consegue usar.
    """

    # `AlteracaoNormativa.target_path` é CharField(max_length=1000).
    targetPath = serializers.CharField(min_length=1, max_length=1000)
    operation = serializers.ChoiceField(choices=["ADD", "REPLACE", "REMOVE"])
    newValue = serializers.JSONField(required=False, allow_null=True)
    # SHA-256 em hexadecimal: 64 caracteres, o tamanho exato da coluna.
    expectedPreviousHash = serializers.CharField(
        required=False, allow_blank=True, max_length=64
    )


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
