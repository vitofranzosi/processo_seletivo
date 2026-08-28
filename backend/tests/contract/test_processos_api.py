from pathlib import Path

import pytest
import yaml


@pytest.mark.contract
def test_openapi_declares_mvp_operations():
    contract = (
        Path(__file__).resolve().parents[3]
        / "specs/001-processo-seletivo-editais/contracts/openapi.yaml"
    )
    document = yaml.safe_load(contract.read_text(encoding="utf-8"))
    assert (
        document["paths"]["/admin/processos"]["post"]["operationId"]
        == "criarProcessoComPrimeiroEdital"
    )
    assert (
        document["paths"]["/admin/processos/{processoId}/editais"]["post"]["operationId"]
        == "criarEdital"
    )
    assert (
        document["paths"]["/admin/processos/{processoId}/ativacoes"]["post"]["operationId"]
        == "ativarProcesso"
    )


@pytest.mark.django_db
@pytest.mark.contract
def test_create_response_matches_contract(api_client, manager_headers, process_payload):
    response = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert response.status_code == 201
    assert set(response.json()) == {"id", "institutionalCode", "status", "revision"}
    assert response["ETag"] == '"1"'
    assert response["X-Correlation-ID"] == "test-correlation-id"
