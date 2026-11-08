"""A ocupação recusa o marco intermediário, e nada fica gravado (133, FR-4532, FR-4533, FR-4536).

O caso é o CV-01 do estudo de convergência de 07/11/2026: com as vagas apuradas no marco final, o
cartão mandava apurar a *Classificação para a entrevista*, e o comando aceitava. Aqui o comando é
chamado direto, sem tela, como pela API.
"""

from unittest import mock

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.application import marco_intermediario
from processo_seletivo.ocupacao.application.acrescimo import acrescentar_vagas
from processo_seletivo.ocupacao.application.causar_faixa import causar_faixa_seguinte
from processo_seletivo.ocupacao.application.emissao import APURAR
from processo_seletivo.ocupacao.models import AcrescimoDeVagas, ApuracaoDeOcupacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures import marco_intermediario as m900
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return m900.ate_a_apuracao_m2(m900.montar(gestor, api_client, manager_headers, process_payload))


def _contagem():
    return (
        ApuracaoDeOcupacao.objects.count(),
        AcrescimoDeVagas.objects.count(),
        RegistroAuditoria.objects.filter(operation=APURAR).count(),
    )


@pytest.mark.parametrize("lista", m900.LISTAS)
def test_apurar_o_marco_intermediario_e_recusado_sem_gravar(cenario, lista):
    antes = _contagem()

    with pytest.raises(DomainError) as recusa:
        m900.apurar(cenario, m900.MARCO_1, lista, chave="apurar-m1")

    assert recusa.value.code == marco_intermediario.CODIGO
    assert "Classificação final" in recusa.value.detail
    assert _contagem() == antes


def test_repetir_o_pedido_recusado_recusa_de_novo(cenario):
    for _ in range(2):
        with pytest.raises(DomainError) as recusa:
            m900.apurar(cenario, m900.MARCO_1, chave="apurar-repetido")
        assert recusa.value.code == marco_intermediario.CODIGO


def test_a_apuracao_do_marco_final_continua_aceita(cenario):
    sucessora = m900.apurar(
        cenario, m900.MARCO_2, chave="apurar-de-novo", motivo="Conferência da suíte."
    )

    assert sucessora["publicadas"] == 2


def test_acrescentar_vaga_no_marco_intermediario_e_recusado(cenario):
    edital = cenario["edital"]
    antes = _contagem()

    with pytest.raises(DomainError) as recusa:
        acrescentar_vagas(
            actor=cenario["gestor"],
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=m900.MARCO_1,
            quantidade=1,
            origem="Portaria fictícia",
            fundamento="Ampliação de turma.",
            leitura_confirmada="qualquer",
            idempotency_key="acrescimo-m1",
            correlation_id="teste-133",
        )

    assert recusa.value.code == marco_intermediario.CODIGO
    assert _contagem() == antes


def test_a_faixa_por_deficit_de_uma_apuracao_legada_e_recusada(cenario):
    """Uma apuração legada no marco 1 (gravada antes desta feature) não vira faixa seguinte."""
    with mock.patch.object(marco_intermediario, "recusar"):
        m900.apurar(cenario, m900.MARCO_1, chave="apurar-legado")

    with pytest.raises(DomainError) as recusa:
        causar_faixa_seguinte(
            actor=cenario["gestor"],
            processo_id=cenario["edital"].processo_id,
            edital=cenario["edital"],
            perfil_id=PROFILE_ID,
            marco_id=m900.MARCO_1,
            idempotency_key="faixa-m1",
            correlation_id="teste-133",
        )

    assert recusa.value.code == marco_intermediario.CODIGO
    # A apuração legada continua vigente e legível (FR-4540).
    assert ApuracaoDeOcupacao.objects.filter(marco_id=m900.MARCO_1).count() == 1
