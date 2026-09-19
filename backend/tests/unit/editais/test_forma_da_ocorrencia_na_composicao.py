"""A sexta guarda do método: a ocorrência tem de ter a forma que a regra consome (035, US2).

**A assimetria é o achado, e é o que este arquivo prende.** Cinco dos seis campos do método já eram
conferidos ao gravar o rascunho — o algoritmo, a fonte, o instante e as duas regras. A ocorrência,
o **único** cuja má declaração impede o sorteio de rodar, não era conferida em lugar nenhum: ela
aparecia no módulo que valida o método uma única vez, como rótulo.

**A recusa nasce ao lado das cinco, e não numa família nova.** Pôr a sexta noutro lugar criaria
duas gramáticas para o mesmo tipo de erro, e a pessoa descobriria metade dos problemas ao gravar e
a outra metade na Revisão, sem que nada explicasse a diferença.

A garantia de que a composição e o motor respondem **a mesma coisa** está em
`tests/unit/sorteios/test_forma_da_ocorrencia.py`, que compara as duas respostas. Aqui o que se
prende é onde a conferência acontece, e o que ela diz.
"""

import pytest

from processo_seletivo.editais.domain.perfis import (
    ProfileValidationError,
    validate_classification_milestones,
    validate_common_draw_method,
)

PERFIL = "aaaaaaaa-0000-4000-8000-000000000351"
MARCO = "aaaaaaaa-0000-4000-8000-000000000352"
ETAPA = "aaaaaaaa-0000-4000-8000-000000000353"

METODO = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Loteria Federal",
    "occurrence": "5900",
    "occurrenceAt": "2026-11-20T20:00:00-03:00",
    "derivation": "a extração de sábado imediatamente anterior à data publicada",
    "normalization": {
        "rule": "DIGITOS_EM_SEQUENCIA",
        "text": "os cinco números sorteados, na ordem dos prêmios",
    },
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "não havendo extração na data, vale a extração seguinte da mesma fonte",
    },
}

#: A forma que uma pessoa escreve, e a que três fixtures deste repositório tinham: o número está
#: lá, e só não está onde a regra o procura, porque a fonte foi repetida depois dele.
EM_PROSA = "concurso 6100 da Loteria Federal"


def _marco(metodo=None, **alteracoes):
    marco = {
        "id": MARCO,
        "code": "SORTEIO",
        "name": "Sorteio público",
        "orderProduction": "POR_SORTEIO",
        "stages": [],
        "tiebreakers": [],
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "cutRule": {
            "targetKind": "FIXED",
            "targetCount": 2,
            "surplusCount": 0,
            "tieOutcome": "STRICT",
            "governedStage": "NONE",
            "continuation": "NONE",
        },
    }
    if metodo is not None:
        marco["drawMethod"] = metodo
    return {**marco, **alteracoes}


def _validar(marco):
    validate_classification_milestones([marco])


def test_a_ocorrencia_em_prosa_e_recusada_ao_gravar_o_rascunho():
    """`FR-512` — no mesmo momento em que um algoritmo fora do vocabulário já era recusado."""
    with pytest.raises(ProfileValidationError) as recusa:
        _validar(_marco({**METODO, "occurrence": EM_PROSA}))

    assert EM_PROSA in str(recusa.value)


def test_a_recusa_nomeia_o_campo_a_forma_e_a_razao_da_forma():
    """`FR-513` e `SC-178` — e nenhuma das cinco vizinhas descreve o sintoma.

    *"O método não é executável"* diria o que aconteceu e não o que corrigir. As três partes são
    testadas uma a uma porque cada uma responde a um pedaço do requisito.
    """
    with pytest.raises(ProfileValidationError) as recusa:
        _validar(_marco({**METODO, "occurrence": EM_PROSA}))
    dito = str(recusa.value)

    assert "Ocorrência" in dito, "o campo"
    assert "terminar no número" in dito, "a forma esperada"
    assert "deriva a substituta" in dito, "por que a forma é exigida"
    assert "campo próprio" in dito, "e o erro específico que se comete"
    assert "não é executável" not in dito, "descreveria o sintoma"


@pytest.mark.parametrize("referencia", ["5900", "Concurso 5900", "0099", "6100"])
def test_a_ocorrencia_que_termina_em_numero_e_aceita(referencia):
    _validar(_marco({**METODO, "occurrence": referencia}))


def test_o_metodo_comum_do_edital_recebe_a_mesma_recusa():
    """A conferência não distingue o método próprio do comum — há uma função só, e é ela.

    E o dano do comum é maior: ele governa todo marco que não declara o próprio, de modo que uma
    ocorrência inexecutável ali alcança todos de uma vez.
    """
    with pytest.raises(ProfileValidationError) as recusa:
        validate_common_draw_method({**METODO, "occurrence": EM_PROSA})

    assert "terminar no número" in str(recusa.value)


def test_o_metodo_comum_com_ocorrencia_na_forma_e_aceito():
    validate_common_draw_method(METODO)


# --- O que **não** dispara (T017) ---------------------------------------------------------------
#
# A ausência de método é válida e significa alguma coisa: marco que não sorteia não declara método,
# e a maioria não sorteia. Uma guarda que disparasse aí transformaria o silêncio legítimo em erro.


def test_marco_que_nao_sorteia_nao_produz_nada_desta_familia():
    _validar(
        _marco(
            orderProduction="COMPUTADA",
            operation="SOMA_PONDERADA",
            normalization="NENHUMA",
            stages=[ETAPA],
        )
    )


def test_edital_sem_metodo_algum_nao_produz_nada_desta_familia():
    validate_common_draw_method(None)
    validate_common_draw_method({})
