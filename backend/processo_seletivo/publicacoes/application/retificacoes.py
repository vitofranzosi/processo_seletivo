import hashlib

from django.db.models import F

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.editais.domain.validation import (
    blocking_findings,
    validate_for_publication,
)
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.domain.changes import (
    AcrescimoPosicionado,
    ChaveNaoEncontrada,
    ColecaoAtomica,
    ColecaoDescaracterizada,
    EnderecamentoPosicional,
    EntidadeSemChave,
    IdentidadeImplicita,
    IdentidadeNaoEnderecavel,
    SeletorInvalido,
    apply_changes,
)
from processo_seletivo.publicacoes.domain.conflicts import (
    DUPLICATE_KEY,
    HASH_MISMATCH,
    KEY_NOT_FOUND,
    TARGET_PRESENT,
    content_conflicts,
    derive_preconditions,
    duplicate_keys,
)
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
from processo_seletivo.shared.idempotency import finish as finish_idempotency
from processo_seletivo.shared.idempotency import reserve


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
        {
            "targetPath": item.target_path,
            "operation": item.operation,
            "newValue": item.new_value,
            "expectedPreviousHash": item.expected_previous_hash,
        }
        for item in retificacao.alteracoes.all()
    ]


# Endereçar por posição só faz sentido recusar na elaboração: impede o ato instável de nascer,
# e nenhum ato já elaborado pode conter essa forma (FR-007).
POSITIONAL_REFUSED = "positional_addressing_refused"

CONFLICT_MESSAGES = {
    KEY_NOT_FOUND: (
        "O item normativo endereçado em {paths} não existe no conteúdo sobre o qual esta "
        "Retificação passaria a valer: outra Retificação publicada no intervalo o removeu. "
        "Refaça a Retificação sobre a versão consolidada atual."
    ),
    DUPLICATE_KEY: (
        "A composição deixaria mais de um item com o mesmo identificador em: {paths}. "
        "Refaça a Retificação sobre a versão consolidada atual."
    ),
    HASH_MISMATCH: (
        "O conteúdo anterior informado não corresponde ao vigente em: {paths}. "
        "Refaça a Retificação sobre a versão consolidada atual."
    ),
    TARGET_PRESENT: (
        "A operação ADD pressupõe caminho ausente, mas já há conteúdo vigente em: {paths}. "
        "Use REPLACE sobre a versão consolidada atual."
    ),
}


def _reject_stale_changes(content, changes):
    """Rejeita alterações cuja precondição de conteúdo já não se verifica (FR-036)."""
    conflicts = content_conflicts(content, changes)
    for code in (KEY_NOT_FOUND, DUPLICATE_KEY, HASH_MISMATCH, TARGET_PRESENT):
        paths = conflicts.get(code)
        if paths:
            raise DomainError(code, CONFLICT_MESSAGES[code].format(paths=", ".join(paths)), 409)


MISSING_PRECONDITION = "precondition_missing"


def _reject_changes_without_content_precondition(changes):
    """`REPLACE` e `REMOVE` não são publicáveis sem hash do conteúdo que substituem ou apagam.

    O caminho por chave garante que o ato ainda fala da mesma entidade; ele não diz nada sobre o
    conteúdo dela. Sem o hash, duas Retificações que alterem o mesmo campo do mesmo Perfil
    passariam as duas, e a segunda sobrescreveria a primeira em silêncio — que é o caso original
    da FR-036, e a razão de a precondição por hash não ter saído junto com a âncora (FR-014).

    Alcança qualquer linha que chegue por fora da elaboração. Recusar é o comportamento seguro:
    devolver e reenviar o rascunho sobre a versão vigente reconstrói a precondição.
    """
    orphans = [
        change["targetPath"]
        for change in changes
        if change["operation"] in {"REPLACE", "REMOVE"} and not change.get("expectedPreviousHash")
    ]
    if orphans:
        raise DomainError(
            MISSING_PRECONDITION,
            "Esta Retificação não declara o conteúdo anterior de: "
            f"{', '.join(orphans)}, e não pode ser publicada sem ele. Devolva-a para elaboração "
            "e reenvie o rascunho sobre a versão consolidada atual.",
            409,
        )


# A ordem importa: `ChaveNaoEncontrada` é um `CaminhoInexistente`, e a específica precisa ser
# reconhecida antes da genérica. `invalid_change` recebe o que é erro de forma do caminho —
# seletor malformado, coleção atômica item a item, acréscimo em posição, entidade sem chave e as
# duas violações de identidade —, porque o contrato declara três códigos novos e não nove.
RECUSAS_DE_CAMINHO = (
    (EnderecamentoPosicional, POSITIONAL_REFUSED, 422),
    (ChaveNaoEncontrada, KEY_NOT_FOUND, 409),
    (SeletorInvalido, "invalid_change", 422),
    (ColecaoAtomica, "invalid_change", 422),
    (AcrescimoPosicionado, "invalid_change", 422),
    (EntidadeSemChave, "invalid_change", 422),
    (IdentidadeNaoEnderecavel, "invalid_change", 422),
    (IdentidadeImplicita, "invalid_change", 422),
    (ColecaoDescaracterizada, "invalid_change", 422),
)


def _recusa_de_caminho(exc):
    """Traduz a recusa do domínio no código do contrato.

    A mensagem do domínio é preservada porque é ela que nomeia o caminho envolvido (FR-010).
    """
    for tipo, code, status in RECUSAS_DE_CAMINHO:
        if isinstance(exc, tipo):
            return DomainError(code, str(exc), status)
    return DomainError("invalid_change", str(exc), 422)


def _no_effective_change():
    return DomainError(
        "no_effective_change",
        "A Retificação não altera o conteúdo normativo do Edital.",
        422,
    )


def _apply_declared_changes(base, changes):
    """Aplica sobre a base declarada e exige efeito prático (FR-026) e precondições (FR-036)."""
    try:
        content, _ = apply_changes(base, changes, publication_id="draft")
    except ValueError as exc:
        raise _recusa_de_caminho(exc) from exc
    _reject_stale_changes(base, changes)
    if canonical_sha256(content) == canonical_sha256(base):
        raise _no_effective_change()
    return content


def _replace_changes(retificacao, changes, base_content):
    """Persiste as alterações já com a precondição de conteúdo que valerá na Publicação.

    Quem elabora vê a base declarada em `baseSnapshotId`; derivar a precondição dela aqui é o
    que garante que o ato publicado encontre o conteúdo que estava à vista, e não o que outra
    Retificação publicada no intervalo tenha deixado no lugar (FR-036 da `001`).
    """
    preconditions = derive_preconditions(base_content, changes)
    retificacao.alteracoes.all().delete()
    AlteracaoNormativa.objects.bulk_create(
        [
            AlteracaoNormativa(
                retificacao=retificacao,
                target_path=item["targetPath"],
                operation=item["operation"],
                new_value=item.get("newValue"),
                expected_previous_hash=precondition,
                order=index,
            )
            for index, (item, precondition) in enumerate(
                zip(changes, preconditions, strict=True), 1
            )
        ]
    )


def create_retification(*, actor, edital_id, data, idempotency_key, correlation_id):
    require_permission(actor, "retificacao:elaborar")
    with command_context() as now:
        idem = reserve(
            actor=actor,
            operation=f"retificacao:elaborar:{edital_id}",
            key=idempotency_key,
            payload=data,
        )
        if idem.result_id:
            return Retificacao.objects.get(pk=idem.result_id), idem.response_status
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
        _apply_declared_changes(base.content, data["changes"])
        _replace_changes(retificacao, data["changes"], base.content)
        record_event(
            actor=actor,
            permission="retificacao:elaborar",
            operation="CRIAR",
            aggregate=retificacao,
            now=now,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        finish_idempotency(idem, retificacao, 201)
        return retificacao, 201


def edit_retification(*, actor, retificacao_id, expected_revision, data):
    require_permission(actor, "retificacao:elaborar")
    with command_context():
        item = _retificacao(actor, retificacao_id)
        if item.status != Retificacao.Status.EM_ELABORACAO:
            raise DomainError("invalid_state", "Retificação não está em elaboração.", 409)
        # Rebase: uma Retificação devolvida por conflito precisa poder reapontar para a
        # versão consolidada atual, senão a correção nasce sobre a mesma base obsoleta.
        base = item.base_snapshot
        if data.get("baseSnapshotId") and data["baseSnapshotId"] != base.pk:
            try:
                base = VersaoConsolidada.objects.get(
                    pk=data["baseSnapshotId"], edital=item.edital_id
                )
            except VersaoConsolidada.DoesNotExist as exc:
                raise DomainError("not_found", "Recurso não encontrado.", 404) from exc
        _apply_declared_changes(base.content, data["changes"])
        compare_and_swap(
            Retificacao.objects,
            pk=item.pk,
            expected_revision=expected_revision,
            base_snapshot=base,
            justification=data["justification"],
            effective_at=data.get("effectiveAt"),
        )
        _replace_changes(item, data["changes"], base.content)
        item.refresh_from_db()
        return item


# Estados de origem admitidos e estado alvo de cada transição. `None` significa
# "qualquer estado não final", verificado à parte.
TRANSITIONS = {
    "submeter": ((Retificacao.Status.EM_ELABORACAO,), Retificacao.Status.EM_REVISAO),
    "homologar": ((Retificacao.Status.EM_REVISAO,), Retificacao.Status.HOMOLOGADA),
    "devolver": (
        (Retificacao.Status.EM_REVISAO, Retificacao.Status.HOMOLOGADA),
        Retificacao.Status.EM_ELABORACAO,
    ),
    "cancelar": (None, Retificacao.Status.CANCELADA),
}

# Devolver desfaz revisão ou homologação: é ato de quem homologa, como a revogação de
# homologação do Edital, que também exige `edital:homologar`.
TRANSITION_PERMISSIONS = {"devolver": "retificacao:homologar"}


def transition_retification(
    *, actor, retificacao_id, expected_revision, action, reason="", idempotency_key, correlation_id
):
    permission = TRANSITION_PERMISSIONS.get(action, f"retificacao:{action}")
    require_permission(actor, permission)
    with command_context() as now:
        idem = reserve(
            actor=actor,
            operation=f"retificacao:{action}:{retificacao_id}",
            key=idempotency_key,
            payload={"reason": reason},
        )
        if idem.result_id:
            return Retificacao.objects.get(pk=idem.result_id), idem.response_status
        item = _retificacao(actor, retificacao_id)
        origins, target = TRANSITIONS[action]
        previous = item.status
        if origins and previous not in origins:
            raise DomainError("invalid_state", "Transição inválida para a Retificação.", 409)
        if action == "cancelar" and previous in {
            Retificacao.Status.PUBLICADA,
            Retificacao.Status.CANCELADA,
        }:
            raise DomainError("invalid_state", "Retificação final não pode ser cancelada.", 409)
        if action == "devolver" and not reason.strip():
            raise DomainError("reason_required", "A devolução exige motivo.", 422)
        changes = {"status": target}
        if action == "submeter":
            changes.update(prepared_by=actor.subject, submitted_at=now)
        elif action == "homologar":
            changes.update(
                homologated_by=actor.subject, homologated_at=now, homologation_reason=reason
            )
        elif action == "devolver":
            # A homologação desfeita não pode continuar descrevendo um ato em elaboração;
            # sua autoria permanece no registro de auditoria do evento HOMOLOGAR.
            changes.update(
                homologated_by="",
                homologated_at=None,
                homologation_reason="",
                return_reason=reason,
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
            correlation_id=correlation_id,
            reason=reason,
            previous_state=previous,
            previous_revision=expected_revision,
            idempotency_key=idempotency_key,
        )
        finish_idempotency(idem, item, 200)
        return item, 200


def _original_version(edital):
    return (
        VersaoConsolidada.objects.filter(edital=edital, source_publication__revisao__isnull=False)
        .order_by("valid_from")
        .first()
    )


def _published_retifications(edital):
    return list(
        Retificacao.objects.filter(edital=edital, status=Retificacao.Status.PUBLICADA)
        .select_related("publication")
        .prefetch_related("alteracoes")
    )


def _acts(items):
    return [
        {
            "effectiveAt": item.publication.effective_at,
            "publicationOrder": item.publication.publication_order,
            "publicationId": str(item.publication_id),
            "changes": _changes_payload(item),
        }
        for item in items
    ]


def _consolidate(base_content, acts):
    """Consolida, traduzindo alteração inaplicável em rejeição em vez de erro interno.

    A composição só é conhecida ao aplicar todos os atos vigentes em ordem: uma Retificação
    pode remover o caminho que outra, publicada antes mas com vigência posterior, substitui.
    Nesse caso não há resultado determinístico a materializar, e a FR-039 exige que haja.
    """
    try:
        content, provenance = consolidate(base_content, acts)
    except ValueError as exc:
        raise DomainError(
            "inconsistent_consolidation",
            f"A composição das Retificações vigentes ficaria inconsistente: {exc}. "
            "Refaça a Retificação sobre a versão consolidada atual.",
            409,
        ) from exc
    repetidas = duplicate_keys(content)
    if repetidas:
        raise DomainError(
            DUPLICATE_KEY,
            CONFLICT_MESSAGES[DUPLICATE_KEY].format(paths=", ".join(repetidas)),
            409,
        )
    return content, provenance


def _content_in_force(edital, moment):
    """Conteúdo consolidado das Retificações já publicadas que vigoram em `moment`."""
    applicable = [
        item for item in _published_retifications(edital) if item.publication.effective_at <= moment
    ]
    content, _ = _consolidate(_original_version(edital).content, _acts(applicable))
    return content


def _assert_effective_change(edital, retificacao, effective_at, publication_order):
    """O efeito prático é medido no início da própria vigência (FR-027).

    Compara o conteúdo que já vigoraria sem este ato com o conteúdo que passa a vigorar
    com ele. Captura tanto a mudança declarada sem efeito quanto o ato esvaziado por
    outra Retificação publicada entre a homologação e esta Publicação.
    """
    original = _original_version(edital)
    in_force = _acts(
        [
            item
            for item in _published_retifications(edital)
            if item.publication.effective_at <= effective_at
        ]
    )
    pendente = {
        "effectiveAt": effective_at,
        "publicationOrder": publication_order,
        "publicationId": "pending",
        "changes": _changes_payload(retificacao),
    }
    antes, _ = _consolidate(original.content, in_force)
    depois, _ = _consolidate(original.content, [*in_force, pendente])
    if canonical_sha256(antes) == canonical_sha256(depois):
        raise _no_effective_change()


def _assert_structurally_publishable(content, boundary):
    """As invariantes da Publicação valem também para o que a Retificação faz vigorar (FR-006).

    `publish_edital` recusa Edital sem título, sem Perfil ou sem Cronograma; sem esta verificação
    a mesma regra deixava de valer justamente no caminho pelo qual o conteúdo muda depois de
    público, e uma Retificação podia deixar vigente um Edital sem nenhum Perfil.
    """
    errors = blocking_findings(validate_for_publication(content))
    if errors:
        raise DomainError(
            "blocking_findings",
            "O conteúdo que passaria a vigorar em "
            f"{boundary.isoformat()} possui erros impeditivos: "
            + "; ".join(item.message for item in errors),
            422,
        )


def _materialize_affected_versions(retificacao, publication, now):
    original = _original_version(retificacao.edital)
    published = _published_retifications(retificacao.edital)
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
        acts = _acts(applicable)
        content, provenance = _consolidate(original.content, acts)
        _assert_structurally_publishable(content, boundary)
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


def publish_retification(
    *, actor, retificacao_id, expected_revision, signatory, idempotency_key, correlation_id
):
    require_permission(actor, "retificacao:publicar")
    with command_context() as now:
        idem = reserve(
            actor=actor,
            operation=f"retificacao:publicar:{retificacao_id}",
            key=idempotency_key,
            payload={"signatory": signatory},
        )
        if idem.result_id:
            return Publicacao.objects.get(pk=idem.result_id), idem.response_status
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
        changes = _changes_payload(item)
        _reject_changes_without_content_precondition(changes)
        _reject_stale_changes(_content_in_force(edital, effective_at), changes)
        _assert_effective_change(edital, item, effective_at, edital.next_publication_order)
        content, _ = apply_changes(item.base_snapshot.content, changes, publication_id="pending")
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
        # Publicar é o ato que muda o que o público vê; era o único da Retificação que não
        # deixava registro, porque não passa pela transição compartilhada com os demais.
        record_event(
            actor=actor,
            permission="retificacao:publicar",
            operation="PUBLICAR",
            aggregate=item,
            now=now,
            correlation_id=correlation_id,
            previous_state=Retificacao.Status.HOMOLOGADA,
            previous_revision=expected_revision,
            idempotency_key=idempotency_key,
        )
        _materialize_affected_versions(item, publication, now)
        Edital.objects.filter(pk=edital.pk).update(
            next_publication_order=F("next_publication_order") + 1
        )
        finish_idempotency(idem, publication, 201)
        return publication, 201
