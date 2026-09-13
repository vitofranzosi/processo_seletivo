"""O reclassificado volta a ser chamável — e a chamada nova passa pela fila (019, `US4`).

**O beco que este arquivo prende.** O reclassificado vai para o fim da fila, chega a vez dele, e a
chamada precisa acontecer. Bloquear por "já tem convocação vigente" a tornava impossível; oferecer
a sucessão como saída era pior, porque sucessão pula as guardas de ordem — a única forma de chamá-lo
furaria a fila.

O que separa os dois casos é o **desfecho**: chamada sem desfecho está aguardando resposta, e a
segunda seria uma duplicata; chamada com desfecho está concluída, e a segunda é uma chamada nova.
"""

import pytest

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.convocacao import apurar, convocar
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)


def contexto(edital):
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )


def responder(edital, gestor, convocacao_id, especie, chave):
    return desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao_id,
        especie=especie,
        fundamento="Não compareceu à chamada do item 7.2 do Edital 69/2026.",
        idempotency_key=chave,
        correlation_id="teste-convocacao-019",
    )


def test_o_reclassificado_e_chamavel_de_novo_sem_motivo_de_sucessao(cenario_do_77, gestor):
    """A chamada nova é uma chamada, e não a correção da anterior.

    O percurso é o que o 69/2026 descreve: a titular não comparece e é reclassificada; a suplente é
    chamada para a vaga e desiste; esgotada a lista, a reclassificada volta a ser chamável — e a
    convocação dela nasce **raiz**, sem sucessão, porque nada está sendo corrigido.
    """
    edital, _, _ = cenario_do_77
    inicio = contexto(edital)["fila"]
    reclassificada, titular, suplente = inicio[0], inicio[1], inicio[2]
    primeira = convocar(edital, gestor, reclassificada, idempotency_key="rc-1")
    responder(edital, gestor, primeira["id"], nomes.RECLASSIFICACAO, "rc-1-desfecho")
    # **A reclassificação exclui, e a apuração fica obsoleta**: emitir a seguinte é o passo que o
    # próprio sistema exige antes de qualquer chamada nova (`FR-266`).
    apurar(edital, gestor, chave="rc-apura-1", motivo="Reclassificação registrada")
    convocar(edital, gestor, titular, idempotency_key="rc-titular")
    chamada = convocar(
        edital, gestor, suplente, especie=nomes.SUPLENCIA, idempotency_key="rc-suplente"
    )
    responder(edital, gestor, chamada["id"], nomes.DESISTENCIA_EXPRESSA, "rc-suplente-desiste")
    apurar(edital, gestor, chave="rc-apura-2", motivo="Desistência da suplente")

    assert contexto(edital)["fila"] == [reclassificada], "esgotada a lista, ela é a próxima"

    segunda = convocar(edital, gestor, reclassificada, idempotency_key="rc-2")

    assert segunda["sucede"] is None, "é chamada nova, e não sucessora"
    assert Convocacao.objects.filter(inscricao_id=reclassificada, edital=edital).count() == 2


def test_a_chamada_aguardando_desfecho_continua_bloqueando(cenario_do_77, gestor):
    """A metade que a recusa existe para proteger: duas chamadas em aberto para a mesma pessoa."""
    edital, _, _ = cenario_do_77
    alguem = contexto(edital)["fila"][0]
    convocar(edital, gestor, alguem, idempotency_key="rc-aberta")

    with pytest.raises(DomainError) as erro:
        convocar(edital, gestor, alguem, idempotency_key="rc-duplicata")

    assert erro.value.code == nomes.CONVOCACAO_VIGENTE_EXISTENTE


def test_o_reclassificado_ainda_nao_fura_a_fila(cenario_do_77, gestor):
    """`reclassificado_antes_do_esgotamento` continua valendo para a chamada nova.

    **É a garantia que a saída pela sucessão destruía**: chamada nova passa pelas guardas de ordem;
    sucessão não passa, porque corrige um ato já praticado.
    """
    edital, _, _ = cenario_do_77
    inicio = contexto(edital)["fila"]
    reclassificado = inicio[0]
    primeira = convocar(edital, gestor, reclassificado, idempotency_key="rf-1")
    responder(edital, gestor, primeira["id"], nomes.RECLASSIFICACAO, "rf-1-desfecho")
    apurar(edital, gestor, chave="rf-apura", motivo="Reclassificação registrada")

    with pytest.raises(DomainError) as erro:
        convocar(edital, gestor, reclassificado, idempotency_key="rf-2")

    assert erro.value.code == nomes.RECLASSIFICADO_ANTES_DO_ESGOTAMENTO
