"""As consequências que a conferência da Retificação declara (051, FR-941, R-015).

As três perguntas são as das telas de condução — a ordem emitida, a divulgação —, e aqui elas são
substituídas por respostas fixas: o que se prende é **quando** a conferência as faz e o que diz,
e não o banco que as responde, que tem os testes dele.
"""

import copy

import pytest

from processo_seletivo.interface import aplicacao_na_retificacao as gesto
from tests.unit.publicacoes.test_aplicacao_na_retificacao import _conteudo, _id, _marco


class _Ato:
    pass


@pytest.fixture
def respostas(monkeypatch):
    """Quais marcos têm ordem emitida e quais têm resultado divulgado."""
    estado = {"com_ordem": set(), "divulgados": set()}
    monkeypatch.setattr(
        "processo_seletivo.classificacao.application.selectors.ato_vigente",
        lambda *, edital, marco_id, lista_id=None: (
            _Ato() if str(marco_id) in estado["com_ordem"] else None
        ),
    )
    monkeypatch.setattr(
        "processo_seletivo.divulgacao.application.selectors.historico_do_marco",
        lambda *, edital, marco_id: (
            [{"vigente": True}] if str(marco_id) in estado["divulgados"] else []
        ),
    )
    return estado


def test_a_janela_muda_em_marco_ordenado_e_divulgado(respostas):
    vigente = _conteudo()
    resultante = copy.deepcopy(vigente)
    for n in (1, 2, 3):
        _marco(resultante, n)["appealWindow"]["durationDays"] = 3
    respostas["com_ordem"] |= {_id("c", 1), _id("c", 2)}
    respostas["divulgados"] |= {_id("c", 2)}

    frases = gesto.consequencias(None, vigente, resultante)

    assert frases == [
        "A ordem emitida do marco Classificação P1, do Perfil P1, fica obsoleta: a regra que ela "
        "cita muda, e ela terá de ser emitida de novo.",
        "A ordem emitida do marco Classificação P2, do Perfil P2, fica obsoleta: a regra que ela "
        "cita muda, e ela terá de ser emitida de novo.",
        "O marco Classificação P2, do Perfil P2, já tem resultado divulgado, e a janela recursal "
        "dele muda: Admite recurso em 2 dia(s) corrido(s) → Admite recurso em 3 dia(s) "
        "corrido(s).",
    ]


def test_o_corte_nao_obsoleta_a_ordem(respostas):
    """O corte lê a ordem, e não a produz (`recorte_da_regra`, FR-205 da `014`)."""
    vigente = _conteudo()
    resultante = copy.deepcopy(vigente)
    _marco(resultante, 1)["cutRule"]["surplusCount"] = 3
    respostas["com_ordem"].add(_id("c", 1))

    assert gesto.consequencias(None, vigente, resultante) == []


def test_a_cota_que_nasce_em_perfil_ordenado_nasce_sem_ordem(respostas):
    """FR-781 da `048`."""
    vigente = _conteudo()
    resultante = copy.deepcopy(vigente)
    resultante["profiles"][1]["competitionModalities"].append(
        {"id": _id("z", 9), "code": "PCD", "name": "PcD", "description": "", "normativeRule": None}
    )
    respostas["com_ordem"].add(_id("c", 2))

    assert gesto.consequencias(None, vigente, resultante) == [
        "O recorte da Modalidade PCD, que nasce no Perfil P2, nasce sem ordem: o marco "
        "Classificação P2 já tem ordem emitida nos outros."
    ]


def test_sem_ordem_nem_divulgacao_nada_a_dizer(respostas):
    vigente = _conteudo()
    resultante = copy.deepcopy(vigente)
    _marco(resultante, 1)["appealWindow"]["durationDays"] = 3
    assert gesto.consequencias(None, vigente, resultante) == []
