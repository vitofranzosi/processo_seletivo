"""Apoio dos testes da identidade institucional (106): o provedor simulado e a segunda unidade."""

import pytest

from tests.fixtures import provedor_simulado
from tests.fixtures.autoridades import registrar_unidade


@pytest.fixture
def provedor(settings):
    """O provedor simulado configurado, e os bilhetes limpos antes e depois do caso."""
    provedor_simulado.limpar()
    settings.GESTAO_PROVEDOR_INSTITUCIONAL = provedor_simulado.CAMINHO
    yield provedor_simulado
    provedor_simulado.limpar()


@pytest.fixture
def campus_a(db):
    return registrar_unidade("campus-a")
