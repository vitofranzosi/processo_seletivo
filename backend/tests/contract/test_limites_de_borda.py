"""FR-020 e FR-021 da 003 — a borda recusa o que a persistência não aguenta.

Campo maior que a coluna, cabeçalho fora do formato e instante sem fuso chegavam ao PostgreSQL e
viravam erro interno. 500 não é contrato: o cliente não consegue fazer nada com ele, e a
mensagem de erro do banco não é informação que deva sair da aplicação.
"""

import pytest

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import publish_original

pytestmark = pytest.mark.contract


def _criar(api_client, edital, changes, **headers):
    base = VersaoConsolidada.objects.get(edital=edital)
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Limites de borda",
            "changes": changes,
        },
        format="json",
        **{
            **actor_headers("retificador", ["retificacao:elaborar"], key="borda-000000001"),
            **headers,
        },
    )


@pytest.mark.django_db(transaction=True)
def test_target_path_acima_da_coluna_e_recusado_sem_erro_interno(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)

    resposta = _criar(
        api_client,
        edital,
        [{"targetPath": "/" + "a" * 1000, "operation": "REPLACE", "newValue": "x"}],
    )

    # 422 é como o projeto responde a violação de contrato de campo; o que importa aqui é que a
    # recusa aconteça na borda e chegue como problema descrito, não como erro do banco.
    assert resposta.status_code == 422
    assert resposta["Content-Type"].startswith("application/problem+json")


@pytest.mark.django_db(transaction=True)
def test_hash_declarado_acima_da_coluna_e_recusado(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)

    resposta = _criar(
        api_client,
        edital,
        [
            {
                "targetPath": "/title",
                "operation": "REPLACE",
                "newValue": "x",
                "expectedPreviousHash": "f" * 65,
            }
        ],
    )

    assert resposta.status_code == 422


@pytest.mark.django_db(transaction=True)
def test_correlation_id_inutilizavel_nao_impede_a_requisicao_nem_vaza_para_a_resposta(
    api_client, manager_headers, process_payload
):
    """O cabeçalho é de diagnóstico e opcional: recusar a requisição seria desproporcional.

    O que não pode é ser aceito. A resposta ecoa sempre o identificador em uso, então o cliente
    que enviou um valor inutilizável vê de volta um diferente — a substituição é visível.
    """
    for ordem, declarado in enumerate(("c" * 200, "com\r\nquebra", ""), 1):
        resposta = api_client.post(
            "/api/v1/admin/processos",
            {
                **process_payload,
                "institutionalCode": f"PS-2026-{ordem:03d}",
                "firstEdital": {**process_payload["firstEdital"], "number": f"{ordem:02d}"},
            },
            format="json",
            **{
                **manager_headers,
                "HTTP_IDEMPOTENCY_KEY": f"borda-correlacao-{ordem:04d}",
                "HTTP_X_CORRELATION_ID": declarado,
            },
        )
        assert resposta.status_code == 201, resposta.content
        assert resposta["X-Correlation-ID"] != declarado
        assert len(resposta["X-Correlation-ID"]) <= 100


@pytest.mark.django_db(transaction=True)
def test_correlation_id_utilizavel_e_preservado(api_client, manager_headers, process_payload):
    resposta = api_client.post(
        "/api/v1/admin/processos",
        process_payload,
        format="json",
        **{**manager_headers, "HTTP_X_CORRELATION_ID": "corr-2026-08-29-0001"},
    )

    assert resposta.status_code == 201
    assert resposta["X-Correlation-ID"] == "corr-2026-08-29-0001"


@pytest.mark.django_db(transaction=True)
def test_instante_sem_fuso_e_recusado_na_consulta_temporal(
    api_client, manager_headers, process_payload
):
    """FR-021: sem fuso não há instante, e o do servidor tornaria o passado irreprodutível."""
    edital = publish_original(api_client, manager_headers, process_payload)
    url = f"/api/v1/public/editais/{edital.id}/versao-vigente"

    ingenuo = api_client.get(url, {"em": "2026-03-01T10:00:00"}, format="json")

    assert ingenuo.status_code == 400
    assert ingenuo.json()["code"] == "invalid_instant"
    assert "fuso" in ingenuo.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_instante_com_fuso_continua_valendo(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    url = f"/api/v1/public/editais/{edital.id}/versao-vigente"

    com_fuso = api_client.get(url, {"em": "2099-03-01T10:00:00-03:00"}, format="json")
    sem_parametro = api_client.get(url, format="json")

    assert com_fuso.status_code == 200
    assert sem_parametro.status_code == 200
