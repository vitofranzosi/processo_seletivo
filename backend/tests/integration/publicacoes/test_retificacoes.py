import pytest
from django.db import DatabaseError, connection

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.edital import actor_headers, complete_draft


def publish_original(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    preparer = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**preparer, "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparer, "HTTP_IF_MATCH": '"2"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{**actor_headers("homologador", ["edital:homologar"]), "HTTP_IF_MATCH": '"3"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {
            "signatory": {
                "authorityId": "00000000-0000-0000-0000-000000000601",
                "name": "Diretora",
                "role": "Diretora",
            }
        },
        format="json",
        **{**actor_headers("publicador", ["edital:publicar"]), "HTTP_IF_MATCH": '"4"'},
    )
    return Edital.objects.get(pk=edital.pk)


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


def create_retification(api_client, edital, base, changes, *, subject="retificador"):
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Correção",
            "changes": changes,
        },
        format="json",
        **actor_headers(subject, ["retificacao:elaborar"]),
    )


def homologate_and_publish(api_client, retificacao_id, *, suffix):
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/submissoes",
        format="json",
        **actor_headers(f"retificador-{suffix}", ["retificacao:submeter"], if_match=1),
    )
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **actor_headers(f"homologador-{suffix}", ["retificacao:homologar"], if_match=2),
    )
    return api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/publicacoes",
        {
            "signatory": {
                "authorityId": "00000000-0000-0000-0000-000000000602",
                "name": "Diretora",
                "role": "Diretora",
            }
        },
        format="json",
        **actor_headers(f"publicador-{suffix}", ["retificacao:publicar"], if_match=3),
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


def homologate(api_client, retificacao_id, *, suffix):
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/submissoes",
        format="json",
        **actor_headers(f"retificador-{suffix}", ["retificacao:submeter"], if_match=1),
    )
    return api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **actor_headers(f"homologador-{suffix}", ["retificacao:homologar"], if_match=2),
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
    assert response.status_code == 400
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
