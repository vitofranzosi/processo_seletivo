"""O teto de tentativas resiste a requisições simultâneas — regressão de um defeito real.

A primeira versão incrementava o contador **depois** de conferir o código, filtrando apenas pelo
identificador da linha. Dez requisições simultâneas liam `tentativas = 0`, todas erravam, todas
incrementavam: o contador terminava em dez e as dez tinham sido avaliadas. O teto existia no texto
e não no banco — e o custo disso é direto, porque seis dígitos são um milhão de possibilidades e o
que as protege é justamente não poder tentar mais que cinco vezes.

A correção é reservar a tentativa **antes** de conferir. Quem não consegue a reserva não chega a
conferir nada.
"""

import threading

import pytest
from django.db import connections

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import TETO_DE_TENTATIVAS, DesafioDeAcesso
from tests.conftest import encerrar_conexoes_da_thread

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

ENDERECO = "maria@exemplo.test"
ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR
SIMULTANEAS = 12


def em_paralelo(tarefa, quantidade=SIMULTANEAS):
    """Todas as chamadas soltas no mesmo instante, e não uma depois da outra."""
    barreira = threading.Barrier(quantidade)
    resultados = []

    def correr():
        try:
            barreira.wait()
            resultados.append(tarefa())
        finally:
            encerrar_conexoes_da_thread()

    fios = [threading.Thread(target=correr) for _ in range(quantidade)]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join()
    connections.close_all()
    return resultados


def test_o_teto_do_codigo_nao_e_ultrapassado_por_concorrencia():
    servico.solicitar(email_canonico=ENDERECO, finalidade=ENTRAR)

    resultados = em_paralelo(
        lambda: servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo="000000")
    )

    assert all(resultado is None for resultado in resultados)
    assert DesafioDeAcesso.objects.get().tentativas_codigo == TETO_DE_TENTATIVAS


def test_o_codigo_certo_nao_passa_depois_do_teto_disputado():
    _, codigo = servico.solicitar(email_canonico=ENDERECO, finalidade=ENTRAR)
    em_paralelo(
        lambda: servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo="000000")
    )

    assert servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo=codigo) is None


def test_o_teto_do_cpf_nao_e_ultrapassado_por_concorrencia():
    """Mesmo defeito, mesmo remédio: a contagem lia o valor anterior e gravava `lido + 1`."""
    _, codigo = servico.solicitar(email_canonico=ENDERECO, finalidade=ENTRAR)
    desafio = servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo=codigo)
    alvo = associacao.criar_identidade_com("historico@exemplo.test", "historico@exemplo.test")
    associacao.abrir_reconciliacao(desafio, [alvo])

    def tentar():
        atual = DesafioDeAcesso.objects.get(pk=desafio.pk)
        return associacao.confirmar_cpf(atual, "111.111.111-11")

    resultados = em_paralelo(tentar)

    assert all(resultado is None for resultado in resultados)
    assert DesafioDeAcesso.objects.get(pk=desafio.pk).tentativas_cpf == TETO_DE_TENTATIVAS
