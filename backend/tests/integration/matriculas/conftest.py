"""O cenário da exportação. As funções moram em `tests/fixtures/matriculas.py`."""

import pytest

from processo_seletivo.matriculas.domain import nomes
from tests.conftest import ator_institucional
from tests.fixtures.matriculas import montar_cenario_da_exportacao


@pytest.fixture
def quem_exporta():
    """O ator com a permissão **própria** da feature, e nada além dela (`FR-455`).

    Ele **não** tem `inscricao:consultar`: ler um dossiê por vez e baixar o conjunto inteiro são
    atos distintos, e a exportação não pode depender da permissão do outro.
    """
    return ator_institucional("exportadora", nomes.EXPORTAR)


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Dois convocados, os dois com requerimento enviado — o caso em que o arquivo sai."""
    return montar_cenario_da_exportacao(gestor, api_client, manager_headers, process_payload)
