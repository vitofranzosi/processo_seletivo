"""Edital publicado antes do degrau 12 continua vivo — e a coleção vazia **significa** algo.

Lista vazia diz "este Edital não publicou quadro de vagas", e nunca "zero vaga". A frase é
verdadeira sobre todo Edital publicado antes deste degrau, porque a capacidade não existia: não
havia onde escrever o número, e é exatamente por isso que Editais reais que o sistema conduz até a
ordem do sorteio não eram publicáveis por ele (025, D-005, FR-167).

**A conversão não inventa nada, e é isso que a distingue do 3→4.** Lá, escrever a coleção vazia
teria afirmado que o Edital não exigia documento nenhum, o que não era verdade — ele exigia, em
prosa. Aqui a lista vazia é a grafia da ausência que este módulo já usa desde o degrau 7, e não
converter deixaria o acervo inteiro com uma coleção inendereçável.
"""

import pytest

from processo_seletivo.publicacoes.domain.changes import apply_changes
from processo_seletivo.publicacoes.domain.elevacao import (
    DEGRAUS_DE_PERFIL,
    elevar,
    elevar_perfil,
    elevar_valor,
)
from processo_seletivo.shared.canonical import SCHEMA_VERSION

pytestmark = [pytest.mark.contract]

PERFIL = "aaaaaaaa-1111-4111-8111-111111111111"
MODALIDADE = "aaaaaaaa-2222-4222-8222-222222222222"
LINHA = "aaaaaaaa-3333-4333-8333-333333333333"


def perfil():
    return {
        "id": PERFIL,
        "code": "C1",
        "name": "Curso",
        "description": "",
        "requirements": [],
        "immediateVacancies": 80,
        "reserveType": "NONE",
        "reserveLimit": None,
        "locality": "Vitória",
        "duties": "",
        "workload": "",
        "compensation": "",
        "classificationInformation": {},
        "callInformation": {},
        "competitionModalities": [{"id": MODALIDADE, "code": "PPI", "name": "PPI"}],
        "declaredFacts": [],
        "classificationMilestones": [],
    }


def conteudo_na_versao(versao):
    return {
        "schemaVersion": versao,
        "stages": [],
        "schedule": [],
        "attachments": [],
        "documentRequirements": [],
        "maxInscricoesPorCandidato": None,
        "profiles": [perfil()],
    }


def test_o_degrau_12_existe_no_nivel_do_perfil_e_grafa_a_ausencia_como_lista_vazia():
    assert DEGRAUS_DE_PERFIL[12] == {"vacancyTable": []}
    assert SCHEMA_VERSION >= 12


def test_o_edital_anterior_eleva_sem_inventar_quantidade():
    """E nada mais do Perfil é tocado: o degrau acrescenta a chave e não reescreve o resto."""
    antes = conteudo_na_versao(11)
    elevado = elevar(antes)

    convertido = elevado["profiles"][0]
    assert elevado["schemaVersion"] == SCHEMA_VERSION
    assert convertido["vacancyTable"] == []
    # **Os degraus seguintes também escrevem no Perfil**, e por isso a comparação descarta o que
    # eles acrescentam: o 13 trouxe `generalCompetitionModalityId` (014, D-014) e o 14 trouxe
    # `vacancyReversion` (016, D-007). O que este teste protege é que o degrau 12 não reescreve
    # **o resto**, e isso continua valendo.
    acrescentados = {"vacancyTable", "generalCompetitionModalityId", "vacancyReversion"}
    assert {
        chave: valor for chave, valor in convertido.items() if chave not in acrescentados
    } == perfil()


def test_o_perfil_que_ja_declara_quadro_nao_e_reescrito():
    """Idempotência: elevar de novo não apaga o que já estava lá."""
    ja_declarado = [{"id": LINHA, "modalityId": None, "immediateVacancies": 56}]
    convertido = elevar_perfil({"id": PERFIL, "vacancyTable": ja_declarado}, de=11)

    assert convertido["vacancyTable"] == ja_declarado


def test_a_elevacao_e_idempotente():
    ja_elevado = elevar(conteudo_na_versao(11))

    assert elevar(ja_elevado) is ja_elevado


def test_conteudo_de_versao_futura_atravessa_intacto():
    """O degrau sabe só a sua origem e o seu destino, e não reescreve o que veio depois."""
    futuro = {**conteudo_na_versao(SCHEMA_VERSION + 1), "profiles": []}

    assert elevar(futuro) is futuro


def test_elevar_valor_nao_precisa_de_predicado_novo():
    """A coleção **nasce** no degrau 12: não existe Alteração anterior a ela (025, R-004).

    É o mesmo argumento que `elevacao.py` escreve para os Anexos, e vale confirmá-lo por teste e
    não por leitura — a entrada em `elevar_valor` vem no dia em que a linha ganhar um campo, e não
    antes. Uma linha endereçada por uma Alteração atravessa como está, sem elevação.
    """
    linha = {"id": LINHA, "modalityId": None, "immediateVacancies": 56}

    assert elevar_valor(f"/profiles/id={PERFIL}/vacancyTable/id={LINHA}", linha) == linha
    assert elevar_valor(f"/profiles/id={PERFIL}/vacancyTable/-", linha) == linha
    assert elevar_valor(f"/profiles/id={PERFIL}/vacancyTable", [linha]) == [linha]


def test_a_retificacao_alcanca_a_linha_pela_gramatica_que_ja_existe():
    """FR-170: por identidade da linha, e sem gramática nova."""
    conteudo = elevar(conteudo_na_versao(11))
    conteudo["profiles"][0]["vacancyTable"] = [
        {"id": LINHA, "modalityId": None, "immediateVacancies": 56}
    ]

    resultado, _registro = apply_changes(
        conteudo,
        [
            {
                "targetPath": f"/profiles/id={PERFIL}/vacancyTable/id={LINHA}/immediateVacancies",
                "operation": "REPLACE",
                "newValue": 54,
            }
        ],
        publication_id="55555555-5555-5555-5555-555555555555",
    )

    assert resultado["profiles"][0]["vacancyTable"][0]["immediateVacancies"] == 54
    assert resultado["profiles"][0]["immediateVacancies"] == 80, "o total do Perfil não é tocado"
