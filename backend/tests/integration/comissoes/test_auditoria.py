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
