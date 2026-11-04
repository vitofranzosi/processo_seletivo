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


@pytest.fixture
def provedor(settings):
    """O provedor simulado configurado, como em `tests/seguranca/conftest.py`."""
    from tests.fixtures import provedor_simulado

    provedor_simulado.limpar()
    settings.GESTAO_PROVEDOR_INSTITUCIONAL = provedor_simulado.CAMINHO
    yield provedor_simulado
    provedor_simulado.limpar()


@pytest.fixture
def seletor(settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
