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


def test_remove_varias_alocacoes_numa_submissao(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    """Desfazer pelo mesmo preço de fazer: a assimetria é o que tornava a ida arriscada."""
    from processo_seletivo.comissoes.application.alocacao import remover_varias_alocacoes
    from processo_seletivo.comissoes.models import AlocacaoEtapa

    joao = comissao_de_a["joao"]
    alocacoes = [
        alocar_em(gestor, processo_a, joao, edital_a, etapa) for etapa in (etapa_a1, etapa_a2)
    ]

    removidas = remover_varias_alocacoes(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_ids=[a.id for a in alocacoes],
        idempotency_key="remocao-lote-1",
        correlation_id="c",
    )

    assert len(removidas) == 2
    assert AlocacaoEtapa.objects.filter(ativo=True).count() == 0
    joao.refresh_from_db()
    assert joao.ativo is True


def test_remocao_em_lote_de_alocacao_alheia_e_recusada(
    gestor, processo_a, edital_b, comissao_de_a, etapa_b1
):
    from processo_seletivo.comissoes.application.alocacao import remover_varias_alocacoes
    from processo_seletivo.shared.api.problems import DomainError
    from tests.fixtures.comissao import constituir

    alheia = constituir(gestor, edital_b.processo, [("ana", "PRESIDENTE")])["ana"]
    da_outra = alocar_em(gestor, edital_b.processo, alheia, edital_b, etapa_b1)

    with pytest.raises(DomainError) as recusa:
        remover_varias_alocacoes(
            actor=gestor,
            processo_id=processo_a.id,
            alocacao_ids=[da_outra.id],
            idempotency_key="remocao-alheia",
            correlation_id="c",
        )

    assert recusa.value.status == 409


def test_id_que_nao_e_do_processo_recusa_o_lote_inteiro(
    gestor, processo_a, edital_a, edital_b, comissao_de_a, etapa_a1, etapa_b1
):
    """Remover quatro de cinco e responder sucesso deixa a quinta pessoa com acesso."""
    import uuid

    from processo_seletivo.comissoes.application.alocacao import remover_varias_alocacoes
    from processo_seletivo.comissoes.models import AlocacaoEtapa
    from processo_seletivo.shared.api.problems import DomainError

    valida = alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    with pytest.raises(DomainError) as recusa:
        remover_varias_alocacoes(
            actor=gestor,
            processo_id=processo_a.id,
            alocacao_ids=[valida.id, uuid.uuid4()],
            idempotency_key="lote-com-id-alheio",
            correlation_id="c",
        )

    # 409, e não 404: a causa quase sempre é concorrência, e recusa de estado não pode derrubar
    # a página inteira nem esconder de quem opera o que aconteceu.
    assert recusa.value.status == 409
    assert recusa.value.code == "selecao_desatualizada"
    assert "Recarregue" in recusa.value.detail
    valida.refresh_from_db()
    assert valida.ativo is True
    assert AlocacaoEtapa.objects.filter(ativo=True).count() == 1


def test_remover_a_mesma_alocacao_duas_vezes_no_lote_nao_e_conflito(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """Repetir um id na seleção é engano de quem marcou, e o conjunto é o que importa."""
    from processo_seletivo.comissoes.application.alocacao import remover_varias_alocacoes

    alocacao = alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    removidas = remover_varias_alocacoes(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_ids=[alocacao.id, alocacao.id],
        idempotency_key="lote-repetido",
        correlation_id="c",
    )

    assert len(removidas) == 1
