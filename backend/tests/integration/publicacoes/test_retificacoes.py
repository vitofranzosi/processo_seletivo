import pytest
from django.db import DatabaseError, connection

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
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


def create_retification(api_client, edital, base, changes, *, subject="retificador", key="k1"):
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Correção",
            "changes": changes,
        },
        format="json",
        **actor_headers(subject, ["retificacao:elaborar"], key=key),
    )


def publish_retification(api_client, retificacao_id, *, suffix, authority, key="k1"):
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/submissoes",
        format="json",
        **{
            **actor_headers(f"retificador{suffix}", ["retificacao:submeter"], key=key),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{
            **actor_headers(f"homologador{suffix}", ["retificacao:homologar"], key=key),
            "HTTP_IF_MATCH": '"2"',
        },
    )
    return api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao_id}/publicacoes",
        {"signatory": {"authorityId": authority, "name": "Diretora", "role": "Diretora"}},
        format="json",
        **{
            **actor_headers(f"publicador{suffix}", ["retificacao:publicar"], key=key),
            "HTTP_IF_MATCH": '"3"',
        },
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

    published = publish_retification(
        api_client,
        first.data["id"],
        suffix="-a",
        authority="00000000-0000-0000-0000-000000000602",
        key="k1",
    )
    assert published.status_code == 201

    emptied = publish_retification(
        api_client,
        second.data["id"],
        suffix="-b",
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
        publish_retification(
            api_client,
            first.data["id"],
            suffix="-a",
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
    published = publish_retification(
        api_client,
        revert.data["id"],
        suffix="-b",
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
def test_consolidated_version_is_append_only_on_postgresql(
    api_client, manager_headers, process_payload
):
    if connection.vendor != "postgresql":
        pytest.skip("Invariante de infraestrutura PostgreSQL")
    edital = publish_original(api_client, manager_headers, process_payload)
    version = VersaoConsolidada.objects.get(edital=edital)
    with pytest.raises(DatabaseError):
        VersaoConsolidada.objects.filter(pk=version.pk).update(content={"changed": True})
