"""Nenhuma listagem da 012 verifica autorização por linha (FR-024, FR-048).

A 011 entregou `etapas_autorizadas` **por causa desta feature**: `pode_atuar_na_etapa` responde por
uma Etapa e custa duas a três consultas, e chamá-lo por linha faria dele o gargalo de uma tela com
quinhentas atribuições. Aqui a regra é verificada de duas formas — pela contagem de chamadas, e
pela equivalência entre as duas maneiras de perguntar a mesma coisa.
"""

from unittest.mock import patch

import pytest

from processo_seletivo.avaliacoes.application import selectors as avaliacao_selectors
from processo_seletivo.comissoes.domain.autorizacao import etapas_autorizadas, pode_atuar_na_etapa
from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import distribuir_para, montar_banca

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=18, codigo="I1")


@pytest.fixture
def com_trabalho(cenario, gestor):
    inscricoes = inscrever(cenario["edital"], 12, primeiro=2500)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-autz")
    return inscricoes


def test_a_mesa_chama_o_guard_no_maximo_uma_vez(cenario, com_trabalho):
    """Doze linhas, e a pergunta é feita uma vez — ou nenhuma, pela forma em lote."""
    joao = ator_institucional("joao")

    with patch(
        "processo_seletivo.comissoes.domain.autorizacao.pode_atuar_na_etapa",
        wraps=pode_atuar_na_etapa,
    ) as guard:
        linhas, _, _ = avaliacao_selectors.mesa(
            ator=joao, edital=cenario["edital"], etapa_id=cenario["etapa"]
        )

    assert len(linhas) == 12
    assert guard.call_count == 0, "a Mesa deve usar a forma em lote, e não o guard individual"


def test_a_mesa_nao_cresce_em_chamadas_com_o_numero_de_linhas(cenario, gestor, com_trabalho):
    joao = ator_institucional("joao")
    outras = inscrever(cenario["edital"], 12, primeiro=2600)
    distribuir_para(cenario, gestor, ["joao"], outras, chave="mais")

    with patch(
        "processo_seletivo.comissoes.domain.autorizacao.pode_atuar_na_etapa",
        wraps=pode_atuar_na_etapa,
    ) as guard:
        avaliacao_selectors.mesa(ator=joao, edital=cenario["edital"], etapa_id=cenario["etapa"])

    assert guard.call_count == 0


def test_as_duas_formas_nunca_divergem(cenario, com_trabalho):
    """O teste que a 011 pediu para a 012 manter.

    `etapas_autorizadas` é uma **otimização de leitura** da mesma regra: se um dia elas
    divergirem, a listagem passará a mostrar o que o guard recusaria — ou a esconder o que ele
    permitiria, que é pior.
    """
    for subject in ("joao", "ana", "maria", "estranho"):
        ator = ator_institucional(subject)
        em_lote = etapas_autorizadas(ator, cenario["edital"])
        uma_a_uma = {
            etapa_id
            for etapa_id in etapas_vigentes(cenario["edital"])
            if pode_atuar_na_etapa(ator, cenario["edital"], etapa_id)
        }

        assert em_lote == uma_a_uma, subject


def test_a_organizacao_do_trabalho_tambem_nao_usa_o_guard(cenario, com_trabalho):
    """A tela da presidência autoriza por gestão, e não pelo guard contextual (FR-067)."""
    from processo_seletivo.comissoes.domain.etapas import etapa_vigente

    etapa = etapa_vigente(cenario["edital"], cenario["etapa"])

    with patch(
        "processo_seletivo.comissoes.domain.autorizacao.pode_atuar_na_etapa",
        wraps=pode_atuar_na_etapa,
    ) as guard:
        avaliacao_selectors.inscricoes_da_etapa(edital=cenario["edital"], etapa=etapa)
        avaliacao_selectors.carga_por_avaliador(edital=cenario["edital"], etapa_id=cenario["etapa"])

    assert guard.call_count == 0


def test_o_guard_individual_continua_valendo_na_rota_de_uma_inscricao(cenario, com_trabalho):
    """Listagem usa a forma em lote; **rota individual usa o guard**, e é aí que ele custa pouco."""
    from processo_seletivo.avaliacoes.domain.autorizacao import pode_avaliar_inscricao

    joao = ator_institucional("joao")
    ana = ator_institucional("ana")

    assert (
        pode_avaliar_inscricao(joao, cenario["edital"], cenario["etapa"], com_trabalho[0].id)
        is not None
    )
    assert (
        pode_avaliar_inscricao(ana, cenario["edital"], cenario["etapa"], com_trabalho[0].id) is None
    )
