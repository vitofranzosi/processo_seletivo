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


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_consolidar_sobre_conteudo_base_de_outra_versao_canonica_e_recusado(
    api_client, manager_headers, process_payload, monkeypatch
):
    """FR-047: a versão registrada tem de ser a versão do conteúdo.

    A Publicação de Retificação carimba a constante global sobre conteúdo derivado de uma
    Publicação-base que carrega a própria `schemaVersion`. Depois de um incremento as duas podem
    divergir, e o registro afirmaria uma versão que o conteúdo não tem.

    A recusa é uma comparação. A alternativa — converter v1 em v2, ou atualizar em massa os
    snapshots — seria construir compatibilidade para conteúdo que não existe.
    """
    from processo_seletivo.publicacoes.application import retificacoes
    from processo_seletivo.publicacoes.domain.conflicts import previous_hash
    from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
    from tests.fixtures.edital import actor_headers, caminho_perfil
    from tests.fixtures.publicacao import publish_original, try_publish_retification

    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    criada = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Versão canônica divergente",
            "changes": [
                {
                    "targetPath": caminho_perfil("immediateVacancies"),
                    "operation": "REPLACE",
                    "newValue": 5,
                    "expectedPreviousHash": previous_hash(
                        base.content, caminho_perfil("immediateVacancies")
                    ),
                }
            ],
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], key="versao-canonica-0001"),
    )
    assert criada.status_code == 201, criada.content

    # A versão canônica sobe, e o conteúdo-base fica para trás. Envelhecê-lo pelo outro lado não
    # é possível — e é bom que não seja: a Versão Consolidada é append-only, e o trigger recusa.
    # Um incremento futuro de `SCHEMA_VERSION` produz exatamente este estado.
    monkeypatch.setattr(retificacoes, "SCHEMA_VERSION", base.content["schemaVersion"] + 1)

    resposta = try_publish_retification(
        api_client, Retificacao.objects.get(pk=criada.json()["id"]), suffix="v"
    )

    assert resposta.status_code == 409, resposta.content
    assert resposta.json()["code"] == "canonical_schema_version_mismatch"
    assert Retificacao.objects.get(pk=criada.json()["id"]).publication is None
