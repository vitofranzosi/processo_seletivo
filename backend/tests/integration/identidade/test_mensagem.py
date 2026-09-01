"""O que a mensagem carrega — e, sobretudo, o que ela não carrega (FR-082).

Ela vai para uma caixa que ainda não se sabe de quem é: é justamente o que está sendo descoberto.
Por isso não leva CPF, não leva dado de inscrição e não leva link que autentica — um link assim
viaja no histórico do navegador, no encaminhamento da mensagem e no cabeçalho de origem.
"""

import pytest
from django.core import mail

from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.application.mensagem import enviar_codigo
from processo_seletivo.identidade.models import VALIDADE_EM_MINUTOS, DesafioDeAcesso

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENDERECO = "maria@exemplo.test"


@pytest.fixture
def enviada(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    _, codigo = servico.solicitar(
        email_canonico=ENDERECO, finalidade=DesafioDeAcesso.Finalidade.ENTRAR
    )
    enviar_codigo(para=ENDERECO, codigo=codigo)
    return mail.outbox[0], codigo


def test_leva_o_codigo(enviada):
    mensagem, codigo = enviada
    assert codigo in mensagem.body


def test_diz_por_quanto_tempo_vale(enviada):
    mensagem, _ = enviada
    assert str(VALIDADE_EM_MINUTOS) in mensagem.body


def test_orienta_a_ignorar_quem_nao_pediu(enviada):
    mensagem, _ = enviada
    assert "ignore" in mensagem.body.lower()


def test_nao_leva_link_que_autentica(enviada):
    """O código é digitado. Um link que entra sozinho viaja para onde ninguém controla (P-001)."""
    mensagem, _ = enviada
    assert "http://" not in mensagem.body and "https://" not in mensagem.body


def test_nao_leva_cpf_nem_dado_de_inscricao(enviada):
    mensagem, _ = enviada
    proibidos = ("cpf", "protocolo", "inscrição", "inscricao")
    for termo in proibidos:
        assert termo not in mensagem.body.lower(), termo


def test_falha_de_envio_nao_estoura(settings, monkeypatch):
    """Quem está do outro lado não pode descobrir nada pela falha (FR-083)."""
    from processo_seletivo.identidade.application import mensagem as modulo

    def explodir(*_args, **_kwargs):
        raise OSError("indisponível")

    monkeypatch.setattr(modulo, "send_mail", explodir)
    enviar_codigo(para=ENDERECO, codigo="123456")
