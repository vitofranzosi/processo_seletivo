"""Views da interface administrativa.

Cada view invoca a camada de aplicação — nunca modelos direto, nunca a própria API por HTTP.
A decisão de autorização continua no backend: ocultar uma ação na tela é conveniência, não
fronteira de segurança (FR-002).
"""

import secrets
from uuid import uuid4
from zoneinfo import ZoneInfo

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods

from processo_seletivo.auditoria import selectors as auditoria_selectors
from processo_seletivo.editais.application.draft import replace_draft
from processo_seletivo.editais.domain.validation import validate_for_publication
from processo_seletivo.interface import (
    atos,
    atos_processo,
    atos_retificacao,
    forms,
    identidade,
)
from processo_seletivo.interface import retificacao as retificacao_ui
from processo_seletivo.processos.application.selectors import (
    contar_por_situacao,
    listar_processos,
    obter_edital,
)
from processo_seletivo.processos.domain.finalizacao import pending_editais
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from processo_seletivo.publicacoes.application.retificacoes import create_retification
from processo_seletivo.publicacoes.application.selectors import (
    impede_por_segregacao,
    participantes_do_edital,
)
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.seguranca.application.authorization import require_permission
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
ROTA_DA_ACAO = {"Elaborar": "interface:compor", "Retificar": "interface:retificar"}
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


def _indice_de_linha(request):
    """Índice único dentro do formulário — duas linhas com o mesmo índice viram uma só ao ler.

    Nasce no servidor para que a página não dependa de `hx-vals='js:{...}'`, que exige o
    `allowEval` do HTMX e quebraria sob uma CSP que proíba `unsafe-eval`. Quem informar o
    próprio índice continua sendo atendido: é o que a restauração do rascunho local faz.
    """
    informado = request.GET.get("indice", "")
    return informado if informado.isdigit() else str(secrets.randbelow(10**15))


@require_http_methods(["GET"])
def fragmento_perfil(request):
    return render(request, "interface/_perfil.html",
                  {"perfil": {"id": str(uuid4()), "reserveType": "NONE"},
                   "indice": _indice_de_linha(request), "reservas": forms.RESERVA})


@require_http_methods(["GET"])
def fragmento_evento(request):
    return render(request, "interface/_evento.html",
                  {"evento": {"id": str(uuid4())}, "indice": _indice_de_linha(request)})


def _campos_de(definicoes):
    return [{"chave": chave, "rotulo": rotulo, "tipo": tipo} for chave, rotulo, tipo in definicoes]


@require_http_methods(["GET"])
def fragmento_retificacao_perfil(request):
    """Perfil a acrescentar por Retificação (US4). Só a linha; o que ela vira é decidido na
    composição por diferença, ao comparar com o conteúdo vigente."""
    return render(request, "interface/_retificacao_perfil.html",
                  {"indice": _indice_de_linha(request),
                   "campos": _campos_de(retificacao_ui.NOVO_PERFIL)})


@require_http_methods(["GET"])
def fragmento_retificacao_evento(request):
    return render(request, "interface/_retificacao_evento.html",
                  {"indice": _indice_de_linha(request),
                   "campos": _campos_de(retificacao_ui.NOVO_EVENTO)})


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
            "pode_auditar": ator.can("auditoria:consultar"),
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
    segregacao = ato.chave == "publicar" and impede_por_segregacao(participantes, ator)
    pendencias = _pendencias(edital) if ato.chave in {"submeter", "publicar"} else []
    # Alcançável por URL direta: sem isto a tela oferece "Confirmar" para um ato que o
    # command recusaria, e a recusa só apareceria depois do clique.
    impedimento = atos.impedimento(edital, ator, ato)
    contexto = {
        "edital": edital,
        "ato": ato,
        "participantes": participantes,
        "impedido_por_segregacao": segregacao,
        "pendencias": pendencias,
        "impedimento": impedimento,
        # As três previsões usam exatamente o que o command aplica — a mesma
        # `validate_for_publication`, a mesma regra de segregação —, então dizer que o ato será
        # recusado e ainda oferecer o botão só adia a recusa para depois do clique.
        "recusa_certa": bool(impedimento)
        or segregacao
        or any(item["severidade"] == "erro" for item in pendencias),
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


def _versao_vigente(edital):
    return (
        VersaoConsolidada.objects.filter(edital=edital)
        .order_by("-valid_from", "-materialized_at")
        .first()
    )


@require_http_methods(["GET", "POST"])
def retificar(request, edital_id):
    """Compõe uma Retificação editando o conteúdo vigente (US4 da 002)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404
    base = _versao_vigente(edital)
    if base is None or edital.status != Edital.Status.PUBLICADO:
        # O Edital existe e está no escopo de quem pediu; dizer "não encontrado" esconderia
        # a razão real. Retificação incide sobre o que já foi publicado.
        raise DomainError(
            "edital_nao_publicado",
            "Só é possível retificar um Edital publicado. Este ainda não foi.",
            409,
        )

    erros, resumo, dados = [], [], request.POST if request.method == "POST" else None
    if request.method == "POST":
        if not ator.can("retificacao:elaborar"):
            erros.append("Você não tem a permissão para elaborar Retificações.")
        else:
            try:
                alteracoes, resumo = retificacao_ui.diferencas(base.content, request.POST)
                if not alteracoes:
                    erros.append(
                        "Nenhum campo foi alterado. Uma Retificação precisa mudar algum "
                        "conteúdo para ter efeito."
                    )
                elif request.POST.get("confirmar") == "1":
                    nova = create_retification(
                        actor=ator,
                        edital_id=edital.id,
                        data={
                            "baseSnapshotId": base.id,
                            "justification": (request.POST.get("justificativa") or "").strip(),
                            "changes": alteracoes,
                            **_vigencia(request.POST),
                        },
                    )
                    return redirect(reverse("interface:retificacao-detalhe", args=[nova.id]))
            except ValueError as exc:
                erros.append(str(exc))
            except DomainError as exc:
                erros.append(exc.detail)

    return render(
        request,
        "interface/retificar.html",
        {
            "edital": edital,
            "base": base,
            "grupos": retificacao_ui.campos_editaveis(base.content),
            "digitado": dados,
            # As linhas acrescentadas nascem no cliente, mas precisam voltar do servidor depois
            # do POST: sem isto, ver o resumo devolve um formulário sem elas.
            "novos_perfis": retificacao_ui.novas_para_formulario(
                dados or {}, "perfil", retificacao_ui.NOVO_PERFIL
            ),
            "novos_eventos": retificacao_ui.novas_para_formulario(
                dados or {}, "evento", retificacao_ui.NOVO_EVENTO
            ),
            "resumo": resumo,
            "erros": erros,
            "justificativa": (request.POST.get("justificativa") or "") if dados else "",
            "vigencia": (request.POST.get("vigencia") or "") if dados else "",
            "pode_elaborar": ator.can("retificacao:elaborar"),
        },
    )


def _vigencia(dados):
    bruto = (dados.get("vigencia") or "").strip()
    if not bruto:
        return {}
    momento = parse_datetime(bruto)
    if momento is None:
        raise ValueError(f"'{bruto}' não é uma data e hora válidas.")
    if timezone.is_naive(momento):
        momento = momento.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
    return {"effectiveAt": momento}


@require_http_methods(["GET"])
def retificacao_detalhe(request, retificacao_id):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    item = _retificacao_do_ator(ator, retificacao_id)
    return render(
        request,
        "interface/retificacao_detalhe.html",
        {
            "retificacao": item,
            "edital": item.edital,
            "alteracoes": _alteracoes_legiveis(item),
            "atos": list(atos_retificacao.disponiveis(item, ator)),
            "vigencia": item.effective_at,
            "publicada": item.publication,
        },
    )


def _retificacao_do_ator(ator, retificacao_id):
    item = (
        Retificacao.objects.filter(
            pk=retificacao_id, edital__institution_scope=ator.institution_scope
        )
        .select_related("edital__processo", "publication", "base_snapshot")
        .prefetch_related("alteracoes")
        .first()
    )
    if item is None:
        raise Http404
    return item


def _resumo_de_linha(valor):
    """Perfil e Evento inteiros são ilegíveis como dicionário; o que identifica basta."""
    if not isinstance(valor, dict):
        return valor
    for chave in ("code", "type", "name", "description"):
        if valor.get(chave):
            return valor[chave]
    return "—"


def _alteracoes_legiveis(retificacao):
    """Antes e depois de cada caminho alterado, lidos do snapshot que serviu de base.

    Acréscimo não tem antes — `/profiles/-` é a posição de acréscimo, e nada existe ali.
    Remoção não tem depois: o que havia sai do Edital.
    """
    base = retificacao.base_snapshot.content
    legiveis = []
    for alteracao in retificacao.alteracoes.all():
        anterior = retificacao_ui._ler(base, alteracao.target_path)
        removendo = alteracao.operation == "REMOVE"
        legiveis.append(
            {
                "caminho": alteracao.target_path,
                "operacao": alteracao.operation,
                "antes": _resumo_de_linha(anterior) if anterior is not None else "—",
                "depois": "removido do Edital"
                if removendo
                else _resumo_de_linha(alteracao.new_value)
                if alteracao.new_value is not None
                else "—",
            }
        )
    return legiveis


@require_http_methods(["GET", "POST"])
def praticar_ato_retificacao(request, retificacao_id, acao):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    item = _retificacao_do_ator(ator, retificacao_id)
    ato = atos_retificacao.ATOS.get(acao)
    if ato is None:
        raise Http404

    impedimento = atos_retificacao.impedimento(item, ator, ato)
    contexto = {
        "retificacao": item,
        "edital": item.edital,
        "ato": ato,
        "alteracoes": _alteracoes_legiveis(item),
        "impedimento": impedimento,
        "recusa_certa": bool(impedimento),
        "vigencia": item.effective_at,
        "chave_idempotencia": request.POST.get("chave_idempotencia") or f"ui-{uuid4().hex}",
    }
    if request.method == "GET":
        return render(request, "interface/retificacao_confirmar.html", contexto)

    try:
        if ato.exige_motivo and not (request.POST.get("motivo") or "").strip():
            raise DomainError("motivo_obrigatorio", f"{ato.rotulo_motivo} é obrigatório.", 422)
        signatario = None
        if ato.exige_signatario:
            signatario = {
                "authorityId": (request.POST.get("signatario_id") or "").strip(),
                "name": (request.POST.get("signatario_nome") or "").strip(),
                "role": (request.POST.get("signatario_cargo") or "").strip(),
            }
            if not all(signatario.values()):
                raise DomainError(
                    "signatario_obrigatorio",
                    "Autoridade Signatária, nome e cargo são obrigatórios para publicar.",
                    422,
                )
        atos_retificacao.executar(ato, request, ator, item, signatario)
    except DomainError as exc:
        contexto["erro"] = exc.detail
        return render(request, "interface/retificacao_confirmar.html", contexto, status=exc.status)
    return redirect(f"{reverse('interface:retificacao-detalhe', args=[item.id])}?ato={ato.chave}")


# Como cada operação auditada é lida por quem responde um questionamento.
OPERACOES = {
    "CRIAR": "Criação",
    "ALTERAR_RASCUNHO": "Alteração do rascunho",
    "ATIVAR": "Ativação do Processo",
    "SUBMETER": "Submissão para revisão",
    "HOMOLOGAR": "Homologação",
    "REVOGAR_HOMOLOGACAO": "Revogação da homologação",
    "PUBLICAR": "Publicação",
    "ENCERRAR": "Encerramento",
    "CANCELAR": "Cancelamento",
    "DEVOLVER": "Devolução para elaboração",
}
AGREGADOS = {
    "ProcessoSeletivo": "Processo Seletivo",
    "Edital": "Edital",
    "Retificacao": "Retificação",
}


@require_http_methods(["GET"])
def auditoria(request, edital_id):
    """Trilha do Edital e de suas Retificações (US6 da 002)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404
    require_permission(ator, "auditoria:consultar")

    registros, proximo = auditoria_selectors.trilha_do_edital(
        actor=ator,
        edital=edital,
        cursor=request.GET.get("cursor"),
        limit=auditoria_selectors.parse_limit(request.GET.get("limit")),
    )
    return render(
        request,
        "interface/auditoria.html",
        {
            "edital": edital,
            "registros": [
                {
                    "quando": registro.occurred_at,
                    "ator": registro.actor_subject,
                    "operacao": OPERACOES.get(registro.operation, registro.operation),
                    "agregado": AGREGADOS.get(registro.aggregate_type, registro.aggregate_type),
                    "de": registro.previous_state,
                    "para": registro.new_state,
                    "motivo": registro.reason,
                    "correlacao": registro.correlation_id,
                }
                for registro in registros
            ],
            "proximo_cursor": proximo,
        },
    )


ETAPAS_PROCESSO = [
    ("EM_ELABORACAO", "Em elaboração"),
    ("ATIVO", "Ativo"),
    ("ENCERRADO", "Encerrado"),
]


def _trilha_processo(processo):
    if processo.status == "CANCELADO":
        return [{"chave": c, "rotulo": r, "estado": "fora"} for c, r in ETAPAS_PROCESSO]
    atual = [c for c, _ in ETAPAS_PROCESSO].index(processo.status)
    return [
        {
            "chave": chave,
            "rotulo": rotulo,
            "estado": "concluida" if i < atual else "atual" if i == atual else "futura",
        }
        for i, (chave, rotulo) in enumerate(ETAPAS_PROCESSO)
    ]


def _processo_do_ator(ator, processo_id):
    processo = (
        ProcessoSeletivo.objects.filter(
            pk=processo_id, institution_scope=ator.institution_scope
        )
        .prefetch_related("editais")
        .first()
    )
    if processo is None:
        raise Http404
    return processo


@require_http_methods(["GET"])
def processo_detalhe(request, processo_id):
    """Situação do Processo, seus Editais e os atos do ciclo de vida (US5 da 002)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    processo = _processo_do_ator(ator, processo_id)
    return render(
        request,
        "interface/processo_detalhe.html",
        {
            "processo": processo,
            "trilha": _trilha_processo(processo),
            "editais": processo.editais.order_by("year", "number"),
            "pendentes": pending_editais(processo),
            "atos": list(atos_processo.disponiveis(processo, ator)),
        },
    )


@require_http_methods(["GET", "POST"])
def praticar_ato_processo(request, processo_id, acao):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    processo = _processo_do_ator(ator, processo_id)
    ato = atos_processo.ATOS.get(acao)
    if ato is None:
        raise Http404

    pendentes = pending_editais(processo) if ato.depende_dos_editais else []
    impedimento = atos_processo.impedimento(processo, ator, ato)
    contexto = {
        "processo": processo,
        "ato": ato,
        # FR-018: o que impede é mostrado antes da tentativa, com caminho para cada pendência.
        "pendentes": pendentes,
        "impedimento": impedimento,
        "recusa_certa": bool(impedimento) or bool(pendentes),
        "chave_idempotencia": request.POST.get("chave_idempotencia") or f"ui-{uuid4().hex}",
    }
    if request.method == "GET":
        return render(request, "interface/processo_confirmar.html", contexto)

    try:
        motivo = (request.POST.get("motivo") or "").strip()
        if not motivo:
            raise DomainError("motivo_obrigatorio", f"{ato.rotulo_motivo} é obrigatório.", 422)
        ato.command(
            actor=ator,
            processo_id=processo.id,
            expected_revision=processo.revision,
            reason=motivo,
            idempotency_key=request.POST.get("chave_idempotencia", ""),
            correlation_id=request.correlation_id,
        )
    except DomainError as exc:
        contexto["erro"] = exc.detail
        contexto["pendentes"] = pending_editais(processo) if ato.depende_dos_editais else []
        return render(request, "interface/processo_confirmar.html", contexto, status=exc.status)
    return redirect(f"{reverse('interface:processo-detalhe', args=[processo.id])}?ato={ato.chave}")
