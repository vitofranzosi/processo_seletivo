"""Views da interface administrativa.

Cada view invoca a camada de aplicação — nunca modelos direto, nunca a própria API por HTTP.
A decisão de autorização continua no backend: ocultar uma ação na tela é conveniência, não
fronteira de segurança (FR-002).
"""

import secrets
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods

from processo_seletivo.auditoria import selectors as auditoria_selectors
from processo_seletivo.editais.application.draft import replace_draft
from processo_seletivo.editais.application.identificacao import update_edital_identification
from processo_seletivo.editais.domain.validation import validate_for_publication
from processo_seletivo.interface import (
    atos,
    atos_processo,
    atos_retificacao,
    forms,
    identidade,
)
from processo_seletivo.interface import retificacao as retificacao_ui
from processo_seletivo.processos.application.commands import create_process_with_first_edital
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
from processo_seletivo.publicacoes.infrastructure.pdf import MODO_PREVIA, render_edital_pdf
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
def criar_processo(request):
    """FR-025 da 003 — FR-004 da 002 estava especificado e o botão apontava para `#`.

    Processo e primeiro Edital nascem juntos porque o domínio não admite um sem o outro. A view
    traduz o formulário e delega ao command, que é quem verifica permissão, unicidade e auditoria.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))

    contexto = {
        "digitado": request.POST if request.method == "POST" else {},
        "ano_corrente": timezone.localtime().year,
        # A chave atravessa o reenvio do formulário: recarregar depois de um erro de preenchimento
        # não pode criar dois Processos quando a segunda tentativa der certo.
        "chave_idempotencia": request.POST.get("chave_idempotencia") or f"ui-{uuid4().hex}",
    }
    if request.method == "GET":
        return render(request, "interface/processo_criar.html", contexto)

    try:
        processo, _ = create_process_with_first_edital(
            actor=ator,
            data=_processo_do_formulario(request.POST),
            idempotency_key=request.POST.get("chave_idempotencia", ""),
            correlation_id=request.correlation_id,
        )
    except ValueError as exc:
        contexto["erro"] = str(exc)
        return render(request, "interface/processo_criar.html", contexto, status=422)
    except DomainError as exc:
        contexto["erro"] = exc.detail
        return render(request, "interface/processo_criar.html", contexto, status=exc.status)
    return redirect(reverse("interface:processo-detalhe", args=[processo.id]))


# (campo do formulário, rótulo, modelo, campo do modelo). O limite vem de `_meta` em vez de ser
# repetido aqui: campo maior que a coluna vira erro 500 no PostgreSQL, e um número copiado à mão
# se desatualiza em silêncio na primeira migration que mudar o tamanho.
TEXTOS_DA_CRIACAO = (
    ("codigo", "Identificação institucional", ProcessoSeletivo, "institutional_code"),
    ("titulo", "Título do Processo", ProcessoSeletivo, "title"),
    ("numero", "Número do Edital", Edital, "number"),
    ("titulo_edital", "Título do Edital", Edital, "title"),
)
ANO_MINIMO, ANO_MAXIMO = 2000, 9999


def _processo_do_formulario(dados):
    """Traduz o formulário e recusa o que a persistência não aguentaria (FR-020/SC-007).

    A tela nova entrava direto no command, sem passar pelo serializer que a API usa: o que
    excedesse a coluna atravessava a borda e voltava como 500. Quem decide continua sendo o
    domínio; o que se faz aqui é não deixar o erro chegar ao banco sem forma.
    """
    campos = {
        "codigo": "Identificação institucional",
        "titulo": "Título do Processo",
        "numero": "Número do Edital",
        "ano": "Ano do Edital",
        "titulo_edital": "Título do Edital",
    }
    vazios = [rotulo for chave, rotulo in campos.items() if not (dados.get(chave) or "").strip()]
    if vazios:
        raise ValueError("Preencha: " + ", ".join(vazios) + ".")
    excedidos = [
        f"{rotulo} (máximo {modelo._meta.get_field(campo).max_length} caracteres)"
        for chave, rotulo, modelo, campo in TEXTOS_DA_CRIACAO
        if len(dados[chave].strip()) > modelo._meta.get_field(campo).max_length
    ]
    if excedidos:
        raise ValueError("Encurte: " + ", ".join(excedidos) + ".")
    try:
        ano = int(dados["ano"])
    except ValueError as exc:
        raise ValueError(f"'{dados['ano']}' não é um ano válido.") from exc
    if not ANO_MINIMO <= ano <= ANO_MAXIMO:
        raise ValueError(f"O ano do Edital deve estar entre {ANO_MINIMO} e {ANO_MAXIMO}.")
    return {
        "institutionalCode": dados["codigo"].strip(),
        "title": dados["titulo"].strip(),
        "firstEdital": {
            "number": dados["numero"].strip(),
            "year": ano,
            "title": dados["titulo_edital"].strip(),
            "description": (dados.get("descricao") or "").strip(),
        },
    }


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

# Onde cada achado do domínio se resolve: a etapa que trata aquele conteúdo, a âncora da seção
# dentro dela, e se a pessoa consegue de fato corrigi-lo ali. FR-027 pede a pendência ao lado do
# campo, e o domínio já diz de qual campo fala — a informação existia e era descartada na
# tradução para a tela.
#
# Para `profiles` e `schedule` a âncora é a seção, não um campo: a pendência é "não há nenhum", e
# o lugar de agir é o botão de acrescentar, dentro da seção.
#
# `title` e `description` passaram a ser corrigíveis: a etapa de Identificação deixou de ser
# somente leitura quando `update_edital_identification` nasceu (FR-006). Enquanto não havia o ato,
# o caminho terminava numa tela que não corrigia nada — pior do que não oferecer caminho.
DESTINO_DA_PENDENCIA = {
    "title": ("identificacao", "#ident-titulo", True),
    "description": ("identificacao", "#ident-titulo", True),
    "profiles": ("perfis", "#perfis-titulo", True),
    "schedule": ("cronograma", "#cronograma-titulo", True),
    "stages": ("etapas", "#etapas-titulo", True),
}


def _destino(caminho):
    """A etapa onde o achado se resolve.

    Achado de raiz vem com o nome da coleção (`profiles`); achado de forma vem com o caminho da
    entidade (`/profiles/id=…/name`). Os dois se resolvem no mesmo lugar, e resolver só o primeiro
    faria a pendência mais específica — a que já diz qual campo corrigir — ser a única sem caminho.
    """
    if caminho in DESTINO_DA_PENDENCIA:
        return DESTINO_DA_PENDENCIA[caminho]
    colecao = caminho.split("/")[1] if caminho.startswith("/") else ""
    return DESTINO_DA_PENDENCIA.get(colecao, (None, "", False))
# Caminho que a tradução não conhece — os da forma publicada, por exemplo — não ganha destino nem
# explicação inventada. FR-007 proíbe declarar incorrigível o que a etapa resolve; não obriga a
# justificar o que ninguém mapeou.
MOTIVO_SEM_DESTINO = "não há etapa do assistente que trate deste conteúdo"


def _pendencias(edital):
    """FR-008 e FR-027: o que falta para submeter, e onde cada coisa se resolve."""
    rotulos = {chave: rotulo for chave, rotulo, _ in ETAPAS_COMPOSICAO}
    pendencias = []
    for item in validate_for_publication(edital_snapshot(edital)):
        etapa, ancora, corrigivel = _destino(item.path)
        pendencias.append(
            {
                "severidade": SEVERIDADE.get(str(item.severity), "informacao"),
                "mensagem": item.message,
                "campo": item.path,
                "etapa": etapa,
                "ancora": ancora,
                "corrigivel": corrigivel,
                "rotulo_etapa": rotulos.get(etapa, ""),
                "motivo": "" if corrigivel else MOTIVO_SEM_DESTINO,
            }
        )
    return pendencias


def _pendencias_da_etapa(pendencias, etapa):
    """As que a pessoa consegue resolver sem sair desta tela."""
    return [item for item in pendencias if item["etapa"] == etapa and item["corrigivel"]]


# O wizard só tem as etapas que o domínio sustenta. A Identificação era leitura porque nenhum
# command alterava título ou descrição depois da criação; com `update_edital_identification` ela
# passou a ser etapa como as outras.
ETAPAS_COMPOSICAO = [
    ("identificacao", "Identificação", "interface/compor_identificacao.html"),
    ("perfis", "Perfis de Vaga", "interface/compor_perfis.html"),
    ("cronograma", "Cronograma", "interface/compor_cronograma.html"),
    # Depois do Cronograma porque a Etapa referencia Evento dele: pedir o vínculo antes de existir
    # o que vincular seria oferecer uma lista vazia e chamá-la de escolha.
    ("etapas", "Etapas de Avaliação", "interface/compor_etapas.html"),
    ("revisao", "Revisão", "interface/compor_revisao.html"),
]
CHAVES_ETAPA = [chave for chave, _, _ in ETAPAS_COMPOSICAO]
# As que aceitam POST. `revisao` consolida e não grava.
ETAPAS_GRAVAVEIS = {"identificacao", "perfis", "cronograma", "etapas"}


def _progresso(edital, atual):
    """Cada etapa sabe se já está resolvida — o que orienta quem retoma o trabalho depois."""
    concluidas = {
        "identificacao": True,
        "perfis": edital.perfis.exists(),
        "cronograma": bool(
            getattr(edital, "cronograma", None) and edital.cronograma.eventos.exists()
        ),
        # Etapas são opcionais; "concluída" aqui quer dizer "já tem conteúdo", não "obrigatória".
        "etapas": edital.etapas.exists(),
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

    if request.method == "POST" and etapa in ETAPAS_GRAVAVEIS:
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
    pendencias = _pendencias(edital)
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
            "identificacao": (
                digitados
                if etapa == "identificacao" and digitados is not None
                else {"title": edital.title, "description": edital.description}
            ),
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
            "etapas_avaliacao": (
                _reexibir_etapas(digitados)
                if etapa == "etapas" and digitados is not None
                else forms.etapas_do_edital(edital)
            ),
            "reservas": forms.RESERVA,
            "pendencias": pendencias,
            # A tela de revisão mostra tudo; as demais, só o que se resolve nelas — pendência
            # exibida onde não há como agir vira ruído que a pessoa aprende a ignorar.
            "pendencias_aqui": _pendencias_da_etapa(pendencias, etapa),
        },
    )


def _reexibir_perfis(perfis):
    """Após erro, devolve o que a pessoa digitou — nunca o que estava salvo."""
    return [
        {
            **perfil,
            "requirements": "\n".join(perfil["requirements"]),
            "modalidades": [
                _reexibir_modalidade(modalidade)
                for modalidade in perfil["competitionModalities"]
            ],
        }
        for perfil in perfis
    ]


def _reexibir_modalidade(modalidade):
    regra = modalidade.get("normativeRule") or {}
    percentual = regra.get("percentage")
    return {
        "id": modalidade.get("id", ""),
        "code": modalidade.get("code", ""),
        "name": modalidade.get("name", ""),
        "description": modalidade.get("description", ""),
        "ruleId": regra.get("id", ""),
        "foundation": regra.get("foundation", ""),
        "version": regra.get("version", ""),
        "percentage": "" if percentual is None else f"{percentual:f}",
    }


def _reexibir_etapas(etapas):
    """Após erro, devolve o que a pessoa digitou — inclusive o valor que o domínio recusou."""
    return [
        {
            **etapa,
            "weight": "" if etapa["weight"] is None else f"{etapa['weight']:f}",
            "minimumScore": "" if etapa["minimumScore"] is None else f"{etapa['minimumScore']:f}",
            "scheduleEventId": etapa["scheduleEventId"] or "",
        }
        for etapa in etapas
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


# Qual coleção do rascunho cada etapa do assistente escreve.
COLECAO_DA_ETAPA = {"perfis": "profiles", "cronograma": "schedule", "etapas": "stages"}

LEITURA_DA_ETAPA = {
    "identificacao": forms.ler_identificacao,
    "perfis": forms.ler_perfis,
    "cronograma": forms.ler_eventos,
    "etapas": forms.ler_etapas,
}


def _ler_etapa(request, etapa):
    return LEITURA_DA_ETAPA[etapa](request.POST)


def _gravar_etapa(request, ator, edital, etapa, digitados):
    """Grava uma seção preservando a outra: replace_draft substitui o rascunho inteiro."""
    if etapa == "identificacao":
        # A identificação não é conteúdo do rascunho: tem ato próprio, com auditoria própria.
        return update_edital_identification(
            actor=ator,
            edital_id=edital.id,
            expected_revision=edital.revision,
            title=digitados["title"],
            description=digitados["description"],
            correlation_id=request.correlation_id,
        )
    # `replace_draft` substitui o rascunho inteiro: o que não for reenviado é apagado. Por isso as
    # três coleções viajam sempre, e só a da etapa atual vem do formulário.
    conteudo = {
        "profiles": forms.perfis_persistidos(edital),
        "schedule": forms.eventos_persistidos(edital),
        "stages": forms.etapas_persistidas(edital),
    }
    conteudo[COLECAO_DA_ETAPA[etapa]] = digitados
    return replace_draft(
        actor=ator,
        edital_id=edital.id,
        expected_revision=edital.revision,
        profiles=conteudo["profiles"],
        schedule=conteudo["schedule"],
        stages=conteudo["stages"],
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


@require_http_methods(["GET"])
def fragmento_modalidade(request, indice):
    """A linha nova nasce com **os dois** identificadores: o da modalidade e o da sua Regra.

    A gravação preserva o `id` recebido, e uma linha sem identidade não teria o que preservar. O da
    Regra nasce mesmo antes de a Regra existir, porque quem digitar o fundamento em seguida vai
    criá-la, e a identidade precisa estar no formulário nesse momento.

    `indice` é o do Perfil que contém a linha: os nomes dos campos são `modalidade-<perfil>-<n>-…`.
    """
    return render(
        request,
        "interface/_modalidade.html",
        {
            "modalidade": {"id": str(uuid4()), "ruleId": str(uuid4())},
            "indice": indice,
            "sub": _indice_de_linha(request),
        },
    )


@require_http_methods(["GET"])
def fragmento_etapa(request, edital_id):
    """A linha nova nasce com identidade, como as de Perfil e Evento.

    A gravação preserva o `id` recebido; sem gerá-lo aqui, a Etapa criada pela tela nasceria sem
    identidade e não haveria o que preservar. A rota é escopada ao Edital porque o vínculo com
    Evento precisa da lista de Eventos **daquele** Cronograma.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404
    return render(
        request,
        "interface/_etapa.html",
        {
            "etapa_linha": {"id": str(uuid4())},
            "indice": _indice_de_linha(request),
            "eventos": forms.eventos_do_edital(edital),
            "edital": edital,
        },
    )


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


# Onde a prévia faz sentido. Publicado tem documento de verdade, e oferecer uma prévia ao lado
# dele criaria dois documentos concorrentes para o mesmo conteúdo.
ESTADOS_COM_PREVIA = (
    Edital.Status.EM_ELABORACAO,
    Edital.Status.EM_REVISAO,
    Edital.Status.HOMOLOGADO,
)


@require_http_methods(["GET"])
def previa(request, edital_id):
    """O documento como ele ficará, sem praticar ato nenhum (US1).

    Não é command: não altera estado, não gera ato e não tem chave de idempotência. É leitura que
    compõe um documento a partir do snapshot atual — que nos três estados admitidos **é** o
    conteúdo que será publicado, porque depois da submissão o rascunho não é editável e a
    publicação já recusa divergência entre rascunho e revisão homologada. Uma segunda origem
    existiria para reproduzir o que a primeira já garante.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404
    if edital.status not in ESTADOS_COM_PREVIA:
        raise DomainError(
            "invalid_state",
            "A prévia existe enquanto o Edital está em elaboração, submetido ou homologado. "
            "Depois da publicação, o documento é o publicado.",
            409,
        )
    documento = render_edital_pdf(edital_snapshot(edital), "", modo=MODO_PREVIA)
    resposta = HttpResponse(documento, content_type="application/pdf")
    nome = f"previa-edital-{edital.number}-{edital.year}.pdf".replace("/", "-")
    resposta["Content-Disposition"] = f'inline; filename="{nome}"'
    return resposta


def _documentos_publicados(edital):
    """O documento de cada Publicação, na ordem, identificado pelo ato que o produziu (FR-002).

    **Nenhum é apresentado como vigente, e a omissão é a parte que importa.** A vigência pertence à
    Versão Consolidada (`publicacoes/application/selectors.py:26`), que não tem documento próprio; e
    uma Retificação pode ser publicada com vigência futura, de modo que a Publicação mais recente
    nem sempre é a que vigora. Rotular a última como vigente seria afirmar sobre o documento uma
    propriedade que ele não tem.
    """
    documentos = []
    for publicacao in edital.publicacoes.select_related("retificacao").order_by(
        "publication_order"
    ):
        retificacao = getattr(publicacao, "retificacao", None)
        documentos.append(
            {
                "ordem": publicacao.publication_order,
                "ato": "Retificação" if retificacao else "Publicação original",
                "retificacao_id": retificacao.id if retificacao else None,
                "publicada_em": publicacao.published_at,
                "url": reverse("public-document", args=[publicacao.id]),
            }
        )
    return documentos


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
            "documentos": _documentos_publicados(edital),
            "pendencias": _pendencias(edital),
            "atos": list(atos.disponiveis(edital, ator)),
            "impedido_por_segregacao": impede_por_segregacao(participantes, ator),
            "pode_compor": edital.status == Edital.Status.EM_ELABORACAO
            and ator.can("edital:elaborar"),
            "pode_visualizar": edital.status in ESTADOS_COM_PREVIA,
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


def _base_da_composicao(edital, dados):
    """A versão sobre a qual o formulário foi montado, e não a que estiver vigente agora.

    O formulário identifica seus campos por referência de posição — `g2c3` —, que só significa
    alguma coisa contra o conteúdo que a gerou. Resolver o POST contra a versão vigente do
    momento fazia a mesma referência apontar para outra entidade quando uma Publicação
    concorrente entrava no intervalo entre abrir a tela e confirmar: a pessoa editava o Perfil
    que viu e o ato saía sobre outro. Por isso a versão base atravessa o formulário e o POST
    volta a ela; quem publicou no intervalo é tratado pelas precondições da elaboração.
    """
    if dados is None:
        return _versao_vigente(edital)
    # No POST a versão é obrigatória, e não opcional com queda para a vigente: um formulário
    # antigo que não a envie resolveria as referências contra outro conteúdo, que é o defeito
    # que esta função existe para impedir.
    try:
        declarada = UUID(str(dados.get("base", "")))
    except ValueError:
        return None
    return VersaoConsolidada.objects.filter(edital=edital, pk=declarada).first()


@require_http_methods(["GET", "POST"])
def retificar(request, edital_id):
    """Compõe uma Retificação editando o conteúdo vigente (US4 da 002)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404
    dados = request.POST if request.method == "POST" else None
    base = _base_da_composicao(edital, dados)
    if base is None and dados is not None:
        # A versão declarada sumiu ou não é deste Edital: recompor sobre a vigente sem avisar
        # produziria alterações sobre um conteúdo que a pessoa não viu.
        raise DomainError(
            "base_desconhecida",
            "A versão sobre a qual esta Retificação estava sendo composta não está mais "
            "disponível. Abra a tela novamente para partir da versão vigente.",
            409,
        )
    if base is None or edital.status != Edital.Status.PUBLICADO:
        # O Edital existe e está no escopo de quem pediu; dizer "não encontrado" esconderia
        # a razão real. Retificação incide sobre o que já foi publicado.
        raise DomainError(
            "edital_nao_publicado",
            "Só é possível retificar um Edital publicado. Este ainda não foi.",
            409,
        )

    erros, resumo = [], []
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
                    nova, _ = create_retification(
                        actor=ator,
                        edital_id=edital.id,
                        data={
                            "baseSnapshotId": base.id,
                            "justification": (request.POST.get("justificativa") or "").strip(),
                            "changes": alteracoes,
                            **_vigencia(request.POST),
                        },
                        idempotency_key=request.POST.get("chave_idempotencia", ""),
                        correlation_id=request.correlation_id,
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
            # Nasce no primeiro GET e atravessa o resumo até a confirmação: reenviar o mesmo
            # formulário devolve a Retificação já criada em vez de criar uma segunda.
            "chave_idempotencia": request.POST.get("chave_idempotencia") or f"ui-{uuid4().hex}",
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
    "ALTERAR_IDENTIFICACAO": "Alteração da identificação",
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
