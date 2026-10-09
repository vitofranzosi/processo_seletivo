"""Sob sorteio declarado, o documento não afirma conta nem empate (067, ED-03, FR-1313, FR-1314).

No cenário A da auditoria de 08/10/2026, cada um dos quatro marcos por sorteio imprimia
"Arredondamento: 2 casas decimais, meio para cima" e "Empate no corte: Havendo empate na última
posição, essa quantidade não é excedida." — uma conta que não existe e um empate impossível: a ordem
sorteada é total, e cada posição é única. A regra é pela forma **declarada** (D-004): o marco do
acervo que não a declara sai como sempre saiu.
"""

import pytest

from tests.unit.publicacoes.cenarios_da_auditoria import composto
from tests.unit.publicacoes.test_pdf import texto_de
from tests.unit.publicacoes.test_pdf_classificacao import com_classificacao, marco, texto

METODO_PROPRIO = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Loteria Federal",
    "occurrence": "5901",
}
CORTE = {
    "targetKind": "FIXED",
    "targetCount": 10,
    "surplusCount": 5,
    "tieOutcome": "STRICT",
    "governedStage": "NONE",
    "continuation": "ALLOWED",
}
JANELA = {"admits": True, "durationDays": 2, "unit": "DIAS_CORRIDOS"}


def _texto(forma, **alteracoes):
    """O documento com um marco na forma pedida, com arredondamento e empate **declarados**."""
    declarado = marco(orderProduction=forma, cutRule=CORTE, appealWindow=JANELA, **alteracoes)
    assert declarado["rounding"] and declarado["cutRule"]["tieOutcome"], "declarados, de propósito"
    return texto(com_classificacao(marcos=[declarado]))


def test_sob_sorteio_declarado_nem_arredondamento_nem_empate_mesmo_declarados():
    corrido = _texto("POR_SORTEIO", stages=[], drawMethod=METODO_PROPRIO)

    assert "Arredondamento" not in corrido
    assert "Empate no corte" not in corrido
    # O resto do bloco do marco continua.
    for rotulo in ("Ordem: por sorteio", "Sorteio", "Recurso:", "Corte:", "Continuação:"):
        assert rotulo in corrido, rotulo


def test_sob_pontuacao_os_dois_continuam():
    corrido = _texto("POR_PONTUACAO")

    assert "Arredondamento: 2 casas decimais, meio para cima" in corrido
    assert "Empate no corte: Havendo empate na última posição" in corrido


@pytest.mark.parametrize("forma", ["", None])
def test_o_acervo_sem_forma_declarada_sai_como_sempre_saiu(forma):
    """Marco anterior à `030`, com método próprio: a forma inferida seria sorteio, e não vale."""
    corrido = _texto(forma, drawMethod=METODO_PROPRIO)

    assert "Arredondamento: 2 casas decimais, meio para cima" in corrido
    assert "Empate no corte:" in corrido


def test_o_cenario_a_da_auditoria_nao_tem_nenhuma_das_duas_linhas():
    corrido = " ".join(texto_de(composto("A")).split())

    # Uma vez, e não quatro, desde a `068`: os quatro marcos são idênticos e saem na subseção comum.
    assert corrido.count("Ordem: por sorteio") == 1
    assert "Arredondamento" not in corrido
    assert "Empate no corte" not in corrido
    assert corrido.count("Continuação: Poderá haver chamada") == 1
