import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import Edital, ProcessoSeletivo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_process_and_first_edital_are_atomic(api_client, manager_headers, process_payload):
    response = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert response.status_code == 201
    processo = ProcessoSeletivo.objects.get()
    assert processo.editais.count() == 1
    assert (
        RegistroAuditoria.objects.filter(aggregate_id=processo.id, operation="CRIAR").count() == 1
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_missing_first_edital_creates_nothing(api_client, manager_headers):
    response = api_client.post(
        "/api/v1/admin/processos",
        {"institutionalCode": "INVALID", "title": "Sem Edital"},
        format="json",
        **manager_headers,
    )
    assert response.status_code == 400
    assert ProcessoSeletivo.objects.count() == 0
    assert Edital.objects.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_duplicate_identifier_leaves_no_partial_process(
    api_client, manager_headers, process_payload
):
    assert (
        api_client.post(
            "/api/v1/admin/processos", process_payload, format="json", **manager_headers
        ).status_code
        == 201
    )
    other_headers = {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0002"}
    response = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **other_headers
    )
    assert response.status_code == 409
    assert ProcessoSeletivo.objects.count() == 1
    assert Edital.objects.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_second_edital_has_independent_identity_and_state(
    api_client, manager_headers, process_payload
):
    created = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    processo_id = created.json()["id"]
    headers = {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0003"}
    second = api_client.post(
        f"/api/v1/admin/processos/{processo_id}/editais",
        {"number": "02", "year": 2026, "title": "Segundo Edital"},
        format="json",
        **headers,
    )
    assert second.status_code == 201
    editais = list(Edital.objects.order_by("number"))
    assert len(editais) == 2
    assert editais[0].id != editais[1].id
    assert all(item.status == Edital.Status.EM_ELABORACAO for item in editais)
