from rest_framework import serializers

from processo_seletivo.processos.models import Edital, ProcessoSeletivo


class CreateEditalSerializer(serializers.Serializer):
    number = serializers.CharField(min_length=1, max_length=50)
    year = serializers.IntegerField(min_value=2000, max_value=9999)
    title = serializers.CharField(min_length=1, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)


class CreateProcessSerializer(serializers.Serializer):
    institutionalCode = serializers.CharField(min_length=1, max_length=100)
    title = serializers.CharField(min_length=1, max_length=255)
    firstEdital = CreateEditalSerializer()


class AdministrativeActSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=1)


class ProcessoResponseSerializer(serializers.ModelSerializer):
    institutionalCode = serializers.CharField(source="institutional_code")

    class Meta:
        model = ProcessoSeletivo
        fields = ["id", "institutionalCode", "status", "revision"]


class EditalResponseSerializer(serializers.ModelSerializer):
    processoId = serializers.UUIDField(source="processo_id")

    class Meta:
        model = Edital
        fields = ["id", "processoId", "status", "revision"]
