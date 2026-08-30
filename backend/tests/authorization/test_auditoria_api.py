"""T087 — a trilha administrativa é consultável só por quem tem permissão, no próprio escopo."""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import ProcessoSeletivo
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import publish_original

URL = "/api/v1/admin/auditoria"
AUDITOR = ["auditoria:consultar"]


@pytest.fixture
def cenario(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.mark.django_db
@pytest.mark.authorization
def test_audit_query_denies_by_default(api_client, cenario):
    negado = api_client.get(URL, **actor_headers("curioso", ["processo:criar"]))
    assert negado.status_code == 403
    assert negado.json()["code"] == "forbidden"
    assert api_client.get(URL).status_code == 401


@pytest.mark.django_db
@pytest.mark.authorization
def test_audit_query_returns_events_of_the_actor_scope(api_client, cenario):
    response = api_client.get(URL, **actor_headers("auditor", AUDITOR))
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "nextCursor"}
    assert body["items"], "o fluxo de publicação deve ter gerado auditoria"
    primeiro = body["items"][0]
    assert set(primeiro) == {
        "eventId",
        "occurredAt",
        "actorSubject",
        "permission",
        "operation",
        "aggregateType",
        "aggregateId",
        "previousState",
        "newState",
        "previousRevision",
        "newRevision",
        "reason",
        "correlationId",
    }


@pytest.mark.django_db
@pytest.mark.authorization
def test_audit_query_never_exposes_idempotency_keys_or_content(api_client, cenario):
    """A trilha não pode virar via alternativa de leitura do conteúdo normativo."""
    assert RegistroAuditoria.objects.exclude(idempotency_key="").exists()
    corpo = api_client.get(
        URL, {"limit": 100}, **actor_headers("auditor", AUDITOR)
    ).content.decode()
    for chave in RegistroAuditoria.objects.values_list("idempotency_key", flat=True):
        if chave:
            assert chave not in corpo
    assert "idempotency" not in corpo.lower()
    assert "content" not in corpo.lower()


@pytest.mark.django_db
@pytest.mark.authorization
def test_audit_query_does_not_cross_institutional_scope(api_client, cenario):
    assert RegistroAuditoria.objects.filter(institution_scope="cefor").exists()
    response = api_client.get(
        URL,
        **{
            "HTTP_AUTHORIZATION": "Bearer auditor|outra-instituicao|auditoria:consultar",
            "HTTP_IDEMPOTENCY_KEY": "auditoria-key-00000001",
            "HTTP_X_CORRELATION_ID": "escopo",
        },
    )
    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.django_db
@pytest.mark.authorization
def test_audit_query_filters_by_aggregate(api_client, cenario):
    processo = ProcessoSeletivo.objects.get(pk=cenario.processo_id)
    response = api_client.get(
        URL,
        {"aggregateType": "ProcessoSeletivo", "aggregateId": str(processo.id)},
        **actor_headers("auditor", AUDITOR),
    )
    assert response.status_code == 200
    itens = response.json()["items"]
    assert itens
    assert {item["aggregateType"] for item in itens} == {"ProcessoSeletivo"}
    assert {item["aggregateId"] for item in itens} == {str(processo.id)}


@pytest.mark.django_db
@pytest.mark.authorization
def test_audit_query_paginates_newest_first_without_repeating(api_client, cenario):
    todos = api_client.get(URL, {"limit": 100}, **actor_headers("auditor", AUDITOR)).json()["items"]
    assert len(todos) > 2
    instantes = [item["occurredAt"] for item in todos]
    assert instantes == sorted(instantes, reverse=True)

    primeira = api_client.get(URL, {"limit": 2}, **actor_headers("auditor", AUDITOR)).json()
    assert len(primeira["items"]) == 2
    assert primeira["nextCursor"]
    segunda = api_client.get(
        URL,
        {"limit": 100, "cursor": primeira["nextCursor"]},
        **actor_headers("auditor", AUDITOR),
    ).json()
    assert segunda["nextCursor"] is None
    assert primeira["items"] + segunda["items"] == todos


@pytest.mark.django_db
@pytest.mark.authorization
@pytest.mark.parametrize("limit", ["0", "101", "muitos"])
def test_audit_query_rejects_limit_outside_the_contract(api_client, cenario, limit):
    response = api_client.get(URL, {"limit": limit}, **actor_headers("auditor", AUDITOR))
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_limit"


@pytest.mark.django_db
@pytest.mark.authorization
def test_audit_query_rejects_corrupted_cursor(api_client, cenario):
    response = api_client.get(URL, {"cursor": "###"}, **actor_headers("auditor", AUDITOR))
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_cursor"
