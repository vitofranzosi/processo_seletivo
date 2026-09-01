"""A única mensagem que esta feature envia.

**Só o desafio** (FR-084). Comprovante por e-mail, aviso de retificação, aviso de resultado,
lembrete e campanha continuam fora de escopo — e esta frase está aqui exatamente porque, a partir
da 010, a objeção "não temos como enviar e-mail" deixa de existir.

**Sem link que autentica** (P-001). Um link assim viaja no histórico do navegador, no
encaminhamento da mensagem e no cabeçalho de origem. O código é digitado.

**Sem CPF e sem dado de inscrição** (FR-082). A mensagem vai para uma caixa que ainda não se sabe
de quem é — é justamente o que ela está tentando descobrir.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

from processo_seletivo.identidade.models import VALIDADE_EM_MINUTOS

logger = logging.getLogger("processo_seletivo.identidade")

ASSUNTO = "Seu código de acesso — Seleções Cefor/Ifes"

CORPO = """Seu código de acesso é:

    {codigo}

Ele vale por {validade} minutos e só pode ser usado uma vez.

Se não foi você que pediu este código, ignore esta mensagem: ninguém entra sem ele.

Cefor/Ifes — Seleções
Esta mensagem é automática; não responda.
"""


def enviar_codigo(*, para: str, codigo: str) -> None:
    """Envia — e, se falhar, some em silêncio para quem está do outro lado.

    A falha não pode ser visível: uma mensagem de erro que só aparece para endereços existentes
    seria o mesmo canal lateral que a equivalência de resposta fecha (FR-083). O servidor registra
    o que aconteceu; o visitante lê a mesma coisa dos dois lados.
    """
    if not codigo:
        return
    try:
        send_mail(
            subject=ASSUNTO,
            message=CORPO.format(codigo=codigo, validade=VALIDADE_EM_MINUTOS),
            from_email=settings.DEFAULT_FROM_EMAIL or None,
            recipient_list=[para],
            fail_silently=False,
        )
    except Exception:
        # Sem o endereço e sem o código: o registro técnico diz que falhou, e nada além disso.
        logger.exception("Falha ao enviar código de acesso.")
