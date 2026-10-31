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


def _tela_de_origem(request):
    """A página de onde o envio veio, quando é do próprio servidor; senão, vazio.

    O `Referer` é o que o navegador diz, e numa falsificação ele é o site de quem a montou: um link
    para ele seria o sistema convidando a pessoa a voltar lá (D-005 da `093`).
    """
    origem = request.headers.get("referer", "")
    if not url_has_allowed_host_and_scheme(
        origem, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return ""
    return origem


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
                    f"administra o sistema no {_unidade_de_quem_enviou(request)}, dizendo o "
                    "Edital e a tela: até lá, esta tela não consegue gravar."
                ),
                "reabrir": _tela_de_origem(request),
            },
            status=413,
        )


def _unidade_de_quem_enviou(request):
    """A unidade em que o ator atua, como a moldura da gestão a diz (109, FR-3205)."""
    from processo_seletivo.interface import identidade

    return identidade.identificacao_da_gestao(identidade.ator_da_sessao(request)).nome_curto


def falha_de_csrf(request, reason=""):
    """A recusa da verificação anti-falsificação na moldura da área, e não na página do framework.

    O `CSRF_FAILURE_VIEW` do Django responde com o `403_csrf.html` dele, que traz o estilo num
    `<style>`: sob a política de segurança de conteúdo em recusa (091, 092), o navegador não o
    aplica, e a página saía crua, em inglês, falando em "cookie" a quem só tinha deixado a aba
    aberta de um dia para o outro (093). Só trocar o modelo, por `CSRF_FAILURE_TEMPLATE_NAME`, não
    bastaria: o framework o renderiza sem a requisição, e as bases das duas áreas precisam dela
    (D-001 da `093`).

    **A moldura pelo caminho, e a do portal fora da gestão** (D-002 da `093`). As recusas do
    domínio, fora dos dois prefixos, deixam a resposta do framework; esta não pode, porque é ela que
    sai sem desenho. E `path_info`, e não `path`: com a aplicação sob um prefixo, `path` o traria, e
    a gestão inteira receberia a moldura do portal (o achado da revisão da `091` sobre a política).

    **O motivo vai ao registro, e não à página.** Para quem lê, o que fazer é o mesmo qualquer que
    seja a causa; o motivo do framework só serve a quem diagnostica (D-003 da `093`). O Django já o
    registra, em `django.security.csrf` — mas o manipulador que o `LOGGING` padrão dele dá a esse
    logger só escreve com a depuração ligada, e em produção a linha não chegava a lugar nenhum. Daí
    o registro no logger do projeto, que é o que a produção coleta (R-003 da `093`).
    """
    logger.warning("Envio recusado pela verificação de CSRF em %s: %r", request.path, reason)
    contexto = {
        "titulo": "O formulário não pôde ser enviado",
        "detalhe": (
            "Nada foi gravado. O formulário expirou ou foi enviado de outra página, e por "
            "segurança o envio foi recusado."
        ),
        "ajuda": (
            "Volte à página do formulário, recarregue-a e envie de novo. Ao recarregar, o que você "
            "digitou e não foi gravado se perde: copie antes o que quiser manter."
        ),
        "reabrir": _tela_de_origem(request),
    }
    template = next(
        (
            pagina
            for prefixo, pagina in PAGINA_DA_RECUSA.items()
            if request.path_info.startswith(prefixo)
        ),
        PAGINA_DA_RECUSA["/selecoes/"],
    )
    return render(request, template, contexto, status=403)
