"""T021 — constituir a comissão: inclusão, duplicidade e repetição."""

import pytest

from processo_seletivo.comissoes.application.comissao import adicionar_membro
from processo_seletivo.comissoes.models import MembroComissao
from processo_seletivo.shared.api.problems import DomainError

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def incluir(gestor, processo, subject, funcao="MEMBRO", chave="k-1"):
    return adicionar_membro(
        actor=gestor,
        processo_id=processo.id,
        identity_subject=subject,
        funcao=funcao,
        idempotency_key=chave,
        correlation_id="c-1",
    )


def test_inclui_membro_na_comissao_do_processo(gestor, processo_a):
    membro, status = incluir(gestor, processo_a, "maria", "PRESIDENTE")

    assert status == 201
    assert membro.processo_id == processo_a.id
    assert membro.ativo and membro.funcao == "PRESIDENTE"


def test_incluir_nao_concede_acesso_a_etapa_alguma(gestor, processo_a):
    """§13 da spec: integrar a comissão é uma coisa; atuar numa Etapa é outra."""
    membro, _ = incluir(gestor, processo_a, "joao")

    assert membro.alocacoes.count() == 0


def test_mesma_pessoa_nao_tem_dois_vinculos_ativos(gestor, processo_a):
    """EC-001: a segunda tentativa é conflito, e não duplicidade."""
    incluir(gestor, processo_a, "joao", chave="k-1")

    with pytest.raises(DomainError) as recusa:
        incluir(gestor, processo_a, "joao", chave="k-2")

    assert recusa.value.code == "membro_ja_integra_a_comissao"
    assert recusa.value.status == 409
    assert MembroComissao.objects.filter(processo=processo_a, ativo=True).count() == 1


def test_repetir_a_mesma_chave_devolve_o_resultado_original(gestor, processo_a):
    """FR-064: repetição não é conflito — o duplo clique não pode virar erro."""
    primeiro, _ = incluir(gestor, processo_a, "joao", chave="k-1")
    segundo, status = incluir(gestor, processo_a, "joao", chave="k-1")

    assert segundo.pk == primeiro.pk
    assert status == 201
    assert MembroComissao.objects.filter(processo=processo_a).count() == 1


def test_identificador_vazio_e_recusado(gestor, processo_a):
    with pytest.raises(DomainError) as recusa:
        incluir(gestor, processo_a, "   ")

    assert recusa.value.code == "identificador_ausente"


def test_pessoa_de_outro_escopo_nao_alcanca_o_processo(processo_a):
    """FR-056: escopo divergente responde como recurso inexistente, e não como proibido."""
    from tests.integration.comissoes.conftest import ator

    de_fora = ator("carlos", "comissao:gerir", escopo="outra-unidade")
    with pytest.raises(DomainError) as recusa:
        incluir(de_fora, processo_a, "joao")

    assert recusa.value.status == 404


def test_sem_base_nenhuma_responde_como_inexistente(sem_nada, processo_a):
    with pytest.raises(DomainError) as recusa:
        incluir(sem_nada, processo_a, "joao")

    assert recusa.value.status == 404
