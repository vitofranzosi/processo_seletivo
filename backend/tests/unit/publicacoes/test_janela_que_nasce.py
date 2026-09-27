"""A janela recursal que nasce por Retificação concede (048, D-003, FR-787).

A guarda compara o conteúdo de antes com o de depois, e só julga o **nascimento** num marco que já
existia. A janela que já existia e é alterada segue a regra de hoje, e o nascimento dos outros
objetos que podem nascer não é desta guarda.
"""

from copy import deepcopy

import pytest

from processo_seletivo.publicacoes.domain.changes import (
    CampoNaoRetificavel,
    apply_changes,
    recusar_janela_que_nasce_sem_recurso,
)

PERFIL = "11111111-1111-4111-8111-111111111111"
MARCO = "22222222-2222-4222-8222-222222222222"
CAMINHO = f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}"
CONCEDE = {"admits": True, "durationDays": 3, "unit": "DIAS_CORRIDOS"}
NAO_ADMITE = {"admits": False, "durationDays": None, "unit": "DIAS_CORRIDOS"}


def conteudo(janela=None, **marco):
    return {
        "profiles": [
            {
                "id": PERFIL,
                "classificationMilestones": [
                    {"id": MARCO, "code": "M1", "appealWindow": janela, **marco}
                ],
            }
        ]
    }


def depois(base, janela):
    resultado = deepcopy(base)
    resultado["profiles"][0]["classificationMilestones"][0]["appealWindow"] = janela
    return resultado


def test_a_janela_que_nasce_admitindo_recurso_passa():
    base = conteudo()
    recusar_janela_que_nasce_sem_recurso(base, depois(base, CONCEDE))


@pytest.mark.parametrize("admite", [False, None, "sim", 1])
def test_a_janela_que_nasce_sem_admitir_e_recusada(admite):
    base = conteudo()
    with pytest.raises(CampoNaoRetificavel, match="concede prazo de recurso onde não havia"):
        recusar_janela_que_nasce_sem_recurso(base, depois(base, {**NAO_ADMITE, "admits": admite}))


def test_a_recusa_nomeia_o_caminho_do_marco():
    base = conteudo()
    with pytest.raises(CampoNaoRetificavel, match=f"{CAMINHO}/appealWindow"):
        recusar_janela_que_nasce_sem_recurso(base, depois(base, NAO_ADMITE))


def test_a_janela_existente_alterada_nao_e_desta_guarda():
    """Alterar janela que existia é alteração de valor: a regra de hoje a admite (US3, cen. 4)."""
    base = conteudo(CONCEDE)
    recusar_janela_que_nasce_sem_recurso(base, depois(base, NAO_ADMITE))


def test_remover_e_acrescentar_a_janela_existente_nao_e_nascimento():
    base = conteudo(CONCEDE)
    resultado, _ = apply_changes(
        base,
        [
            {"targetPath": f"{CAMINHO}/appealWindow", "operation": "REMOVE"},
            {"targetPath": f"{CAMINHO}/appealWindow", "operation": "ADD", "newValue": NAO_ADMITE},
        ],
        publication_id="teste",
    )
    recusar_janela_que_nasce_sem_recurso(base, resultado)


def test_o_nascimento_por_remocao_e_acrescimo_tambem_e_julgado():
    """`REMOVE` + `ADD` sobre janela nula ainda é nascimento: a comparação é antes e depois."""
    base = conteudo(None)
    resultado = depois(base, NAO_ADMITE)
    with pytest.raises(CampoNaoRetificavel):
        recusar_janela_que_nasce_sem_recurso(base, resultado)


def test_os_outros_objetos_que_nascem_nao_sao_desta_guarda():
    base = conteudo()
    resultado = deepcopy(base)
    marco = resultado["profiles"][0]["classificationMilestones"][0]
    marco["cutRule"] = {"targetKind": "FIXED", "targetCount": 10}
    marco["drawMethod"] = {"algorithm": "X"}
    recusar_janela_que_nasce_sem_recurso(base, resultado)


def test_o_marco_acrescentado_inteiro_nao_e_nascimento_de_janela():
    base = conteudo()
    resultado = deepcopy(base)
    resultado["profiles"][0]["classificationMilestones"].append(
        {"id": "33333333-3333-4333-8333-333333333333", "appealWindow": NAO_ADMITE}
    )
    recusar_janela_que_nasce_sem_recurso(base, resultado)


def test_o_marco_removido_nao_e_julgado():
    base = conteudo()
    resultado = deepcopy(base)
    resultado["profiles"][0]["classificationMilestones"] = []
    recusar_janela_que_nasce_sem_recurso(base, resultado)
