import hashlib

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.editais.domain.validation import blocking_findings, validate_for_publication
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.infrastructure.pdf import render_edital_pdf
from processo_seletivo.publicacoes.models import (
    DocumentoPublicado,
    Homologacao,
    Publicacao,
    RevisaoEdital,
)
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.canonical import SCHEMA_VERSION, canonical_bytes, canonical_sha256
from processo_seletivo.shared.concurrency import compare_and_swap
from processo_seletivo.shared.idempotency import finish as _finish_idempotency
from processo_seletivo.shared.idempotency import reserve


def edital_snapshot(edital: Edital) -> dict:
    profiles = []
    for profile in edital.perfis.prefetch_related("modalidades__regra_normativa").order_by("code"):
        modalities = []
        for modality in profile.modalidades.order_by("code"):
            rule = getattr(modality, "regra_normativa", None)
            modalities.append(
                {
                    "id": str(modality.id),
                    "code": modality.code,
                    "name": modality.name,
                    "description": modality.description,
                    "normativeRule": None
                    if rule is None
                    else {
                        "id": str(rule.id),
                        "foundation": rule.foundation,
                        "version": rule.version,
                        "percentage": None if rule.percentage is None else str(rule.percentage),
                        "calculation": rule.calculation,
                        "rounding": rule.rounding,
                        "distribution": rule.distribution,
                        "callRules": rule.call_rules,
                        "effectiveFrom": None
                        if rule.effective_from is None
                        else rule.effective_from.isoformat(),
                    },
                }
            )
        profiles.append(
            {
                "id": str(profile.id),
                "code": profile.code,
                "name": profile.name,
                "description": profile.description,
                "requirements": profile.requirements,
                "immediateVacancies": profile.immediate_vacancies,
                "reserveType": profile.reserve_type,
                "reserveLimit": profile.reserve_limit,
                "locality": profile.locality,
                "classificationInformation": profile.classification_information,
                "callInformation": profile.call_information,
                "competitionModalities": modalities,
            }
        )
    schedule = []
    cronograma = getattr(edital, "cronograma", None)
    if cronograma:
        schedule = [
            {
                "id": str(event.id),
                "type": event.type,
                "description": event.description,
                "startAt": event.start_at.isoformat(),
                "endAt": None if event.end_at is None else event.end_at.isoformat(),
                "order": event.order,
                "status": event.status,
            }
            for event in cronograma.eventos.all()
        ]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "editalId": str(edital.id),
        "processoId": str(edital.processo_id),
        "number": edital.number,
        "year": edital.year,
        "title": edital.title,
        "description": edital.description,
        "profiles": profiles,
        "schedule": schedule,
    }


def _locked_edital(actor, edital_id):
    try:
        edital = (
            Edital.objects.select_for_update()
            .select_related("processo")
            .get(pk=edital_id, institution_scope=actor.institution_scope)
        )
    except Edital.DoesNotExist as exc:
        raise DomainError("not_found", "Recurso não encontrado.", 404) from exc
    ensure_processo_accepts_changes(edital.processo)
    return edital


def submit_edital(*, actor, edital_id, expected_revision, idempotency_key, correlation_id):
    require_permission(actor, "edital:submeter")
    with command_context() as now:
        idem = reserve(
            actor=actor,
            operation=f"edital:submeter:{edital_id}",
            key=idempotency_key,
            payload={},
        )
        if idem.result_id:
            return Edital.objects.get(pk=idem.result_id), [], False
        edital = _locked_edital(actor, edital_id)
        if edital.status != Edital.Status.EM_ELABORACAO:
            raise DomainError("invalid_state", "Edital não está em elaboração.", 409)
        snapshot = edital_snapshot(edital)
        findings = validate_for_publication(snapshot)
        errors = blocking_findings(findings)
        if errors:
            raise DomainError("blocking_findings", "; ".join(item.message for item in errors), 422)
        canonical = canonical_bytes(snapshot)
        RevisaoEdital.objects.create(
            edital=edital,
            edital_revision=edital.revision,
            content=snapshot,
            canonical_content=canonical,
            canonical_schema_version=SCHEMA_VERSION,
            content_hash=canonical_sha256(snapshot),
            prepared_by=actor.subject,
            submitted_at=now,
        )
        compare_and_swap(
            Edital.objects,
            pk=edital.pk,
            expected_revision=expected_revision,
            status=Edital.Status.EM_REVISAO,
        )
        edital.refresh_from_db()
        edital.validation_findings = findings
        record_event(
            actor=actor,
            permission="edital:submeter",
            operation="SUBMETER",
            aggregate=edital,
            now=now,
            correlation_id=correlation_id,
            previous_state=Edital.Status.EM_ELABORACAO,
            previous_revision=expected_revision,
            idempotency_key=idempotency_key,
        )
        _finish_idempotency(idem, edital, 200)
        return edital, findings, True


def homologate_edital(
    *, actor, edital_id, expected_revision, reason, idempotency_key, correlation_id
):
    require_permission(actor, "edital:homologar")
    with command_context() as now:
        idem = reserve(
            actor=actor,
            operation=f"edital:homologar:{edital_id}",
            key=idempotency_key,
            payload={"reason": reason},
        )
        if idem.result_id:
            return Edital.objects.get(pk=idem.result_id), False
        edital = _locked_edital(actor, edital_id)
        if edital.status != Edital.Status.EM_REVISAO:
            raise DomainError("invalid_state", "Edital não está em revisão.", 409)
        revisao = edital.revisoes.order_by("-submitted_at").first()
        Homologacao.objects.create(
            revisao=revisao,
            homologated_by=actor.subject,
            reason=reason,
            homologated_at=now,
        )
        compare_and_swap(
            Edital.objects,
            pk=edital.pk,
            expected_revision=expected_revision,
            status=Edital.Status.HOMOLOGADO,
        )
        edital.refresh_from_db()
        record_event(
            actor=actor,
            permission="edital:homologar",
            operation="HOMOLOGAR",
            aggregate=edital,
            now=now,
            correlation_id=correlation_id,
            reason=reason,
            previous_state=Edital.Status.EM_REVISAO,
            previous_revision=expected_revision,
            idempotency_key=idempotency_key,
        )
        _finish_idempotency(idem, edital, 200)
        return edital, True


def revoke_homologation(
    *, actor, edital_id, expected_revision, reason, idempotency_key, correlation_id
):
    require_permission(actor, "edital:homologar")
    with command_context() as now:
        idem = reserve(
            actor=actor,
            operation=f"edital:revogar-homologacao:{edital_id}",
            key=idempotency_key,
            payload={"reason": reason},
        )
        if idem.result_id:
            return Edital.objects.get(pk=idem.result_id), False
        edital = _locked_edital(actor, edital_id)
        if edital.status != Edital.Status.HOMOLOGADO:
            raise DomainError("invalid_state", "Edital não está homologado.", 409)
        homologacao = Homologacao.objects.filter(
            revisao__edital=edital, revoked_at__isnull=True
        ).latest("homologated_at")
        homologacao.revoked_at = now
        homologacao.revoked_by = actor.subject
        homologacao.revocation_reason = reason
        homologacao.save(update_fields=["revoked_at", "revoked_by", "revocation_reason"])
        compare_and_swap(
            Edital.objects,
            pk=edital.pk,
            expected_revision=expected_revision,
            status=Edital.Status.EM_REVISAO,
        )
        edital.refresh_from_db()
        record_event(
            actor=actor,
            permission="edital:homologar",
            operation="REVOGAR_HOMOLOGACAO",
            aggregate=edital,
            now=now,
            correlation_id=correlation_id,
            reason=reason,
            previous_state=Edital.Status.HOMOLOGADO,
            previous_revision=expected_revision,
            idempotency_key=idempotency_key,
        )
        _finish_idempotency(idem, edital, 200)
        return edital, True


def publish_edital(
    *, actor, edital_id, expected_revision, signatory, reason, idempotency_key, correlation_id
):
    require_permission(actor, "edital:publicar")
    payload = {"signatory": signatory, "reason": reason}
    with command_context() as now:
        idem = reserve(
            actor=actor,
            operation=f"edital:publicar:{edital_id}",
            key=idempotency_key,
            payload=payload,
        )
        if idem.result_id:
            return Publicacao.objects.get(pk=idem.result_id), False
        edital = _locked_edital(actor, edital_id)
        if edital.status != Edital.Status.HOMOLOGADO:
            raise DomainError("invalid_state", "Edital não está homologado.", 409)
        revisao = edital.revisoes.order_by("-submitted_at").first()
        homologacao = Homologacao.objects.filter(revisao=revisao, revoked_at__isnull=True).latest(
            "homologated_at"
        )
        if revisao.prepared_by == homologacao.homologated_by == actor.subject:
            raise DomainError(
                "segregation_of_duties",
                "Uma única pessoa não pode elaborar, homologar e publicar.",
                403,
            )
        current_snapshot = edital_snapshot(edital)
        if canonical_sha256(current_snapshot) != revisao.content_hash:
            raise DomainError(
                "homologated_revision_changed", "O rascunho diverge da revisão homologada.", 409
            )
        findings = validate_for_publication(current_snapshot)
        if blocking_findings(findings):
            raise DomainError("blocking_findings", "O Edital possui erros impeditivos.", 422)
        pdf = render_edital_pdf(revisao.content, revisao.content_hash)
        document_hash = hashlib.sha256(pdf).hexdigest()
        publication = Publicacao.objects.create(
            edital=edital,
            revisao=revisao,
            publication_order=edital.next_publication_order,
            published_at=now,
            effective_at=now,
            content_hash=revisao.content_hash,
            canonical_content=revisao.canonical_content,
            canonical_schema_version=revisao.canonical_schema_version,
            published_by=actor.subject,
            signatory_id=signatory["authorityId"],
            signatory_name=signatory["name"],
            signatory_role=signatory["role"],
        )
        document = DocumentoPublicado.objects.create(
            publicacao=publication,
            bytes=pdf,
            document_hash=document_hash,
        )
        publication.document_hash = document.document_hash
        from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

        VersaoConsolidada.objects.create(
            edital=edital,
            valid_from=now,
            materialized_at=now,
            source_publication=publication,
            content=revisao.content,
            canonical_content=revisao.canonical_content,
            content_hash=revisao.content_hash,
            applied_publications=[str(publication.id)],
        )
        compare_and_swap(
            Edital.objects,
            pk=edital.pk,
            expected_revision=expected_revision,
            status=Edital.Status.PUBLICADO,
            next_publication_order=edital.next_publication_order + 1,
        )
        edital.refresh_from_db()
        record_event(
            actor=actor,
            permission="edital:publicar",
            operation="PUBLICAR",
            aggregate=edital,
            now=now,
            correlation_id=correlation_id,
            reason=reason,
            previous_state=Edital.Status.HOMOLOGADO,
            previous_revision=expected_revision,
            idempotency_key=idempotency_key,
        )
        _finish_idempotency(idem, publication, 201)
        return publication, True
