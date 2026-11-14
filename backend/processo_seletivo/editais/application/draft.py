import uuid

from django.db import transaction

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.avaliacoes.domain.formas import Forma
from processo_seletivo.editais.domain import alcance, cadastro_de_reserva
from processo_seletivo.editais.domain import secoes as secoes_do_catalogo
from processo_seletivo.editais.domain.cronograma import ScheduleValidationError, validate_schedule
from processo_seletivo.editais.domain.documentos import (
    DocumentRequirementValidationError,
    validate_document_requirements,
)
from processo_seletivo.editais.domain.etapas import StageValidationError, validate_stages
from processo_seletivo.editais.domain.perfis import (
    ProfileValidationError,
    derivar_linha_geral,
    validate_common_draw_method,
    validate_profiles,
)
from processo_seletivo.editais.models.cronograma import Cronograma, EventoCronograma
from processo_seletivo.editais.models.documentos import DocumentoExigido
from processo_seletivo.editais.models.etapas import CriterioAvaliacao, EtapaAvaliacao
from processo_seletivo.editais.models.perfis import (
    CriterioDesempate,
    FatoDeclarado,
    LinhaDoQuadroDeVagas,
    MarcoClassificatorio,
    ModalidadeConcorrencia,
    PerfilVaga,
    RegraNormativa,
)
from processo_seletivo.editais.models.secoes import SecaoEdital
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import Edital
from processo_seletivo.resultados.domain import deliberacao, efeito
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.concurrency import compare_and_swap
from processo_seletivo.verificacao.domain import admissao as admissao_do_video


def _identidades_aninhadas_alheias(profiles):
    """Modalidade contra o Perfil, Regra Normativa contra a Modalidade (FR-029).

    **Cada entidade é verificada no nível do seu contêiner, e nenhuma um nível acima.** A Regra
    pertence à Modalidade, e não ao Perfil (`editais/models/perfis.py:63-66`): conferir só até o
    Perfil deixaria duas Modalidades irmãs trocarem a identidade das suas Regras sem que nada
    acusasse, e a identidade estável passaria a designar outra relação normativa.

    O marco segue a mesma regra contra o Perfil, e o critério contra o marco: dois marcos irmãos
    trocarem critérios seria trocar a norma de lugar sem que nada acusasse (015, FR-002).
    """
    modalidades, regras, marcos, criterios, fatos = {}, {}, {}, {}, {}
    linhas = {}
    for perfil in profiles:
        for modalidade in perfil.get("competitionModalities", []):
            if modalidade.get("id"):
                modalidades[str(modalidade["id"])] = str(perfil["id"])
            regra = modalidade.get("normativeRule") or {}
            if regra.get("id"):
                regras[str(regra["id"])] = str(modalidade.get("id") or "")
        for fato in perfil.get("declaredFacts", []):
            if fato.get("id"):
                fatos[str(fato["id"])] = str(perfil["id"])
        # A linha do quadro, contra o Perfil. Sem esta conferência, um `id` de linha pertencente a
        # outro Edital seria aceito na gravação, e o 409 que o contrato promete não aconteceria
        # para esta coleção — defeito silencioso (025, R-008).
        for linha in perfil.get("vacancyTable", []):
            if linha.get("id"):
                linhas[str(linha["id"])] = str(perfil["id"])
        for marco in perfil.get("classificationMilestones", []):
            if marco.get("id"):
                marcos[str(marco["id"])] = str(perfil["id"])
            for criterio in marco.get("tiebreakers", []):
                if criterio.get("id"):
                    criterios[str(criterio["id"])] = str(marco.get("id") or "")

    alheios = set()
    for identificador, contêiner in ModalidadeConcorrencia.objects.filter(
        id__in=list(modalidades)
    ).values_list("id", "perfil_id"):
        if str(contêiner) != modalidades[str(identificador)]:
            alheios.add(str(identificador))
    for identificador, contêiner in RegraNormativa.objects.filter(id__in=list(regras)).values_list(
        "id", "modalidade_id"
    ):
        if str(contêiner) != regras[str(identificador)]:
            alheios.add(str(identificador))
    for identificador, contêiner in MarcoClassificatorio.objects.filter(
        id__in=list(marcos)
    ).values_list("id", "perfil_id"):
        if str(contêiner) != marcos[str(identificador)]:
            alheios.add(str(identificador))
    for identificador, contêiner in CriterioDesempate.objects.filter(
        id__in=list(criterios)
    ).values_list("id", "marco_id"):
        if str(contêiner) != criterios[str(identificador)]:
            alheios.add(str(identificador))
    for identificador, contêiner in FatoDeclarado.objects.filter(id__in=list(fatos)).values_list(
        "id", "perfil_id"
    ):
        if str(contêiner) != fatos[str(identificador)]:
            alheios.add(str(identificador))
    for identificador, contêiner in LinhaDoQuadroDeVagas.objects.filter(
        id__in=list(linhas)
    ).values_list("id", "perfil_id"):
        if str(contêiner) != linhas[str(identificador)]:
            alheios.add(str(identificador))
    return alheios


def _criterios_de_avaliacao_alheios(stages):
    """O critério do barema, contra a **sua** Etapa (146, FR-5213).

    Mesma régua do critério de desempate contra o marco: duas Etapas trocarem critérios, ou um
    critério de outro Edital ser reparentado aqui, faria a identidade estável — que a Retificação
    endereça — passar a designar outra linha de outra ficha.
    """
    criterios = {
        str(criterio["id"]): str(stage.get("id") or "")
        for stage in stages
        for criterio in stage.get("criteria") or []
        if isinstance(criterio, dict) and criterio.get("id")
    }
    return {
        str(identificador)
        for identificador, etapa in CriterioAvaliacao.objects.filter(
            id__in=list(criterios)
        ).values_list("id", "etapa_id")
        if str(etapa) != criterios[str(identificador)]
    }


def _reject_identifiers_of_other_editais(edital, profiles, schedule, stages):
    """FR-017: Perfil, Evento ou Etapa já vinculado a outro Edital é inconsistência determinável.

    `replace_draft` apaga e recria: sem esta recusa, uma entidade poderia ser reparentada de um
    Edital para outro e a identidade estável passaria a designar outra coisa. Cada uma é verificada
    contra o **seu** contêiner.
    """
    alheios = sorted(
        str(identifier)
        for identifier in (
            set(
                PerfilVaga.objects.filter(id__in=[item["id"] for item in profiles])
                .exclude(edital=edital)
                .values_list("id", flat=True)
            )
            | set(
                EventoCronograma.objects.filter(id__in=[item["id"] for item in schedule])
                .exclude(cronograma__edital=edital)
                .values_list("id", flat=True)
            )
            | set(
                EtapaAvaliacao.objects.filter(id__in=[item["id"] for item in stages])
                .exclude(edital=edital)
                .values_list("id", flat=True)
            )
            | _identidades_aninhadas_alheias(profiles)
            | _criterios_de_avaliacao_alheios(stages)
        )
    )
    if alheios:
        raise DomainError(
            "identifier_belongs_to_another_edital",
            "Identificadores já vinculados a outro contêiner: " + ", ".join(alheios),
            409,
        )


def _validar_secoes(sections):
    """Só seção textual do catálogo é gravável (FR-034 e FR-036).

    Chave fora do catálogo tentaria acrescentar seção onde o conjunto é fixo; chave de seção
    gerada tentaria persistir como texto o que é derivado do dado estruturado, criando dois
    endereços para o mesmo conteúdo normativo.
    """
    invalidas = sorted(
        item["key"] for item in sections if not secoes_do_catalogo.e_textual(item["key"])
    )
    if invalidas:
        raise DomainError(
            "field_constraint_violated",
            "Não são seções textuais do catálogo do Edital: " + ", ".join(invalidas),
            422,
        )


def _sem_zeros_no_concurso(metodo):
    """`006114` gravado como `6114`, e nada além disso, na fonte que tem forma (116, D-001).

    `OcorrenciaDaFonte` é única por `(fonte, referência)` em texto: as duas grafias gravariam duas
    linhas para a mesma extração. O que não tem a forma volta como veio, para a recusa de
    `perfis._validar_forma_da_ocorrencia` dizer o valor que a pessoa escreveu.
    """
    from processo_seletivo.sorteios.domain import conferencia
    from processo_seletivo.sorteios.infrastructure import fontes

    if not isinstance(metodo, dict) or "occurrence" not in metodo:
        return metodo
    if fontes.forma_da_referencia(metodo.get("source")) is None:
        return metodo
    return {**metodo, "occurrence": conferencia.normalizar(metodo["occurrence"])}


def _sem_zeros_no_concurso_dos_marcos(perfil):
    if not isinstance(perfil, dict) or not isinstance(perfil.get("classificationMilestones"), list):
        return perfil
    return {
        **perfil,
        "classificationMilestones": [
            {**marco, "drawMethod": _sem_zeros_no_concurso(marco["drawMethod"])}
            if isinstance(marco, dict) and isinstance(marco.get("drawMethod"), dict)
            else marco
            for marco in perfil["classificationMilestones"]
        ],
    }


def replace_draft(
    *,
    actor,
    edital_id,
    expected_revision,
    profiles,
    schedule,
    correlation_id,
    stages=None,
    sections=None,
    document_requirements=None,
    draw_method=None,
    area="",
):
    require_permission(actor, "edital:elaborar")
    stages = list(stages or [])
    sections = list(sections or [])
    document_requirements = list(document_requirements or [])
    _validar_secoes(sections)
    # **A linha geral é materializada aqui, e não na tela nem no serializer** (027, D-001, FR-316).
    # No command porque é o ponto por onde passam os dois canais: a interface administrativa invoca
    # `replace_draft` direto, e a API chega ao mesmo lugar. Escrevê-la no formulário deixaria de
    # fora quem grava rascunho por `PUT /draft`, e a FR-316 fala do sistema, não da tela.
    #
    # **Antes de validar**, para que a conferência enxergue o conteúdo que será gravado: a linha
    # derivada passa pela mesma forma que qualquer outra, e não por uma porta lateral.
    #
    # **E antes de persistir**, porque `replace_draft` apaga e recria o rascunho inteiro: é daqui
    # que sai o `id` que a linha leva para o banco, e é a preservação dele que mantém a linha
    # alcançável pela Retificação depois de publicada (`research.md`, T-001).
    profiles = [
        derivar_linha_geral(payload) if isinstance(payload, dict) else payload
        for payload in profiles
    ]
    # **Os zeros à esquerda saem aqui, pela mesma razão da linha geral** (116, FR-3623): é o ponto
    # por onde passam a tela e o `PUT /draft`, e antes de validar.
    profiles = [_sem_zeros_no_concurso_dos_marcos(payload) for payload in profiles]
    draw_method = _sem_zeros_no_concurso(draw_method)
    try:
        validate_profiles(profiles)
    except ProfileValidationError as exc:
        # `campo` e `identidade` seguem junto: sem eles a interface não teria como ancorar a
        # recusa no controle que a causou, e o resumo voltaria a ser texto solto (FR-033).
        raise DomainError(
            "invalid_profiles", str(exc), 422, campo=exc.campo, identidade=exc.identidade
        ) from exc
    if draw_method:
        try:
            # O rascunho admite o método comum que espera a extração (116, FR-3716).
            validate_common_draw_method(draw_method, exigir_a_extracao=False)
        except ProfileValidationError as exc:
            raise DomainError(
                "invalid_draw_method", str(exc), 422, campo=exc.campo, identidade=exc.identidade
            ) from exc
    try:
        validate_schedule(schedule)
    except ScheduleValidationError as exc:
        # `campo` e `identidade` seguem junto: sem eles a interface não teria como ancorar a
        # recusa no controle que a causou, e o resumo voltaria a ser texto solto (FR-033).
        raise DomainError(
            "invalid_schedule", str(exc), 422, campo=exc.campo, identidade=exc.identidade
        ) from exc
    try:
        # Contra o Cronograma **desta gravação**, e não contra o banco: `replace_draft` substitui o
        # rascunho inteiro, então um Evento removido no mesmo POST já não existe.
        validate_stages(stages, schedule=schedule, document_requirements=document_requirements)
    except StageValidationError as exc:
        # `campo` e `identidade` seguem junto: sem eles a interface não teria como ancorar a
        # recusa no controle que a causou, e o resumo voltaria a ser texto solto (FR-033).
        raise DomainError(
            "invalid_stages", str(exc), 422, campo=exc.campo, identidade=exc.identidade
        ) from exc
    try:
        # Contra os Perfis desta gravação, pela mesma razão das Etapas: um Perfil removido no
        # mesmo envio já não existe, e conferir contra o banco recusaria o que a pessoa fez.
        validate_document_requirements(document_requirements, profiles=profiles)
    except DocumentRequirementValidationError as exc:
        raise DomainError(
            "invalid_document_requirements",
            str(exc),
            422,
            campo=exc.campo,
            identidade=exc.identidade,
        ) from exc
    with command_context() as now:
        try:
            edital = (
                Edital.objects.select_for_update()
                .select_related("processo")
                .get(pk=edital_id, institution_scope=actor.institution_scope)
            )
        except Edital.DoesNotExist as exc:
            raise DomainError("not_found", "Recurso não encontrado.", 404) from exc
        ensure_processo_accepts_changes(edital.processo)
        if edital.status != Edital.Status.EM_ELABORACAO:
            raise DomainError(
                "invalid_state", "Somente Edital em elaboração pode ser editado.", 409
            )
        if edital.revision != expected_revision:
            raise DomainError("stale_revision", "A revisão informada está obsoleta.", 412)
        _reject_identifiers_of_other_editais(edital, profiles, schedule, stages)
        # As linhas do quadro saem **antes**, e não é detalhe de ordenação: `modalidade` é
        # `PROTECT` — a D-008 escrita no banco —, e a `ModalidadeConcorrencia` que a cascata do
        # Perfil apagaria em seguida ainda está referenciada por elas. Sem esta linha, `delete()`
        # levanta `ProtectedError` e **nenhuma** gravação de rascunho passa.
        #
        # Contorná-lo aqui não desfaz a proteção, porque quem a exerce já falou: `validate_profiles`
        # rodou lá em cima e recusa a linha que aponte Modalidade que este envio não declara. Uma
        # gravação que remova a Modalidade e deixe a linha para trás não chega até aqui — e é
        # exatamente isso que a D-008 pede, com a mensagem que separa os dois casos.
        LinhaDoQuadroDeVagas.objects.filter(perfil__edital=edital).delete()
        # **O número digitado antes da `162` sobrevive à regravação** (FR-6940). A gravação não
        # aceita mais número no limitado — ele vem do corte —, mas o rascunho salvo antes guarda o
        # dele, e é ele que a Revisão mostra ao lado do derivado. Regravar o Perfil por outra etapa
        # o apagaria em silêncio, e a advertência sumiria antes de quem elabora a ler. Ele fica só
        # enquanto o Perfil continuar limitado; a publicação nunca o leva (`edital_snapshot`).
        digitados = dict(
            PerfilVaga.objects.filter(
                edital=edital, reserve_type="LIMITED", reserve_limit__isnull=False
            ).values_list("id", "reserve_limit")
        )
        PerfilVaga.objects.filter(edital=edital).delete()
        for payload in profiles:
            perfil = PerfilVaga.objects.create(
                id=payload["id"],
                edital=edital,
                code=payload["code"],
                name=payload["name"],
                description=payload.get("description", ""),
                requirements=payload.get("requirements", []),
                immediate_vacancies=payload["immediateVacancies"],
                reserve_type=payload["reserveType"],
                reserve_limit=(
                    digitados.get(_uuid_ou_nada(payload["id"]))
                    if payload["reserveType"] == "LIMITED"
                    else payload.get("reserveLimit")
                ),
                modalidade_ampla_concorrencia=(payload.get("generalCompetitionModalityId") or None),
                # **Vazio, e não `None`**: a coluna é `CharField` com `default=""`, e escrever nulo
                # viola o `NOT NULL`. É a mesma grafia de ausência que o resto do modelo usa.
                especie_de_reversao=((payload.get("vacancyReversion") or {}).get("kind") or ""),
                # Campo solto no conteúdo publicado, e por isso lido direto (019, R-007). Vazio
                # quando ausente, pela mesma razão da linha acima.
                forma_de_convocacao=(payload.get("callForm") or ""),
                locality=payload.get("locality", ""),
                duties=payload.get("duties", ""),
                workload=payload.get("workload", ""),
                compensation=payload.get("compensation", ""),
                classification_information=payload.get("classificationInformation", {}),
                call_information=payload.get("callInformation", {}),
            )
            for modality_payload in payload.get("competitionModalities", []):
                # Com o `id` recebido, como Perfil e Evento já eram criados. Sem isto, toda
                # gravação do rascunho trocava a identidade das modalidades — e a da Regra, que
                # viaja no conteúdo publicado.
                modality = ModalidadeConcorrencia.objects.create(
                    id=modality_payload["id"],
                    perfil=perfil,
                    code=modality_payload["code"],
                    name=modality_payload["name"],
                    description=modality_payload.get("description", ""),
                )
                rule = modality_payload.get("normativeRule")
                if rule:
                    RegraNormativa.objects.create(
                        id=rule["id"],
                        modalidade=modality,
                        foundation=rule["foundation"],
                        version=rule["version"],
                        percentage=rule.get("percentage"),
                        calculation=rule.get("calculation", {}),
                        rounding=rule.get("rounding", {}),
                        distribution=rule.get("distribution", {}),
                        call_rules=rule.get("callRules", {}),
                        effective_from=rule.get("effectiveFrom"),
                    )
            for fato_payload in payload.get("declaredFacts", []):
                # Com o `id` recebido, como tudo o mais: é por ele que a Retificação alcança o fato
                # e que o valor congelado na inscrição diz de qual fato ele é.
                FatoDeclarado.objects.create(
                    id=fato_payload["id"],
                    perfil=perfil,
                    code=fato_payload["code"],
                    label=fato_payload["label"],
                    tipo=fato_payload["type"],
                )
            for ordem, linha_payload in enumerate(payload.get("vacancyTable", [])):
                # Depois das Modalidades, porque a linha reservada aponta uma delas. Com o `id`
                # recebido, como tudo o mais: é por ele que a Retificação alcança a linha depois de
                # publicada, e trocar a identidade a cada gravação a tornaria inalcançável.
                #
                # `ordem` nasce da posição no envio — determinismo da emissão, e não norma: a
                # D-009 recusa publicar a ordem, porque o quadro não afirma precedência entre
                # listas. Sem ela, dois snapshots do mesmo conteúdo teriam resumos diferentes.
                LinhaDoQuadroDeVagas.objects.create(
                    id=linha_payload["id"],
                    perfil=perfil,
                    modalidade_id=linha_payload.get("modalityId") or None,
                    vagas_imediatas=linha_payload["immediateVacancies"],
                    ordem=ordem,
                )
            for marco_payload in payload.get("classificationMilestones", []):
                # Com o `id` recebido, pela mesma razão da Modalidade: sem isto, cada gravação do
                # rascunho trocaria a identidade do marco — e é por ela que a Retificação o alcança
                # e que o ato de ordenação declara qual marco realizou.
                marco = MarcoClassificatorio.objects.create(
                    id=marco_payload["id"],
                    perfil=perfil,
                    code=marco_payload["code"],
                    name=marco_payload["name"],
                    # `""` quando o marco não declara a forma da ordem (030, FR-413). A ausência
                    # é o estado de todo marco composto antes desta feature, e não uma omissão a
                    # corrigir depois: é dela que os leitores derivam o comportamento de sempre.
                    forma_da_ordem=marco_payload.get("orderProduction") or "",
                    etapas=[str(etapa) for etapa in marco_payload.get("stages", [])],
                    operacao=marco_payload["operation"],
                    normalizacao=marco_payload["normalization"],
                    arredondamento=marco_payload.get("rounding", {}),
                    # `{}` quando o marco não declara janela — a ausência é a afirmação, e não uma
                    # omissão a corrigir depois (018, FR-020, FR-028).
                    janela_recursal=marco_payload.get("appealWindow") or {},
                    metodo_de_sorteio=marco_payload.get("drawMethod") or {},
                    # `{}` quando o marco não corta, pela mesma razão dos dois acima (014, FR-178).
                    regra_de_corte=marco_payload.get("cutRule") or {},
                )
                for criterio_payload in marco_payload.get("tiebreakers", []):
                    CriterioDesempate.objects.create(
                        id=criterio_payload["id"],
                        marco=marco,
                        ordem=criterio_payload["order"],
                        tipo=criterio_payload["type"],
                        parametros=criterio_payload.get("parameters", {}),
                        quando_ausente=criterio_payload["whenMissing"],
                    )
        cronograma, _ = Cronograma.objects.get_or_create(edital=edital)
        EventoCronograma.objects.filter(cronograma=cronograma).delete()
        EventoCronograma.objects.bulk_create(
            [
                EventoCronograma(
                    id=event["id"],
                    cronograma=cronograma,
                    type=event["type"],
                    description=event["description"],
                    start_at=event["startAt"],
                    end_at=event.get("endAt"),
                    order=event.get("order", 0),
                    status=event.get("status", EventoCronograma.Status.PLANEJADO),
                    is_registration_period=event.get("isRegistrationPeriod", False),
                    location=(event.get("location") or "").strip(),
                    # Ausente é exibido (144, FR-5104): o payload anterior à coluna, o
                    # reaproveitamento de conteúdo publicado antes do degrau 20 e o cliente da API
                    # que não conhece o campo não ocultam nada sem ter pedido.
                    shown_in_pdf=event.get("shownInPdf", True) is not False,
                )
                for event in schedule
            ]
        )
        # As Etapas são recriadas depois dos Eventos porque referenciam Evento desta gravação.
        EtapaAvaliacao.objects.filter(edital=edital).delete()
        EtapaAvaliacao.objects.bulk_create(
            [
                EtapaAvaliacao(
                    id=stage["id"],
                    edital=edital,
                    name=stage["name"],
                    order=stage.get("order", 0),
                    weight=stage.get("weight"),
                    eliminatory=stage.get("eliminatory", False),
                    classificatory=stage.get("classificatory", False),
                    minimum_score=stage.get("minimumScore"),
                    evaluations_per_registration=stage.get("evaluationsPerRegistration"),
                    maximum_score=stage.get("maximumScore"),
                    # `stage.get("forma")` **não** serve aqui: a chave ausente devolveria `None` e
                    # gravaria nulo numa coluna que não o admite, contornando o default do modelo.
                    # A omissão vale `PONTUADA`, e é o único lugar do rascunho em que a ausência de
                    # um campo normativo tem valor escrito em vez de `None` (012, FR-120).
                    forma=stage.get("forma") or Forma.PONTUADA,
                    rotulo_favoravel=stage.get("rotuloFavoravel") or "",
                    rotulo_desfavoravel=stage.get("rotuloDesfavoravel") or "",
                    evento_id=stage.get("scheduleEventId"),
                    # O alcance (163, FR-6960). Chave ausente é "todas as inscrições", e não
                    # apagamento: é a leitura de quem integrava antes do campo existir (D-002).
                    alcance=alcance.normalizar(stage.get("modalityCodes")),
                    # O efeito do desfecho (164, FR-7000, FR-7004), na grafia publicada; chave
                    # ausente é "não declarado", que a publicação lê pelo padrão (FR-7001).
                    efeito_desfavoravel=efeito.para_coluna(stage.get("unfavorableOutcomeEffect")),
                    efeito_da_ausencia=efeito.para_coluna(stage.get("absenceEffect")),
                    # A regra de deliberação (165, FR-7050), na grafia publicada; chave ausente é
                    # "não declarada", sem padrão (D-002).
                    regra_de_deliberacao=deliberacao.para_coluna(stage.get("deliberationRule")),
                    # A admissão do vídeo (166, FR-7102): só `true` admite.
                    admite_video=admissao_do_video.ler(stage.get("videoOption")),
                )
                for stage in stages
            ]
        )
        # O barema, depois das Etapas, porque o critério é delas (146, FR-5213). A `CASCADE` acima
        # já levou os critérios gravados junto com as Etapas, e eles renascem com o `id` recebido:
        # é por ele que a Retificação alcança cada linha da ficha depois de publicada. A ordem vem
        # da posição no envio — o conteúdo publicado não tem campo de ordem, e a lista é a ordem.
        #
        # **Etapa sem a chave é Etapa sem critério**, que é o que a FR-5213 pede. Quem grava outra
        # etapa do assistente reenvia o barema por `etapas_persistidas` — sem isso, gravar os Perfis
        # apagaria a ficha, que é o risco 2 do plano.
        CriterioAvaliacao.objects.bulk_create(
            [
                CriterioAvaliacao(
                    id=criterio["id"],
                    etapa_id=stage["id"],
                    ordem=ordem,
                    nome=(criterio.get("name") or "").strip(),
                    descricao=(criterio.get("description") or "").strip(),
                    maxima=criterio["maximumScore"],
                    pontos_por_unidade=criterio.get("pointsPerUnit"),
                    unidade=(criterio.get("unitLabel") or "").strip()
                    if criterio.get("pointsPerUnit") is not None
                    else "",
                    documento=criterio.get("documentRequirementId") or None,
                )
                for stage in stages
                for ordem, criterio in enumerate(stage.get("criteria") or [], 1)
            ]
        )
        # A identidade da linha é a mesma do snapshot: uma identidade só para a seção, e não uma
        # para o conteúdo publicado e outra para a persistência.
        SecaoEdital.objects.filter(edital=edital).delete()
        SecaoEdital.objects.bulk_create(
            [
                SecaoEdital(
                    id=secoes_do_catalogo.identidade(edital.id, section["key"]),
                    edital=edital,
                    key=section["key"],
                    content=section["content"],
                )
                for section in sections
            ]
        )
        # Depois dos Perfis e das Modalidades, porque a aplicabilidade os referencia — mesma razão
        # que já ordenava as Etapas depois dos Eventos.
        DocumentoExigido.objects.filter(edital=edital).delete()
        DocumentoExigido.objects.bulk_create(
            [
                DocumentoExigido(
                    id=requirement["id"],
                    edital=edital,
                    key=requirement["key"],
                    name=requirement["name"],
                    instructions=requirement.get("instructions", ""),
                    required=requirement.get("required", True),
                    order=requirement.get("order", 0),
                    perfil_id=requirement.get("profileId"),
                    modalidade_id=requirement.get("modalityId"),
                    # O recorte transversal (044). Pela mesma razão do Anexo abaixo, ele precisa
                    # viajar em toda gravação: as linhas são recriadas a cada etapa.
                    modalidade_codigo=requirement.get("modalityCode") or "",
                    # O modelo que o Edital fornece (020, FR-020). Estar aqui não é detalhe: as
                    # linhas são apagadas e recriadas a cada gravação de etapa, e um campo que não
                    # viaje no payload volta nulo — o vínculo morreria em silêncio, sem erro e sem
                    # que ninguém tocasse na tela de documentos.
                    anexo_id=requirement.get("attachmentId"),
                    # O momento e o aproveitamento (115), pela mesma razão: viajam em toda gravação.
                    momento=requirement.get("moment") or "AT_ENROLLMENT",
                    aproveita=requirement.get("reusesRequirementId"),
                    # A condição de exigência (131), pela mesma razão: viaja em toda gravação.
                    condicao=(requirement.get("requiredWhen") or "").strip(),
                )
                for requirement in document_requirements
            ]
        )
        # O método do sorteio comum ao Edital (030, FR-429). **`None` significa "não veio neste
        # envio", e `{}` significa "não declarado"** — e a diferença é a que impede a travessia:
        # `replace_draft` apaga e recria tudo o que recebe, e as demais etapas do assistente não
        # desenham este campo. Se a ausência valesse por vazio, declarar o método na Classificação
        # e visitar o Cronograma o apagaria em silêncio, que é a classe de perda que este comando
        # já nomeia quatro vezes.
        atualizacao = {"last_edited_by": actor.subject}
        if draw_method is not None:
            atualizacao["metodo_de_sorteio_comum"] = draw_method or {}
        compare_and_swap(
            Edital.objects,
            pk=edital.pk,
            expected_revision=expected_revision,
            **atualizacao,
        )
        edital.refresh_from_db()
        record_event(
            actor=actor,
            permission="edital:elaborar",
            operation="ALTERAR_RASCUNHO",
            aggregate=edital,
            now=now,
            correlation_id=correlation_id,
            previous_state=edital.status,
            previous_revision=expected_revision,
            # Qual área do Edital mudou (FR-042). Sem isto, quatro gravações em etapas diferentes
            # produziam quatro registros idênticos — "Alteração do rascunho · Em elaboração → Em
            # elaboração" — e a trilha, que existe para responder questionamento, não respondia
            # nenhum. O sistema conhecia a etapa e descartava a informação.
            #
            # **A área, e não a diferença** (FR-043): nada de diff, versionamento de rascunho ou
            # histórico editorial. `reason` é o campo que a trilha já exibe, e não custa migration.
            reason=area,
        )
        transaction.on_commit(lambda: None)
        return edital


def _uuid_ou_nada(valor):
    try:
        return uuid.UUID(str(valor))
    except (TypeError, ValueError):
        return None


NUMERO_DIGITADO = "reserve_limit_typed_in_draft"


def advertencias_do_numero_digitado(edital, snapshot):
    """O rascunho salvo antes da `162` que ainda guarda o número digitado (FR-6940).

    **Lido das linhas, e não do conteúdo.** O conteúdo composto já não leva o número —
    `edital_snapshot` o publica `null` —, e é por isso que quem elabora precisa ouvir a troca antes
    de publicar: o Edital vai dizer o número do corte, e não o que foi digitado. Quando os dois
    coincidem, não há troca a avisar.
    """
    from processo_seletivo.editais.domain.validation import Severity, ValidationFinding

    perfis = {str(p.get("id")): p for p in snapshot.get("profiles") or [] if isinstance(p, dict)}
    achados = []
    for linha in edital.perfis.filter(reserve_type="LIMITED", reserve_limit__isnull=False):
        perfil = perfis.get(str(linha.id))
        if perfil is None:
            continue
        cadastro = cadastro_de_reserva.do_perfil(perfil)
        if cadastro.numero_unico == linha.reserve_limit:
            continue
        rotulo = perfil.get("code") or perfil.get("name") or ""
        marco = cadastro.marco_que_convoca
        nome = cadastro_de_reserva.nome_do_marco(marco)
        if cadastro.por_lista:
            publicado = f"{cadastro.descricao_curta().removeprefix('Limitado: ')}"
            depois = (
                f"O Edital vai publicar {publicado}, que é o que o corte d{nome} alcança além "
                "das vagas."
            )
        else:
            depois = (
                "O Edital vai publicar o número que o corte do marco que convoca alcançar além "
                "das vagas, e esse corte ainda não foi declarado."
            )
        achados.append(
            ValidationFinding(
                Severity.WARNING,
                NUMERO_DIGITADO,
                f"O Perfil '{rotulo}' guardava o cadastro de reserva limitado em "
                f"{linha.reserve_limit}, digitado antes de o número passar a vir do corte. "
                f"{depois}",
                f"/profiles/id={linha.id}/reserveType",
            )
        )
    return achados
