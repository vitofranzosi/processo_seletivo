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
from processo_seletivo.auditoria.application import record_event
from processo_seletivo.avaliacoes.application import distribuicao as distribuicao_app
from processo_seletivo.avaliacoes.application import selectors as avaliacao_selectors
from processo_seletivo.comissoes.application import alocacao as alocacao_app
from processo_seletivo.comissoes.application import comissao as comissao_app
from processo_seletivo.comissoes.application import selectors as comissao_selectors
from processo_seletivo.comissoes.domain.autorizacao import (
    pode_atuar_na_etapa,
    pode_gerir_comissao,
)
from processo_seletivo.comissoes.domain.etapas import etapa_vigente, evento_vigente
from processo_seletivo.editais.application.draft import replace_draft
from processo_seletivo.editais.application.identificacao import update_edital_identification
from processo_seletivo.editais.domain.validation import validate_for_publication
from processo_seletivo.inscricoes.application.consulta import (
    CONSULTAR,
    documento_para_consulta,
    inscricao_para_consulta,
    inscricoes_do_edital,
)
from processo_seletivo.interface import (
    acoes,
    atos,
    atos_processo,
    atos_retificacao,
    forms,
    identidade,
    revisao,
)
from processo_seletivo.interface import retificacao as retificacao_ui
from processo_seletivo.portal.arquivos import copia_verificada, entregar
from processo_seletivo.processos.application.commands import create_process_with_first_edital
from processo_seletivo.processos.application.selectors import (
    contar_por_situacao,
    listar_processos,
    obter_edital,
)
from processo_seletivo.processos.domain.finalizacao import pending_editais
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from processo_seletivo.publicacoes.application.retificacoes import (
    conteudo_base,
    create_retification,
)
from processo_seletivo.publicacoes.application.selectors import (
    impede_por_segregacao,
    participantes_do_edital,
)
from processo_seletivo.publicacoes.domain import autoridades
from processo_seletivo.publicacoes.infrastructure.pdf import MODO_PREVIA, render_edital_pdf
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.http import marcar_como_privada

# Ordem em que as situações aparecem: o fluxo do Edital, não a ordem alfabética.
ORDEM_SITUACAO = [
    "EM_ELABORACAO",
    "EM_REVISAO",
    "HOMOLOGADO",
    "PUBLICADO",
    "ENCERRADO",
    "CANCELADO",
]

# `ACOES_POR_SITUACAO` foi removido: era a segunda fonte de verdade que FR-023 proíbe, e ela **já
# divergia**. O mapa não conhecia `Cancelar`, então um gestor via a ação no detalhe do Edital e a
# listagem, ao lado, afirmava que não havia nenhuma — a mesma contradição do achado 08, um nível
# acima. `acoes.do_edital` é agora o único lugar que responde à pergunta.


@require_http_methods(["GET"])
def lista(request):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))

    processos = list(listar_processos(actor=ator))
    for processo in processos:
        for edital in processo.editais.all():
            # Sem pendências nem segregação: a listagem não as exibe, e prever recusa onde o
            # motivo não cabe transformaria a linha da tabela numa tela de detalhe. O conjunto é o
            # mesmo; o que muda é quanto dele a tela mostra.
            edital.acoes = [
                acao for acao in acoes.do_edital(edital, ator) if acao.chave != "auditoria"
            ]

    # A base contextual da 011: sem isto a tela decide só por `ator.permissions` e diz a quem
    # preside uma comissão que sua conta não possui papel algum.
    vinculos = {v.processo_id: v for v in comissao_selectors.comissoes_da_pessoa(ator)}
    for processo in processos:
        processo.vinculo = vinculos.get(processo.id)

    contagem = contar_por_situacao(processos)
    return render(
        request,
        "interface/lista.html",
        {
            "processos": processos,
            "vinculos": list(vinculos.values()),
            "total_editais": sum(contagem.values()),
            "resumo": [
                (situacao, contagem[situacao])
                for situacao in ORDEM_SITUACAO
                if situacao in contagem
            ],
            "pode_criar": ator.can("processo:criar"),
            # Quem preside uma comissão tem o que fazer, mesmo sem papel sistêmico.
            "sem_papel": not ator.permissions and not vinculos,
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
    except RecusaDoFormulario as exc:
        return render(
            request,
            "interface/processo_criar.html",
            _com_recusas(contexto, exc.recusas),
            status=422,
        )
    except ValueError as exc:
        # Recusa sem campo conhecido continua em texto: apontar um campo qualquer seria pior.
        return render(
            request,
            "interface/processo_criar.html",
            _com_recusas(contexto, [{"mensagem": str(exc), "ancora": ""}]),
            status=422,
        )
    except DomainError as exc:
        recusas = [{"mensagem": exc.detail, "ancora": CAMPO_DO_CONFLITO.get(exc.code, "")}]
        return render(
            request,
            "interface/processo_criar.html",
            _com_recusas(contexto, recusas),
            status=exc.status,
        )
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

# O campo a que cada recusa do domínio pertence, na criação. `edital_identifier_conflict` nasceu na
# `007` apontando o Edital; aqui a interface o leva até o controle que a pessoa precisa corrigir.
CAMPO_DO_CONFLITO = {
    "institutional_identifier_conflict": "codigo",
    "edital_identifier_conflict": "numero",
}


def _com_recusas(contexto, recusas):
    """O contexto com o resumo e o mapa por campo — a mesma forma das etapas do assistente."""
    return {
        **contexto,
        "erros": recusas,
        "recusas": {r["ancora"]: r["mensagem"] for r in recusas if r["ancora"]},
    }


class RecusaDoFormulario(ValueError):
    """Recusas da tela de criação, uma por campo.

    Existe para que o resumo possa ancorar e a mensagem aparecer junto do controle — o mesmo que
    as etapas do assistente fazem com as recusas do domínio.
    """

    def __init__(self, recusas):
        super().__init__("; ".join(item["mensagem"] for item in recusas))
        self.recusas = recusas


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
    # Uma recusa **por campo**, e não uma frase agregada (FR-033). "Preencha: A, B, C." obriga a
    # pessoa a reencontrar cada um dos três; com a recusa presa ao campo, o resumo leva até ele.
    recusas = [
        {"mensagem": f"{rotulo} é obrigatório.", "ancora": chave}
        for chave, rotulo in campos.items()
        if not (dados.get(chave) or "").strip()
    ]
    if recusas:
        raise RecusaDoFormulario(recusas)
    recusas = [
        {
            "mensagem": (
                f"{rotulo} excede o máximo de "
                f"{modelo._meta.get_field(campo).max_length} caracteres."
            ),
            "ancora": chave,
        }
        for chave, rotulo, modelo, campo in TEXTOS_DA_CRIACAO
        if len(dados[chave].strip()) > modelo._meta.get_field(campo).max_length
    ]
    if recusas:
        raise RecusaDoFormulario(recusas)
    try:
        ano = int(dados["ano"])
    except ValueError as exc:
        raise RecusaDoFormulario(
            [{"mensagem": f"'{dados['ano']}' não é um ano válido.", "ancora": "ano"}]
        ) from exc
    if not ANO_MINIMO <= ano <= ANO_MAXIMO:
        raise RecusaDoFormulario(
            [
                {
                    "mensagem": (f"O ano do Edital deve estar entre {ANO_MINIMO} e {ANO_MAXIMO}."),
                    "ancora": "ano",
                }
            ]
        )
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
        if subject:
            # Papel deixou de ser obrigatório com a 011: quem integra uma comissão pode não ter
            # capacidade sistêmica nenhuma — sua autorização vem do vínculo, objeto a objeto — e
            # ainda assim precisa entrar para ver `Minhas Etapas`. Exigir papel aqui tornava esse
            # ator, que é metade da feature, impossível de representar.
            identidade.identificar(request, subject=subject, papeis=papeis)
            return redirect(
                reverse("interface:lista") if papeis else reverse("interface:minhas-etapas")
            )
        return render(
            request,
            "interface/identificar.html",
            {"papeis": identidade.PAPEIS, "erro": "Informe um nome."},
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
    # A designação do período é achado sobre `/schedule`, mas se resolve na etapa `Inscrição`, que
    # é onde existe o controle. Chave exata, e por isso vence a busca por coleção logo abaixo —
    # mandar quem lê para o Cronograma seria mandá-lo a uma tela sem o que corrigir.
    "/schedule": ("inscricao", "#inscricao-periodo", True),
    "documentRequirements": ("inscricao", "#inscricao-documentos", True),
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
    # Depois dos Perfis, das Modalidades e do Cronograma: a designação do período escolhe um
    # Evento que precisa existir, e a aplicabilidade de cada documento referencia Perfil e
    # modalidade que precisam existir. Pedir antes seria oferecer listas vazias.
    ("inscricao", "Inscrição", "interface/compor_inscricao.html"),
    # Depois de tudo o que gera conteúdo: as seções textuais complementam o que o sistema já
    # sabe, e quem as redige precisa ver o que já está estruturado.
    ("conteudo", "Conteúdo", "interface/compor_conteudo.html"),
    ("revisao", "Revisão", "interface/compor_revisao.html"),
]
CHAVES_ETAPA = [chave for chave, _, _ in ETAPAS_COMPOSICAO]
# As que aceitam POST. `revisao` consolida e não grava.
ETAPAS_GRAVAVEIS = {"identificacao", "perfis", "cronograma", "etapas", "inscricao", "conteudo"}


# Três estados, e não dois (FR-040). O terceiro existe por um defeito preciso: `conteudo` era
# `True` fixo, porque as seções nascem com o texto do catálogo e, tecnicamente, nada falta — então
# um Edital recém-criado exibia o passo 5 como **concluído** sem que ninguém o tivesse aberto. O
# sistema afirmava que a pessoa fez algo que ela não fez.
#
# "Aberta" seria o critério errado e caro: exigiria persistir "esta pessoa visitou esta etapa", por
# Edital e por pessoa — estado novo, sem valor normativo, que ainda afirmaria revisão onde houve
# exibição. Gravar já é sinal, já existe e já é auditado.
PENDENTE, PRONTA, CONCLUIDA = "pendente", "pronta", "concluida"

ROTULO_DO_ESTADO = {
    PENDENTE: "pendente",
    PRONTA: "pronta para revisar",
    CONCLUIDA: "concluída",
}


# Prefixo do nome dos campos de cada etapa, para reconstruir o `id` do controle recusado.
PREFIXO_DA_ETAPA = {
    "perfis": "perfil",
    "cronograma": "evento",
    "etapas": "etapa",
    "inscricao": "documento",
}


def _recusa(exc, digitados, etapa):
    """A recusa do domínio, com a âncora do campo quando ele é conhecido (FR-033).

    O domínio nomeia o campo e a entidade; a interface sabe em que **linha** aquela entidade foi
    digitada. Juntando os dois sai o `id` do controle — `perfil-3-reserveLimit` —, que é o que a
    âncora do resumo e a marcação junto do campo precisam.

    Quando a recusa não pertence a campo nenhum — "o Edital deve possuir ao menos um Perfil" — a
    âncora fica vazia e o resumo a mostra como texto. Apontar um campo qualquer seria pior.
    """
    campo = getattr(exc, "campo", "")
    identidade = getattr(exc, "identidade", "")
    mensagem = getattr(exc, "detail", None) or str(exc)
    prefixo = PREFIXO_DA_ETAPA.get(etapa, "")
    if not (campo and identidade and prefixo):
        return {"mensagem": mensagem, "ancora": ""}

    # `digitados` é a lista de linhas na ordem em que o formulário as enviou; o índice do
    # formulário é o que compõe o `id` do controle. A etapa `Inscrição` envia duas coisas — a
    # designação do período e as linhas —, e são as linhas que têm campo a ancorar.
    linhas = digitados.get("documentos", []) if isinstance(digitados, dict) else (digitados or [])
    for indice, linha in enumerate(linhas):
        if str(linha.get("id", "")) == identidade:
            return {"mensagem": mensagem, "ancora": f"{prefixo}-{indice}-{campo}"}
    return {"mensagem": mensagem, "ancora": ""}


def _progresso(edital, atual):
    """Cada etapa sabe se já está resolvida — o que orienta quem retoma o trabalho depois."""
    estados = {
        "identificacao": CONCLUIDA,
        "perfis": CONCLUIDA if edital.perfis.exists() else PENDENTE,
        "cronograma": CONCLUIDA
        if getattr(edital, "cronograma", None) and edital.cronograma.eventos.exists()
        else PENDENTE,
        # Etapas são opcionais; "concluída" aqui quer dizer "já tem conteúdo", não "obrigatória".
        "etapas": CONCLUIDA if edital.etapas.exists() else PENDENTE,
        # `SecaoEdital` só tem linha depois da primeira edição — ausência de linha significa "texto
        # padrão do catálogo". Logo `exists()` responde exatamente "esta etapa já foi gravada",
        # sem custar estado novo.
        # Como `etapas`: o contrato de inscrição é opcional nesta versão — um Edital pode ser
        # publicado sem receber inscrições pelo sistema —, e "concluída" diz "já tem conteúdo".
        "inscricao": CONCLUIDA
        if edital.documentos_exigidos.exists() or forms.periodo_do_edital(edital)
        else PENDENTE,
        "conteudo": CONCLUIDA if edital.secoes.exists() else PRONTA,
        "revisao": PENDENTE,
    }
    return [
        {
            "chave": chave,
            "rotulo": rotulo,
            "numero": indice + 1,
            "atual": chave == atual,
            "estado": estados[chave],
            "rotulo_estado": ROTULO_DO_ESTADO[estados[chave]],
            # Preservado para quem já lia `concluida`: a etapa atual não se anuncia concluída.
            "concluida": estados[chave] == CONCLUIDA and chave != atual,
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
                {
                    "mensagem": (
                        "Este Edital não está em elaboração ou você não tem permissão "
                        "para editá-lo."
                    ),
                    "ancora": "",
                }
            )
        else:
            try:
                # A leitura acontece antes da gravação para que o digitado sobreviva à recusa.
                digitados = _ler_etapa(request, etapa)
            except ValueError as exc:
                erros.append(_recusa(exc, digitados, etapa))
            else:
                try:
                    _gravar_etapa(request, ator, edital, etapa, digitados)
                    destino = request.POST.get("destino") or etapa
                    # A etapa salva viaja na confirmação porque "Avançar" grava uma e abre outra:
                    # "Rascunho salvo" sozinho, na tela seguinte, dizia respeito à anterior.
                    return redirect(
                        f"{reverse('interface:compor-etapa', args=[edital.id, destino])}"
                        f"?salvo={etapa}"
                    )
                except DomainError as exc:
                    erros.append(_recusa(exc, digitados, etapa))
        edital.refresh_from_db()

    _, _, template = ETAPAS_COMPOSICAO[CHAVES_ETAPA.index(etapa)]
    pendencias = _pendencias(edital)
    # A conferência é lida do conteúdo canônico, e não montada bloco a bloco no template: é o que
    # impede a Revisão de envelhecer quando uma coleção nova entra no Edital.
    conferencia = revisao.blocos(edital_snapshot(edital)) if etapa == "revisao" else []
    return render(
        request,
        template,
        {
            "edital": edital,
            "etapa": etapa,
            # A outra metade de FR-033: a mensagem junto do campo, por `id` do controle.
            "recusas": {
                erro["ancora"]: erro["mensagem"]
                for erro in erros
                if isinstance(erro, dict) and erro.get("ancora")
            },
            "progresso": _progresso(edital, etapa),
            "anterior": anterior,
            "proxima": proxima,
            "editavel": editavel,
            "erros": erros,
            "salvo": dict((chave, rotulo) for chave, rotulo, _ in ETAPAS_COMPOSICAO).get(
                request.GET.get("salvo", "")
            ),
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
            # Após recusa, o que a pessoa digitou; fora disso, o que está gravado — a mesma regra
            # das demais etapas, e o que impede a recusa apagar o preenchimento.
            "documentos": (
                digitados["documentos"]
                if etapa == "inscricao" and digitados is not None
                else forms.documentos_do_edital(edital)
            ),
            "periodo_escolhido": (
                digitados["periodo"]
                if etapa == "inscricao" and digitados is not None
                else forms.periodo_do_edital(edital)
            ),
            "alcance": forms.alcance_da_aplicabilidade(edital) if etapa == "inscricao" else [],
            "etapas_avaliacao": (
                _reexibir_etapas(digitados)
                if etapa == "etapas" and digitados is not None
                else forms.etapas_do_edital(edital)
            ),
            "secoes": (
                _reexibir_secoes(edital, digitados)
                if etapa == "conteudo" and digitados is not None
                else forms.secoes_do_edital(edital)
            ),
            "reservas": forms.RESERVA,
            "conferencia": conferencia,
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
                _reexibir_modalidade(modalidade) for modalidade in perfil["competitionModalities"]
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


def _reexibir_secoes(edital, digitadas):
    """Após erro, o texto digitado por cima da estrutura do catálogo, que não vem do formulário."""
    texto = {item["key"]: item["content"] for item in digitadas}
    return [
        {**secao, "content": texto.get(secao["key"], secao["content"])}
        for secao in forms.secoes_do_edital(edital)
    ]


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
COLECAO_DA_ETAPA = {
    "perfis": "profiles",
    "cronograma": "schedule",
    "etapas": "stages",
    "conteudo": "sections",
}

LEITURA_DA_ETAPA = {
    "identificacao": forms.ler_identificacao,
    "perfis": forms.ler_perfis,
    "cronograma": forms.ler_eventos,
    "etapas": forms.ler_etapas,
    "inscricao": forms.ler_inscricao,
    "conteudo": forms.ler_secoes,
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
        "sections": forms.secoes_persistidas(edital),
        "documentRequirements": forms.documentos_persistidos(edital),
    }
    if etapa == "inscricao":
        # A única etapa que escreve em duas coleções, porque a designação do período mora **no**
        # Evento: para quem elabora é uma decisão só — como este Edital recebe inscrição —, e
        # separá-la em duas telas partiria o contrato ao meio.
        conteudo["documentRequirements"] = digitados["documentos"]
        conteudo["schedule"] = [
            {**evento, "isRegistrationPeriod": str(evento["id"]) == digitados["periodo"]}
            for evento in conteudo["schedule"]
        ]
    else:
        conteudo[COLECAO_DA_ETAPA[etapa]] = digitados
    return replace_draft(
        actor=ator,
        edital_id=edital.id,
        expected_revision=edital.revision,
        profiles=conteudo["profiles"],
        schedule=conteudo["schedule"],
        stages=conteudo["stages"],
        sections=conteudo["sections"],
        document_requirements=conteudo["documentRequirements"],
        correlation_id=request.correlation_id,
        # O rótulo da etapa, como quem elabora a vê no assistente (FR-042).
        area=dict((chave, rotulo) for chave, rotulo, _ in ETAPAS_COMPOSICAO).get(etapa, ""),
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
    return render(
        request,
        "interface/_perfil.html",
        {
            "perfil": {"id": str(uuid4()), "reserveType": "NONE"},
            "indice": _indice_de_linha(request),
            "reservas": forms.RESERVA,
        },
    )


@require_http_methods(["GET"])
def fragmento_evento(request):
    return render(
        request,
        "interface/_evento.html",
        {"evento": {"id": str(uuid4())}, "indice": _indice_de_linha(request)},
    )


@require_http_methods(["GET"])
def fragmento_documento(request, edital_id):
    """A linha nova de Documento Exigido.

    Escopada ao Edital, como a da Etapa: os dois `select` de aplicabilidade precisam dos Perfis e
    das modalidades **daquele** Edital para oferecer a escolha. Sem escopo, a linha nasceria com
    duas listas vazias e a restrição só poderia ser declarada recarregando a página.
    """
    ator = identidade.ator_da_sessao(request)
    edital = obter_edital(actor=ator, edital_id=edital_id) if ator else None
    if edital is None:
        raise Http404
    return render(
        request,
        "interface/_documento.html",
        {
            "documento": {"id": str(uuid4()), "required": True},
            "indice": _indice_de_linha(request),
            "alcance": forms.alcance_da_aplicabilidade(edital),
        },
    )


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
    return render(
        request,
        "interface/_retificacao_perfil.html",
        {"indice": _indice_de_linha(request), "campos": _campos_de(retificacao_ui.NOVO_PERFIL)},
    )


@require_http_methods(["GET"])
def fragmento_retificacao_evento(request):
    return render(
        request,
        "interface/_retificacao_evento.html",
        {"indice": _indice_de_linha(request), "campos": _campos_de(retificacao_ui.NOVO_EVENTO)},
    )


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


# `ESTADOS_COM_PREVIA` mora em `acoes`, junto de quem decide o que a tela oferece.
ESTADOS_COM_PREVIA = acoes.ESTADOS_COM_PREVIA


def _edital_com_previa(request, edital_id):
    """O Edital cuja prévia se pode ver, ou a recusa que explica por quê."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, redirect(reverse("interface:identificar"))
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
    return edital, None


# De onde a pessoa veio, para onde ela volta. Sem isto, "voltar" da prévia significava o botão do
# navegador — e, quando a prévia era um arquivo baixado, não significava nada.
ORIGEM_DA_PREVIA = {"revisao": "revisao", "conteudo": "conteudo", "etapas": "etapas"}

# O documento é o mesmo nos três estados; o que muda é o que quem lê está prestes a decidir.
ROTULO_DA_PREVIA = {
    Edital.Status.EM_ELABORACAO: "Ver o Edital",
    Edital.Status.EM_REVISAO: "Ver o Edital submetido",
    Edital.Status.HOMOLOGADO: "Ver o Edital homologado",
}


@require_http_methods(["GET"])
def previa(request, edital_id):
    """A prévia como **tela**, com o documento embutido e o caminho de volta visível.

    Entregar o PDF direto fazia o navegador tratá-lo como download: o ciclo de olhar e voltar a
    editar virava baixar, abrir noutro aplicativo e procurar a aba. FR-012 pede que se possa
    retornar e continuar editando, e não havia para onde retornar.

    O artefato continua sendo o mesmo PDF — não há representação paralela do documento.
    """
    edital, desvio = _edital_com_previa(request, edital_id)
    if desvio is not None:
        return desvio
    origem = ORIGEM_DA_PREVIA.get(request.GET.get("origem", ""))
    return render(
        request,
        "interface/previa.html",
        {
            "edital": edital,
            "voltar": reverse("interface:compor-etapa", args=[edital.id, origem])
            if origem
            else reverse("interface:detalhe", args=[edital.id]),
            "rotulo_voltar": "Voltar para a Revisão" if origem == "revisao" else "Voltar",
        },
    )


@require_http_methods(["GET"])
def previa_documento(request, edital_id):
    """Os bytes da prévia, para a tela embutir e para quem quiser abrir o arquivo.

    Não é command: não altera estado, não gera ato e não tem chave de idempotência. É leitura que
    compõe um documento a partir do snapshot atual — que nos três estados admitidos **é** o
    conteúdo que será publicado, porque depois da submissão o rascunho não é editável e a
    publicação já recusa divergência entre rascunho e revisão homologada. Uma segunda origem
    existiria para reproduzir o que a primeira já garante.
    """
    edital, desvio = _edital_com_previa(request, edital_id)
    if desvio is not None:
        return desvio
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
    pendencias = _pendencias(edital)
    segregacao = impede_por_segregacao(participantes, ator)
    # Um conjunto só (FR-023): a lista e a mensagem de ausência saem daqui, e a previsão de recusa
    # é a mesma que `praticar_ato` usa. Nada de `pode_compor`, `pode_visualizar` e `pode_auditar`
    # como bandeiras soltas — eram elas que o `{% empty %}` não enxergava.
    conjunto = acoes.do_edital(edital, ator, pendencias=pendencias, segregacao=segregacao)
    return render(
        request,
        "interface/detalhe.html",
        {
            "edital": edital,
            "trilha": _trilha(edital),
            "participantes": participantes,
            "documentos": _documentos_publicados(edital),
            "pendencias": pendencias,
            "acoes": conjunto,
            "impedido_por_segregacao": segregacao,
            "proximo_passo": acoes.proximo_passo(edital, ator, segregacao=segregacao),
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
        "pode_visualizar": edital.status in ESTADOS_COM_PREVIA,
        "rotulo_previa": ROTULO_DA_PREVIA.get(edital.status, "Ver o Edital"),
        # Passagem de bastão dita antes do ato (FR-028): quem submete está entregando a alguém.
        "entrega_para": acoes.entrega_para(ato),
        "autoridades": autoridades.CATALOGO,
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
        # A autoridade vem do catálogo declarado (FR-039). Nome, cargo e identificador saem da
        # entrada escolhida — nenhum deles é digitado, e o identificador não é sequer exibido.
        autoridade = autoridades.escolher(request.POST.get("signatario"))
        if autoridade is None:
            raise DomainError(
                "signatario_obrigatorio",
                "Escolha a Autoridade Signatária que assina este Edital.",
                422,
            )
        argumentos["signatory"] = {
            "authorityId": str(autoridade.identificador),
            "name": autoridade.nome,
            "role": autoridade.cargo,
        }
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

    # **A projeção que o autor compõe** (012, T-015). Quem escreve a Retificação vê o conteúdo na
    # forma vigente, e é dela que sai `expectedPreviousHash` — o hash "do conteúdo que o autor
    # encontrou". Servir a forma antiga aqui e conferir a nova na publicação faria o autor errar um
    # alvo que não lhe foi mostrado. Projetar não é persistir nem publicar: a linha continua como
    # está, e a leitura pública continua literal (T-002).
    projecao = conteudo_base(base)

    erros, resumo = [], []
    if request.method == "POST":
        if not ator.can("retificacao:elaborar"):
            erros.append("Você não tem a permissão para elaborar Retificações.")
        else:
            try:
                alteracoes, resumo = retificacao_ui.diferencas(projecao, request.POST)
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
            "grupos": retificacao_ui.reexibir(retificacao_ui.campos_editaveis(projecao), dados),
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
    base = conteudo_base(retificacao.base_snapshot)
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
        "autoridades": autoridades.CATALOGO,
    }
    if request.method == "GET":
        return render(request, "interface/retificacao_confirmar.html", contexto)

    try:
        if ato.exige_motivo and not (request.POST.get("motivo") or "").strip():
            raise DomainError("motivo_obrigatorio", f"{ato.rotulo_motivo} é obrigatório.", 422)
        signatario = None
        if ato.exige_signatario:
            # **São dois fluxos de publicação**, e o do Edital não é o único: corrigir um Edital
            # publicado passa por aqui. Deixar este de fora manteria o UUID digitado exatamente
            # onde a correção acontece (FR-039).
            autoridade = autoridades.escolher(request.POST.get("signatario"))
            if autoridade is None:
                raise DomainError(
                    "signatario_obrigatorio",
                    "Escolha a Autoridade Signatária que assina esta Retificação.",
                    422,
                )
            signatario = {
                "authorityId": str(autoridade.identificador),
                "name": autoridade.nome,
                "role": autoridade.cargo,
            }
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
    # Atos do candidato (009). Entram aqui porque a trilha é uma só: quem responde a um
    # questionamento sobre uma inscrição lê a mesma tela de quem responde sobre um Edital.
    "GRAVAR": "Preenchimento da inscrição",
    "ANEXAR": "Envio de documento",
    "REMOVER": "Remoção de documento",
    "INTEGRIDADE": "Falha de integridade de documento",
    "CONSULTAR_DOCUMENTO": "Consulta a documento do candidato",
    # A organização do trabalho (011). Mesma trilha, pela mesma razão: quem investiga quem
    # perdeu acesso a uma Etapa lê a mesma tela de quem investiga uma publicação.
    "COMISSAO_INCLUIR_MEMBRO": "Inclusão na comissão",
    "COMISSAO_ALTERAR_FUNCAO": "Alteração de função na comissão",
    "COMISSAO_REMOVER_MEMBRO": "Remoção da comissão",
    "ALOCACAO_INCLUIR": "Alocação em Etapa",
    "ALOCACAO_REMOVER": "Remoção de alocação",
}
AGREGADOS = {
    "ProcessoSeletivo": "Processo Seletivo",
    "Edital": "Edital",
    "Retificacao": "Retificação",
    "Inscricao": "Inscrição",
    "MembroComissao": "Membro da comissão",
    "AlocacaoEtapa": "Alocação em Etapa",
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
        ProcessoSeletivo.objects.filter(pk=processo_id, institution_scope=ator.institution_scope)
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
            "pode_auditar": ator.can("auditoria:consultar"),
            # FR-021: criado o Processo, o próximo passo é elaborar o Edital — e era só um link
            # discreto no número, enquanto o destaque ia para o impedimento de cancelar, ato que
            # ninguém tentou. O primeiro Edital em elaboração que este ator pode compor.
            "elaboravel": (
                processo.editais.filter(status=Edital.Status.EM_ELABORACAO)
                .order_by("year", "number")
                .first()
                if ator.can("edital:elaborar")
                else None
            ),
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


@require_http_methods(["GET"])
def inscricoes_recebidas(request, edital_id):
    """`Inscrições` no contexto do Edital (US6 da 009, FR-066, FR-067).

    A tela que substitui a planilha: quantas chegaram, de quem, para qual Perfil, e quantos
    documentos vieram dos que aquela inscrição exige. Nada de avaliação — a `009` termina em
    "recebido e consultável", e a próxima jornada é que transforma isso em avaliável.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital, linhas = inscricoes_do_edital(actor=ator, edital_id=edital_id)
    # Recebido é o que foi entregue. O rascunho continua na tela — em seção própria e sob o nome do
    # que é —, mas fora do total: contá-lo diria à gestão que recebeu inscrição que ninguém enviou.
    recebidas = [linha for linha in linhas if linha["enviada"]]
    return marcar_como_privada(
        render(
            request,
            "interface/inscricoes.html",
            {
                "edital": edital,
                "recebidas": recebidas,
                "em_preenchimento": [linha for linha in linhas if not linha["enviada"]],
                "total": len(recebidas),
            },
        )
    )


@require_http_methods(["GET"])
def inscricao_recebida(request, inscricao_id):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    contexto = inscricao_para_consulta(actor=ator, inscricao_id=inscricao_id)
    return marcar_como_privada(render(request, "interface/inscricao_detalhe.html", contexto))


@require_http_methods(["GET"])
def documento_da_inscricao(request, inscricao_id, requirement_id):
    """O documento apresentado, conferido **antes** de sair um byte (FR-053a, FR-069).

    A conferência não pode acontecer durante o streaming: uma vez enviados, os bytes não voltam, e
    descobrir a divergência no meio do arquivo deixaria a pessoa com meio documento e nenhuma
    explicação. Ler para conferir e depois servir custa uma leitura a mais por consulta — o preço
    de poder afirmar que o que a comissão abriu é o que o candidato enviou.

    `inline` para ver; `?baixar=1` para guardar. Baixar é ação secundária e individual: não existe
    download em lote, porque é dele que a feature existe para tirar a equipe (FR-069, FR-084).
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    documento = documento_para_consulta(
        actor=ator, inscricao_id=inscricao_id, requirement_id=requirement_id
    )
    # Uma passagem só: a cópia é conferida e é **ela** que vai para a resposta. Conferir o
    # arquivo e depois reabri-lo pelo caminho deixaria uma janela entre as duas leituras — e uma
    # verificação que aprova um conteúdo e serve outro é pior do que verificação nenhuma, porque
    # produz a afirmação de integridade que ninguém checou.
    copia, calculado = copia_verificada(documento)
    if calculado != documento.content_hash:
        copia.close()
        _registrar_divergencia(ator, documento, request)
    _registrar_consulta(ator, documento, request)
    return entregar(documento, anexo=bool(request.GET.get("baixar")), verificado=copia)


def _registrar_consulta(ator, documento, request):
    """Quem abriu o documento de quem, e quando (L10 da auditoria de percurso).

    FR-077 audita os atos do candidato e dispensa a consulta pública; sobre a consulta
    **administrativa** a spec é silenciosa, e o silêncio deixava o sistema sem resposta para a
    pergunta que uma auditoria de dados pessoais faz primeiro. Documento de candidato inclui
    autodeclaração étnico-racial: é dado sensível, e acesso a dado sensível deixa rastro.

    Registra a leitura, e não o conteúdo — nem o nome do arquivo, que é do candidato (FR-074). O
    requisito basta para saber o que foi aberto.
    """
    with command_context() as agora:
        record_event(
            actor=ator,
            permission=CONSULTAR,
            operation="CONSULTAR_DOCUMENTO",
            aggregate=documento.inscricao,
            now=agora,
            correlation_id=getattr(request, "correlation_id", ""),
            reason=f"requisito {documento.requirement_id}",
        )


def _registrar_divergencia(ator, documento, request):
    with command_context() as agora:
        record_event(
            actor=ator,
            permission=CONSULTAR,
            operation="INTEGRIDADE",
            aggregate=documento.inscricao,
            now=agora,
            correlation_id=getattr(request, "correlation_id", ""),
            reason=f"requisito {documento.requirement_id}",
        )
    raise DomainError(
        "document_integrity_failed",
        "O arquivo guardado não confere com o que foi recebido. O documento não pode ser "
        "apresentado como íntegro; registre a ocorrência e solicite novo envio ao candidato.",
        409,
    )


# ---------------------------------------------------------------------------
# A comissão e a alocação por Etapa (011).
#
# Duas portas, e elas não se misturam: `comissao` e `alocacoes` dependem de **gerir**;
# `minhas_etapas` e `minha_etapa` dependem de **atuar**. A página da Etapa aceita as duas e diz
# por qual delas o ator chegou (D-006).
# ---------------------------------------------------------------------------


def _processo_para_gerir(request, processo_id):
    """Processo, ator e base — ou 404 para tudo que este ator não alcança (D-017)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, None, None
    processo = _processo_do_ator(ator, processo_id)
    base = pode_gerir_comissao(ator, processo)
    if base is None:
        raise Http404
    return ator, processo, base


@require_http_methods(["GET", "POST"])
def comissao(request, processo_id):
    """Quem integra a comissão deste Processo (US1 e US2 da 011)."""
    ator, processo, _ = _processo_para_gerir(request, processo_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))

    erro = None
    if request.method == "POST":
        acao = (request.POST.get("acao") or "").strip()
        dados = forms.ler_membro(request.POST)
        chave = request.POST.get("chave_idempotencia") or uuid4().hex
        try:
            if acao == "incluir":
                # FR-022: o primeiro envio não grava — devolve a conferência do identificador.
                if not request.POST.get("confirmado"):
                    return render(
                        request,
                        "interface/comissao_confirmar.html",
                        {
                            "processo": processo,
                            "membro": dados,
                            "chave_idempotencia": chave,
                        },
                    )
                comissao_app.adicionar_membro(
                    actor=ator,
                    processo_id=processo.id,
                    identity_subject=dados["identity_subject"],
                    display_label=dados["display_label"],
                    funcao=dados["funcao"],
                    idempotency_key=chave,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
            elif acao == "incluir_lote":
                lote = forms.ler_membros_em_lote(request.POST)
                # A conferência confere a lista inteira: sem diretório, ela é a única defesa
                # contra o identificador errado — e conferir quarenta um a um não é conferir.
                if not request.POST.get("confirmado"):
                    if not lote["entradas"]:
                        raise DomainError(
                            "identificador_ausente",
                            "Informe ao menos um identificador institucional.",
                            422,
                        )
                    ja = {m.identity_subject for m in comissao_selectors.membros(processo)}
                    return render(
                        request,
                        "interface/comissao_confirmar.html",
                        {
                            "processo": processo,
                            "lote": [
                                {
                                    "identity_subject": subject,
                                    "display_label": rotulo,
                                    "ja_integra": subject in ja,
                                }
                                for subject, rotulo in lote["entradas"]
                            ],
                            "funcao": lote["funcao"],
                            "lista": lote["lista"],
                            "chave_idempotencia": chave,
                        },
                    )
                comissao_app.adicionar_varios(
                    actor=ator,
                    processo_id=processo.id,
                    entradas=lote["entradas"],
                    funcao=lote["funcao"],
                    idempotency_key=chave,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
            elif acao == "alterar_funcao":
                comissao_app.alterar_funcao(
                    actor=ator,
                    processo_id=processo.id,
                    membro_id=request.POST.get("membro_id"),
                    funcao=dados["funcao"],
                    idempotency_key=chave,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
            elif acao == "remover":
                comissao_app.remover_membro(
                    actor=ator,
                    processo_id=processo.id,
                    membro_id=request.POST.get("membro_id"),
                    idempotency_key=chave,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
            return redirect(f"{reverse('interface:comissao', args=[processo.id])}?feito={acao}")
        except DomainError as recusa:
            if recusa.status == 404:
                raise Http404 from recusa
            erro = recusa.detail

    membros = comissao_selectors.membros(processo)
    # Em lote: por membro, a leitura custava cinco consultas, e a tela não terminava numa
    # comissão do tamanho que mil candidatos exigem.
    por_membro = comissao_selectors.etapas_por_membro(processo)
    total = len(membros)
    busca = (request.GET.get("q") or "").strip()
    so_sem_etapa = request.GET.get("sem_etapa") == "1"
    linhas = [{"membro": m, "etapas": por_membro.get(m.id, [])} for m in membros]
    sem_etapa = sum(1 for linha in linhas if not linha["etapas"])
    # Filtrar em memória: a lista já foi lida inteira para contar, e uma banca cabe na memória
    # com folga — o que não cabe é a pessoa rolando cento e vinte cartões atrás de um nome.
    if busca:
        alvo = busca.casefold()
        linhas = [
            linha
            for linha in linhas
            if alvo in linha["membro"].identity_subject.casefold()
            or alvo in (linha["membro"].display_label or "").casefold()
        ]
    if so_sem_etapa:
        linhas = [linha for linha in linhas if not linha["etapas"]]
    return render(
        request,
        "interface/comissao.html",
        {
            "processo": processo,
            "membros": linhas,
            "total_de_membros": total,
            "sem_etapa": sem_etapa,
            "busca": busca,
            "so_sem_etapa": so_sem_etapa,
            "filtrando": bool(busca or so_sem_etapa),
            "tem_presidente": comissao_selectors.tem_presidente(processo),
            "erro": erro,
            "chave_idempotencia": uuid4().hex,
        },
    )


@require_http_methods(["GET", "POST"])
def alocacoes(request, processo_id):
    """Quem atua em cada Etapa, por Edital (US3 e US4 da 011)."""
    ator, processo, _ = _processo_para_gerir(request, processo_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))

    erro = None
    if request.method == "POST":
        acao = (request.POST.get("acao") or "").strip()
        dados = forms.ler_alocacao(request.POST)
        chave = request.POST.get("chave_idempotencia") or uuid4().hex
        try:
            if acao == "distribuir":
                alocacao_app.definir_distribuicao(
                    actor=ator,
                    processo_id=processo.id,
                    # O escopo é o que a tela desenhou. Sem ele, salvar com a busca ativa
                    # removeria todo mundo que o filtro escondeu.
                    escopo_membros=request.POST.getlist("escopo_membro"),
                    escopo_etapas=request.POST.getlist("escopo_etapa"),
                    marcadas=request.POST.getlist("celula"),
                    coluna_todos=request.POST.get("coluna_todos"),
                    coluna_nenhum=request.POST.get("coluna_nenhum"),
                    idempotency_key=chave,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
                destino = reverse("interface:alocacoes", args=[processo.id])
                busca = (request.POST.get("q") or "").strip()
                return redirect(f"{destino}?feito=distribuir" + (f"&q={busca}" if busca else ""))
            if acao == "incluir":
                # `todos` escolhe **quais** pessoas, dentro da inclusão — não é uma ação
                # concorrente. Como ramo irmão, ele decidia sozinho: um envio com
                # `acao=remover` e `todos=1` alocava.
                selecionados = (
                    request.POST.getlist("disponivel")
                    if request.POST.get("todos")
                    else request.POST.getlist("membro_id")
                )
                alocacao_app.alocar_varios(
                    actor=ator,
                    processo_id=processo.id,
                    membro_ids=selecionados,
                    edital_id=dados["edital_id"],
                    etapa_id=dados["etapa_id"],
                    idempotency_key=chave,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
            elif acao == "remover":
                alocacao_app.remover_varias_alocacoes(
                    actor=ator,
                    processo_id=processo.id,
                    alocacao_ids=request.POST.getlist("alocacao_id"),
                    idempotency_key=chave,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
            return redirect(f"{reverse('interface:alocacoes', args=[processo.id])}?feito={acao}")
        except DomainError as recusa:
            if recusa.status == 404:
                raise Http404 from recusa
            erro = recusa.detail

    organizacao = comissao_selectors.organizacao(processo)
    membros_ativos = comissao_selectors.membros(processo)
    busca = (request.GET.get("q") or "").strip()
    return render(
        request,
        "interface/alocacoes.html",
        {
            "processo": processo,
            "matriz": comissao_selectors.matriz(processo, busca=busca),
            "busca": busca,
            "organizacao": organizacao,
            "membros": membros_ativos,
            "orfas": comissao_selectors.orfas(processo),
            "resumo": comissao_selectors.resumo_da_organizacao(organizacao, membros_ativos),
            "tem_presidente": comissao_selectors.tem_presidente(processo),
            "erro": erro,
            "chave_idempotencia": uuid4().hex,
        },
    )


@require_http_methods(["GET", "POST"])
def distribuicao(request, edital_id, etapa_id):
    """A distribuição das inscrições de uma Etapa (US1 da `012`).

    A porta é a de gestão da comissão — as duas bases que a 011 reconhece —, e não a de atuação:
    distribuir é ato de quem responde pela organização do trabalho, e o guard contextual da 011
    continua respondendo por quem **executa** (FR-067).
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=ator.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None or pode_gerir_comissao(ator, edital.processo) is None:
        # A mesma resposta para Edital de outro escopo e para quem não gere esta comissão: a
        # existência não é enumerável por quem não alcança (FR-044).
        raise Http404
    try:
        etapa = etapa_vigente(edital, etapa_id)
    except DomainError:
        etapa = None
    if etapa is None:
        raise Http404

    erro, resultado = None, None
    if request.method == "POST":
        dados = forms.ler_distribuicao(request.POST)
        chave = request.POST.get("chave_idempotencia") or uuid4().hex
        try:
            if dados["acao"] == "remover":
                removidas, recusas = distribuicao_app.remover_atribuicao(
                    actor=ator,
                    processo_id=edital.processo_id,
                    atribuicao_ids=dados["atribuicao_ids"],
                    idempotency_key=chave,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
                resultado = _resultado_do_lote(len(removidas), recusas, "removida")
            else:
                criadas, recusas = distribuicao_app.distribuir(
                    actor=ator,
                    processo_id=edital.processo_id,
                    edital_id=edital.id,
                    etapa_id=etapa_id,
                    membro_ids=dados["membro_ids"],
                    inscricao_ids=dados["inscricao_ids"],
                    idempotency_key=chave,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
                resultado = _resultado_do_lote(len(criadas), recusas, "atribuída")
            request.session["resultado_da_distribuicao"] = resultado
            return redirect(request.get_full_path())
        except DomainError as recusa:
            if recusa.status == 404:
                raise Http404 from recusa
            erro = recusa.detail

    linhas, pagina = avaliacao_selectors.inscricoes_da_etapa(
        edital=edital,
        etapa=etapa,
        pagina=request.GET.get("pagina") or 1,
        cobertura=request.GET.get("cobertura") or None,
        avaliador=request.GET.get("avaliador") or None,
    )
    return marcar_como_privada(
        render(
            request,
            "interface/distribuicao.html",
            {
                "edital": edital,
                "processo": edital.processo,
                "etapa": etapa,
                "linhas": linhas,
                "pagina": pagina,
                "carga": avaliacao_selectors.carga_por_avaliador(edital=edital, etapa_id=etapa_id),
                "resumo": avaliacao_selectors.resumo_da_etapa(edital=edital, etapa=etapa),
                "cobertura": request.GET.get("cobertura") or "",
                "avaliador": request.GET.get("avaliador") or "",
                "erro": erro,
                "resultado": request.session.pop("resultado_da_distribuicao", None),
                "chave_idempotencia": uuid4().hex,
            },
        )
    )


def _resultado_do_lote(feitas, recusas, verbo):
    """O resultado é **declarado**, e não inferido (FR-097).

    Sucesso parcial que não se anuncia vira surpresa administrativa: quem distribuiu precisa saber
    o que ficou de fora sem conferir mil linhas.
    """
    return {
        "feitas": feitas,
        "verbo": verbo,
        "recusadas": len(recusas),
        "motivos": [
            {
                "avaliador": recusa.membro.identity_subject,
                "inscricao": recusa.inscricao.protocolo or str(recusa.inscricao.id),
                "motivo": recusa.motivo,
            }
            for recusa in recusas
        ],
    }


@require_http_methods(["GET"])
def minhas_etapas(request):
    """A área pessoal de quem trabalha (US5 da 011).

    Não exige permissão nenhuma: para quem não tem alocação, ela é o estado vazio — e não uma
    recusa. Mostrar as Etapas alheias como bloqueadas seria dizer que existem (UX-011).
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    atribuicoes = comissao_selectors.minhas_etapas(ator)
    vinculos = comissao_selectors.comissoes_da_pessoa(ator)
    return render(
        request,
        "interface/minhas_etapas.html",
        {
            "atribuicoes": atribuicoes,
            # As comissões que a pessoa integra, com destaque para as que ela preside: sem isto,
            # quem preside não tinha rota nenhuma até a própria comissão — o acesso existia, o
            # caminho não.
            "vinculos": vinculos,
            # A orientação da 002 é para quem não tem nada. Mostrá-la a quem já integra uma
            # comissão mandava a pessoa pedir exatamente o que ela já tem (FR-028 da 002).
            "sem_papel_nem_atribuicao": (not atribuicoes and not ator.permissions and not vinculos),
        },
    )


@require_http_methods(["GET"])
def minha_etapa(request, edital_id, etapa_id):
    """A Etapa como contexto de trabalho — e nada além disso (§27 e §50 da spec)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=ator.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None:
        raise Http404
    por_alocacao = pode_atuar_na_etapa(ator, edital, etapa_id)
    por_gestao = pode_gerir_comissao(ator, edital.processo) is not None
    if not (por_alocacao or por_gestao):
        # A mesma resposta para Etapa não alocada, de outro Processo ou de outro escopo: a
        # existência não é enumerável por quem não tem acesso (FR-057).
        raise Http404
    try:
        etapa = etapa_vigente(edital, etapa_id)
    except DomainError:
        etapa = None
    if etapa is None:
        raise Http404
    try:
        publicado = evento_vigente(edital, etapa.get("scheduleEventId"))
    except DomainError:
        publicado = None
    # O conteúdo publicado guarda instantes em texto ISO; a tela mostra data brasileira, como
    # todas as outras. A conversão é aqui para o template não conhecer o formato canônico.
    evento = (
        {
            "inicio": parse_datetime(publicado["startAt"]),
            "fim": parse_datetime(publicado["endAt"]) if publicado.get("endAt") else None,
        }
        if publicado
        else None
    )
    return render(
        request,
        "interface/minha_etapa.html",
        {
            "edital": edital,
            "processo": edital.processo,
            "etapa": etapa,
            "evento": evento,
            "por_alocacao": por_alocacao,
            "por_gestao": por_gestao and not por_alocacao,
        },
    )


@require_http_methods(["GET"])
def auditoria_da_comissao(request, processo_id):
    """A trilha da comissão deste Processo, ao lado da trilha do Edital que já existia.

    Sem esta tela a auditoria da 011 só seria verificável por consulta ao banco, e o princípio VI
    da Constituição não a consideraria entregue (D-018).
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    processo = _processo_do_ator(ator, processo_id)
    require_permission(ator, "auditoria:consultar")
    operacao = (request.GET.get("operacao") or "").strip()
    pessoa = (request.GET.get("pessoa") or "").strip()
    registros, proximo = auditoria_selectors.trilha_da_comissao(
        actor=ator,
        processo=processo,
        cursor=request.GET.get("cursor"),
        limit=auditoria_selectors.parse_limit(request.GET.get("limit")),
        operation=operacao or None,
        pessoa=pessoa or None,
    )
    return render(
        request,
        "interface/auditoria.html",
        {
            "processo": processo,
            "da_comissao": True,
            "operacao_filtro": operacao,
            "pessoa_filtro": pessoa,
            # Escolha, e não digitação: o filtro compara identificador exato, e um campo livre
            # transformaria "maria" — quando o identificador é "maria.presidente" — em "nenhum
            # ato encontrado". Falso negativo numa trilha é pior que falso positivo.
            "pessoas_da_trilha": comissao_selectors.pessoas_da_trilha(processo),
            "operacoes_da_comissao": [
                ("COMISSAO_INCLUIR_MEMBRO", OPERACOES["COMISSAO_INCLUIR_MEMBRO"]),
                ("COMISSAO_ALTERAR_FUNCAO", OPERACOES["COMISSAO_ALTERAR_FUNCAO"]),
                ("COMISSAO_REMOVER_MEMBRO", OPERACOES["COMISSAO_REMOVER_MEMBRO"]),
                ("ALOCACAO_INCLUIR", OPERACOES["ALOCACAO_INCLUIR"]),
                ("ALOCACAO_REMOVER", OPERACOES["ALOCACAO_REMOVER"]),
            ],
            "registros": [
                {
                    "quando": registro.occurred_at,
                    "ator": registro.actor_subject,
                    "operacao": OPERACOES.get(registro.operation, registro.operation),
                    "agregado": AGREGADOS.get(registro.aggregate_type, registro.aggregate_type),
                    "identificador": registro.aggregate_id,
                    "permissao": registro.permission,
                    "motivo": registro.reason,
                }
                for registro in registros
            ],
            "proximo_cursor": proximo,
        },
    )
