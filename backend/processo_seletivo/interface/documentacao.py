"""Documentação de uso acessível às identidades da gestão."""

from django.conf import settings
from django.http import Http404
from django.views.decorators.http import require_GET
from django.views.static import serve

from processo_seletivo.interface import identidade


@require_GET
def consultar(request, arquivo="index.html"):
    if identidade.ator_da_sessao(request) is None:
        return identidade.pedir_identificacao(request)
    # Só os arquivos do manual são destinos; nenhum outro arquivo do repositório é servido.
    if arquivo not in {"index.html", "assets/style.css", "assets/app.js", "assets/iniciar.js"}:
        raise Http404
    return serve(
        request,
        arquivo,
        document_root=settings.BASE_DIR.parent / "docs" / "visao-sistema",
    )
