"""Edital publicado antes do degrau 13 continua vivo — e a ausência da regra **significa** algo.

A régua deste módulo é a mesma desde o 4→5: converter só quando a ausência tem significado
declarado e **verdadeiro**. `cutRule: None` diz "este marco não corta", e a frase é verdadeira sobre
todo Edital publicado antes deste degrau — a capacidade não existia, e nenhum deles declarou alvo,
excedente, desfecho de empate, Etapa governada ou política de continuação.

**E o sistema não completa a regra por conta própria.** Quatro dos seis campos existem porque não há
padrão honesto para eles: resolver a ausência do desfecho do empate, da Etapa governada ou da
continuação afirmaria norma que ninguém escreveu. Por isso a conversão escreve `None` no objeto
inteiro, e nunca um objeto pela metade — que seria uma regra publicada que o Edital não publicou
(014, D-011, D-012, FR-186).

**Não elevar seria pior do que elevar**, pela razão de sempre: conteúdo em versão diferente da
vigente é recusado, e deixar o acervo em 12 tornaria todo Edital publicado irretificável por causa
de uma feature que ele não usa.
"""

import pytest

from processo_seletivo.publicacoes.domain.changes import apply_changes
from processo_seletivo.publicacoes.domain.elevacao import (
    DEGRAUS_DE_MARCO,
    elevar,
    elevar_marco,
    elevar_valor,
)
from processo_seletivo.shared.canonical import SCHEMA_VERSION

pytestmark = [pytest.mark.contract]

PERFIL = "22222222-2222-2222-2222-222222222222"
MARCO = "33333333-3333-3333-3333-333333333333"
ETAPA = "44444444-4444-4444-4444-444444444444"
CAMINHO_DO_MARCO = f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}"

REGRA = {
    "targetKind": "FIXED",
    "targetCount": 10,
    "surplusCount": 0,
    "tieOutcome": "STRICT",
    "governedStage": ETAPA,
    "continuation": "NONE",
}


def conteudo_na_versao(versao):
    """Um conteúdo mínimo na versão anterior ao degrau, com um marco que não corta."""
    return {
        "schemaVersion": versao,
        "stages": [],
        "attachments": [],
        "documentRequirements": [],
        "maxInscricoesPorCandidato": None,
        "profiles": [
            {
                "id": PERFIL,
                "declaredFacts": [],
                "vacancyTable": [],
                "classificationMilestones": [
                    {"id": MARCO, "code": "M1", "appealWindow": None, "drawMethod": None},
                ],
            }
        ],
    }


def test_o_degrau_13_existe_no_nivel_do_marco_e_grafa_a_ausencia_como_nula():
    assert DEGRAUS_DE_MARCO[13] == {"cutRule": None}
    assert SCHEMA_VERSION >= 13


def test_o_edital_anterior_eleva_sem_inventar_regra():
    elevado = elevar(conteudo_na_versao(12))

    marco = elevado["profiles"][0]["classificationMilestones"][0]
    assert elevado["schemaVersion"] == SCHEMA_VERSION
    assert marco["cutRule"] is None
    # E os degraus anteriores do mesmo objeto continuam valendo.
    assert marco["appealWindow"] is None
    assert marco["drawMethod"] is None


def test_a_ausencia_nao_vira_objeto_pela_metade():
    """`None`, e não `{}` nem um objeto com quatro campos nulos.

    Um objeto pela metade seria uma regra publicada que o Edital não publicou — e passaria pela
    aferição de publicabilidade como "regra declarada sem desfecho de empate", que é impeditivo.
    Editais antigos passariam a ser impublicáveis por uma feature que eles não usam.
    """
    marco = elevar_marco({"id": MARCO}, de=12)

    assert marco["cutRule"] is None


def test_o_marco_que_ja_declara_regra_nao_e_reescrito():
    marco = elevar_marco({"id": MARCO, "cutRule": REGRA}, de=12)

    assert marco["cutRule"] == REGRA


def test_a_elevacao_e_idempotente():
    ja_elevado = elevar(conteudo_na_versao(12))

    assert elevar(ja_elevado) is ja_elevado


def test_a_retificacao_endereca_o_marco_inteiro_e_a_elevacao_o_alcanca():
    elevado = elevar_valor(CAMINHO_DO_MARCO, {"id": MARCO, "code": "M1"})

    assert elevado["cutRule"] is None


def test_o_campo_da_regra_e_enderecavel_e_nao_e_elevado():
    """Objeto aninhado é alvo direto, como a janela recursal e o método — e não é coleção.

    É por isso que `cutRule` **não** entra em `colecoes.py`: em objeto, o segmento do caminho é nome
    de chave literal, e a gramática de endereçamento já o resolve (FR-184).
    """
    assert elevar_valor(f"{CAMINHO_DO_MARCO}/cutRule", REGRA) == REGRA


def test_a_retificacao_alcanca_um_campo_da_regra_no_conteudo_publicado():
    """O caminho resolve de fato, campo a campo — e não só o objeto inteiro (FR-184)."""
    conteudo = elevar(conteudo_na_versao(12))
    conteudo["profiles"][0]["classificationMilestones"][0]["cutRule"] = dict(REGRA)

    resultado, _registro = apply_changes(
        conteudo,
        [
            {
                "targetPath": f"{CAMINHO_DO_MARCO}/cutRule/targetCount",
                "operation": "REPLACE",
                "newValue": 12,
            }
        ],
        publication_id="55555555-5555-5555-5555-555555555555",
    )

    regra = resultado["profiles"][0]["classificationMilestones"][0]["cutRule"]
    assert regra["targetCount"] == 12
    assert regra["tieOutcome"] == "STRICT"
