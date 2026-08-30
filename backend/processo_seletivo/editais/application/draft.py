from django.db import transaction

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.editais.domain.cronograma import ScheduleValidationError, validate_schedule
from processo_seletivo.editais.domain.etapas import StageValidationError, validate_stages
from processo_seletivo.editais.domain.perfis import ProfileValidationError, validate_profiles
from processo_seletivo.editais.models.cronograma import Cronograma, EventoCronograma
from processo_seletivo.editais.models.etapas import EtapaAvaliacao
from processo_seletivo.editais.models.perfis import (
    ModalidadeConcorrencia,
    PerfilVaga,
    RegraNormativa,
)
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.concurrency import compare_and_swap


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
        )
    )
    if alheios:
        raise DomainError(
            "identifier_belongs_to_another_edital",
            "Identificadores já vinculados a outro Edital: " + ", ".join(alheios),
            409,
        )


def replace_draft(
    *, actor, edital_id, expected_revision, profiles, schedule, correlation_id, stages=None
):
    require_permission(actor, "edital:elaborar")
    stages = list(stages or [])
    try:
        validate_profiles(profiles)
    except ProfileValidationError as exc:
        raise DomainError("invalid_profiles", str(exc), 422) from exc
    try:
        validate_schedule(schedule)
    except ScheduleValidationError as exc:
        raise DomainError("invalid_schedule", str(exc), 422) from exc
    try:
        # Contra o Cronograma **desta gravação**, e não contra o banco: `replace_draft` substitui o
        # rascunho inteiro, então um Evento removido no mesmo POST já não existe.
        validate_stages(stages, schedule=schedule)
    except StageValidationError as exc:
        raise DomainError("invalid_stages", str(exc), 422) from exc
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
                classification_information=payload.get("classificationInformation", {}),
                call_information=payload.get("callInformation", {}),
            )
            for modality_payload in payload.get("competitionModalities", []):
                modality = ModalidadeConcorrencia.objects.create(
                    perfil=perfil,
                    code=modality_payload["code"],
                    name=modality_payload["name"],
                    description=modality_payload.get("description", ""),
                )
                rule = modality_payload.get("normativeRule")
                if rule:
                    RegraNormativa.objects.create(
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
        )
        transaction.on_commit(lambda: None)
        return edital
