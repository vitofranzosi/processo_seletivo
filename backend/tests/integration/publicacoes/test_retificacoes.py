from datetime import timedelta

import pytest
from django.db import DatabaseError, connection
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import (
    AlteracaoNormativa,
    ProvenienciaConteudo,
    Retificacao,
    VersaoConsolidada,
)
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.edital import actor_headers, caminho_evento, caminho_perfil
from tests.fixtures.publicacao import SIGNATORY, publish_original, retify

VAGAS = caminho_perfil("immediateVacancies")
DESCRICAO_DO_EVENTO = caminho_evento("description")
PERFIL_UNICO = caminho_perfil()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_published_retification_preserves_original_and_creates_consolidated_version(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    create = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Correção",
            "changes": [
                {"targetPath": "/title", "operation": "REPLACE", "newValue": "Título retificado"}
            ],
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"]),
    )
    assert create.status_code == 201
    retificacao = Retificacao.objects.get()
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/submissoes",
        format="json",
        **{**actor_headers("retificador", ["retificacao:submeter"]), "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{**actor_headers("homologador-r", ["retificacao:homologar"]), "HTTP_IF_MATCH": '"2"'},
    )
    published = api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/publicacoes",
        {
            "signatory": {
                "authorityId": "00000000-0000-0000-0000-000000000602",
                "name": "Diretora",
                "role": "Diretora",
            }
        },
        format="json",
        **{**actor_headers("publicador-r", ["retificacao:publicar"]), "HTTP_IF_MATCH": '"3"'},
    )
    assert published.status_code == 201
    assert Publicacao.objects.filter(edital=edital).count() == 2
    assert list(
        Publicacao.objects.filter(edital=edital)
        .order_by("publication_order")
        .values_list("publication_order", flat=True)
    ) == [1, 2]
    assert VersaoConsolidada.objects.filter(edital=edital).count() >= 2
    assert (
        VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content["title"]
        == "Título retificado"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_stale_retification_revision_is_rejected(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    payload = {
        "baseSnapshotId": str(base.id),
        "justification": "Correção",
        "changes": [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Novo"}],
    }
    created = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        payload,
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"]),
    )
    retificacao_id = created.data["id"]
    headers = actor_headers("retificador", ["retificacao:elaborar"], if_match=1)
    assert (
        api_client.put(
            f"/api/v1/admin/retificacoes/{retificacao_id}/rascunho",
            payload,
            format="json",
            **headers,
        ).status_code
        == 200
    )
    assert (
        api_client.put(
            f"/api/v1/admin/retificacoes/{retificacao_id}/rascunho",
            payload,
            format="json",
            **headers,
        ).status_code
        == 412
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_consolidated_version_is_append_only_on_postgresql(
    api_client, manager_headers, process_payload
):
    if connection.vendor != "postgresql":
        pytest.skip("Invariante de infraestrutura PostgreSQL")
    edital = publish_original(api_client, manager_headers, process_payload)
    version = VersaoConsolidada.objects.get(edital=edital)
    with pytest.raises(DatabaseError):
        VersaoConsolidada.objects.filter(pk=version.pk).update(content={"changed": True})


def create_retification(
    api_client,
    edital,
    base,
    changes,
    *,
    subject="retificador",
    effective_at=None,
    key="retificacao-chave-k1",
):
    payload = {
        "baseSnapshotId": str(base.id),
        "justification": "Correção",
        "changes": changes,
    }
    if effective_at:
        payload["effectiveAt"] = effective_at
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        payload,
        format="json",
        **actor_headers(subject, ["retificacao:elaborar"], key=key),
    )


def homologate_and_publish(
    api_client,
    retificacao_id,
    *,
    suffix,
    authority="00000000-0000-0000-0000-000000000602",
    key="retificacao-chave-k1",
):
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/submissoes",
        format="json",
        **actor_headers(f"retificador-{suffix}", ["retificacao:submeter"], if_match=1, key=key),
    )
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **actor_headers(f"homologador-{suffix}", ["retificacao:homologar"], if_match=2, key=key),
    )
    return api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/publicacoes",
        {"signatory": {"authorityId": authority, "name": "Diretora", "role": "Diretora"}},
        format="json",
        **actor_headers(f"publicador-{suffix}", ["retificacao:publicar"], if_match=3, key=key),
    )


def title_change(new_value, expected_previous_hash=None):
    change = {"targetPath": "/title", "operation": "REPLACE", "newValue": new_value}
    if expected_previous_hash is not None:
        change["expectedPreviousHash"] = expected_previous_hash
    return change


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_stale_expected_previous_hash_is_rejected_on_creation(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    response = create_retification(
        api_client,
        edital,
        base,
        [title_change("Novo", canonical_sha256("Conteúdo que não vigora"))],
    )
    assert response.status_code == 409
    assert response.data["code"] == "expected_hash_mismatch"
    assert "/title" in response.data["detail"]
    assert not Retificacao.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_stale_expected_previous_hash_is_rejected_on_draft_edit(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    created = create_retification(
        api_client, edital, base, [title_change("Novo", canonical_sha256(base.content["title"]))]
    )
    assert created.status_code == 201
    response = api_client.put(
        f"/api/v1/admin/retificacoes/{created.data['id']}/rascunho",
        {
            "justification": "Correção",
            "changes": [title_change("Outro", canonical_sha256("Conteúdo que não vigora"))],
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], if_match=1),
    )
    assert response.status_code == 409
    assert response.data["code"] == "expected_hash_mismatch"
    assert Retificacao.objects.get().alteracoes.get().new_value == "Novo"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retification_cannot_silently_overwrite_a_path_changed_meanwhile(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    original_hash = canonical_sha256(base.content["title"])
    first = create_retification(api_client, edital, base, [title_change("Primeiro", original_hash)])
    second = create_retification(
        api_client, edital, base, [title_change("Segundo", original_hash)], subject="retificador-b"
    )
    assert homologate_and_publish(api_client, first.data["id"], suffix="a").status_code == 201

    conflict = homologate_and_publish(api_client, second.data["id"], suffix="b")

    assert conflict.status_code == 409
    assert conflict.data["code"] == "expected_hash_mismatch"
    assert "/title" in conflict.data["detail"]
    assert Retificacao.objects.get(pk=second.data["id"]).status == Retificacao.Status.HOMOLOGADA
    assert Publicacao.objects.filter(edital=edital).count() == 2
    assert (
        VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content["title"]
        == "Primeiro"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retifications_on_independent_paths_still_compose(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    first = create_retification(
        api_client,
        edital,
        base,
        [title_change("Primeiro", canonical_sha256(base.content["title"]))],
    )
    second = create_retification(
        api_client,
        edital,
        base,
        [
            {
                "targetPath": "/description",
                "operation": "REPLACE",
                "newValue": "Descrição retificada",
                "expectedPreviousHash": canonical_sha256(base.content["description"]),
            }
        ],
        subject="retificador-b",
    )
    assert homologate_and_publish(api_client, first.data["id"], suffix="a").status_code == 201
    assert homologate_and_publish(api_client, second.data["id"], suffix="b").status_code == 201
    consolidated = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content
    assert consolidated["title"] == "Primeiro"
    assert consolidated["description"] == "Descrição retificada"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_change_without_expected_previous_hash_is_still_verified_against_its_base(
    api_client, manager_headers, process_payload
):
    """FR-002 da 003: declarar o hash é opcional; verificar não é.

    Antes desta regra, duas Retificações elaboradas sobre a mesma versão sobre o mesmo caminho
    publicavam as duas, e a última simplesmente sobrescrevia a primeira sem que ninguém fosse
    avisado de que o conteúdo já não era o que a segunda tinha à vista.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    first = create_retification(api_client, edital, base, [title_change("Primeiro")])
    second = create_retification(
        api_client, edital, base, [title_change("Segundo")], subject="retificador-b"
    )
    assert homologate_and_publish(api_client, first.data["id"], suffix="a").status_code == 201

    conflict = homologate_and_publish(api_client, second.data["id"], suffix="b")

    assert conflict.status_code == 409
    assert conflict.data["code"] == "expected_hash_mismatch"
    assert "/title" in conflict.data["detail"]
    assert Retificacao.objects.get(pk=second.data["id"]).status == Retificacao.Status.HOMOLOGADA
    assert Publicacao.objects.filter(edital=edital).count() == 2
    assert (
        VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content["title"]
        == "Primeiro"
    )


def homologate(api_client, retificacao_id, *, suffix, key="retificacao-chave-k1"):
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/submissoes",
        format="json",
        **actor_headers(f"retificador-{suffix}", ["retificacao:submeter"], if_match=1, key=key),
    )
    return api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **actor_headers(f"homologador-{suffix}", ["retificacao:homologar"], if_match=2, key=key),
    )


def devolve(api_client, retificacao_id, *, revision, reason="Conflito com a Retificação anterior"):
    return api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/devolucoes",
        {"reason": reason},
        format="json",
        **actor_headers("homologador-d", ["retificacao:homologar"], if_match=revision),
    )


def conflicting_pair(api_client, manager_headers, process_payload):
    """Duas Retificações sobre o mesmo /title; a primeira publica e a segunda é rejeitada."""
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    original_hash = canonical_sha256(base.content["title"])
    first = create_retification(api_client, edital, base, [title_change("Primeiro", original_hash)])
    second = create_retification(
        api_client, edital, base, [title_change("Segundo", original_hash)], subject="retificador-b"
    )
    assert homologate_and_publish(api_client, first.data["id"], suffix="a").status_code == 201
    assert homologate_and_publish(api_client, second.data["id"], suffix="b").status_code == 409
    return edital, second.data["id"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retification_rejected_on_publication_can_be_returned_to_drafting(
    api_client, manager_headers, process_payload
):
    _, retificacao_id = conflicting_pair(api_client, manager_headers, process_payload)

    returned = devolve(api_client, retificacao_id, revision=3)

    assert returned.status_code == 200
    assert returned.data["status"] == Retificacao.Status.EM_ELABORACAO
    item = Retificacao.objects.get(pk=retificacao_id)
    assert item.homologated_by == ""
    assert item.homologated_at is None
    assert item.homologation_reason == ""
    assert item.return_reason == "Conflito com a Retificação anterior"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_returned_retification_is_rebased_and_republished(
    api_client, manager_headers, process_payload
):
    edital, retificacao_id = conflicting_pair(api_client, manager_headers, process_payload)
    assert devolve(api_client, retificacao_id, revision=3).status_code == 200
    current = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    rebased = api_client.put(
        f"/api/v1/admin/retificacoes/{retificacao_id}/rascunho",
        {
            "baseSnapshotId": str(current.id),
            "justification": "Correção sobre a versão vigente",
            "changes": [title_change("Segundo", canonical_sha256(current.content["title"]))],
        },
        format="json",
        **actor_headers("retificador-b", ["retificacao:elaborar"], if_match=4),
    )

    assert rebased.status_code == 200
    assert Retificacao.objects.get(pk=retificacao_id).base_snapshot_id == current.id
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/submissoes",
        format="json",
        **actor_headers("retificador-b", ["retificacao:submeter"], if_match=5),
    )
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **actor_headers("homologador-c", ["retificacao:homologar"], if_match=6),
    )
    published = api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/publicacoes",
        {
            "signatory": {
                "authorityId": "00000000-0000-0000-0000-000000000602",
                "name": "Diretora",
                "role": "Diretora",
            }
        },
        format="json",
        **actor_headers("publicador-c", ["retificacao:publicar"], if_match=7),
    )

    assert published.status_code == 201
    assert (
        VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content["title"]
        == "Segundo"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_editing_a_returned_retification_without_rebasing_keeps_the_old_base(
    api_client, manager_headers, process_payload
):
    edital, retificacao_id = conflicting_pair(api_client, manager_headers, process_payload)
    assert devolve(api_client, retificacao_id, revision=3).status_code == 200
    current = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    edited = api_client.put(
        f"/api/v1/admin/retificacoes/{retificacao_id}/rascunho",
        {
            "justification": "Correção",
            "changes": [title_change("Segundo", canonical_sha256(current.content["title"]))],
        },
        format="json",
        **actor_headers("retificador-b", ["retificacao:elaborar"], if_match=4),
    )

    assert edited.status_code == 409
    assert edited.data["code"] == "expected_hash_mismatch"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_return_to_drafting_requires_reason_and_homologation_permission(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    created = create_retification(api_client, edital, base, [title_change("Novo")])
    assert homologate(api_client, created.data["id"], suffix="a").status_code == 200
    url = f"/api/v1/admin/retificacoes/{created.data['id']}/devolucoes"
    assert (
        api_client.post(
            url,
            {"reason": "  "},
            format="json",
            **actor_headers("homologador-d", ["retificacao:homologar"], if_match=3),
        ).status_code
        == 422
    )
    assert (
        api_client.post(
            url,
            {"reason": "Motivo"},
            format="json",
            **actor_headers("retificador", ["retificacao:elaborar"], if_match=3),
        ).status_code
        == 403
    )
    assert Retificacao.objects.get().status == Retificacao.Status.HOMOLOGADA


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_return_to_drafting_is_refused_for_final_and_drafting_states(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    created = create_retification(api_client, edital, base, [title_change("Novo")])
    drafting = devolve(api_client, created.data["id"], revision=1)
    assert (drafting.status_code, drafting.data["code"]) == (409, "invalid_state")
    assert homologate_and_publish(api_client, created.data["id"], suffix="a").status_code == 201
    published = devolve(api_client, created.data["id"], revision=4)
    assert (published.status_code, published.data["code"]) == (409, "invalid_state")
    assert Retificacao.objects.get().status == Retificacao.Status.PUBLICADA


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_return_from_review_records_the_previous_state_in_the_audit_trail(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    created = create_retification(api_client, edital, base, [title_change("Novo")])
    api_client.post(
        f"/api/v1/admin/retificacoes/{created.data['id']}/submissoes",
        format="json",
        **actor_headers("retificador", ["retificacao:submeter"], if_match=1),
    )
    assert devolve(api_client, created.data["id"], revision=2).status_code == 200
    event = RegistroAuditoria.objects.filter(operation="DEVOLVER").get()
    assert event.previous_state == Retificacao.Status.EM_REVISAO
    assert event.new_state == Retificacao.Status.EM_ELABORACAO
    assert event.reason == "Conflito com a Retificação anterior"
    assert event.permission == "retificacao:homologar"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_creation_without_base_snapshot_is_rejected_as_problem_details(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    response = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {"justification": "Correção", "changes": [title_change("Novo")]},
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"]),
    )
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_payload"
    assert response["Content-Type"].startswith("application/problem+json")
    assert not Retificacao.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_rebasing_a_draft_to_an_unknown_snapshot_is_rejected(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    created = create_retification(api_client, edital, base, [title_change("Novo")])
    response = api_client.put(
        f"/api/v1/admin/retificacoes/{created.data['id']}/rascunho",
        {
            "baseSnapshotId": "00000000-0000-0000-0000-0000000009ff",
            "justification": "Correção",
            "changes": [title_change("Novo")],
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], if_match=1),
    )
    assert response.status_code == 404
    assert response.data["code"] == "not_found"
    assert Retificacao.objects.get().base_snapshot_id == base.id


def add_change(path, new_value):
    return {"targetPath": path, "operation": "ADD", "newValue": new_value}


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_add_cannot_silently_overwrite_a_path_created_meanwhile(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    first = create_retification(api_client, edital, base, [add_change("/anexo", "Primeiro")])
    second = create_retification(
        api_client, edital, base, [add_change("/anexo", "Segundo")], subject="retificador-b"
    )
    assert homologate_and_publish(api_client, first.data["id"], suffix="a").status_code == 201

    conflict = homologate_and_publish(api_client, second.data["id"], suffix="b")

    assert conflict.status_code == 409
    assert conflict.data["code"] == "target_already_present"
    assert "/anexo" in conflict.data["detail"]
    assert (
        VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content["anexo"]
        == "Primeiro"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_add_over_a_path_present_in_the_base_is_rejected_on_creation(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    response = create_retification(api_client, edital, base, [add_change("/title", "Novo")])
    assert response.status_code == 409
    assert response.data["code"] == "target_already_present"
    assert not Retificacao.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_add_declaring_the_current_content_is_an_informed_overwrite(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    change = {
        **add_change("/title", "Novo"),
        "expectedPreviousHash": canonical_sha256(base.content["title"]),
    }
    created = create_retification(api_client, edital, base, [change])
    assert created.status_code == 201
    assert homologate_and_publish(api_client, created.data["id"], suffix="a").status_code == 201
    assert (
        VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content["title"]
        == "Novo"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_removing_and_recreating_the_same_path_in_one_act_is_accepted(
    api_client, manager_headers, process_payload
):
    """A precondição de cada alteração parte do conteúdo que a anterior produziu.

    Este teste usava `/schedule` inteiro — removido e recriado. Isso deixou de ser admissível
    por outro motivo: trocar a coleção de uma vez destrói a identidade dos Eventos sem endereçar
    nenhum. O que ele verifica continua sendo a cadeia de precondições dentro de um mesmo ato, e
    para isso basta um caminho sem identidade.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    created = create_retification(
        api_client,
        edital,
        base,
        [
            {"targetPath": "/title", "operation": "REMOVE"},
            add_change("/title", "Título recriado no mesmo ato"),
        ],
    )
    assert created.status_code == 201
    assert homologate_and_publish(api_client, created.data["id"], suffix="a").status_code == 201
    assert (
        VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content["title"]
        == "Título recriado no mesmo ato"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_swapping_the_whole_schedule_is_done_entity_by_entity(
    api_client, manager_headers, process_payload
):
    """Trocar o Cronograma inteiro continua possível — declarando cada entidade.

    O Cronograma recriado precisa continuar tendo Evento: a Publicação da Retificação verifica
    as mesmas invariantes estruturais da Publicação original (FR-006 da 003), e um Edital
    vigente sem nenhum Evento é erro impeditivo, não resultado admissível.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    novo_evento = {
        "id": "00000000-0000-0000-0000-000000000412",
        "type": "PROVA",
        "description": "Prova objetiva",
        "startAt": "2026-10-01T09:00:00-03:00",
        "endAt": None,
        "order": 1,
        "status": "PLANEJADO",
    }
    created = create_retification(
        api_client,
        edital,
        base,
        [
            add_change("/schedule/-", novo_evento),
            {"targetPath": caminho_evento(), "operation": "REMOVE"},
        ],
    )
    assert created.status_code == 201
    assert homologate_and_publish(api_client, created.data["id"], suffix="a").status_code == 201
    assert VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content[
        "schedule"
    ] == [novo_evento]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_replacing_a_whole_collection_wholesale_is_refused(
    api_client, manager_headers, process_payload
):
    """A recusa que substituiu o cenário anterior, dita explicitamente."""
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)

    recusa = create_retification(
        api_client, edital, base, [{"targetPath": "/schedule", "operation": "REMOVE"}]
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "invalid_change"
    assert "não endereça" in recusa.data["detail"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_transition_with_a_non_textual_reason_is_rejected_as_problem_details(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    created = create_retification(api_client, edital, base, [title_change("Novo")])
    assert homologate(api_client, created.data["id"], suffix="a").status_code == 200
    response = api_client.post(
        f"/api/v1/admin/retificacoes/{created.data['id']}/devolucoes",
        {"reason": None},
        format="json",
        **actor_headers("homologador-d", ["retificacao:homologar"], if_match=3),
    )
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_payload"
    assert response["Content-Type"].startswith("application/problem+json")
    assert Retificacao.objects.get().status == Retificacao.Status.HOMOLOGADA


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_replacing_a_path_another_act_removed_is_rejected(
    api_client, manager_headers, process_payload
):
    """O `REMOVE` publicado no intervalo esvazia o caminho que o `REPLACE` esperava encontrar.

    A composição também rejeitaria, por não haver resultado determinístico; a precondição de
    conteúdo chega antes e diz qual caminho divergiu, que é o que permite refazer o ato.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    remover = create_retification(
        api_client, edital, base, [{"targetPath": "/description", "operation": "REMOVE"}]
    )
    replacer = create_retification(
        api_client,
        edital,
        base,
        [{"targetPath": "/description", "operation": "REPLACE", "newValue": "Nova"}],
        subject="retificador-b",
    )
    assert homologate_and_publish(api_client, remover.data["id"], suffix="a").status_code == 201

    conflict = homologate_and_publish(api_client, replacer.data["id"], suffix="b")

    assert conflict.status_code == 409
    assert conflict.data["code"] == "expected_hash_mismatch"
    assert "/description" in conflict.data["detail"]
    assert Publicacao.objects.filter(edital=edital).count() == 2
    assert Retificacao.objects.get(pk=replacer.data["id"]).status == Retificacao.Status.HOMOLOGADA
    assert "description" not in (
        VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_publication_that_would_break_a_later_effective_act_is_rejected(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    future = create_retification(
        api_client,
        edital,
        base,
        [{"targetPath": "/description", "operation": "REPLACE", "newValue": "Nova"}],
        effective_at="2027-06-01T12:00:00-03:00",
    )
    remover = create_retification(
        api_client,
        edital,
        base,
        [{"targetPath": "/description", "operation": "REMOVE"}],
        subject="retificador-b",
    )
    assert homologate_and_publish(api_client, future.data["id"], suffix="a").status_code == 201

    conflict = homologate_and_publish(api_client, remover.data["id"], suffix="b")

    assert conflict.status_code == 409
    assert conflict.data["code"] == "inconsistent_consolidation"
    assert Publicacao.objects.filter(edital=edital).count() == 2
    assert (
        VersaoConsolidada.objects.filter(edital=edital)
        .latest("materialized_at")
        .content["description"]
        == "Nova"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retification_without_effective_change_is_rejected_on_creation(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    assert base.content["profiles"][0]["immediateVacancies"] == 1
    response = create_retification(
        api_client,
        edital,
        base,
        [{"targetPath": VAGAS, "operation": "REPLACE", "newValue": 1}],
    )
    assert response.status_code == 422
    assert response["Content-Type"].startswith("application/problem+json")
    assert response.data["code"] == "no_effective_change"
    assert not Retificacao.objects.exists()

    reasserting_the_title = create_retification(
        api_client,
        edital,
        base,
        [{"targetPath": "/title", "operation": "REPLACE", "newValue": base.content["title"]}],
        key="retificacao-chave-k2",
    )
    assert reasserting_the_title.status_code == 422
    assert reasserting_the_title.data["code"] == "no_effective_change"
    assert not Retificacao.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retification_emptied_before_its_publication_is_rejected_with_problem_details(
    api_client, manager_headers, process_payload
):
    """Duas Retificações concorrentes com a mesma mudança: a segunda perde o efeito.

    Regressão: antes, a segunda Publicação gerava conteúdo — e portanto PDF —
    idêntico ao da primeira e estourava IntegrityError (HTTP 500) ao inserir o
    DocumentoPublicado, em vez de recusar o ato sem efeito prático.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    changes = [{"targetPath": VAGAS, "operation": "REPLACE", "newValue": 2}]
    first = create_retification(api_client, edital, base, changes, key="retificacao-chave-k1")
    second = create_retification(api_client, edital, base, changes, key="retificacao-chave-k2")
    assert (first.status_code, second.status_code) == (201, 201)

    published = homologate_and_publish(
        api_client,
        first.data["id"],
        suffix="a",
        authority="00000000-0000-0000-0000-000000000602",
        key="retificacao-chave-k1",
    )
    assert published.status_code == 201

    emptied = homologate_and_publish(
        api_client,
        second.data["id"],
        suffix="b",
        authority="00000000-0000-0000-0000-000000000603",
        key="retificacao-chave-k2",
    )
    # A divergência de conteúdo é diagnosticada antes de o efeito ser medido: o caminho já não
    # contém o que esta Retificação tinha à vista. `no_effective_change` segue guardando a
    # elaboração, coberto por test_retification_without_effective_change_is_rejected_on_creation.
    assert emptied.status_code == 409
    assert emptied["Content-Type"].startswith("application/problem+json")
    assert emptied.data["code"] == "expected_hash_mismatch"
    assert Retificacao.objects.get(pk=second.data["id"]).status == Retificacao.Status.HOMOLOGADA
    assert Publicacao.objects.filter(edital=edital).count() == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retification_may_revert_a_previous_one_and_reproduce_the_original_document(
    api_client, manager_headers, process_payload
):
    """Reverter uma Retificação tem efeito normativo e reproduz o documento original.

    Regressão da unicidade global de `document_hash`: o PDF resultante é
    byte-a-byte igual ao da Publicação original e não pode colidir.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    original_document_hash = Publicacao.objects.get(
        edital=edital, publication_order=1
    ).documento.document_hash

    first = create_retification(
        api_client,
        edital,
        base,
        [{"targetPath": VAGAS, "operation": "REPLACE", "newValue": 2}],
        key="retificacao-chave-k1",
    )
    assert (
        homologate_and_publish(
            api_client,
            first.data["id"],
            suffix="a",
            authority="00000000-0000-0000-0000-000000000602",
            key="retificacao-chave-k1",
        ).status_code
        == 201
    )

    consolidated = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert consolidated.content["profiles"][0]["immediateVacancies"] == 2
    revert = create_retification(
        api_client,
        edital,
        consolidated,
        [{"targetPath": VAGAS, "operation": "REPLACE", "newValue": 1}],
        key="retificacao-chave-k2",
    )
    assert revert.status_code == 201
    published = homologate_and_publish(
        api_client,
        revert.data["id"],
        suffix="b",
        authority="00000000-0000-0000-0000-000000000603",
        key="retificacao-chave-k2",
    )
    assert published.status_code == 201
    assert published.data["documentHash"] == original_document_hash
    assert (
        VersaoConsolidada.objects.filter(edital=edital)
        .latest("materialized_at")
        .content["profiles"][0]["immediateVacancies"]
        == 1
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retification_changes_vacancies_and_schedule_inside_snapshot_lists(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    original = VersaoConsolidada.objects.get(edital=edital).content
    assert original["profiles"][0]["immediateVacancies"] == 1

    retify(
        api_client,
        edital,
        [
            {
                "targetPath": VAGAS,
                "operation": "REPLACE",
                "newValue": 12,
            },
            {
                "targetPath": DESCRICAO_DO_EVENTO,
                "operation": "REPLACE",
                "newValue": "Inscrições prorrogadas",
            },
        ],
    )

    consolidada = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert consolidada.content["profiles"][0]["immediateVacancies"] == 12
    assert consolidada.content["schedule"][0]["description"] == "Inscrições prorrogadas"
    assert consolidada.content["profiles"][0]["code"] == "P1"

    primeira = VersaoConsolidada.objects.filter(edital=edital).earliest("materialized_at")
    assert primeira.content["profiles"][0]["immediateVacancies"] == 1
    assert ProvenienciaConteudo.objects.filter(versao=consolidada, target_path=VAGAS).count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retification_with_future_effective_date_materializes_version_at_that_boundary(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    vigencia = timezone.now() + timedelta(days=30)

    retify(
        api_client,
        edital,
        [{"targetPath": VAGAS, "operation": "REPLACE", "newValue": 40}],
        effective_at=vigencia.isoformat(),
    )

    retificada = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert retificada.valid_from == vigencia
    assert retificada.content["profiles"][0]["immediateVacancies"] == 40

    vigente_hoje = (
        VersaoConsolidada.objects.filter(edital=edital, valid_from__lte=timezone.now())
        .order_by("-valid_from")
        .first()
    )
    assert vigente_hoje.content["profiles"][0]["immediateVacancies"] == 1


PERFIS_DA_TRINCA = [f"/profiles/id=00000000-0000-0000-0000-00000000050{n}" for n in (1, 2, 3)]


def draft_com_tres_perfis(nomes=("Perfil 1", "Perfil 2", "Perfil 3")):
    """Três Perfis, para que remover um mexa na composição da lista."""
    from tests.fixtures.edital import complete_draft

    draft = complete_draft()
    modelo = draft["profiles"][0]
    draft["profiles"] = [
        {
            **modelo,
            "id": f"00000000-0000-0000-0000-00000000050{numero}",
            "code": f"P{numero}",
            "name": nome,
        }
        for numero, nome in enumerate(nomes, 1)
    ]
    return draft


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_removing_the_addressed_profile_is_key_not_found_and_not_a_silent_hit(
    api_client, manager_headers, process_payload
):
    """A recusa que passou a valer no lugar de `target_identity_mismatch`.

    A `003` recusava aqui porque o índice deslocava e a âncora acusava. Agora o índice não
    existe mais, e só sobra a pergunta que interessa: a entidade endereçada ainda está lá? Não
    está — outra Retificação a removeu —, e a resposta é `target_key_not_found`.

    Os dois últimos Perfis têm a **mesma denominação** de propósito. Era esse par que tornava o
    hash incapaz de distinguir as entidades depois do deslocamento, e é o que torna o teste
    honesto: o que recusa não é o conteúdo, é a ausência da entidade.
    """
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=draft_com_tres_perfis(("Perfil 1", "Mesma denominação", "Mesma denominação")),
    )
    base = VersaoConsolidada.objects.get(edital=edital)
    renomear_o_segundo = create_retification(
        api_client,
        edital,
        base,
        [{"targetPath": f"{PERFIS_DA_TRINCA[1]}/name", "operation": "REPLACE", "newValue": "X"}],
        subject="retificador-b",
        key="retificacao-chave-k2",
    )
    remover_o_segundo = create_retification(
        api_client, edital, base, [{"targetPath": PERFIS_DA_TRINCA[1], "operation": "REMOVE"}]
    )
    assert (
        homologate_and_publish(api_client, remover_o_segundo.data["id"], suffix="a").status_code
        == 201
    )

    conflict = homologate_and_publish(
        api_client,
        renomear_o_segundo.data["id"],
        suffix="b",
        authority="00000000-0000-0000-0000-000000000603",
        key="retificacao-chave-k2",
    )

    assert conflict.status_code == 409
    assert conflict.data["code"] == "target_key_not_found"
    assert PERFIS_DA_TRINCA[1] in conflict.data["detail"]
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert [perfil["code"] for perfil in vigente.content["profiles"]] == ["P1", "P3"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_an_unrelated_removal_no_longer_defeats_a_retification(
    api_client, manager_headers, process_payload
):
    """O ganho que a `003` não podia entregar: as duas publicam.

    Mesmo Edital, mesma versão base, Perfis diferentes. Antes, remover o Perfil 1 deslocava os
    índices e a Retificação sobre o Perfil 2 era recusada — mesmo sem ninguém ter tocado nela.
    """
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=draft_com_tres_perfis(("Perfil 1", "Mesma denominação", "Mesma denominação")),
    )
    base = VersaoConsolidada.objects.get(edital=edital)
    renomear_o_segundo = create_retification(
        api_client,
        edital,
        base,
        [
            {
                "targetPath": f"{PERFIS_DA_TRINCA[1]}/name",
                "operation": "REPLACE",
                "newValue": "RENOMEADO",
            }
        ],
        subject="retificador-b",
        key="retificacao-chave-k2",
    )
    remover_o_primeiro = create_retification(
        api_client, edital, base, [{"targetPath": PERFIS_DA_TRINCA[0], "operation": "REMOVE"}]
    )
    assert (
        homologate_and_publish(api_client, remover_o_primeiro.data["id"], suffix="a").status_code
        == 201
    )

    publicada = homologate_and_publish(
        api_client,
        renomear_o_segundo.data["id"],
        suffix="b",
        authority="00000000-0000-0000-0000-000000000603",
        key="retificacao-chave-k2",
    )

    assert publicada.status_code == 201, publicada.content
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert [perfil["code"] for perfil in vigente.content["profiles"]] == ["P2", "P3"]
    assert [perfil["name"] for perfil in vigente.content["profiles"]] == [
        "RENOMEADO",
        "Mesma denominação",
    ]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retification_cannot_leave_a_structurally_invalid_edital(
    api_client, manager_headers, process_payload
):
    """FR-006 da 003: as invariantes da Publicação valem para o que a Retificação faz vigorar.

    A garantia é a mesma; o momento mudou. Este teste levava o ato até a Publicação, porque a
    elaboração não olhava o resultado. Desde a `005` ela olha, e o ato que removeria o único Perfil
    é recusado antes de existir — recusa mais cedo, mesma proteção.

    O portão da Publicação continua provado, com o ato gravado direto, em
    `test_integridade_publicacao.py`: é a linha que chega por fora da elaboração.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)

    refused = create_retification(
        api_client, edital, base, [{"targetPath": PERFIL_UNICO, "operation": "REMOVE"}]
    )

    assert refused.status_code == 422, refused.content
    assert refused.data["code"] == "blocking_findings"
    assert "Perfil" in refused.data["detail"]
    # Recusar na borda não pode deixar rastro: o ato não chega a existir.
    assert not Retificacao.objects.filter(edital=edital).exists()
    assert Publicacao.objects.filter(edital=edital).count() == 1
    assert VersaoConsolidada.objects.filter(edital=edital).count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_repeating_the_idempotency_key_does_not_create_a_second_retification(
    api_client, manager_headers, process_payload
):
    """FR-013 da 003: o contrato exigia a chave; os endpoints da Retificação a ignoravam."""
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)

    first = create_retification(api_client, edital, base, [title_change("Novo")])
    repeated = create_retification(api_client, edital, base, [title_change("Novo")])

    assert first.status_code == 201
    assert repeated.status_code == 201
    assert repeated.data["id"] == first.data["id"]
    assert Retificacao.objects.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_same_idempotency_key_with_another_body_is_refused(
    api_client, manager_headers, process_payload
):
    """FR-014 da 003."""
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    create_retification(api_client, edital, base, [title_change("Novo")])

    conflict = create_retification(api_client, edital, base, [title_change("Outro")])

    assert conflict.status_code == 409
    assert conflict.data["code"] == "idempotency_conflict"
    assert Retificacao.objects.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retification_audit_records_correlation_and_idempotency(
    api_client, manager_headers, process_payload
):
    """FR-015 da 003: os atos de Retificação gravavam `correlation_id` vazio."""
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    created = create_retification(api_client, edital, base, [title_change("Novo")])
    assert homologate_and_publish(api_client, created.data["id"], suffix="a").status_code == 201

    registros = RegistroAuditoria.objects.filter(aggregate_type="Retificacao")
    assert registros.exists()
    assert not registros.filter(correlation_id="").exists()
    assert not registros.filter(idempotency_key="").exists()
    assert {registro.operation for registro in registros} == {
        "CRIAR",
        "SUBMETER",
        "HOMOLOGAR",
        "PUBLICAR",
    }


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_positional_add_is_refused_when_the_act_is_elaborated(
    api_client, manager_headers, process_payload
):
    """A `003` recusava na Publicação o `ADD` cuja posição tinha deslocado. Agora ele não nasce.

    Inserir "antes do Perfil 2" era ato distinto de inserir depois dele, e a única forma de
    dizê-lo era por índice — que desloca. A gramática deixou de admitir a forma: acréscimo é ao
    fim, e endereçar `/profiles/1` é recusado na elaboração, com 422 (FR-006, FR-007).
    """
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=draft_com_tres_perfis()
    )
    base = VersaoConsolidada.objects.get(edital=edital)
    novo_perfil = {
        **base.content["profiles"][0],
        "id": "00000000-0000-0000-0000-000000000599",
        "code": "PX",
        "name": "Perfil acrescentado",
    }

    recusa = create_retification(
        api_client,
        edital,
        base,
        [{"targetPath": "/profiles/1", "operation": "ADD", "newValue": novo_perfil}],
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "positional_addressing_refused"
    assert "/profiles/1" in recusa.data["detail"]
    assert not Retificacao.objects.filter(edital=edital).exists(), (
        "um ato que nasce instável não deve chegar a existir"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_appending_at_the_end_survives_an_unrelated_removal(
    api_client, manager_headers, process_payload
):
    """A recíproca: acrescentar ao fim é estável e não pode virar recusa."""
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=draft_com_tres_perfis()
    )
    base = VersaoConsolidada.objects.get(edital=edital)
    novo = {
        **base.content["profiles"][0],
        "id": "00000000-0000-0000-0000-000000000598",
        "code": "PX",
        "name": "Perfil acrescentado",
    }
    acrescentar = create_retification(
        api_client,
        edital,
        base,
        [{"targetPath": "/profiles/-", "operation": "ADD", "newValue": novo}],
        subject="retificador-b",
        key="retificacao-chave-k2",
    )
    remover_o_primeiro = create_retification(
        api_client, edital, base, [{"targetPath": PERFIS_DA_TRINCA[0], "operation": "REMOVE"}]
    )
    assert (
        homologate_and_publish(api_client, remover_o_primeiro.data["id"], suffix="a").status_code
        == 201
    )

    publicada = homologate_and_publish(
        api_client,
        acrescentar.data["id"],
        suffix="b",
        authority="00000000-0000-0000-0000-000000000603",
        key="retificacao-chave-k2",
    )

    assert publicada.status_code == 201, publicada.content
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert [perfil["code"] for perfil in vigente.content["profiles"]] == ["P2", "P3", "PX"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_change_without_any_precondition_cannot_be_published(
    api_client, manager_headers, process_payload
):
    """FR-002c da 003: linha sem precondição de conteúdo não volta a publicar às cegas.

    Este é o cinto para a linha que chegue por fora da elaboração — restaurada de backup, criada
    por importação: publicar é recusado e o caminho de volta é devolver e reenviar o rascunho,
    que reconstrói a precondição.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    created = create_retification(api_client, edital, base, [title_change("Novo")])
    AlteracaoNormativa.objects.filter(retificacao_id=created.data["id"]).update(
        expected_previous_hash=""
    )

    refused = homologate_and_publish(api_client, created.data["id"], suffix="a")

    assert refused.status_code == 409
    assert refused.data["code"] == "precondition_missing"
    assert "/title" in refused.data["detail"]
    assert Publicacao.objects.filter(edital=edital).count() == 1


def repetir(api_client, url, corpo, *, subject, permissao, revision, key, suffix=""):
    """Envia duas vezes a mesma requisição, com a mesma chave, e devolve as duas respostas."""
    headers = actor_headers(f"{subject}{suffix}", [permissao], if_match=revision, key=key)
    primeira = api_client.post(url, corpo, format="json", **headers)
    segunda = api_client.post(url, corpo, format="json", **headers)
    return primeira, segunda


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_every_retification_act_replays_with_its_documented_status(
    api_client, manager_headers, process_payload
):
    """FR-013 da 003: as seis operações honram a chave, não só a criação.

    A repetição não pratica um segundo ato e responde com o status documentado no contrato para
    aquela operação — a mesma resposta que o cliente perdeu, e não um código alternativo.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    criada = create_retification(api_client, edital, base, [title_change("Novo")])
    assert criada.status_code == 201
    identificador = criada.data["id"]
    raiz = f"/api/v1/admin/retificacoes/{identificador}"

    submetida, submetida_repetida = repetir(
        api_client,
        f"{raiz}/submissoes",
        {},
        subject="retificador",
        permissao="retificacao:submeter",
        revision=1,
        key="repeticao-submissao-01",
    )
    assert (submetida.status_code, submetida_repetida.status_code) == (200, 200)
    assert submetida_repetida.data["status"] == Retificacao.Status.EM_REVISAO

    devolvida, devolvida_repetida = repetir(
        api_client,
        f"{raiz}/devolucoes",
        {"reason": "Corrigir a justificativa"},
        subject="homologador",
        permissao="retificacao:homologar",
        revision=2,
        key="repeticao-devolucao-01",
    )
    assert (devolvida.status_code, devolvida_repetida.status_code) == (200, 200)
    assert devolvida_repetida.data["status"] == Retificacao.Status.EM_ELABORACAO

    api_client.post(
        f"{raiz}/submissoes",
        {},
        format="json",
        **actor_headers(
            "retificador", ["retificacao:submeter"], if_match=3, key="repeticao-submissao-02"
        ),
    )
    homologada, homologada_repetida = repetir(
        api_client,
        f"{raiz}/homologacoes",
        {"reason": "OK"},
        subject="homologador",
        permissao="retificacao:homologar",
        revision=4,
        key="repeticao-homologacao-01",
    )
    assert (homologada.status_code, homologada_repetida.status_code) == (200, 200)

    publicada, publicada_repetida = repetir(
        api_client,
        f"{raiz}/publicacoes",
        {"signatory": SIGNATORY},
        subject="publicador",
        permissao="retificacao:publicar",
        revision=5,
        key="repeticao-publicacao-01",
    )
    assert (publicada.status_code, publicada_repetida.status_code) == (201, 201)
    assert publicada_repetida.data["id"] == publicada.data["id"]
    assert Publicacao.objects.filter(edital=edital).count() == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cancelling_a_retification_replays_without_a_second_act(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    criada = create_retification(api_client, edital, base, [title_change("Novo")])

    primeira, segunda = repetir(
        api_client,
        f"/api/v1/admin/retificacoes/{criada.data['id']}/cancelamentos",
        {"reason": "Desnecessária"},
        subject="cancelador",
        permissao="retificacao:cancelar",
        revision=1,
        key="repeticao-cancelamento-01",
    )

    assert (primeira.status_code, segunda.status_code) == (200, 200)
    assert segunda.data["status"] == Retificacao.Status.CANCELADA
    assert (
        RegistroAuditoria.objects.filter(aggregate_type="Retificacao", operation="CANCELAR").count()
        == 1
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_the_key_alone_does_not_authorize_a_replace(api_client, manager_headers, process_payload):
    """FR-014: a precondição por hash não saiu junto com a âncora, porque responde a outra coisa.

    O caminho por chave garante que ainda se fala da mesma entidade. Não diz nada sobre o
    conteúdo dela: se outra Retificação alterou o mesmo campo do mesmo Perfil, a entidade
    continua sendo aquela e o caminho resolve normalmente. Sem exigir também o hash, este ato
    sobrescreveria a alteração concorrente em silêncio — o caso que a FR-036 existe para impedir.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    alvo = caminho_perfil("name")
    concorrente = create_retification(
        api_client,
        edital,
        base,
        [{"targetPath": alvo, "operation": "REPLACE", "newValue": "Alterado por outra"}],
    )
    assert homologate_and_publish(api_client, concorrente.data["id"], suffix="a").status_code == 201

    sem_hash = create_retification(
        api_client,
        edital,
        VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at"),
        [{"targetPath": alvo, "operation": "REPLACE", "newValue": "Alterado por esta"}],
        subject="retificador-b",
        key="retificacao-chave-k2",
    )
    alteracao = AlteracaoNormativa.objects.get(retificacao_id=sem_hash.data["id"])
    assert "id=" in alteracao.target_path, "o caminho nomeia a entidade, que é o que sobra sem hash"
    AlteracaoNormativa.objects.filter(pk=alteracao.pk).update(expected_previous_hash="")

    refused = homologate_and_publish(
        api_client,
        sem_hash.data["id"],
        suffix="b",
        authority="00000000-0000-0000-0000-000000000603",
        key="retificacao-chave-k2",
    )

    assert refused.status_code == 409
    assert refused.data["code"] == "precondition_missing"
    assert alvo in refused.data["detail"]
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert vigente.content["profiles"][0]["name"] == "Alterado por outra"
