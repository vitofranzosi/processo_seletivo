"""Do acréscimo à convocação: o cadastro de reserva do TMD chamado pelo sistema (097).

**É o teste que prova que a feature faz o que ela existe para fazer.** Até a `097`, o Edital de
remanescentes publicava, sorteava e divulgava, e a primeira chamada era recusada com `sem_deficit`:
a convocação era feita fora do sistema, e a Revisão avisava disso. Aqui a mesma chamada acontece por
dois atos — o acréscimo e a convocação —, e nada do que vem depois dela muda.
"""

import pytest

from processo_seletivo.convocacao.application import fluxo, selectors
from processo_seletivo.convocacao.application.desfechar import desfechar as registrar_desfecho
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.ocupacao.application import selectors as ocupacao_selectors
from processo_seletivo.ocupacao.application.acrescimo import acrescentar_vagas, previa_do_acrescimo
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.convocacao import convocar
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)

ORIGEM = "Edital Multicampi nº 20/2026, Campus Vitória"
FUNDAMENTO = "Vaga não preenchida no Edital regular"


def acrescentar(edital, gestor, quantidade=1, *, chave="097-acrescentar"):
    leitura = previa_do_acrescimo(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, quantidade=quantidade
    )["assinatura"]
    return acrescentar_vagas(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        quantidade=quantidade,
        origem=ORIGEM,
        fundamento=FUNDAMENTO,
        leitura_confirmada=leitura,
        idempotency_key=chave,
        correlation_id="teste-097",
    )


def fila(edital):
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]


def desfechar(edital, gestor, convocacao_id, especie, chave):
    return registrar_desfecho(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao_id,
        especie=especie,
        fundamento="Manifestação da pessoa convocada, registrada em processo.",
        idempotency_key=chave,
        correlation_id="teste-097",
    )


def test_sem_acrescimo_a_chamada_continua_recusada(cenario_reserva, gestor):
    """O ponto de partida da `DP-05`: 0 vagas, e a recusa que dizia "convocação fora do sistema"."""
    edital, _, _ = cenario_reserva
    primeiro = fila(edital)[0]

    with pytest.raises(DomainError) as recusa:
        convocar(edital, gestor, primeiro, idempotency_key="097-antes")

    assert recusa.value.code == nomes.SEM_DEFICIT
    assert Convocacao.objects.count() == 0


def test_a_vaga_acrescida_faz_do_primeiro_da_ordem_um_titular_chamavel(cenario_reserva, gestor):
    """`FR-2455` e `SC-921`: o acréscimo e a convocação, e nenhuma apuração à mão entre os dois."""
    edital, _, _ = cenario_reserva
    primeiro = fila(edital)[0]
    apuracoes = ApuracaoDeOcupacao.objects.count()

    acrescentar(edital, gestor)

    assert ApuracaoDeOcupacao.objects.count() == apuracoes + 1, "a seguinte saiu do próprio ato"
    titulares = fluxo.previa_dos_titulares(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    assert [p["id"] for p in titulares["pessoas"]] == [primeiro]
    convocada = convocar(edital, gestor, primeiro, idempotency_key="097-titular")
    assert Convocacao.objects.get(id=convocada["id"]).especie == nomes.VAGA_INICIAL


def test_o_desfecho_devolve_a_vaga_e_o_seguinte_e_chamado_sem_novo_acrescimo(
    cenario_reserva, gestor
):
    """Acceptance 4 da US1: depois do acréscimo, o certame é o de um Edital com vaga publicada."""
    edital, _, _ = cenario_reserva
    primeiro, segundo = fila(edital)[:2]
    acrescentar(edital, gestor)
    convocada = convocar(edital, gestor, primeiro, idempotency_key="097-titular")

    desfechar(edital, gestor, convocada["id"], nomes.DESISTENCIA_EXPRESSA, "097-desiste")

    leitura = ocupacao_selectors.ocupacao_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO
    )
    assert (leitura["efetivas"], leitura["ocupadas"], leitura["faltando"]) == (1, 0, 1)
    assert fila(edital)[0] == segundo
    suplente = convocar(
        edital, gestor, segundo, especie=nomes.SUPLENCIA, idempotency_key="097-suplente"
    )
    assert Convocacao.objects.get(id=suplente["id"]).especie == nomes.SUPLENCIA


def test_o_fundamento_da_convocacao_nao_carrega_a_origem_do_acrescimo(cenario_reserva, gestor):
    """`FR-2467`: o convocado lê no portal a apuração que registrou a vaga, e não a origem dela.

    O fundamento derivado é o que o gesto dos titulares grava (050, `D-009`), e a prévia o mostra
    com o mesmo texto: a função é pura, e a prévia e o ato a chamam com os mesmos argumentos.
    """
    edital, _, _ = cenario_reserva
    acrescentar(edital, gestor)

    texto = fluxo.previa_dos_titulares(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)[
        "fundamento"
    ]

    assert "apuração de ocupação" in texto
    assert ORIGEM not in texto
    assert FUNDAMENTO not in texto


# --- A trava do desfazimento (US3) -------------------------------------------------------------


def pessoas(edital):
    return selectors.pessoas_chamadas(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)


def test_pessoas_chamadas_conta_quem_espera_e_quem_atendeu(cenario_reserva, gestor):
    """Em aberto e atendida contam; quem encerrou não espera a vaga, e não conta."""
    edital, _, _ = cenario_reserva
    primeiro, segundo = fila(edital)[:2]
    acrescentar(edital, gestor, 2)
    assert pessoas(edital) == 0

    um = convocar(edital, gestor, primeiro, idempotency_key="097-p1")
    dois = convocar(edital, gestor, segundo, idempotency_key="097-p2")
    assert pessoas(edital) == 2

    desfechar(edital, gestor, um["id"], nomes.ACEITE, "097-aceite")
    assert pessoas(edital) == 2, "atendida continua contando"

    desfechar(edital, gestor, dois["id"], nomes.DESISTENCIA_EXPRESSA, "097-desiste")
    assert pessoas(edital) == 1, "quem encerrou não espera a vaga"


def test_desfazer_a_vaga_de_quem_foi_chamado_e_recusado_pela_trava_real(cenario_reserva, gestor):
    """Acceptance 2 da US3, com o seletor da convocação, e não com dublê."""
    from processo_seletivo.ocupacao.application.acrescimo import (
        desfazer_acrescimo,
        previa_do_desfazimento,
    )
    from processo_seletivo.ocupacao.domain import nomes as nomes_da_ocupacao
    from processo_seletivo.ocupacao.models import AcrescimoDeVagas

    edital, _, _ = cenario_reserva
    acrescentar(edital, gestor)
    convocar(edital, gestor, fila(edital)[0], idempotency_key="097-chamado")
    acrescimo = AcrescimoDeVagas.objects.get()
    leitura = previa_do_desfazimento(
        edital=edital,
        acrescimo_id=acrescimo.id,
        quantidade=1,
        pessoas_chamadas=selectors.pessoas_chamadas,
    )

    assert leitura["recusa"] == nomes_da_ocupacao.DESFAZIMENTO_COM_PESSOAS_CHAMADAS
    with pytest.raises(DomainError) as recusa:
        desfazer_acrescimo(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            acrescimo_id=acrescimo.id,
            quantidade=1,
            motivo="Engano",
            pessoas_chamadas=selectors.pessoas_chamadas,
            leitura_confirmada=leitura["assinatura"],
            idempotency_key="097-desfaz-chamado",
            correlation_id="teste-097",
        )

    assert recusa.value.code == nomes_da_ocupacao.DESFAZIMENTO_COM_PESSOAS_CHAMADAS
    assert AcrescimoDeVagas.objects.count() == 1
