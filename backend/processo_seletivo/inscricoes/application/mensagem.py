"""A confirmação do envio da inscrição.

**Por que ela existe, se a `010` dizia que não existiria.** A `FR-084` proibia qualquer outra
comunicação por e-mail, e a razão era boa: o canal passar a existir não torna comunicação
transacional escopo implícito. Percorrer a jornada mostrou o custo concreto dessa fronteira — a
pessoa conclui o ato mais importante do ano dela, o sistema mostra o comprovante na tela, e a caixa
de entrada não registra nada. Fechada a aba antes de baixar o PDF, ela fica sem o protocolo, que é
justamente o que a página manda guardar.

A `FR-084` passou então a nomear **duas** exceções, e esta é uma delas; a outra é o aviso de mudança
de credencial, em `identidade/application/mensagem.py`. As duas são recibo de ato que a própria
pessoa praticou, e é essa a fronteira: aviso de resultado, de retificação e lembrete continuam fora,
e uma terceira exigiria revisar a regra em vez de acrescentar um remetente.

**Não é a mensagem do desafio.** Lá a caixa ainda não se sabe de quem é, e por isso a `FR-082`
proíbe CPF e dado de inscrição. Aqui o endereço é credencial provada da identidade que praticou o
ato, e o conteúdo é o que ela acabou de ver na tela. Ainda assim, **sem CPF e sem telefone**: eles
não ajudam quem lê e viajam para onde a mensagem for encaminhada.

**Depois do commit, e nunca dentro dele.** O envio acontece com a inscrição já gravada. Enviar de
dentro da transação amarraria um ato administrativo à disponibilidade de um servidor de SMTP: uma
falha de rede desfaria uma inscrição válida, e um rollback posterior deixaria na caixa da pessoa a
confirmação de algo que não aconteceu (Princípio IV). Falha de envio não custa a inscrição, e por
isso ela é registrada no servidor em vez de interromper a pessoa.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger("processo_seletivo.inscricoes")

ASSUNTO = "Inscrição recebida — {protocolo}"

CORPO = """Recebemos a sua inscrição.

    Protocolo: {protocolo}
    Código de verificação: {verificacao}

{selecao}
Perfil de vaga: {perfil}
Concorrência: {modalidade}
Enviada em {quando}

Documentos recebidos:
{documentos}

O recebimento não implica deferimento: a conferência dos documentos e a análise dos requisitos são
feitas pela comissão, nos prazos do Edital.

Para rever a inscrição e baixar o comprovante, acesse
{endereco}
e entre com este e-mail — enviamos um código de acesso a cada entrada, e não há senha.

Cefor/Ifes — Seleções
Esta mensagem é automática; não responda.
"""


def enviar_comprovante(*, para: str, dados: dict) -> None:
    """Envia o recibo do envio — e, falhando, registra sem interromper quem se inscreveu.

    Sem `para` não há o que fazer: uma inscrição sem endereço não deveria existir, mas se existir
    não é aqui que ela vai ser descoberta.
    """
    if not para:
        return
    documentos = (
        "\n".join(
            f"    - {documento['requisito']}: {documento['arquivo']}"
            for documento in dados["documentos"]
        )
        or "    (nenhum)"
    )
    try:
        send_mail(
            subject=ASSUNTO.format(protocolo=dados["protocolo"]),
            message=CORPO.format(
                protocolo=dados["protocolo"],
                verificacao=dados["verificacao"],
                selecao=dados["selecao"],
                perfil=dados["perfil"],
                modalidade=dados["modalidade"],
                quando=dados["quando"],
                documentos=documentos,
                endereco=dados["endereco"],
            ),
            from_email=settings.DEFAULT_FROM_EMAIL or None,
            recipient_list=[para],
            fail_silently=False,
        )
    except Exception:
        # Sem o endereço e sem o protocolo: o registro técnico diz que falhou, e nada além disso.
        logger.exception("Falha ao enviar a confirmação de inscrição.")
