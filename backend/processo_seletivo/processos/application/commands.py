from django.db import IntegrityError

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.processos.models import AtoAdministrativo, Edital, ProcessoSeletivo
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.concurrency import compare_and_swap
from processo_seletivo.shared.idempotency import reserve


def _finish_idempotency(record, result, status):
    record.result_type = result.__class__.__name__
    record.result_id = result.pk
    record.response_status = status
    record.save(update_fields=["result_type", "result_id", "response_status"])


def create_process_with_first_edital(*, actor, data, idempotency_key, correlation_id):
    require_permission(actor, "processo:criar")
    with command_context() as now:
        idem = reserve(actor=actor, operation="processo:criar", key=idempotency_key, payload=data)
        if idem.result_id:
            return ProcessoSeletivo.objects.get(pk=idem.result_id), False
        try:
            processo = ProcessoSeletivo.objects.create(
                institution_scope=actor.institution_scope,
                institutional_code=data["institutionalCode"],
                title=data["title"],
                created_at=now,
                created_by=actor.subject,
                last_changed_at=now,
            )
            first = data["firstEdital"]
            Edital.objects.create(
                processo=processo,
                institution_scope=actor.institution_scope,
                number=first["number"],
                year=first["year"],
                title=first["title"],
                description=first.get("description", ""),
                created_at=now,
                created_by=actor.subject,
                last_edited_by=actor.subject,
            )
        except IntegrityError as exc:
            raise DomainError(
                "institutional_identifier_conflict",
                "Identificação institucional já utilizada.",
                409,
            ) from exc
        record_event(
            actor=actor,
            permission="processo:criar",
            operation="CRIAR",
            aggregate=processo,
            now=now,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        _finish_idempotency(idem, processo, 201)
        return processo, True


def add_edital(*, actor, processo_id, data, idempotency_key, correlation_id):
    require_permission(actor, "edital:criar")
    with command_context() as now:
        try:
            processo = ProcessoSeletivo.objects.get(
                pk=processo_id, institution_scope=actor.institution_scope
            )
        except ProcessoSeletivo.DoesNotExist as exc:
            raise DomainError("not_found", "Recurso não encontrado.", 404) from exc
        idem = reserve(
            actor=actor, operation=f"edital:criar:{processo_id}", key=idempotency_key, payload=data
        )
        if idem.result_id:
            return Edital.objects.get(pk=idem.result_id), False
        try:
            edital = Edital.objects.create(
                processo=processo,
                institution_scope=actor.institution_scope,
                number=data["number"],
                year=data["year"],
                title=data["title"],
                description=data.get("description", ""),
                created_at=now,
                created_by=actor.subject,
                last_edited_by=actor.subject,
            )
        except IntegrityError as exc:
            raise DomainError(
                "edital_identifier_conflict", "Número/ano do Edital já utilizado.", 409
            ) from exc
        record_event(
            actor=actor,
            permission="edital:criar",
            operation="CRIAR",
            aggregate=edital,
            now=now,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        _finish_idempotency(idem, edital, 201)
        return edital, True


def activate_process(
    *, actor, processo_id, expected_revision, reason, idempotency_key, correlation_id
):
    require_permission(actor, "processo:ativar")
    with command_context() as now:
        try:
            processo = ProcessoSeletivo.objects.select_for_update().get(
                pk=processo_id, institution_scope=actor.institution_scope
            )
        except ProcessoSeletivo.DoesNotExist as exc:
            raise DomainError("not_found", "Recurso não encontrado.", 404) from exc
        idem = reserve(
            actor=actor,
            operation=f"processo:ativar:{processo_id}",
            key=idempotency_key,
            payload={"reason": reason},
        )
        if idem.result_id:
            return ProcessoSeletivo.objects.get(pk=idem.result_id), False
        if processo.status != ProcessoSeletivo.Status.EM_ELABORACAO:
            raise DomainError(
                "invalid_state", "Somente Processo em elaboração pode ser ativado.", 409
            )
        previous_revision = processo.revision
        compare_and_swap(
            ProcessoSeletivo.objects,
            pk=processo.pk,
            expected_revision=expected_revision,
            status=ProcessoSeletivo.Status.ATIVO,
            last_changed_at=now,
        )
        processo.refresh_from_db()
        AtoAdministrativo.objects.create(
            aggregate_type="ProcessoSeletivo",
            aggregate_id=processo.pk,
            operation="ATIVAR",
            actor_subject=actor.subject,
            reason=reason,
            occurred_at=now,
        )
        record_event(
            actor=actor,
            permission="processo:ativar",
            operation="ATIVAR",
            aggregate=processo,
            now=now,
            correlation_id=correlation_id,
            reason=reason,
            previous_state=ProcessoSeletivo.Status.EM_ELABORACAO,
            previous_revision=previous_revision,
            idempotency_key=idempotency_key,
        )
        _finish_idempotency(idem, processo, 200)
        return processo, True
