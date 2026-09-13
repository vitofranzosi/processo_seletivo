"""Edital publicado antes do degrau 15 continua vivo — e a ausência da forma **significa** algo.

A régua deste módulo é a mesma desde o 4→5: converter só quando a ausência tem significado declarado
e **verdadeiro**. `callForm: None` diz "este Edital não declarou como comunica a convocação", e a
frase é verdadeira sobre todo Edital publicado antes deste degrau — a capacidade não existia, e
nenhum deles poderia tê-la declarado.

**E a ausência não vira padrão de comportamento**, pela mesma razão do degrau 14. A amostra tem duas
formas incompatíveis e as duas são normais: o 69/2026 (7.2) convoca por publicação; o 77, o 58 e o
59 (8.3) por mensagem individual, com o prazo contado do recebimento. Escolher uma por omissão
decidiria norma no lugar do Edital — e convocação alcançada pela forma errada não tem conserto
depois, porque publicação é ato imutável. Sem declaração, a `019` **recusa** convocar (019, D-009).

**Não elevar seria pior do que elevar**, pela razão de sempre: conteúdo em versão diferente da
vigente é recusado, e deixar o acervo em 14 tornaria todo Edital publicado irretificável por causa
de uma feature que ele não usa.
"""

import pytest

from processo_seletivo.publicacoes.domain.elevacao import DEGRAUS_DE_PERFIL, elevar
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMAS_DE_CONVOCACAO
from processo_seletivo.shared.canonical import SCHEMA_VERSION

pytestmark = [pytest.mark.contract]

PERFIL = "22222222-2222-2222-2222-222222222222"


def conteudo_na_versao(versao):
    """Um conteúdo mínimo na versão anterior ao degrau, sem declaração de forma."""
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
                "vacancyReversion": None,
                "classificationMilestones": [],
            }
        ],
    }


def test_o_degrau_15_e_de_perfil_e_grafa_a_ausencia_como_nula():
    """É do **Perfil**, e não de raiz nem de marco.

    A forma de convocar é sobre *aquele* Perfil: um Edital de sete polos pode comunicar de modos
    diferentes, e é o Perfil que carrega as informações de chamada desde a `001`. Uma chave de raiz
    obrigaria todo Perfil a compartilhar a forma, que é regra que Edital nenhum publicou.
    """
    assert DEGRAUS_DE_PERFIL[15] == {"callForm": None}
    assert SCHEMA_VERSION >= 15


def test_o_acervo_anterior_sobe_e_passa_a_dizer_que_nao_declarou_forma():
    elevado = elevar(conteudo_na_versao(14))

    assert elevado["schemaVersion"] == SCHEMA_VERSION
    assert elevado["profiles"][0]["callForm"] is None


def test_a_elevacao_nao_afirma_forma_em_lugar_nenhum():
    """**Conversão sem invenção.** `None` é a grafia de "não declarou", e não de uma das formas.

    O modo de errar aqui é escolher a publicação por ser a mais comum — e seria errado justamente
    nos três Editais da amostra que convocam por mensagem individual.
    """
    elevado = elevar(conteudo_na_versao(14))
    perfil = elevado["profiles"][0]

    for forma in FORMAS_DE_CONVOCACAO:
        assert forma not in repr(perfil)


def test_a_elevacao_nao_toca_a_declaracao_de_quem_ja_a_tinha():
    """Quem já declarou sobe com o que declarou — elevar não reinterpreta conteúdo publicado."""
    conteudo = conteudo_na_versao(14)
    conteudo["profiles"][0]["callForm"] = "INDIVIDUAL_MESSAGE"

    elevado = elevar(conteudo)

    assert elevado["profiles"][0]["callForm"] == "INDIVIDUAL_MESSAGE"


def test_o_degrau_e_idempotente():
    """Elevar o já elevado devolve o mesmo conteúdo, e não uma segunda passada.

    É o que permite a elevação rodar na leitura de qualquer versão sem que ninguém precise saber se
    ela já rodou — e o que impede um `callForm` declarado de ser sobrescrito por nulo.
    """
    uma_vez = elevar(conteudo_na_versao(14))

    assert elevar(uma_vez) == uma_vez

    declarado = conteudo_na_versao(14)
    declarado["profiles"][0]["callForm"] = "PUBLICATION"
    elevado = elevar(declarado)

    assert elevar(elevado) == elevado
    assert elevado["profiles"][0]["callForm"] == "PUBLICATION"


def test_elevar_a_partir_de_bem_antes_atravessa_o_degrau_15():
    """O degrau é um passo de uma cadeia, e a cadeia inteira continua fechando."""
    elevado = elevar(conteudo_na_versao(7))

    assert elevado["schemaVersion"] == SCHEMA_VERSION
    assert elevado["profiles"][0]["callForm"] is None
    # E os degraus anteriores do mesmo nível continuam valendo.
    assert elevado["profiles"][0]["vacancyTable"] == []
    assert elevado["profiles"][0]["generalCompetitionModalityId"] is None
    assert elevado["profiles"][0]["vacancyReversion"] is None
