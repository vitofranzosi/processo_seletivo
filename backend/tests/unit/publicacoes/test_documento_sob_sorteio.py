"""Sob sorteio declarado, o documento não afirma conta nem empate (067, ED-03, FR-1313, FR-1314).

No cenário A da auditoria de 08/10/2026, cada um dos quatro marcos por sorteio imprimia
"Arredondamento: 2 casas decimais, meio para cima" e "Empate no corte: Havendo empate na última
posição, essa quantidade não é excedida." — uma conta que não existe e um empate impossível: a ordem
sorteada é total, e cada posição é única. A regra é pela forma **declarada** (D-004): o marco do
acervo que não a declara sai como sempre saiu.

**Na redação 2 desde a `069`**: o arredondamento é "A nota final é arredondada…" e o empate é "Se
houver empate na última posição…" (C11 a C14, K5, K6 do contrato de redação).
"""

import pytest

from tests.unit.publicacoes.cenarios_da_auditoria import composto
from tests.unit.publicacoes.test_pdf import texto_de
from tests.unit.publicacoes.test_pdf_classificacao import com_classificacao, marco, texto

ARREDONDAMENTO = (
    "A nota final é arredondada para 2 casas decimais; a partir da metade, arredonda-se para cima."
)
EMPATE = "Se houver empate na última posição"

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

    assert "arredondada" not in corrido
    assert EMPATE not in corrido
    # O resto do bloco do marco continua.
    for trecho in (
        "Sorteio",
        "Participam do sorteio",
        "Recurso",
        "Seguem no processo os 10 (dez) primeiros classificados",
        "Depois, poderão ser chamados",
    ):
        assert trecho in corrido, trecho


def test_sob_pontuacao_os_dois_continuam():
    corrido = _texto("POR_PONTUACAO")

    assert ARREDONDAMENTO in corrido
    assert EMPATE in corrido


@pytest.mark.parametrize("forma", ["", None])
def test_o_acervo_sem_forma_declarada_sai_como_sempre_saiu(forma):
    """Marco anterior à `030`, com método próprio: a forma inferida seria sorteio, e não vale."""
    corrido = _texto(forma, drawMethod=METODO_PROPRIO)

    assert ARREDONDAMENTO in corrido
    assert EMPATE in corrido


def test_o_cenario_a_da_auditoria_nao_tem_nenhuma_das_duas_linhas():
    corrido = " ".join(texto_de(composto("A")).split())

    # Uma vez, e não quatro, desde a `068`: os quatro marcos são idênticos e saem na subseção comum.
    assert corrido.count("Participam do sorteio todas as inscrições enviadas.") == 1
    assert "arredondada" not in corrido
    assert EMPATE not in corrido
    assert corrido.count("Depois, poderão ser chamados outros candidatos") == 1
