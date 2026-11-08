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


def test_com_chamada_aberta_para_a_vaga_que_vagou_nao_se_chama_outra(cenario):
    """D-004: a chamada da vaga que vagou ainda não ocupa, e já responde pela vaga."""
    m900.ate_a_desistencia_com_titular_pendente(cenario)
    m900.convocar(cenario, cenario["inscricoes"][4], chave="vaga-que-vagou")

    atos = [c.ato for c in _suas(_ler(cenario))]
    assert "Chamar a próxima da fila" not in atos, atos


def test_a_tela_da_convocacao_e_o_cartao_apontam_a_mesma_proxima(client, cenario, seletor_ligado):
    """FR-4549: a mesma parada, as duas leituras."""
    from django.urls import reverse

    from tests.interface.conftest import identificar

    m900.ate_a_desistencia_com_titular_pendente(cenario)
    identificar(client, "carlos", ["gestor"])
    edital = cenario["edital"]
    tela = client.get(
        reverse("interface:convocacao", args=[edital.id, m900.MARCO_2])
    ).content.decode()
    cartao = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()

    assert "próxima da fila" in tela
    assert "Chamar a próxima da fila" in cartao


def _suceder_a_ordem_da_ampla(cenario):
    from processo_seletivo.classificacao.application.calculo import calcular_ordem
    from processo_seletivo.classificacao.application.emissao import (
        assinatura_da_proposta,
        emitir_ordem,
    )
    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from tests.fixtures.edital import PROFILE_ID

    edital = cenario["edital"]
    vigente = ato_vigente(edital=edital, marco_id=m900.MARCO_1, lista_id=None)
    emitir_ordem(
        actor=cenario["gestor"],
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=m900.MARCO_1,
        lista_id=None,
        motivo="Resultado novo no universo da ordem.",
        idempotency_key="m900-sucessora-ampla",
        correlation_id="teste-133",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=m900.MARCO_1),
            ato_vigente=vigente,
        ),
    )


def test_com_a_sucessora_ainda_nao_publicada_o_corte_continua_esperando_o_prazo(
    client, cenario, seletor_ligado
):
    """Revisão do PR #432: a publicação vigente é a de um ato anterior, e o prazo ainda corre.

    O cartão e a tela do corte dizem a mesma coisa — a espera (FR-4546).
    """
    from django.urls import reverse

    from tests.interface.conftest import identificar

    m900.ate_a_ordem_obsoleta(cenario)
    _suceder_a_ordem_da_ampla(cenario)

    ampla = _celulas(_ler(cenario), m900.MARCO_1, andamento.CORTE)[None]
    assert ampla.situacao == andamento.AGUARDA, ampla
    assert ampla.recomendacao

    identificar(client, "carlos", ["gestor"])
    tela = client.get(
        reverse("interface:corte", args=[cenario["edital"].id, m900.MARCO_1])
    ).content.decode()
    assert "Recomendação: aguarde." in tela


def test_sem_nada_de_ninguem_a_praticar_no_marco_o_proximo_nao_pula_para_a_etapa_paralela(
    cenario,
):
    """Revisão do PR #432 (FR-4090 da `127`): com o corte e a definitiva em espera, o próximo
    desta lista é do marco — e não a Etapa de base sem avaliação, que é paralela a ele."""
    lido = _ler(m900.ate_a_preliminar_m1(cenario))

    desta, _, _ = andamento.da_lista(lido, m900.MARCO_1, None, preferir=lambda *_: False)

    assert desta.natureza in (andamento.CORTE, andamento.RESULTADO), desta
