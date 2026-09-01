"""T052 — remover da Etapa preserva o vínculo com a comissão (SC-006)."""

import pytest

from processo_seletivo.comissoes.application.alocacao import remover_alocacao
from tests.fixtures.comissao import alocar_em

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_remover_da_etapa_nao_remove_da_comissao(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    joao = comissao_de_a["joao"]
    alocacao = alocar_em(gestor, processo_a, joao, edital_a, etapa_a1)

    remover_alocacao(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_id=alocacao.id,
        idempotency_key="k-1",
        correlation_id="c",
    )

    alocacao.refresh_from_db()
    joao.refresh_from_db()
    assert alocacao.ativo is False and alocacao.inativado_em is not None
    assert joao.ativo is True


def test_remover_uma_etapa_nao_toca_a_outra(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    joao = comissao_de_a["joao"]
    primeira = alocar_em(gestor, processo_a, joao, edital_a, etapa_a1)
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a2)

    remover_alocacao(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_id=primeira.id,
        idempotency_key="k-2",
        correlation_id="c",
    )

    assert joao.alocacoes.filter(ativo=True).count() == 1
