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


# A mesma Etapa já na forma da versão 5: ela ainda precisa do degrau da 6.
ETAPA_V5 = {**ETAPA_V4, "evaluationsPerRegistration": 1, "maximumScore": None}

# E na forma vigente, que não precisa de degrau nenhum.
ETAPA_V6 = {**ETAPA_V5, "forma": "PONTUADA", "rotuloFavoravel": None, "rotuloDesfavoravel": None}


def conteudo(versao, etapas):
    return {"schemaVersion": versao, "title": "Edital", "stages": etapas}


def test_a_etapa_antiga_ganha_o_que_a_ausencia_ja_dizia():
    """Da v4 até a vigente, os dois degraus de uma vez — e nenhum deles inventa conteúdo."""
    elevada = elevar_etapa(ETAPA_V4)

    assert elevada["evaluationsPerRegistration"] == 1
    assert elevada["maximumScore"] is None
    assert elevada["forma"] == "PONTUADA"
    assert elevada["rotuloFavoravel"] is None and elevada["rotuloDesfavoravel"] is None
    # E nada mais muda: elevar não é reescrever.
    assert {k: v for k, v in elevada.items() if k in ETAPA_V4} == ETAPA_V4


def test_a_etapa_da_versao_5_sobe_um_degrau_so():
    """A cadeia aplica o que vem **depois** da origem, e não tudo sempre (TR-001)."""
    elevada = elevar_etapa(ETAPA_V5, de=5)

    assert elevada == ETAPA_V6


def test_a_etapa_vigente_atravessa_sem_copia():
    assert elevar_etapa(ETAPA_V6, de=SCHEMA_VERSION) is ETAPA_V6


def test_elevar_e_idempotente():
    uma = elevar(conteudo(4, [ETAPA_V4]))
    duas = elevar(uma)

    assert canonical_sha256(uma) == canonical_sha256(duas)
    assert uma["schemaVersion"] == SCHEMA_VERSION


def test_o_que_ja_declarou_atravessa_intacto():
    declarada = {
        **ETAPA_V6,
        "evaluationsPerRegistration": 2,
        "maximumScore": "100.0000",
    }

    assert elevar_etapa(declarada) == declarada


def test_nulo_declarado_continua_nulo():
    """Ausente e nulo significam a mesma coisa, e é por isso que a função é idempotente."""
    nula = {
        **ETAPA_V6,
        "evaluationsPerRegistration": None,
        "maximumScore": None,
        "forma": None,
    }

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


def test_versao_anterior_a_quatro_nao_e_elevada():
    """A conversão é 4→5, e só. Carimbar v3 como 5 neutralizaria a verificação de versão.

    Conteúdo que esta elevação não conhece atravessa intacto, para ser recusado onde a recusa é
    dita — como a 007 e a 009 decidiram para os incrementos delas (D-002).
    """
    v3 = conteudo(3, [ETAPA_V4])

    assert elevar(v3) is v3
    assert elevar(v3)["schemaVersion"] == 3


def test_versao_posterior_desconhecida_tambem_atravessa_intacta():
    futuro = conteudo(SCHEMA_VERSION + 1, [ETAPA_V4])

    assert elevar(futuro)["schemaVersion"] == SCHEMA_VERSION + 1


def test_a_entidade_de_etapa_e_a_unica_que_a_precondicao_reconhece():
    """A classificação é compartilhada com a precondição de conteúdo (T-017)."""
    from processo_seletivo.publicacoes.domain.elevacao import endereca_etapa

    assert endereca_etapa("/stages/-")
    assert endereca_etapa("/stages/id=00000000-0000-0000-0000-0000000000e1")
    assert not endereca_etapa("/stages")
    assert not endereca_etapa("/stages/id=00000000-0000-0000-0000-0000000000e1/minimumScore")
    assert not endereca_etapa("/other")
    assert not endereca_etapa("/profiles/-")


def test_a_cadeia_sobe_dois_degraus_do_conteudo_v4():
    """v4 → 5 → 6 num passo só de chamada, e em dois de significado (TR-001)."""
    elevado = elevar(conteudo(4, [ETAPA_V4]))

    assert elevado["schemaVersion"] == SCHEMA_VERSION == 7
    assert elevado["stages"][0]["forma"] == "PONTUADA"
    assert elevado["stages"][0]["evaluationsPerRegistration"] == 1


def test_a_cadeia_sobe_um_degrau_do_conteudo_v5():
    elevado = elevar(conteudo(5, [ETAPA_V5]))

    assert elevado["schemaVersion"] == SCHEMA_VERSION
    assert elevado["stages"] == [ETAPA_V6]


def test_conteudo_vigente_atravessa_sem_copia():
    original = conteudo(SCHEMA_VERSION, [ETAPA_V6])

    assert elevar(original) is original


def test_versao_que_a_cadeia_nao_conhece_atravessa_intacta():
    """Carimbá-la aqui afirmaria uma forma que o conteúdo não tem — a recusa é dita adiante."""
    original = conteudo(3, [ETAPA_V4])

    assert elevar(original) is original
