"""O cenário da formalização. As funções moram em `tests/fixtures/formalizacao.py`."""

import pytest

from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.formalizacao import montar_cenario_da_formalizacao

RUI = "rui"


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Cinco aptas, uma indeferida e uma sem resposta, no molde do 72/2026."""
    return montar_cenario_da_formalizacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        aptas=5,
        indeferidas=1,
        sem_resposta=1,
    )


@pytest.fixture
def rui():
    """O servidor do Registro Acadêmico, com o papel Formalização na unidade."""
    return Actor(RUI, "cefor", frozenset({"formalizacao:acessar"}))
