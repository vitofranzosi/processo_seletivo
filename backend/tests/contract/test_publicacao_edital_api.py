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
        # FR-006 declara as duas voltas anteriores à Publicação, e o contrato precisa das duas:
        # devolver desfaz a submissão, revogar desfaz a homologação.
        "/admin/editais/{editalId}/devolucoes": "devolverEdital",
        "/admin/editais/{editalId}/revogacoes-homologacao": "revogarHomologacaoEdital",
        "/admin/editais/{editalId}/publicacoes": "publicarEdital",
    }
    for path, operation_id in expected.items():
        assert paths[path]["post"]["operationId"] == operation_id
    assert document["components"]["schemas"]["PublicacaoRequest"]["required"] == ["signatory"]
    # Só o identificador desde a 060 (R-014): nome, cargo e ato de nomeação vêm do registro de
    # autoridades da unidade, e o contrato recusa os três se vierem.
    signatario = document["components"]["schemas"]["SignatorySnapshot"]
    assert signatario["required"] == ["authorityId"]
    assert set(signatario["properties"]) == {"authorityId"}
    assert signatario["additionalProperties"] is False
