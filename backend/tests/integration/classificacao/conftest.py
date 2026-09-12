"""A fixture do cenário do corte, no lugar que o pytest tem para ela (014).

Os atalhos e as constantes moram em `tests/fixtures/corte.py`: importar uma **função** de outro
módulo é comum, e importar uma **fixture** a redefine no importador.
"""

import pytest

from tests.fixtures.corte import montar_cenario_do_corte


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """Quatro inscritos, três pontuados, ordem emitida — e um alvo de dois."""
    return montar_cenario_do_corte(gestor, api_client, manager_headers, process_payload)
