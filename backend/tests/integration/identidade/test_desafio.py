"""O ciclo do desafio: nasce, vale por dez minutos, serve uma vez, e morre de quatro maneiras."""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import (
    TETO_DE_TENTATIVAS,
    DesafioDeAcesso,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENDERECO = "maria@exemplo.test"
ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR


def solicitar(endereco=ENDERECO, finalidade=ENTRAR, origem="203.0.113.7"):
    return servico.solicitar(email_canonico=endereco, finalidade=finalidade, origem=origem)


def test_o_codigo_vale_uma_vez(_=None):
    _, codigo = solicitar()
    assert servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo=codigo)
    assert servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo=codigo) is None


def test_o_codigo_expira_por_instante_absoluto():
    _, codigo = solicitar()
    DesafioDeAcesso.objects.update(expira_em=timezone.now() - timedelta(seconds=1))
    assert servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo=codigo) is None


def test_um_codigo_novo_invalida_o_anterior():
    _, primeiro = solicitar()
    DesafioDeAcesso.objects.update(criado_em=timezone.now() - timedelta(minutes=5))
    _, segundo = solicitar()
    assert servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo=primeiro) is None
    assert servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo=segundo)


def test_o_teto_de_tentativas_mata_o_desafio():
    _, codigo = solicitar()
    for _tentativa in range(TETO_DE_TENTATIVAS):
        assert servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo="000000") is None
    # Mesmo o código certo, depois do teto: o desafio já morreu.
    assert servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo=codigo) is None


def test_o_resumo_do_codigo_nao_carrega_o_codigo():
    _, codigo = solicitar()
    assert codigo not in DesafioDeAcesso.objects.get().codigo_hash


def test_a_origem_e_guardada_como_resumo():
    """A contagem por origem precisa distinguir, não precisa saber de onde veio (D-005)."""
    solicitar(origem="203.0.113.7")
    guardado = DesafioDeAcesso.objects.get().origem_hash
    assert "203.0.113.7" not in guardado
    assert len(guardado) == 64
