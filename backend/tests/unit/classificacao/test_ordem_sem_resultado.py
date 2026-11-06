"""A regra da `128`, sobre a proposta montada à mão: quem conta como tendo resultado, e a frase.

Os casos de banco — a trava, a sucessão, o gesto — estão em
`tests/integration/classificacao/test_ordem_sem_resultado.py`. Aqui fica o que a regra decide sobre
o que o cálculo já devolveu, sem consulta.
"""

import pytest

from processo_seletivo.classificacao.application import ordem_sem_resultado
from processo_seletivo.classificacao.domain.universo_classificavel import nenhuma_com_resultado
from processo_seletivo.shared.api.problems import DomainError

PROVA, ENTREVISTA, PORTA, DESEMPATE = "e-prova", "e-entrevista", "e-porta", "e-desempate"
ETAPAS = {
    PROVA: {"id": PROVA, "name": "Prova Objetiva", "order": 2},
    ENTREVISTA: {"id": ENTREVISTA, "name": "Entrevista", "order": 3},
    PORTA: {"id": PORTA, "name": "Habilitação", "order": 1},
    DESEMPATE: {"id": DESEMPATE, "name": "Prova de Títulos", "order": 4},
}


def _marco(*enumeradas):
    return {"id": "m", "stages": list(enumeradas)}


def _sem(protocolo, pontuacoes=None, consequencia=""):
    return {
        "protocolo": protocolo,
        "inscricao_id": protocolo,
        "pontuacoes": pontuacoes or {},
        "consequencia": consequencia,
        "motivo": "Sem pontuação nas Etapas enumeradas: Prova Objetiva.",
    }


def _proposta(marco, posicoes=(), sem_posicao=()):
    return {
        "marco": marco,
        "etapas": ETAPAS,
        "posicoes": list(posicoes),
        "sem_posicao": list(sem_posicao),
    }


def test_ninguem_com_resultado_e_recusado():
    """FR-4200."""
    assert nenhuma_com_resultado(_marco(PROVA), [_sem("1"), _sem("2")])


def test_universo_vazio_nao_e_recusado():
    """FR-4205: a ordem em que ninguém concorreu se emite."""
    assert not nenhuma_com_resultado(_marco(PROVA), [])
    assert ordem_sem_resultado.impedimento(_proposta(_marco(PROVA))) is None


def test_um_resultado_basta_ordem_parcial():
    """FR-4204."""
    linhas = [_sem("1"), _sem("2", {PROVA: "70.0000"})]
    assert not nenhuma_com_resultado(_marco(PROVA), linhas)


def test_a_porta_sem_pontuacao_conta_como_resultado():
    """FR-4201, D-001, D-002: a chave da Etapa, e não o valor."""
    linhas = [_sem("1", {PORTA: None}), _sem("2")]
    assert not nenhuma_com_resultado(_marco(PORTA, PROVA), linhas)


def test_a_eliminacao_conta_como_resultado():
    """FR-4201: a Ocorrência que elimina é Resultado."""
    linhas = [_sem("1", {PROVA: None}, consequencia="ELIMINADA"), _sem("2")]
    assert not nenhuma_com_resultado(_marco(PROVA), linhas)


def test_todos_eliminados_e_ordem_emissivel():
    """SC-1301: todos sem posição por eliminação é um fato, e não uma ordem precoce."""
    linhas = [_sem(p, {PROVA: None}, consequencia="ELIMINADA") for p in ("1", "2")]
    assert not nenhuma_com_resultado(_marco(PROVA), linhas)


def test_resultado_so_na_etapa_do_desempate_nao_conta():
    """FR-4202, D-003."""
    linhas = [_sem("1", {DESEMPATE: "80.0000"}), _sem("2", {DESEMPATE: "70.0000"})]
    assert nenhuma_com_resultado(_marco(PROVA), linhas)


def test_quem_tem_posicao_tem_resultado():
    proposta = _proposta(_marco(PROVA), posicoes=[{"pontuacoes": {PROVA: "90.0000"}}])
    assert ordem_sem_resultado.impedimento(proposta) is None


def test_a_frase_no_plural_com_uma_etapa():
    """FR-4211, UX-260."""
    achado = ordem_sem_resultado.impedimento(
        _proposta(_marco(PROVA), sem_posicao=[_sem("1"), _sem("2"), _sem("3")])
    )

    assert achado["inscricoes"] == 3
    assert achado["etapas"] == [(PROVA, "Prova Objetiva")]
    assert achado["frase"] == (
        "Nenhuma das 3 inscrições deste recorte tem resultado na Etapa Prova Objetiva. Para emitir "
        "a ordem, distribua as inscrições, avalie e consolide os resultados dessa Etapa."
    )


def test_a_frase_no_singular_e_com_varias_etapas_na_ordem_do_marco():
    """UX-260: o nome publicado, na ordem em que o marco enumera."""
    achado = ordem_sem_resultado.impedimento(
        _proposta(_marco(PORTA, PROVA, ENTREVISTA), sem_posicao=[_sem("1")])
    )

    assert achado["frase"] == (
        "A inscrição deste recorte não tem resultado nas Etapas Habilitação, Prova Objetiva e "
        "Entrevista. Para emitir a ordem, distribua as inscrições, avalie e consolide os "
        "resultados dessas Etapas."
    )


def test_recusar_levanta_o_codigo_proprio_com_a_frase():
    """FR-4211: código próprio, frase sem identificador técnico."""
    proposta = _proposta(_marco(PROVA), sem_posicao=[_sem("1"), _sem("2")])

    with pytest.raises(DomainError) as recusa:
        ordem_sem_resultado.recusar(proposta)

    assert recusa.value.code == "ordering_without_stage_results"
    assert recusa.value.status == 422
    assert recusa.value.detail == ordem_sem_resultado.impedimento(proposta)["frase"]
    assert "e-prova" not in recusa.value.detail


def test_recusar_nao_faz_nada_sem_impedimento():
    ordem_sem_resultado.recusar(_proposta(_marco(PROVA), sem_posicao=[_sem("1", {PROVA: None})]))
