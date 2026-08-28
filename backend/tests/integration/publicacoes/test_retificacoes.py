from datetime import timedelta

import pytest
from django.db import DatabaseError, connection
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import (
    ProvenienciaConteudo,
    Retificacao,
    VersaoConsolidada,
)
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import publish_original, retify


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
    api_client, edital, base, changes, *, subject="retificador", effective_at=None, key="k1"
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
    key="k1",
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
        **actor_headers(
            f"homologador-{suffix}", ["retificacao:homologar"], if_match=2, key=key
        ),
    )
    return api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/publicacoes",
        {
            "signatory": {"authorityId": authority, "name": "Diretora", "role": "Diretora"}
        },
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
def test_change_without_expected_previous_hash_keeps_last_publication_winning(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    first = create_retification(api_client, edital, base, [title_change("Primeiro")])
    second = create_retification(
        api_client, edital, base, [title_change("Segundo")], subject="retificador-b"
    )
    assert homologate_and_publish(api_client, first.data["id"], suffix="a").status_code == 201
    assert homologate_and_publish(api_client, second.data["id"], suffix="b").status_code == 201
    assert (
        VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content["title"]
        == "Segundo"
    )


def homologate(api_client, retificacao_id, *, suffix, key="k1"):
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/submissoes",
        format="json",
        **actor_headers(f"retificador-{suffix}", ["retificacao:submeter"], if_match=1, key=key),
    )
    return api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **actor_headers(
            f"homologador-{suffix}", ["retificacao:homologar"], if_match=2, key=key
        ),
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
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    created = create_retification(
        api_client,
        edital,
        base,
        [
            {"targetPath": "/schedule", "operation": "REMOVE"},
            add_change("/schedule", []),
        ],
    )
    assert created.status_code == 201
    assert homologate_and_publish(api_client, created.data["id"], suffix="a").status_code == 201
    assert (
        VersaoConsolidada.objects.filter(edital=edital)
        .latest("materialized_at")
        .content["schedule"]
        == []
    )


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
def test_publication_that_would_break_the_consolidation_is_rejected(
    api_client, manager_headers, process_payload
):
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
    assert conflict.data["code"] == "inconsistent_consolidation"
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
        [{"targetPath": "/profiles/0/immediateVacancies", "operation": "REPLACE", "newValue": 1}],
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
        key="k2",
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
    changes = [
        {"targetPath": "/profiles/0/immediateVacancies", "operation": "REPLACE", "newValue": 2}
    ]
    first = create_retification(api_client, edital, base, changes, key="k1")
    second = create_retification(api_client, edital, base, changes, key="k2")
    assert (first.status_code, second.status_code) == (201, 201)

    published = homologate_and_publish(
        api_client,
        first.data["id"],
        suffix="a",
        authority="00000000-0000-0000-0000-000000000602",
        key="k1",
    )
    assert published.status_code == 201

    emptied = homologate_and_publish(
        api_client,
        second.data["id"],
        suffix="b",
        authority="00000000-0000-0000-0000-000000000603",
        key="k2",
    )
    assert emptied.status_code == 422
    assert emptied["Content-Type"].startswith("application/problem+json")
    assert emptied.data["code"] == "no_effective_change"
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
        [{"targetPath": "/profiles/0/immediateVacancies", "operation": "REPLACE", "newValue": 2}],
        key="k1",
    )
    assert (
        homologate_and_publish(
            api_client,
            first.data["id"],
            suffix="a",
            authority="00000000-0000-0000-0000-000000000602",
            key="k1",
        ).status_code
        == 201
    )

    consolidated = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert consolidated.content["profiles"][0]["immediateVacancies"] == 2
    revert = create_retification(
        api_client,
        edital,
        consolidated,
        [{"targetPath": "/profiles/0/immediateVacancies", "operation": "REPLACE", "newValue": 1}],
        key="k2",
    )
    assert revert.status_code == 201
    published = homologate_and_publish(
        api_client,
        revert.data["id"],
        suffix="b",
        authority="00000000-0000-0000-0000-000000000603",
        key="k2",
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
                "targetPath": "/profiles/0/immediateVacancies",
                "operation": "REPLACE",
                "newValue": 12,
            },
            {
                "targetPath": "/schedule/0/description",
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
    assert (
        ProvenienciaConteudo.objects.filter(
            versao=consolidada, target_path="/profiles/0/immediateVacancies"
        ).count()
        == 1
    )

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
        [{"targetPath": "/profiles/0/immediateVacancies", "operation": "REPLACE", "newValue": 40}],
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
