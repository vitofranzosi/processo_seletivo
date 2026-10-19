"""A política de segurança de conteúdo (091, 092).

O cabeçalho `Content-Security-Policy` diz ao navegador de onde a página pode tirar estilo, script,
quadro e destino de formulário. Esta política permite só a própria origem, e nada embutido: um
`<style>`, um `style=""`, um `<script>` sem `src` ou um `onclick` plantado num texto que o sistema
exibe é recusado pelo navegador, ainda que tenha escapado do escape dos modelos. É a segunda
barreira, e só pôde ser ligada quando a gestão (089 e 091) e o portal (092) deixaram de ter estilo
embutido.

**Quem recebe o quê** (R-008 da `091`, decisão 003 da `092`):

- toda resposta HTML — a gestão, o portal do candidato, a página pública da seleção, as páginas de
  erro — recebe a política em **recusa**. Na `091` só a gestão recebia; o resto ia em observação
  (`-Report-Only`), porque o portal tinha a folha dele no documento. Com ela num arquivo, a regra
  deixou de depender do caminho: uma área nova nasce sob a política, e não precisa que alguém se
  lembre de incluí-la;
- resposta que não é HTML — JSON, PDF, estático — não recebe nada: a política não tem efeito nela;
- a página de depuração do Django, com `DEBUG`, não recebe nada (D-010 da `091`): ela traz estilo e
  script embutidos, e sob a política perderia o desenho e o que se expande nela. Ela é reconhecida
  pela marca que os modelos de depuração do Django põem no `<head>`, e não pelo status: a gestão
  também serve as próprias recusas com 404;
- resposta que já traz política fica como está: a view que precisar de outra a declara.

O framework, na versão em uso (5.2), não traz middleware de CSP — ele chega na 6.0. Daí este, sem
dependência nova (D-006 da `091`).

**Sem `frame-ancestors`**: quem impede outra origem de emoldurar a gestão continua sendo o
`X-Frame-Options`, com a exceção `SAMEORIGIN` que a prévia do PDF declara por view. Repetir a regra
aqui exigiria espelhar a exceção, e `frame-ancestors` vence o `X-Frame-Options` nos navegadores
atuais: um erro aqui derrubaria a prévia ou abriria a gestão.
"""

from django.conf import settings

# Uma diretiva por linha, para o diff mostrar qual mudou. `object-src` e `frame-src` são da
# própria origem porque a prévia do Edital abre o PDF num `<object>` e a Mesa abre o documento do
# candidato num `<iframe>`. `base-uri` e `form-action` não herdam de `default-src`: sem elas, uma
# marcação injetada poderia trocar a base dos endereços ou mandar um formulário para fora.
DIRETIVAS = (
    ("default-src", "'self'"),
    ("script-src", "'self'"),
    ("style-src", "'self'"),
    ("img-src", "'self'"),
    ("font-src", "'self'"),
    ("connect-src", "'self'"),
    ("object-src", "'self'"),
    ("frame-src", "'self'"),
    ("base-uri", "'self'"),
    ("form-action", "'self'"),
)
POLITICA = "; ".join(f"{diretiva} {valor}" for diretiva, valor in DIRETIVAS)

CABECALHO = "Content-Security-Policy"

# O `<meta>` que os modelos de depuração do Django (`technical_404.html`, `technical_500.html`)
# trazem no `<head>`, e que os modelos do sistema não trazem.
_MARCA_DA_DEPURACAO = b'<meta name="robots" content="NONE,NOARCHIVE">'


def _e_pagina_de_depuracao(resposta):
    # A marca é procurada no `<head>` inteiro, e não num prefixo fixo: no `technical_404.html` ela
    # vem depois do `<title>`, que traz o caminho pedido — um endereço longo a empurraria para fora.
    if not settings.DEBUG or resposta.streaming:
        return False
    cabeca = resposta.content.split(b"</head>", 1)[0]
    return _MARCA_DA_DEPURACAO in cabeca


def recebe_a_politica(resposta):
    """Se a resposta recebe o cabeçalho da política.

    Não depende do caminho (decisão 003 da `092`): na `091` dependia, e o caminho era lido de
    `path_info` para não tirar a gestão da recusa quando a aplicação estivesse sob um prefixo.
    """
    if not resposta.get("Content-Type", "").startswith("text/html"):
        return False
    if CABECALHO in resposta:
        return False
    return not _e_pagina_de_depuracao(resposta)


class PoliticaDeConteudoMiddleware:
    """O primeiro da lista: a resposta de todo middleware de dentro passa por ele na volta."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resposta = self.get_response(request)
        if recebe_a_politica(resposta):
            resposta[CABECALHO] = POLITICA
        return resposta
