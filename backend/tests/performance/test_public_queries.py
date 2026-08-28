"""T092 — custo e escalabilidade das consultas públicas.

Estes testes medem **custo de consulta**, não o SLO de produção. Contagem de queries é
determinística e detecta a degradação que importa — o custo crescer com o histórico — enquanto
tempo de parede em suíte de teste é ruidoso e depende da máquina. Os limites de tempo aqui são
generosos e servem como rede de segurança contra regressão catastrófica.

O SLO institucional do plan.md — p95 até 2 s nas consultas públicas e pico de 500 consultas por
segundo — exige carga distribuída contra um serviço implantado e **não** é verificado aqui. O
harness para medi-lo está em `scripts/carga_publica.py`.
"""

import time
from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import publish_original, retify

VACANCIES = "/profiles/0/immediateVacancies"
# Teto por consulta pública. Vale como guarda de regressão, não como SLO.
BUDGET_SECONDS = 1.0


def replace(valor):
    return [{"targetPath": VACANCIES, "operation": "REPLACE", "newValue": valor}]


def outro_processo(process_payload, sufixo):
    """Identificação institucional e número de Edital próprios, por causa das constraints."""
    return {
        **process_payload,
        "institutionalCode": f"PS-CARGA-{sufixo}",
        "firstEdital": {**process_payload["firstEdital"], "number": f"9{sufixo}"},
    }


def edital_com_retificacoes(api_client, manager_headers, process_payload, quantidade, seed=0):
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=complete_draft(seed)
    )
    for indice in range(1, quantidade + 1):
        retify(api_client, edital, replace(100 + indice), suffix=f"c{seed}{indice}")
    return edital


def queries_de(api_client, url, params=None):
    with CaptureQueriesContext(connection) as capturadas:
        resposta = api_client.get(url, params or {})
    assert resposta.status_code == 200, resposta.content
    return len(capturadas.captured_queries), resposta


@pytest.mark.django_db(transaction=True)
@pytest.mark.performance
def test_effective_version_cost_does_not_grow_with_the_history(
    api_client, manager_headers, process_payload
):
    """A consulta mais quente do sistema precisa ser O(1) em número de Retificações."""
    curto = edital_com_retificacoes(api_client, manager_headers, process_payload, 3)
    barato, _ = queries_de(api_client, f"/api/v1/public/editais/{curto.id}/versao-vigente")

    longo = edital_com_retificacoes(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "carga-key-000000002"},
        outro_processo(process_payload, "02"),
        20,
        seed=2,
    )
    caro, _ = queries_de(api_client, f"/api/v1/public/editais/{longo.id}/versao-vigente")

    assert barato == caro, (
        f"custo cresceu com o histórico: {barato} consultas com 3 Retificações, "
        f"{caro} com 20 — a versão consolidada é materializada e deve custar o mesmo"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.performance
def test_history_cost_does_not_grow_with_the_history(
    api_client, manager_headers, process_payload
):
    """Sem prefetch da proveniência, cada versão vira uma consulta e o histórico degrada."""
    curto = edital_com_retificacoes(api_client, manager_headers, process_payload, 3)
    barato, _ = queries_de(
        api_client, f"/api/v1/public/editais/{curto.id}/historico", {"limit": 100}
    )

    longo = edital_com_retificacoes(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "carga-key-000000003"},
        outro_processo(process_payload, "03"),
        20,
        seed=3,
    )
    caro, resposta = queries_de(
        api_client, f"/api/v1/public/editais/{longo.id}/historico", {"limit": 100}
    )

    # 21 Publicações (original + 20) + 20 Retificações + 21 versões consolidadas.
    assert len(resposta.json()["items"]) == 62
    assert barato == caro, (
        f"custo cresceu com o histórico: {barato} consultas com 3 Retificações, {caro} com 20"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.performance
def test_immutable_resources_cost_a_bounded_number_of_queries(
    api_client, manager_headers, process_payload
):
    edital = edital_com_retificacoes(api_client, manager_headers, process_payload, 5)
    publicacao = Publicacao.objects.filter(edital=edital).first()
    versao = VersaoConsolidada.objects.filter(edital=edital).first()

    for url, teto in (
        (f"/api/v1/public/publicacoes/{publicacao.id}", 1),
        (f"/api/v1/public/versoes/{versao.id}", 2),
        (f"/api/v1/public/publicacoes/{publicacao.id}/documento", 1),
    ):
        quantidade, _ = queries_de(api_client, url)
        assert quantidade <= teto, f"{url} custou {quantidade} consultas, esperado até {teto}"


@pytest.mark.django_db(transaction=True)
@pytest.mark.performance
def test_history_page_cost_is_independent_of_the_requested_page_size(
    api_client, manager_headers, process_payload
):
    edital = edital_com_retificacoes(api_client, manager_headers, process_payload, 20)
    pequena, _ = queries_de(
        api_client, f"/api/v1/public/editais/{edital.id}/historico", {"limit": 1}
    )
    grande, _ = queries_de(
        api_client, f"/api/v1/public/editais/{edital.id}/historico", {"limit": 100}
    )
    assert pequena == grande


@pytest.mark.django_db(transaction=True)
@pytest.mark.performance
def test_sc005_recovers_current_and_any_historical_version_within_budget(
    api_client, manager_headers, process_payload
):
    """SC-005: até 20 Retificações, versão vigente e qualquer histórica em até 10 s por consulta."""
    edital = edital_com_retificacoes(api_client, manager_headers, process_payload, 20)
    fronteiras = list(
        VersaoConsolidada.objects.filter(edital=edital).values_list("valid_from", flat=True)
    )
    assert len(fronteiras) == 21

    tempos = []
    url = f"/api/v1/public/editais/{edital.id}/versao-vigente"
    for instante in [None, *fronteiras]:
        params = {} if instante is None else {"em": instante.isoformat()}
        inicio = time.monotonic()
        resposta = api_client.get(url, params)
        tempos.append(time.monotonic() - inicio)
        assert resposta.status_code == 200
        assert resposta.json()["appliedPublications"] is not None

    assert max(tempos) < BUDGET_SECONDS, (
        f"consulta mais lenta levou {max(tempos):.3f}s, acima do teto de regressão "
        f"de {BUDGET_SECONDS}s (o limite de SC-005 é 10 s)"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.performance
def test_temporal_query_cost_is_the_same_at_every_boundary(
    api_client, manager_headers, process_payload
):
    """Consultar o passado remoto não pode custar mais que consultar o presente."""
    edital = edital_com_retificacoes(api_client, manager_headers, process_payload, 20)
    fronteiras = sorted(
        VersaoConsolidada.objects.filter(edital=edital).values_list("valid_from", flat=True)
    )
    url = f"/api/v1/public/editais/{edital.id}/versao-vigente"

    custos = {
        queries_de(api_client, url, {"em": instante.isoformat()})[0]
        for instante in (fronteiras[0], fronteiras[len(fronteiras) // 2], fronteiras[-1])
    }
    assert len(custos) == 1, f"custo variou por instante consultado: {custos}"


@pytest.mark.django_db(transaction=True)
@pytest.mark.performance
def test_public_queries_stay_correct_under_concurrent_readers(
    api_client, manager_headers, process_payload
):
    """Leitores concorrentes não podem observar versão parcial nem conteúdo trocado."""
    import threading

    from django.db import connections
    from rest_framework.test import APIClient

    edital = edital_com_retificacoes(api_client, manager_headers, process_payload, 5)
    esperado = api_client.get(f"/api/v1/public/editais/{edital.id}/versao-vigente").json()
    resultados = []
    barreira = threading.Barrier(8, timeout=20)

    def consultar():
        try:
            cliente = APIClient()
            barreira.wait()
            resposta = cliente.get(f"/api/v1/public/editais/{edital.id}/versao-vigente")
            resultados.append((resposta.status_code, resposta.json()["contentHash"]))
        except Exception as exc:  # noqa: BLE001 — avaliado no corpo do teste
            resultados.append(exc)
        finally:
            connections.close_all()

    threads = [threading.Thread(target=consultar) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert resultados == [(200, esperado["contentHash"])] * 8, resultados


@pytest.mark.django_db(transaction=True)
@pytest.mark.performance
def test_future_versions_are_not_scanned_by_the_current_query(
    api_client, manager_headers, process_payload
):
    """Vigências futuras não podem encarecer nem contaminar a consulta do presente."""
    edital = publish_original(api_client, manager_headers, process_payload)
    antes, _ = queries_de(api_client, f"/api/v1/public/editais/{edital.id}/versao-vigente")

    for indice in range(1, 11):
        vigencia = timezone.now() + timedelta(days=30 * indice)
        retify(
            api_client, edital, replace(200 + indice), effective_at=vigencia.isoformat(),
            suffix=f"f{indice}",
        )

    depois, resposta = queries_de(api_client, f"/api/v1/public/editais/{edital.id}/versao-vigente")
    assert antes == depois
    assert resposta.json()["content"]["profiles"][0]["immediateVacancies"] == 1
