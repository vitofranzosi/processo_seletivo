"""Views da interface administrativa.

Cada view invoca a camada de aplicação — nunca modelos direto, nunca a própria API por HTTP.
A decisão de autorização continua no backend: ocultar uma ação na tela é conveniência, não
fronteira de segurança (FR-002).
"""

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from processo_seletivo.interface import identidade
from processo_seletivo.processos.application.selectors import (
    contar_por_situacao,
    listar_processos,
)

# Ordem em que as situações aparecem: o fluxo do Edital, não a ordem alfabética.
ORDEM_SITUACAO = [
    "EM_ELABORACAO",
    "EM_REVISAO",
    "HOMOLOGADO",
    "PUBLICADO",
    "ENCERRADO",
    "CANCELADO",
]

# O que cada situação permite fazer, e com qual permissão. A tela oferece; o domínio decide.
ACOES_POR_SITUACAO = {
    "EM_ELABORACAO": [("Elaborar", "edital:elaborar"), ("Submeter", "edital:submeter")],
    "EM_REVISAO": [("Homologar", "edital:homologar")],
    "HOMOLOGADO": [("Publicar", "edital:publicar"), ("Revogar homologação", "edital:homologar")],
    "PUBLICADO": [("Retificar", "retificacao:elaborar"), ("Encerrar", "edital:encerrar")],
}


def acoes_disponiveis(ator, situacao):
    return [
        rotulo
        for rotulo, permissao in ACOES_POR_SITUACAO.get(situacao, [])
        if ator.can(permissao)
    ]


@require_http_methods(["GET"])
def lista(request):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))

    processos = list(listar_processos(actor=ator))
    for processo in processos:
        for edital in processo.editais.all():
            edital.acoes = acoes_disponiveis(ator, edital.status)

    contagem = contar_por_situacao(processos)
    return render(
        request,
        "interface/lista.html",
        {
            "processos": processos,
            "total_editais": sum(contagem.values()),
            "resumo": [
                (situacao, contagem[situacao])
                for situacao in ORDEM_SITUACAO
                if situacao in contagem
            ],
            "pode_criar": ator.can("processo:criar"),
            "sem_papel": not ator.permissions,
        },
    )


@require_http_methods(["GET", "POST"])
def identificar(request):
    """Seletor de identidade: substitui a autenticação institucional fora de produção."""
    if not identidade.seletor_disponivel():
        return render(request, "interface/sem_autenticacao.html", status=503)
    if request.method == "POST":
        papeis = request.POST.getlist("papeis")
        subject = (request.POST.get("subject") or "").strip()
        if subject and papeis:
            identidade.identificar(request, subject=subject, papeis=papeis)
            return redirect(reverse("interface:lista"))
        return render(
            request,
            "interface/identificar.html",
            {"papeis": identidade.PAPEIS, "erro": "Informe um nome e ao menos um papel."},
            status=422,
        )
    return render(request, "interface/identificar.html", {"papeis": identidade.PAPEIS})


@require_http_methods(["POST"])
def sair(request):
    identidade.encerrar(request)
    return redirect(reverse("interface:identificar"))
