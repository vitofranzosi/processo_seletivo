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
from django.utils.http import urlencode
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_http_methods

from processo_seletivo.auditoria import selectors as auditoria_selectors
from processo_seletivo.auditoria.application import record_event
from processo_seletivo.avaliacoes.application import avaliacao as avaliacao_app
from processo_seletivo.avaliacoes.application import distribuicao as distribuicao_app
from processo_seletivo.avaliacoes.application import impedimento as impedimento_app
from processo_seletivo.avaliacoes.application import mesa as mesa_app
from processo_seletivo.avaliacoes.application import selectors as avaliacao_selectors
from processo_seletivo.avaliacoes.application.mesa import (
    BASE_DA_MESA,
    CONSULTAR_DOCUMENTO,
    INTEGRIDADE,
)
from processo_seletivo.avaliacoes.application.trilha import auditar as auditar_ato
from processo_seletivo.avaliacoes.domain.previsao import rotulos
from processo_seletivo.comissoes.application import alocacao as alocacao_app
from processo_seletivo.comissoes.application import comissao as comissao_app
from processo_seletivo.comissoes.application import selectors as comissao_selectors
from processo_seletivo.comissoes.domain.autorizacao import (
    pode_atuar_na_etapa,
    pode_gerir_comissao,
)
from processo_seletivo.comissoes.domain.etapas import (
    etapa_vigente,
    etapas_vigentes,
    evento_vigente,
)
from processo_seletivo.comissoes.models import Funcao
from processo_seletivo.editais.application.draft import replace_draft
from processo_seletivo.editais.application.identificacao import update_edital_identification
from processo_seletivo.editais.domain.validation import validate_for_publication
from processo_seletivo.inscricoes.application.consulta import (
    CONSULTAR,
    consulta_de_inscricoes,
    documento_para_consulta,
    inscricao_para_consulta,
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
from processo_seletivo.resultados.application import consolidacao as consolidacao_app
from processo_seletivo.resultados.application import ocorrencia as ocorrencia_app
from processo_seletivo.resultados.application import prontidao as prontidao_013
from processo_seletivo.resultados.application import selectors as resultado_selectors
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
    # Integrar a comissão não é geri-la: a lista oferecia as duas telas a qualquer membro, e
    # ambas exigem **gerir** — o link levava ao 404. A porta aqui é a mesma de
    # `pode_gerir_comissao`, resolvida sobre os vínculos já lidos para não custar uma consulta
    # por Processo.
    gere_por_papel = ator.can("comissao:gerir")
    for processo in processos:
        processo.vinculo = vinculos.get(processo.id)
        # E a recíproca: **quem pode gerir vê o caminho**, ainda que não integre a comissão. O
        # gestor com `comissao:gerir` que não fosse membro não recebia link nenhum para a comissão
        # nem para a alocação — e é justamente ele quem constitui a comissão que ainda não integra.
        # Sem consulta nova: a permissão sistêmica ou a presidência **deste** Processo, sobre os
        # vínculos já lidos.
        processo.pode_gerir = gere_por_papel or (
            processo.vinculo is not None and processo.vinculo.funcao == Funcao.PRESIDENTE
        )

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
        # A identidade escolhida na lista tem prioridade sobre o campo livre: quem clicou num nome
        # sugerido disse o que queria, e o campo pode estar com o exemplo que veio preenchido.
        subject = (
            request.POST.get("identidade_sugerida") or request.POST.get("subject") or ""
        ).strip()
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
            {
                "papeis": identidade.PAPEIS,
                "erro": "Informe um nome.",
                "com_trabalho": comissao_selectors.identidades_com_trabalho(
                    identidade.ESCOPO_PADRAO
                ),
            },
            status=422,
        )
    return render(
        request,
        "interface/identificar.html",
        {
            "papeis": identidade.PAPEIS,
            # Presidir e avaliar **não são papéis** — vêm do vínculo com a comissão —, e por isso
            # nenhuma caixa desta tela os concede. Sem esta lista, quem quisesse percorrer a Mesa
            # tinha de adivinhar um nome que estivesse numa comissão.
            "com_trabalho": comissao_selectors.identidades_com_trabalho(identidade.ESCOPO_PADRAO),
        },
    )


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
            # A chave da etapa que acabou de ser gravada, e não o rótulo dela: é o que o rascunho
            # local precisa para apagar exatamente o que o servidor passou a ter. "Avançar" grava
            # uma etapa e abre outra, então nem sempre é a etapa desta tela.
            "salvo_chave": request.GET.get("salvo", ""),
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
    # A execução do trabalho (012). Os sete atos de FR-052 na mesma trilha, pela razão de sempre:
    # quem investiga por que uma avaliação não conta lê a mesma tela de quem investiga uma
    # publicação.
    "AVALIACAO_ATRIBUIR": "Atribuição de inscrição a avaliador",
    "AVALIACAO_ATRIBUICAO_REMOVER": "Remoção de atribuição",
    "AVALIACAO_GRAVAR": "Gravação de avaliação",
    "AVALIACAO_CONCLUIR": "Conclusão de avaliação",
    "AVALIACAO_REABRIR": "Reabertura de avaliação",
    "AVALIACAO_IMPEDIR": "Registro de impedimento",
    "AVALIACAO_TORNAR_INELEGIVEL": "Avaliação tornada inelegível",
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
    "Atribuicao": "Atribuição de avaliação",
    "Avaliacao": "Avaliação",
    "Impedimento": "Impedimento",
}

# Os sete atos de FR-052, na ordem do percurso. É esta lista que a tela oferece como filtro.
OPERACOES_DA_AVALIACAO = (
    "AVALIACAO_ATRIBUIR",
    "AVALIACAO_ATRIBUICAO_REMOVER",
    "CONSULTAR_DOCUMENTO",
    "AVALIACAO_GRAVAR",
    "AVALIACAO_CONCLUIR",
    "AVALIACAO_REABRIR",
    "AVALIACAO_IMPEDIR",
)


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
            # As duas telas da comissão exigem gerir (011, FR-016). O painel as oferecia a
            # qualquer identidade que enxergasse o Processo, e quem não gere batia num 404 sem
            # explicação: a oferta agora é a mesma decisão que a view de destino toma.
            "pode_gerir_comissao": pode_gerir_comissao(ator, processo) is not None,
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
    busca = (request.GET.get("busca") or "").strip()
    perfil = request.GET.get("perfil") or ""
    modalidade = request.GET.get("modalidade") or ""
    # Recebido é o que foi entregue. O rascunho continua na tela — em seção própria e sob o nome do
    # que é —, mas fora do total: contá-lo diria à gestão que recebeu inscrição que ninguém enviou.
    contexto = consulta_de_inscricoes(
        actor=ator,
        edital_id=edital_id,
        pagina=request.GET.get("pagina") or 1,
        pagina_rascunhos=request.GET.get("rascunhos") or 1,
        busca=busca or None,
        perfil=perfil or None,
        modalidade=modalidade or None,
    )
    # O filtro viaja em todo link da tela — nas duas paginações e em cada cartão de Perfil. Montá-lo
    # uma vez evita a cadeia de `{% if %}` repetida por link, que foi como o cartão acabou perdendo
    # a busca que o formulário preservava.
    filtro = _querystring(busca=busca, perfil=perfil, modalidade=modalidade)
    return marcar_como_privada(
        render(
            request,
            "interface/inscricoes.html",
            {
                **contexto,
                "busca": busca,
                "perfil": perfil,
                "modalidade": modalidade,
                "filtrando": bool(busca or perfil or modalidade),
                "filtro": filtro,
                # Sem o Perfil, para que o cartão possa trocá-lo sem descartar o resto.
                "filtro_sem_perfil": _querystring(busca=busca, modalidade=modalidade),
                # A posição da outra seção, para que paginar uma não devolva a outra ao começo.
                "pagina_da_irma": _querystring(pagina=contexto["pagina_recebidas"].number),
                "rascunhos_da_irma": _querystring(rascunhos=contexto["pagina_rascunhos"].number),
            },
        )
    )


def _querystring(**parametros):
    """Os parâmetros informados, codificados, sem separador nenhum na frente.

    Sem o `&` inicial porque quem monta o link sabe se ele é o primeiro parâmetro ou não, e um
    separador embutido produziria `?&busca=…` nos links que começam por ele. Devolve `""` quando
    não há nada a dizer. Página 1 não entra: é o padrão, e carregá-la só alongaria a URL.
    """
    presentes = {chave: valor for chave, valor in parametros.items() if valor not in (None, "", 1)}
    return urlencode(presentes) if presentes else ""


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
            reason=mesa_app.motivo_da_abertura(documento.requirement_id),
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
            reason=mesa_app.motivo_da_abertura(documento.requirement_id),
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


def _etapa_para_distribuir(request, edital_id, etapa_id):
    """Edital, Etapa e ator — ou 404 para tudo que este ator não alcança (FR-044).

    A porta é a de **gestão da comissão**, e não a de atuação: distribuir é ato de quem responde
    pela organização do trabalho, e o guard contextual da 011 continua respondendo por quem
    executa (FR-067).
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, None, None
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=ator.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None or pode_gerir_comissao(ator, edital.processo) is None:
        raise Http404
    try:
        etapa = etapa_vigente(edital, etapa_id)
    except DomainError:
        etapa = None
    if etapa is None:
        raise Http404
    return ator, edital, etapa


@require_http_methods(["GET", "POST"])
def impedimentos(request, edital_id, etapa_id):
    """Registrar impedimento, e ver o que ele já tirou do conjunto (US5 da `012`)."""
    ator, edital, etapa = _etapa_para_distribuir(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    erro, confirmacao, digitado = None, None, {}
    if request.method == "POST":
        dados = forms.ler_impedimento(request.POST)
        digitado = dados
        try:
            # **Sem a assinatura do alcance não há confirmação**, e o passo é refeito. Aceitar o
            # POST sem ela deixaria a proteção de FR-106 desligável por quem monta o formulário —
            # que é a mesma falha, um nível acima.
            if request.POST.get("confirmar") != "1" or not request.POST.get("alcance"):
                # **A confirmação declara o alcance antes de o ato acontecer** (FR-041): retirar
                # trabalho de alguém não pode ser efeito colateral silencioso de registrar um
                # motivo. Quem confirma vê quantas atribuições e quantas conclusões serão
                # alcançadas.
                #
                # O motivo é cobrado **aqui**, e não só no comando: sem isso, o passo de
                # confirmação aceitaria um formulário incompleto e a recusa só apareceria depois
                # de a pessoa confirmar — o que transforma a validação em armadilha.
                impedimento_app.exigir_dados(**dados)
                confirmacao = impedimento_app.alcance_do_impedimento(
                    processo=edital.processo,
                    identity_subject=dados["identity_subject"],
                    inscricao_id=dados["inscricao_id"],
                )
            else:
                resultado = impedimento_app.registrar_impedimento(
                    actor=ator,
                    processo_id=edital.processo_id,
                    identity_subject=dados["identity_subject"],
                    inscricao_id=dados["inscricao_id"],
                    motivo=dados["motivo"],
                    idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
                    correlation_id=getattr(request, "correlation_id", ""),
                    # A assinatura do alcance que esta pessoa viu. O comando a confere **sob
                    # trava**, contra o conjunto que vai mesmo inativar.
                    alcance_confirmado=request.POST.get("alcance") or None,
                )
                request.session["resultado_do_impedimento"] = resultado
                return redirect(request.path)
        except DomainError as recusa:
            if recusa.status == 404:
                raise Http404 from recusa
            erro = recusa.detail
            if recusa.code == "alcance_mudou":
                # Recusar sem mostrar o novo alcance devolveria a pessoa ao formulário vazio para
                # ela repetir exatamente o mesmo ato às cegas. A confirmação é refeita sobre o que
                # existe agora (FR-041).
                confirmacao = impedimento_app.alcance_do_impedimento(
                    processo=edital.processo,
                    identity_subject=dados["identity_subject"],
                    inscricao_id=dados["inscricao_id"],
                )
    inelegiveis, pagina_dos_inelegiveis = avaliacao_selectors.avaliacoes_inelegiveis(
        edital=edital, etapa_id=etapa_id, pagina=request.GET.get("pagina") or 1
    )
    return marcar_como_privada(
        render(
            request,
            "interface/impedimentos.html",
            {
                "edital": edital,
                "processo": edital.processo,
                "etapa": etapa,
                "carga": avaliacao_selectors.carga_por_avaliador(edital=edital, etapa_id=etapa_id),
                "inelegiveis": [
                    # O ato por extenso, e não a constante: a trilha já traduz `AVALIACAO_…` e
                    # esta tabela mostrava o código cru para a mesma pessoa.
                    {
                        **linha,
                        "ato_rotulo": OPERACOES.get(getattr(linha["ato"], "operation", ""), ""),
                    }
                    for linha in inelegiveis
                ],
                "pagina_dos_inelegiveis": pagina_dos_inelegiveis,
                "erro": erro,
                "confirmacao": confirmacao,
                "digitado": digitado,
                "resultado": request.session.pop("resultado_do_impedimento", None),
                "chave_idempotencia": uuid4().hex,
            },
        )
    )


@require_http_methods(["POST"])
def reabrir_avaliacao(request, edital_id, etapa_id):
    """Reabertura: ato da presidência, com motivo, registrado (FR-036).

    Chamada da página de **conclusões preservadas**, que é onde se lê o que foi concluído antes de
    decidir sobre aquilo — e para onde a resposta volta.
    """
    ator, edital, _ = _etapa_para_distribuir(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    dados = forms.ler_reabertura(request.POST)
    try:
        avaliacao_app.reabrir(
            actor=ator,
            processo_id=edital.processo_id,
            avaliacao_id=dados["avaliacao_id"],
            motivo=dados["motivo"],
            expected_revision=dados["expected_revision"],
            idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
            correlation_id=getattr(request, "correlation_id", ""),
        )
        request.session["resultado_da_reabertura"] = (
            "Avaliação reaberta. Ela voltou a ser trabalho pendente na Mesa de quem tem a "
            "atribuição, e o que havia sido concluído continua nesta página."
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        request.session["erro_da_reabertura"] = recusa.detail
    return redirect(reverse("interface:conclusoes-preservadas", args=[edital_id, etapa_id]))


@require_http_methods(["POST"])
def consolidar_resultados(request, edital_id, etapa_id):
    """O lote da 013: as inscrições prontas viram Resultado num ato confirmado (FR-018).

    Rota própria, e não um ramo do formulário de distribuir. A razão é a mesma que a 012 usou para
    separar remover de atribuir, e aqui o custo do engano seria maior: consolidar é irreversível, e
    a V1 não oferece anulação.

    A porta é a de gestão da comissão — a mesma da reabertura —, e não há capacidade nova. Quem
    preside o Processo consolida a Etapa dele; quem não preside recebe a resposta uniforme.
    """
    ator, edital, _ = _etapa_para_distribuir(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    destino = reverse("interface:distribuicao", args=[edital_id, etapa_id])
    try:
        request.session["resultado_da_consolidacao"] = consolidacao_app.consolidar(
            actor=ator,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            etapa_id=etapa_id,
            inscricao_ids=request.POST.getlist("inscricao_id"),
            idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
            correlation_id=getattr(request, "correlation_id", ""),
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        request.session["erro_da_consolidacao"] = recusa.detail
    return redirect(destino)


@require_http_methods(["GET", "POST"])
def registrar_ocorrencia(request, edital_id, etapa_id):
    """O desfecho de quem não foi avaliado, alcançável por quem preside (D-1).

    **Página própria, e não um `formaction` a mais na distribuição.** Consolidar compartilha o
    formulário de distribuir porque a seleção é a mesma e nada mais é informado; aqui a presidência
    informa o motivo, e um campo obrigatório ao lado de três botões pertenceria visualmente aos
    três. O ato também é de outra natureza: ele **elimina** quem a Etapa nunca avaliou, e não se
    desfaz.

    **Confirmação em dois passos, como o impedimento da 012.** O primeiro passo declara o alcance —
    quantas e quais inscrições serão eliminadas — antes de o ato acontecer; o segundo o executa.
    Retirar alguém do Processo não pode ser efeito colateral de um clique.

    A porta é a de gestão da comissão — a mesma de consolidar e de reabrir —, e não há capacidade
    nova: quem preside o Processo constata a ocorrência na Etapa dele, e quem não preside recebe a
    resposta uniforme.
    """
    from django.core.paginator import Paginator

    from processo_seletivo.inscricoes.models import Inscricao

    ator, edital, etapa = _etapa_para_distribuir(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    vigentes = etapas_vigentes(edital)
    erro, confirmacao = None, None
    motivo = (request.POST.get("motivo") or "").strip() if request.method == "POST" else ""
    marcadas = request.POST.getlist("inscricao_id") if request.method == "POST" else []
    if request.method == "POST":
        try:
            # O motivo e a seleção são cobrados **aqui**, e não só no comando: sem isso o passo de
            # confirmação aceitaria um formulário incompleto e a recusa só apareceria depois de a
            # pessoa confirmar, o que transforma a validação em armadilha.
            ocorrencia_app.exigir_motivo(motivo)
            if not marcadas:
                raise DomainError(
                    "selecao_vazia",
                    "Selecione ao menos uma inscrição para registrar a ocorrência.",
                    422,
                    campo="inscricao_id",
                )
            if request.POST.get("confirmar") != "1":
                confirmacao = list(
                    Inscricao.objects.filter(pk__in=marcadas, edital=edital).order_by(
                        "protocolo", "id"
                    )
                )
            else:
                request.session["resultado_da_ocorrencia"] = ocorrencia_app.registrar_ocorrencia(
                    actor=ator,
                    processo_id=edital.processo_id,
                    edital_id=edital.id,
                    etapa_id=etapa_id,
                    inscricao_ids=marcadas,
                    motivo=motivo,
                    idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
                return redirect(
                    reverse("interface:registrar-ocorrencia", args=[edital_id, etapa_id])
                )
        except DomainError as recusa:
            if recusa.status == 404:
                raise Http404 from recusa
            erro = recusa.detail

    pendentes = ocorrencia_app.participantes_sem_resultado(
        edital=edital, etapa=etapa, vigentes=vigentes
    )
    paginas = Paginator(pendentes, 25)
    pagina = paginas.get_page(request.GET.get("pagina") or 1)
    return marcar_como_privada(
        render(
            request,
            "interface/ocorrencia.html",
            {
                "edital": edital,
                "processo": edital.processo,
                "etapa": etapa,
                "linhas": list(pagina),
                "pagina": pagina,
                "erro": erro,
                "confirmacao": confirmacao,
                "motivo": motivo,
                "marcadas": set(marcadas),
                "resultado": request.session.pop("resultado_da_ocorrencia", None),
                "chave_idempotencia": uuid4().hex,
            },
        )
    )


@require_http_methods(["POST"])
def remover_atribuicao(request, edital_id, etapa_id):
    """Retira Atribuições da Etapa — as que ainda não têm Avaliação concluída.

    Rota própria, e não um ramo do formulário de distribuir: `acao` decidindo entre criar e
    remover foi como a 011 descobriu que ramo irmão decide sozinho, e aqui o custo do engano seria
    retirar trabalho de alguém.
    """
    ator, edital, _ = _etapa_para_distribuir(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    destino = reverse("interface:distribuicao", args=[edital_id, etapa_id])
    try:
        request.session["resultado_da_distribuicao"] = distribuicao_app.remover_atribuicao(
            actor=ator,
            processo_id=edital.processo_id,
            atribuicao_ids=request.POST.getlist("atribuicao_id"),
            idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
            correlation_id=getattr(request, "correlation_id", ""),
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        request.session["erro_da_distribuicao"] = recusa.detail
    return redirect(destino)


@require_http_methods(["GET", "POST"])
def distribuicao(request, edital_id, etapa_id):
    """A distribuição das inscrições de uma Etapa (US1 da `012`).

    A porta é a de gestão da comissão — as duas bases que a 011 reconhece —, e não a de atuação:
    distribuir é ato de quem responde pela organização do trabalho, e o guard contextual da 011
    continua respondendo por quem **executa** (FR-067).
    """
    ator, edital, etapa = _etapa_para_distribuir(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))

    erro = request.session.pop("erro_da_distribuicao", None)
    proposta = None
    if request.method == "POST":
        dados = forms.ler_distribuicao(request.POST)
        chave = request.POST.get("chave_idempotencia") or uuid4().hex
        try:
            if dados["acao"] == "propor":
                # **Propor não grava nada** (FR-107). A tela mostra a proposta inteira — quanto
                # cada pessoa recebe e o que fica de fora — e nada acontece até a confirmação.
                proposta = distribuicao_app.propor_rodizio(
                    actor=ator,
                    processo=edital.processo,
                    edital_id=edital.id,
                    etapa_id=etapa_id,
                    membro_ids=dados["membro_ids"],
                )
            elif dados["acao"] == "confirmar_rodizio":
                resultado = distribuicao_app.confirmar_rodizio(
                    actor=ator,
                    processo_id=edital.processo_id,
                    edital_id=edital.id,
                    etapa_id=etapa_id,
                    membro_ids=dados["membro_ids"],
                    assinatura=dados["assinatura"],
                    idempotency_key=chave,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
                request.session["resultado_da_distribuicao"] = resultado
                return redirect(request.get_full_path())
            else:
                resultado = distribuicao_app.distribuir(
                    actor=ator,
                    processo_id=edital.processo_id,
                    edital_id=edital.id,
                    etapa_id=etapa_id,
                    membro_ids=dados["membro_ids"],
                    inscricao_ids=dados["inscricao_ids"],
                    idempotency_key=chave,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
                request.session["resultado_da_distribuicao"] = resultado
                return redirect(request.get_full_path())
        except DomainError as recusa:
            if recusa.status == 404:
                raise Http404 from recusa
            erro = recusa.detail
            if recusa.code == "proposta_mudou":
                # Recusar sem mostrar a nova proposta devolveria a pessoa ao ponto de partida para
                # repetir o mesmo ato às cegas.
                proposta = distribuicao_app.propor_rodizio(
                    actor=ator,
                    processo=edital.processo,
                    edital_id=edital.id,
                    etapa_id=etapa_id,
                    membro_ids=dados["membro_ids"],
                )

    # O panorama da 013 é resolvido **uma vez** e entregue ao resumo e à listagem. Consultá-lo nos
    # dois lugares daria dois números para a mesma Etapa, que é o que D-004 recusa; consultá-lo por
    # linha devolveria à listagem o custo que a 012 tirou dela (FR-006, FR-009).
    panorama = prontidao_013.panorama_da_etapa(
        edital=edital, etapa=etapa, etapas_vigentes=etapas_vigentes(edital)
    )
    linhas, pagina = avaliacao_selectors.inscricoes_da_etapa(
        edital=edital,
        etapa=etapa,
        pagina=request.GET.get("pagina") or 1,
        cobertura=request.GET.get("cobertura") or None,
        avaliador=request.GET.get("avaliador") or None,
        panorama=panorama,
        prontidao=request.GET.get("prontidao") or None,
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
                "resumo": avaliacao_selectors.resumo_da_etapa(
                    edital=edital, etapa=etapa, panorama=panorama
                ),
                "prontidao": request.GET.get("prontidao") or "",
                "impedimento_da_etapa": panorama["impedimento_da_etapa"],
                "cobertura": request.GET.get("cobertura") or "",
                "avaliador": request.GET.get("avaliador") or "",
                "erro": erro,
                "proposta": proposta,
                "resultado": request.session.pop("resultado_da_distribuicao", None),
                "consolidacao": request.session.pop("resultado_da_consolidacao", None),
                "erro_da_consolidacao": request.session.pop("erro_da_consolidacao", None),
                "chave_consolidacao": uuid4().hex,
                "chave_idempotencia": uuid4().hex,
                "chave_remocao": uuid4().hex,
                "chave_rodizio": uuid4().hex,
                "tem_atribuicoes": any(linha["atribuicoes"] for linha in linhas),
                "orfas": avaliacao_selectors.atribuicoes_orfas(edital=edital, etapa_id=etapa_id),
            },
        )
    )


def _mesa_do_avaliador(request, edital_id, etapa_id):
    """Ator e Edital para as rotas da Mesa — a primeira metade da autorização composta.

    A segunda metade é por inscrição, e vive em `avaliacoes.application.mesa`: aqui só se resolve
    o Edital e o ator, e tudo o que o ator não alcança responde como inexistente (FR-044).
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, None
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=ator.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None:
        raise Http404
    return ator, edital


@require_http_methods(["GET"])
def inscricao_da_mesa(request, edital_id, etapa_id, inscricao_id):
    """O que o candidato enviou, sob a Atribuição que autoriza abrir (US3 da `012`)."""
    ator, edital = _mesa_do_avaliador(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    try:
        contexto = mesa_app.inscricao_para_avaliar(
            ator=ator, edital=edital, etapa_id=etapa_id, inscricao_id=inscricao_id
        )
    except DomainError as recusa:
        raise Http404 from recusa
    leituras = _leituras_por_requisito(ator, contexto["atribuicao"])
    leitura = max(leituras.values(), default=None)
    documentos = [
        {**documento, "aberto_em": leituras.get(str(documento["id"]))}
        for documento in contexto["documentos"]
    ]
    contexto["documentos"] = documentos
    tem_documento = any(documento["enviado"] for documento in documentos)
    abertos = sum(1 for documento in documentos if documento["enviado"] and documento["aberto_em"])
    # A **página** carrega dado pessoal, e não só o arquivo: protocolo, nome e CPF mascarado não
    # podem ficar no cache do navegador (FR-056).
    return marcar_como_privada(
        render(
            request,
            "interface/mesa_inscricao.html",
            {
                **contexto,
                "edital": edital,
                "processo": edital.processo,
                "etapa_id": etapa_id,
                "aviso": request.session.pop("aviso_da_avaliacao", None),
                # **Se esta pessoa já abriu algum documento desta inscrição.** Não é palpite nem
                # estado de sessão: é a trilha, que registra cada abertura sob a Atribuição. Serve
                # a duas coisas — dizer, a quem volta a uma Mesa de centenas, se já leu esta; e
                # decidir onde o foco começa, porque a tela abria com o cursor na nota, pronta
                # para receber uma pontuação antes de qualquer leitura.
                "ultima_leitura": leitura,
                "documentos_abertos": abertos,
                "documentos_entregues": sum(1 for d in documentos if d["enviado"]),
                "ja_abriu_documento": leitura is not None,
                "tem_documento": tem_documento,
                # Onde o cursor para: na nota só quando não há o que ler antes.
                "foco_na_nota": leitura is not None or not tem_documento,
                # Para onde ir depois desta. Com centenas atribuídas, voltar pela trilha de
                # navegação a cada inscrição faz o caminho ser mais longo que o trabalho.
                "proxima": avaliacao_selectors.proxima_pendente(
                    ator=ator, edital=edital, etapa_id=etapa_id, depois_de=inscricao_id
                ),
                # O que a tela exibe nos campos, resolvido **aqui**: o digitado antes da recusa
                # tem prioridade — perder o parecer escrito porque a revisão estava obsoleta
                # seria punir duas vezes —, e depois o que já estava gravado.
                "valores": _valores_da_avaliacao(
                    request.session.pop("digitado_na_avaliacao", None),
                    contexto.get("avaliacao"),
                ),
            },
        )
    )


def _leituras_por_requisito(ator, atribuicao):
    """Quais documentos desta inscrição **esta pessoa** já abriu, e quando cada um.

    Numa inscrição com dez documentos exigidos, "onde eu parei" deixa de ser uma pergunta que se
    responde olhando — e a resposta já está registrada, um evento por abertura, com o requisito no
    motivo (FR-027).

    O que se marca é **aberto**, e não avaliado: a Avaliação é uma só por inscrição, e não há
    julgamento por documento a exibir. Chamar isto de "avaliado" inventaria um veredito que o
    domínio não tem.
    """
    from processo_seletivo.auditoria.models import RegistroAuditoria

    leituras = {}
    for motivo, quando in RegistroAuditoria.objects.filter(
        operation=CONSULTAR_DOCUMENTO,
        aggregate_id=atribuicao.id,
        actor_subject=ator.subject,
    ).values_list("reason", "occurred_at"):
        requisito = mesa_app.requisito_do_motivo(motivo)
        if requisito is None:
            continue
        # A mais recente de cada requisito. `datetime.min` não serve de piso aqui: ele é ingênuo,
        # e os instantes da trilha têm fuso.
        anterior = leituras.get(requisito)
        if anterior is None or quando > anterior:
            leituras[requisito] = quando
    return leituras


def _valores_da_avaliacao(digitado, avaliacao):
    if digitado:
        return {
            "pontuacao": digitado.get("pontuacao", ""),
            "sentido": digitado.get("sentido", ""),
            "parecer": digitado.get("parecer", ""),
        }
    if avaliacao is None:
        return {"pontuacao": "", "sentido": "", "parecer": ""}
    return {
        "pontuacao": "" if avaliacao.pontuacao is None else f"{avaliacao.pontuacao:f}",
        "sentido": avaliacao.sentido,
        "parecer": avaliacao.parecer,
    }


@require_http_methods(["POST"])
def avaliacao_gravar(request, edital_id, etapa_id, inscricao_id):
    """Salvar o rascunho — sem exigir conclusão (FR-031)."""
    return _registrar_avaliacao(
        request, edital_id, etapa_id, inscricao_id, avaliacao_app.gravar, "Rascunho salvo."
    )


@require_http_methods(["POST"])
def avaliacao_concluir(request, edital_id, etapa_id, inscricao_id):
    """Concluir — ato explícito, distinto de salvar (FR-032) — **e seguir para a próxima**.

    Concluir e ir para a próxima eram dois cliques, cobrados uma vez por inscrição: numa Mesa de
    230 são 230 cliques para dizer "continuo trabalhando". Quem conclui uma avaliação está, quase
    sempre, indo para a seguinte — e quando não está, a Mesa fica a um clique.

    O aviso nomeia **qual** inscrição foi concluída, porque a tela que aparece é a de outra: sem o
    protocolo escrito, a confirmação passaria a se referir a um candidato diferente do que ela
    confirma.
    """
    return _registrar_avaliacao(
        request,
        edital_id,
        etapa_id,
        inscricao_id,
        avaliacao_app.concluir,
        "Avaliação concluída.",
        seguir=True,
    )


def _registrar_avaliacao(
    request, edital_id, etapa_id, inscricao_id, comando, sucesso, *, seguir=False
):
    """O caminho comum das duas rotas: autorizar, executar, e devolver a recusa legível.

    A recusa volta para a mesma tela, e não vira 500: revisão obsoleta, parecer obrigatório e
    versão mudada são coisas que a pessoa precisa **ler** para corrigir.
    """
    ator, edital = _mesa_do_avaliador(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    dados = forms.ler_avaliacao(request.POST)
    destino = reverse("interface:mesa-inscricao", args=[edital_id, etapa_id, inscricao_id])
    argumentos = {
        "ator": ator,
        "edital": edital,
        "etapa_id": etapa_id,
        "inscricao_id": inscricao_id,
        "pontuacao": dados["pontuacao"],
        "sentido": dados["sentido"],
        "parecer": dados["parecer"],
        "expected_revision": dados["expected_revision"],
        "correlation_id": getattr(request, "correlation_id", ""),
    }
    if comando is avaliacao_app.concluir:
        argumentos["versao_reconhecida"] = dados["versao_reconhecida"]
    try:
        comando(**argumentos)
        texto = sucesso
        if seguir:
            texto, destino = _para_a_proxima(ator, edital, etapa_id, inscricao_id, destino)
        request.session["aviso_da_avaliacao"] = {"tipo": "sucesso", "texto": texto}
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        request.session["aviso_da_avaliacao"] = {"tipo": "erro", "texto": recusa.detail}
        request.session["digitado_na_avaliacao"] = {
            "pontuacao": dados["pontuacao"],
            "sentido": dados["sentido"],
            "parecer": dados["parecer"],
        }
    return redirect(destino)


def _para_a_proxima(ator, edital, etapa_id, inscricao_id, destino):
    """O aviso e o destino depois de concluir: a próxima pendente, ou o fim do trabalho.

    O protocolo da que foi concluída entra no texto porque a página que se abre é a de outra
    inscrição — uma confirmação sem nome se referiria ao candidato errado.
    """
    from processo_seletivo.inscricoes.models import Inscricao

    concluida = Inscricao.objects.filter(pk=inscricao_id).first()
    protocolo = (concluida.protocolo or inscricao_id) if concluida else inscricao_id
    proxima = avaliacao_selectors.proxima_pendente(
        ator=ator, edital=edital, etapa_id=etapa_id, depois_de=inscricao_id
    )
    if proxima is None:
        return (
            f"Avaliação da inscrição {protocolo} concluída. "
            "Não há mais inscrições pendentes suas nesta Etapa.",
            destino,
        )
    return (
        f"Avaliação da inscrição {protocolo} concluída. Esta é a próxima pendente da sua Mesa.",
        reverse("interface:mesa-inscricao", args=[edital.id, etapa_id, proxima.id]),
    )


@xframe_options_sameorigin
@require_http_methods(["GET"])
def documento_da_mesa(request, edital_id, etapa_id, inscricao_id, requirement_id):
    """O documento do candidato, conferido **antes** de sair um byte.

    **Emoldurável pela própria origem**, e só por ela. A Mesa exibe o documento ao lado do
    formulário, e sem isto o `X-Frame-Options: DENY` do resto do sistema bloquearia a moldura —
    inclusive a nossa. A proteção contra clickjacking continua valendo contra qualquer outra
    origem, que é de quem ela protege; e o que vai dentro da moldura é a mesma resposta
    autenticada, conferida e não armazenável de sempre.

    A mecânica é a mesma da consulta administrativa da 009 — e a autorização não é: aqui vale a
    Atribuição, e nunca a permissão que alcança o Edital inteiro (D-005).
    """
    ator, edital = _mesa_do_avaliador(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    try:
        documento, atribuicao = mesa_app.documento_para_avaliar(
            ator=ator,
            edital=edital,
            etapa_id=etapa_id,
            inscricao_id=inscricao_id,
            requirement_id=requirement_id,
        )
    except DomainError as recusa:
        raise Http404 from recusa
    # Uma passagem só: a cópia é conferida e é **ela** que vai para a resposta. Verificar um
    # conteúdo e servir outro é pior do que não verificar, porque produz a afirmação de
    # integridade que ninguém checou (FR-029).
    copia, calculado = copia_verificada(documento)
    if calculado != documento.content_hash:
        copia.close()
        _registrar_na_mesa(ator, atribuicao, documento, request, INTEGRIDADE)
        raise DomainError(
            "document_integrity_failed",
            "O arquivo guardado não confere com o que foi recebido. O documento não pode ser "
            "apresentado como íntegro; registre a ocorrência à presidência.",
            409,
        )
    _registrar_na_mesa(ator, atribuicao, documento, request, CONSULTAR_DOCUMENTO)
    return entregar(documento, anexo=bool(request.GET.get("baixar")), verificado=copia)


def _registrar_na_mesa(ator, atribuicao, documento, request, operacao):
    """Cada abertura fica registrada **sob a Atribuição que a autorizou** (FR-027, FR-053).

    O agregado é a Atribuição, e não a Inscrição, porque é ela que nomeia as quatro coisas que o
    registro precisa identificar: quem, qual inscrição, qual Etapa e por qual vínculo. A Inscrição
    nomeia uma só — e ancorar ali fazia a trilha de uma Etapa exibir as aberturas de outra, e
    exibir as consultas administrativas da 009, que registram a mesma operação sobre a mesma
    Inscrição sob outra permissão. Histórico que mistura origens é pior que histórico incompleto.

    A base registrada é a da Mesa, e não a permissão da consulta administrativa: é ela que diz
    **por que** o acesso foi concedido — a Atribuição, e não um papel (FR-051).

    A trilha guarda que o ato aconteceu, e nunca o nome do arquivo, que é do candidato (FR-054).
    """
    with command_context() as agora:
        # Pelo emissor da 012, e não por `record_event` direto: a Atribuição não tem ciclo de vida,
        # e o registrador leria `aggregate.status` de um objeto que não tem estado (D-014, FR-070).
        auditar_ato(
            actor=ator,
            permissao=BASE_DA_MESA,
            operation=operacao,
            aggregate=atribuicao,
            now=agora,
            correlation_id=getattr(request, "correlation_id", ""),
            reason=mesa_app.motivo_da_abertura(documento.requirement_id),
        )


@require_http_methods(["GET"])
def resultados_da_etapa(request, edital_id, etapa_id):
    """Os Resultados da Etapa, com a origem de cada um (US4 da `013`).

    **Consultar é de dois; consolidar é de um.** A presidência e a auditoria leem esta página pela
    mesma porta das conclusões preservadas — são as duas que respondem a recurso —, e ler não
    concede o poder de decidir: consolidar continua exigindo a base de gestão da comissão.

    A resposta carrega pontuação e protocolo de candidato, e por isso não fica no cache do
    navegador (013, FR-039).
    """
    ator, edital, etapa = _etapa_para_auditar(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    pagina = resultado_selectors.resultados_da_etapa(
        edital=edital,
        etapa_id=etapa_id,
        consequencia=(request.GET.get("consequencia") or "").upper() or None,
        pagina=request.GET.get("pagina") or 1,
    )
    linhas = list(pagina)
    # A vigência da norma resolvida **uma vez por versão distinta**, e pendurada na linha. Um Edital
    # tem duas ou três Versões Consolidadas; `select_related("versao")` traria uma cópia do Edital
    # inteiro em JSON por linha da página para imprimir esta data, e a contagem de consultas não
    # mudaria — nenhum teste de custo denunciaria (D-1).
    vigencias = resultado_selectors.vigencias_das_versoes({linha.versao_id for linha in linhas})
    for linha in linhas:
        linha.vigencia = vigencias.get(linha.versao_id)
    return marcar_como_privada(
        render(
            request,
            "interface/resultados.html",
            {
                "edital": edital,
                "processo": edital.processo,
                "etapa": etapa,
                "linhas": linhas,
                "pagina": pagina,
                # A contestação superveniente vai ao lado da decisão, e não escondida na trilha:
                # quem consulta precisa saber que a origem foi questionada depois (FR-032).
                "contestados": resultado_selectors.contestacoes_supervenientes(linhas),
                "consequencia": request.GET.get("consequencia") or "",
                # Os rótulos que **este** Edital publicou: quem consulta o Resultado tem direito ao
                # vocabulário do Edital, e não ao enum do domínio (FR-118).
                "rotulo_favoravel": rotulos(etapa)[0],
                "rotulo_desfavoravel": rotulos(etapa)[1],
            },
        )
    )


@require_http_methods(["GET"])
def conclusoes_preservadas(request, edital_id, etapa_id):
    """O que foi concluído e deixou de valer — íntegro, e legível por quem responde (FR-091).

    Esta página existe porque "está gravado em algum lugar" não é resposta a um recurso. A trilha
    diz que a reabertura aconteceu e quem a praticou; ela não diz — e não deve dizer — qual era a
    pontuação, o parecer e a versão que governava (FR-054). Isso vive no registro append-only do
    domínio, e é o que esta tela lê.
    """
    ator, edital, etapa = _etapa_para_auditar(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    # **Consultar é de dois; reabrir é de um.** A auditoria lê esta página inteira e não age nela,
    # e é por isso que o formulário de reabertura depende da mesma base que a rota do ato exige.
    pode_reabrir = pode_gerir_comissao(ator, edital.processo) is not None
    inscricao = (request.GET.get("inscricao") or "").strip()
    filtro_invalido = None
    procurada = _inscricao_do_filtro(edital, inscricao) if inscricao else None
    if inscricao and procurada is None:
        filtro_invalido = "Não há inscrição com este protocolo ou identificador neste Edital."
        linhas, pagina = [], None
    else:
        encontradas, pagina = avaliacao_selectors.conclusoes_preservadas(
            edital=edital,
            etapa_id=etapa_id,
            inscricao_id=procurada,
            pagina=request.GET.get("pagina") or 1,
        )
        linhas = [
            {**linha, "rotulo": SITUACAO_DA_CONCLUSAO[linha["situacao"]]} for linha in encontradas
        ]
    return marcar_como_privada(
        render(
            request,
            "interface/conclusoes.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "etapa": etapa,
                "linhas": linhas,
                "pagina": pagina,
                "inscricao_filtro": inscricao,
                "filtro_invalido": filtro_invalido,
                "pode_reabrir": pode_reabrir,
                "erro": request.session.pop("erro_da_reabertura", None),
                "resultado": request.session.pop("resultado_da_reabertura", None),
                "chave_reabertura": uuid4().hex,
            },
        )
    )


# O que aconteceu com cada conclusão preservada, dito por extenso. Preservar não é o mesmo que
# continuar valendo, e a tela que não distingue as duas coisas engana quem consulta.
SITUACAO_DA_CONCLUSAO = {
    "em_vigor": "Em vigor",
    "reaberta": "Substituída por reabertura",
    "inelegivel": "Preservada e inelegível",
}


def _inscricao_do_filtro(edital, valor):
    """O identificador da inscrição a filtrar, aceitando **protocolo** ou UUID.

    As telas exibem o protocolo — a trilha diz “inscrição 7529 — bruno” — e o filtro exigia o UUID,
    recusando exatamente o número que ela acabara de mostrar. Devolve `None` quando o texto não
    corresponde a inscrição nenhuma deste Edital, e quem chama transforma isso em aviso de
    formulário, nunca em erro de servidor.
    """
    from processo_seletivo.inscricoes.models import Inscricao

    texto = str(valor or "").strip()
    consulta = Inscricao.objects.filter(edital=edital)
    try:
        encontrada = consulta.filter(pk=UUID(texto)).first()
    except (TypeError, ValueError):
        encontrada = consulta.filter(protocolo=texto).first()
    return str(encontrada.id) if encontrada is not None else None


def _etapa_para_auditar(request, edital_id, etapa_id):
    """A porta da consulta: presidência **ou** auditoria — nunca as duas ao mesmo tempo (FR-091).

    Exigir a conjunção reduzia a trilha ao usuário híbrido: quem preside sem o papel de auditor
    lia 403, e quem audita sem gerir o Processo lia 404. Quem responde a um recurso é um dos dois,
    e quase nunca é os dois — o que a spec concede a cada um, a porta negava a ambos.

    A recusa é 404 para as duas, como em todo o resto da feature: quem não alcança não descobre
    pela resposta se o que existe é a Etapa ou a permissão (FR-044).
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, None, None
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=ator.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None:
        raise Http404
    if pode_gerir_comissao(ator, edital.processo) is None and not ator.can("auditoria:consultar"):
        raise Http404
    try:
        etapa = etapa_vigente(edital, etapa_id)
    except DomainError:
        etapa = None
    if etapa is None:
        raise Http404
    return ator, edital, etapa


@require_http_methods(["GET"])
def trilha_da_avaliacao(request, edital_id, etapa_id):
    """A trilha da execução do trabalho, filtrável pelas três dimensões de FR-050.

    Volumosa por natureza — duas mil atribuições e cada documento aberto —, ela nasce filtrável por
    inscrição, por avaliador e por operação. As duas primeiras não saem de `aggregate_id` nem de
    `actor_subject` sozinhos, e a razão está em T-016.
    """
    ator, edital, etapa = _etapa_para_auditar(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    operacao = (request.GET.get("operacao") or "").strip()
    inscricao = (request.GET.get("inscricao") or "").strip()
    avaliador = (request.GET.get("avaliador") or "").strip()
    # O campo é digitado, e o que a tela mostra é o protocolo — é ele que precisa funcionar aqui.
    filtro_invalido = None
    procurada = _inscricao_do_filtro(edital, inscricao) if inscricao else None
    if inscricao and procurada is None:
        filtro_invalido = "Não há inscrição com este protocolo ou identificador neste Edital."
        registros, proximo = [], None
    else:
        registros, proximo = auditoria_selectors.trilha_da_avaliacao(
            actor=ator,
            edital=edital,
            etapa_id=etapa_id,
            inscricao=procurada,
            avaliador=avaliador or None,
            cursor=request.GET.get("cursor"),
            limit=auditoria_selectors.parse_limit(request.GET.get("limit")),
            operation=operacao or None,
        )
    rotulos = avaliacao_selectors.rotulos_dos_agregados(registros)
    # Os nomes dos requisitos, para a trilha dizer qual documento foi aberto em vez do UUID dele.
    nomes_dos_requisitos = mesa_app.nomes_dos_requisitos(edital.id)
    return marcar_como_privada(
        render(
            request,
            "interface/auditoria.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "etapa": etapa,
                "da_avaliacao": True,
                "filtro_invalido": filtro_invalido,
                "operacao_filtro": operacao,
                "inscricao_filtro": inscricao,
                "avaliador_filtro": avaliador,
                "avaliadores_da_etapa": [
                    linha["membro"]
                    for linha in avaliacao_selectors.carga_por_avaliador(
                        edital=edital, etapa_id=etapa_id
                    )
                ],
                "operacoes_da_avaliacao": [
                    (chave, OPERACOES[chave]) for chave in OPERACOES_DA_AVALIACAO
                ],
                "registros": [
                    {
                        "quando": registro.occurred_at,
                        "ator": registro.actor_subject,
                        "operacao": OPERACOES.get(registro.operation, registro.operation),
                        "agregado": AGREGADOS.get(registro.aggregate_type, registro.aggregate_type),
                        "identificador": registro.aggregate_id,
                        # A que o ato se refere, em nome de gente: sem isto a trilha dizia
                        # "Conclusão de avaliação, por joao" e escondia de qual inscrição.
                        "sobre": rotulos.get(registro.aggregate_id),
                        "permissao": registro.permission,
                        "motivo": mesa_app.motivo_legivel(registro.reason, nomes_dos_requisitos),
                    }
                    for registro in registros
                ],
                "proximo_cursor": proximo,
            },
        )
    )


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
    # Quanto falta em cada Etapa: a primeira pergunta de quem trabalha, e a tela respondia só
    # depois de entrar. As contagens vêm de uma agregação só, e não de uma consulta por Etapa.
    carga = avaliacao_selectors.carga_nas_etapas(ator=ator, atribuicoes=atribuicoes)
    for item in atribuicoes:
        item["carga"] = carga.get((item["edital"].id, str(item["etapa_id"])))
    vinculos = comissao_selectors.comissoes_da_pessoa(ator)
    return render(
        request,
        "interface/minhas_etapas.html",
        {
            "atribuicoes": atribuicoes,
            # Quanto falta em cada Etapa. Sem isto a tela listava Etapas e um botão “Abrir”, e a
            # primeira pergunta de quem trabalha — quanto falta — só era respondida entrando.
            # As comissões que a pessoa integra, com destaque para as que ela preside: sem isto,
            # quem preside não tinha rota nenhuma até a própria comissão — o acesso existia, o
            # caminho não.
            "vinculos": vinculos,
            # Presidir não atribui trabalho de avaliação, e o estado vazio precisa dizer isso a
            # quem preside — e não a quem é membro, para quem a frase seria falsa.
            "preside": any(v.funcao == "PRESIDENTE" for v in vinculos),
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
        # A coleção inteira, e não `etapa_vigente`: é o que aquele wrapper leria por dentro, e a
        # Mesa precisa dela para resolver a progressão. Ler uma vez e repassar mantém o custo onde
        # estava — o orçamento de consulta desta tela é testado (013, FR-006).
        vigentes = etapas_vigentes(edital)
    except DomainError:
        vigentes = {}
    etapa = vigentes.get(etapa_id)
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
    # A Mesa: **todas e somente** as inscrições atribuídas a esta pessoa nesta Etapa (FR-020).
    # Quem chegou por gestão não tem Mesa — organizar o trabalho não é executá-lo —, e a página
    # continua sendo a da Etapa, dizendo por qual atribuição o ator chegou (011, D-006).
    linhas, pagina, contagens = (
        avaliacao_selectors.mesa(
            ator=ator,
            edital=edital,
            etapa_id=etapa_id,
            pagina=request.GET.get("pagina") or 1,
            filtro=request.GET.get("filtro") or None,
            vigentes=vigentes,
        )
        if por_alocacao
        else (None, None, None)
    )
    # A resposta carrega protocolo de candidato: é dado pessoal, e não fica no cache (FR-056).
    return marcar_como_privada(
        render(
            request,
            "interface/minha_etapa.html",
            {
                "edital": edital,
                "processo": edital.processo,
                "etapa": etapa,
                "evento": evento,
                "por_alocacao": por_alocacao,
                "por_gestao": por_gestao and not por_alocacao,
                "linhas": linhas,
                "pagina": pagina,
                "contagens": contagens,
                "filtro": request.GET.get("filtro") or "",
                # O que saiu desta Mesa, e por qual ato: a revogação é imediata e silenciosa, e
                # quem perdeu o trabalho era o único sem canal para saber por quê.
                "retiradas": (
                    avaliacao_selectors.retiradas_do_avaliador(
                        ator=ator, edital=edital, etapa_id=etapa_id
                    )
                    if por_alocacao
                    else []
                ),
            },
        )
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
