import pytest

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import Publicacao
from tests.fixtures.edital import actor_headers, complete_draft


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us4_complete_publication_flow(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    preparer = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    homologator = actor_headers("homologador", ["edital:homologar"])
    publisher = actor_headers("publicador", ["edital:publicar"])
    assert (
        api_client.put(
            f"/api/v1/admin/editais/{edital.id}/rascunho",
            complete_draft(),
            format="json",
            **{**preparer, "HTTP_IF_MATCH": '"1"'},
        ).status_code
        == 200
    )
    assert (
        api_client.post(
            f"/api/v1/admin/editais/{edital.id}/submissoes",
            format="json",
            **{**preparer, "HTTP_IF_MATCH": '"2"'},
        ).status_code
        == 200
    )
    assert (
        api_client.post(
            f"/api/v1/admin/editais/{edital.id}/homologacoes",
            {"reason": "Aprovado"},
            format="json",
            **{**homologator, "HTTP_IF_MATCH": '"3"'},
        ).status_code
        == 200
    )
    published = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {
            "signatory": {
                "authorityId": "00000000-0000-0000-0000-000000000496",
                "name": "Diretora",
                "role": "Diretora-Geral",
            }
        },
        format="json",
        **{**publisher, "HTTP_IF_MATCH": '"4"'},
    )
    assert published.status_code == 201
    assert Edital.objects.get().status == Edital.Status.PUBLICADO
    publication = Publicacao.objects.get()
    assert published.json()["contentHash"] == publication.content_hash
    assert published["Location"].endswith(str(publication.id))
