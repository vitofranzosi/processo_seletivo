"""A ausência tem um leitor só, e é este."""

from decimal import Decimal

import pytest

from processo_seletivo.avaliacoes.domain.previsao import avaliacoes_previstas, pontuacao_maxima


@pytest.mark.parametrize(
    ("etapa", "esperado"),
    [
        ({}, 1),
        ({"evaluationsPerRegistration": None}, 1),
        ({"evaluationsPerRegistration": 1}, 1),
        ({"evaluationsPerRegistration": 2}, 2),
    ],
)
def test_quantas_avaliacoes_a_inscricao_recebe(etapa, esperado):
    assert avaliacoes_previstas(etapa) == esperado


def test_ausente_e_nulo_dizem_a_mesma_coisa():
    """É essa equivalência que torna a elevação idempotente e a precondição comparável."""
    assert avaliacoes_previstas({}) == avaliacoes_previstas({"evaluationsPerRegistration": None})
    assert pontuacao_maxima({}) == pontuacao_maxima({"maximumScore": None}) is None


def test_limite_nao_declarado_nao_vira_teto_inventado():
    """`None` é "o Edital não disse", e não "sem limite" — a diferença é do FR-066."""
    assert pontuacao_maxima({"minimumScore": "70.0000"}) is None


def test_a_maxima_declarada_vem_como_decimal():
    assert pontuacao_maxima({"maximumScore": "100.0000"}) == Decimal("100.0000")
