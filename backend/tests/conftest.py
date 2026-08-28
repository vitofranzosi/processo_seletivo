import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def manager_headers():
    return {
        "HTTP_AUTHORIZATION": "Bearer gestor-a|cefor|processo:criar,processo:ativar,edital:criar",
        "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0001",
        "HTTP_X_CORRELATION_ID": "test-correlation-id",
    }


@pytest.fixture
def process_payload():
    return {
        "institutionalCode": "PS-2026-001",
        "title": "Processo Seletivo 2026",
        "firstEdital": {"number": "01", "year": 2026, "title": "Primeiro Edital"},
    }
