"""Views da interface administrativa.

Cada view invoca a camada de aplicação — nunca modelos direto, nunca a própria API por HTTP.
A decisão de autorização continua no backend: ocultar uma ação na tela é conveniência, não
fronteira de segurança (FR-002).
"""

from uuid import uuid4

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from processo_seletivo.editais.application.draft import replace_draft
from processo_seletivo.editais.domain.validation import validate_for_publication
from processo_seletivo.interface import forms, identidade
from processo_seletivo.processos.application.selectors import (
    contar_por_situacao,
    listar_processos,
    obter_edital,
)
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from processo_seletivo.shared.api.problems import DomainError

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


# Ações que já têm tela; as demais aparecem sem link até serem construídas.
ROTA_DA_ACAO = {"Elaborar": "interface:compor"}


def acoes_disponiveis(ator, situacao):
    return [
        {"rotulo": rotulo, "rota": ROTA_DA_ACAO.get(rotulo)}
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


SEVERIDADE = {"BLOCKING_ERROR": "erro", "WARNING": "aviso", "INFO": "informacao"}


def _pendencias(edital):
    """FR-008: o que ainda falta para o Edital poder ser submetido."""
    achados = validate_for_publication(edital_snapshot(edital))
    return [
        {"severidade": SEVERIDADE.get(str(item.severity), "informacao"),
         "mensagem": item.message, "campo": item.path}
        for item in achados
    ]


@require_http_methods(["GET", "POST"])
def compor(request, edital_id):
    """Composição de Perfis e Cronograma do rascunho (US2 e US3 da 002)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))

    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404
    editavel = edital.status == Edital.Status.EM_ELABORACAO and ator.can("edital:elaborar")

    erros, perfis, eventos = [], None, None
    if request.method == "POST":
        if not editavel:
            erros.append(
                "Este Edital não está em elaboração ou você não tem permissão para editá-lo."
            )
        else:
            try:
                perfis = forms.ler_perfis(request.POST)
                eventos = forms.ler_eventos(request.POST)
                replace_draft(
                    actor=ator,
                    edital_id=edital.id,
                    expected_revision=edital.revision,
                    profiles=perfis,
                    schedule=eventos,
                    correlation_id=request.correlation_id,
                )
                return redirect(f"{reverse('interface:compor', args=[edital.id])}?salvo=1")
            except ValueError as exc:
                erros.append(str(exc))
            except DomainError as exc:
                erros.append(exc.detail)
        edital.refresh_from_db()

    return render(
        request,
        "interface/compor.html",
        {
            "edital": edital,
            "editavel": editavel,
            "erros": erros,
            "salvo": request.GET.get("salvo") == "1",
            "perfis": (
                forms.perfis_do_edital(edital) if perfis is None else _reexibir_perfis(perfis)
            ),
            "eventos": (
                forms.eventos_do_edital(edital) if eventos is None else _reexibir_eventos(eventos)
            ),
            "reservas": forms.RESERVA,
            "pendencias": _pendencias(edital),
        },
    )


def _reexibir_perfis(perfis):
    """Após erro, devolve o que a pessoa digitou — nunca o que estava salvo."""
    return [
        {
            **perfil,
            "requirements": "\n".join(perfil["requirements"]),
            "modalidades": "\n".join(
                f"{m['code']} — {m['name']}" for m in perfil["competitionModalities"]
            ),
        }
        for perfil in perfis
    ]


def _reexibir_eventos(eventos):
    return [
        {**evento,
         "startAt": evento["startAt"].strftime("%Y-%m-%dT%H:%M") if evento["startAt"] else "",
         "endAt": evento["endAt"].strftime("%Y-%m-%dT%H:%M") if evento["endAt"] else ""}
        for evento in eventos
    ]


@require_http_methods(["GET"])
def fragmento_perfil(request):
    return render(request, "interface/_perfil.html",
                  {"perfil": {"id": str(uuid4()), "reserveType": "NONE"},
                   "indice": request.GET.get("indice", "0"), "reservas": forms.RESERVA})


@require_http_methods(["GET"])
def fragmento_evento(request):
    return render(request, "interface/_evento.html",
                  {"evento": {"id": str(uuid4())}, "indice": request.GET.get("indice", "0")})


@require_http_methods(["GET"])
def fragmento_remover(request):
    """A linha removida é substituída por nada; o conteúdo digitado some junto."""
    return HttpResponse("")
