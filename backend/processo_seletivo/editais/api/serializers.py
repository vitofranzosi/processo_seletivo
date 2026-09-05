from decimal import Decimal

from rest_framework import serializers

from processo_seletivo.avaliacoes.domain.formas import Forma
from processo_seletivo.editais.domain.cronograma import ScheduleValidationError, validate_event
from processo_seletivo.editais.domain.perfis import ProfileValidationError, validate_profile


class NormativeRuleSerializer(serializers.Serializer):
    """`id` é **obrigatório**, como já é o de Perfil, Evento e Etapa.

    Opcional, ele reabriria pela API o defeito que esta feature veio fechar: um payload sem
    identificador é aceito, o servidor gera um, a resposta do rascunho devolve só o resumo do
    Edital — e a gravação seguinte, também sem identificador, troca a identidade de novo. O cliente
    não teria como preservar o que nunca recebeu.

    Quem cria a regra escolhe o identificador dela, e a recusa de identificador pertencente a
    outro contêiner é o que impede que essa escolha reparente conteúdo alheio.
    """

    id = serializers.UUIDField()
    foundation = serializers.CharField(min_length=1)
    version = serializers.CharField(min_length=1, max_length=50)
    percentage = serializers.DecimalField(max_digits=7, decimal_places=4, required=False)
    calculation = serializers.JSONField(required=False)
    rounding = serializers.JSONField(required=False)
    distribution = serializers.JSONField(required=False)
    callRules = serializers.JSONField(required=False)
    effectiveFrom = serializers.DateTimeField(required=False)


class CompetitionModalitySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    code = serializers.CharField(min_length=1, max_length=100)
    name = serializers.CharField(min_length=1, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    normativeRule = NormativeRuleSerializer(required=False)


class DeclaredFactSerializer(serializers.Serializer):
    """Um fato que o Edital exige do candidato (D-2).

    `type` é escolha entre os dois que os Editais lidos de fato usam — idade sai de data de
    nascimento, tempo de experiência sai de meses. Terceiro tipo entra quando aparecer o Edital que
    o exija, e não antes: cada tipo novo é uma forma nova de congelar e de comparar.
    """

    id = serializers.UUIDField()
    code = serializers.CharField(min_length=1, max_length=100)
    label = serializers.CharField(min_length=1, max_length=255)
    type = serializers.ChoiceField(choices=["DATA", "INTEIRO"])


class TiebreakerSerializer(serializers.Serializer):
    """Um critério de desempate. `order` e `whenMissing` são exigidos, e não têm padrão.

    `order` porque a ordem **é** a norma, e inferi-la da posição no array faria a Retificação
    reordenar substituindo a lista inteira, perdendo as identidades que ela mesma endereça.
    `whenMissing` porque valor ausente é declarado, nunca inferido (015, FR-015, FR-018).
    """

    id = serializers.UUIDField()
    order = serializers.IntegerField(min_value=1)
    type = serializers.ChoiceField(
        choices=["MAIOR_PONTUACAO_NA_ETAPA", "MAIOR_VALOR_DE_FATO", "MENOR_VALOR_DE_FATO"]
    )
    parameters = serializers.JSONField(required=False)
    whenMissing = serializers.ChoiceField(
        choices=["ULTIMO_NO_CRITERIO", "CRITERIO_NAO_SE_APLICA"]
    )


class ClassificationMilestoneSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    code = serializers.CharField(min_length=1, max_length=100)
    name = serializers.CharField(min_length=1, max_length=255)
    stages = serializers.ListField(child=serializers.UUIDField(), required=False)
    operation = serializers.ChoiceField(choices=["SOMA_PONDERADA", "MEDIA_PONDERADA"])
    normalization = serializers.ChoiceField(choices=["NENHUMA", "PELA_SOMA_DOS_PESOS"])
    rounding = serializers.JSONField(required=False)
    tiebreakers = TiebreakerSerializer(many=True, required=False)


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
    # Opcionais com padrão `""` (FR-012, FR-014): a ausência é legítima no rascunho.
    duties = serializers.CharField(required=False, allow_blank=True)
    workload = serializers.CharField(required=False, allow_blank=True)
    compensation = serializers.CharField(required=False, allow_blank=True)
    classificationInformation = serializers.JSONField(required=False)
    callInformation = serializers.JSONField(required=False)
    competitionModalities = CompetitionModalitySerializer(many=True)
    # Opcional no rascunho: um Edital que não classifica não declara marco nenhum.
    classificationMilestones = ClassificationMilestoneSerializer(many=True, required=False)
    # Opcional pelo mesmo motivo: um Edital que não declara fato nenhum continua sem campo nenhum.
    declaredFacts = DeclaredFactSerializer(many=True, required=False)

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
    # Ausente significa "não é o período de inscrições", que é a verdade para quase todo Evento.
    isRegistrationPeriod = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        try:
            validate_event(attrs)
        except ScheduleValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return attrs


class StageSerializer(serializers.Serializer):
    """Etapa de Avaliação no rascunho.

    A coerência — Evento existente no Cronograma da mesma gravação, faixa de peso e de nota
    mínima — é verificada no domínio, e não aqui: a interface administrativa invoca o command
    diretamente e não atravessa este serializer.
    """

    id = serializers.UUIDField()
    name = serializers.CharField(min_length=1, max_length=200)
    order = serializers.IntegerField(min_value=0, required=False, default=0)
    weight = serializers.DecimalField(
        max_digits=7, decimal_places=4, required=False, allow_null=True
    )
    eliminatory = serializers.BooleanField(required=False, default=False)
    classificatory = serializers.BooleanField(required=False, default=False)
    minimumScore = serializers.DecimalField(
        max_digits=7, decimal_places=4, required=False, allow_null=True
    )
    # As duas do incremento da `012`. Opcionais e anuláveis: rascunho que não as informa declara
    # ausência, e ausência é uma avaliação por inscrição e limite não declarado (FR-009, FR-066).
    evaluationsPerRegistration = serializers.IntegerField(
        min_value=1, required=False, allow_null=True
    )
    maximumScore = serializers.DecimalField(
        max_digits=7, decimal_places=4, required=False, allow_null=True, min_value=Decimal("0.0001")
    )
    # As três do incremento da revisão da `012` (D-008, FR-119). `forma` é opcional e **não**
    # anulável, e a assimetria entre omitir e enviar `null` é a decisão: quem já integrava com esta
    # API não conhece o campo, e a omissão continua valendo — vale `PONTUADA`, que é o que a
    # ausência significa em todo o resto do sistema (FR-120). `null` explícito é outra coisa: é
    # afirmar que não há forma, e não há Etapa sem forma. Aceitá-lo devolveria ao rascunho o vazio
    # que o modelo deixou de admitir, contornando o default pela porta dos fundos.
    forma = serializers.ChoiceField(choices=Forma.choices, required=False, allow_null=False)
    # Os rótulos são anuláveis, porque neles o "não se aplica" é real. `null` e ausência chegam ao
    # rascunho como string vazia, que é como a coluna grava "não publicado".
    rotuloFavoravel = serializers.CharField(
        max_length=100, required=False, allow_null=True, allow_blank=True
    )
    rotuloDesfavoravel = serializers.CharField(
        max_length=100, required=False, allow_null=True, allow_blank=True
    )
    scheduleEventId = serializers.UUIDField(required=False, allow_null=True)


class SectionSerializer(serializers.Serializer):
    """Só as seções **textuais** que tiveram o conteúdo editado.

    A entrada não carrega o UUID: ele é determinístico sobre `(editalId, key)` e o snapshot o
    deriva. Enviar um identificador aqui abriria a porta para declarar um que não corresponde à
    chave, e não haveria como dizer qual dos dois vale.

    Seção gerada não é enviada, e seção textual ausente significa "conteúdo padrão do catálogo",
    não "seção vazia". A recusa de chave fora do catálogo é do domínio, que o command atravessa.
    """

    key = serializers.CharField(min_length=1, max_length=60)
    content = serializers.CharField(allow_blank=False)


class DocumentRequirementSerializer(serializers.Serializer):
    """O que o Edital exige do candidato.

    `profileId` e `modalityId` ausentes ou nulos significam "não restringe" — é a ausência que
    produz as quatro combinações de aplicabilidade, e por isso os dois são anuláveis em vez de
    obrigatórios com valor especial.
    """

    id = serializers.UUIDField()
    key = serializers.CharField(min_length=1, max_length=100)
    name = serializers.CharField(min_length=1, max_length=255)
    instructions = serializers.CharField(required=False, allow_blank=True, default="")
    required = serializers.BooleanField(required=False, default=True)
    order = serializers.IntegerField(min_value=0, required=False, default=0)
    profileId = serializers.UUIDField(required=False, allow_null=True)
    modalityId = serializers.UUIDField(required=False, allow_null=True)


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
    stages = StageSerializer(many=True, required=False)
    sections = SectionSerializer(many=True, required=False)
    documentRequirements = DocumentRequirementSerializer(many=True, required=False)

    def validate(self, attrs):
        desconhecidos = sorted(set(self.initial_data) - set(self.fields))
        if desconhecidos:
            raise serializers.ValidationError(
                "Campos não reconhecidos no rascunho do Edital: "
                + ", ".join(desconhecidos)
                + ". Aceitar e descartar em silêncio faria parecer que o conteúdo foi guardado."
            )
        return attrs
