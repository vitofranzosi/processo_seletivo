"""T031 — alocar: o caminho feliz e as quatro recusas que o definem."""

import pytest

from processo_seletivo.comissoes.application.alocacao import alocar
from processo_seletivo.comissoes.models import AlocacaoEtapa
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.comissao import alocar_em, constituir

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_aloca_membro_a_etapa_do_proprio_processo(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    alocacao = alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    assert alocacao.ativo
    assert str(alocacao.etapa_id) == etapa_a1


def test_mesma_pessoa_em_varias_etapas_e_em_varios_editais(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    """FR-037: sem duplicar o vínculo de comissão."""
    joao = comissao_de_a["joao"]
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a1)
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a2)

    assert joao.alocacoes.filter(ativo=True).count() == 2


def test_etapa_de_edital_de_outro_processo_e_recusada(
    gestor, processo_a, edital_b, comissao_de_a, etapa_b1
):
    """EC-004: a coerência percorre etapa → edital → processo, e é do servidor."""
    with pytest.raises(DomainError) as recusa:
        alocar(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=comissao_de_a["joao"].id,
            edital_id=edital_b.id,
            etapa_id=etapa_b1,
            idempotency_key="k-x",
            correlation_id="c",
        )

    assert recusa.value.status == 404
    assert AlocacaoEtapa.objects.count() == 0


def test_pessoa_que_nao_e_membro_e_recusada(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, edital_b
):
    """EC-005: a jornada é pessoa → comissão → Etapa, e nunca pessoa → Etapa."""
    de_outra_comissao = constituir(gestor, edital_b.processo, [("ana", "PRESIDENTE")])["ana"]

    with pytest.raises(DomainError) as recusa:
        alocar(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=de_outra_comissao.id,
            edital_id=edital_a.id,
            etapa_id=etapa_a1,
            idempotency_key="k-y",
            correlation_id="c",
        )

    assert recusa.value.code == "pessoa_nao_e_membro_ativo"


def test_etapa_inexistente_no_conteudo_vigente_e_recusada(
    gestor, processo_a, edital_a, comissao_de_a
):
    with pytest.raises(DomainError) as recusa:
        alocar(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=comissao_de_a["joao"].id,
            edital_id=edital_a.id,
            etapa_id="00000000-0000-0000-0000-000000000999",
            idempotency_key="k-z",
            correlation_id="c",
        )

    assert recusa.value.status == 404


def test_edital_sem_versao_publicada_e_recusado(
    gestor, api_client, manager_headers, processo_a, comissao_de_a, etapa_a1
):
    """FR-032 e EC-014: a fonte é a Versão Consolidada vigente, e ela não existe ainda."""
    api_client.post(
        f"/api/v1/admin/processos/{processo_a.id}/editais",
        {"number": "77", "year": 2026, "title": "Ainda em elaboração"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "edital-em-elaboracao"},
    )
    novo = Edital.objects.get(processo=processo_a, number="77")

    with pytest.raises(DomainError) as recusa:
        alocar(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=comissao_de_a["joao"].id,
            edital_id=novo.id,
            etapa_id=etapa_a1,
            idempotency_key="k-w",
            correlation_id="c",
        )

    assert recusa.value.code == "edital_sem_versao_vigente"


def test_alocacao_ativa_repetida_com_chave_nova_e_conflito(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """EC-002: repetição é uma coisa; dois pedidos distintos para o mesmo vínculo são outra."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1, chave="k-1")

    with pytest.raises(DomainError) as recusa:
        alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1, chave="k-2")

    assert recusa.value.code == "alocacao_ja_existe"
    assert AlocacaoEtapa.objects.filter(ativo=True).count() == 1
