"""T063 e T067 — a Retificação que mexe numa Etapa alocada.

Este é o teste que prova D-002. Se a alocação apontasse para a linha de elaboração, uma destas
duas coisas aconteceria: a Retificação falharia, ou a alocação sumiria em silêncio. Nenhuma das
duas pode acontecer — e o que sobra, a alocação órfã, é derivado na leitura e não persistido.
"""

import pytest

from processo_seletivo.comissoes.application import selectors
from processo_seletivo.comissoes.domain.autorizacao import pode_atuar_na_etapa
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em
from tests.fixtures.publicacao import retify

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def caminho_da_etapa(etapa_id, campo=""):
    caminho = f"/stages/id={etapa_id}"
    return f"{caminho}/{campo}" if campo else caminho


def test_remover_a_etapa_alocada_nao_falha_e_nao_apaga_a_alocacao(
    api_client, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    alocacao = alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    retify(
        api_client, edital_a, [{"targetPath": caminho_da_etapa(etapa_a1), "operation": "REMOVE"}]
    )

    alocacao.refresh_from_db()
    assert alocacao.ativo is True  # não foi apagada nem inativada por efeito colateral


def test_a_alocacao_sem_etapa_vira_orfa_derivada(
    api_client, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    alocacao = alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    retify(
        api_client, edital_a, [{"targetPath": caminho_da_etapa(etapa_a1), "operation": "REMOVE"}]
    )

    orfas = selectors.orfas(processo_a)

    assert [o.pk for o in orfas] == [alocacao.pk]


def test_a_orfa_nao_concede_acesso_e_some_de_minhas_etapas(
    api_client, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """FR-047: a identidade saiu do conteúdo vigente, então não há o que autorizar."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    joao = ator_institucional("joao")
    assert pode_atuar_na_etapa(joao, edital_a, etapa_a1) is True

    retify(
        api_client, edital_a, [{"targetPath": caminho_da_etapa(etapa_a1), "operation": "REMOVE"}]
    )

    assert pode_atuar_na_etapa(joao, edital_a, etapa_a1) is False
    assert selectors.minhas_etapas(joao) == []


def test_mudar_o_nome_preservando_a_identidade_nao_produz_orfa(
    api_client, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """A outra metade do FR-084, e a que costuma passar despercebida."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    retify(
        api_client,
        edital_a,
        [
            {
                "targetPath": caminho_da_etapa(etapa_a1, "name"),
                "operation": "REPLACE",
                "newValue": "Análise de títulos",
            }
        ],
    )

    joao = ator_institucional("joao")
    assert selectors.orfas(processo_a) == []
    assert pode_atuar_na_etapa(joao, edital_a, etapa_a1) is True
    assert [a["nome"] for a in selectors.minhas_etapas(joao)] == ["Análise de títulos"]
