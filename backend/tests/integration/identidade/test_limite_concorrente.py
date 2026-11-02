"""A sala inteira clica junto — e cada pessoa recebe ou um código, ou a explicação certa (FR-031c).

O teto por origem é conferido antes de gravar, sem trava: pedidos simultâneos na borda podem passar
dele em alguns, um por processo que os atende ao mesmo tempo. É risco conhecido e pequeno — o
excesso é limitado pela concorrência do servidor, e não pelo atacante —, e não é o que o achado A-12
corrige. O que estes casos guardam é que o excesso não estraga a resposta: ninguém fica sem código e
sem explicação, e o tempo anunciado depois da rajada continua sendo o efetivo, contando inclusive
os pedidos que passaram.
"""

import threading

import pytest
from django.db import connection, connections

from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import DesafioDeAcesso
from tests.conftest import encerrar_conexoes_da_thread

# Mesma razão de `test_teto_concorrente`: em SQLite os escritores simultâneos se atropelam, e a
# corrida que o teste investiga não chega a acontecer.
pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.integration,
    pytest.mark.skipif(
        connection.vendor != "postgresql", reason="a corrida exige as travas do PostgreSQL"
    ),
]

ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR
POLO = "203.0.113.50"
SIMULTANEAS = 8


def em_paralelo(tarefas):
    barreira = threading.Barrier(len(tarefas))
    resultados = []

    def correr(tarefa):
        try:
            barreira.wait()
            resultados.append(tarefa())
        finally:
            encerrar_conexoes_da_thread()

    fios = [threading.Thread(target=correr, args=(tarefa,)) for tarefa in tarefas]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join()
    connections.close_all()
    return resultados


def pedido(endereco):
    return lambda: servico.solicitar(email_canonico=endereco, finalidade=ENTRAR, origem=POLO)


def test_na_borda_do_teto_cada_um_recebe_codigo_ou_a_explicacao():
    for indice in range(servico.LIMITE_POR_ORIGEM - 2):
        servico.solicitar(
            email_canonico=f"sala{indice}@exemplo.test", finalidade=ENTRAR, origem=POLO
        )

    resultados = em_paralelo(
        [pedido(f"junto{indice}@exemplo.test") for indice in range(SIMULTANEAS)]
    )

    enviados = [recibo for recibo, codigo in resultados if codigo]
    recusados = [recibo for recibo, codigo in resultados if not codigo]
    assert len(enviados) + len(recusados) == SIMULTANEAS
    assert len(enviados) >= 2, "as duas vagas que restavam foram usadas"
    for recibo in enviados:
        assert recibo.bloqueio is None
    for recibo in recusados:
        assert recibo.bloqueio.motivo == servico.TETO_DA_ORIGEM
        assert recibo.proxima_tentativa_em > 60, "nunca a espera fictícia de um minuto"
    # O excesso existe e é limitado pelo que chegou junto — registrado aqui para que crescer
    # apareça.
    assert DesafioDeAcesso.objects.count() <= servico.LIMITE_POR_ORIGEM - 2 + SIMULTANEAS


def test_depois_da_rajada_o_tempo_conta_os_pedidos_que_passaram():
    """Com o teto ultrapassado, liberar exige que saiam da janela também os excedentes."""
    for indice in range(servico.LIMITE_POR_ORIGEM - 1):
        servico.solicitar(
            email_canonico=f"sala{indice}@exemplo.test", finalidade=ENTRAR, origem=POLO
        )
    em_paralelo([pedido(f"junto{indice}@exemplo.test") for indice in range(SIMULTANEAS)])

    recibo, codigo = servico.solicitar(
        email_canonico="depois@exemplo.test", finalidade=ENTRAR, origem=POLO
    )

    assert not codigo
    assert recibo.bloqueio.motivo == servico.TETO_DA_ORIGEM
    assert 0 < recibo.proxima_tentativa_em <= 3600
