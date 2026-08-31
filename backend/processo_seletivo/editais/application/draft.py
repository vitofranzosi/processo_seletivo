from django.db import transaction

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.editais.domain import secoes as secoes_do_catalogo
from processo_seletivo.editais.domain.cronograma import ScheduleValidationError, validate_schedule
from processo_seletivo.editais.domain.documentos import (
    DocumentRequirementValidationError,
    validate_document_requirements,
)
from processo_seletivo.editais.domain.etapas import StageValidationError, validate_stages
from processo_seletivo.editais.domain.perfis import ProfileValidationError, validate_profiles
from processo_seletivo.editais.models.cronograma import Cronograma, EventoCronograma
from processo_seletivo.editais.models.documentos import DocumentoExigido
from processo_seletivo.editais.models.etapas import EtapaAvaliacao
from processo_seletivo.editais.models.perfis import (
    ModalidadeConcorrencia,
    PerfilVaga,
    RegraNormativa,
)
from processo_seletivo.editais.models.secoes import SecaoEdital
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.concurrency import compare_and_swap


def _identidades_aninhadas_alheias(profiles):
    """Modalidade contra o Perfil, Regra Normativa contra a Modalidade (FR-029).

    **Cada entidade é verificada no nível do seu contêiner, e nenhuma um nível acima.** A Regra
    pertence à Modalidade, e não ao Perfil (`editais/models/perfis.py:63-66`): conferir só até o
    Perfil deixaria duas Modalidades irmãs trocarem a identidade das suas Regras sem que nada
    acusasse, e a identidade estável passaria a designar outra relação normativa.
    """
    modalidades, regras = {}, {}
    for perfil in profiles:
        for modalidade in perfil.get("competitionModalities", []):
            if modalidade.get("id"):
                modalidades[str(modalidade["id"])] = str(perfil["id"])
            regra = modalidade.get("normativeRule") or {}
            if regra.get("id"):
                regras[str(regra["id"])] = str(modalidade.get("id") or "")

    alheios = set()
    for identificador, contêiner in ModalidadeConcorrencia.objects.filter(
        id__in=list(modalidades)
    ).values_list("id", "perfil_id"):
        if str(contêiner) != modalidades[str(identificador)]:
            alheios.add(str(identificador))
    for identificador, contêiner in RegraNormativa.objects.filter(
        id__in=list(regras)
    ).values_list("id", "modalidade_id"):
        if str(contêiner) != regras[str(identificador)]:
            alheios.add(str(identificador))
    return alheios


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
    area="",
):
    require_permission(actor, "edital:elaborar")
    stages = list(stages or [])
    sections = list(sections or [])
    document_requirements = list(document_requirements or [])
    _validar_secoes(sections)
    try:
        validate_profiles(profiles)
    except ProfileValidationError as exc:
        # `campo` e `identidade` seguem junto: sem eles a interface não teria como ancorar a
        # recusa no controle que a causou, e o resumo voltaria a ser texto solto (FR-033).
        raise DomainError(
            "invalid_profiles", str(exc), 422, campo=exc.campo, identidade=exc.identidade
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
        validate_stages(stages, schedule=schedule)
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
                reserve_limit=payload.get("reserveLimit"),
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
                    evento_id=stage.get("scheduleEventId"),
                )
                for stage in stages
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
                )
                for requirement in document_requirements
            ]
        )
        compare_and_swap(
            Edital.objects,
            pk=edital.pk,
            expected_revision=expected_revision,
            last_edited_by=actor.subject,
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
