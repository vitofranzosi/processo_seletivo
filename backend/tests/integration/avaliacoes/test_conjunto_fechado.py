"""A distribuição recusa enquanto as inscrições correm (E2E-017), nos **dois** caminhos.

**O achado.** A auditoria registrou que inscrições chegadas depois da distribuição ficavam sem
avaliador. A 013 melhorou o sintoma sem tocar na causa: a participação da Etapa é o conjunto das
submetidas, então a inscrição atrasada aparece como participante sem conclusão e fica retida em
"aguardando" — não some, não é eliminada por omissão e não avança. O que faltava era o invariante:
nada impedia a situação, só a tornava visível depois.

**Por que a proposta também recusa.** Proteger apenas a confirmação faria a presidência montar um
plano inteiro para ser recusada no fim, e o projeto já recusou oferecer o que o domínio nega.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.avaliacoes.application.distribuicao import distribuir, propor_rodizio
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.comissao import (
    ETAPA_A1,
    alocar_em,
    constituir,
    etapas,
    inscrever,
)
from tests.fixtures.edital import complete_draft, identificador
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def rascunho_com_periodo(*, inicio, fim=None):
    base = {**complete_draft(0), "stages": etapas(0)}
    evento = base["schedule"][0]
    evento["isRegistrationPeriod"] = True
    evento["startAt"] = inicio.isoformat()
    if fim is not None:
        evento["endAt"] = fim.isoformat()
    else:
        evento.pop("endAt", None)
    return base


@pytest.fixture
def etapa():
    return identificador(ETAPA_A1, 0)


def cenario(api_client, manager_headers, process_payload, gestor, etapa, *, inicio, fim):
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho_com_periodo(inicio=inicio, fim=fim),
    )
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo="conjunto",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, etapa)
    return edital, membros, inscrever(edital, 2, primeiro=700)


def test_distribuir_e_recusado_enquanto_as_inscricoes_correm(
    api_client, manager_headers, process_payload, gestor, etapa
):
    agora = timezone.now()
    edital, membros, inscricoes = cenario(
        api_client,
        manager_headers,
        process_payload,
        gestor,
        etapa,
        inicio=agora - timedelta(days=1),
        fim=agora + timedelta(days=2),
    )

    with pytest.raises(DomainError) as recusa:
        distribuir(
            actor=gestor,
            processo_id=edital.processo.id,
            edital_id=edital.id,
            etapa_id=etapa,
            membro_ids=[membros["joao"].id],
            inscricao_ids=[i.id for i in inscricoes],
            idempotency_key="conjunto-aberto-01",
            correlation_id="teste",
        )

    assert recusa.value.status == 409
    assert "sem avaliador quem se inscrever depois" in str(recusa.value.detail)


def test_a_proposta_recusa_antes_de_montar_o_plano(
    api_client, manager_headers, process_payload, gestor, etapa
):
    """Proteger só a confirmação deixaria o automático como a porta larga."""
    agora = timezone.now()
    edital, membros, _ = cenario(
        api_client,
        manager_headers,
        process_payload,
        gestor,
        etapa,
        inicio=agora - timedelta(days=1),
        fim=agora + timedelta(days=2),
    )

    with pytest.raises(DomainError) as recusa:
        propor_rodizio(
            actor=gestor,
            processo=edital.processo,
            edital_id=edital.id,
            etapa_id=etapa,
            membro_ids=[membros["joao"].id],
        )

    assert recusa.value.status == 409


def test_encerrado_o_prazo_a_distribuicao_volta_a_ser_admitida(
    api_client, manager_headers, process_payload, gestor, etapa
):
    agora = timezone.now()
    edital, membros, inscricoes = cenario(
        api_client,
        manager_headers,
        process_payload,
        gestor,
        etapa,
        inicio=agora - timedelta(days=9),
        fim=agora - timedelta(hours=1),
    )

    desfecho = distribuir(
        actor=gestor,
        processo_id=edital.processo.id,
        edital_id=edital.id,
        etapa_id=etapa,
        membro_ids=[membros["joao"].id],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key="conjunto-fechado-01",
        correlation_id="teste",
    )

    assert desfecho["feitas"] == len(inscricoes)
