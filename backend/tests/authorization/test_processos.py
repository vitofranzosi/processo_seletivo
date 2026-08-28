import pytest


@pytest.mark.django_db
@pytest.mark.authorization
def test_cross_scope_process_is_not_revealed(api_client, manager_headers, process_payload):
    created = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    processo_id = created.json()["id"]
    response = api_client.post(
        f"/api/v1/admin/processos/{processo_id}/editais",
        {"number": "02", "year": 2026, "title": "Outro"},
        format="json",
        HTTP_AUTHORIZATION="Bearer gestor-b|outra|edital:criar",
        HTTP_IDEMPOTENCY_KEY="cross-scope-key-01",
    )
    assert response.status_code == 404
