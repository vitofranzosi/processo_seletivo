"""Um desafio vale para um endereço **e uma finalidade** (FR-028).

Sem isso, o código pedido para entrar confirmaria a adição de uma credencial — e alguém induzido a
pedir um código "para entrar" estaria, sem saber, autorizando a ligação de um endereço alheio à
sua identidade. São dois atos distintos, e cada um pede a sua prova.
"""

import pytest

from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import DesafioDeAcesso

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENDERECO = "maria@exemplo.test"
ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR
ADICIONAR = DesafioDeAcesso.Finalidade.ADICIONAR_CREDENCIAL


def test_codigo_de_entrar_nao_confirma_credencial():
    _, codigo = servico.solicitar(email_canonico=ENDERECO, finalidade=ENTRAR)
    assert servico.validar(email_canonico=ENDERECO, finalidade=ADICIONAR, codigo=codigo) is None


def test_codigo_de_adicionar_nao_autentica():
    _, codigo = servico.solicitar(email_canonico=ENDERECO, finalidade=ADICIONAR)
    assert servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo=codigo) is None


def test_cada_finalidade_valida_a_sua():
    _, entrar = servico.solicitar(email_canonico=ENDERECO, finalidade=ENTRAR)
    assert servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo=entrar)


def test_o_endereco_tambem_delimita():
    _, codigo = servico.solicitar(email_canonico=ENDERECO, finalidade=ENTRAR)
    de_outro = servico.validar(
        email_canonico="outro@exemplo.test", finalidade=ENTRAR, codigo=codigo
    )
    assert de_outro is None
