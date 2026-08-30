import pytest

from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import publish_original, retify

VACANCIES = "/profiles/0/immediateVacancies"


@pytest.fixture
def edital_publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.mark.django_db
@pytest.mark.contract
def test_effective_version_matches_contract(api_client, edital_publicado):
    response = api_client.get(f"/api/v1/public/editais/{edital_publicado.id}/versao-vigente")
    assert response.status_code == 200
    body = response.json()
    assert {"id", "editalId", "validFrom", "contentHash", "content", "appliedPublications"} <= set(
        body
    )
    assert body["editalId"] == str(edital_publicado.id)
    assert body["content"]["profiles"][0]["code"] == "P1"
    assert response["ETag"] == f'"{body["contentHash"]}"'
    assert "max-age" in response["Cache-Control"]


@pytest.mark.django_db
@pytest.mark.contract
def test_effective_version_returns_problem_when_no_version_was_in_force(
    api_client, edital_publicado
):
    response = api_client.get(
        f"/api/v1/public/editais/{edital_publicado.id}/versao-vigente",
        {"em": "2020-01-01T00:00:00-03:00"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "no_effective_version"


@pytest.mark.django_db
@pytest.mark.contract
def test_effective_version_rejects_unparseable_instant(api_client, edital_publicado):
    response = api_client.get(
        f"/api/v1/public/editais/{edital_publicado.id}/versao-vigente", {"em": "ontem"}
    )
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_instant"


@pytest.mark.django_db
@pytest.mark.contract
def test_effective_version_answers_304_for_known_etag(api_client, edital_publicado):
    url = f"/api/v1/public/editais/{edital_publicado.id}/versao-vigente"
    etag = api_client.get(url)["ETag"]
    assert api_client.get(url, HTTP_IF_NONE_MATCH=etag).status_code == 304


@pytest.mark.django_db
@pytest.mark.contract
def test_publication_detail_matches_contract(api_client, edital_publicado):
    publicacao = Publicacao.objects.get(edital=edital_publicado)
    response = api_client.get(f"/api/v1/public/publicacoes/{publicacao.id}")
    assert response.status_code == 200
    body = response.json()
    assert {
        "id",
        "editalId",
        "publicationOrder",
        "publishedAt",
        "effectiveAt",
        "contentHash",
        "documentHash",
        "sourceType",
        "sourceId",
        "signatory",
        "content",
        "documentUrl",
    } <= set(body)
    assert body["sourceType"] == "EDITAL"
    assert body["sourceId"] == str(edital_publicado.id)
    assert body["signatory"]["role"] == "Diretora-Geral"
    assert body["documentUrl"] == f"/api/v1/public/publicacoes/{publicacao.id}/documento"
    assert "immutable" in response["Cache-Control"]


@pytest.mark.django_db
@pytest.mark.contract
def test_published_retification_matches_contract(api_client, edital_publicado):
    retificacao = retify(
        api_client,
        edital_publicado,
        [{"targetPath": VACANCIES, "operation": "REPLACE", "newValue": 7}],
    )
    response = api_client.get(f"/api/v1/public/retificacoes/{retificacao.id}")
    assert response.status_code == 200
    body = response.json()
    assert {
        "id",
        "editalId",
        "publicationId",
        "justification",
        "publishedAt",
        "effectiveAt",
        "changes",
    } <= set(body)
    assert body["changes"] == [
        {"targetPath": VACANCIES, "operation": "REPLACE", "newValue": 7},
    ]


@pytest.mark.django_db
@pytest.mark.contract
def test_consolidated_version_is_addressable_by_id(api_client, edital_publicado):
    version = VersaoConsolidada.objects.get(edital=edital_publicado)
    response = api_client.get(f"/api/v1/public/versoes/{version.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(version.id)
    assert "immutable" in response["Cache-Control"]


@pytest.mark.django_db
@pytest.mark.contract
def test_history_page_matches_contract(api_client, edital_publicado):
    retify(
        api_client,
        edital_publicado,
        [{"targetPath": VACANCIES, "operation": "REPLACE", "newValue": 7}],
    )
    response = api_client.get(f"/api/v1/public/editais/{edital_publicado.id}/historico")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "nextCursor"}
    assert body["nextCursor"] is None
    kinds = [item["kind"] for item in body["items"]]
    assert kinds.count("PUBLICACAO") == 2
    assert kinds.count("RETIFICACAO") == 1
    assert kinds.count("VERSAO_CONSOLIDADA") >= 2


@pytest.mark.django_db
@pytest.mark.contract
def test_history_paginates_by_opaque_cursor(api_client, edital_publicado):
    retify(
        api_client,
        edital_publicado,
        [{"targetPath": VACANCIES, "operation": "REPLACE", "newValue": 7}],
    )
    url = f"/api/v1/public/editais/{edital_publicado.id}/historico"
    todos = api_client.get(url, {"limit": 100}).json()["items"]

    primeira = api_client.get(url, {"limit": 2}).json()
    assert len(primeira["items"]) == 2
    assert primeira["nextCursor"]

    segunda = api_client.get(url, {"limit": 100, "cursor": primeira["nextCursor"]}).json()
    assert segunda["nextCursor"] is None
    assert primeira["items"] + segunda["items"] == todos


@pytest.mark.django_db
@pytest.mark.contract
@pytest.mark.parametrize("limit", ["0", "101", "muitos"])
def test_history_rejects_limit_outside_the_contract(api_client, edital_publicado, limit):
    response = api_client.get(
        f"/api/v1/public/editais/{edital_publicado.id}/historico", {"limit": limit}
    )
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_limit"


@pytest.mark.django_db
@pytest.mark.contract
def test_history_rejects_corrupted_cursor(api_client, edital_publicado):
    response = api_client.get(
        f"/api/v1/public/editais/{edital_publicado.id}/historico", {"cursor": "###"}
    )
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_cursor"


@pytest.mark.django_db
@pytest.mark.contract
def test_unknown_public_resources_return_not_found(api_client):
    ausente = "00000000-0000-0000-0000-0000000009ff"
    for url in (
        f"/api/v1/public/publicacoes/{ausente}",
        f"/api/v1/public/retificacoes/{ausente}",
        f"/api/v1/public/versoes/{ausente}",
    ):
        response = api_client.get(url)
        assert response.status_code == 404, url
        assert response.json()["code"] == "not_found", url
