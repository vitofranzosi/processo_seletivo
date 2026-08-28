import hashlib

from django.db.models import F

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.domain.changes import apply_changes
from processo_seletivo.publicacoes.domain.consolidation import consolidate
from processo_seletivo.publicacoes.infrastructure.pdf import render_edital_pdf
from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from processo_seletivo.publicacoes.models_retificacao import (
    AlteracaoNormativa,
    ProvenienciaConteudo,
    Retificacao,
    VersaoConsolidada,
)
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.canonical import SCHEMA_VERSION, canonical_bytes, canonical_sha256
from processo_seletivo.shared.concurrency import compare_and_swap


def _retificacao(actor, retificacao_id):
    try:
        item = (
            Retificacao.objects.select_for_update()
            .select_related("edital__processo")
            .get(pk=retificacao_id, edital__institution_scope=actor.institution_scope)
        )
    except Retificacao.DoesNotExist as exc:
        raise DomainError("not_found", "Recurso não encontrado.", 404) from exc
    ensure_processo_accepts_changes(item.edital.processo)
    return item


def _changes_payload(retificacao):
    return [
        {"targetPath": item.target_path, "operation": item.operation, "newValue": item.new_value}
        for item in retificacao.alteracoes.all()
    ]


def _replace_changes(retificacao, changes):
    retificacao.alteracoes.all().delete()
    AlteracaoNormativa.objects.bulk_create(
        [
            AlteracaoNormativa(
                retificacao=retificacao,
                target_path=item["targetPath"],
                operation=item["operation"],
                new_value=item.get("newValue"),
                expected_previous_hash=item.get("expectedPreviousHash", ""),
                order=index,
            )
            for index, item in enumerate(changes, 1)
        ]
    )


def create_retification(*, actor, edital_id, data):
    require_permission(actor, "retificacao:elaborar")
    with command_context() as now:
        try:
            edital = Edital.objects.select_related("processo").get(
                pk=edital_id, institution_scope=actor.institution_scope
            )
            base = VersaoConsolidada.objects.get(pk=data["baseSnapshotId"], edital=edital)
        except (Edital.DoesNotExist, VersaoConsolidada.DoesNotExist) as exc:
            raise DomainError("not_found", "Recurso não encontrado.", 404) from exc
        ensure_processo_accepts_changes(edital.processo)
        if edital.status != Edital.Status.PUBLICADO:
            raise DomainError("invalid_state", "Somente Edital publicado pode ser retificado.", 409)
        retificacao = Retificacao.objects.create(
            edital=edital,
            base_snapshot=base,
            justification=data["justification"],
            effective_at=data.get("effectiveAt"),
            created_by=actor.subject,
            created_at=now,
        )
        try:
            apply_changes(base.content, data["changes"], publication_id="draft")
        except ValueError as exc:
            raise DomainError("invalid_change", str(exc), 422) from exc
        _replace_changes(retificacao, data["changes"])
        record_event(
            actor=actor,
            permission="retificacao:elaborar",
            operation="CRIAR",
            aggregate=retificacao,
            now=now,
            correlation_id="",
        )
        return retificacao


def edit_retification(*, actor, retificacao_id, expected_revision, data):
    require_permission(actor, "retificacao:elaborar")
    with command_context():
        item = _retificacao(actor, retificacao_id)
        if item.status != Retificacao.Status.EM_ELABORACAO:
            raise DomainError("invalid_state", "Retificação não está em elaboração.", 409)
        try:
            apply_changes(item.base_snapshot.content, data["changes"], publication_id="draft")
        except ValueError as exc:
            raise DomainError("invalid_change", str(exc), 422) from exc
        compare_and_swap(
            Retificacao.objects,
            pk=item.pk,
            expected_revision=expected_revision,
            justification=data["justification"],
            effective_at=data.get("effectiveAt"),
        )
        _replace_changes(item, data["changes"])
        item.refresh_from_db()
        return item


def transition_retification(*, actor, retificacao_id, expected_revision, action, reason=""):
    permission = f"retificacao:{action}"
    require_permission(actor, permission)
    states = {
        "submeter": (Retificacao.Status.EM_ELABORACAO, Retificacao.Status.EM_REVISAO),
        "homologar": (Retificacao.Status.EM_REVISAO, Retificacao.Status.HOMOLOGADA),
        "cancelar": (None, Retificacao.Status.CANCELADA),
    }
    with command_context() as now:
        item = _retificacao(actor, retificacao_id)
        previous, target = states[action]
        if previous and item.status != previous:
            raise DomainError("invalid_state", "Transição inválida para a Retificação.", 409)
        if action == "cancelar" and item.status in {
            Retificacao.Status.PUBLICADA,
            Retificacao.Status.CANCELADA,
        }:
            raise DomainError("invalid_state", "Retificação final não pode ser cancelada.", 409)
        changes = {"status": target}
        if action == "submeter":
            changes.update(prepared_by=actor.subject, submitted_at=now)
        elif action == "homologar":
            changes.update(
                homologated_by=actor.subject, homologated_at=now, homologation_reason=reason
            )
        else:
            changes["cancellation_reason"] = reason
        compare_and_swap(
            Retificacao.objects, pk=item.pk, expected_revision=expected_revision, **changes
        )
        item.refresh_from_db()
        record_event(
            actor=actor,
            permission=permission,
            operation=action.upper(),
            aggregate=item,
            now=now,
            correlation_id="",
            reason=reason,
            previous_state=previous or "",
            previous_revision=expected_revision,
        )
        return item


def _materialize_affected_versions(retificacao, publication, now):
    original = (
        VersaoConsolidada.objects.filter(
            edital=retificacao.edital, source_publication__revisao__isnull=False
        )
        .order_by("valid_from")
        .first()
    )
    published = list(
        Retificacao.objects.filter(edital=retificacao.edital, status=Retificacao.Status.PUBLICADA)
        .select_related("publication")
        .prefetch_related("alteracoes")
    )
    boundaries = sorted(
        {
            item.publication.effective_at
            for item in published
            if item.publication.effective_at >= publication.effective_at
        }
    )
    publications = {str(item.publication_id): item.publication for item in published}
    for boundary in boundaries:
        applicable = [item for item in published if item.publication.effective_at <= boundary]
        acts = [
            {
                "effectiveAt": item.publication.effective_at,
                "publicationOrder": item.publication.publication_order,
                "publicationId": str(item.publication_id),
                "changes": _changes_payload(item),
            }
            for item in applicable
        ]
        content, provenance = consolidate(original.content, acts)
        version = VersaoConsolidada.objects.create(
            edital=retificacao.edital,
            valid_from=boundary,
            materialized_at=now,
            source_publication=publication,
            content=content,
            canonical_content=canonical_bytes(content),
            content_hash=canonical_sha256(content),
            applied_publications=[act["publicationId"] for act in acts],
        )
        ProvenienciaConteudo.objects.bulk_create(
            [
                ProvenienciaConteudo(
                    versao=version,
                    target_path=path,
                    publicacao=publications[publication_id],
                )
                for path, publication_id in provenance.items()
            ]
        )


def publish_retification(*, actor, retificacao_id, expected_revision, signatory):
    require_permission(actor, "retificacao:publicar")
    with command_context() as now:
        item = _retificacao(actor, retificacao_id)
        edital = Edital.objects.select_for_update().get(pk=item.edital_id)
        if item.status != Retificacao.Status.HOMOLOGADA:
            raise DomainError("invalid_state", "Retificação não está homologada.", 409)
        if item.prepared_by == item.homologated_by == actor.subject:
            raise DomainError(
                "segregation_of_duties", "Uma pessoa não pode elaborar, homologar e publicar.", 403
            )
        effective_at = item.effective_at or now
        if effective_at < now:
            raise DomainError("invalid_effective_at", "Vigência não pode ser retroativa.", 422)
        content, _ = apply_changes(
            item.base_snapshot.content, _changes_payload(item), publication_id="pending"
        )
        canonical = canonical_bytes(content)
        pdf = render_edital_pdf(content, canonical_sha256(content))
        publication = Publicacao.objects.create(
            edital=edital,
            revisao=None,
            publication_order=edital.next_publication_order,
            published_at=now,
            effective_at=effective_at,
            content_hash=canonical_sha256(content),
            canonical_content=canonical,
            canonical_schema_version=SCHEMA_VERSION,
            published_by=actor.subject,
            signatory_id=signatory["authorityId"],
            signatory_name=signatory["name"],
            signatory_role=signatory["role"],
        )
        DocumentoPublicado.objects.create(
            publicacao=publication, bytes=pdf, document_hash=hashlib.sha256(pdf).hexdigest()
        )
        updated = Retificacao.objects.filter(pk=item.pk, revision=expected_revision).update(
            status=Retificacao.Status.PUBLICADA, publication=publication, revision=F("revision") + 1
        )
        if updated != 1:
            raise DomainError("stale_revision", "A revisão informada está obsoleta.", 412)
        item.refresh_from_db()
        _materialize_affected_versions(item, publication, now)
        Edital.objects.filter(pk=edital.pk).update(
            next_publication_order=F("next_publication_order") + 1
        )
        return publication
