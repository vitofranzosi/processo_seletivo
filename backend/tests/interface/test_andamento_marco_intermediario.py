"""A jornada não aponta o ato errado (133): a derivação da `127` nas paradas do Edital 900 reduzido.

Cada teste é um instante do estudo de convergência de 07/11/2026 (FR-4557), na fixture
`tests/fixtures/marco_intermediario.py`, e confere o que a sonda do estudo conferiu no 900 completo.
"""

import pytest

from processo_seletivo.interface import andamento
from tests.conftest import ator_institucional
from tests.fixtures import marco_intermediario as m900

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return m900.montar(gestor, api_client, manager_headers, process_payload)


def _ler(cenario, quem="maria"):
    return andamento.do_edital(cenario["edital"], ator_institucional(quem))


def _celulas(lido, marco, tipo):
    for perfil in lido.perfis:
        for ponto in perfil.pontos:
            if ponto.tipo == tipo and ponto.marco and str(ponto.marco.get("id")) == marco:
                return {lista: ponto.celula(lista) for lista in m900.LISTAS}
    raise AssertionError(f"sem ponto {tipo} no marco {marco}")


def _providencias(lido):
    return [(p.celula if hasattr(p, "celula") else p) for p in lido.providencias]


def _suas(lido):
    return [c for c in _providencias(lido) if lido.e_sua(c)]


# --- CV-01: o marco intermediário (US1) -------------------------------------------------------


def test_depois_da_apuracao_do_marco_final_so_as_convocacoes_dele_sao_providencia(cenario):
    lido = _ler(m900.ate_a_apuracao_m2(cenario))

    for tipo in (andamento.APURACAO, andamento.CONVOCACAO):
        for celula in _celulas(lido, m900.MARCO_1, tipo).values():
            assert celula.situacao == andamento.NAO_SE_APLICA, (tipo, celula)
            assert "Entrevista" in celula.nota
    atos = [c.ato for c in _suas(lido)]
    assert "Apurar a ocupação" not in atos
    assert any(ato.startswith("Convocar") for ato in atos)


def test_o_resumo_do_perfil_nao_conta_a_apuracao_do_marco_intermediario(cenario):
    lido = _ler(m900.ate_a_apuracao_m2(cenario))

    resumo = andamento.resumo_do_perfil(lido.perfis[0])
    assert "apuração 2 de 2" in resumo, resumo


# --- CV-02: o corte espera o prazo recursal, como recomendação (US2) --------------------------


def test_depois_da_ordem_o_proximo_e_divulgar_e_o_corte_espera(cenario):
    lido = _ler(m900.ate_a_ordem_m1(cenario))

    for celula in _celulas(lido, m900.MARCO_1, andamento.CORTE).values():
        assert celula.situacao == andamento.AGUARDA
        assert celula.recomendacao
        assert "divulgação" in celula.razao
    # O que se pratica vem antes do que espera (FR-4543): sem preferência de papel, o próximo do
    # marco é divulgar; com a da presidência, nunca o corte em espera. (A fixture deixa a Etapa de
    # base sem avaliação, e distribuí-la é "sua" — a regra da `127` a põe primeiro.)
    desta, _, _ = andamento.da_lista(lido, m900.MARCO_1, None)
    assert desta.natureza == andamento.RESULTADO
    assert desta.situacao == andamento.PENDENTE
    sua, _, _ = andamento.da_lista(lido, m900.MARCO_1, None, preferir=lido.e_sua)
    assert sua.natureza != andamento.CORTE


def test_com_a_preliminar_publicada_o_corte_espera_o_prazo_e_nao_e_seu(cenario):
    lido = _ler(m900.ate_a_preliminar_m1(cenario))

    for celula in _celulas(lido, m900.MARCO_1, andamento.CORTE).values():
        assert celula.situacao == andamento.AGUARDA
        assert celula.recomendacao
        assert celula.ate is not None
        assert "obsoleto" in celula.razao
    assert not [c for c in _suas(lido) if c.natureza == andamento.CORTE]


# --- CV-04: a divulgação com ordem obsoleta (US4) ---------------------------------------------


def test_com_a_ordem_obsoleta_a_definitiva_nao_e_pendente_para_quem_publica(cenario):
    lido = _ler(m900.ate_a_ordem_obsoleta(cenario), quem="paula.publicadora")

    ampla = _celulas(lido, m900.MARCO_1, andamento.RESULTADO)[None]
    assert andamento.ORDEM and ampla.situacao == andamento.DEPOIS, ampla
    assert "ordem vigente" in ampla.razao


# --- CV-03: a próxima da fila (US3) -----------------------------------------------------------


def test_depois_da_desistencia_a_proxima_da_fila_e_providencia(cenario):
    lido = _ler(m900.ate_a_desistencia_com_titular_pendente(cenario))

    atos = [c.ato for c in _suas(lido)]
    assert "Chamar a próxima da fila" in atos, atos
    esperas = [c for c in _providencias(lido) if c.situacao == andamento.AGUARDA]
    assert any("Resposta de 1 convocação" in c.ato for c in esperas)
