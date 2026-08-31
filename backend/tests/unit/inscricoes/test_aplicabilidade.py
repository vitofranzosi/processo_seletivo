"""As quatro combinações de aplicabilidade — e nenhuma quinta (US4 da 009, FR-006, FR-040).

A função é pura sobre o conteúdo publicado e vive no domínio dos Editais, junto da regra que a
declara. É ela que decide o que a tela pede, o que o envio aceita e o que a submissão exige: três
leituras da mesma função, e não três interpretações da mesma frase.
"""

import pytest

from processo_seletivo.editais.domain.documentos import aplicaveis

PERFIL_A, PERFIL_B = "perfil-a", "perfil-b"
MODALIDADE_A, MODALIDADE_B = "modalidade-a", "modalidade-b"

DE_TODOS = {"id": "r1", "name": "Identificação", "order": 1}
DO_PERFIL = {"id": "r2", "name": "Diploma", "order": 2, "profileId": PERFIL_A}
DA_MODALIDADE = {"id": "r3", "name": "Autodeclaração", "order": 3, "modalityId": MODALIDADE_A}
DA_COMBINACAO = {
    "id": "r4",
    "name": "Laudo",
    "order": 4,
    "profileId": PERFIL_A,
    "modalityId": MODALIDADE_A,
}
TODOS = [DE_TODOS, DO_PERFIL, DA_MODALIDADE, DA_COMBINACAO]


@pytest.mark.parametrize(
    ("perfil", "modalidade", "esperados", "porque"),
    [
        (PERFIL_A, MODALIDADE_A, ["r1", "r2", "r3", "r4"], "a combinação recebe as quatro"),
        (PERFIL_A, None, ["r1", "r2"], "sem modalidade, só o de todos e o do Perfil"),
        (PERFIL_B, MODALIDADE_A, ["r1", "r3"], "outro Perfil não recebe o documento do Perfil A"),
        (PERFIL_B, MODALIDADE_B, ["r1"], "nada específico se aplica"),
        (PERFIL_B, None, ["r1"], "só o de todos"),
    ],
)
def test_cada_combinacao_recebe_exatamente_o_que_lhe_cabe(perfil, modalidade, esperados, porque):
    escolhidos = aplicaveis(TODOS, profile_id=perfil, modality_id=modalidade)

    assert [item["id"] for item in escolhidos] == esperados, porque


def test_a_ordem_e_a_declarada_e_nao_a_da_lista():
    fora_de_ordem = [DA_COMBINACAO, DE_TODOS, DO_PERFIL]

    escolhidos = aplicaveis(fora_de_ordem, profile_id=PERFIL_A, modality_id=MODALIDADE_A)

    assert [item["order"] for item in escolhidos] == [1, 2, 4]


def test_lista_vazia_nao_pede_nada():
    assert aplicaveis([], profile_id=PERFIL_A, modality_id=MODALIDADE_A) == []


def test_nenhuma_modalidade_e_diferente_de_qualquer_modalidade():
    """`None` não é curinga: quem não escolheu não recebe o documento de modalidade nenhuma."""
    escolhidos = aplicaveis([DA_MODALIDADE], profile_id=PERFIL_A, modality_id=None)

    assert escolhidos == []
