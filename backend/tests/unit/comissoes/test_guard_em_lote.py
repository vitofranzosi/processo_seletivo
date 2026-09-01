"""`etapas_autorizadas` — a mesma regra do guard, respondida para o conjunto.

Existe para a 012: ela vai desenhar listas de candidatos, e chamar `pode_atuar_na_etapa` por
linha faria do guard o gargalo da feature seguinte.
"""

import pytest

from processo_seletivo.comissoes.domain.autorizacao import (
    etapas_autorizadas,
    pode_atuar_na_etapa,
)
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em

pytestmark = pytest.mark.django_db


def test_devolve_apenas_as_etapas_alocadas(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    import uuid

    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    autorizadas = etapas_autorizadas(ator_institucional("joao"), edital_a)

    assert autorizadas == {uuid.UUID(etapa_a1)}


def test_concorda_com_o_guard_de_uma_etapa(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    """Duas formas da mesma regra não podem divergir — é o que tornaria o lote perigoso."""
    import uuid

    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    joao = ator_institucional("joao")

    autorizadas = etapas_autorizadas(joao, edital_a)

    for etapa in (etapa_a1, etapa_a2):
        assert (uuid.UUID(etapa) in autorizadas) == pode_atuar_na_etapa(joao, edital_a, etapa)


def test_conjunto_vazio_para_quem_nao_tem_nada(processo_a, edital_a, comissao_de_a):
    assert etapas_autorizadas(ator_institucional("joao"), edital_a) == set()
    assert etapas_autorizadas(ator_institucional("estranho"), edital_a) == set()


def test_escopo_alheio_nao_autoriza(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    de_fora = ator_institucional("joao", escopo="outra-unidade")

    assert etapas_autorizadas(de_fora, edital_a) == set()


def test_uma_leitura_para_o_conjunto(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2, django_assert_max_num_queries
):
    """O ponto da função: responder por N Etapas sem custar N vezes."""
    for etapa in (etapa_a1, etapa_a2):
        alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa)
    joao = ator_institucional("joao")

    with django_assert_max_num_queries(5):
        etapas_autorizadas(joao, edital_a)
