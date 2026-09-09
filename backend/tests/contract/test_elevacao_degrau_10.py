"""Edital publicado antes do degrau 10 continua vivo — e a ausência do método **significa** algo.

A régua deste módulo é a mesma desde o 4→5: converter só quando a ausência tem significado
declarado e **verdadeiro**. `drawMethod: None` diz "este marco não declarou método de sorteio", e a
frase é verdadeira sobre todo Edital publicado antes deste degrau — a capacidade não existia, e
nenhum deles declarou fonte, ocorrência, derivação ou regra de normalização.

**E o sistema não escolhe um por conta própria.** Onde o degrau grafa `None`, o comando de
publicação da relação recusa congelar (FR-066): a alternativa — presumir uma fonte padrão —
aplicaria ao Edital uma norma que ele não publicou, que é a mesma degradação que os rótulos da
Etapa e o local do Evento já recusaram.

**Não elevar seria pior do que elevar.** Conteúdo em versão diferente da vigente é recusado por
`_assert_versao_canonica`, e deixar o acervo em 9 tornaria todo Edital publicado irretificável por
causa de uma feature que ele não usa (021, D-013, R-009).
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
CAMINHO_DO_MARCO = f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}"

METODO = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Loteria Federal",
    "occurrence": "5900",
    "occurrenceAt": "2026-11-20T20:00:00-03:00",
    "derivation": "a extração de sábado imediatamente anterior à data publicada",
    "normalization": {"rule": "DIGITOS_EM_SEQUENCIA", "text": "os cinco números, na ordem"},
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "não havendo extração, vale a seguinte",
    },
}


def conteudo_na_versao(versao):
    """Um conteúdo mínimo na versão anterior ao degrau, com um marco sem método."""
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
                "classificationMilestones": [
                    {"id": MARCO, "code": "M1", "appealWindow": None},
                ],
            }
        ],
    }


def test_o_degrau_10_existe_no_nivel_do_marco_e_grafa_a_ausencia_como_nula():
    assert DEGRAUS_DE_MARCO[10] == {"drawMethod": None}
    assert SCHEMA_VERSION >= 10


def test_o_edital_anterior_eleva_sem_inventar_metodo():
    elevado = elevar(conteudo_na_versao(9))

    marco = elevado["profiles"][0]["classificationMilestones"][0]
    assert elevado["schemaVersion"] == SCHEMA_VERSION
    assert marco["drawMethod"] is None
    # E o degrau anterior continua valendo: elevar não desfaz o que o 8 escreveu.
    assert marco["appealWindow"] is None


def test_o_marco_que_ja_declara_metodo_nao_e_reescrito():
    marco = elevar_marco({"id": MARCO, "drawMethod": METODO}, de=9)

    assert marco["drawMethod"] == METODO


def test_a_elevacao_e_idempotente():
    ja_elevado = elevar(conteudo_na_versao(9))

    assert elevar(ja_elevado) is ja_elevado


def test_a_retificacao_endereca_o_marco_inteiro_e_a_elevacao_o_alcanca():
    elevado = elevar_valor(CAMINHO_DO_MARCO, {"id": MARCO, "code": "M1"})

    assert elevado["drawMethod"] is None


def test_o_campo_do_metodo_e_enderecavel_e_nao_e_elevado():
    """Objeto aninhado é alvo direto, como a janela recursal do degrau 8 — e não é coleção.

    É por isso que o `drawMethod` **não** entra em `colecoes.py`: em objeto, o segmento do caminho
    é nome de chave literal, e a gramática de endereçamento já o resolve. Sem gramática nova é
    exatamente o que a FR-014 precisa para deixar de ser promessa.
    """
    assert elevar_valor(f"{CAMINHO_DO_MARCO}/drawMethod", METODO) == METODO


def test_a_retificacao_alcanca_o_metodo_no_conteudo_publicado():
    """O caminho resolve de fato — e não só na leitura de quem escreveu o teste (FR-014)."""
    conteudo = elevar(conteudo_na_versao(9))

    resultado, _registro = apply_changes(
        conteudo,
        [
            {
                "targetPath": f"{CAMINHO_DO_MARCO}/drawMethod",
                "operation": "REPLACE",
                "newValue": METODO,
            }
        ],
        publication_id="44444444-4444-4444-4444-444444444444",
    )

    assert resultado["profiles"][0]["classificationMilestones"][0]["drawMethod"] == METODO


def test_a_retificacao_alcanca_uma_regra_isolada_do_metodo():
    """A regra de substituição sozinha, sem reescrever o método inteiro — e sem gramática nova."""
    conteudo = elevar(conteudo_na_versao(9))
    conteudo["profiles"][0]["classificationMilestones"][0]["drawMethod"] = dict(METODO)
    nova = {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "vale a extração da semana seguinte",
    }

    resultado, _registro = apply_changes(
        conteudo,
        [
            {
                "targetPath": f"{CAMINHO_DO_MARCO}/drawMethod/substitutionRule",
                "operation": "REPLACE",
                "newValue": nova,
            }
        ],
        publication_id="44444444-4444-4444-4444-444444444444",
    )

    metodo = resultado["profiles"][0]["classificationMilestones"][0]["drawMethod"]
    assert metodo["substitutionRule"] == nova
    assert metodo["source"] == METODO["source"], "retificar uma regra não reescreve as demais"
