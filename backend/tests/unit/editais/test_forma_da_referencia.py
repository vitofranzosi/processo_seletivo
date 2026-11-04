"""A forma da referência da Loteria Federal, conferida na gravação (116, US5, FR-3623–FR-3626).

**Só algarismos, e nada mais.** A API da Caixa recusa com HTTP 400 até a grafia `6106-9`, que é a do
próprio comunicado dela, e o defeito só apareceria no dia do sorteio. É regra local, sem rede: a
gravação do rascunho a confere, e não consulta a Caixa (D-007).
"""

import copy

import pytest

from processo_seletivo.editais.domain.perfis import (
    ProfileValidationError,
    validate_classification_milestones,
    validate_common_draw_method,
)
from processo_seletivo.editais.domain.validation import (
    ATO_DE_RETIFICACAO,
    validate_for_publication,
)
from tests.fixtures.edital import DRAW_METHOD, complete_draft

CORRECAO = "informe só o número do concurso, como 6106 — sem dígito verificador, texto ou ano"


def _metodo(ocorrencia, fonte="Loteria Federal"):
    metodo = copy.deepcopy(DRAW_METHOD)
    metodo.update({"source": fonte, "occurrence": ocorrencia})
    return metodo


def _marco(metodo):
    return {
        "id": "aaaaaaaa-0000-4000-8000-000000001161",
        "code": "SORTEIO",
        "name": "Sorteio público",
        "orderProduction": "POR_SORTEIO",
        "stages": [],
        "tiebreakers": [],
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "cutRule": {
            "targetKind": "FIXED",
            "targetCount": 2,
            "surplusCount": 0,
            "tieOutcome": "STRICT",
            "governedStage": "NONE",
            "continuation": "NONE",
        },
        "drawMethod": metodo,
    }


@pytest.mark.parametrize(
    "grafia", ["6106-9", "Concurso 6115", "6115/2026", "0", "-1", "6114.0", "1234567", " 6115"]
)
def test_as_grafias_fora_da_forma_sao_recusadas_com_a_correcao(grafia):
    with pytest.raises(ProfileValidationError) as recusa:
        validate_classification_milestones([_marco(_metodo(grafia))])
    assert f'"{grafia}"' in str(recusa.value)
    assert CORRECAO in str(recusa.value)


def test_o_metodo_comum_recebe_a_mesma_recusa():
    with pytest.raises(ProfileValidationError) as recusa:
        validate_common_draw_method(_metodo("6106-9"))
    assert CORRECAO in str(recusa.value)


@pytest.mark.parametrize("grafia", ["6115", "1", "006114", "999999"])
def test_o_numero_e_aceito(grafia):
    validate_classification_milestones([_marco(_metodo(grafia))])


@pytest.mark.parametrize("grafia", ["Concurso 5900", "5900", "0099"])
def test_a_fonte_de_demonstracao_aceita_o_que_aceitava(grafia):
    """A forma é da fonte (FR-3625): a de demonstração continua com a guarda da `035`, e só."""
    validate_classification_milestones([_marco(_metodo(grafia, "Fonte de demonstração"))])


def test_a_retificacao_do_acervo_nao_reconfere_a_forma():
    """A FR-514 da `035`: o conteúdo que a Retificação não toca não é reconferido (FR-3624)."""
    conteudo = complete_draft()
    conteudo["profiles"][0]["classificationMilestones"][0]["drawMethod"] = _metodo("Concurso 6100")
    codigos = {achado.code for achado in validate_for_publication(conteudo, ato=ATO_DE_RETIFICACAO)}
    assert "draw_method_invalid" not in codigos
    na_publicacao = {achado.code for achado in validate_for_publication(conteudo)}
    assert "draw_method_invalid" in na_publicacao
