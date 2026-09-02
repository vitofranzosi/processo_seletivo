"""T072 — a trilha: os cinco eventos, a base real e a cascata evento a evento."""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.auditoria.selectors import trilha_da_comissao
from processo_seletivo.comissoes.application.alocacao import remover_alocacao
from processo_seletivo.comissoes.application.comissao import alterar_funcao, remover_membro
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_as_cinco_operacoes_ficam_registradas(
    gestor, auditor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    joao = comissao_de_a["joao"]
    alocacao = alocar_em(gestor, processo_a, joao, edital_a, etapa_a1)
    remover_alocacao(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_id=alocacao.id,
        idempotency_key="k1",
        correlation_id="c",
    )
    alterar_funcao(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=joao.id,
        funcao="PRESIDENTE",
        idempotency_key="k2",
        correlation_id="c",
    )
    remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=joao.id,
        idempotency_key="k3",
        correlation_id="c",
    )

    registros, _ = trilha_da_comissao(actor=auditor, processo=processo_a, limit=100)
    operacoes = {registro.operation for registro in registros}
    assert operacoes == {
        "COMISSAO_INCLUIR_MEMBRO",
        "COMISSAO_ALTERAR_FUNCAO",
        "COMISSAO_REMOVER_MEMBRO",
        "ALOCACAO_INCLUIR",
        "ALOCACAO_REMOVER",
    }


def test_a_trilha_registra_a_base_efetivamente_usada(gestor, auditor, processo_a, comissao_de_a):
    """FR-016: com duas bases, registrar sempre a sistêmica apagaria a informação que elas criam."""
    maria = ator_institucional("maria")
    alterar_funcao(
        actor=maria,
        processo_id=processo_a.id,
        membro_id=comissao_de_a["joao"].id,
        funcao="PRESIDENTE",
        idempotency_key="k",
        correlation_id="c",
    )

    registros, _ = trilha_da_comissao(actor=auditor, processo=processo_a, limit=100)
    por_ator = {r.actor_subject: r.permission for r in registros}
    assert por_ator["carlos"] == "comissao:gerir"
    assert por_ator["maria"] == "comissao:presidir"


def test_remover_membro_com_tres_alocacoes_grava_quatro_eventos(
    gestor, auditor, processo_a, edital_a, edital_b, comissao_de_a, etapa_a1, etapa_a2
):
    """A trilha responde por agregado: um evento único não nomearia as três Etapas."""
    joao = comissao_de_a["joao"]
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a1)
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a2)
    antes = RegistroAuditoria.objects.count()

    remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=joao.id,
        idempotency_key="k",
        correlation_id="c",
    )

    novos = RegistroAuditoria.objects.count() - antes
    assert novos == 3  # duas alocações + o membro


def test_a_trilha_nao_grava_o_rotulo_de_exibicao(gestor, auditor, processo_a):
    """FR-075: o rótulo é leitura humana da lista, e não identidade."""
    from processo_seletivo.comissoes.application.comissao import adicionar_membro

    adicionar_membro(
        actor=gestor,
        processo_id=processo_a.id,
        identity_subject="joao",
        display_label="João da Silva",
        funcao="MEMBRO",
        idempotency_key="k",
        correlation_id="c",
    )

    registros, _ = trilha_da_comissao(actor=auditor, processo=processo_a, limit=100)
    assert all("João da Silva" not in (r.reason or "") for r in registros)


def test_a_trilha_nomeia_a_etapa_e_nao_so_o_identificador(
    gestor, auditor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """L6: "Etapa 00000000-...-d1" identifica sem informar. Quem audita precisa do nome."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    registros, _ = trilha_da_comissao(actor=auditor, processo=processo_a, limit=100)
    inclusao = next(r for r in registros if r.operation == "ALOCACAO_INCLUIR")

    assert "Análise documental" in inclusao.reason
    assert str(etapa_a1) not in inclusao.reason


def test_a_cascata_tambem_nomeia_a_etapa(
    gestor, auditor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=comissao_de_a["joao"].id,
        idempotency_key="k-cascata",
        correlation_id="c",
    )

    registros, _ = trilha_da_comissao(actor=auditor, processo=processo_a, limit=100)
    remocoes = [r for r in registros if r.operation == "ALOCACAO_REMOVER"]

    assert any(
        "Análise documental" in r.reason and "saída da comissão" in r.reason for r in remocoes
    )


def test_o_filtro_por_pessoa_e_exato_e_nao_por_pedaco_do_motivo(
    gestor, auditor, processo_a, edital_a, etapa_a1
):
    """Filtrar “ana” trazia os atos de “susana.lima” — numa trilha isso é pior que não filtrar."""
    from processo_seletivo.comissoes.application.comissao import adicionar_varios

    adicionar_varios(
        actor=gestor,
        processo_id=processo_a.id,
        entradas=[("ana", "Ana Costa"), ("susana.lima", "Susana Lima")],
        funcao="PRESIDENTE",
        idempotency_key="filtro-exato",
        correlation_id="c",
    )

    registros, _ = trilha_da_comissao(actor=auditor, processo=processo_a, pessoa="ana", limit=100)

    assert registros
    assert all("susana" not in r.reason for r in registros)
    assert all("ana incluído" in r.reason for r in registros)


def test_filtrar_por_quem_nao_integra_a_comissao_devolve_vazio(
    gestor, auditor, processo_a, comissao_de_a
):
    registros, _ = trilha_da_comissao(
        actor=auditor, processo=processo_a, pessoa="ninguem", limit=100
    )

    assert registros == []
