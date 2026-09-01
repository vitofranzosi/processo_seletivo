"""As mensagens do acesso: o código, e o aviso de que alguém mexeu em quem alcança a conta.

**Nada além disso** (FR-084). Aviso de retificação, de resultado, lembrete e campanha continuam
fora de escopo — e esta frase está aqui exatamente porque, a partir da 010, a objeção "não temos
como enviar e-mail" deixa de existir. A confirmação de inscrição vive em `inscricoes`, junto do ato
que a origina.

**O código muda de texto conforme a finalidade** (FR-082a). Entrar e adicionar credencial produzem
riscos opostos para quem recebe: no primeiro, ignorar a mensagem basta, porque ninguém entra sem o
código; no segundo, quem obtiver o código anexa **esta** caixa à conta **dele**, e passa a entrar
por ela. Repetir "ignore, ninguém entra sem ele" no segundo caso é dizer o contrário do que é
verdade.

**Sem link que autentica** (P-001). Um link assim viaja no histórico do navegador, no
encaminhamento da mensagem e no cabeçalho de origem. O código é digitado.

**Sem CPF e sem dado de inscrição** (FR-082). A mensagem vai para uma caixa que ainda não se sabe
de quem é — é justamente o que ela está tentando descobrir.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

from processo_seletivo.identidade.models import VALIDADE_EM_MINUTOS, DesafioDeAcesso

logger = logging.getLogger("processo_seletivo.identidade")

ASSUNTO = "Seu código de acesso — Seleções Cefor/Ifes"
ASSUNTO_VINCULO = "Confirme este e-mail — Seleções Cefor/Ifes"

RODAPE = """
Cefor/Ifes — Seleções
Esta mensagem é automática; não responda.
"""

CORPO = (
    """Seu código de acesso é:

    {codigo}

Ele vale por {validade} minutos e só pode ser usado uma vez.

Se não foi você que pediu este código, ignore esta mensagem: ninguém entra sem ele.
"""
    + RODAPE
)

# O risco é o oposto do de entrar, e o texto precisa dizer isso. Quem receber este código e o
# repassar não perde o acesso a nada — passa a ter este endereço vinculado à conta de outra
# pessoa, que então entra por ele.
CORPO_VINCULO = (
    """Alguém pediu para usar este e-mail como forma de entrar numa conta das Seleções
Cefor/Ifes. Se foi você, o código é:

    {codigo}

Ele vale por {validade} minutos e só pode ser usado uma vez.

Se não foi você, não informe este código a ninguém: quem o tiver poderá entrar na conta dele
por este endereço. Ignorar esta mensagem é suficiente — nada acontece sem o código.
"""
    + RODAPE
)

ASSUNTO_DA_MUDANCA = "Mudança no acesso à sua conta — Seleções Cefor/Ifes"

CORPO_DA_MUDANCA = (
    """O endereço abaixo foi {acao} como forma de entrar na sua conta das Seleções Cefor/Ifes:

    {endereco}

Se foi você, não é preciso fazer nada.

Se não foi, fale com {atendimento}: alguém pode ter obtido acesso à sua conta.
"""
    + RODAPE
)


def enviar_codigo(*, para: str, codigo: str, finalidade: str = "") -> None:
    """Envia — e, se falhar, some em silêncio para quem está do outro lado.

    A falha não pode ser visível: uma mensagem de erro que só aparece para endereços existentes
    seria o mesmo canal lateral que a equivalência de resposta fecha (FR-083). O servidor registra
    o que aconteceu; o visitante lê a mesma coisa dos dois lados.
    """
    if not codigo:
        return
    vinculo = finalidade == DesafioDeAcesso.Finalidade.ADICIONAR_CREDENCIAL
    try:
        send_mail(
            subject=ASSUNTO_VINCULO if vinculo else ASSUNTO,
            message=(CORPO_VINCULO if vinculo else CORPO).format(
                codigo=codigo, validade=VALIDADE_EM_MINUTOS
            ),
            from_email=settings.DEFAULT_FROM_EMAIL or None,
            recipient_list=[para],
            fail_silently=False,
        )
    except Exception:
        # Sem o endereço e sem o código: o registro técnico diz que falhou, e nada além disso.
        logger.exception("Falha ao enviar código de acesso.")


def avisar_mudanca_de_credencial(*, para: str, endereco: str, acao: str, atendimento: str) -> None:
    """Avisa a caixa principal de que outra passou a alcançar — ou deixou de alcançar — a conta.

    Sem senha, a lista de credenciais **é** a conta: quem consegue anexar um endereço a ela entra
    por ele para sempre. Este aviso é o único sinal que a pessoa teria de que isso aconteceu, e por
    isso vai para o endereço principal, que é o que a instituição já usa para falar com ela.

    Vai também na remoção, e pela mesma razão: perder uma via de acesso sem saber é como perder a
    conta em silêncio, e a remoção é o passo que um invasor daria depois de anexar a caixa dele.
    """
    if not para:
        return
    try:
        send_mail(
            subject=ASSUNTO_DA_MUDANCA,
            message=CORPO_DA_MUDANCA.format(
                acao=acao,
                endereco=endereco,
                atendimento=atendimento or "o atendimento institucional",
            ),
            from_email=settings.DEFAULT_FROM_EMAIL or None,
            recipient_list=[para],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Falha ao avisar mudança de credencial.")
