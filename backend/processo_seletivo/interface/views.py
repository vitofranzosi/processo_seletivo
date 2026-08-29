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
from processo_seletivo.interface import atos, forms, identidade
from processo_seletivo.processos.application.selectors import (
    contar_por_situacao,
    listar_processos,
    obter_edital,
)
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from processo_seletivo.publicacoes.application.selectors import (
    impede_por_segregacao,
    participantes_do_edital,
)
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
ROTA_PADRAO = "interface:detalhe"


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


# O wizard só tem as etapas que o domínio sustenta. Identificação é leitura porque não há
# command que altere título ou descrição depois da criação — ver ETAPAS_SEM_BACKEND no plano.
ETAPAS_COMPOSICAO = [
    ("identificacao", "Identificação", "interface/compor_identificacao.html"),
    ("perfis", "Perfis de Vaga", "interface/compor_perfis.html"),
    ("cronograma", "Cronograma", "interface/compor_cronograma.html"),
    ("revisao", "Revisão", "interface/compor_revisao.html"),
]
CHAVES_ETAPA = [chave for chave, _, _ in ETAPAS_COMPOSICAO]


def _progresso(edital, atual):
    """Cada etapa sabe se já está resolvida — o que orienta quem retoma o trabalho depois."""
    concluidas = {
        "identificacao": True,
        "perfis": edital.perfis.exists(),
        "cronograma": bool(
            getattr(edital, "cronograma", None) and edital.cronograma.eventos.exists()
        ),
        "revisao": False,
    }
    return [
        {
            "chave": chave,
            "rotulo": rotulo,
            "numero": indice + 1,
            "atual": chave == atual,
            "concluida": concluidas[chave] and chave != atual,
        }
        for indice, (chave, rotulo, _) in enumerate(ETAPAS_COMPOSICAO)
    ]


def _vizinhas(atual):
    indice = CHAVES_ETAPA.index(atual)
    return (
        CHAVES_ETAPA[indice - 1] if indice > 0 else None,
        CHAVES_ETAPA[indice + 1] if indice + 1 < len(CHAVES_ETAPA) else None,
    )


@require_http_methods(["GET"])
def compor(request, edital_id):
    return redirect(reverse("interface:compor-etapa", args=[edital_id, CHAVES_ETAPA[0]]))


@require_http_methods(["GET", "POST"])
def compor_etapa(request, edital_id, etapa):
    """Composição em etapas (US2 e US3 da 002), no formato de assistente guiado."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    if etapa not in CHAVES_ETAPA:
        raise Http404
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404

    editavel = edital.status == Edital.Status.EM_ELABORACAO and ator.can("edital:elaborar")
    anterior, proxima = _vizinhas(etapa)
    erros, digitados = [], None

    if request.method == "POST" and etapa in {"perfis", "cronograma"}:
        if not editavel:
            erros.append(
                "Este Edital não está em elaboração ou você não tem permissão para editá-lo."
            )
        else:
            try:
                # A leitura acontece antes da gravação para que o digitado sobreviva à recusa.
                digitados = _ler_etapa(request, etapa)
            except ValueError as exc:
                erros.append(str(exc))
            else:
                try:
                    _gravar_etapa(request, ator, edital, etapa, digitados)
                    destino = request.POST.get("destino") or etapa
                    return redirect(
                        f"{reverse('interface:compor-etapa', args=[edital.id, destino])}?salvo=1"
                    )
                except DomainError as exc:
                    erros.append(exc.detail)
        edital.refresh_from_db()

    _, _, template = ETAPAS_COMPOSICAO[CHAVES_ETAPA.index(etapa)]
    return render(
        request,
        template,
        {
            "edital": edital,
            "etapa": etapa,
            "progresso": _progresso(edital, etapa),
            "anterior": anterior,
            "proxima": proxima,
            "editavel": editavel,
            "erros": erros,
            "salvo": request.GET.get("salvo") == "1",
            "perfis": (
                _reexibir_perfis(digitados)
                if etapa == "perfis" and digitados is not None
                else forms.perfis_do_edital(edital)
            ),
            "eventos": (
                _reexibir_eventos(digitados)
                if etapa == "cronograma" and digitados is not None
                else forms.eventos_do_edital(edital)
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
        {
            **evento,
            "startAt": evento["startAt"].strftime("%Y-%m-%dT%H:%M") if evento["startAt"] else "",
            "endAt": evento["endAt"].strftime("%Y-%m-%dT%H:%M") if evento["endAt"] else "",
        }
        for evento in eventos
    ]


def _ler_etapa(request, etapa):
    return forms.ler_perfis(request.POST) if etapa == "perfis" else forms.ler_eventos(request.POST)


def _gravar_etapa(request, ator, edital, etapa, digitados):
    """Grava uma seção preservando a outra: replace_draft substitui o rascunho inteiro."""
    if etapa == "perfis":
        perfis, eventos = digitados, forms.eventos_persistidos(edital)
    else:
        perfis, eventos = forms.perfis_persistidos(edital), digitados
    replace_draft(
        actor=ator,
        edital_id=edital.id,
        expected_revision=edital.revision,
        profiles=perfis,
        schedule=eventos,
        correlation_id=request.correlation_id,
    )


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


ETAPAS = [
    ("EM_ELABORACAO", "Em elaboração"),
    ("EM_REVISAO", "Em revisão"),
    ("HOMOLOGADO", "Homologado"),
    ("PUBLICADO", "Publicado"),
    ("ENCERRADO", "Encerrado"),
]


def _trilha(edital):
    """Onde o Edital está no fluxo ordinário. Cancelado sai da trilha, não avança nela."""
    if edital.status == "CANCELADO":
        return [{"chave": c, "rotulo": r, "estado": "fora"} for c, r in ETAPAS]
    atual = [c for c, _ in ETAPAS].index(edital.status)
    return [
        {
            "chave": chave,
            "rotulo": rotulo,
            "estado": "concluida" if i < atual else "atual" if i == atual else "futura",
        }
        for i, (chave, rotulo) in enumerate(ETAPAS)
    ]


@require_http_methods(["GET"])
def detalhe(request, edital_id):
    """Situação do Edital, quem já atuou e o que se pode fazer agora (US3 da 002)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404

    participantes = participantes_do_edital(edital)
    return render(
        request,
        "interface/detalhe.html",
        {
            "edital": edital,
            "trilha": _trilha(edital),
            "participantes": participantes,
            "pendencias": _pendencias(edital),
            "atos": list(atos.disponiveis(edital, ator)),
            "impedido_por_segregacao": impede_por_segregacao(participantes, ator),
            "pode_compor": edital.status == Edital.Status.EM_ELABORACAO
            and ator.can("edital:elaborar"),
        },
    )


@require_http_methods(["GET", "POST"])
def praticar_ato(request, edital_id, acao):
    """FR-010: nenhum ato irreversível ocorre sem confirmação que diga o que ele provoca."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = obter_edital(actor=ator, edital_id=edital_id)
    ato = atos.ATOS.get(acao)
    if edital is None or ato is None:
        raise Http404

    participantes = participantes_do_edital(edital)
    contexto = {
        "edital": edital,
        "ato": ato,
        "participantes": participantes,
        "impedido_por_segregacao": ato.chave == "publicar"
        and impede_por_segregacao(participantes, ator),
        "pendencias": _pendencias(edital) if ato.chave in {"submeter", "publicar"} else [],
        # A chave nasce aqui: confirmar duas vezes repete o mesmo ato, não pratica dois.
        "chave_idempotencia": request.POST.get("chave_idempotencia") or f"ui-{uuid4().hex}",
    }

    if request.method == "GET":
        return render(request, "interface/confirmar.html", contexto)

    try:
        _executar(ato, request, ator, edital)
    except DomainError as exc:
        contexto["erro"] = exc.detail
        return render(request, "interface/confirmar.html", contexto, status=exc.status)
    return redirect(f"{reverse('interface:detalhe', args=[edital.id])}?ato={ato.chave}")


def _executar(ato, request, ator, edital):
    argumentos = {
        "actor": ator,
        "edital_id": edital.id,
        "expected_revision": edital.revision,
        "idempotency_key": request.POST.get("chave_idempotencia", ""),
        "correlation_id": request.correlation_id,
    }
    if ato.exige_motivo:
        motivo = (request.POST.get("motivo") or "").strip()
        if not motivo:
            raise DomainError("motivo_obrigatorio", f"{ato.rotulo_motivo} é obrigatório.", 422)
        argumentos["reason"] = motivo
    if ato.exige_signatario:
        argumentos["signatory"] = {
            "authorityId": (request.POST.get("signatario_id") or "").strip(),
            "name": (request.POST.get("signatario_nome") or "").strip(),
            "role": (request.POST.get("signatario_cargo") or "").strip(),
        }
        if not all(argumentos["signatory"].values()):
            raise DomainError(
                "signatario_obrigatorio",
                "Autoridade Signatária, nome e cargo são obrigatórios para publicar.",
                422,
            )
        argumentos["reason"] = (request.POST.get("motivo") or "").strip()
    return ato.command(**argumentos)
