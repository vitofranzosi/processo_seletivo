"""A apuração seguinte sai com o desfecho, e só quando a única coisa que mudou foi ele (050).

É a `D-005` da `050`.

**Três condições, uma por teste**: outra causa de obsolescência não é varrida; a conta que moveria
vaga não é gravada; e a recusa da emissão não desfaz o desfecho. As duas últimas dependem de estados
que o cenário do 77 não produz — uma cota sem ninguém, um empate na fronteira —, e por isso o ponto
de decisão é substituído por `mock`: o que se prova é o que o desfecho faz com cada resposta.
"""

from unittest import mock

import pytest

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import DesfechoDaConvocacao
from processo_seletivo.ocupacao.application import selectors as ocupacao_selectors
from processo_seletivo.ocupacao.domain import nomes as nomes_da_ocupacao
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao, MovimentoDeVaga
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.convocacao import convocar
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)


def titular_convocado(edital, gestor):
    contexto = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    return convocar(edital, gestor, contexto["fila"][0], idempotency_key="seguinte-convoca")


def desistir(edital, gestor, convocacao_id, chave="seguinte-desiste"):
    return desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao_id,
        especie=nomes.DESISTENCIA_EXPRESSA,
        fundamento="Desistência por escrito.",
        idempotency_key=chave,
        correlation_id="teste",
    )


def causas(edital):
    vigente = ocupacao_selectors.apuracao_vigente(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    return [c["causa"] for c in ocupacao_selectors.causas_de_obsolescencia(vigente)]


def test_o_desfecho_sucede_a_apuracao_e_ela_nao_fica_obsoleta(cenario_do_77, gestor):
    """`FR-882`: a sucessora cita a anterior, e a anterior continua legível (`FR-883`)."""
    edital, _, _ = cenario_do_77
    antes = ApuracaoDeOcupacao.objects.get()
    convocada = titular_convocado(edital, gestor)

    resultado = desistir(edital, gestor, convocada["id"])

    assert resultado["apuracaoSeguinte"]["faltando"] == 1
    assert causas(edital) == []
    sucessora = ApuracaoDeOcupacao.objects.exclude(id=antes.id).get()
    assert sucessora.apuracao_anterior_id == antes.id
    antes.refresh_from_db()
    assert antes.ocupadas == 2, "a apuração de antes diz o que apurou"


def test_outra_causa_de_obsolescencia_nao_e_varrida(cenario_do_77, gestor):
    """`FR-884`: a apuração obsoleta por outra razão continua pedindo o ato da ocupação."""
    edital, _, _ = cenario_do_77
    convocada = titular_convocado(edital, gestor)
    outra = [
        {"causa": nomes_da_ocupacao.CAUSA_QUADRO_RETIFICADO},
        {"causa": nomes_da_ocupacao.CAUSA_EFEITO_POSTERIOR},
    ]

    with mock.patch.object(ocupacao_selectors, "causas_de_obsolescencia", return_value=outra):
        resultado = desistir(edital, gestor, convocada["id"])

    assert resultado["apuracaoSeguinte"] is None
    assert resultado["apuracaoPendente"]["codigo"] == nomes.OUTRA_CAUSA_DE_OBSOLESCENCIA
    assert ApuracaoDeOcupacao.objects.count() == 1
    assert nomes_da_ocupacao.CAUSA_EFEITO_POSTERIOR in causas(edital)


def test_a_conta_que_moveria_vaga_nao_e_gravada(cenario_do_77, gestor):
    """`FR-885`, `FR-270`: mover quantidade entre recortes continua sendo ato da ocupação."""
    edital, _, _ = cenario_do_77
    convocada = titular_convocado(edital, gestor)

    with mock.patch(
        "processo_seletivo.ocupacao.application.emissao.emitir_sucessora_por_efeito",
        return_value=None,
    ):
        resultado = desistir(edital, gestor, convocada["id"])

    assert resultado["apuracaoPendente"]["codigo"] == nomes.MOVERIA_VAGA
    assert MovimentoDeVaga.objects.count() == 0
    assert ApuracaoDeOcupacao.objects.count() == 1


def test_a_recusa_da_emissao_nao_desfaz_o_desfecho(cenario_do_77, gestor):
    """O desfecho é decisão sobre uma pessoa, e uma conta que não fecha não pode impedi-lo."""
    edital, _, _ = cenario_do_77
    convocada = titular_convocado(edital, gestor)
    recusa = DomainError(nomes.EMPATE_NA_FRONTEIRA_DO_ALVO, "Empate não julgado.", 409)

    with mock.patch(
        "processo_seletivo.ocupacao.application.emissao.emitir_sucessora_por_efeito",
        side_effect=recusa,
    ):
        resultado = desistir(edital, gestor, convocada["id"])

    assert resultado["apuracaoPendente"]["codigo"] == nomes.EMPATE_NA_FRONTEIRA_DO_ALVO
    assert DesfechoDaConvocacao.objects.count() == 1
    assert nomes_da_ocupacao.CAUSA_EFEITO_POSTERIOR in causas(edital)
