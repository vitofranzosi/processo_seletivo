"""O que a resposta do servidor de correio permite afirmar, pela fase em que veio (066, `R-004`).

**O código só classifica quando é resposta lida a um comando da mensagem.** O `smtplib` levanta
`SMTPSenderRefused`, `SMTPRecipientsRefused` e `SMTPDataError` quando leu uma resposta ao `MAIL`, ao
`RCPT`, ao `DATA` ou à confirmação final do conteúdo — e aí 4xx é recusa temporária e 5xx é recusa
definitiva, porque o servidor **disse** que não aceitou.

**Todo o resto é indeterminado**, mesmo quando parece código: queda da conexão, timeout, resposta
ilegível (o `smtplib` devolve `-1` para a linha que não conseguiu interpretar) ou um número fora de
400–599. Nesses casos a mensagem pode ter saído, e reenviá-la sozinho entregaria duas vezes a mesma
coisa — o defeito que esta feature existe para não ter (`FR-1267`).

**O detalhe técnico não leva o texto do servidor.** Ele costuma trazer o endereço recusado —
`550 5.1.1 <pessoa@exemplo>: user unknown` — e o detalhe vai para a tela de quem conduz o certame
(`FR-1279`). Leva o tipo e o código, que bastam para o diagnóstico.
"""

import smtplib
from dataclasses import dataclass

from processo_seletivo.avisos.domain import nomes


@dataclass(frozen=True)
class Classificacao:
    resultado: str
    detalhe: str = ""
    # A conexão está em estado desconhecido, ou não se abriu: a execução para aqui, e a seguinte
    # recomeça com conexão nova.
    para_a_execucao: bool = False


# Falhas da abertura da sessão: conexão, `EHLO`, autenticação. Nenhum comando da mensagem foi
# emitido, e por isso nada saiu — mas a sessão não serve para a próxima.
_ABERTURA = (
    smtplib.SMTPConnectError,
    smtplib.SMTPHeloError,
    smtplib.SMTPAuthenticationError,
    smtplib.SMTPNotSupportedError,
)

# As que só existem com uma resposta lida a um comando da transação da mensagem.
_RESPOSTA_DA_TRANSACAO = (
    smtplib.SMTPSenderRefused,
    smtplib.SMTPDataError,
)


def _pelo_codigo(codigo, tipo):
    if isinstance(codigo, int) and 400 <= codigo <= 499:
        return Classificacao(nomes.FALHA_TEMPORARIA, f"{tipo} {codigo}: recusa temporária")
    if isinstance(codigo, int) and 500 <= codigo <= 599:
        return Classificacao(nomes.FALHA_DEFINITIVA, f"{tipo} {codigo}: recusa definitiva")
    return Classificacao(
        nomes.INDETERMINADA,
        f"{tipo} {codigo}: resposta que não se pôde interpretar",
        para_a_execucao=True,
    )


def na_preparacao(erro):
    """O erro ao montar a mensagem, **antes** da rede: endereço ou conteúdo que não se codifica.

    Nada foi ao servidor, e tentar de novo daria o mesmo erro — por isso é definitiva, e não para a
    execução: a conexão nem foi usada.
    """
    return Classificacao(
        nomes.FALHA_DEFINITIVA, f"{type(erro).__name__}: endereço ou conteúdo inválido"
    )


def do_envio(*, erro=None, enviadas=None):
    """A classificação do que `send_messages([mensagem])` devolveu, ou levantou."""
    if erro is None:
        if enviadas == 1:
            return Classificacao(nomes.ACEITA)
        # **Zero não é sucesso** — o critério de `convocacao/application/comunicar.py`: um backend
        # que engole a mensagem devolve 0 sem levantar nada. Temporária, e o limite de tentativas a
        # torna definitiva.
        return Classificacao(nomes.FALHA_TEMPORARIA, "o servidor de correio não aceitou a mensagem")
    tipo = type(erro).__name__
    if isinstance(erro, _ABERTURA):
        return Classificacao(
            nomes.FALHA_TEMPORARIA,
            f"{tipo}: a sessão com o servidor de correio não se abriu",
            para_a_execucao=True,
        )
    if isinstance(erro, smtplib.SMTPRecipientsRefused):
        # Um destinatário só por mensagem (`FR-1271`): a recusa é a dele, com o código que o
        # servidor deu ao `RCPT`.
        codigos = [codigo for codigo, _ in (erro.recipients or {}).values()]
        return _pelo_codigo(codigos[0] if len(codigos) == 1 else None, tipo)
    if isinstance(erro, _RESPOSTA_DA_TRANSACAO):
        return _pelo_codigo(getattr(erro, "smtp_code", None), tipo)
    return Classificacao(
        nomes.INDETERMINADA,
        f"{tipo}: a conexão caiu ou não respondeu, e não se sabe se a mensagem foi aceita",
        para_a_execucao=True,
    )


__all__ = ["Classificacao", "do_envio", "na_preparacao"]
