"""A fixture do cenário da ocupação. As funções moram em `tests/fixtures/ocupacao.py`."""

import pytest

from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao import montar_cenario_da_ocupacao


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return montar_cenario_da_ocupacao(gestor, api_client, manager_headers, process_payload)


@pytest.fixture
def recorte():
    """O recorte da ampla concorrência do cenário: Perfil, marco e lista nula."""
    return {"perfil_id": PROFILE_ID, "marco_id": MARCO, "lista_id": None}
