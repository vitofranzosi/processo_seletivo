"""Os quatro atos da presidência repetem sem criar nada (FR-084, FR-086).

Distribuir já tem arquivo próprio. Aqui os outros três — remover, impedir e reabrir —, e a
reautorização depois do bloqueio, que é o que impede a repetição de responder a quem já não pode.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.application.avaliacao import reabrir
from processo_seletivo.avaliacoes.application.distribuicao import remover_atribuicao
from processo_seletivo.avaliacoes.application.impedimento import registrar_impedimento
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, Impedimento
from processo_seletivo.comissoes.application.comissao import alterar_funcao
from processo_seletivo.processos.models import AtoAdministrativo
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.mesa import (
    concluir_como,
    constituir_presidencia,
    distribuir_para,
    inscricoes_de,
    montar_banca,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=12, codigo="C1")


def eventos():
    return RegistroAuditoria.objects.count()


def atos():
    return AtoAdministrativo.objects.count()


def test_remover_repete_sem_criar_registro_nem_evento(cenario, gestor):
    inscricao = inscricoes_de(cenario, 1, primeiro=1200)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao])
    argumentos = {
        "actor": gestor,
        "processo_id": cenario["processo"].id,
        "atribuicao_ids": [Atribuicao.objects.get(inscricao=inscricao).id],
        "idempotency_key": "rem",
        "correlation_id": "teste",
    }
    primeiro = remover_atribuicao(**argumentos)
    antes = eventos()

    repetido = remover_atribuicao(**argumentos)

    assert repetido == primeiro
    assert eventos() == antes


def test_impedir_repete_sem_criar_registro_nem_evento(cenario, gestor):
    inscricao = inscricoes_de(cenario, 1, primeiro=1210)[0]
    argumentos = {
        "actor": gestor,
        "processo_id": cenario["processo"].id,
        "identity_subject": "joao",
        "inscricao_id": inscricao.id,
        "motivo": "Parentesco.",
        "idempotency_key": "imp",
        "correlation_id": "teste",
    }
    registrar_impedimento(**argumentos)
    antes_eventos, antes_atos = eventos(), atos()

    registrar_impedimento(**argumentos)

    assert Impedimento.objects.count() == 1
    assert eventos() == antes_eventos
    assert atos() == antes_atos


def test_reabrir_repete_sem_criar_ato_novo(cenario, gestor):
    inscricao = inscricoes_de(cenario, 1, primeiro=1220)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao])
    avaliacao = concluir_como(cenario, "joao", inscricao)
    argumentos = {
        "actor": gestor,
        "processo_id": cenario["processo"].id,
        "avaliacao_id": avaliacao.id,
        "motivo": "Recurso deferido.",
        "expected_revision": avaliacao.revision,
        "idempotency_key": "reab",
        "correlation_id": "teste",
    }
    reabrir(**argumentos)
    antes_atos = atos()

    reabrir(**argumentos)

    assert atos() == antes_atos
    assert Avaliacao.objects.get(pk=avaliacao.pk).estado == Avaliacao.Estado.RASCUNHO


@pytest.mark.parametrize("chave", ["imp-conflito"])
def test_a_mesma_chave_com_outro_conteudo_e_conflito(cenario, gestor, chave):
    """Repetir é devolver o desfecho; **mudar** o conteúdo sob a mesma chave é outra coisa."""
    uma, outra = inscricoes_de(cenario, 2, primeiro=1230)
    registrar_impedimento(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject="joao",
        inscricao_id=uma.id,
        motivo="Parentesco.",
        idempotency_key=chave,
        correlation_id="teste",
    )

    with pytest.raises(DomainError) as recusa:
        registrar_impedimento(
            actor=gestor,
            processo_id=cenario["processo"].id,
            identity_subject="joao",
            inscricao_id=outra.id,
            motivo="Outro motivo.",
            idempotency_key=chave,
            correlation_id="teste",
        )

    assert recusa.value.code == "idempotency_conflict"


def test_quem_perdeu_a_presidencia_no_intervalo_nao_impede(cenario, gestor):
    """A base é reavaliada **depois** do bloqueio, e a presidência é dado que muda (FR-086)."""
    inscricao = inscricoes_de(cenario, 1, primeiro=1240)[0]
    maria = ator_institucional("maria")
    registrar_impedimento(
        actor=maria,
        processo_id=cenario["processo"].id,
        identity_subject="joao",
        inscricao_id=inscricao.id,
        motivo="Primeiro ato dela.",
        idempotency_key="de-maria",
        correlation_id="teste",
    )
    constituir_presidencia(gestor, cenario)
    alterar_funcao(
        actor=gestor,
        processo_id=cenario["processo"].id,
        membro_id=cenario["membros"]["maria"].id,
        funcao="MEMBRO",
        idempotency_key="rebaixar",
        correlation_id="teste",
    )

    with pytest.raises(DomainError) as recusa:
        registrar_impedimento(
            actor=maria,
            processo_id=cenario["processo"].id,
            identity_subject="ana",
            inscricao_id=inscricao.id,
            motivo="Depois de rebaixada.",
            idempotency_key="de-maria-2",
            correlation_id="teste",
        )

    assert recusa.value.status == 404
