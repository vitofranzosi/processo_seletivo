"""T022 e T059 — quem pode gerir a comissão, e quem recebe 404 tentando."""

import pytest

from processo_seletivo.comissoes.application.comissao import adicionar_membro, alterar_funcao
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]


def incluir(ator, processo, subject="ana", chave="k"):
    return adicionar_membro(
        actor=ator,
        processo_id=processo.id,
        identity_subject=subject,
        funcao="MEMBRO",
        idempotency_key=chave,
        correlation_id="c",
    )


def test_o_presidente_gere_sem_possuir_a_permissao_sistemica(processo_a, comissao_de_a):
    """SC-020, primeira metade."""
    maria = ator_institucional("maria")

    membro, status = incluir(maria, processo_a)

    assert status == 201 and membro.identity_subject == "ana"


def test_quem_possui_a_permissao_gere_sem_ser_membro(gestor, processo_a):
    """SC-020, segunda metade: FR-013 — permissão global não faz ninguém membro."""
    from processo_seletivo.comissoes.models import MembroComissao

    incluir(gestor, processo_a)

    assert not MembroComissao.objects.filter(identity_subject="carlos").exists()


def test_membro_comum_nao_gere(processo_a, comissao_de_a):
    with pytest.raises(DomainError) as recusa:
        incluir(ator_institucional("joao"), processo_a)

    assert recusa.value.status == 404


def test_presidente_de_outro_processo_nao_gere_este(processo_a, edital_b, comissao_de_a):
    """SC-011: presidir não é papel global."""
    maria = ator_institucional("maria")

    with pytest.raises(DomainError) as recusa:
        incluir(maria, edital_b.processo)

    assert recusa.value.status == 404


def test_escopo_alheio_responde_como_inexistente(processo_a):
    """SC-016: 404, e não 403 — enumerar já seria revelar."""
    de_fora = ator_institucional("carlos", "comissao:gerir", escopo="outra-unidade")

    with pytest.raises(DomainError) as recusa:
        incluir(de_fora, processo_a)

    assert recusa.value.status == 404


def test_membro_de_outro_processo_nao_e_alcancavel_pelo_identificador(
    gestor, processo_a, edital_b, comissao_de_a
):
    """Trocar o identificador na requisição não alcança a composição alheia."""
    from tests.fixtures.comissao import constituir

    alheio = constituir(gestor, edital_b.processo, [("ana", "MEMBRO")])["ana"]

    with pytest.raises(DomainError) as recusa:
        alterar_funcao(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=alheio.id,
            funcao="PRESIDENTE",
            idempotency_key="k",
            correlation_id="c",
        )

    assert recusa.value.status == 404
