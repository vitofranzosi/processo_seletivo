"""O ciclo do 77/2026, do começo ao fim: chamar, responder, e o número se mover (019, `SC-085`).

**É o teste que prova que a feature faz o que ela existe para fazer.** Hoje isso mora numa planilha
paralela: alguém anota quem foi chamado, quem aceitou e quem desistiu, e recalcula à mão quantas
vagas sobraram. O que este arquivo percorre é o mesmo trabalho, feito por atos registrados.

**E é onde a correção da `§1.0` fica visível.** Com o cálculo antigo — `min(|faixa ∩ habilitadas|,
efetivas)` — o número saturava no alvo: a desistência acontecia, a planilha mudava, e a apuração
continuava dizendo duas ocupadas de duas. A suplente era promovida em silêncio, e nenhum ato do
sistema registrava a vaga que vagou.
"""

import pytest

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.desfechar import desfechar as registrar_desfecho
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.ocupacao.application import selectors as ocupacao_selectors
from processo_seletivo.ocupacao.domain import nomes as nomes_da_ocupacao
from tests.fixtures.convocacao import apurar, convocar
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)


def contexto(edital):
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )


def numeros(edital):
    leitura = ocupacao_selectors.ocupacao_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    return leitura["efetivas"], leitura["ocupadas"], leitura["faltando"]


def desfechar(edital, gestor, convocacao_id, especie, chave, **kwargs):
    return registrar_desfecho(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao_id,
        especie=especie,
        fundamento="Manifestação da pessoa convocada, registrada em processo.",
        idempotency_key=chave,
        correlation_id="teste-convocacao-019",
        **kwargs,
    )


def test_o_ciclo_inteiro_do_77(cenario_do_77, gestor):
    """Duas vagas, dois titulares, uma suplente — e a desistência que a promove (`SC-085`).

    Cada linha abaixo é um ato registrado, e o número entre elas é o que a `016` apura. **Nenhuma
    apuração é reescrita**: o desfecho torna a vigente obsoleta, e o número novo sai na emissão
    seguinte (`D-006`).
    """
    edital, _, _ = cenario_do_77
    inicio = contexto(edital)
    titulares = list(inicio["fila"][:2])
    suplente = inicio["fila"][2]

    assert numeros(edital) == (2, 2, 0), "os dois titulares ocupam as duas vagas publicadas"
    assert len(inicio["fila"]) == 3, "ninguém foi chamado ainda — os três são chamáveis"

    # 1. Os dois titulares são convocados. `faltando` é zero, e é assim que todo certame começa:
    #    a vaga deles já é deles, e a chamada é o ato que a formaliza.
    primeira = convocar(edital, gestor, titulares[0], idempotency_key="77-titular-1")
    segunda = convocar(edital, gestor, titulares[1], idempotency_key="77-titular-2")

    assert numeros(edital) == (2, 2, 0), "convocar não move número nenhum"

    # 2. A primeira aceita. A inclusão é registrada, e o número **não muda**: ela já ocupava.
    desfechar(edital, gestor, primeira["id"], nomes.ACEITE, "77-aceite-1")
    apurar(edital, gestor, chave="77-apura-2", motivo="Aceite registrado")

    assert numeros(edital) == (2, 2, 0)

    # 3. A segunda desiste. **Aqui o número antigo não se movia** — e é a vaga que vagou.
    desfechar(edital, gestor, segunda["id"], nomes.DESISTENCIA_EXPRESSA, "77-desiste-2")

    assert nomes_da_ocupacao.CAUSA_EFEITO_POSTERIOR in [
        c["causa"]
        for c in ocupacao_selectors.causas_de_obsolescencia(
            ocupacao_selectors.apuracao_vigente(
                edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
            )
        )
    ], "a apuração vigente passa a aparecer obsoleta, e não é reescrita"

    apurar(edital, gestor, chave="77-apura-3", motivo="Desistência registrada")

    assert numeros(edital) == (2, 1, 1), "uma desistência, uma vaga a menos ocupada"

    # 4. A suplente é chamada para a vaga que vagou, e aceita.
    depois = contexto(edital)
    assert depois["fila"][0] == suplente, "a suplente é a próxima, e ninguém a precede"

    terceira = convocar(
        edital, gestor, suplente, especie=nomes.SUPLENCIA, idempotency_key="77-suplente"
    )
    desfechar(edital, gestor, terceira["id"], nomes.ACEITE, "77-aceite-3")
    apurar(edital, gestor, chave="77-apura-4", motivo="Aceite da suplente")

    assert numeros(edital) == (2, 2, 0), "o aceite da suplente devolve o número"


def test_a_desistencia_registrada_nao_reescreve_a_apuracao_anterior(cenario_do_77, gestor):
    """**Preservação** (Princípio II): o número de ontem continua sendo o que foi apurado ontem.

    A apuração é ato imutável. O que a desistência faz é torná-la obsoleta — e o histórico continua
    dizendo `2 ocupadas` no dia em que foram duas, porque naquele dia eram.
    """
    edital, _, _ = cenario_do_77
    titular = contexto(edital)["fila"][0]
    antes = ocupacao_selectors.apuracao_vigente(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    convocada = convocar(edital, gestor, titular, idempotency_key="preserva-convoca")

    desfechar(edital, gestor, convocada["id"], nomes.DESISTENCIA_EXPRESSA, "preserva-desiste")
    apurar(edital, gestor, chave="preserva-apura", motivo="Desistência registrada")

    antes.refresh_from_db()
    assert antes.ocupadas == 2, "a apuração de ontem continua dizendo o que apurou"
    assert numeros(edital) == (2, 1, 1), "e a de hoje diz o de hoje"


def test_o_desfecho_nao_se_repete_e_a_correcao_e_sucessao(cenario_do_77, gestor):
    """`FR-273`: um desfecho por convocação, e a segunda resposta é recusada.

    Duas respostas contraditórias sobre a mesma vaga deixariam o sistema sem como dizer qual vale.
    """
    from processo_seletivo.shared.api.problems import DomainError

    edital, _, _ = cenario_do_77
    titular = contexto(edital)["fila"][0]
    convocada = convocar(edital, gestor, titular, idempotency_key="repete-convoca")
    desfechar(edital, gestor, convocada["id"], nomes.ACEITE, "repete-aceite")

    with pytest.raises(DomainError) as erro:
        desfechar(edital, gestor, convocada["id"], nomes.DESISTENCIA_EXPRESSA, "repete-desiste")

    assert erro.value.code == nomes.DESFECHO_JA_REGISTRADO


def test_a_inercia_sem_atestado_e_recusada(cenario_do_77, gestor):
    """`FR-277`, `atestado_obrigatorio`: fato externo sem atestante não entra.

    O cancelamento por inércia decide a vaga de alguém, e *"o prazo venceu"* não é uma pessoa
    responsável — a `D-004` exige que alguém competente tenha concluído.
    """
    from processo_seletivo.shared.api.problems import DomainError

    edital, _, _ = cenario_do_77
    titular = contexto(edital)["fila"][0]
    convocada = convocar(edital, gestor, titular, idempotency_key="inercia-convoca")

    with pytest.raises(DomainError) as erro:
        desfechar(edital, gestor, convocada["id"], nomes.INERCIA, "inercia-sem-atestado")

    assert erro.value.code == nomes.ATESTADO_OBRIGATORIO


def test_a_exclusao_de_quem_nao_era_titular_nao_desconta_nada(cenario_do_77, gestor):
    """`FR-278d`: a suplente só entra na contagem depois de aceitar.

    Chamada porque uma vaga vagou, e desistindo **antes de aceitar**, ela nunca ocupou nada — e o
    número não pode cair de novo por causa disso. É o `−2` que uma subtração cega produziria a
    partir de duas exclusões, e que o conjunto evita: a vaga continua faltando **uma**, e não duas.
    """
    edital, _, _ = cenario_do_77
    inicio = contexto(edital)
    titulares, suplente = list(inicio["fila"][:2]), inicio["fila"][2]
    convocar(edital, gestor, titulares[0], idempotency_key="d278-t1")
    segunda = convocar(edital, gestor, titulares[1], idempotency_key="d278-t2")
    desfechar(edital, gestor, segunda["id"], nomes.DESISTENCIA_EXPRESSA, "d278-t2-desiste")
    apurar(edital, gestor, chave="d278-apura-1", motivo="Desistência do titular")

    assert numeros(edital) == (2, 1, 1), "a vaga do titular vagou"

    chamada = convocar(
        edital, gestor, suplente, especie=nomes.SUPLENCIA, idempotency_key="d278-suplente"
    )
    desfechar(edital, gestor, chamada["id"], nomes.DESISTENCIA_EXPRESSA, "d278-suplente-desiste")
    apurar(edital, gestor, chave="d278-apura-2", motivo="Desistência da suplente")

    assert numeros(edital) == (2, 1, 1), "a suplente não ocupava nada: a vaga continua sendo uma"
