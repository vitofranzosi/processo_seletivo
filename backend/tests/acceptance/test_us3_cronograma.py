import pytest

from processo_seletivo.editais.models.cronograma import EventoCronograma
from processo_seletivo.processos.models import Edital


def draft_payload(profile_id, event_id, start_at):
    return {
        "profiles": [
            {
                "id": profile_id,
                "code": "P1",
                "name": "Perfil",
                "immediateVacancies": 1,
                "reserveType": "NONE",
                "competitionModalities": [],
            }
        ],
        "schedule": [
            {
                "id": event_id,
                "type": "INSCRICAO",
                "description": "Inscrições",
                "startAt": start_at,
                "order": 1,
            }
        ],
    }


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us3_keeps_schedules_independent(api_client, manager_headers, process_payload):
    created = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    api_client.post(
        f"/api/v1/admin/processos/{created.json()['id']}/editais",
        {"number": "02", "year": 2026, "title": "Segundo"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "us3-second-edital"},
    )
    first, second = Edital.objects.order_by("number")
    auth = "Bearer gestor-a|cefor|edital:elaborar"
    first_response = api_client.put(
        f"/api/v1/admin/editais/{first.id}/rascunho",
        draft_payload(
            "00000000-0000-0000-0000-000000000311",
            "00000000-0000-0000-0000-000000000321",
            "2026-09-01T09:00:00-03:00",
        ),
        format="json",
        HTTP_AUTHORIZATION=auth,
        HTTP_IF_MATCH='"1"',
    )
    second_response = api_client.put(
        f"/api/v1/admin/editais/{second.id}/rascunho",
        draft_payload(
            "00000000-0000-0000-0000-000000000312",
            "00000000-0000-0000-0000-000000000322",
            "2026-10-01T09:00:00-03:00",
        ),
        format="json",
        HTTP_AUTHORIZATION=auth,
        HTTP_IF_MATCH='"1"',
    )
    assert first_response.status_code == second_response.status_code == 200
    first_event = EventoCronograma.objects.get(cronograma__edital=first)
    second_event = EventoCronograma.objects.get(cronograma__edital=second)
    assert first_event.start_at != second_event.start_at


@pytest.mark.django_db
@pytest.mark.acceptance
def test_us3_rejects_inverted_period_without_partial_change(
    api_client, manager_headers, process_payload
):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    payload = draft_payload(
        "00000000-0000-0000-0000-000000000313",
        "00000000-0000-0000-0000-000000000323",
        "2026-09-02T09:00:00-03:00",
    )
    payload["schedule"][0]["endAt"] = "2026-09-01T09:00:00-03:00"
    response = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        payload,
        format="json",
        HTTP_AUTHORIZATION="Bearer gestor-a|cefor|edital:elaborar",
        HTTP_IF_MATCH='"1"',
    )
    assert response.status_code == 422
    assert not EventoCronograma.objects.exists()
