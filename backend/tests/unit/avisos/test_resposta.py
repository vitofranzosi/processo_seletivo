"""A resposta do servidor de correio, classificada pela fase em que veio (`R-004`, `FR-1269`).

**Um caso por linha da tabela de `R-004`.** O que se prende é a assimetria que o usuário exigiu: só
a resposta lida a um comando da mensagem classifica; queda, timeout, resposta ilegível e código fora
de 400–599 são indeterminados, e param a execução.
"""

import smtplib
import socket

import pytest

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.domain.resposta import do_envio, na_preparacao

ENDERECO = "pessoa@exemplo.test"


def test_aceita():
    assert do_envio(enviadas=1).resultado == nomes.ACEITA


def test_zero_nao_e_sucesso():
    classificacao = do_envio(enviadas=0)

    assert classificacao.resultado == nomes.FALHA_TEMPORARIA
    assert not classificacao.para_a_execucao


@pytest.mark.parametrize(
    ("erro", "esperado"),
    [
        (smtplib.SMTPSenderRefused(451, b"try later", "nao-responda@x"), nomes.FALHA_TEMPORARIA),
        (smtplib.SMTPSenderRefused(550, b"denied", "nao-responda@x"), nomes.FALHA_DEFINITIVA),
        (smtplib.SMTPRecipientsRefused({ENDERECO: (452, b"full")}), nomes.FALHA_TEMPORARIA),
        (smtplib.SMTPRecipientsRefused({ENDERECO: (550, b"no such user")}), nomes.FALHA_DEFINITIVA),
        (smtplib.SMTPDataError(451, b"queue full"), nomes.FALHA_TEMPORARIA),
        (smtplib.SMTPDataError(554, b"rejected"), nomes.FALHA_DEFINITIVA),
    ],
    ids=["mail-4xx", "mail-5xx", "rcpt-4xx", "rcpt-5xx", "data-4xx", "data-5xx"],
)
def test_resposta_lida_classifica_pelo_codigo(erro, esperado):
    classificacao = do_envio(erro=erro)

    assert classificacao.resultado == esperado
    assert not classificacao.para_a_execucao


@pytest.mark.parametrize(
    "erro",
    [
        smtplib.SMTPDataError(-1, b"linha ilegivel"),
        smtplib.SMTPDataError(999, b"?"),
        smtplib.SMTPDataError(250, b"ok?"),
        smtplib.SMTPServerDisconnected("Connection unexpectedly closed"),
        TimeoutError("timed out"),
        socket.timeout("timed out"),  # noqa: UP041 — o alias antigo, que o smtplib ainda levanta
        OSError("broken pipe"),
        RuntimeError("qualquer outra coisa"),
    ],
    ids=[
        "codigo-menos-um",
        "codigo-999",
        "codigo-250-como-erro",
        "desconexao",
        "timeout",
        "socket-timeout",
        "oserror",
        "outra",
    ],
)
def test_sem_resposta_lida_e_indeterminada_e_para(erro):
    """**Parece código e não é resposta**: `-1` é o que o `smtplib` usa para linha ilegível."""
    classificacao = do_envio(erro=erro)

    assert classificacao.resultado == nomes.INDETERMINADA
    assert classificacao.para_a_execucao


@pytest.mark.parametrize(
    "erro",
    [
        smtplib.SMTPAuthenticationError(535, b"bad"),
        smtplib.SMTPConnectError(421, b"busy"),
        smtplib.SMTPHeloError(501, b"bad helo"),
    ],
)
def test_sessao_que_nao_se_abre_nao_enviou_e_para(erro):
    classificacao = do_envio(erro=erro)

    assert classificacao.resultado == nomes.FALHA_TEMPORARIA
    assert classificacao.para_a_execucao


def test_erro_na_preparacao_e_definitivo_e_nao_para():
    classificacao = na_preparacao(ValueError("endereço inválido"))

    assert classificacao.resultado == nomes.FALHA_DEFINITIVA
    assert not classificacao.para_a_execucao


@pytest.mark.parametrize(
    "erro",
    [
        smtplib.SMTPRecipientsRefused({ENDERECO: (550, f"<{ENDERECO}> unknown".encode())}),
        smtplib.SMTPDataError(554, f"rejected for {ENDERECO}".encode()),
        smtplib.SMTPServerDisconnected(f"closed while sending to {ENDERECO}"),
    ],
)
def test_o_detalhe_nao_leva_o_endereco(erro):
    """`FR-1279`: o servidor costuma ecoar o endereço, e o detalhe vai para a tela da gestão."""
    assert ENDERECO not in do_envio(erro=erro).detalhe
