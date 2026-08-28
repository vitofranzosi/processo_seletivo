from concurrent.futures import ThreadPoolExecutor

import pytest
from django.db import DatabaseError, close_old_connections, connection
from rest_framework.test import APIClient

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from tests.fixtures.edital import actor_headers, complete_draft


def prepare_homologated(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    prepared = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    homologator = actor_headers("homologador", ["edital:homologar"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**prepared, "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**prepared, "HTTP_IF_MATCH": '"2"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "Conferido"},
        format="json",
        **{**homologator, "HTTP_IF_MATCH": '"3"'},
    )
    return edital


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_publication_is_atomic_and_idempotent(api_client, manager_headers, process_payload):
    edital = prepare_homologated(api_client, manager_headers, process_payload)
    publisher = actor_headers("publicador", ["edital:publicar"], if_match=4)
    payload = {
        "signatory": {
            "authorityId": "00000000-0000-0000-0000-000000000498",
            "name": "Autoridade",
            "role": "Diretor",
        }
    }
    first = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes", payload, format="json", **publisher
    )
    replay = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes", payload, format="json", **publisher
    )
    assert first.status_code == 201
    assert replay.status_code == 200
    assert Publicacao.objects.count() == DocumentoPublicado.objects.count() == 1
    document = DocumentoPublicado.objects.get()
    assert document.bytes.startswith(b"%PDF-")


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_database_trigger_rejects_publication_update(api_client, manager_headers, process_payload):
    if connection.vendor != "postgresql":
        pytest.skip("trigger validado somente no PostgreSQL")
    edital = prepare_homologated(api_client, manager_headers, process_payload)
    payload = {
        "signatory": {
            "authorityId": "00000000-0000-0000-0000-000000000497",
            "name": "Autoridade",
            "role": "Diretor",
        }
    }
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        payload,
        format="json",
        **actor_headers("publicador", ["edital:publicar"], if_match=4),
    )
    with pytest.raises(DatabaseError):
        Publicacao.objects.update(content_hash="0" * 64)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_pdf_failure_rolls_back_entire_publication(
    api_client, manager_headers, process_payload, monkeypatch
):
    edital = prepare_homologated(api_client, manager_headers, process_payload)

    def fail_pdf(*args, **kwargs):
        raise RuntimeError("renderer failure")

    monkeypatch.setattr(
        "processo_seletivo.publicacoes.application.publish_edital.render_edital_pdf", fail_pdf
    )
    payload = {
        "signatory": {
            "authorityId": "00000000-0000-0000-0000-000000000495",
            "name": "Autoridade",
            "role": "Diretor",
        }
    }
    with pytest.raises(RuntimeError):
        api_client.post(
            f"/api/v1/admin/editais/{edital.id}/publicacoes",
            payload,
            format="json",
            **actor_headers("publicador", ["edital:publicar"], if_match=4),
        )
    assert Publicacao.objects.count() == DocumentoPublicado.objects.count() == 0
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.HOMOLOGADO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_concurrent_publications_create_exactly_one(api_client, manager_headers, process_payload):
    if connection.vendor != "postgresql":
        pytest.skip("concorrência validada somente no PostgreSQL")
    edital = prepare_homologated(api_client, manager_headers, process_payload)
    payload = {
        "signatory": {
            "authorityId": "00000000-0000-0000-0000-000000000494",
            "name": "Autoridade",
            "role": "Diretor",
        }
    }

    def publish(index):
        close_old_connections()
        client = APIClient()
        response = client.post(
            f"/api/v1/admin/editais/{edital.id}/publicacoes",
            payload,
            format="json",
            **actor_headers(
                f"publicador-{index}",
                ["edital:publicar"],
                if_match=4,
                key=f"concurrent-publication-{index}",
            ),
        )
        close_old_connections()
        return response.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(publish, [1, 2]))
    assert sorted(statuses) == [201, 409]
    assert Publicacao.objects.count() == DocumentoPublicado.objects.count() == 1
