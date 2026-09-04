import hashlib
from decimal import Decimal

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.editais.domain import secoes
from processo_seletivo.editais.domain.validation import blocking_findings, validate_for_publication
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import AtoAdministrativo, Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.infrastructure.pdf import (
    AutoridadeSignataria,
    render_edital_pdf,
)
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


def _decimal_canonico(valor):
    """A forma que o conteúdo publicado carrega: quatro casas, sempre, sem zero à esquerda.

    Não é `str(Decimal)`: um `Decimal("2")` viraria `"2"`, e duas gravações semanticamente iguais
    produziriam hashes diferentes. O padrão declarado em `COLECOES_PUBLICADAS` descreve exatamente
    esta forma, e é o que impede que uma Retificação escreva `"2"` ou `"002.0000"` no lugar.
    """
    return None if valor is None else f"{Decimal(valor):.4f}"


def _stages(edital: Edital) -> list[dict]:
    return [
        {
            "id": str(etapa.id),
            "name": etapa.name,
            "order": etapa.order,
            "weight": _decimal_canonico(etapa.weight),
            "eliminatory": etapa.eliminatory,
            "classificatory": etapa.classificatory,
            "minimumScore": _decimal_canonico(etapa.minimum_score),
            # O incremento da `012`: quantas avaliações e qual a máxima (FR-007). `None` viaja
            # como `null`, e é assim que "não declarado" fica dito no conteúdo publicado.
            "evaluationsPerRegistration": etapa.evaluations_per_registration,
            "maximumScore": _decimal_canonico(etapa.maximum_score),
            # O incremento da revisão da `012`: a forma da conclusão e, na decisória, os rótulos
            # com que este Edital nomeia o sentido (D-008, FR-119). A forma viaja como string e
            # nunca como `null` — não há Etapa sem forma, e é a versão canônica 6 que fixa isso.
            # Os rótulos vazios viajam como `null`, que é como o conteúdo publicado diz "não se
            # aplica", pela mesma grafia de `weight` e `minimumScore`.
            "forma": etapa.forma,
            "rotuloFavoravel": etapa.rotulo_favoravel or None,
            "rotuloDesfavoravel": etapa.rotulo_desfavoravel or None,
            # A Etapa referencia o Evento; as datas são dele e não são copiadas (FR-021).
            "scheduleEventId": None if etapa.evento_id is None else str(etapa.evento_id),
        }
        for etapa in edital.etapas.all()
    ]


def _sections(edital: Edital) -> list[dict]:
    """As seções do catálogo, na ordem declarada.

    A seção **gerada não carrega `content`** — declara a coleção que a origina, e o documento a
    compõe a partir dela. Persistir o texto gerado criaria dois endereços para o mesmo conteúdo e a
    possibilidade de retificar um deixando o outro desatualizado; não persistir resolve o problema e
    ainda dispensa regra nova na gramática, porque endereçar um campo que não existe já falha pelo
    erro de caminho inexistente da `004` (FR-040).
    """
    redigidas = {item.key: item.content for item in edital.secoes.all()}
    return [
        {
            "id": str(secoes.identidade(edital.id, secao.key)),
            "key": secao.key,
            "title": secao.title,
            "order": secao.order,
            "type": secao.type,
            **(
                {"source": secao.source}
                if secao.gerada
                # Ausência de linha significa "texto padrão do catálogo", e não "seção vazia":
                # persistir uma linha por seção só para guardar o padrão traria a estrutura de
                # volta ao banco, que é o que a declaração do catálogo existe para evitar.
                else {"content": redigidas.get(secao.key, secao.default_text)}
            ),
        }
        for secao in secoes.CATALOGO
    ]


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
                # String sempre presente, `""` quando ausente — nunca `null`, nunca chave omitida
                # (FR-014). É a convenção do próprio objeto: `description` e `locality` acima são
                # strings, e `reserveLimit` é `null` por ser numérico. Uma terceira convenção para
                # texto faria a versão canônica admitir mais de uma forma.
                "duties": profile.duties,
                "workload": profile.workload,
                "compensation": profile.compensation,
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
                # Qual Evento é o período de inscrições (FR-008 da 009). Booleano sempre presente,
                # dentro do Evento: o candidato precisa saber quando as inscrições abrem, e a
                # Retificação já alcança o campo por `/schedule/id=…/isRegistrationPeriod`, sem
                # nenhuma gramática nova.
                "isRegistrationPeriod": event.is_registration_period,
            }
            for event in cronograma.eventos.all()
        ]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "editalId": str(edital.id),
        "processoId": str(edital.processo_id),
        # A identificação institucional do Processo, para que o documento possa nomeá-lo sem expor
        # UUID a quem lê (FR-004). O efeito colateral é o que mais importa: com estes dois campos o
        # snapshot **basta** para compor o documento, sem consultar o banco — que é o que a
        # Constituição pede da cadeia "dados estruturados → versão homologada → PDF". O Processo já
        # vem por `select_related("processo")` em `_locked_edital`; não há consulta a mais.
        "processoCode": edital.processo.institutional_code,
        "processoTitle": edital.processo.title,
        "number": edital.number,
        "year": edital.year,
        "title": edital.title,
        "description": edital.description,
        "profiles": profiles,
        "schedule": schedule,
        "documentRequirements": _document_requirements(edital),
        "stages": _stages(edital),
        "sections": _sections(edital),
    }


def _document_requirements(edital: Edital) -> list[dict]:
    """Os documentos que o Edital exige do candidato, na ordem declarada (FR-008 da 009).

    `profileId` e `modalityId` são anuláveis por semântica, e não por conveniência: `null` significa
    "não restringe", e é a ausência dos dois que faz o requisito valer para todo mundo. As quatro
    combinações de aplicabilidade se leem daqui, sem operador e sem expressão.
    """
    return [
        {
            "id": str(documento.id),
            "key": documento.key,
            "name": documento.name,
            "instructions": documento.instructions,
            "required": documento.required,
            "order": documento.order,
            "profileId": None if documento.perfil_id is None else str(documento.perfil_id),
            "modalityId": (
                None if documento.modalidade_id is None else str(documento.modalidade_id)
            ),
        }
        for documento in edital.documentos_exigidos.all()
    ]


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
            return Edital.objects.get(pk=idem.result_id), [], idem.response_status
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
        return edital, findings, 200


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
            return Edital.objects.get(pk=idem.result_id), idem.response_status
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
        return edital, 200


def return_edital_to_drafting(
    *, actor, edital_id, expected_revision, reason, idempotency_key, correlation_id
):
    """FR-006: antes da Publicação, a revisão devolve o Edital a Em elaboração.

    A metade da FR-006 que faltava. Sem ela, quem revisa e discorda tinha duas saídas e nenhuma
    era a certa: cancelar — que é interrupção administrativa, estado final, e queima o número no
    escopo — ou homologar o que recusa para retificar depois, publicando o defeito de propósito.

    É ato de quem homologa, como a revogação de homologação e como a devolução da Retificação,
    que exige `retificacao:homologar` pela mesma razão: devolver desfaz a revisão que alguém
    submeteu, e quem desfaz é quem recusa.

    A `RevisaoEdital` submetida **permanece** — ela é o que foi submetido, e continua verdadeira
    depois de devolvida. A próxima submissão cria outra, com o número de revisão que esta
    transição acabou de incrementar; a única unicidade em jogo, `(edital, edital_revision)`,
    nunca colide por isso.
    """
    require_permission(actor, "edital:homologar")
    with command_context() as now:
        idem = reserve(
            actor=actor,
            operation=f"edital:devolver:{edital_id}",
            key=idempotency_key,
            payload={"reason": reason},
        )
        if idem.result_id:
            return Edital.objects.get(pk=idem.result_id), idem.response_status
        edital = _locked_edital(actor, edital_id)
        if edital.status != Edital.Status.EM_REVISAO:
            raise DomainError("invalid_state", "Edital não está em revisão.", 409)
        if not (reason or "").strip():
            raise DomainError("reason_required", "A devolução exige motivo.", 422)
        compare_and_swap(
            Edital.objects,
            pk=edital.pk,
            expected_revision=expected_revision,
            status=Edital.Status.EM_ELABORACAO,
        )
        edital.refresh_from_db()
        record_event(
            actor=actor,
            permission="edital:homologar",
            operation="DEVOLVER",
            aggregate=edital,
            now=now,
            correlation_id=correlation_id,
            reason=reason,
            previous_state=Edital.Status.EM_REVISAO,
            previous_revision=expected_revision,
            idempotency_key=idempotency_key,
        )
        _finish_idempotency(idem, edital, 200)
        return edital, 200


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
            return Edital.objects.get(pk=idem.result_id), idem.response_status
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
        return edital, 200


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
            return Publicacao.objects.get(pk=idem.result_id), idem.response_status
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
        # A autoridade é contexto do ato, não conteúdo publicado: ela chega por parâmetro
        # porque o documento é composto **antes** de a `Publicacao` existir (`008`, FR-034).
        pdf = render_edital_pdf(
            revisao.content,
            revisao.content_hash,
            autoridade=AutoridadeSignataria(nome=signatory["name"], cargo=signatory["role"]),
        )
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
        _ativar_o_processo_na_primeira_publicacao(
            edital.processo, actor=actor, now=now, correlation_id=correlation_id
        )
        _finish_idempotency(idem, publication, 201)
        return publication, 201


def _ativar_o_processo_na_primeira_publicacao(processo, *, actor, now, correlation_id):
    """Publicar o primeiro Edital **é** a abertura formal do certame (E2E-005).

    O estado tinha uma consequência só — ser precondição de encerrar —, e nada obrigava a abertura.
    O certame rodava inteiro em "Em elaboração", com Edital publicado e inscrições correndo, e no
    fim não podia ser encerrado sem uma ativação retroativa sobre fato consumado. O crachá mentia
    todo esse tempo.

    **O ato explícito continua existindo**, para quem abre o certame antes de publicar. O que muda
    é que ele deixa de ser a única porta: publicar o primeiro Edital passa a produzir a ativação
    como consequência, e não como ato à parte.

    **Por que não exige `processo:ativar`.** Isto não é um segundo ato praticado pela mesma pessoa,
    e sim efeito do ato que ela já estava autorizada a praticar — como a Versão Consolidada e o
    documento publicado, que nascem daqui sem permissão própria. Exigir a permissão faria quem
    publica precisar também poder ativar, o que inverteria a segregação em vez de reforçá-la.

    **Silencioso não é.** O `AtoAdministrativo` nasce com a autoria de quem publicou e com o
    motivo dizendo de onde a ativação veio, de modo que a trilha distinga a abertura declarada da
    derivada.
    """
    if processo.status != ProcessoSeletivo.Status.EM_ELABORACAO:
        return
    motivo = "Ativação derivada da publicação do primeiro Edital do Processo."
    anterior = processo.revision
    compare_and_swap(
        ProcessoSeletivo.objects,
        pk=processo.pk,
        expected_revision=anterior,
        status=ProcessoSeletivo.Status.ATIVO,
        last_changed_at=now,
    )
    processo.refresh_from_db()
    AtoAdministrativo.objects.create(
        aggregate_type="ProcessoSeletivo",
        aggregate_id=processo.pk,
        operation="ATIVAR",
        actor_subject=actor.subject,
        reason=motivo,
        occurred_at=now,
    )
    record_event(
        actor=actor,
        permission="edital:publicar",
        operation="ATIVAR",
        aggregate=processo,
        now=now,
        correlation_id=correlation_id,
        reason=motivo,
        previous_state=ProcessoSeletivo.Status.EM_ELABORACAO,
        previous_revision=anterior,
    )
