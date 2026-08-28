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
