from pathlib import Path

import pytest
import yaml


@pytest.mark.contract
def test_openapi_declares_structured_draft_contract():
    contract = (
        Path(__file__).resolve().parents[3]
        / "specs/001-processo-seletivo-editais/contracts/openapi.yaml"
    )
    document = yaml.safe_load(contract.read_text(encoding="utf-8"))
    operation = document["paths"]["/admin/editais/{editalId}/rascunho"]["put"]
    assert operation["operationId"] == "atualizarRascunhoEdital"
    assert any(parameter["$ref"].endswith("/IfMatch") for parameter in operation["parameters"])
    schema = document["components"]["schemas"]["EditalDraftRequest"]
    assert set(schema["required"]) == {"profiles", "schedule"}


@pytest.mark.django_db
@pytest.mark.contract
def test_draft_response_has_etag(api_client, manager_headers, process_payload):
    created = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    from processo_seletivo.processos.models import Edital

    edital = Edital.objects.get(processo_id=created.json()["id"])
    response = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        {
            "profiles": [
                {
                    "id": "00000000-0000-0000-0000-000000000201",
                    "code": "P1",
                    "name": "Perfil 1",
                    "immediateVacancies": 1,
                    "reserveType": "NONE",
                    "competitionModalities": [],
                }
            ],
            "schedule": [],
        },
        format="json",
        HTTP_AUTHORIZATION="Bearer gestor-a|cefor|edital:elaborar",
        HTTP_IF_MATCH='"1"',
    )
    assert response.status_code == 200
    assert response["ETag"] == '"2"'
