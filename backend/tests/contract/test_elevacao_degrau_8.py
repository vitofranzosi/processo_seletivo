"""Edital publicado antes do degrau 8 continua vivo — e a ausência da janela **significa** algo.

O degrau eleva o conteúdo sem inventar norma: o marco ganha `appealWindow: None`, e `None` quer
dizer **janela não declarada**. Não é prazo de zero dias, não é "cabe recurso sem prazo", e não é
pendência a resolver: é a afirmação de que aquele Edital não publicou prazo, e por isso a
tempestividade continua sendo juízo de admissibilidade motivado (FR-028, FR-029, SC-016).

Um Edital elevado **continua retificável e publicável**: elevar não pode ser a porta pela qual um
certame em curso deixa de funcionar.
"""

import pytest

from processo_seletivo.publicacoes.domain.elevacao import (
    DEGRAUS_DE_MARCO,
    elevar,
    elevar_marco,
    elevar_valor,
)
from processo_seletivo.recursos.domain.janela import computavel, declaracao_do_marco
from processo_seletivo.shared.canonical import SCHEMA_VERSION

pytestmark = [pytest.mark.contract]


def conteudo_na_versao(versao):
    """Um conteúdo mínimo na versão anterior ao degrau, com um marco sem janela declarada."""
    return {
        "schemaVersion": versao,
        "stages": [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "code": "E1",
                "name": "Análise",
                "weight": "1.0000",
                "evaluationsPerRegistration": 1,
                "maximumScore": None,
                "forma": "PONTUADA",
                "rotuloFavoravel": None,
                "rotuloDesfavoravel": None,
            }
        ],
        "profiles": [
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "code": "P1",
                "declaredFacts": [],
                "classificationMilestones": [
                    {
                        "id": "33333333-3333-3333-3333-333333333333",
                        "code": "M1",
                        "name": "Final",
                        "stages": ["11111111-1111-1111-1111-111111111111"],
                        "operation": "SOMA_PONDERADA",
                        "normalization": "NENHUMA",
                        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
                        "tiebreakers": [],
                    }
                ],
            }
        ],
        "maxInscricoesPorCandidato": None,
    }


def test_o_degrau_8_existe_e_grafa_a_ausencia_como_nula():
    assert DEGRAUS_DE_MARCO == {8: {"appealWindow": None}}
    assert SCHEMA_VERSION == 8


def test_o_edital_anterior_eleva_sem_inventar_janela():
    elevado = elevar(conteudo_na_versao(7))

    marco = elevado["profiles"][0]["classificationMilestones"][0]
    assert elevado["schemaVersion"] == 8
    assert marco["appealWindow"] is None
    assert computavel(marco["appealWindow"]) is None


def test_a_ausencia_significa_janela_nao_declarada_e_nao_prazo_zero():
    """A distinção que a decisão institucional fez, e que o esquema precisa preservar.

    Prazo de zero dias recusaria toda interposição; janela não declarada a permite enquanto o
    objeto for vigente, e devolve a tempestividade ao juízo humano. Confundir as duas transformaria
    todo Edital antigo num certame sem recurso.
    """
    elevado = elevar(conteudo_na_versao(7))
    marco = elevado["profiles"][0]["classificationMilestones"][0]

    assert declaracao_do_marco(elevado, marco["id"]) is None
    assert computavel({"admits": True, "durationDays": 0}) is None
    assert computavel(None) is None


def test_a_elevacao_e_idempotente():
    """Conteúdo já na versão vigente atravessa **igual**, e sem pagar cópia de dicionário."""
    ja_elevado = elevar(conteudo_na_versao(7))

    assert elevar(ja_elevado) is ja_elevado


def test_o_marco_que_ja_declara_janela_nao_e_reescrito():
    declarada = {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"}

    marco = elevar_marco({"id": "m1", "appealWindow": declarada}, de=7)

    assert marco["appealWindow"] == declarada


def test_o_conteudo_de_versao_desconhecida_atravessa_intacto():
    """Versão que a conversão não conhece é recusada onde a recusa é dita, e não carimbada aqui."""
    antigo = {"schemaVersion": 3, "profiles": []}

    assert elevar(antigo) is antigo


# ---------------------------------------------------------------------------
# T109 — o endereçamento por Retificação
# ---------------------------------------------------------------------------


def test_a_retificacao_endereca_o_marco_inteiro_e_a_elevacao_o_alcanca():
    """Substituir o marco inteiro eleva o `newValue`, como já acontece com a Etapa."""
    caminho = (
        "/profiles/id=22222222-2222-2222-2222-222222222222"
        "/classificationMilestones/id=33333333-3333-3333-3333-333333333333"
    )
    marco = {"id": "33333333-3333-3333-3333-333333333333", "code": "M1"}

    elevado = elevar_valor(caminho, marco)

    assert elevado["appealWindow"] is None


def test_o_campo_da_janela_e_enderecavel_e_nao_e_elevado():
    """**O objeto aninhado é alvo direto**, e por isso não entra em `COLECOES_ATOMICAS` (T-007).

    `changes.py` resolve `appealWindow` como campo do marco — um `REPLACE` ali substitui o objeto
    inteiro, que é exatamente a semântica que a janela pede: os três campos valem juntos, e
    retificar só a duração deixando a unidade para trás seria retificar pela metade.

    E **não** se eleva: quem endereça o campo já está escrevendo a forma nova.
    """
    caminho = (
        "/profiles/id=22222222-2222-2222-2222-222222222222"
        "/classificationMilestones/id=33333333-3333-3333-3333-333333333333/appealWindow"
    )
    valor = {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"}

    assert elevar_valor(caminho, valor) == valor


def test_a_retificacao_alcanca_a_janela_no_conteudo_publicado():
    """O caminho resolve de fato — e não só na leitura de quem escreveu o teste."""
    from processo_seletivo.publicacoes.domain.changes import apply_changes

    conteudo = elevar(conteudo_na_versao(7))
    caminho = (
        "/profiles/id=22222222-2222-2222-2222-222222222222"
        "/classificationMilestones/id=33333333-3333-3333-3333-333333333333/appealWindow"
    )
    nova = {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"}

    resultado, _registro = apply_changes(
        conteudo,
        [{"targetPath": caminho, "operation": "REPLACE", "newValue": nova}],
        publication_id="44444444-4444-4444-4444-444444444444",
    )

    marco = resultado["profiles"][0]["classificationMilestones"][0]
    assert marco["appealWindow"] == nova
    assert computavel(marco["appealWindow"]) == {"dias": 5, "unidade": "DIAS_CORRIDOS"}
