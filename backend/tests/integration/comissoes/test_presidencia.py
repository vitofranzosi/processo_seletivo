"""T032 e T057 — a governança: alocar exige presidente, e o último não some com trabalho ativo."""

import pytest

from processo_seletivo.comissoes.application.comissao import alterar_funcao, remover_membro
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.comissao import alocar_em, constituir

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_comissao_sem_presidente_pode_ser_constituida(gestor, processo_a):
    """D-007: o estado transitório é legítimo — senão o primeiro membro teria de ser o presidente."""
    membros = constituir(gestor, processo_a, [("joao", "MEMBRO"), ("ana", "MEMBRO")])

    assert len(membros) == 2


def test_comissao_sem_presidente_nao_aloca(gestor, processo_a, edital_a, etapa_a1):
    membros = constituir(gestor, processo_a, [("joao", "MEMBRO")])

    with pytest.raises(DomainError) as recusa:
        alocar_em(gestor, processo_a, membros["joao"], edital_a, etapa_a1)

    assert recusa.value.code == "comissao_sem_presidente"
    assert "presidência" in recusa.value.detail


def test_rebaixar_o_ultimo_presidente_com_alocacao_ativa_e_recusado(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    with pytest.raises(DomainError) as recusa:
        alterar_funcao(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=comissao_de_a["maria"].id,
            funcao="MEMBRO",
            idempotency_key="k-1",
            correlation_id="c",
        )

    assert recusa.value.code == "comissao_ficaria_sem_presidente"
    # A recusa nomeia o caminho, e não só o impedimento.
    assert "outro membro" in recusa.value.detail


def test_remover_o_ultimo_presidente_com_alocacao_ativa_e_recusado(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    with pytest.raises(DomainError):
        remover_membro(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=comissao_de_a["maria"].id,
            idempotency_key="k-2",
            correlation_id="c",
        )


def test_designar_outro_presidente_antes_libera_a_remocao(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """O caminho feliz que a recusa nomeia."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    alterar_funcao(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=comissao_de_a["joao"].id,
        funcao="PRESIDENTE",
        idempotency_key="k-3",
        correlation_id="c",
    )

    membro, status = remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=comissao_de_a["maria"].id,
        idempotency_key="k-4",
        correlation_id="c",
    )

    assert status == 200 and membro.ativo is False


def test_sem_alocacao_ativa_o_presidente_pode_sair(gestor, processo_a, comissao_de_a):
    """A presidência é exigível porque há trabalho distribuído — sem ele, não há o que travar."""
    membro, status = remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=comissao_de_a["maria"].id,
        idempotency_key="k-5",
        correlation_id="c",
    )

    assert status == 200 and membro.ativo is False
