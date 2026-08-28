import pytest

from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers, complete_draft


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_one_actor_cannot_prepare_homologate_and_publish(
    api_client, manager_headers, process_payload
):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    actor = actor_headers(
        "actor-a", ["edital:elaborar", "edital:submeter", "edital:homologar", "edital:publicar"]
    )
    assert (
        api_client.put(
            f"/api/v1/admin/editais/{edital.id}/rascunho",
            complete_draft(),
            format="json",
            **{**actor, "HTTP_IF_MATCH": '"1"'},
        ).status_code
        == 200
    )
    assert (
        api_client.post(
            f"/api/v1/admin/editais/{edital.id}/submissoes",
            format="json",
            **{**actor, "HTTP_IF_MATCH": '"2"'},
        ).status_code
        == 200
    )
    assert (
        api_client.post(
            f"/api/v1/admin/editais/{edital.id}/homologacoes",
            {"reason": "Conferido"},
            format="json",
            **{**actor, "HTTP_IF_MATCH": '"3"'},
        ).status_code
        == 200
    )
    denied = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {
            "signatory": {
                "authorityId": "00000000-0000-0000-0000-000000000499",
                "name": "Autoridade",
                "role": "Diretor",
            }
        },
        format="json",
        **{**actor, "HTTP_IF_MATCH": '"4"'},
    )
    assert denied.status_code == 403
