"""T056 — a cascata: sair da comissão leva junto as alocações, na mesma transação."""

import pytest

from processo_seletivo.comissoes.application.comissao import remover_membro
from processo_seletivo.comissoes.models import AlocacaoEtapa
from tests.fixtures.comissao import alocar_em

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_remover_membro_inativa_todas_as_alocacoes_dele(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    """EC-003: alocação ativa sob membro inativo é relação contraditória."""
    joao = comissao_de_a["joao"]
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a1)
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a2)

    remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=joao.id,
        idempotency_key="k-1",
        correlation_id="c",
    )

    joao.refresh_from_db()
    assert joao.ativo is False
    assert AlocacaoEtapa.objects.filter(membro=joao, ativo=True).count() == 0
    assert AlocacaoEtapa.objects.filter(membro=joao, ativo=False).count() == 2


def test_nenhuma_alocacao_ativa_sobrevive_a_membro_inativo(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=comissao_de_a["joao"].id,
        idempotency_key="k-2",
        correlation_id="c",
    )

    contraditorias = AlocacaoEtapa.objects.filter(ativo=True, membro__ativo=False)
    assert contraditorias.count() == 0
