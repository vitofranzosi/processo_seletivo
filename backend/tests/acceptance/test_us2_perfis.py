import pytest

from processo_seletivo.editais.models.perfis import PerfilVaga
from processo_seletivo.processos.models import Edital


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us2_replaces_profiles_without_affecting_other_edital(
    api_client, manager_headers, process_payload
):
    created = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    processo_id = created.json()["id"]
    api_client.post(
        f"/api/v1/admin/processos/{processo_id}/editais",
        {"number": "02", "year": 2026, "title": "Segundo"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "us2-second-edital"},
    )
    first, second = Edital.objects.order_by("number")
    response = api_client.put(
        f"/api/v1/admin/editais/{first.id}/rascunho",
        {
            "profiles": [
                {
                    "id": "00000000-0000-0000-0000-000000000211",
                    "code": "CR",
                    "name": "Somente cadastro reserva",
                    "immediateVacancies": 0,
                    "reserveType": "UNLIMITED",
                    "competitionModalities": [
                        {
                            "id": "00000000-0000-0000-0000-000000000212",
                            "code": "AC",
                            "name": "Ampla concorrência",
                        }
                    ],
                }
            ],
            "schedule": [],
        },
        format="json",
        HTTP_AUTHORIZATION="Bearer gestor-a|cefor|edital:elaborar",
        HTTP_IF_MATCH='"1"',
    )
    assert response.status_code == 200
    assert PerfilVaga.objects.filter(edital=first).count() == 1
    assert PerfilVaga.objects.filter(edital=second).count() == 0
