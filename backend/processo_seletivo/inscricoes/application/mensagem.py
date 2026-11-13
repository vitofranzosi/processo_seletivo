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

**A terceira chegou, e a regra foi revisada em vez de contornada** (019, `R-008`). A convocação por
mensagem individual é a situação nova, em `convocacao/application/comunicar.py`, e ela **quebra** o
critério que unia as duas primeiras: é ato da Administração dirigido à pessoa, e não recibo de ato
dela. O que a admite é norma publicada — o Edital declara que comunica assim —, e a `FR-084` da
`010` foi reescrita, com a redação anterior preservada. A contagem é verificada em
`tests/test_situacoes_de_mensagem.py`, para que a quarta não entre calada como esta quase entrou.

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
from django.core.mail import EmailMultiAlternatives

from processo_seletivo.shared import correio
from processo_seletivo.unidades.application import identificacao

logger = logging.getLogger("processo_seletivo.inscricoes")

# **O texto mora nos modelos** (`inscricoes/templates/inscricoes/mensagem/comprovante.*`): o texto
# puro, com o assunto na primeira linha, e o HTML na moldura comum de `shared/correio.py`.
MODELO = "inscricoes/mensagem/comprovante"


def compor_comprovante(dados):
    """O assunto, o texto e o HTML do recibo — sem enviar.

    `dados["assinatura"]` é a unidade do ato, que o portal resolve como o comprovante em papel
    (109). Sem ela, a da implantação — e nunca um Cefor escrito aqui.
    """
    assinatura = dados.get("assinatura") or identificacao.da_implantacao().rotulo
    sigla, _, instituicao = assinatura.partition("/")
    return correio.compor(
        MODELO,
        {
            "instituicao": identificacao.SIGLA_DA_INSTITUICAO,
            "instituicao_por_extenso": identificacao.NOME_DA_INSTITUICAO,
            # O cabeçalho diz a unidade que assina, e só a instituição quando é ela que assina.
            "unidade": sigla if instituicao else "",
            "assinatura": assinatura,
            "protocolo": dados["protocolo"],
            "verificacao": dados["verificacao"],
            "selecao": [linha for linha in str(dados["selecao"]).split("\n") if linha.strip()],
            "perfil": dados["perfil"],
            "modalidade": dados["modalidade"],
            "quando": dados["quando"],
            "documentos": dados["documentos"],
            "endereco": dados["endereco"],
        },
    )


def entregar(*, para, mensagem):
    """Põe a mensagem na fila do correio: texto puro, HTML e os cabeçalhos de mensagem automática.

    **Um destinatário só, sem cópia.** `EmailMultiAlternatives`, e não `send_mail`, porque só ela
    leva cabeçalho: `Auto-Submitted` diz aos servidores que ninguém a escreveu à mão, e a resposta
    automática de férias não volta para uma caixa que ninguém lê.
    """
    email = EmailMultiAlternatives(
        subject=mensagem.assunto,
        body=mensagem.texto,
        from_email=settings.DEFAULT_FROM_EMAIL or None,
        to=[para],
        headers=dict(correio.CABECALHOS),
    )
    email.attach_alternative(mensagem.html, "text/html")
    email.send(fail_silently=False)


def enviar_comprovante(*, para: str, dados: dict) -> None:
    """Envia o recibo do envio — e, falhando, registra sem interromper quem se inscreveu.

    Sem `para` não há o que fazer: uma inscrição sem endereço não deveria existir, mas se existir
    não é aqui que ela vai ser descoberta.
    """
    if not para:
        return
    try:
        entregar(para=para, mensagem=compor_comprovante(dados))
    except Exception:
        # Sem o endereço e sem o protocolo: o registro técnico diz que falhou, e nada além disso.
        logger.exception("Falha ao enviar a confirmação de inscrição.")
