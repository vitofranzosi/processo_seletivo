import pytest


@pytest.mark.django_db
@pytest.mark.authorization
def test_anonymous_is_denied(api_client, process_payload):
    response = api_client.post(
        "/api/v1/admin/processos",
        process_payload,
        format="json",
        HTTP_IDEMPOTENCY_KEY="anonymous-key-0001",
    )
    assert response.status_code == 401
    assert response["Content-Type"].startswith("application/problem+json")


@pytest.mark.django_db
@pytest.mark.authorization
def test_missing_permission_is_denied(api_client, process_payload):
    response = api_client.post(
        "/api/v1/admin/processos",
        process_payload,
        format="json",
        HTTP_AUTHORIZATION="Bearer leitor|cefor|auditoria:consultar",
        HTTP_IDEMPOTENCY_KEY="forbidden-key-001",
    )
    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.authorization
def test_idempotency_replays_and_rejects_changed_payload(
    api_client, manager_headers, process_payload
):
    first = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    replay = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    changed = {**process_payload, "title": "Outro conteúdo"}
    conflict = api_client.post("/api/v1/admin/processos", changed, format="json", **manager_headers)
    assert first.status_code == 201
    # A repetição responde com o status do ato original: o contrato documenta um único código
    # de sucesso por operação, e 200 numa repetição de criação sugeriria que nada foi criado.
    assert replay.status_code == 201
    assert replay.json()["id"] == first.json()["id"]
    assert conflict.status_code == 409


@pytest.mark.django_db
@pytest.mark.authorization
def test_activation_requires_if_match(api_client, manager_headers, process_payload):
    created = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    headers = {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "if-match-required-1"}
    response = api_client.post(
        f"/api/v1/admin/processos/{created.json()['id']}/ativacoes",
        {"reason": "Ativação"},
        format="json",
        **headers,
    )
    assert response.status_code == 428
