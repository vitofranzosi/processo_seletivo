from pathlib import Path

import pytest
import yaml


@pytest.mark.contract
def test_openapi_has_explicit_publication_workflow_and_signatory():
    contract = (
        Path(__file__).resolve().parents[3]
        / "specs/001-processo-seletivo-editais/contracts/openapi.yaml"
    )
    document = yaml.safe_load(contract.read_text(encoding="utf-8"))
    paths = document["paths"]
    expected = {
        "/admin/editais/{editalId}/submissoes": "submeterEdital",
        "/admin/editais/{editalId}/homologacoes": "homologarEdital",
        "/admin/editais/{editalId}/revogacoes-homologacao": "revogarHomologacaoEdital",
        "/admin/editais/{editalId}/publicacoes": "publicarEdital",
    }
    for path, operation_id in expected.items():
        assert paths[path]["post"]["operationId"] == operation_id
    assert document["components"]["schemas"]["PublicacaoRequest"]["required"] == ["signatory"]
    assert set(document["components"]["schemas"]["SignatorySnapshot"]["required"]) == {
        "authorityId",
        "name",
        "role",
    }
