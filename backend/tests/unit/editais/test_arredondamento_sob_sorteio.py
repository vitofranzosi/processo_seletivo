"""Sob sorteio declarado, a publicação não exige arredondamento (067, ED-03, FR-1311, FR-1312).

A auditoria de 08/10/2026 só conseguiu montar o cenário A — pós-graduação com classificação por
sorteio — declarando um arredondamento que o marco nunca usa: *"O arredondamento do marco deve
declarar `scale` como inteiro."* O documento, depois, imprimia "Arredondamento: 2 casas decimais"
sob uma ordem sorteada, onde não há nota. A dispensa é a metade da validação; a do compositor está
em `tests/unit/publicacoes/test_documento_sob_sorteio.py`. Corrigir só uma deixaria o defeito vivo.
"""

import copy

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    blocking_findings,
    validate_for_publication,
)
from tests.fixtures.snapshot import rascunho_completo
from tests.unit.editais.test_marco_classificatorio import PERFIL, conteudo_com_marco

ARREDONDAMENTO = "milestone_rounding_invalid"
METODO_PROPRIO = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Loteria Federal",
    "occurrence": "5901",
}


def codigos(conteudo, ato=ATO_DE_PUBLICACAO):
    return {
        achado.code for achado in blocking_findings(validate_for_publication(conteudo, ato=ato))
    }


def sorteios(rounding):
    """O rascunho completo da suíte — três marcos, todos por sorteio declarado — com `rounding`."""
    conteudo = rascunho_completo()
    for perfil in conteudo["profiles"]:
        for marco in perfil["classificationMilestones"]:
            assert marco["orderProduction"] == "POR_SORTEIO"
            if rounding is AUSENTE:
                marco.pop("rounding", None)
            else:
                marco["rounding"] = copy.deepcopy(rounding)
    return conteudo


AUSENTE = object()


def test_a_contraprova_o_rascunho_com_arredondamento_publica():
    assert ARREDONDAMENTO not in codigos(sorteios({"scale": 2, "mode": "MEIO_PARA_CIMA"}))


@pytest.mark.parametrize(
    "rounding",
    [AUSENTE, None, {}, {"scale": None, "mode": None}],
    ids=["ausente", "nulo", "vazio", "nulos"],
)
@pytest.mark.parametrize("ato", [ATO_DE_PUBLICACAO, ATO_DE_RETIFICACAO])
def test_sob_sorteio_a_ausencia_nao_e_recusada(rounding, ato):
    assert ARREDONDAMENTO not in codigos(sorteios(rounding), ato)


@pytest.mark.parametrize(
    "rounding",
    [
        {"scale": 9, "mode": "X"},
        {"scale": 2},
        {"mode": "MEIO_PARA_CIMA"},
        {"scale": "2", "mode": "MEIO_PARA_CIMA"},
        {"scale": 2, "mode": "ROUND_HALF_UP"},
    ],
    ids=["fora-da-faixa", "sem-modo", "sem-escala", "escala-texto", "grafia-da-biblioteca"],
)
def test_sob_sorteio_o_declarado_continua_conferido_na_forma(rounding):
    """FR-1312, como o desfecho de empate declarado sob sorteio (`FR-928`): a ausência é livre."""
    assert ARREDONDAMENTO in codigos(sorteios(rounding))


@pytest.mark.parametrize("ato", [ATO_DE_PUBLICACAO, ATO_DE_RETIFICACAO])
def test_sob_pontuacao_a_ausencia_continua_recusada(ato):
    assert ARREDONDAMENTO in codigos(conteudo_com_marco(rounding={}), ato)


def test_sem_forma_declarada_a_ausencia_continua_recusada_mesmo_com_metodo_proprio():
    """O acervo anterior à `030`: a dispensa é pela forma declarada (D-004), não pela inferida."""
    conteudo = conteudo_com_marco(rounding={})
    perfil = next(item for item in conteudo["profiles"] if item["id"] == PERFIL["B"])
    (marco,) = perfil["classificationMilestones"]
    marco["orderProduction"] = ""
    marco["drawMethod"] = METODO_PROPRIO
    assert ARREDONDAMENTO in codigos(conteudo)


def test_a_retificacao_que_passa_de_sorteio_para_pontuacao_sem_arredondamento_e_recusada():
    """Caso-limite da spec: quem passa a ordenar por nota tem de dizer como a nota se arredonda."""
    conteudo = sorteios({})
    marco = conteudo["profiles"][0]["classificationMilestones"][0]
    marco["orderProduction"] = "POR_PONTUACAO"
    assert ARREDONDAMENTO in codigos(conteudo, ATO_DE_RETIFICACAO)
