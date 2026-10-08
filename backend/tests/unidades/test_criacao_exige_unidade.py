"""Processo e Edital novos só nascem em Unidade registrada e ativa (060, FR-1110).

O que já existe numa Unidade desativada continua: o certame em curso termina, e só não ganha
Processo nem Edital novos.
"""

import pytest

from processo_seletivo.processos.models import ProcessoSeletivo
from processo_seletivo.unidades.models import Unidade
from tests.fixtures.autoridades import registrar_unidade

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _headers(escopo, chave="criar-processo-0001"):
    return {
        "HTTP_AUTHORIZATION": f"Bearer gestor|{escopo}|processo:criar,processo:ativar,edital:criar",
        "HTTP_IDEMPOTENCY_KEY": chave,
        "HTTP_X_CORRELATION_ID": "criacao",
    }


def _criar(api_client, process_payload, escopo):
    return api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **_headers(escopo)
    )


def test_escopo_sem_unidade_registrada_nao_cria_processo(api_client, process_payload):
    resposta = _criar(api_client, process_payload, "sem-unidade")

    assert resposta.status_code == 422
    assert resposta.json()["code"] == "unidade_nao_registrada"
    assert not ProcessoSeletivo.objects.filter(institution_scope="sem-unidade").exists()


def test_unidade_desativada_nao_cria_processo(api_client, process_payload):
    registrar_unidade("serra", ativa=False)
    resposta = _criar(api_client, process_payload, "serra")

    assert resposta.status_code == 422
    assert "desativada" in resposta.json()["detail"]


def test_unidade_registrada_e_ativa_cria(api_client, process_payload):
    registrar_unidade("serra")
    assert _criar(api_client, process_payload, "serra").status_code == 201


def test_o_processo_da_unidade_desativada_nao_ganha_edital_novo(api_client, process_payload):
    registrar_unidade("serra")
    processo_id = _criar(api_client, process_payload, "serra").json()["id"]
    Unidade.objects.filter(codigo="serra").update(ativa=False)

    resposta = api_client.post(
        f"/api/v1/admin/processos/{processo_id}/editais",
        {"number": "02", "year": 2026, "title": "Segundo"},
        format="json",
        **_headers("serra", chave="criar-edital-0002"),
    )

    assert resposta.status_code == 422
    assert resposta.json()["code"] == "unidade_nao_registrada"
