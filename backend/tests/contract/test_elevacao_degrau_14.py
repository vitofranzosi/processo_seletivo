"""Edital publicado antes do degrau 14 continua vivo — e a ausência da reversão **significa** algo.

A régua deste módulo é a mesma desde o 4→5: converter só quando a ausência tem significado declarado
e **verdadeiro**. `vacancyReversion: None` diz "este Edital não declara reversão de vaga reservada",
e a frase é verdadeira sobre todo Edital publicado antes deste degrau — a capacidade não existia, e
nenhum deles poderia tê-la declarado.

**E a ausência não vira padrão de comportamento.** O 57/2026 prova por que isso importa: o item 4.5
dele proíbe por escrito o remanejamento de vagas remanescentes entre os cursos. Um sistema que
revertesse por conta própria produziria, naquele Edital, exatamente o que ele veda — e é por isso
que "não declarou" tem de ser lido como "não move", e nunca como "move do jeito comum"
(016, D-002).

**Não elevar seria pior do que elevar**, pela razão de sempre: conteúdo em versão diferente da
vigente é recusado, e deixar o acervo em 13 tornaria todo Edital publicado irretificável por causa
de uma feature que ele não usa.
"""

import pytest

from processo_seletivo.publicacoes.domain.elevacao import DEGRAUS_DE_PERFIL, elevar
from processo_seletivo.shared.canonical import SCHEMA_VERSION

pytestmark = [pytest.mark.contract]

PERFIL = "22222222-2222-2222-2222-222222222222"


def conteudo_na_versao(versao):
    """Um conteúdo mínimo na versão anterior ao degrau, sem declaração de reversão."""
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
                "generalCompetitionModalityId": None,
                "classificationMilestones": [],
            }
        ],
    }


def test_o_degrau_14_e_de_perfil_e_grafa_a_ausencia_como_nula():
    """É do **Perfil**, e não de raiz nem de marco.

    A reversão é sobre as cotas *daquele* Perfil: um Edital de sete polos declara sete vezes, e a
    Constituição manda cota ser definida por Perfil. Uma coleção de raiz teria de carregar a
    referência ao Perfil, inventando uma segunda forma de dizer o que o aninhamento já diz.
    """
    assert DEGRAUS_DE_PERFIL[14] == {"vacancyReversion": None}
    assert SCHEMA_VERSION >= 14


def test_o_acervo_anterior_sobe_e_passa_a_dizer_que_nao_declara_reversao():
    elevado = elevar(conteudo_na_versao(13))

    assert elevado["schemaVersion"] == SCHEMA_VERSION
    assert elevado["profiles"][0]["vacancyReversion"] is None


def test_a_elevacao_nao_afirma_reversao_em_lugar_nenhum():
    """**Conversão sem invenção.** `None` é a grafia de "não declarou", e não de uma espécie."""
    elevado = elevar(conteudo_na_versao(13))
    perfil = elevado["profiles"][0]

    assert "ON_EXHAUSTION" not in repr(perfil)
    assert "ON_BALANCE" not in repr(perfil)


def test_a_elevacao_nao_toca_a_declaracao_de_quem_ja_a_tinha():
    """Quem já declarou sobe com o que declarou — elevar não reinterpreta conteúdo publicado."""
    conteudo = conteudo_na_versao(13)
    conteudo["profiles"][0]["vacancyReversion"] = {"kind": "ON_BALANCE"}

    elevado = elevar(conteudo)

    assert elevado["profiles"][0]["vacancyReversion"] == {"kind": "ON_BALANCE"}


def test_elevar_a_partir_de_bem_antes_atravessa_o_degrau_14():
    """O degrau é um passo de uma cadeia, e a cadeia inteira continua fechando."""
    elevado = elevar(conteudo_na_versao(7))

    assert elevado["schemaVersion"] == SCHEMA_VERSION
    assert elevado["profiles"][0]["vacancyReversion"] is None
    # E os degraus anteriores do mesmo nível continuam valendo.
    assert elevado["profiles"][0]["vacancyTable"] == []
    assert elevado["profiles"][0]["generalCompetitionModalityId"] is None
