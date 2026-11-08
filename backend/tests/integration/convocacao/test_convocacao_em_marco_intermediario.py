"""A convocação recusa o marco intermediário; encerrar o que existe continua.

133, FR-4534 a FR-4536 e D-002.

O CV-01 do estudo de convergência de 07/11/2026: depois de apurar o marco intermediário, o comando
aceitava convocar, para vaga, quem já tinha desistido no marco final e quem ficara fora das vagas.
"""

from unittest import mock

import pytest
from django.core import mail

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.application import marco_intermediario
from processo_seletivo.convocacao.application import fluxo
from processo_seletivo.convocacao.application.comunicar import comunicar
from processo_seletivo.convocacao.application.convocar import CONVOCAR
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures import marco_intermediario as m900
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return m900.ate_a_apuracao_m2(m900.montar(gestor, api_client, manager_headers, process_payload))


def _contagem():
    return (
        Convocacao.objects.count(),
        ComunicacaoEmitida.objects.count(),
        RegistroAuditoria.objects.filter(operation=CONVOCAR).count(),
        len(mail.outbox),
    )


def _com_apuracao_legada(cenario):
    """A apuração do marco 1 como ela ficaria se gravada antes desta feature."""
    with mock.patch.object(marco_intermediario, "recusar"):
        m900.apurar(cenario, m900.MARCO_1, chave="apurar-legado")


def test_convocar_no_marco_intermediario_e_recusado_sem_gravar_nem_comunicar(cenario):
    _com_apuracao_legada(cenario)
    antes = _contagem()

    with pytest.raises(DomainError) as recusa:
        m900.convocar(cenario, cenario["inscricoes"][0], marco=m900.MARCO_1, chave="m1")

    assert recusa.value.code == marco_intermediario.CODIGO
    assert _contagem() == antes


def test_o_lote_de_titulares_no_marco_intermediario_e_recusado(cenario):
    _com_apuracao_legada(cenario)
    edital = cenario["edital"]
    recorte = {
        "edital": edital,
        "perfil_id": PROFILE_ID,
        "marco_id": m900.MARCO_1,
        "lista_id": None,
    }
    previa = fluxo.previa_dos_titulares(**recorte)
    antes = _contagem()

    with pytest.raises(DomainError) as recusa:
        fluxo.convocar_titulares(
            actor=cenario["gestor"],
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=m900.MARCO_1,
            alcance_confirmado=previa["assinatura"],
            idempotency_key="titulares-m1",
        )

    assert recusa.value.code == marco_intermediario.CODIGO
    assert _contagem() == antes


def test_a_correcao_de_convocacao_legada_e_recusada(cenario):
    """Decisão do usuário de 08/11: a correção cria convocação nova, e é começar um ato."""
    _com_apuracao_legada(cenario)
    with mock.patch.object(marco_intermediario, "recusar"):
        legada = m900.convocar(cenario, cenario["inscricoes"][0], marco=m900.MARCO_1, chave="leg")
    antes = _contagem()

    with pytest.raises(DomainError) as recusa:
        m900.convocar(
            cenario,
            cenario["inscricoes"][0],
            marco=m900.MARCO_1,
            chave="corrige",
            motivo="Correção do vencimento.",
            correcao={"convocacao_id": legada["id"], "assinatura": "qualquer"},
        )

    assert recusa.value.code == marco_intermediario.CODIGO
    assert _contagem() == antes


def test_a_convocacao_legada_ainda_recebe_desfecho(cenario):
    """D-002: encerrar o que existe continua. A apuração seguinte é recusada e fica pendente, sem
    derrubar o desfecho (R-003)."""
    _com_apuracao_legada(cenario)
    edital = cenario["edital"]
    with mock.patch.object(marco_intermediario, "recusar"):
        legada = m900.convocar(cenario, cenario["inscricoes"][0], marco=m900.MARCO_1, chave="leg")
    comunicar(
        actor=cenario["gestor"],
        processo_id=edital.processo_id,
        convocacao_id=legada["id"],
        idempotency_key="comunicar-legada",
        correlation_id="teste-133",
    )

    declarado = desfechar(
        actor=cenario["gestor"],
        processo_id=edital.processo_id,
        convocacao_id=legada["id"],
        especie="DESISTENCIA_EXPRESSA",
        fundamento="Desistência comunicada por e-mail.",
        idempotency_key="desfecho-legada",
        correlation_id="teste-133",
    )

    assert declarado["apuracaoSeguinte"] is None
    assert declarado["apuracaoPendente"]["codigo"] == marco_intermediario.CODIGO


def test_convocar_no_marco_final_continua(cenario):
    declarado = m900.convocar(cenario, cenario["inscricoes"][1])

    assert Convocacao.objects.filter(pk=declarado["id"], marco_id=m900.MARCO_2).exists()
