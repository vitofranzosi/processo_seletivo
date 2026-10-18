"""A política de segurança de conteúdo (091).

O cabeçalho `Content-Security-Policy` diz ao navegador de onde a página pode tirar estilo, script,
quadro e destino de formulário. Esta política permite só a própria origem, e nada embutido: um
`<style>`, um `style=""`, um `<script>` sem `src` ou um `onclick` plantado num texto que a gestão
exibe é recusado pelo navegador, ainda que tenha escapado do escape dos modelos. É a segunda
barreira, e só pôde ser ligada quando a gestão deixou de ter estilo embutido (089 e 091).

**Quem recebe o quê** (R-008 da `091`):

- toda resposta HTML sob `/gestao/` — telas, fragmentos do htmx, página de acesso, recusas, página
  de erro — recebe a política em **recusa**;
- toda outra resposta HTML — o portal do candidato e a página pública da seleção — recebe a mesma
  política em **observação** (`-Report-Only`): o navegador acusa no console o que recusaria, sem
  recusar. O portal ainda tem a folha dele no documento; quando ela sair, o portal passa a recusa
  (D-007 da `091`);
- resposta que não é HTML — JSON, PDF, estático — não recebe nada: a política não tem efeito nela;
- a página de depuração do Django, com `DEBUG`, não recebe nada (D-010): ela traz estilo e script
  embutidos, e sob a política perderia o desenho e o que se expande nela. Ela é reconhecida pela
  marca que os modelos de depuração do Django põem no `<head>`, e não pelo status: a gestão também
  serve as próprias recusas com 404;
- resposta que já traz política fica como está — é por aí que a resposta sob `/gestao/` que é página
  do portal fica sob a regra do portal (`em_observacao`).

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

EM_RECUSA = ("/gestao/",)
CABECALHO_DE_RECUSA = "Content-Security-Policy"
CABECALHO_DE_OBSERVACAO = "Content-Security-Policy-Report-Only"

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


def cabecalho_para(caminho, resposta):
    """O nome do cabeçalho que a resposta recebe, ou `None`."""
    if not resposta.get("Content-Type", "").startswith("text/html"):
        return None
    if CABECALHO_DE_RECUSA in resposta or CABECALHO_DE_OBSERVACAO in resposta:
        return None
    if _e_pagina_de_depuracao(resposta):
        return None
    if caminho.startswith(EM_RECUSA):
        return CABECALHO_DE_RECUSA
    return CABECALHO_DE_OBSERVACAO


class PoliticaDeConteudoMiddleware:
    """O primeiro da lista: a resposta de todo middleware de dentro passa por ele na volta."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resposta = self.get_response(request)
        # `path_info`, e não `path`: com a aplicação montada sob um prefixo (`SCRIPT_NAME`), `path`
        # começaria por ele, nenhuma tela casaria com `/gestao/`, e a gestão cairia em observação.
        cabecalho = cabecalho_para(request.path_info, resposta)
        if cabecalho:
            resposta[cabecalho] = POLITICA
        return resposta


def em_observacao(resposta):
    """A resposta sob `/gestao/` que é uma página do portal fica sob a regra do portal.

    É o protótipo do painel de dúvidas (`interface/prototipo_do_assistente.py`): o fundo é a página
    pública da seleção, de verdade, com a folha do portal no documento. Em recusa ela perderia o
    desenho — o inventário da 091 mostrou a violação. A política vai em observação, como no portal,
    e o middleware não a troca, porque a resposta já traz uma.

    Marca a **resposta**, e não a view: a recusa da gestão que a mesma view devolve a quem não tem o
    piloto é página da gestão, e continua em recusa.
    """
    resposta[CABECALHO_DE_OBSERVACAO] = POLITICA
    return resposta
