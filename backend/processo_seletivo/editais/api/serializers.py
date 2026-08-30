from rest_framework import serializers

from processo_seletivo.editais.domain.cronograma import ScheduleValidationError, validate_event
from processo_seletivo.editais.domain.perfis import ProfileValidationError, validate_profile


class NormativeRuleSerializer(serializers.Serializer):
    foundation = serializers.CharField(min_length=1)
    version = serializers.CharField(min_length=1, max_length=50)
    percentage = serializers.DecimalField(max_digits=7, decimal_places=4, required=False)
    calculation = serializers.JSONField(required=False)
    rounding = serializers.JSONField(required=False)
    distribution = serializers.JSONField(required=False)
    callRules = serializers.JSONField(required=False)
    effectiveFrom = serializers.DateTimeField(required=False)


class CompetitionModalitySerializer(serializers.Serializer):
    code = serializers.CharField(min_length=1, max_length=100)
    name = serializers.CharField(min_length=1, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    normativeRule = NormativeRuleSerializer(required=False)


class ProfileSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    code = serializers.CharField(min_length=1, max_length=100)
    name = serializers.CharField(min_length=1, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    requirements = serializers.ListField(child=serializers.JSONField(), required=False)
    immediateVacancies = serializers.IntegerField(min_value=0)
    reserveType = serializers.ChoiceField(choices=["NONE", "LIMITED", "UNLIMITED"])
    reserveLimit = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    locality = serializers.CharField(required=False, allow_blank=True)
    classificationInformation = serializers.JSONField(required=False)
    callInformation = serializers.JSONField(required=False)
    competitionModalities = CompetitionModalitySerializer(many=True)

    def validate(self, attrs):
        try:
            validate_profile(attrs)
        except ProfileValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return attrs


class EventSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.CharField(min_length=1, max_length=100)
    description = serializers.CharField(min_length=1, max_length=500)
    startAt = serializers.DateTimeField()
    endAt = serializers.DateTimeField(required=False, allow_null=True)
    order = serializers.IntegerField(min_value=0, required=False, default=0)
    status = serializers.ChoiceField(
        choices=["PLANEJADO", "EM_ANDAMENTO", "CONCLUIDO", "CANCELADO"],
        required=False,
    )

    def validate(self, attrs):
        try:
            validate_event(attrs)
        except ScheduleValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return attrs


class EditalDraftSerializer(serializers.Serializer):
    """Rascunho normativo do Edital: Perfis e Cronograma.

    `editorialContent` era aceito aqui e no contrato, e descartado em silêncio — nenhum comando o
    persistia, nenhum snapshot o carregava, nenhum PDF o renderizava. Foi removido em vez de
    implementado: conteúdo editorial livre num Edital é conteúdo normativo, e a Constituição exige
    que ele tenha fonte autoritativa única, validação, vigência e presença no documento publicado.
    Nada disso existe, e inventá-lo por baixo de um campo já aceito seria decidir por omissão.

    Campo desconhecido é recusado em vez de ignorado. Ignorar é o que fazia o problema passar
    despercebido: quem enviava `editorialContent` recebia 200 e acreditava que o conteúdo estava
    guardado.
    """

    profiles = ProfileSerializer(many=True, allow_empty=False)
    schedule = EventSerializer(many=True)

    def validate(self, attrs):
        desconhecidos = sorted(set(self.initial_data) - set(self.fields))
        if desconhecidos:
            raise serializers.ValidationError(
                "Campos não reconhecidos no rascunho do Edital: "
                + ", ".join(desconhecidos)
                + ". Aceitar e descartar em silêncio faria parecer que o conteúdo foi guardado."
            )
        return attrs
