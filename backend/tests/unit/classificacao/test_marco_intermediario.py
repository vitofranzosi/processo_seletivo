"""A regra do marco intermediário (133, FR-4530, FR-4531, FR-4537, D-001), sem banco.

O caso que a motivou é o Edital 900 do estudo de convergência de 07/11/2026: a *Classificação para a
entrevista* governa a Entrevista, que a *Classificação final* lê. A primeira não apura vagas nem
convoca. Os casos de banco — a recusa nos comandos, sem gravação — estão em `tests/integration/`.
"""

import pytest

from processo_seletivo.classificacao.application import marco_intermediario as aplicacao
from processo_seletivo.classificacao.domain import marco_intermediario as regra
from processo_seletivo.shared.api.problems import DomainError

PROVA, ENTREVISTA, HABILITACAO = "e-prova", "e-entrevista", "e-habilitacao"
ETAPAS = [
    {"id": PROVA, "name": "Prova escrita"},
    {"id": ENTREVISTA, "name": "Entrevista"},
    {"id": HABILITACAO, "name": "Heteroidentificação"},
]


def _marco(ident, nome, stages, governa=None, sorteio=False):
    marco = {"id": ident, "name": nome, "stages": list(stages)}
    if governa is not False:
        marco["cutRule"] = {"targetKind": "FIXED", "targetCount": 8, "governedStage": governa}
    if sorteio:
        marco["orderProduction"] = "SORTEIO"
    return marco


M1 = _marco("m1", "Classificação para a entrevista", [PROVA], governa=ENTREVISTA)
M2 = _marco("m2", "Classificação final", [PROVA, ENTREVISTA], governa=None)


def _perfil(*marcos):
    return {"id": "p", "classificationMilestones": list(marcos)}


def _conteudo(*marcos):
    return {"stages": ETAPAS, "profiles": [_perfil(*marcos)]}


def test_o_marco_que_governa_a_etapa_que_o_final_le_e_intermediario():
    perfil = _perfil(M1, M2)

    assert regra.e_intermediario(perfil, "m1")
    assert regra.marco_que_le(perfil, "m1")["id"] == "m2"


def test_o_marco_final_nao_e_intermediario():
    assert not regra.e_intermediario(_perfil(M1, M2), "m2")


def test_o_sorteio_seguido_de_habilitacao_que_ninguem_le_nao_e_intermediario():
    # O caso que a `127` trata como legítimo: a apuração espera a Etapa governada, e nenhum marco
    # depois dela a lê.
    sorteio = _marco("s", "Sorteio", [HABILITACAO], governa=HABILITACAO, sorteio=True)

    assert not regra.e_intermediario(_perfil(sorteio), "s")


def test_o_sorteio_cuja_etapa_governada_outro_marco_le_e_intermediario():
    sorteio = _marco("s", "Sorteio", [HABILITACAO], governa=ENTREVISTA, sorteio=True)
    final = _marco("f", "Classificação final", [ENTREVISTA], governa=None)

    assert regra.e_intermediario(_perfil(sorteio, final), "s")


@pytest.mark.parametrize("governa", [False, None])
def test_o_marco_sem_etapa_governada_seguido_de_outro_nao_e_intermediario(governa):
    # D-001, confirmada pelo usuário em 08/11: a definição é a estreita.
    primeiro = _marco("a", "Classificação preliminar", [PROVA], governa=governa)
    segundo = _marco("b", "Classificação final", [PROVA, ENTREVISTA], governa=None)

    assert not regra.e_intermediario(_perfil(primeiro, segundo), "a")


def test_tres_marcos_em_cadeia():
    primeiro = _marco("a", "Para a prova", [HABILITACAO], governa=PROVA)
    segundo = _marco("b", "Para a entrevista", [PROVA], governa=ENTREVISTA)
    terceiro = _marco("c", "Final", [PROVA, ENTREVISTA], governa=None)
    perfil = _perfil(primeiro, segundo, terceiro)

    assert regra.e_intermediario(perfil, "a")
    assert regra.e_intermediario(perfil, "b")
    assert not regra.e_intermediario(perfil, "c")


def test_perfil_sem_marcos_e_marco_desconhecido_nao_quebram():
    assert not regra.e_intermediario({"id": "p"}, "m1")
    assert not regra.e_intermediario(_perfil(M1, M2), "inexistente")


def test_o_impedimento_nomeia_o_marco_a_etapa_e_o_marco_que_apura():
    achado = aplicacao.impedimento(_conteudo(M1, M2), "p", "m1")

    assert achado["marco_que_le_id"] == "m2"
    assert achado["frase"] == (
        "A Classificação para a entrevista decide quem participa da Etapa Entrevista: ela não "
        "apura vagas nem convoca. As vagas são apuradas e convocadas na Classificação final."
    )
    assert achado["nota"] == "decide quem vai à Entrevista; as vagas são da Classificação final"
    # Nenhum identificador interno chega à frase (FR-4537).
    assert "m1" not in achado["frase"] and "e-entrevista" not in achado["frase"]


def test_sem_impedimento_no_marco_final_e_em_perfil_desconhecido():
    assert aplicacao.impedimento(_conteudo(M1, M2), "p", "m2") is None
    assert aplicacao.impedimento(_conteudo(M1, M2), "outro", "m1") is None


def test_a_recusa_tem_codigo_proprio():
    with pytest.raises(DomainError) as recusa:
        aplicacao.recusar(_conteudo(M1, M2), "p", "m1")

    assert recusa.value.code == aplicacao.CODIGO == "apuracao_em_marco_intermediario"
    assert recusa.value.status == 409


def test_a_recusa_nao_faz_nada_fora_do_marco_intermediario():
    aplicacao.recusar(_conteudo(M1, M2), "p", "m2")
