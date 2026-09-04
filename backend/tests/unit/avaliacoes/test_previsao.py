"""A ausência tem um leitor só, e é este."""

from decimal import Decimal

import pytest

from processo_seletivo.avaliacoes.domain.formas import Forma
from processo_seletivo.avaliacoes.domain.previsao import (
    avaliacoes_previstas,
    decisoria,
    forma_publicada,
    pontuacao_maxima,
    rotulos,
)


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


@pytest.mark.parametrize(
    ("etapa", "esperado"),
    [
        ({}, Forma.PONTUADA),
        ({"forma": None}, Forma.PONTUADA),
        ({"forma": "PONTUADA"}, Forma.PONTUADA),
        ({"forma": "DECISORIA"}, Forma.DECISORIA),
    ],
)
def test_a_forma_que_a_etapa_publicou(etapa, esperado):
    assert forma_publicada(etapa) == esperado


def test_ausencia_e_nulo_sao_lidos_como_pontuada():
    """FR-120: até a versão 5 o domínio não admitia outra forma, e escrever isso não inventa nada.

    O leitor continua defensivo depois do salto para 6, onde a chave existe sempre: é a validação de
    publicação que recusa o nulo, e não este leitor, que também atravessa conteúdo antigo.
    """
    assert forma_publicada({}) == forma_publicada({"forma": None}) == Forma.PONTUADA


def test_forma_fora_do_par_cai_na_ausencia_sem_estourar():
    """O mesmo tratamento que `avaliacoes_previstas` dá a lixo, e pela mesma razão."""
    assert forma_publicada({"forma": "ORDINAL"}) == Forma.PONTUADA
    assert forma_publicada({"forma": 7}) == Forma.PONTUADA
    assert forma_publicada(None) == Forma.PONTUADA


def test_decisoria_e_o_atalho_da_mesma_leitura():
    assert decisoria({"forma": "DECISORIA"})
    assert not decisoria({"forma": "PONTUADA"})
    assert not decisoria({})


def test_os_rotulos_vem_do_edital_e_nao_do_dominio():
    """Não há default institucional: rótulo que o Edital não publicou não é aplicado (D-008)."""
    assert rotulos({"rotuloFavoravel": "Deferido", "rotuloDesfavoravel": "Indeferido"}) == (
        "Deferido",
        "Indeferido",
    )
    assert rotulos({"forma": "DECISORIA"}) == (None, None)
    assert rotulos({}) == (None, None)


def test_rotulo_em_branco_nao_e_rotulo():
    """Um PDF com `""` no lugar do indeferimento não diz nada a quem lê o Edital."""
    assert rotulos({"rotuloFavoravel": "  ", "rotuloDesfavoravel": ""}) == (None, None)
