"""O documento diz a quem a Etapa restrita se aplica, e só ela (163, FR-6983, D-008, SC-2310).

A Etapa para todas sai com o texto de antes, e é o que recompõe o acervo byte a byte: a chave
ausente (Edital publicado antes do degrau 22) e o `null` do degrau compõem o mesmo documento.
"""

import copy

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from processo_seletivo.publicacoes.infrastructure.pdf import REDACAO_1, Composicao

FRASE = "Aplica-se somente aos candidatos inscritos na modalidade Pretos e pardos (PPI)."


def _snapshot(alcance):
    return {
        "profiles": [
            {
                "id": "perfil",
                "code": "C1",
                "competitionModalities": [{"id": "m", "code": "PPI", "name": "Pretos e pardos"}],
            }
        ],
        "stages": [
            {
                "id": "hetero",
                "name": "Heteroidentificação",
                "order": 1,
                "eliminatory": True,
                "classificatory": False,
                "forma": "DECISORIA",
                "rotuloFavoravel": "Confirmada",
                "rotuloDesfavoravel": "Não confirmada",
                "criteria": [],
                "modalityCodes": alcance,
            }
        ],
        "documentRequirements": [],
        "schedule": [],
    }


def _textos(snapshot, redacao=None):
    composicao = Composicao(**({"redacao": redacao} if redacao is not None else {}))
    pdf._etapas(composicao, snapshot, 6, pdf._Numerador())
    return [item[1] for item in composicao.itens if item[0] == "texto"]


def test_a_redacao_vigente_diz_o_alcance_em_frase():
    assert FRASE in _textos(_snapshot(["PPI"]))


def test_a_redacao_1_diz_o_alcance_no_par():
    textos = _textos(_snapshot(["PPI"]), REDACAO_1)

    assert any("Somente candidatos inscritos em Pretos e pardos (PPI)" in texto for texto in textos)


@pytest.mark.parametrize("redacao", [None, REDACAO_1], ids=["vigente", "redacao-1"])
def test_a_etapa_para_todas_compoe_o_texto_de_antes(redacao):
    """SC-2310: `null` e a chave ausente produzem o mesmo texto, sem frase de alcance."""
    com_nulo = _snapshot(None)
    sem_chave = copy.deepcopy(com_nulo)
    del sem_chave["stages"][0]["modalityCodes"]

    textos = _textos(com_nulo, redacao)

    assert textos == _textos(sem_chave, redacao)
    assert not any(
        "Aplica-se somente" in texto or "Somente candidatos" in texto for texto in textos
    )
