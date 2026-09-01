"""T016 — as duas perguntas de autorização, e o que cada uma recusa."""

import pytest

from processo_seletivo.comissoes.domain.autorizacao import (
    BASE_PRESIDENCIA,
    PERMISSAO_SISTEMICA,
    pode_atuar_na_etapa,
    pode_gerir_comissao,
)
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em

pytestmark = pytest.mark.django_db


def test_permissao_sistemica_autoriza_gerir(gestor, processo_a):
    base = pode_gerir_comissao(gestor, processo_a)

    assert base is not None and base.permissao == PERMISSAO_SISTEMICA


def test_presidencia_autoriza_gerir_sem_o_papel_de_gestor(processo_a, comissao_de_a):
    """SC-020: as duas bases são independentes, e cada uma basta sozinha."""
    maria = ator_institucional("maria")

    base = pode_gerir_comissao(maria, processo_a)

    assert base is not None and base.permissao == BASE_PRESIDENCIA


def test_membro_comum_nao_gere(processo_a, comissao_de_a):
    assert pode_gerir_comissao(ator_institucional("joao"), processo_a) is None


def test_presidencia_vale_so_no_processo_dela(processo_a, edital_b, comissao_de_a):
    """SC-011: presidir não é papel global — se fosse, valeria em todo Processo."""
    maria = ator_institucional("maria")

    assert pode_gerir_comissao(maria, edital_b.processo) is None


def test_presidente_nao_alocado_nao_atua(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    """FR-012: presidir não concede atuação. Para atuar, tem de estar alocado como qualquer um."""
    maria = ator_institucional("maria")

    assert pode_gerir_comissao(maria, processo_a) is not None
    assert pode_atuar_na_etapa(maria, edital_a, etapa_a1) is False


def test_alocado_atua_na_etapa_dele_e_nao_na_outra(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    joao = ator_institucional("joao")
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    assert pode_atuar_na_etapa(joao, edital_a, etapa_a1) is True
    # SC-010: alocação numa Etapa não alcança a vizinha, nem no mesmo Edital.
    assert pode_atuar_na_etapa(joao, edital_a, etapa_a2) is False


def test_escopo_divergente_nao_autoriza(processo_a, edital_a, comissao_de_a, etapa_a1):
    de_fora = ator_institucional("maria", PERMISSAO_SISTEMICA, escopo="outra-unidade")

    assert pode_gerir_comissao(de_fora, processo_a) is None
    assert pode_atuar_na_etapa(de_fora, edital_a, etapa_a1) is False
