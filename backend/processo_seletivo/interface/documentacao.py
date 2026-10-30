"""A Visão do Sistema dentro da gestão (105): o manual de `docs/visao-sistema/`, sob a identidade.

**Toda identidade da gestão entra** (`D-001`), como na Agenda: o manual é o mesmo arquivo que o
repositório traz, e não mostra dado de certame nenhum. Pedir capacidade deixaria de fora justamente
quem só tem vínculo, que é quem mais precisa do tutorial.

**Lista literal de arquivos, e não a pasta** (`D-002`). A pasta tem os registros de mudança do
manual, e o diretório-pai tem o repositório inteiro: servir por caminho pedido exigiria provar, a
cada pedido, que o caminho não sai dela. Com a lista, o que não está nela é inexistente, e um
arquivo novo do manual só aparece depois de alguém o acrescentar aqui — o guardião
`test_documentacao_do_sistema.py` cobra a lista contra o que o `index.html` referencia.

**Os bytes vão na resposta, e não um `FileResponse`** (`D-003`). O `serve` do Django devolvia o
arquivo aberto, e quem lê a resposta sem consumi-la — a suíte, que confere os destinos da barra —
deixava o descritor para o coletor de lixo: `ResourceWarning`, que o `pyproject.toml` promove a
erro. São cinco arquivos, o maior com ~1 MB.
"""

from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_http_methods

from processo_seletivo.interface import identidade

PASTA = settings.BASE_DIR.parent / "docs" / "visao-sistema"

# O tipo é declarado, e não adivinhado pela extensão: o HTML recebe a política de conteúdo pelo
# tipo (`shared/politica_de_conteudo.py`), e um `text/html` errado aqui a tiraria do manual.
ARQUIVOS = {
    "index.html": "text/html; charset=utf-8",
    "assets/style.css": "text/css; charset=utf-8",
    "assets/app.js": "text/javascript; charset=utf-8",
    "assets/iniciar.js": "text/javascript; charset=utf-8",
    "assets/icone.svg": "image/svg+xml",
}


@require_http_methods(["GET"])
def visao_do_sistema(request, arquivo="index.html"):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    tipo = ARQUIVOS.get(arquivo)
    if tipo is None:
        raise Http404
    return HttpResponse((PASTA / arquivo).read_bytes(), content_type=tipo)
