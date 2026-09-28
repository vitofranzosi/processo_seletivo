"""A substituição é campo a campo, e nunca troca pelo objeto inteiro (RC-130; DP-13).

A guarda compara, elemento a elemento, o conteúdo de antes com o de depois do ato. Julga só o
elemento que existe nos dois, e só os campos que o contrato declara não retificáveis. O que nasce, o
que o ato acrescenta e o que ele retira são de outras guardas.
"""

from copy import deepcopy

import pytest

from processo_seletivo.editais.domain import mutabilidade
from processo_seletivo.publicacoes.domain import colecoes
from processo_seletivo.publicacoes.domain.changes import (
    CampoNaoRetificavel,
    apply_changes,
    recusar_troca_de_campo_nao_retificavel,
)

PERFIL = "11111111-1111-4111-8111-111111111111"
OUTRO_PERFIL = "11111111-1111-4111-8111-222222222222"
MARCO = "22222222-2222-4222-8222-222222222222"
CRITERIO = "33333333-3333-4333-8333-333333333333"
ETAPA = "44444444-4444-4444-8444-444444444444"
DO_MARCO = f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}"
CORTE = {
    "targetKind": "FIXED",
    "targetCount": 3,
    "surplusCount": 0,
    "tieOutcome": "STRICT",
    "governedStage": "NONE",
    "continuation": "ALLOWED",
}


def conteudo(corte=CORTE):
    return {
        "number": "12",
        "profiles": [
            {
                "id": PERFIL,
                "code": "P1",
                "reserveType": "NONE",
                "classificationMilestones": [
                    {
                        "id": MARCO,
                        "code": "M1",
                        "stages": [ETAPA],
                        "cutRule": deepcopy(corte),
                        "tiebreakers": [
                            {
                                "id": CRITERIO,
                                "order": 1,
                                "type": "MAIOR_PONTUACAO_NA_ETAPA",
                                "parameters": {"stageId": ETAPA},
                                "whenMissing": "ULTIMO_NO_CRITERIO",
                            }
                        ],
                    }
                ],
            }
        ],
    }


def aplicar(base, *alteracoes):
    resultado, _ = apply_changes(base, list(alteracoes), publication_id="teste")
    return resultado


def test_o_contrato_e_a_fonte_dos_campos_julgados():
    """Nenhuma lista própria: cada não retificável do contrato está numa espécie de elemento."""
    julgados = {
        (forma, "/".join(campo))
        for forma, campos in colecoes.NAO_RETIFICAVEIS_POR_ELEMENTO.items()
        for campo, _ in campos
    }
    esperados = {
        (colecoes.FORMA_DA_COLECAO[colecao], caminho)
        for (colecao, caminho), decisao in mutabilidade.CONTRATO.items()
        if decisao.natureza is mutabilidade.Natureza.NAO_RETIFICAVEL
        and (colecao, caminho) not in colecoes.RECUSADOS_EM_OUTRO_LUGAR
    }
    assert julgados == esperados
    assert ("/profiles/*/classificationMilestones/*", "cutRule/governedStage") in julgados


def test_a_troca_pelo_objeto_inteiro_e_recusada_com_a_razao_do_contrato():
    base = conteudo()
    resultado = aplicar(
        base,
        {
            "targetPath": f"{DO_MARCO}/cutRule",
            "operation": "REPLACE",
            "newValue": {**CORTE, "continuation": "NONE"},
        },
    )

    with pytest.raises(CampoNaoRetificavel, match=r"cutRule/continuation passaria de \"ALLOWED\""):
        recusar_troca_de_campo_nao_retificavel(base, resultado)


def test_o_objeto_inteiro_que_so_corrige_o_retificavel_passa():
    base = conteudo()
    resultado = aplicar(
        base,
        {
            "targetPath": f"{DO_MARCO}/cutRule",
            "operation": "REPLACE",
            "newValue": {**CORTE, "targetCount": 7, "tieOutcome": "ADMITS_SURPLUS"},
        },
    )

    recusar_troca_de_campo_nao_retificavel(base, resultado)


def test_o_objeto_que_nasce_nao_e_troca():
    """O corte que nasce num marco sem corte é da `048` (FR-788), e o contrato o admite."""
    base = conteudo(corte=None)
    resultado = aplicar(
        base, {"targetPath": f"{DO_MARCO}/cutRule", "operation": "REPLACE", "newValue": CORTE}
    )

    recusar_troca_de_campo_nao_retificavel(base, resultado)


@pytest.mark.parametrize(
    "alteracao",
    [
        {"targetPath": f"{DO_MARCO}/cutRule", "operation": "REPLACE", "newValue": None},
        {"targetPath": f"{DO_MARCO}/cutRule", "operation": "REMOVE"},
    ],
    ids=["por REPLACE nulo", "por REMOVE"],
)
def test_remover_a_regra_inteira_nao_e_troca(alteracao):
    """Remover a regra de corte é decisão normativa da `014` (T082), e não troca dos campos dela."""
    base = conteudo()
    resultado = aplicar(base, alteracao)

    recusar_troca_de_campo_nao_retificavel(base, resultado)


def test_o_campo_que_some_de_dentro_do_objeto_que_fica_e_troca():
    """Sumir com a Etapa governada de um corte que continua existindo muda quem progride."""
    base = conteudo()
    sem_etapa = {chave: valor for chave, valor in CORTE.items() if chave != "governedStage"}
    resultado = aplicar(
        base, {"targetPath": f"{DO_MARCO}/cutRule", "operation": "REPLACE", "newValue": sem_etapa}
    )

    with pytest.raises(CampoNaoRetificavel, match='governedStage passaria de "NONE" para ausente'):
        recusar_troca_de_campo_nao_retificavel(base, resultado)


def test_remover_e_redeclarar_a_regra_no_mesmo_ato_e_troca():
    """Remover e fazer nascer num ato só é a troca escrita de outro jeito."""
    base = conteudo()
    resultado = aplicar(
        base,
        {"targetPath": f"{DO_MARCO}/cutRule", "operation": "REPLACE", "newValue": None},
        {
            "targetPath": f"{DO_MARCO}/cutRule",
            "operation": "REPLACE",
            "newValue": {**CORTE, "targetKind": "FROM_VACANCY_TABLE", "targetCount": None},
        },
    )

    with pytest.raises(CampoNaoRetificavel, match="cutRule/targetKind"):
        recusar_troca_de_campo_nao_retificavel(base, resultado)


def test_a_entidade_retirada_ou_acrescentada_nao_e_julgada():
    """Retirar o critério e acrescentar outro, de identidade nova, é o caminho da `048` (FR-792)."""
    base = conteudo()
    novo = {
        "id": "55555555-5555-4555-8555-555555555555",
        "order": 1,
        "type": "MAIOR_VALOR_DE_FATO",
        "parameters": {"factId": ETAPA},
        "whenMissing": "CRITERIO_NAO_SE_APLICA",
    }
    resultado = aplicar(
        base,
        {"targetPath": f"{DO_MARCO}/tiebreakers/id={CRITERIO}", "operation": "REMOVE"},
        {"targetPath": f"{DO_MARCO}/tiebreakers/-", "operation": "ADD", "newValue": novo},
    )

    recusar_troca_de_campo_nao_retificavel(base, resultado)


def test_o_perfil_acrescentado_nao_e_julgado():
    base = conteudo()
    perfil = {**deepcopy(base["profiles"][0]), "id": OUTRO_PERFIL, "reserveType": "UNLIMITED"}
    perfil["classificationMilestones"] = []
    resultado = aplicar(base, {"targetPath": "/profiles/-", "operation": "ADD", "newValue": perfil})

    recusar_troca_de_campo_nao_retificavel(base, resultado)


def test_a_mesma_identidade_de_volta_com_outro_tipo_e_troca():
    base = conteudo()
    trocado = {**base["profiles"][0]["classificationMilestones"][0]["tiebreakers"][0]}
    trocado["whenMissing"] = "CRITERIO_NAO_SE_APLICA"
    resultado = aplicar(
        base,
        {"targetPath": f"{DO_MARCO}/tiebreakers/id={CRITERIO}", "operation": "REMOVE"},
        {"targetPath": f"{DO_MARCO}/tiebreakers/-", "operation": "ADD", "newValue": trocado},
    )

    with pytest.raises(CampoNaoRetificavel, match=f"tiebreakers/id={CRITERIO}/whenMissing"):
        recusar_troca_de_campo_nao_retificavel(base, resultado)


def test_as_etapas_do_marco_nao_se_trocam_pelo_marco_inteiro():
    base = conteudo()
    marco = {**deepcopy(base["profiles"][0]["classificationMilestones"][0]), "stages": []}
    resultado = aplicar(base, {"targetPath": DO_MARCO, "operation": "REPLACE", "newValue": marco})

    with pytest.raises(CampoNaoRetificavel, match="O caminho para mudar o que se mede"):
        recusar_troca_de_campo_nao_retificavel(base, resultado)
