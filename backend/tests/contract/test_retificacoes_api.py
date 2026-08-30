from pathlib import Path

import pytest
import yaml


@pytest.mark.contract
def test_openapi_has_explicit_retification_workflow():
    contract = (
        Path(__file__).resolve().parents[3]
        / "specs/001-processo-seletivo-editais/contracts/openapi.yaml"
    )
    paths = yaml.safe_load(contract.read_text(encoding="utf-8"))["paths"]
    expected = {
        "/admin/editais/{editalId}/retificacoes": "criarRetificacao",
        "/admin/retificacoes/{retificacaoId}/rascunho": "atualizarRascunhoRetificacao",
        "/admin/retificacoes/{retificacaoId}/submissoes": "submeterRetificacao",
        "/admin/retificacoes/{retificacaoId}/homologacoes": "homologarRetificacao",
        "/admin/retificacoes/{retificacaoId}/publicacoes": "publicarRetificacao",
        "/admin/retificacoes/{retificacaoId}/devolucoes": "devolverRetificacao",
        "/admin/retificacoes/{retificacaoId}/cancelamentos": "cancelarRetificacao",
    }
    for path, operation in expected.items():
        assert paths[path]["post" if "rascunho" not in path else "put"]["operationId"] == operation
