"""As mensagens do acesso: o código, e o aviso de que alguém mexeu em quem alcança a conta.

**Nada além disso** (FR-084). Aviso de retificação, de resultado, lembrete e campanha continuam
fora de escopo — e esta frase está aqui exatamente porque, a partir da 010, a objeção "não temos
como enviar e-mail" deixa de existir. A confirmação de inscrição vive em `inscricoes`, junto do ato
que a origina.

**São três situações desde a `019`**, e não duas: a convocação por mensagem individual entrou depois
de a `FR-084` ser revisada por escrito, e não por exceção silenciosa. Ela mora em
`convocacao/application/comunicar.py`, e a contagem é varrida por
`tests/test_situacoes_de_mensagem.py` — um `send_mail` num módulo não declarado reprova a suíte.

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
from processo_seletivo.shared import correio
from processo_seletivo.unidades.application import identificacao

logger = logging.getLogger("processo_seletivo.identidade")

# **O texto mora nos modelos**, em `identidade/templates/identidade/mensagem/`: o texto puro, com o
# assunto na primeira linha, e o HTML na moldura comum de `shared/correio.py`. Os dois saem na mesma
# mensagem; quem não lê HTML lê o texto, que diz tudo o que o HTML diz.
#
# **A identificação da implantação, e não a de uma unidade** (109, FR-3210): a conta do candidato
# não é de unidade nenhuma, e o código serve para entrar em qualquer seleção. Com o Cefor sozinho no
# registro, é "Cefor/Ifes", como sempre foi; com mais de uma unidade ativa, "Ifes" (P-1).
MODELO_DO_CODIGO = "identidade/mensagem/codigo"
# O risco é o oposto do de entrar, e o texto precisa dizer isso (FR-082a).
MODELO_DO_VINCULO = "identidade/mensagem/vinculo"
MODELO_DA_MUDANCA = "identidade/mensagem/mudanca"


def _enviar(para, mensagem):
    send_mail(
        subject=mensagem.assunto,
        message=mensagem.texto,
        html_message=mensagem.html,
        from_email=settings.DEFAULT_FROM_EMAIL or None,
        recipient_list=[para],
        fail_silently=False,
    )


def compor_codigo(*, codigo, identificacao_da_implantacao, finalidade=""):
    """O assunto, o texto e o HTML do código — sem enviar, e sem ler o banco."""
    vinculo = finalidade == DesafioDeAcesso.Finalidade.ADICIONAR_CREDENCIAL
    return correio.compor(
        MODELO_DO_VINCULO if vinculo else MODELO_DO_CODIGO,
        {
            **correio.moldura(identificacao_da_implantacao),
            "codigo": codigo,
            "validade": VALIDADE_EM_MINUTOS,
        },
    )


def compor_mudanca(*, endereco, acao, atendimento, identificacao_da_implantacao):
    """O assunto, o texto e o HTML do aviso de mudança de credencial — sem enviar."""
    return correio.compor(
        MODELO_DA_MUDANCA,
        {
            **correio.moldura(identificacao_da_implantacao),
            "acao": acao,
            "endereco": endereco,
            "atendimento": atendimento or "o atendimento institucional",
        },
    )


def enviar_codigo(*, para: str, codigo: str, finalidade: str = "") -> None:
    """Envia — e, se falhar, some em silêncio para quem está do outro lado.

    A falha não pode ser visível: uma mensagem de erro que só aparece para endereços existentes
    seria o mesmo canal lateral que a equivalência de resposta fecha (FR-083). O servidor registra
    o que aconteceu; o visitante lê a mesma coisa dos dois lados.
    """
    if not codigo:
        return
    try:
        _enviar(
            para,
            compor_codigo(
                codigo=codigo,
                identificacao_da_implantacao=identificacao.da_implantacao(),
                finalidade=finalidade,
            ),
        )
    except Exception:
        # Sem o endereço e sem o código: o registro técnico diz que falhou, e nada além disso. O
        # `code` é o que separa a falha do correio das recusas por limite, que `desafio.py` registra
        # com os seus — antes, as duas eram silêncio igual do lado do candidato e só esta deixava
        # rastro.
        logger.exception(
            "Falha ao enviar código de acesso.",
            extra={
                "code": "envio_de_codigo_falhou",
                "operation": f"identidade.solicitar_codigo.{(finalidade or 'entrar').lower()}",
            },
        )


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
        _enviar(
            para,
            compor_mudanca(
                endereco=endereco,
                acao=acao,
                atendimento=atendimento,
                identificacao_da_implantacao=identificacao.da_implantacao(),
            ),
        )
    except Exception:
        logger.exception("Falha ao avisar mudança de credencial.")
