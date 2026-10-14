"""Os falsos do piloto (071) e a rede recusada para todo caso do pacote (`FR-1519`)."""

import pytest

from tests.fixtures.inferencia import contador_falso, porta_falsa, sem_rede  # noqa: F401


@pytest.fixture(autouse=True)
def _nenhum_caso_alcanca_a_rede(sem_rede):  # noqa: F811
    """O piloto fala com serviço externo; nenhum caso deste pacote pode."""
