import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import AtoAdministrativo, ProcessoSeletivo


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us1_create_add_and_activate(api_client, manager_headers, process_payload):
    created = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert created.status_code == 201
    processo_id = created.json()["id"]
    second_headers = {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "acceptance-key-002"}
    assert (
        api_client.post(
            f"/api/v1/admin/processos/{processo_id}/editais",
            {"number": "02", "year": 2026, "title": "Edital independente"},
            format="json",
            **second_headers,
        ).status_code
        == 201
    )
    activate_headers = {
        **manager_headers,
        "HTTP_IDEMPOTENCY_KEY": "acceptance-key-003",
        "HTTP_IF_MATCH": '"1"',
    }
    activated = api_client.post(
        f"/api/v1/admin/processos/{processo_id}/ativacoes",
        {"reason": "Abertura formal autorizada"},
        format="json",
        **activate_headers,
    )
    assert activated.status_code == 200
    assert activated.json()["status"] == "ATIVO"
    assert activated["ETag"] == '"2"'
    assert ProcessoSeletivo.objects.get(pk=processo_id).editais.count() == 2
    assert AtoAdministrativo.objects.filter(aggregate_id=processo_id, operation="ATIVAR").exists()
    assert RegistroAuditoria.objects.filter(aggregate_id=processo_id, operation="ATIVAR").exists()


@pytest.mark.django_db
@pytest.mark.acceptance
def test_stale_activation_is_rejected(api_client, manager_headers, process_payload):
    created = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    processo_id = created.json()["id"]
    headers = {
        **manager_headers,
        "HTTP_IDEMPOTENCY_KEY": "acceptance-key-004",
        "HTTP_IF_MATCH": '"9"',
    }
    response = api_client.post(
        f"/api/v1/admin/processos/{processo_id}/ativacoes",
        {"reason": "Revisão obsoleta"},
        format="json",
        **headers,
    )
    assert response.status_code == 412
