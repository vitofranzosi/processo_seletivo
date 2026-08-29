from pathlib import Path

import pytest
import yaml

from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers, complete_draft


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


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_submission_returns_warnings_so_the_responsible_can_decide(
    api_client, manager_headers, process_payload
):
    """FR-019/FR-020: avisos são classificados e permanecem visíveis na decisão de prosseguir."""
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )
    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"2"'},
    )
    assert resposta.status_code == 200
    achados = resposta.json()["validationFindings"]
    assert achados, "o rascunho sem descrição deve produzir aviso"
    aviso = next(item for item in achados if item["code"] == "description_missing")
    assert aviso["severity"] == "WARNING"
    assert aviso["path"] == "description"
    assert not [item for item in achados if item["severity"] == "BLOCKING_ERROR"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_blocking_error_stops_submission_and_names_the_cause(
    api_client, manager_headers, process_payload
):
    """FR-020: erro impeditivo bloqueia e é apresentado separadamente dos avisos."""
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        {**complete_draft(), "schedule": []},
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )
    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"2"'},
    )
    assert resposta.status_code == 422
    corpo = resposta.json()
    assert corpo["code"] == "blocking_findings"
    assert "Evento" in corpo["detail"]
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.EM_ELABORACAO


@pytest.mark.contract
@pytest.mark.django_db(transaction=True)
def test_campo_nao_reconhecido_no_rascunho_e_recusado(
    api_client, manager_headers, process_payload
):
    """FR-028 da 003: aceitar e descartar em silêncio não é comportamento admissível.

    `editorialContent` era aceito pelo serializer e pelo contrato, e nenhum comando o persistia.
    Quem o enviava recebia 200 e acreditava que o conteúdo editorial estava guardado no Edital.
    """
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])

    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        {**complete_draft(), "editorialContent": {"preambulo": "texto livre"}},
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"]),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )

    assert resposta.status_code == 422
    assert "editorialContent" in resposta.json()["detail"]


@pytest.mark.contract
def test_o_contrato_nao_anuncia_mais_o_campo_descartado():
    contrato = yaml.safe_load(
        (
            Path(__file__).resolve().parents[3]
            / "specs/001-processo-seletivo-editais/contracts/openapi.yaml"
        ).read_text(encoding="utf-8")
    )
    rascunho = contrato["components"]["schemas"]["EditalDraftRequest"]
    assert "editorialContent" not in rascunho["properties"]
    assert rascunho["additionalProperties"] is False
