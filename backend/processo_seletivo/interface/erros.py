"""Traduz recusa do domínio em página, e não em erro de servidor.

O handler de exceções do DRF só alcança views do DRF. As views renderizadas são Django comuns,
então uma DomainError não tratada vira 500 — inclusive quando ela diz apenas "você não tem essa
permissão". Este middleware fecha essa classe inteira: toda recusa do domínio que chegue a um
canal de página vira uma página com o mesmo status HTTP e a mensagem que o domínio escreveu.

**Os dois canais, e um template para cada** (009). A recusa que o candidato lê não pode aparecer
sobre o cabeçalho da gestão, e a que o servidor lê não pode perder o dele. O mecanismo é um só; o
que muda é onde a página é composta.
"""

import logging

from django.conf import settings
from django.core.exceptions import RequestDataTooBig, TooManyFieldsSent, TooManyFilesSent
from django.shortcuts import render
from django.utils.http import url_has_allowed_host_and_scheme

from processo_seletivo.shared.api.problems import DomainError

logger = logging.getLogger("processo_seletivo.interface")

PAGINA_DA_RECUSA = {
    "/gestao/": "interface/recusa.html",
    "/selecoes/": "portal/recusa.html",
}
TITULOS = {
    403: "Você não tem permissão para isto",
    404: "Recurso não encontrado",
    409: "Operação incompatível com a situação atual",
    412: "O conteúdo mudou enquanto você trabalhava",
    422: "Não foi possível concluir",
}


class RecusaDoDominioMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if not isinstance(exception, DomainError):
            return None
        template = next(
            (
                pagina
                for prefixo, pagina in PAGINA_DA_RECUSA.items()
                if request.path.startswith(prefixo)
            ),
            None,
        )
        if template is None:
            return None
        return render(
            request,
            template,
            {
                "titulo": TITULOS.get(exception.status, "Operação recusada"),
                "detalhe": exception.detail,
                "codigo": exception.code,
            },
            status=exception.status,
        )


def _o_que_passou(exception):
    """O limite que o envio passou, com o número — é o que quem administra o sistema precisa ler."""
    if isinstance(exception, TooManyFieldsSent):
        limite = f"{settings.DATA_UPLOAD_MAX_NUMBER_FIELDS:,}".replace(",", ".")
        return f"mais campos do que o sistema aceita num envio só, que são {limite}"
    if isinstance(exception, TooManyFilesSent):
        limite = settings.DATA_UPLOAD_MAX_NUMBER_FILES
        return f"mais arquivos do que o sistema aceita num envio só, que são {limite}"
    return "mais texto do que o sistema aceita num envio só"


class EnvioAcimaDoLimiteMiddleware:
    """O envio que o Django recusa por tamanho vira página da gestão, e não 400 cru.

    `DATA_UPLOAD_MAX_NUMBER_FIELDS` e os dois limites irmãos são conferidos quando o corpo é lido
    pela primeira vez — e quem o lê é o `CsrfViewMiddleware`, antes de qualquer view. A exceção
    nunca chega ao `process_exception` do middleware acima, e o `handler400` do Django não serve:
    ele responde a todo 400, e com `DEBUG` ligado é trocado pela página técnica, de modo que o
    runserver e o preview mostrariam uma coisa e a produção outra. O que a pessoa via era a página
    de erro do servidor, fora do assistente, sem dizer que nada foi gravado nem o que fazer
    (`doc/achado-etapa-perfis-recusa-acima-de-mil-campos.md`) — contra a FR-021 da 002, que manda
    distinguir recusa de falha, e a FR-801 da 048, que manda toda recusa da Retificação dizer o que
    fazer.

    **Por isso lê o corpo antes, e só na gestão.** Fica entre a sessão e o CSRF: a leitura é a
    mesma que o CSRF faria logo em seguida, e o que muda é quem responde quando ela falha. O
    portal e a API continuam com a resposta do Django — o portal não tem formulário perto do
    limite, e a API fala `problem+json`, que não é página.

    **413, e não 400**: o pedido não está malformado, está grande demais, e o limite é do sistema.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith("/gestao/"):
            try:
                request.POST  # noqa: B018 — a leitura é o que dispara a recusa
            except (TooManyFieldsSent, TooManyFilesSent, RequestDataTooBig) as exception:
                return self._recusa(request, exception)
        return self.get_response(request)

    def _recusa(self, request, exception):
        logger.warning(
            "Envio acima do limite recusado em %s: %s", request.path, type(exception).__name__
        )
        origem = request.headers.get("referer", "")
        if not url_has_allowed_host_and_scheme(
            origem, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            origem = ""
        return render(
            request,
            "interface/recusa.html",
            {
                "titulo": "O envio passou do limite que o sistema aceita",
                "detalhe": (
                    f"Nada foi gravado. Esta tela enviou {_o_que_passou(exception)}, e o envio foi "
                    "recusado antes de ser lido."
                ),
                # **O rascunho local guarda, mas não devolve**: restaurá-lo é reenviar o formulário
                # inteiro (`rascunho.js`), e o reenvio passa do mesmo limite. Ele sobrevive à recusa
                # — só a gravação o apaga — e volta a servir quando o limite for ampliado, dentro do
                # dia em que vale. Dizer só "o rascunho preserva" faria a pessoa tentar restaurar e
                # receber esta página de novo.
                "ajuda": (
                    "Para não perder o que digitou, volte com o botão Voltar do navegador, sem "
                    "recarregar a página. Nas etapas da composição, o rascunho guardado neste "
                    "navegador também o preserva por um dia, mas só poderá ser restaurado depois "
                    "que o limite for ampliado. Peça a ampliação do limite de envio a quem "
                    "administra o sistema no Cefor, dizendo o Edital e a tela: até lá, esta tela "
                    "não consegue gravar."
                ),
                "reabrir": origem,
            },
            status=413,
        )
