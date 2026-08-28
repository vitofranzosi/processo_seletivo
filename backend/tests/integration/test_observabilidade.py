"""T091 — logs estruturados, health/readiness e métricas de conflito.

O princípio V da Constituição exige diagnóstico sem exposição indevida: estes testes verificam
tanto que o log carrega contexto suficiente quanto que ele não carrega token nem conteúdo.
"""

import json
import logging

import pytest

from processo_seletivo.shared.observability import JsonFormatter, metrics
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import publish_original


@pytest.fixture
def eventos():
    """Captura direta no logger: `propagate: False` impede o caplog de enxergar os registros."""

    class Coletor(logging.Handler):
        def __init__(self):
            super().__init__(level=logging.DEBUG)
            self.registros = []

        def emit(self, record):
            self.registros.append(record)

    coletor = Coletor()
    logger = logging.getLogger("processo_seletivo")
    logger.addHandler(coletor)
    try:
        yield coletor.registros
    finally:
        logger.removeHandler(coletor)


@pytest.fixture(autouse=True)
def contadores_limpos():
    metrics.reset()
    yield
    metrics.reset()


def registro(**extra):
    record = logging.LogRecord(
        name="processo_seletivo",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg="operacao_recusada",
        args=(),
        exc_info=None,
    )
    for chave, valor in extra.items():
        setattr(record, chave, valor)
    return record


@pytest.mark.integration
def test_structured_log_is_one_json_line_with_correlation():
    saida = JsonFormatter().format(
        registro(correlationId="abc-123", code="stale_revision", status=412, actor="gestor")
    )
    assert "\n" not in saida
    payload = json.loads(saida)
    assert payload["message"] == "operacao_recusada"
    assert payload["correlationId"] == "abc-123"
    assert payload["code"] == "stale_revision"
    assert payload["status"] == 412
    assert payload["level"] == "WARNING"
    assert payload["timestamp"]


@pytest.mark.integration
def test_structured_log_omits_fields_that_were_not_informed():
    payload = json.loads(JsonFormatter().format(registro(correlationId="abc")))
    assert "code" not in payload and "actor" not in payload


@pytest.mark.django_db
@pytest.mark.integration
def test_rejection_log_carries_context_without_token_or_content(
    api_client, manager_headers, process_payload, eventos
):
    """FR-038 e princípio V: contexto suficiente, sem credencial nem conteúdo do Edital."""
    edital = publish_original(api_client, manager_headers, process_payload)
    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/encerramentos",
        {"reason": "Revisão obsoleta com conteúdo sigiloso"},
        format="json",
        **actor_headers("gestor", ["edital:encerrar"], if_match=1, key="obs-key-00000001"),
    )
    assert resposta.status_code == 412

    evento = next(r for r in eventos if r.getMessage() == "operacao_recusada")
    assert evento.code == "stale_revision"
    assert evento.status == 412
    assert evento.actor == "gestor"
    assert evento.correlationId

    serializado = JsonFormatter().format(evento)
    assert "Bearer" not in serializado
    assert "edital:encerrar" not in serializado
    assert "sigiloso" not in serializado


@pytest.mark.django_db
@pytest.mark.integration
def test_conflicts_and_rejections_are_counted_separately(
    api_client, manager_headers, process_payload
):
    """Disputa por recurso (409/412/428) é contada à parte de erro de quem chamou."""
    edital = publish_original(api_client, manager_headers, process_payload)
    gestor = ["edital:encerrar", "edital:cancelar"]

    # 412: revisão obsoleta — disputa.
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/encerramentos",
        {"reason": "Obsoleta"},
        format="json",
        **actor_headers("gestor", gestor, if_match=1, key="obs-key-00000002"),
    )
    # 428: sem If-Match — disputa.
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/encerramentos",
        {"reason": "Sem precondição"},
        format="json",
        **actor_headers("gestor", gestor, key="obs-key-00000003"),
    )
    # 403: sem permissão — recusa, não disputa.
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/cancelamentos",
        {"reason": "Negado"},
        format="json",
        **actor_headers("intruso", [], if_match=edital.revision, key="obs-key-00000004"),
    )

    leitura = metrics.snapshot()
    assert leitura["conflicts"] == {"precondition_required": 1, "stale_revision": 1}
    assert leitura["conflictTotal"] == 2
    assert leitura["rejections"] == {"forbidden": 1}
    assert leitura["rejectionTotal"] == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_health_answers_without_touching_the_database(api_client, django_assert_num_queries):
    with django_assert_num_queries(0):
        resposta = api_client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


@pytest.mark.django_db
@pytest.mark.integration
def test_readiness_checks_database_and_pending_migrations(api_client):
    resposta = api_client.get("/readiness")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "ready"
    assert corpo["checks"] == {"database": True, "migrations": True}


@pytest.mark.django_db
@pytest.mark.integration
def test_readiness_reports_503_when_the_database_is_unreachable(api_client, monkeypatch):
    from processo_seletivo.shared.api import operacional

    monkeypatch.setattr(operacional.ReadinessView, "_database", lambda self: False)
    resposta = api_client.get("/readiness")
    assert resposta.status_code == 503
    assert resposta.json()["status"] == "not_ready"
    assert resposta.json()["checks"]["database"] is False


@pytest.mark.django_db
@pytest.mark.integration
def test_metrics_require_explicit_permission(api_client):
    assert api_client.get("/metrics").status_code == 401
    negado = api_client.get("/metrics", **actor_headers("curioso", ["edital:elaborar"]))
    assert negado.status_code == 403

    autorizado = api_client.get("/metrics", **actor_headers("sre", ["observabilidade:consultar"]))
    assert autorizado.status_code == 200
    assert set(autorizado.json()) == {
        "uptimeSeconds",
        "conflicts",
        "conflictTotal",
        "rejections",
        "rejectionTotal",
    }


@pytest.mark.integration
def test_operational_endpoints_stay_outside_the_business_contract():
    """Health, readiness e métricas não são API institucional e não entram no openapi.yaml."""
    from django.urls import get_resolver

    raiz = {
        str(pattern.pattern)
        for pattern in get_resolver().url_patterns
        if not str(pattern.pattern).startswith("api/")
    }
    assert raiz == {"health", "readiness", "metrics"}
