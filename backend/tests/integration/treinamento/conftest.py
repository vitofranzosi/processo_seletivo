"""A chave do gerador de cenários (134), ligada para os casos desta pasta."""

import pytest


@pytest.fixture
def treinamento(settings, raiz_de_arquivos):
    """A chave ligada, a fonte de demonstração ligada e uma raiz de arquivos própria."""
    settings.CENARIOS_DE_TREINAMENTO = True
    settings.SORTEIO_FONTE_DE_DEMONSTRACAO = True
    return settings
