"""A elevação escreve a forma nova sem inventar conteúdo — e não toca no que não é Etapa."""

import pytest

from processo_seletivo.publicacoes.domain.elevacao import (
    elevar,
    elevar_alteracoes,
    elevar_etapa,
    elevar_valor,
)
from processo_seletivo.shared.canonical import SCHEMA_VERSION, canonical_sha256

ETAPA_V4 = {
    "id": "00000000-0000-0000-0000-0000000000e1",
    "name": "Análise documental",
    "order": 0,
    "weight": None,
    "eliminatory": True,
    "classificatory": False,
    "minimumScore": "70.0000",
    "scheduleEventId": None,
}


def conteudo(versao, etapas):
    return {"schemaVersion": versao, "title": "Edital", "stages": etapas}


def test_a_etapa_antiga_ganha_o_que_a_ausencia_ja_dizia():
    elevada = elevar_etapa(ETAPA_V4)

    assert elevada["evaluationsPerRegistration"] == 1
    assert elevada["maximumScore"] is None
    # E nada mais muda: elevar não é reescrever.
    assert {k: v for k, v in elevada.items() if k in ETAPA_V4} == ETAPA_V4


def test_elevar_e_idempotente():
    uma = elevar(conteudo(4, [ETAPA_V4]))
    duas = elevar(uma)

    assert canonical_sha256(uma) == canonical_sha256(duas)
    assert uma["schemaVersion"] == SCHEMA_VERSION


def test_o_que_ja_declarou_atravessa_intacto():
    declarada = {**ETAPA_V4, "evaluationsPerRegistration": 2, "maximumScore": "100.0000"}

    assert elevar_etapa(declarada) == declarada


def test_nulo_declarado_continua_nulo():
    """Ausente e nulo significam a mesma coisa, e é por isso que a função é idempotente."""
    nula = {**ETAPA_V4, "evaluationsPerRegistration": None, "maximumScore": None}

    assert elevar_etapa(nula) == nula


@pytest.mark.parametrize(
    ("caminho", "eleva"),
    [
        ("/stages/-", True),
        ("/stages/id=00000000-0000-0000-0000-0000000000e1", True),
        ("/stages/id=00000000-0000-0000-0000-0000000000e1/minimumScore", False),
        ("/profiles/-", False),
        ("/profiles/id=00000000-0000-0000-0000-0000000000p1", False),
        ("/documentRequirements/-", False),
    ],
)
def test_a_classificacao_de_caminho_e_declarada(caminho, eleva):
    """A tabela de T-001, uma linha por vez: entidade eleva, escalar e outras coleções não."""
    resultado = elevar_valor(caminho, ETAPA_V4)

    assert ("evaluationsPerRegistration" in resultado) is eleva


def test_escalar_nao_e_tocado():
    """`REPLACE` de nota mínima carrega um decimal. Elevá-lo seria corrompê-lo."""
    caminho = "/stages/id=00000000-0000-0000-0000-0000000000e1/minimumScore"

    assert elevar_valor(caminho, "80.0000") == "80.0000"


def test_a_colecao_inteira_eleva_item_a_item():
    elevada = elevar_valor("/stages", [ETAPA_V4, ETAPA_V4])

    assert all(item["evaluationsPerRegistration"] == 1 for item in elevada)


def test_remove_nao_tem_valor_a_elevar():
    alteracoes = [{"targetPath": "/stages/id=x", "operation": "REMOVE"}]

    assert elevar_alteracoes(alteracoes) == alteracoes


def test_o_ato_que_acrescenta_etapa_chega_na_forma_vigente():
    """O caso que trava a materialização quando não é elevado: ADD por `/stages/-` (T-001)."""
    alteracoes = [{"targetPath": "/stages/-", "operation": "ADD", "newValue": ETAPA_V4}]

    elevadas = elevar_alteracoes(alteracoes)

    assert elevadas[0]["newValue"]["evaluationsPerRegistration"] == 1
    assert elevadas[0]["newValue"]["maximumScore"] is None
