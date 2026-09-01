"""Traduz recusa do domínio em página, e não em erro de servidor.

O handler de exceções do DRF só alcança views do DRF. As views renderizadas são Django comuns,
então uma DomainError não tratada vira 500 — inclusive quando ela diz apenas "você não tem essa
permissão". Este middleware fecha essa classe inteira: toda recusa do domínio que chegue a um
canal de página vira uma página com o mesmo status HTTP e a mensagem que o domínio escreveu.

**Os dois canais, e um template para cada** (009). A recusa que o candidato lê não pode aparecer
sobre o cabeçalho da gestão, e a que o servidor lê não pode perder o dele. O mecanismo é um só; o
que muda é onde a página é composta.
"""

from django.shortcuts import render

from processo_seletivo.shared.api.problems import DomainError

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
