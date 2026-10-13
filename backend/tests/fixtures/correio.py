"""Servidores de correio simulados para o despacho dos avisos (066, US5, `R-004`).

**Nenhum deles alcança a rede** (`FR-1281`). São backends do Django, configurados por
`settings.EMAIL_BACKEND` como o de memória que a suíte já usa — e é por isso que o despacho os
alcança: ele abre a conexão por `get_connection()`, nunca por conta própria.

**O comportamento é escolhido pelo caso**, por `Roteiro`, uma lista de respostas que o servidor dá
mensagem a mensagem. Cada resposta é um número de mensagens aceitas (`1`, `0`) ou uma exceção a
levantar. A mensagem aceita vai para `mail.outbox`, como no backend de memória.
"""

import smtplib

from django.core import mail
from django.core.mail.backends.locmem import EmailBackend as Memoria

CAMINHO = "tests.fixtures.correio"


class Roteiro:
    """O que o servidor simulado responde, em ordem; esgotado, aceita."""

    respostas = []
    ao_enviar = None
    abertura = None

    @classmethod
    def definir(cls, *respostas, ao_enviar=None, abertura=None):
        cls.respostas = list(respostas)
        cls.ao_enviar = ao_enviar
        cls.abertura = abertura

    @classmethod
    def proxima(cls):
        return cls.respostas.pop(0) if cls.respostas else 1


class Simulado(Memoria):
    """O backend de memória do Django, com as respostas do `Roteiro`."""

    def open(self):
        if Roteiro.abertura is not None:
            raise Roteiro.abertura
        return super().open()

    def send_messages(self, mensagens):
        if Roteiro.ao_enviar is not None:
            Roteiro.ao_enviar(mensagens)
        resposta = Roteiro.proxima()
        if isinstance(resposta, BaseException):
            if getattr(resposta, "_saiu_antes", False):
                # "Aceita e derruba": o conteúdo chegou à caixa, e a conexão caiu antes da resposta
                # final — o caso em que reenviar entregaria duas vezes.
                mail.outbox.extend(mensagens)
            raise resposta
        if resposta == 0:
            return 0
        return super().send_messages(mensagens)


def aceita_e_derruba():
    erro = smtplib.SMTPServerDisconnected("Connection unexpectedly closed")
    erro._saiu_antes = True
    return erro


def recusa(codigo, *, fase="rcpt", endereco="pessoa@exemplo.test"):
    if fase == "rcpt":
        return smtplib.SMTPRecipientsRefused({endereco: (codigo, b"refused")})
    if fase == "mail":
        return smtplib.SMTPSenderRefused(codigo, b"refused", "nao-responda@exemplo.test")
    return smtplib.SMTPDataError(codigo, b"refused")


def usar(settings, *respostas, ao_enviar=None, abertura=None):
    """Liga o servidor simulado no caso, com o roteiro dado."""
    settings.EMAIL_BACKEND = f"{CAMINHO}.Simulado"
    Roteiro.definir(*respostas, ao_enviar=ao_enviar, abertura=abertura)
    mail.outbox.clear()
