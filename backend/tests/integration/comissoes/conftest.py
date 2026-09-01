"""Precondições da 011, compartilhadas por integração e unidade do mesmo diretório."""

import pytest

from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.comissao import ETAPA_A1, ETAPA_A2
from tests.fixtures.comissao import publicar_processo_com_etapas
from tests.fixtures.edital import identificador

ESCOPO = "cefor"


def ator(subject, *permissoes, escopo=ESCOPO):
    return Actor(subject, escopo, frozenset(permissoes))


@pytest.fixture
def gestor():
    return ator("carlos", "comissao:gerir")


@pytest.fixture
def sem_nada():
    return ator("estranho")


@pytest.fixture
def edital_a(db, api_client, manager_headers, process_payload):
    return publicar_processo_com_etapas(api_client, manager_headers, process_payload)


@pytest.fixture
def processo_a(edital_a):
    return edital_a.processo


@pytest.fixture
def edital_b(db, api_client, manager_headers):
    return publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0002"},
        {
            "institutionalCode": "PS-2026-002",
            "title": "Outro Processo",
            "firstEdital": {"number": "02", "year": 2026, "title": "Segundo Edital"},
        },
        seed=1,
    )


@pytest.fixture
def etapa_a1():
    return identificador(ETAPA_A1, 0)


@pytest.fixture
def etapa_a2():
    return identificador(ETAPA_A2, 0)


@pytest.fixture
def etapa_b1():
    return identificador(ETAPA_A1, 1)
