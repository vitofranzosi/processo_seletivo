"""O mesmo código, duas requisições ao mesmo tempo, um único consumo (FR-025, SC-003).

Não é hipótese de laboratório: é a pessoa com duas abas abertas, ou o clique duplo num botão de
celular lento. Ler-verificar-gravar deixaria as duas passarem, e a segunda entraria com um código
que já tinha sido usado — que é exatamente o que "uso único" promete não acontecer.
"""

import pytest
from django.db import connections

from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import DesafioDeAcesso
from tests.conftest import encerrar_conexoes_da_thread

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

ENDERECO = "maria@exemplo.test"
ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR


def test_duas_requisicoes_simultaneas_consomem_uma_vez():
    import threading

    _, codigo = servico.solicitar(email_canonico=ENDERECO, finalidade=ENTRAR)
    resultados = []
    barreira = threading.Barrier(2)

    def validar():
        try:
            barreira.wait()
            resultados.append(
                servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo=codigo)
            )
        finally:
            encerrar_conexoes_da_thread()

    fios = [threading.Thread(target=validar) for _ in range(2)]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join()

    connections.close_all()
    aceitos = [resultado for resultado in resultados if resultado is not None]
    assert len(aceitos) == 1, "o código foi aproveitado mais de uma vez"
    assert DesafioDeAcesso.objects.get().consumido_em is not None
