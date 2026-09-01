"""A alocação em lote — mesma operação, uma submissão.

Continua sendo `membro → Etapa`: nada aqui escolhe quem vai onde, olha carga ou conhece
candidato. O que muda é o custo — pessoa a pessoa, montar uma banca de quarenta em quatro Etapas
eram 160 envios.
"""

import pytest

from processo_seletivo.comissoes.application.alocacao import alocar_varios
from processo_seletivo.comissoes.models import AlocacaoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.comissao import alocar_em, constituir

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def lote(gestor, processo, membros, edital, etapa, chave="lote-1"):
    return alocar_varios(
        actor=gestor,
        processo_id=processo.id,
        membro_ids=[m.id for m in membros],
        edital_id=edital.id,
        etapa_id=etapa,
        idempotency_key=chave,
        correlation_id="c",
    )


def test_aloca_a_comissao_inteira_numa_submissao(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    criadas, ja = lote(gestor, processo_a, comissao_de_a.values(), edital_a, etapa_a1)

    assert len(criadas) == 2 and ja == []
    assert AlocacaoEtapa.objects.filter(ativo=True).count() == 2


def test_quem_ja_esta_na_etapa_nao_faz_o_lote_falhar(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """Recusar o conjunto porque uma pessoa já estava seria punir o caminho normal."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    criadas, ja = lote(gestor, processo_a, comissao_de_a.values(), edital_a, etapa_a1)

    assert [a.membro_id for a in criadas] == [comissao_de_a["maria"].id]
    assert [m.identity_subject for m in ja] == ["joao"]


def test_cada_alocacao_do_lote_gera_o_seu_evento(
    gestor, auditor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """FR-070: a trilha responde por agregado — um evento de lote não diria quem ganhou o quê."""
    from processo_seletivo.auditoria.selectors import trilha_da_comissao

    lote(gestor, processo_a, comissao_de_a.values(), edital_a, etapa_a1)

    registros, _ = trilha_da_comissao(actor=auditor, processo=processo_a, limit=100)
    inclusoes = [r for r in registros if r.operation == "ALOCACAO_INCLUIR"]
    assert len(inclusoes) == 2
    assert all("Análise documental" in r.reason for r in inclusoes)


def test_lote_vazio_e_recusado(gestor, processo_a, edital_a, etapa_a1, comissao_de_a):
    with pytest.raises(DomainError) as recusa:
        lote(gestor, processo_a, [], edital_a, etapa_a1)

    assert recusa.value.code == "nenhum_membro_selecionado"


def test_lote_com_pessoa_de_outra_comissao_e_recusado_inteiro(
    gestor, processo_a, edital_a, edital_b, comissao_de_a, etapa_a1
):
    """O lote não é caminho lateral para alocar quem não é membro (FR-034, EC-005)."""
    alheia = constituir(gestor, edital_b.processo, [("ana", "PRESIDENTE")])["ana"]

    with pytest.raises(DomainError) as recusa:
        lote(
            gestor,
            processo_a,
            [comissao_de_a["joao"], alheia],
            edital_a,
            etapa_a1,
        )

    assert recusa.value.code == "pessoa_nao_e_membro_ativo"
    assert AlocacaoEtapa.objects.count() == 0


def test_lote_exige_presidente(gestor, processo_a, edital_a, etapa_a1):
    membros = constituir(gestor, processo_a, [("joao", "MEMBRO")])

    with pytest.raises(DomainError) as recusa:
        lote(gestor, processo_a, membros.values(), edital_a, etapa_a1)

    assert recusa.value.code == "comissao_sem_presidente"


def test_repetir_o_lote_com_a_mesma_chave_nao_duplica(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    lote(gestor, processo_a, comissao_de_a.values(), edital_a, etapa_a1, chave="k")
    criadas, _ = lote(gestor, processo_a, comissao_de_a.values(), edital_a, etapa_a1, chave="k")

    assert criadas == []
    assert AlocacaoEtapa.objects.filter(ativo=True).count() == 2


def test_pagina_velha_diz_o_que_aconteceu_em_vez_de_repetir_a_regra(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """Corrida e caminho lateral são problemas diferentes, e a recusa passou a distingui-los."""
    from processo_seletivo.comissoes.application.comissao import remover_membro

    remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=comissao_de_a["joao"].id,
        idempotency_key="saiu-durante",
        correlation_id="c",
    )

    with pytest.raises(DomainError) as recusa:
        lote(gestor, processo_a, comissao_de_a.values(), edital_a, etapa_a1)

    assert recusa.value.code == "selecao_desatualizada"
    assert recusa.value.status == 409
    assert "Recarregue" in recusa.value.detail
