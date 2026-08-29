import pytest
from django.db import connections
from rest_framework.test import APIClient


def encerrar_conexoes_da_thread():
    """Fecha as conexões desta thread, inclusive a subjacente do SQLite em memória.

    `connections.close_all()` não basta: para banco em memória o backend do SQLite trata
    `close()` como no-op, porque fechar destruiria o banco. Como o Django monta o banco de teste
    com `cache=shared` quando há threads, ele sobrevive enquanto qualquer conexão continuar
    aberta — e a da thread principal continua. Sem isto cada thread deixa uma `sqlite3.Connection`
    para o coletor de lixo, e o ResourceWarning aparece atribuído ao teste seguinte, que não tem
    relação nenhuma com ele.
    """
    for conexao in connections.all(initialized_only=True):
        subjacente = conexao.connection
        em_memoria = getattr(conexao, "is_in_memory_db", lambda: False)()
        conexao.close()
        if em_memoria and subjacente is not None:
            subjacente.close()
            conexao.connection = None


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
