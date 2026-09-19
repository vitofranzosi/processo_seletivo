"""Views da interface administrativa.

Cada view invoca a camada de aplicação — nunca modelos direto, nunca a própria API por HTTP.
A decisão de autorização continua no backend: ocultar uma ação na tela é conveniência, não
fronteira de segurança (FR-002).
"""

import hashlib
import re
import secrets
from uuid import UUID, uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
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
from processo_seletivo.auditoria.models import RegistroAuditoria
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
from processo_seletivo.avaliacoes.domain.conjunto import recusa_por_inscricoes_em_curso
from processo_seletivo.avaliacoes.domain.previsao import forma_publicada, rotulos
from processo_seletivo.classificacao.application.corte import (
    calcular_corte,
    corte_por_id,
    divergencias_da_reproducao,
    estado_do_corte,
    geracao_do_corte,
    linha_do_quadro,
    nomes_do_corte,
    reproduzir_corte,
)
from processo_seletivo.classificacao.application.emissao import assinatura_da_proposta, emitir_ordem
from processo_seletivo.classificacao.application.emissao_do_corte import (
    assinatura_da_proposta as assinatura_do_corte,
)
from processo_seletivo.classificacao.application.emissao_do_corte import (
    continuar_corte,
    emitir_corte,
)
from processo_seletivo.classificacao.application.selectors import (
    ato_por_id,
    ato_vigente,
    atos_vigentes_por_marco,
    estado_do_marco,
    nomear_criterios,
    nomes_do_ato,
    posicoes_do_ato,
    sucessor_de,
)
from processo_seletivo.classificacao.application.selectors import (
    historico as historico_da_ordenacao,
)
from processo_seletivo.comissoes.application import alocacao as alocacao_app
from processo_seletivo.comissoes.application import comissao as comissao_app
from processo_seletivo.comissoes.application import selectors as comissao_selectors
from processo_seletivo.comissoes.domain.autorizacao import (
    pode_atuar_na_etapa,
    pode_gerir_comissao,
)
from processo_seletivo.comissoes.domain.etapas import (
    conteudo_vigente,
    etapa_vigente,
    etapas_vigentes,
    evento_vigente,
)
from processo_seletivo.comissoes.models import Funcao
from processo_seletivo.divulgacao.application.publicar import (
    assinatura_da_previa,
)
from processo_seletivo.divulgacao.application.publicar import (
    publicar_resultado as publicar_resultado_do_marco,
)
from processo_seletivo.divulgacao.application.selectors import (
    historico_do_marco as historico_das_publicacoes,
)
from processo_seletivo.divulgacao.application.selectors import (
    vigente_do_marco as publicacao_vigente_do_marco,
)
from processo_seletivo.divulgacao.domain.conteudo import compor as compor_divulgacao
from processo_seletivo.divulgacao.domain.publicabilidade import aferir as aferir_publicabilidade
from processo_seletivo.divulgacao.models import Natureza
from processo_seletivo.editais.application import anexos as anexos_command
from processo_seletivo.editais.application.draft import replace_draft
from processo_seletivo.editais.application.identificacao import update_edital_identification
from processo_seletivo.editais.application.reaproveitamento import (
    OPERACAO as OPERACAO_DE_REAPROVEITAMENTO,
)
from processo_seletivo.editais.application.reaproveitamento import (
    com_resumo_da_origem,
    o_que_sera_descartado,
    origens_elegiveis,
    rascunho_vazio,
    reaproveitar_edital,
)
from processo_seletivo.editais.application.requerimento import (
    atualizar_requerimento_de_matricula,
)
from processo_seletivo.editais.domain import marcos
from processo_seletivo.editais.domain.calendario import vencido
from processo_seletivo.editais.domain.perfis import listas_reservadas
from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    validate_for_publication,
)
from processo_seletivo.editais.models.anexos import ArtefatoAnexo
from processo_seletivo.editais.models.perfis import MarcoClassificatorio
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
from processo_seletivo.interface import supervisao as supervisao_do_processo
from processo_seletivo.interface.templatetags import interface_extras
from processo_seletivo.portal.arquivos import copia_verificada, entregar
from processo_seletivo.processos.application.commands import (
    add_edital,
    create_process_with_first_edital,
)
from processo_seletivo.processos.application.selectors import (
    contar_por_situacao,
    listar_processos,
    obter_edital,
)
from processo_seletivo.processos.domain.finalizacao import PROCESSO_FINAL, pending_editais
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from processo_seletivo.publicacoes.application.retificacoes import (
    advertencias_do_ato,
    conteudo_base,
    create_retification,
)
from processo_seletivo.publicacoes.application.selectors import (
    effective_version,
    homologar_fecharia_a_publicacao,
    impede_por_segregacao,
    participantes_do_edital,
)
from processo_seletivo.publicacoes.domain import autoridades
from processo_seletivo.publicacoes.infrastructure.pdf import MODO_PREVIA, render_edital_pdf
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.recursos.application import admitir as recursos_admitir
from processo_seletivo.recursos.application import julgar as recursos_julgar
from processo_seletivo.recursos.application import selectors as recursos_selectors
from processo_seletivo.recursos.domain.elegibilidade import RAZOES, impedimento
from processo_seletivo.recursos.domain.janela import janela_declarada
from processo_seletivo.recursos.models import Recurso
from processo_seletivo.requerimentos.domain import nomes as nomes_do_requerimento
from processo_seletivo.resultados.application import consolidacao as consolidacao_app
from processo_seletivo.resultados.application import ocorrencia as ocorrencia_app
from processo_seletivo.resultados.application import prontidao as prontidao_013
from processo_seletivo.resultados.application import selectors as resultado_selectors
from processo_seletivo.seguranca.application.authorization import (
    Base,
    base_de_permissao,
    require_authorization_base,
    require_permission,
)
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.arquivos import aceitar, tamanho_legivel
from processo_seletivo.shared.http import marcar_como_privada
from processo_seletivo.shared.tempo import ZONA as ZONA_INSTITUCIONAL

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


@require_http_methods(["GET", "POST"])
def criar_edital(request, processo_id):
    """O segundo Edital do mesmo Processo — o modelo sempre admitiu, e faltava a porta (FR-005).

    Um Processo reúne Editais que podem ter cronogramas próprios, e `add_edital` já existia
    atendendo à API desde a `002`. Pela interface, porém, o único caminho até um Edital era a tela
    que cria o Processo: quem conduzia o certame terminava com o Edital com que o Processo nasceu,
    e acrescentar o segundo exigia sair do sistema.

    **A recusa por estado final fica com o comando.** `ensure_processo_accepts_changes` é quem
    decide, e repetir a regra aqui criaria a segunda derivação que divergiria dela; o que a tela
    faz é não oferecer o botão, que é outra coisa.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    processo = _processo_do_ator(ator, processo_id)
    if not ator.can("edital:criar"):
        # O mesmo 404 que a composição devolve: distinguir "não existe" de "você não pode" diria a
        # quem não alcança que o Processo existe.
        raise Http404

    contexto = {
        "processo": processo,
        "digitado": request.POST if request.method == "POST" else {},
        "ano_corrente": timezone.localtime().year,
        # A chave atravessa o reenvio do formulário: recarregar depois de um erro de preenchimento
        # não pode criar dois Editais quando a segunda tentativa der certo.
        "chave_idempotencia": request.POST.get("chave_idempotencia") or f"ui-{uuid4().hex}",
    }
    if request.method == "GET":
        return render(request, "interface/edital_criar.html", contexto)

    def recusado(recusas, status):
        return render(
            request,
            "interface/edital_criar.html",
            _com_recusas(contexto, recusas),
            status=status,
        )

    try:
        edital, _ = add_edital(
            actor=ator,
            processo_id=processo.id,
            data=_edital_do_formulario(request.POST),
            idempotency_key=request.POST.get("chave_idempotencia", ""),
            correlation_id=request.correlation_id,
        )
    except RecusaDoFormulario as exc:
        return recusado(exc.recusas, 422)
    except ValueError as exc:
        # Recusa sem campo conhecido continua em texto: apontar um campo qualquer seria pior.
        return recusado([{"mensagem": str(exc), "ancora": ""}], 422)
    except DomainError as exc:
        return recusado(
            [{"mensagem": exc.detail, "ancora": CAMPO_DO_CONFLITO.get(exc.code, "")}], exc.status
        )
    # Para o Edital recém-criado, e **não** para `compor`: `edital:criar` é do Gestor e
    # `edital:elaborar` não — mandá-lo direto à composição daria 404 justamente a quem acabou de
    # criar o Edital. A página do Edital sabe dizer as duas coisas: oferece elaborar a quem elabora
    # e nomeia a espera a quem não elabora.
    return redirect(reverse("interface:detalhe", args=[edital.id]))


# Os campos obrigatórios, separados por agregado porque **duas telas** os preenchem: a criação do
# Processo pede os dois grupos de uma vez, e o Edital acrescentado a um Processo que já existe pede
# só o segundo. Uma lista única obrigaria a segunda tela a exigir o que ela não tem o que fazer com.
CAMPOS_DO_PROCESSO = {
    "codigo": "Identificação institucional",
    "titulo": "Título do Processo",
}
CAMPOS_DO_EDITAL = {
    "numero": "Número do Edital",
    "ano": "Ano do Edital",
    "titulo_edital": "Título do Edital",
}

# (campo do formulário, rótulo, modelo, campo do modelo). O limite vem de `_meta` em vez de ser
# repetido aqui: campo maior que a coluna vira erro 500 no PostgreSQL, e um número copiado à mão
# se desatualiza em silêncio na primeira migration que mudar o tamanho.
TEXTOS_DO_PROCESSO = (
    ("codigo", "Identificação institucional", ProcessoSeletivo, "institutional_code"),
    ("titulo", "Título do Processo", ProcessoSeletivo, "title"),
)
TEXTOS_DO_EDITAL = (
    ("numero", "Número do Edital", Edital, "number"),
    ("titulo_edital", "Título do Edital", Edital, "title"),
)
TEXTOS_DA_CRIACAO = TEXTOS_DO_PROCESSO + TEXTOS_DO_EDITAL
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


def _recusar(recusas):
    """Interrompe se houver o que recusar. Existe para que cada verificação caiba numa linha."""
    if recusas:
        raise RecusaDoFormulario(recusas)


def _vazios(dados, campos):
    """Uma recusa **por campo**, e não uma frase agregada (FR-033).

    "Preencha: A, B, C." obriga a pessoa a reencontrar cada um dos três; com a recusa presa ao
    campo, o resumo leva até ele.
    """
    return [
        {"mensagem": f"{rotulo} é obrigatório.", "ancora": chave}
        for chave, rotulo in campos.items()
        if not (dados.get(chave) or "").strip()
    ]


def _excedidos(dados, textos):
    return [
        {
            "mensagem": (
                f"{rotulo} excede o máximo de "
                f"{modelo._meta.get_field(campo).max_length} caracteres."
            ),
            "ancora": chave,
        }
        for chave, rotulo, modelo, campo in textos
        if len(dados[chave].strip()) > modelo._meta.get_field(campo).max_length
    ]


def _ano_do_formulario(dados):
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
    return ano


def _edital_do_formulario(dados):
    """Os campos do Edital, traduzidos para o comando.

    Compartilhado com a criação do Processo porque é o **mesmo** Edital: a tela que abre o Processo
    cria o primeiro e a que o acrescenta cria o segundo, e duas validações separadas divergiriam na
    primeira migration que mudasse o tamanho de uma coluna.
    """
    _recusar(_vazios(dados, CAMPOS_DO_EDITAL))
    _recusar(_excedidos(dados, TEXTOS_DO_EDITAL))
    return {
        "number": dados["numero"].strip(),
        "year": _ano_do_formulario(dados),
        "title": dados["titulo_edital"].strip(),
        "description": (dados.get("descricao") or "").strip(),
    }


def _processo_do_formulario(dados):
    """Traduz o formulário e recusa o que a persistência não aguentaria (FR-020/SC-007).

    A tela nova entrava direto no command, sem passar pelo serializer que a API usa: o que
    excedesse a coluna atravessava a borda e voltava como 500. Quem decide continua sendo o
    domínio; o que se faz aqui é não deixar o erro chegar ao banco sem forma.

    **Os dois grupos são conferidos juntos, antes de delegar ao do Edital.** Conferir o Processo e
    só depois o Edital devolveria os campos faltantes em duas rodadas — a pessoa corrigiria dois e
    descobriria outros três no reenvio, que é exatamente o que a recusa por campo existe para
    evitar.
    """
    _recusar(_vazios(dados, {**CAMPOS_DO_PROCESSO, **CAMPOS_DO_EDITAL}))
    _recusar(_excedidos(dados, TEXTOS_DA_CRIACAO))
    return {
        "institutionalCode": dados["codigo"].strip(),
        "title": dados["titulo"].strip(),
        "firstEdital": _edital_do_formulario(dados),
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
    "attachments": ("anexos", "#anexos-lista", True),
    # O marco vive **dentro** do Perfil, e por isso a busca por coleção o mandava para `perfis`:
    # toda pendência de marco terminava numa tela sem marco nenhum, que é a única do assistente
    # onde o conteúdo não se corrige. A etapa que o trata é `classificacao`, e reconhecê-la exige
    # olhar o caminho inteiro — o segmento de coleção sozinho não distingue um do outro.
    "classificationMilestones": ("classificacao", "#titulo-classificacao", True),
    # O texto da declaração do Requerimento de Matrícula (029). É campo de **raiz**, como `title`,
    # e se resolve na etapa `Inscrição`, que é onde ele é composto. Sem esta linha a pendência
    # cairia em `(None, "", False)` e apareceria como **não corrigível** — o sistema apontaria um
    # defeito e informaria que não há caminho, que é exatamente o que a `FR-007` proíbe e o que a
    # Identificação sofreu antes de ganhar ato próprio.
    "matriculationRequest/declarationText": ("inscricao", "#inscricao-requerimento", True),
}

# Pendência do marco que **não** se resolve no marco. O peso é campo da Etapa, e a Etapa é quem o
# declara; mandar para a Classificação faria a pessoa procurar, no cartão do marco, um controle que
# está a duas telas dali. É a única exceção, e por isso é por código do achado, e não por caminho.
DESTINO_POR_CODIGO = {
    "milestone_stage_without_weight": ("etapas", "#etapas-titulo", True),
}


def _destino(caminho, codigo=""):
    """A etapa onde o achado se resolve.

    Achado de raiz vem com o nome da coleção (`profiles`); achado de forma vem com o caminho da
    entidade (`/profiles/id=…/name`). Os dois se resolvem no mesmo lugar, e resolver só o primeiro
    faria a pendência mais específica — a que já diz qual campo corrigir — ser a única sem caminho.

    O `codigo` vence o caminho quando o campo a corrigir mora em outra etapa que não a do conteúdo
    que o achado endereça.
    """
    if codigo in DESTINO_POR_CODIGO:
        return DESTINO_POR_CODIGO[codigo]
    if caminho in DESTINO_DA_PENDENCIA:
        return DESTINO_DA_PENDENCIA[caminho]
    # Do mais específico para o mais geral: o marco é a coleção mais profunda do caminho, e a
    # primeira — `profiles` — é a mais rasa. Ler de trás para frente é o que faz a pendência do
    # marco chegar à Classificação em vez de parar nos Perfis.
    for segmento in reversed(caminho.split("/")):
        if segmento in DESTINO_DA_PENDENCIA:
            return DESTINO_DA_PENDENCIA[segmento]
    return (None, "", False)


# Caminho que a tradução não conhece — os da forma publicada, por exemplo — não ganha destino nem
# explicação inventada. FR-007 proíbe declarar incorrigível o que a etapa resolve; não obriga a
# justificar o que ninguém mapeou.
MOTIVO_SEM_DESTINO = "não há etapa do assistente que trate deste conteúdo"


def _pendencias(edital, *, agora=None):
    """FR-008 e FR-027: o que falta para submeter, e onde cada coisa se resolve.

    **`agora` é recebido, e não lido aqui, quando a página também desenha o selo das etapas**
    (`028`, FR-341). O selo do Cronograma e estas pendências respondem à mesma pergunta — que
    Eventos venceram —, e dois relógios lidos na mesma requisição podem discordar: a etapa
    apareceria pendente sem a explicação correspondente, que é o que a UX-049 proíbe. Quem não tem
    selo a desenhar continua chamando sem o argumento.
    """
    rotulos = {chave: rotulo for chave, rotulo, _ in ETAPAS_COMPOSICAO}
    pendencias = []
    agora = agora or timezone.now()
    for item in validate_for_publication(
        edital_snapshot(edital), ato=ATO_DE_PUBLICACAO, agora=agora
    ):
        etapa, ancora, corrigivel = _destino(item.path, item.code)
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
    # Depois das Etapas, e pela mesma razão que a `inscricao` veio depois do Cronograma: o marco
    # **enumera** Etapas e seus critérios apontam Etapa e fato declarado. Oferecê-lo no passo dos
    # Perfis, que vem antes, seria oferecer uma lista vazia e chamá-la de escolha — e foi assim que
    # a primeira redação o colocou (015, T072).
    ("classificacao", "Classificação", "interface/compor_classificacao.html"),
    ("inscricao", "Inscrição", "interface/compor_inscricao.html"),
    # Depois da Inscrição, porque é o requisito que aponta o modelo — oferecer os anexos antes
    # seria oferecê-los sem o que eles servem. **Fora de `ETAPAS_GRAVAVEIS`**: a coleção não viaja
    # no `replace_draft`, e cada operação tem comando próprio (020, R-006).
    ("anexos", "Anexos", "interface/compor_anexos.html"),
    # Depois de tudo o que gera conteúdo: as seções textuais complementam o que o sistema já
    # sabe, e quem as redige precisa ver o que já está estruturado.
    ("conteudo", "Conteúdo", "interface/compor_conteudo.html"),
    ("revisao", "Revisão", "interface/compor_revisao.html"),
]
CHAVES_ETAPA = [chave for chave, _, _ in ETAPAS_COMPOSICAO]
# As que aceitam POST. `revisao` consolida e não grava.
ETAPAS_GRAVAVEIS = {
    "identificacao",
    "perfis",
    "cronograma",
    "etapas",
    "classificacao",
    "inscricao",
    "conteudo",
}


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
    "classificacao": "marco",
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
        # A linha do quadro é entidade **dentro** do Perfil, e a recusa nomeia a linha, não o
        # Perfil. Sem esta descida a mensagem viraria texto solto no resumo, e quem compõe um
        # Edital de sete polos teria de procurar em qual deles o número não fecha (025, UX-023).
        #
        # O índice vem de `quadro_do_formulario`, que é o que a tela **desenha** — e não da lista
        # lida do POST, que já descartou as linhas em branco. Contar na lista lida daria o `id` de
        # um controle que não existe, e a âncora apontaria para o nada.
        if not linha.get("vacancyTable"):
            continue
        oferecidas = forms.quadro_do_formulario(linha)
        for sub, do_quadro in enumerate(oferecidas):
            if str(do_quadro.get("id", "")) == identidade:
                return {"mensagem": mensagem, "ancora": f"linha-{indice}-{sub}-{campo}"}
        # **A linha recusada pode não estar entre as oferecidas**, e o caso é justamente o da
        # duplicata: a tela oferece uma linha por recorte, e a segunda linha do mesmo recorte não
        # tem onde aparecer. A âncora recua para a linha **daquele recorte** — que é onde a pessoa
        # corrige o problema —, em vez de virar texto solto no resumo (025, E2E25-003).
        recusada = next(
            (item for item in linha["vacancyTable"] if str(item.get("id", "")) == identidade),
            None,
        )
        if recusada is None:
            continue
        recorte = str(recusada.get("modalityId") or "")
        for sub, do_quadro in enumerate(oferecidas):
            if str(do_quadro.get("modalityId") or "") == recorte:
                return {"mensagem": mensagem, "ancora": f"linha-{indice}-{sub}-{campo}"}
    return {"mensagem": mensagem, "ancora": ""}


def _eventos_do_cronograma(edital):
    """Os Eventos do Cronograma, **numa consulta**, para serem passados adiante.

    A página da etapa precisa deles duas vezes — o selo pergunta se algum venceu, a frase diz
    quantos venceram —, e buscá-los duas vezes era consulta a mais contra a restrição que o plano
    declara. Lidos aqui uma vez, os dois cálculos trabalham sobre a mesma lista, que é também o que
    garante que o número exibido e o selo falem do mesmo cronograma.
    """
    cronograma = getattr(edital, "cronograma", None)
    return list(cronograma.eventos.all()) if cronograma is not None else []


def _vencidos_entre(eventos, *, agora):
    """Quais daqueles Eventos já passaram, pelo predicado do domínio."""
    return [evento for evento in eventos if vencido(evento.start_at, evento.end_at, agora=agora)]


def _estado_do_cronograma(edital, *, agora=None, eventos=None):
    """Concluída quando há Evento e nenhum deles venceu (`028`, FR-359, FR-360).

    Pendente **não impede nada** (FR-362): o selo orienta quem retoma o trabalho, e quem fecha porta
    é o achado impeditivo do período de inscrições encerrado. E como o estado é derivado e não
    persistido, ele volta sozinho assim que as datas são corrigidas — que é também o que o faz estar
    certo na primeira abertura depois do reaproveitamento, sem gravação nenhuma.

    `eventos` evita a segunda consulta quando quem chama já os tem; sem ele, busca por conta
    própria — é o que mantém a função utilizável sozinha, de teste e de shell.
    """
    eventos = _eventos_do_cronograma(edital) if eventos is None else eventos
    if not eventos:
        return PENDENTE
    if _vencidos_entre(eventos, agora=agora or timezone.now()):
        return PENDENTE
    return CONCLUIDA


def _progresso(edital, atual, *, agora=None, eventos_do_cronograma=None):
    """Cada etapa sabe se já está resolvida — o que orienta quem retoma o trabalho depois."""
    estados = {
        "identificacao": CONCLUIDA,
        "perfis": CONCLUIDA if edital.perfis.exists() else PENDENTE,
        # **Concluída passou a significar "válida", e não "tem Evento"** (`028`, FR-359). O critério
        # era `eventos.exists()`, e por isso um Edital criado a partir de outro nascia com o
        # Cronograma concluído carregando o cronograma inteiro da oferta anterior — todas as nove
        # etapas verdes, e um período de inscrições do ano passado já encerrado.
        #
        # O predicado é o mesmo que a conferência de publicação usa; ele mora em
        # `editais/domain/calendario.py` justamente para que o selo e a Revisão não possam discordar
        # sobre o mesmo cronograma. A leitura é em Python, e não um filtro no banco, pela mesma
        # razão: um `Q(start_at__lt=...)` poria a regra numa expressão que o domínio não alcança.
        #
        # **O ano não entra aqui.** Divergência de ano é advertência; apagar o selo por ela daria a
        # um Edital legítimo de dezembro a aparência de incompleto.
        "cronograma": _estado_do_cronograma(edital, agora=agora, eventos=eventos_do_cronograma),
        # Etapas são opcionais; "concluída" aqui quer dizer "já tem conteúdo", não "obrigatória".
        "etapas": CONCLUIDA if edital.etapas.exists() else PENDENTE,
        # Como `etapas`: um Edital pode não classificar, e nesta versão isso é legítimo. "Concluída"
        # diz "já tem marco", e não "é obrigatório ter".
        "classificacao": CONCLUIDA
        if MarcoClassificatorio.objects.filter(perfil__edital=edital).exists()
        else PENDENTE,
        # `SecaoEdital` só tem linha depois da primeira edição — ausência de linha significa "texto
        # padrão do catálogo". Logo `exists()` responde exatamente "esta etapa já foi gravada",
        # sem custar estado novo.
        # Como `etapas`: o contrato de inscrição é opcional nesta versão — um Edital pode ser
        # publicado sem receber inscrições pelo sistema —, e "concluída" diz "já tem conteúdo".
        "inscricao": CONCLUIDA
        if edital.documentos_exigidos.exists() or forms.periodo_do_edital(edital)
        else PENDENTE,
        # Como `etapas`: Edital sem anexo é legítimo, e "concluída" diz "já tem", não "é
        # obrigatório ter" (FR-024).
        "anexos": CONCLUIDA if edital.anexos.exists() else PENDENTE,
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


# Quem pode ler o artefato de um Edital que ainda não foi publicado (020, FR-017). É a lista da
# regra, e não a dos papéis que "fariam sentido": `edital:publicar` não está aqui porque a FR-017
# nomeia elaboração, revisão e homologação, e alargar a regra por conveniência é como uma fronteira
# de autorização se perde.
LEITURA_DO_RASCUNHO = ("edital:elaborar", "edital:submeter", "edital:homologar")


@require_http_methods(["POST"])
def anexos_acao(request, edital_id):
    """As cinco operações sobre a coleção de Anexos, numa rota só (020, FR-015).

    Uma rota e não cinco porque as cinco são a mesma decisão de quem elabora — "como este Edital
    publica os seus anexos" —, e porque a fronteira que importa não é a rota: é o comando, que
    verifica `edital:elaborar` e o estado do Edital **depois** de travar a linha.

    A view não decide nada. Ela lê o formulário, chama o comando e volta para a etapa; a recusa
    volta pela mensagem, no lugar onde a pessoa estava.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404
    acao = request.POST.get("acao", "")
    destino = f"{reverse('interface:compor-etapa', args=[edital.id, 'anexos'])}"
    comum = {
        "actor": ator,
        "edital_id": edital.id,
        "expected_revision": edital.revision,
        "correlation_id": request.correlation_id,
    }
    try:
        if acao == "anexar":
            arquivo = request.FILES.get("arquivo")
            if arquivo is None:
                raise DomainError("file_required", "Escolha o arquivo do anexo.", 422)
            anexos_command.anexar(**comum, arquivo=arquivo, rotulo=request.POST.get("rotulo", ""))
        elif acao == "substituir":
            arquivo = request.FILES.get("arquivo")
            if arquivo is None:
                raise DomainError("file_required", "Escolha o arquivo do anexo.", 422)
            anexos_command.substituir(
                **comum, anexo_id=request.POST.get("anexo", ""), arquivo=arquivo
            )
        elif acao == "rotular":
            anexos_command.rotular(
                **comum,
                anexo_id=request.POST.get("anexo", ""),
                rotulo=request.POST.get("rotulo", ""),
            )
        elif acao == "mover":
            anexos_command.mover(
                **comum,
                anexo_id=request.POST.get("anexo", ""),
                direcao=request.POST.get("direcao", ""),
            )
        elif acao == "reordenar":
            anexos_command.reordenar(**comum, ordem=request.POST.getlist("ordem"))
        elif acao == "remover":
            anexos_command.remover(**comum, anexo_id=request.POST.get("anexo", ""))
        else:
            raise Http404
    except DomainError as exc:
        # A recusa volta pela **sessão**, e não pela query string: a mensagem inteira no endereço
        # sobrevive a recarregar, a compartilhar e ao histórico do navegador, e não é conteúdo de
        # endereço nenhum. Junto vai o que a pessoa digitou, para que escolher o arquivo errado não
        # custe redigitar o rótulo.
        request.session["anexos_recusa"] = {
            "mensagem": exc.detail,
            "rotulo": request.POST.get("rotulo", ""),
            "anexo": request.POST.get("anexo", ""),
        }
        return redirect(destino)
    return redirect(f"{destino}?salvo=anexos")


@require_http_methods(["GET"])
def anexo_do_rascunho(request, edital_id, anexo_id):
    """Os bytes do anexo antes da publicação, para quem elabora, revisa e homologa (FR-017, FR-018).

    Conferir bytes que não se pode abrir não é conferir. Mas o artefato de Edital não publicado
    **não é conteúdo público**, e estar autenticado no mesmo escopo institucional não basta: a
    primeira redação desta view conferia só isso, e entregava o rascunho a gestor, publicador,
    auditor e a qualquer identidade da casa. Escopo diz **de quem é** o Edital; capacidade diz
    **quem pode** vê-lo antes de ele existir para o público.

    As três capacidades são as que a FR-017 nomeia, e nenhuma a mais. `edital:publicar` fica de
    fora porque a regra escrita diz "elaboração, revisão ou homologação" — incluí-la é decisão de
    produto, e não de implementação.

    A recusa é **404**, e não 403: dizer "existe, mas você não pode" já entregaria que existe, que
    é a mesma régua de `exigir_titularidade` na `009`.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404
    if not any(ator.can(capacidade) for capacidade in LEITURA_DO_RASCUNHO):
        raise Http404
    anexo = edital.anexos.select_related("artefato").filter(pk=anexo_id).first()
    if anexo is None:
        raise Http404
    resposta = HttpResponse(bytes(anexo.artefato.bytes), content_type=anexo.artefato.content_type)
    resposta["Content-Disposition"] = f'inline; filename="{anexo.artefato.nome_original}"'
    return marcar_como_privada(resposta)


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
                    # **Antes de gravar**, porque a gravação é quem sobrescreve: a derivação
                    # reafirma a linha geral com o total, e quem digitou outro número precisa saber
                    # que ele saiu (027, FR-322).
                    rederivadas = _linhas_gerais_rederivadas(etapa, digitados)
                    _gravar_etapa(request, ator, edital, etapa, digitados)
                    if rederivadas:
                        request.session["quadro_rederivado"] = rederivadas
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
    # **Um instante para a página inteira** (`028`, FR-341). O selo da etapa Cronograma e as
    # pendências respondem à mesma pergunta, e um Evento que vencesse entre as duas leituras faria
    # a página exibir a etapa pendente sem a explicação que diz por quê — a UX-049 exige as duas
    # juntas, e a única forma de garanti-lo é as duas olharem o mesmo relógio.
    agora = timezone.now()
    pendencias = _pendencias(edital, agora=agora)
    # A frase que liga os avisos ao selo, e só na etapa que a exibe (`028`, UX-049). O selo diz
    # PENDENTE; sem isto, quem lê vê os avisos logo abaixo e precisa ligar as duas coisas sozinho.
    # A lista é pedida — e não um booleano — porque a frase diz **quantos** Eventos a mantêm assim.
    eventos_do_cronograma = _eventos_do_cronograma(edital)
    vencidos = _vencidos_entre(eventos_do_cronograma, agora=agora) if etapa == "cronograma" else []
    # A conferência é lida do conteúdo canônico, e não montada bloco a bloco no template: é o que
    # impede a Revisão de envelhecer quando uma coleção nova entra no Edital.
    conferencia = revisao.blocos(edital_snapshot(edital)) if etapa == "revisao" else []
    anexos = _anexos_da_etapa(edital) if etapa == "anexos" else []
    recusa_de_anexo = request.session.pop("anexos_recusa", None) if etapa == "anexos" else None
    # **Consumido em qualquer etapa, e não só na dos Perfis.** "Avançar" grava uma etapa e abre a
    # seguinte: preso ao destino `perfis`, o aviso não aparecia para quem avança — e ficava na
    # sessão esperando uma visita futura, onde surgiria já obsoleto, falando de uma gravação que
    # ninguém lembra. Notícia do que acabou de acontecer não sobrevive à próxima tela (FR-322).
    rederivadas = request.session.pop("quadro_rederivado", None)
    perfis = (
        _reexibir_perfis(digitados)
        if etapa == "perfis" and digitados is not None
        else _reexibir_classificacao(edital, digitados)
        if etapa == "classificacao" and digitados is not None
        else forms.perfis_do_edital(edital)
    )
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
            "anexos": anexos,
            "recusa_de_anexo": recusa_de_anexo,
            # O que a derivação reafirmou nesta gravação (027, FR-322). Sobrescrever em silêncio
            # seria trocar um defeito por outro: quem repartiu 60 na ampla e removeu a última lista
            # reservada precisa ver que a ampla voltou a ser o total.
            "quadro_rederivado": rederivadas,
            "progresso": _progresso(
                edital, etapa, agora=agora, eventos_do_cronograma=eventos_do_cronograma
            ),
            "cronograma_vencidos": vencidos,
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
            "perfis": perfis,
            # O prefixo dos campos do primeiro marco desta tela — `marco-<perfil>-0` (030,
            # FR-426, FR-427). **Vazio significa que não há marco**, e é o que faz o bloco de
            # ajuda da etapa não ser apresentado: ajuda sobre campos que ninguém tem à frente é
            # pior que ruído, porque ensina a preencher o que não existe.
            #
            # É também a âncora de cada item do bloco. Do **primeiro** marco, e não de todos: o
            # bloco é da etapa, e um por marco reintroduziria a repetição que trazê-lo para cá
            # veio resolver — num Edital de três Perfis, três blocos idênticos.
            "ancora_do_marco": _ancora_do_primeiro_marco(perfis)
            if etapa == "classificacao"
            else "",
            # O método do sorteio comum ao Edital (030, FR-429): o passo o oferece uma vez, e cada
            # cartão de marco o referencia em vez de redigitá-lo.
            #
            # **Depois de uma recusa, o que volta é o digitado**, e não o gravado — a mesma regra
            # dos marcos, logo acima, e pela mesma razão. A validação do método acontece antes da
            # gravação: ler o banco aqui devolveria os nove campos vazios a quem esqueceu um deles,
            # e a recusa existe para corrigir o que se errou, não para apagar o que se acertou.
            "metodo_comum": (
                forms.metodo_comum_digitado(request.POST)
                if etapa == "classificacao" and digitados is not None
                else forms.metodo_comum_para_exibicao(edital)
                if etapa == "classificacao"
                else {}
            ),
            "tem_metodo_comum": (
                bool(forms.metodo_comum_do_formulario(request.POST))
                if etapa == "classificacao" and digitados is not None
                else bool(edital.metodo_de_sorteio_comum)
            ),
            "eventos": (
                _reexibir_eventos(digitados)
                if etapa == "cronograma" and digitados is not None
                else forms.eventos_do_edital(edital)
            ),
            # A sugestão de local: o do evento anterior, se houver (021, FR-059). Ela vive no
            # `placeholder` e **não** preenche o campo — sugerir é da tela, presumir é do conteúdo
            # publicado.
            "sugestao_de_local": forms.ultimo_local_declarado(edital),
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
            # Após recusa, o que a pessoa digitou; fora disso, o que está gravado — a mesma regra
            # das demais etapas, e o que impede a recusa apagar o preenchimento (029, T047).
            "requerimento_momento": (
                digitados["requerimento_momento"]
                if etapa == "inscricao" and digitados is not None
                else edital.requerimento_momento
            ),
            "requerimento_declaracao": (
                digitados["requerimento_declaracao"]
                if etapa == "inscricao" and digitados is not None
                else edital.requerimento_declaracao
            ),
            "momentos_do_requerimento": MOMENTOS_DO_REQUERIMENTO,
            "alcance": forms.alcance_da_aplicabilidade(edital) if etapa == "inscricao" else [],
            "anexos_do_edital": (forms.anexos_do_edital(edital) if etapa == "inscricao" else []),
            # As listas que o marco e o critério escolhem. Só no passo da classificação: montá-las
            # em toda tela custaria duas consultas por render sem servir a nenhuma delas.
            "etapas_classificatorias": (
                _etapas_e_fatos_do_edital(edital)[0] if etapa == "classificacao" else []
            ),
            # Todas as Etapas, para a Etapa governada pelo corte: ela não precisa classificar
            # (014, FR-224).
            "etapas_governaveis": (_etapas_governaveis(edital) if etapa == "classificacao" else []),
            "fatos_declarados": (
                _etapas_e_fatos_do_edital(edital)[1] if etapa == "classificacao" else []
            ),
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
            # Partir de um Edital anterior só é oferecido onde é possível: rascunho vazio e
            # permissão de elaborar (023, FR-001, FR-002). Oferecer o que se vai recusar é pior do
            # que não oferecer — e a conta das seis coleções só é paga na etapa que exibe o cartão.
            "pode_reaproveitar": (editavel and etapa == CHAVES_ETAPA[0] and rascunho_vazio(edital)),
            # O aviso permanente, em todas as etapas: este Edital partiu de outro, e as informações
            # são da oferta anterior até alguém atualizá-las (023, FR-014).
            "origem_reaproveitada": _origem_reaproveitada(edital),
        },
    )


@require_http_methods(["GET", "POST"])
def reaproveitar(request, edital_id):
    """Escolher o Edital de onde partir, e partir (023, US1).

    A view não decide nada: lista as origens elegíveis, lê dois campos e chama o comando. Os dois
    campos são a origem e a chave de idempotência — `forms.py` existe para reconstruir coleções a
    partir de campos indexados, e aqui não há coleção.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404
    composicao = reverse("interface:compor-etapa", args=[edital.id, CHAVES_ETAPA[0]])
    # **Antes do comando, só o que não muda com a operação**: a permissão de elaborar e o escopo,
    # que são autorização. Situação do Edital, Processo e rascunho vazio ficam **inteiramente** para
    # o serviço, depois da reserva da chave (`FR-017a`, `§7.1`).
    #
    # A razão é a mesma que moveu a reserva para antes das precondições, e vale para todas elas, não
    # só para o rascunho: a operação muda o estado que seria conferido. Depois da primeira cópia o
    # rascunho tem conteúdo — e o Edital pode até ter avançado de situação, se alguém o submeteu no
    # intervalo. Barrar o reenvio aqui devolveria 404 onde a reserva já tem resposta pronta.
    if not ator.can("edital:elaborar"):
        raise Http404
    # A exibição é outra conversa: o que a tela oferece precisa ser o que a tela consegue fazer.
    # **Rascunho cheio não fecha mais a porta**, ele muda o que a porta avisa: escolher outra origem
    # substitui o que está aqui, e o que se perde é enumerado antes de se perder (D-009).
    if request.method == "GET" and edital.status != Edital.Status.EM_ELABORACAO:
        raise Http404
    vazio = rascunho_vazio(edital)

    erros = []
    if request.method == "POST":
        origem_id = request.POST.get("origem", "")
        confirmada = bool(request.POST.get("confirmar_troca"))
        chave = request.POST.get("chave_idempotencia", "")
        try:
            reaproveitar_edital(
                actor=ator,
                edital_id=edital.id,
                origem_id=origem_id,
                expected_revision=edital.revision,
                idempotency_key=chave,
                correlation_id=request.correlation_id,
                substituindo=confirmada,
            )
        except DomainError as exc:
            # **A tela de confirmação é a recusa apresentada na forma em que se pode agir sobre
            # ela**, e não uma segunda verificação da mesma precondição. A ordem importa por uma
            # razão que já custou dois defeitos: perguntar antes de chamar o comando faria a
            # repetição conhecida — mesma chave, cópia já feita — cair na pergunta em vez de
            # terminar onde a primeira terminou. Quem sabe se é repetição é a reserva, e ela mora
            # no comando.
            #
            # A lista é o requisito: descartar em silêncio e reaproveitar em silêncio são os dois
            # erros simétricos, e enumerar o que se perde antes de perder é o que evita os dois
            # (`portal/descarte.html`, e agora aqui).
            origem = (
                origens_elegiveis(ator, excluindo=edital.pk).filter(pk=origem_id).first()
                if exc.code == "draft_not_empty" and not confirmada
                else None
            )
            if origem is not None:
                return render(
                    request,
                    "interface/reaproveitar_confirmar.html",
                    {
                        "edital": edital,
                        "origem": com_resumo_da_origem([origem])[0],
                        "descarte": o_que_sera_descartado(edital),
                        "chave_idempotencia": chave,
                        "voltar": reverse("interface:reaproveitar", args=[edital.id]),
                    },
                )
            erros.append({"mensagem": exc.detail, "ancora": ""})
        else:
            return redirect(f"{composicao}?salvo=reaproveitamento")

    from django.core.paginator import Paginator

    busca = (request.GET.get("busca") or "").strip()
    origens = origens_elegiveis(ator, excluindo=edital.pk, busca=busca)
    # Paginada porque o acervo só cresce: a lista é de **todos** os Editais publicados do escopo, e
    # uma instituição com alguns anos de casa tem centenas. O tamanho é o das demais listas da
    # gestão.
    paginas = Paginator(origens, 20)
    pagina = paginas.get_page(request.GET.get("pagina") or 1)
    return render(
        request,
        "interface/reaproveitar.html",
        {
            "edital": edital,
            "pagina": pagina,
            # O que cada origem traz, contado no conteúdo que vigora — só da página exibida, que é
            # o que separa duas consultas de uma por linha.
            "origens": com_resumo_da_origem(pagina.object_list),
            "busca": busca,
            "total": paginas.count,
            # A pergunta que trouxe a pessoa até aqui viaja com a paginação: avançar de página não
            # pode desfazer o filtro.
            "filtro": urlencode({"busca": busca}) if busca else "",
            "vazio": vazio,
            # O que a escolha vai substituir, quando houver o que substituir.
            "descarte": None if vazio else o_que_sera_descartado(edital),
            "erros": erros,
            "voltar": composicao,
            # A chave atravessa o reenvio do formulário, como nas telas de criação: recarregar
            # depois de uma recusa não pode produzir duas cópias.
            "chave_idempotencia": request.POST.get("chave_idempotencia") or f"ui-{uuid4().hex}",
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
            # As linhas nascem das Modalidades **do formulário**, e não das gravadas: a recusa que
            # esta tela está mostrando pode ter sido causada por uma Modalidade que ainda não
            # existe no banco, e derivar dali devolveria a tela sem o que a pessoa digitou (R-009).
            "quadro": forms.quadro_do_formulario(perfil),
            # Pela mesma razão: a lista reservada que faz o bloco existir pode ter sido acrescentada
            # neste envio, e ainda não estar no banco. Lida do formulário, a tela volta com o bloco
            # que a pessoa tinha na frente quando a recusa aconteceu (027, FR-321).
            "tem_lista_reservada": bool(listas_reservadas(perfil)),
        }
        for perfil in perfis
    ]


def _ancora_do_primeiro_marco(perfis):
    """`marco-<perfil>-0` do primeiro Perfil que tem marco; `""` quando nenhum tem (030, FR-426)."""
    for perfil in perfis or []:
        if perfil.get("marcos"):
            return f"marco-{perfil['id']}-0"
    return ""


def _reexibir_classificacao(edital, marcos_por_perfil):
    """Funde o digitado sobre os Perfis persistidos depois de uma recusa.

    O POST deste passo traz somente os marcos. Voltar a consultar `perfis_do_edital` sem esta
    transformação fazia a resposta 200 descartar visualmente tudo o que a pessoa acabara de
    preencher, embora o domínio tivesse recusado justamente para que ela pudesse corrigir.
    """
    perfis = forms.perfis_do_edital(edital)
    for perfil in perfis:
        digitados = marcos_por_perfil.get(perfil["id"], [])
        perfil["marcos"] = [_reexibir_marco(marco) for marco in digitados]
    return perfis


def _reexibir_marco(marco):
    arredondamento = marco.get("rounding") or {}
    return {
        "id": marco.get("id", ""),
        "code": marco.get("code", ""),
        "name": marco.get("name", ""),
        # Sem esta linha, uma recusa devolveria o cartão sem a resposta de entrada — e o cartão
        # sem resposta esconde tudo o que a resposta revela (030, FR-413).
        "orderProduction": marco.get("orderProduction", ""),
        "etapas": marco.get("stages") or [],
        "operation": marco.get("operation", ""),
        "normalization": marco.get("normalization", ""),
        "scale": arredondamento.get("scale", ""),
        "mode": arredondamento.get("mode", ""),
        # **Os três blocos opcionais, que esta função perdia.** Quem declarava um corte, errava
        # outro campo e recebia a recusa via o corte sumir da tela — e o salvamento seguinte
        # gravava o Edital sem ele. A recusa existe para que a pessoa corrija o que errou, e não
        # para apagar o que ela acertou.
        **forms.blocos_opcionais_do_marco(marco),
        "criterios": [_reexibir_criterio(item) for item in marco.get("tiebreakers") or []],
    }


def _reexibir_criterio(criterio):
    parametros = criterio.get("parameters") or {}
    return {
        "id": criterio.get("id", ""),
        "order": criterio.get("order", ""),
        "type": criterio.get("type", ""),
        "target": parametros.get("stageId") or parametros.get("factId") or "",
        "whenMissing": criterio.get("whenMissing", ""),
    }


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
    # Escreve em `profiles` como o passo de Perfis, porque o marco mora dentro do Perfil. O que
    # muda é **o que** do Perfil vem do formulário: ali, o Perfil inteiro; aqui, só os marcos,
    # fundidos sobre o que já está persistido.
    "classificacao": "profiles",
    "cronograma": "schedule",
    "etapas": "stages",
    "conteudo": "sections",
}

# O que a tela da etapa **não** oferece e, por isso, não pode apagar.
#
# `replace_draft` substitui o rascunho inteiro: a coleção da etapa atual vem do formulário, e o
# formulário conhece só os campos que desenha. Sem esta fusão, gravar de novo a etapa dona da
# coleção apaga em silêncio decisão tomada noutra tela — corrigir a data de um Evento
# desdesignava o período de inscrições, que é decisão da etapa `Inscrição`.
#
# É o mesmo defeito que `eventos_persistidos` tinha, pelo outro caminho: lá o estado se perdia ao
# gravar **outra** etapa; aqui, ao gravar a **própria**. Fechar só um dos dois deixaria a marca
# morrendo por meia jornada.
PRESERVADO_DA_ETAPA = {
    "cronograma": ("status", "isRegistrationPeriod"),
    # Os objetos do Perfil que **esta** tela não desenha. O quadro de vagas **não** entra aqui, e
    # não é esquecimento: esta tela o desenha, e preservar o gravado por cima do digitado faria
    # remover uma linha ser impossível — a remoção voltaria da fusão (025, T034).
    #
    # Os marcos entram pela razão oposta, e custaram o percurso E2E da 014: quem desenha o marco é
    # a etapa `classificacao`, que tem ramo próprio logo abaixo. Sem preservá-los aqui, salvar os
    # Perfis mandava `classificationMilestones: []` para o `replace_draft` — que apaga e recria — e
    # o marco inteiro sumia sem erro nenhum, levando junto a regra de corte declarada na etapa
    # anterior (014, E2E14-001).
    "perfis": ("classificationInformation", "callInformation", "classificationMilestones"),
}

LEITURA_DA_ETAPA = {
    "identificacao": forms.ler_identificacao,
    "perfis": forms.ler_perfis,
    "cronograma": forms.ler_eventos,
    "etapas": forms.ler_etapas,
    "classificacao": forms.ler_classificacao,
    "inscricao": forms.ler_inscricao,
    "conteudo": forms.ler_secoes,
}


def _ler_etapa(request, etapa):
    return LEITURA_DA_ETAPA[etapa](request.POST)


def _linhas_gerais_rederivadas(etapa, digitados):
    """Os Perfis cuja linha geral a gravação vai reafirmar com o total, e com outro número (027).

    Acontece quando a última lista reservada sai do Perfil: a repartição deixa de existir, a ampla
    concorrência volta a ser a vaga imediata inteira, e o número que estava declarado na linha é
    substituído. A derivação está certa — com uma lista de concorrência só, os dois são o mesmo
    número —, mas fazê-lo sem dizer seria esconder do operador que a conta dele mudou.

    Só reporta quando o valor **muda**: reafirmar 2 sobre 2 não é notícia.
    """
    if etapa != "perfis":
        return []
    reafirmadas = []
    for perfil in digitados or []:
        if not isinstance(perfil, dict) or listas_reservadas(perfil):
            continue
        total = perfil.get("immediateVacancies")
        geral = next(
            (
                linha
                for linha in perfil.get("vacancyTable") or []
                if isinstance(linha, dict) and not linha.get("modalityId")
            ),
            None,
        )
        if geral is None or geral.get("immediateVacancies") == total:
            continue
        reafirmadas.append({"code": perfil.get("code") or "", "total": total})
    return reafirmadas


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
        conteudo["documentRequirements"] = _preservando(
            digitados["documentos"],
            conteudo["documentRequirements"],
            PRESERVADO_DA_ETAPA.get(etapa, ()),
        )
        conteudo["schedule"] = [
            {**evento, "isRegistrationPeriod": str(evento["id"]) == digitados["periodo"]}
            for evento in conteudo["schedule"]
        ]
        # **Ato próprio, e antes do `replace_draft`** (029, T045). Os dois campos são de **raiz** do
        # Edital, e `replace_draft` não os carrega: passar por ele apagaria as coleções que ele
        # substitui sem gravar nenhum dos dois. O ato próprio também tem auditoria própria, com o
        # momento na razão — quem audita precisa saber *quando* o Edital passou a pedir isto.
        #
        # **Antes, e não depois**: este comando faz `compare_and_swap` e a revisão sobe; chamá-lo
        # depois de `replace_draft` levaria a `expected_revision` obsoleta que o outro acabou de
        # invalidar. Aqui, o `edital.refresh_from_db()` devolve a revisão que o `replace_draft`
        # seguinte vai declarar.
        atualizar_requerimento_de_matricula(
            actor=ator,
            edital_id=edital.id,
            expected_revision=edital.revision,
            momento=digitados["requerimento_momento"],
            declaracao=digitados["requerimento_declaracao"],
            correlation_id=request.correlation_id,
        )
        edital.refresh_from_db()
    elif etapa == "classificacao":
        # Só os marcos vêm do formulário; o resto de cada Perfil é o que já estava gravado.
        marcos_por_perfil = {str(chave): valor for chave, valor in digitados.items()}
        conteudo["profiles"] = [
            {**perfil, "classificationMilestones": marcos_por_perfil.get(str(perfil["id"]), [])}
            for perfil in conteudo["profiles"]
        ]
    else:
        colecao = COLECAO_DA_ETAPA[etapa]
        conteudo[colecao] = _preservando(
            digitados, conteudo[colecao], PRESERVADO_DA_ETAPA.get(etapa, ())
        )
    return replace_draft(
        actor=ator,
        edital_id=edital.id,
        expected_revision=edital.revision,
        profiles=conteudo["profiles"],
        schedule=conteudo["schedule"],
        stages=conteudo["stages"],
        sections=conteudo["sections"],
        document_requirements=conteudo["documentRequirements"],
        # **Só no passo da Classificação, e `None` nos demais** (030, FR-429). É onde o método
        # comum é oferecido, e é o único envio que fala dele: `None` nas outras etapas preserva o
        # que já estava, em vez de apagá-lo na primeira visita ao Cronograma.
        draw_method=(
            forms.metodo_comum_do_formulario(request.POST) or {}
            if etapa == "classificacao"
            else None
        ),
        correlation_id=request.correlation_id,
        # O rótulo da etapa, como quem elabora a vê no assistente (FR-042).
        area=dict((chave, rotulo) for chave, rotulo, _ in ETAPAS_COMPOSICAO).get(etapa, ""),
    )


def _preservando(digitados, persistidos, campos):
    """Funde, sobre o que o formulário enviou, os campos que ele não oferece.

    A correspondência é pela identidade, que o formulário carrega em campo próprio. Linha nova —
    sem par no que estava gravado — fica com o padrão do contrato, e é o certo: não há decisão
    anterior a preservar sobre um item que acabou de nascer.
    """
    if not campos:
        return digitados
    anterior = {str(item["id"]): item for item in persistidos}
    fundidos = []
    for item in digitados:
        gravado = anterior.get(str(item.get("id", "")))
        if gravado is None:
            fundidos.append(item)
            continue
        fundidos.append({**item, **{campo: gravado[campo] for campo in campos if campo in gravado}})
    return fundidos


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
    """O Perfil novo nasce com a linha geral do quadro, e **sem caixa para ela** (027, FR-316).

    A `025` fez a linha nascer com o Perfil porque a seção do quadro aparecia vazia — título e mais
    nada — e quem compunha do zero não tinha onde escrever a quantidade da ampla concorrência. A
    `027` resolveu o mesmo beco por outro lado, e melhor: o Perfil novo não tem lista reservada, e
    a quantidade da ampla concorrência **é** a vaga imediata dele. O campo já existe, e é um só.

    A linha continua nascendo aqui — identidade e quantidade em campo oculto —, porque é ela que a
    gravação preserva e que a Retificação alcança depois de publicada. O que não nasce é o segundo
    campo para o mesmo número, que é o que produzia o achado. As reservadas continuam nascendo com
    as Modalidades, uma a uma, porque é delas que vêm o rótulo e a identidade que a linha aponta.
    """
    identidade_nova = str(uuid4())
    return render(
        request,
        "interface/_perfil.html",
        {
            "perfil": {
                "id": identidade_nova,
                "reserveType": "NONE",
                "quadro": forms.quadro_do_formulario({"id": identidade_nova}),
                "tem_lista_reservada": False,
            },
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
            "anexos_do_edital": forms.anexos_do_edital(edital),
        },
    )


@require_http_methods(["GET"])
def fragmento_fato(request, indice):
    """A linha nova nasce com identidade: é por ela que o valor congelado dirá de qual fato é."""
    return render(
        request,
        "interface/_fato.html",
        {
            "fato": {"id": str(uuid4())},
            "indice": indice,
            "sub": _indice_de_linha(request),
        },
    )


def _edital_do_fragmento(request):
    """O Edital que o fragmento htmx está compondo, ou `None`.

    O fragmento não recebe o Edital na rota — ele é um pedaço de uma tela que já o tem. O
    identificador viaja na query, como o índice da linha já viaja.

    **E a autorização é a mesma da tela que o contém** (princípio III: negar por padrão, e
    verificar escopo em toda operação). O identificador vem da query, e query é entrada de quem
    chama: sem esta guarda, quem conhecesse o UUID de um Edital de outra unidade lia por aqui as
    Etapas classificatórias, os fatos declarados e — desde a `030`, que passou a derivar a
    identidade do marco — o código e a denominação dos Perfis dele. Nenhuma dessas leituras passava
    por `ator_da_sessao` nem por `obter_edital`.

    **Fora do escopo é 404, e não 403**, como na tela: a existência do Edital de outra unidade não
    é informação que este ator tenha direito de obter.

    **Sem o parâmetro continua sendo `None`**, e não recusa: é o fragmento pedido de uma tela que
    ainda não tem Edital, e os chamadores desenham listas vazias. Distinguir os dois casos é o
    ponto — ausência de parâmetro é estado legítimo; parâmetro que aponta para fora do escopo é
    tentativa de leitura alheia.
    """
    identificador = request.GET.get("edital")
    if not identificador:
        return None
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        raise Http404
    edital = obter_edital(actor=ator, edital_id=identificador)
    if edital is None:
        raise Http404
    return edital


def _etapas_e_fatos_do_edital(edital):
    """As Etapas classificatórias e os fatos declarados que o marco pode apontar.

    Só as **classificatórias**: uma Etapa que o Edital não publicou como classificatória não pode
    integrar marco, e oferecê-la na tela seria convidar a uma recusa que só apareceria na
    publicação (FR-010).
    """
    etapas = [
        {"id": str(etapa.id), "rotulo": f"{etapa.name}"}
        for etapa in edital.etapas.filter(classificatory=True).order_by("order")
    ]
    fatos = [
        {"id": str(fato.id), "rotulo": f"{perfil.code} · {fato.label}", "perfil": str(perfil.id)}
        for perfil in edital.perfis.prefetch_related("fatos").order_by("code")
        for fato in sorted(perfil.fatos.all(), key=lambda item: item.code)
    ]
    return etapas, fatos


def _etapas_governaveis(edital):
    """**Todas** as Etapas do Edital, e não só as classificatórias (014, FR-224).

    A Etapa que o corte alimenta não precisa classificar: no 77/2026 ela é a análise documental,
    eliminatória e decisória, que não entra em ordem nenhuma. Oferecer só as classificatórias aqui
    deixaria de fora justamente a Etapa do Edital que mais motiva esta feature.
    """
    if edital is None:
        return []
    return [
        {"id": str(etapa.id), "rotulo": etapa.name} for etapa in edital.etapas.order_by("order")
    ]


def _marco_novo(edital, indice):
    """O marco recém-acrescentado, já com o que o sistema sabe responder por ele (030).

    **Identidade primeiro**, pela mesma razão da modalidade: a gravação preserva o `id` recebido, e
    uma linha sem identidade não teria o que preservar.

    **Depois o que era pergunta sem resposta possível.** O arredondamento nasce com o par que o
    projeto pratica (FR-419) e a identidade nasce derivada do Perfil (FR-420) — as duas obrigatórias
    sem padrão e o código inventado para um objeto lido pela primeira vez, que eram três das vinte e
    oito perguntas do Edital mais simples.

    **Só no marco novo.** Nada disto alcança marco já declarado, nem em Retificação (FR-421): esta
    função só é chamada pelo fragmento que cria a linha.
    """
    novo = {"id": str(uuid4()), **marcos.ARREDONDAMENTO_PADRAO}
    perfil = None if edital is None else edital.perfis.filter(pk=indice).first()
    if perfil is None:
        return novo
    codigo, nome = marcos.identidade_derivada(
        codigo_do_perfil=perfil.code,
        nome_do_perfil=perfil.name,
        codigos_em_uso=perfil.marcos.values_list("code", flat=True),
    )
    return {**novo, "code": codigo, "name": nome}


def fragmento_marco(request, indice):
    """A linha nova nasce com identidade, pela mesma razão da modalidade.

    `indice` é o do Perfil que a contém: os campos são `marco-<perfil>-<n>-…`.
    """
    edital = _edital_do_fragmento(request)
    etapas, fatos = _etapas_e_fatos_do_edital(edital) if edital else ([], [])
    sub = _indice_de_linha(request)
    return render(
        request,
        "interface/_marco_acrescentado.html",
        {
            "marco": _marco_novo(edital, indice),
            "indice": indice,
            "sub": sub,
            # **O cartão precisa saber se o Edital declara método comum** (030, FR-429): sem isto
            # o fragmento diria "ainda não declarado" sobre um marco que referencia o comum, e a
            # tela inteira — que sabe — passaria a contradizer o pedaço dela que o htmx troca.
            "tem_metodo_comum": bool(edital.metodo_de_sorteio_comum) if edital else False,
            # O bloco de ajuda da etapa vem junto, fora de banda: até este marco nascer não havia a
            # que ele se referir, e quem acrescentou o marco não deveria recarregar a página para
            # descobrir que a ajuda existe (030, FR-426).
            "ancora_do_marco": f"marco-{indice}-{sub}",
            # Sem as listas, a linha nova nasceria com os selects vazios — e quem acrescentasse um
            # marco não teria o que escolher, que é o defeito que este passo existe para evitar.
            "etapas_classificatorias": etapas,
            "etapas_governaveis": _etapas_governaveis(edital),
            "fatos_declarados": fatos,
            # O marco não é folha: dele nasce o botão que pede o fragmento de critério, e esse
            # pedido carrega o Edital na query. Sem `edital` aqui, o `hx-get` do botão sairia com o
            # parâmetro vazio e o critério acrescentado a partir de um marco recém-criado nasceria
            # sem alvo — o mesmo defeito que as listas acima evitam, um nível abaixo.
            "edital": edital,
        },
    )


@require_http_methods(["GET"])
def fragmento_marco_recomposto(request, indice, sub):
    """O cartão do marco reconstruído a partir do que está digitado agora (030, FR-413 a FR-418).

    **Existe porque a resposta de entrada governa quais campos o cartão tem.** Escolher "por
    sorteio" precisa trazer o método à tela; escolher "pela pontuação" precisa tirá-lo, e a segunda
    Etapa precisa fazer a combinação voltar a ser perguntada. Sem a ida ao servidor, isso seria
    JavaScript — que a CSP desta interface não admite — ou ocultação por CSS, que mantém o
    `required` ativo e reproduz a submissão que o navegador recusa sem mostrar o que falta.

    Lê o marco do **formulário**, e não do banco, pela mesma razão de `fragmento_quadro`: o que a
    pessoa está decidindo é sobre o que ela acabou de digitar, e recompor sobre o gravado apagaria
    tudo desde a última gravação.

    **Conteúdo incompleto não troca nada.** Quem está no meio de preencher pode não ter ainda o que
    a leitura exige; responder 204 faz o htmx deixar a tela como está, que é melhor do que devolver
    um cartão montado sobre metade do marco.
    """
    edital = _edital_do_fragmento(request)
    etapas, fatos = _etapas_e_fatos_do_edital(edital) if edital else ([], [])
    try:
        marco = forms.marco_do_formulario(request.GET, indice, sub)
    except (ValueError, KeyError):
        return HttpResponse(status=204)
    if marco is None:
        return HttpResponse(status=204)
    return render(
        request,
        "interface/_marco.html",
        {
            "marco": _reexibir_marco(marco),
            "indice": indice,
            "sub": sub,
            # Como no fragmento que cria a linha, e pela mesma razão: o pedaço trocado não pode
            # saber menos do que a tela que o contém (030, FR-429).
            "tem_metodo_comum": bool(edital.metodo_de_sorteio_comum) if edital else False,
            "etapas_classificatorias": etapas,
            "etapas_governaveis": _etapas_governaveis(edital),
            "fatos_declarados": fatos,
            "edital": edital,
        },
    )


def fragmento_criterio(request, indice, sub):
    """Um nível mais fundo: o critério pertence ao marco, e não ao Perfil.

    Renumerar critérios por Perfil faria dois marcos irmãos disputarem a mesma linha do formulário,
    que é o mesmo defeito que a composição de prefixo da modalidade já evita um nível acima.
    """
    edital = _edital_do_fragmento(request)
    etapas, fatos = _etapas_e_fatos_do_edital(edital) if edital else ([], [])
    return render(
        request,
        "interface/_criterio.html",
        {
            "criterio": {"id": str(uuid4())},
            "indice": indice,
            "sub": sub,
            "n": _indice_de_linha(request),
            "etapas_classificatorias": etapas,
            "fatos_declarados": fatos,
        },
    )


@require_http_methods(["GET"])
def fragmento_quadro(request, indice):
    """O quadro reconstruído a partir do que está digitado agora (027, FR-317, FR-321).

    **Existe porque a escolha da ampla concorrência muda o quadro, e mudava só na gravação.**
    Apontar uma Modalidade como a da ampla tira-a das listas reservadas: a caixa dela deixa de
    existir, e o Perfil que fica sem lista reservada nenhuma deixa de ter bloco. Enquanto isso só
    era recalculado ao salvar, a tela mentia entre uma gravação e outra — a caixa continuava lá, e
    quem digitasse nela levava recusa na submissão.

    Lê o Perfil do **formulário**, e não do banco: a Modalidade recém-acrescentada e o total
    recém-digitado ainda não foram gravados, e é sobre eles que a pessoa está decidindo.

    **Conteúdo incompleto não troca nada.** Quem está no meio de preencher pode não ter ainda o que
    `ler_perfis` exige; responder 204 faz o htmx deixar a tela como está, que é melhor do que
    devolver um quadro montado sobre metade do Perfil.
    """
    try:
        perfis = forms.ler_perfis(request.GET)
    except (ValueError, KeyError):
        return HttpResponse(status=204)
    identidade = request.GET.get(f"perfil-{indice}-id")
    perfil = next((item for item in perfis if str(item.get("id")) == str(identidade)), None)
    if perfil is None:
        return HttpResponse(status=204)
    return render(
        request,
        "interface/_quadro_do_perfil.html",
        {
            "perfil": {
                **perfil,
                "quadro": forms.quadro_do_formulario(perfil),
                "tem_lista_reservada": bool(listas_reservadas(perfil)),
            },
            "indice": indice,
        },
    )


def _tem_lista_reservada_no_formulario(request, indice):
    """Se este Perfil **já** declara lista reservada, lido do formulário que veio junto (027).

    Lista reservada é Modalidade declarada menos a que o Perfil aponta como a da ampla
    concorrência (FR-317) — a mesma definição do domínio, sobre a outra fonte: aqui o dado não está
    no banco, está sendo digitado agora.
    """
    ampla = request.GET.get(f"perfil-{indice}-generalCompetitionModalityId", "")
    declaradas = {
        valor
        for chave, valor in request.GET.items()
        if chave.startswith(f"modalidade-{indice}-") and chave.endswith("-id") and valor
    }
    return bool(declaradas - {ampla})


def fragmento_modalidade(request, indice):
    """A linha nova nasce com **os dois** identificadores: o da modalidade e o da sua Regra.

    A gravação preserva o `id` recebido, e uma linha sem identidade não teria o que preservar. O da
    Regra nasce mesmo antes de a Regra existir, porque quem digitar o fundamento em seguida vai
    criá-la, e a identidade precisa estar no formulário nesse momento.

    `indice` é o do Perfil que contém a linha: os nomes dos campos são `modalidade-<perfil>-<n>-…`.

    **E a linha do quadro nasce junto, fora de banda.** A UX-021 promete que as linhas do quadro
    são oferecidas a partir das Modalidades declaradas; quem acrescenta uma Modalidade e digita a
    quantidade dela antes de gravar precisa ver a linha aparecer, e não descobrir depois que não
    havia onde escrever o número. O rótulo dela só fica completo na volta do servidor, porque o
    código e a denominação estão sendo digitados agora — e a alternativa seria espelhá-los por
    JavaScript, que a CSP desta interface não admite.
    """
    sub = _indice_de_linha(request)
    modalidade = {"id": str(uuid4()), "ruleId": str(uuid4())}
    return render(
        request,
        "interface/_modalidade_com_linha.html",
        {
            "modalidade": modalidade,
            "indice": indice,
            "sub": sub,
            # **A seção do quadro nasce aqui quando esta é a primeira lista reservada** (027,
            # FR-321). O bloco não está na página enquanto não há repartição a pedir, e mandar a
            # linha sozinha para um destino que não existe a perderia em silêncio — o `hx-swap-oob`
            # não acha alvo e **não erra**.
            "secao_nova": not _tem_lista_reservada_no_formulario(request, indice),
            # A linha geral vem preenchida com o total que está no formulário: é o valor que a
            # gravação materializaria, e vê-lo é o que faz a repartição começar de um lugar
            # verdadeiro em vez de um campo vazio.
            "geral": {
                "id": request.GET.get(f"linha-{indice}-0-id") or str(uuid4()),
                "modalityId": "",
                "rotulo": "Ampla concorrência",
                "geral": True,
                "derivada": False,
                "immediateVacancies": request.GET.get(f"perfil-{indice}-immediateVacancies", ""),
            },
            "linha": {
                "id": str(uuid4()),
                "modalityId": modalidade["id"],
                "rotulo": "Modalidade nova",
                "geral": False,
                "derivada": False,
                "immediateVacancies": "",
            },
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
    """Os campos de uma linha nova, já com o valor inicial de cada um.

    O campo de identidade nasce **aqui**, e não em `diferencas`: é o fragmento que cria a linha,
    e é dele que a identidade precisa vir para atravessar conferência e confirmação sem mudar. Sem
    isso, reenviar a confirmação produz um payload diferente sob a mesma chave de idempotência.
    """
    return [
        {
            "chave": chave,
            "rotulo": rotulo,
            "tipo": tipo,
            "valor": str(uuid4()) if tipo == retificacao_ui.OCULTO else "",
        }
        for chave, rotulo, tipo in definicoes
    ]


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
def fragmento_retificacao_anexo(request):
    return render(
        request,
        "interface/_retificacao_anexo.html",
        {"indice": _indice_de_linha(request), "campos": _campos_de(retificacao_ui.NOVO_ANEXO)},
    )


@require_http_methods(["GET"])
def fragmento_retificacao_linha_do_quadro(request, edital_id):
    """Uma linha do quadro a acrescentar por Retificação (025, FR-171).

    A rota é escopada ao Edital porque os dois campos de escolha — o Perfil e a lista de
    concorrência — saem do **conteúdo vigente daquele** Edital, e não de um catálogo global. É o
    mesmo motivo pelo qual o fragmento da Etapa é escopado ao Edital.

    Sem este caminho, nenhum Edital já publicado poderia ganhar quadro: todos foram publicados
    antes de a capacidade existir, e alterar linha existente não alcança quem não tem linha alguma.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404
    base = _base_da_composicao(edital, None)
    if base is None:
        raise Http404
    opcoes = retificacao_ui.opcoes_da_linha_nova(conteudo_base(base))
    campos = [
        {**campo, "opcoes": tuple(opcoes.get(campo["chave"], ()))}
        for campo in _campos_de(retificacao_ui.NOVA_LINHA_DO_QUADRO)
    ]
    return render(
        request,
        "interface/_retificacao_linha_do_quadro.html",
        {"indice": _indice_de_linha(request), "campos": campos},
    )


# O que `junto=` aceita: um `id` de elemento, e nada que possa virar marcação. O valor é escrito
# num atributo `id` do fragmento devolvido, e o autoescape do template já o protegeria — mas a
# recusa aqui é o que garante que só saia daqui um seletor plausível, e não texto qualquer.
ALVO_DE_REMOCAO = re.compile(r"^[A-Za-z][A-Za-z0-9-]{0,80}$")


@require_http_methods(["GET"])
def fragmento_remover(request):
    """A linha removida é substituída por nada; o conteúdo digitado some junto.

    `junto=` pede que **outro** elemento saia no mesmo ato, pelo `id` dele. Existe porque nem toda
    linha do formulário mora inteira dentro do próprio `fieldset`: a Modalidade de Concorrência tem
    uma linha correspondente na seção do quadro de vagas, e `closest fieldset` não a alcança.
    Deixá-la para trás fazia o salvamento seguinte ser recusado por uma referência a uma Modalidade
    que a pessoa acabara de remover — e que já não aparecia em lugar nenhum da tela (025).

    Sem o parâmetro, o comportamento é o de sempre: devolver o vazio que apaga o alvo do
    `hx-target`.
    """
    alvo = request.GET.get("junto", "")
    if not alvo:
        return HttpResponse("")
    if not ALVO_DE_REMOCAO.match(alvo):
        raise Http404
    return render(request, "interface/_remover_junto.html", {"alvo": alvo})


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
            "marcos_classificatorios": _marcos_publicados(edital, ator),
        },
    )


def _destinos_do_marco(edital, marco, *, pode_classificar, atos_vigentes):
    """Para onde este marco leva **aquele** ator, e nada além.

    Um destino entra se, e só se, quem está olhando o alcança — que é o princípio que esta tela já
    declarava. O que muda é o sujeito dele: era aplicado à lista inteira, por uma porta escolhida
    de antemão, e passa a ser aplicado **a cada destino**.

    Os destinos do primeiro grupo pendem da mesma porta que `_edital_para_classificar` guarda; o
    da divulgação pende de `resultado:publicar`, que não decorre de nenhuma das outras. Eram dois
    eixos de autorização e uma pergunta só — e é daí que vinha o `ACH-40`.
    """
    marco_id = str(marco.get("id"))
    destinos = []
    if pode_classificar:
        # **O marco que ordena por sorteio abre a tela do sorteio** (021, D-013): o rótulo diz o
        # que se vai encontrar, e "ordenação" nomearia um recálculo que aquele marco não tem.
        if marco.get("drawMethod"):
            destinos.append(
                {
                    "rotulo": marco.get("name") or "",
                    "url": reverse("interface:sorteio", args=[edital.id, marco_id]),
                    "principal": True,
                    "nota": "sorteio público",
                }
            )
        else:
            destinos.append(
                {
                    "rotulo": marco.get("name") or "",
                    "url": reverse("interface:ordenacao", args=[edital.id, marco_id]),
                    "principal": True,
                    "nota": "",
                }
            )
        # A condição do corte é a regra de corte declarada, e continua sendo exatamente essa: ela
        # é escopo da `032`, e o que mudou aqui é **onde** ela é avaliada, nunca o que ela decide.
        # Deixá-la no template obrigaria a tela a conhecer metade da derivação, e duas verdades
        # sobre a mesma lista divergem na primeira mudança.
        if marco.get("cutRule"):
            destinos.append(
                {"rotulo": "corte", "url": reverse("interface:corte", args=[edital.id, marco_id])}
            )
        destinos.append(
            {"rotulo": "ocupação", "url": reverse("interface:ocupacao", args=[edital.id, marco_id])}
        )
    # **A divulgação de cada ato emitido** — o destino que a tela não oferecia a ninguém. Ela
    # depende do ato **existir**: marco sem ato não tem o que divulgar, e oferecer um caminho que
    # termina em nada é o mesmo defeito que este bloco existe para evitar, com outra roupa.
    for ato in atos_vigentes:
        destinos.append(
            {
                "rotulo": "divulgar o resultado",
                "url": reverse(
                    "interface:previa-de-publicacao", args=[edital.id, marco_id, ato.id]
                ),
            }
        )
    return destinos


def _marcos_publicados(edital, ator=None):
    """Os marcos do Edital publicado, com os destinos que **aquele ator** alcança em cada um.

    **A derivação era por porta, e passou a ser por destino.** A lista inteira dependia de
    `_edital_para_classificar` — presidência ou auditoria —, e essa porta é a de *um* dos eixos de
    autorização do produto. Quem detinha `resultado:publicar` sem vínculo de comissão nenhum podia
    divulgar o resultado, a tela de divulgação abria para ele, e esta tela não mostrava caminho
    nenhum até lá: ele só chegava sabendo montar a URL. Era o `ACH-40`, e a segregação de papéis
    que o produto recomenda ficava inexecutável por causa dele.

    O princípio que a versão anterior já declarava continua inteiro, e é o que impede a correção
    de virar o defeito espelhado: *oferecer o que se vai recusar é pior do que não oferecer*.
    Aplicado à lista, ele fazia quem julga recursos ver "Classificação final" e receber erro ao
    clicar; aplicado a cada destino, ele responde pelos dois sentidos — nenhum caminho oferecido
    que se vá recusar, e nenhum caminho alcançável escondido (`FR-473`, `FR-476`).

    Marco sem destino nenhum não entra, e Edital em que nenhum marco rende destino devolve lista
    vazia: a tela não desenha o bloco, e **a ausência do bloco não é recusa** — é ausência.
    """
    try:
        conteudo = effective_version(edital_id=edital.id).content
    except DomainError:
        return []
    perfis_com_marcos = [
        perfil
        for perfil in conteudo.get("profiles") or []
        if perfil.get("classificationMilestones")
    ]
    if not perfis_com_marcos:
        return []

    pode_classificar = ator is None or _pode_ver_a_classificacao(ator, edital)
    pode_divulgar = ator is not None and ator.can("resultado:publicar")
    atos_por_marco = {}
    if pode_divulgar:
        atos_por_marco = atos_vigentes_por_marco(
            edital=edital,
            marcos_ids=[
                str(marco.get("id"))
                for perfil in perfis_com_marcos
                for marco in perfil["classificationMilestones"]
            ],
        )

    itens = []
    for perfil in perfis_com_marcos:
        for marco in perfil["classificationMilestones"]:
            destinos = _destinos_do_marco(
                edital,
                marco,
                pode_classificar=pode_classificar,
                atos_vigentes=atos_por_marco.get(str(marco.get("id")), ()),
            )
            if destinos:
                itens.append({"perfil": perfil, "marco": marco, "destinos": destinos})
    return itens


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
    # **O impedimento de publicar, anunciado em Homologar** — que é onde ele passa a existir. Ele
    # não impede homologar, e por isso não entra em `recusa_certa`: acumular os dois papéis é
    # permitido, e o que falta é a pessoa saber, antes de praticar, que a publicação ficará com
    # outra (FR-021 da 001).
    homologar_fecha_a_publicacao = ato.chave == "homologar" and homologar_fecharia_a_publicacao(
        participantes, ator
    )
    pendencias = _pendencias(edital) if ato.chave in {"submeter", "publicar"} else []
    # Alcançável por URL direta: sem isto a tela oferece "Confirmar" para um ato que o
    # command recusaria, e a recusa só apareceria depois do clique.
    impedimento = atos.impedimento(edital, ator, ato)
    contexto = {
        "edital": edital,
        "ato": ato,
        "participantes": participantes,
        "impedido_por_segregacao": segregacao,
        "homologar_fecha_a_publicacao": homologar_fecha_a_publicacao,
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


def _resumo_pendente(ator):
    """O resumo de um artefato que **este ator** enviou e que nenhuma versão publicou ainda.

    É consulta ao banco, e não campo oculto: o formulário tem duas fases, e o arquivo só existe na
    primeira — confiar no navegador para carregar o resumo entre elas seria confiar nele para
    dizer o que os bytes são.

    As duas condições são a fronteira. **Não congelado** impede citar artefato de outro Edital já
    publicado, que passaria a ser publicado sob este; **enviado por este ator** impede citar o
    rascunho de outra pessoa. Nenhuma das duas é conveniência: sem elas, um POST fabricado
    escolheria qualquer artefato do sistema.
    """

    def resolver(identificador):
        return (
            ArtefatoAnexo.objects.filter(
                pk=identificador, congelado_em__isnull=True, enviado_por=ator.subject
            )
            .values_list("document_hash", flat=True)
            .first()
        )

    return resolver


def _anexos_da_etapa(edital):
    """Cada Anexo com a posição, o total e os requisitos que o citam como modelo (020).

    Posição e total existem porque a tela precisa dizer **qual** anexo cada ação alcança — foi a
    ausência disso que fez a auditoria de polish classificar a lista como risco de erro operacional.
    Os requisitos vêm junto pela mesma razão: a tela onde se remove era a única que não dizia que
    havia vínculo, e remover desfaz o vínculo.
    """
    anexos = list(edital.anexos.select_related("artefato").prefetch_related("requisitos"))
    return [
        {
            "anexo": anexo,
            "posicao": posicao,
            "total": len(anexos),
            "modelo_de": [requisito.name for requisito in anexo.requisitos.all()],
        }
        for posicao, anexo in enumerate(anexos, start=1)
    ]


def _descricao_do_artefato(identificador):
    """`autodeclaracao.pdf · 3 KB` — o que a conferência precisa para ser conferência."""
    artefato = ArtefatoAnexo.objects.filter(pk=identificador).first()
    if artefato is None:
        return ""
    return f"{artefato.nome_original} · {tamanho_legivel(artefato.tamanho)}"


def _artefatos_enviados(request, ator):
    """Grava os arquivos que a Retificação envia, e devolve o POST com as identidades no lugar.

    **Os bytes entram antes do ato, e não dentro dele** (020, FR-035). O artefato nasce
    descongelado, como o de elaboração, e só a publicação da Retificação o torna público e
    imutável — o que também significa que uma Retificação abandonada deixa um artefato que
    ninguém alcança e que continua apagável, exatamente como as Alterações dela.

    A gravação acontece na fase de conferência porque é ela que produz o resumo "antes e depois":
    sem o artefato gravado não há resumo a mostrar, e pedir o arquivo de novo na confirmação faria
    a pessoa escolhê-lo duas vezes.
    """
    dados = request.POST.copy()
    for chave, arquivo in request.FILES.items():
        if not chave.startswith("arquivo:") or not arquivo:
            continue
        # Duas formas, uma regra: `arquivo:<referencia>` alimenta o campo `campo:<referencia>` de um
        # Anexo que já existe; `arquivo::<destino>` grava a identidade em `<destino>`, que é como o
        # Anexo **acrescentado** recebe o seu. Quem nomeia o destino é o formulário, e não a view.
        destino = (
            chave.removeprefix("arquivo::")
            if chave.startswith("arquivo::")
            else f"campo:{chave.removeprefix('arquivo:')}"
        )
        aceitar(
            arquivo,
            nome_original=arquivo.name,
            limite_em_bytes=settings.EDITAL_ANEXOS_LIMITE_BYTES,
        )
        arquivo.seek(0)
        conteudo = arquivo.read()
        artefato = ArtefatoAnexo.objects.create(
            bytes=conteudo,
            tamanho=len(conteudo),
            document_hash=hashlib.sha256(conteudo).hexdigest(),
            nome_original=arquivo.name[:255],
            enviado_por=ator.subject,
            enviado_em=timezone.now(),
        )
        dados[destino] = str(artefato.id)
    return dados


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
    # **O POST com os arquivos já gravados**, e não o cru. A gravação acontece antes de tudo o que
    # lê o formulário porque a reexibição também precisa dela: sem isso, a conferência devolve a
    # linha nova sem a identidade do artefato, e quem confirma perde o arquivo que acabou de
    # enviar — sem erro, e com a tela dizendo que estava tudo certo (020, FR-035).
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
                # A gravação acontece **dentro** da verificação de permissão, e é por isso que
                # ela fica aqui e não no topo: subida para antes, ela escreveria artefato no banco
                # a pedido de quem não pode elaborar Retificação. O `dados` rebindado é o que a
                # reexibição usa depois, então a linha nova volta com a identidade do artefato.
                dados = _artefatos_enviados(request, ator)
                alteracoes, resumo = retificacao_ui.diferencas(
                    projecao,
                    dados,
                    resumo_do_artefato=_resumo_pendente(ator),
                    descricao_do_artefato=_descricao_do_artefato,
                )
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

    grupos = retificacao_ui.reexibir(
        retificacao_ui.campos_editaveis(projecao, descricao_do_artefato=_descricao_do_artefato),
        dados,
    )
    return render(
        request,
        "interface/retificar.html",
        {
            "edital": edital,
            "base": base,
            "grupos": grupos,
            # As mesmas linhas, divididas nas seções que a tela desenha e que o índice do topo
            # alcança. `grupos` continua servindo a leitura de quem não pode elaborar, que é uma
            # lista corrida e não um formulário para navegar.
            "secoes": retificacao_ui.agrupar_em_secoes(grupos),
            "digitado": dados,
            # As linhas acrescentadas nascem no cliente, mas precisam voltar do servidor depois
            # do POST: sem isto, ver o resumo devolve um formulário sem elas.
            "novos_perfis": retificacao_ui.novas_para_formulario(
                dados or {}, "perfil", retificacao_ui.NOVO_PERFIL
            ),
            "novos_eventos": retificacao_ui.novas_para_formulario(
                dados or {}, "evento", retificacao_ui.NOVO_EVENTO
            ),
            "novos_anexos": retificacao_ui.novas_para_formulario(
                dados or {}, "anexo", retificacao_ui.NOVO_ANEXO
            ),
            # As linhas do quadro acrescentadas voltam com as **opções** junto: os dois campos de
            # escolha vêm do conteúdo vigente, e reexibi-los sem elas devolveria dois `select`
            # vazios — a pessoa leria "vai acrescentar" e confirmaria uma linha sem Perfil.
            "novas_linhas_do_quadro": retificacao_ui.novas_para_formulario(
                dados or {},
                "linha-do-quadro",
                retificacao_ui.NOVA_LINHA_DO_QUADRO,
                opcoes=retificacao_ui.opcoes_da_linha_nova(projecao),
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
        momento = momento.replace(tzinfo=ZONA_INSTITUCIONAL)
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
    """Perfil e Evento inteiros são ilegíveis como dicionário; o que identifica basta.

    Instante sai no fuso institucional. O conteúdo canônico materializa cada um como texto ISO em
    UTC, e era assim que ele chegava às colunas "antes" e "depois": um término digitado como
    `10/10/2026 23:59`, em Brasília, aparecia a quem homologa e a quem assina como
    `2026-10-11T02:59:00+00:00` — outro dia, não só outra hora (auditoria de 13/09).
    """
    if isinstance(valor, str):
        return interface_extras.instante(valor) if _PARECE_INSTANTE.match(valor) else valor
    if not isinstance(valor, dict):
        return valor
    for chave in ("code", "type", "name", "description"):
        if valor.get(chave):
            return valor[chave]
    return "—"


# Texto ISO com fuso, que é a forma em que o conteúdo canônico materializa instante. Restrita de
# propósito: um rótulo que comece com data — "2026: o ano em que…" — não é instante, e convertê-lo
# apagaria o texto que a pessoa escreveu.
_PARECE_INSTANTE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")


# O vocabulário da tela de composição, reaproveitado para dizer em português o campo que a
# Retificação alterou. Ele já existe — é o que rotula cada controle na hora de elaborar —, e
# reconstruí-lo aqui criaria dois nomes para o mesmo campo, que divergiriam no primeiro rename.
#
# **A chave é o par (coleção, campo), e não o campo sozinho.** Quatro nomes se repetem entre as
# listas, e `name` se repete cinco vezes: achatá-las num dicionário só fazia a última vencer, e a
# tela que confere o ato irreversível passava a chamar a Denominação do Perfil de "Nome", a Ordem de
# aplicação do critério de desempate de "Ordem", e a Lista de concorrência da linha do quadro de
# "Exigido apenas da modalidade".
#
# Campo aninhado — `cutRule/targetCount`, `normativeRule/percentage` — entra pelo último segmento,
# que é como ele chega no caminho normativo, sob a coleção da entidade que o carrega.
CAMPOS_POR_COLECAO = {
    "": retificacao_ui.CAMPOS_RAIZ,
    "profiles": retificacao_ui.CAMPOS_PERFIL + retificacao_ui.CAMPOS_DA_REVERSAO,
    "schedule": retificacao_ui.CAMPOS_EVENTO,
    "stages": retificacao_ui.CAMPOS_ETAPA,
    "sections": retificacao_ui.CAMPOS_SECAO,
    "attachments": retificacao_ui.CAMPOS_ANEXO,
    "documentRequirements": retificacao_ui.CAMPOS_DOCUMENTO,
    "competitionModalities": retificacao_ui.CAMPOS_MODALIDADE + retificacao_ui.CAMPOS_REGRA,
    "vacancyTable": retificacao_ui.CAMPOS_DA_LINHA,
    "classificationMilestones": retificacao_ui.CAMPOS_MARCO + retificacao_ui.CAMPOS_DO_CORTE,
    "tiebreakers": retificacao_ui.CAMPOS_CRITERIO,
    "declaredFacts": retificacao_ui.CAMPOS_FATO,
}

CAMPO_EM_PORTUGUES = {
    (colecao, nome.rsplit("/", 1)[-1]): rotulo
    for colecao, lista in CAMPOS_POR_COLECAO.items()
    for nome, rotulo, *_ in lista
}


# Como cada coleção se chama quando é preciso dizer "onde" a alteração acontece.
COLECAO_EM_PORTUGUES = {
    "profiles": "Perfil",
    "schedule": "Evento do cronograma",
    "stages": "Etapa de avaliação",
    "sections": "Seção do texto",
    "documentRequirements": "Documento exigido",
    "attachments": "Anexo",
    "competitionModalities": "Modalidade",
    "vacancyTable": "Linha do quadro de vagas",
    "classificationMilestones": "Marco classificatório",
    "tiebreakers": "Critério de desempate",
    "declaredFacts": "Fato declarado",
}


def _nome_da_entidade(entidade):
    """Como a pessoa reconhece a entidade que a alteração alcança."""
    if not isinstance(entidade, dict):
        return ""
    for chave in ("label", "name", "title", "description", "code", "type", "order"):
        if entidade.get(chave):
            return str(entidade[chave])
    return ""


def _onde_e_campo(base, caminho):
    """O caminho normativo dito em português: a entidade alcançada e o campo dela.

    `interface/retificacao.py` abre dizendo por que isto existe — *"quem elabora um Edital tem um
    problema administrativo, não um problema de representação"* — e a tela de composição obedece.
    As telas de conferência, não: a Retificação chegava a quem homologa e a quem assina o ato
    irreversível como `/schedule/id=1705f922-…/endAt`. A `004` verifica a tela de composição; estas
    ficaram de fora (auditoria de 13/09).
    """
    segmentos = [parte for parte in (caminho or "").split("/") if parte]
    if not segmentos:
        return "", ""
    # A entidade é o último seletor por identidade do caminho; a coleção dela, o segmento anterior.
    # É essa coleção que desambigua o rótulo do campo: `name` existe em cinco listas.
    posicao = next(
        (i for i in range(len(segmentos) - 1, 0, -1) if segmentos[i].startswith("id=")),
        None,
    )
    colecao = segmentos[posicao - 1] if posicao is not None else ""
    campo = ""
    if not segmentos[-1].startswith("id="):
        campo = CAMPO_EM_PORTUGUES.get((colecao, segmentos[-1]), "")
    onde = ""
    if posicao is not None:
        rotulo = COLECAO_EM_PORTUGUES.get(colecao, colecao)
        # O nome é ornamento útil, e a coleção já diz o essencial. Um caminho que não resolva —
        # entidade removida por uma Retificação anterior, seletor de forma antiga — degrada para
        # "Perfil" em vez de derrubar a tela onde o ato irreversível é assinado.
        try:
            entidade = retificacao_ui._ler(base, "/" + "/".join(segmentos[: posicao + 1]))
        except Exception:  # noqa: BLE001 — a tela de conferência não pode cair por um nome
            entidade = None
        nome = _nome_da_entidade(entidade)
        onde = f"{rotulo} “{nome}”" if nome else rotulo
    elif segmentos[0] in COLECAO_EM_PORTUGUES:
        onde = COLECAO_EM_PORTUGUES[segmentos[0]]
    elif campo:
        onde = "Identificação do Edital"
    return onde, campo


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
        legivel = _anexo_legivel(base, alteracao, anterior)
        if legivel is _OMITIR:
            continue
        legiveis.append(
            legivel
            or {
                "caminho": alteracao.target_path,
                **dict(
                    zip(("onde", "campo"), _onde_e_campo(base, alteracao.target_path), strict=True)
                ),
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


# A linha que existe no ato e não se mostra: dizer duas vezes a mesma substituição, uma delas em
# SHA-256, é o que esta correção veio desfazer.
_OMITIR = object()

CAMPO_DO_ANEXO = {
    "artifactId": "Arquivo do anexo",
    "artifactHash": "Conferência do arquivo",
    "label": "Rótulo",
    "order": "Ordem editorial",
}


def _anexo_legivel(base, alteracao, anterior):
    """A alteração sobre um Anexo, dita em português (020, POLISH020-002).

    Sem isto, substituir o formulário rendia duas linhas de UUID e SHA-256 — e é **nesta** tela que
    o homologador aprova e o publicador assina, sem terem visto a tela de composição. As colunas
    "antes" e "depois" existem para conferir, e conferir dois identificadores opacos é confiar.

    O rótulo do anexo vem do conteúdo-base, e não do banco: é o que aquela versão dizia, que é o que
    quem aprova precisa ler.
    """
    caminho = alteracao.target_path or ""
    if not caminho.startswith("/attachments/"):
        return None
    partes = caminho[len("/attachments/") :].split("/")
    seletor, campo = partes[0], (partes[1] if len(partes) > 1 else "")
    identidade_do_anexo = seletor.removeprefix("id=")
    anexo = next(
        (
            item
            for item in base.get("attachments") or []
            if str(item.get("id")) == identidade_do_anexo
        ),
        None,
    )
    onde = (anexo or {}).get("label") or "Anexo acrescentado"
    if not campo:
        # A coleção inteira: acréscimo ou remoção do anexo.
        novo = alteracao.new_value if isinstance(alteracao.new_value, dict) else {}
        return {
            "caminho": caminho,
            "onde": onde if alteracao.operation == "REMOVE" else novo.get("label") or onde,
            "campo": "O anexo",
            "operacao": alteracao.operation,
            "antes": onde if alteracao.operation == "REMOVE" else "—",
            "depois": "removido do Edital"
            if alteracao.operation == "REMOVE"
            else "acrescentado ao Edital",
        }
    if campo == "artifactHash":
        # A conferência anda junto com o arquivo e não é decisão própria: mostrá-la como linha
        # separada duplicaria o mesmo fato e devolveria o SHA-256 à tela.
        return _OMITIR
    return {
        "caminho": caminho,
        "onde": onde,
        "campo": CAMPO_DO_ANEXO.get(campo, campo),
        "operacao": alteracao.operation,
        "antes": "o arquivo publicado até aqui"
        if campo == "artifactId"
        else (_resumo_de_linha(anterior) if anterior is not None else "—"),
        "depois": "um arquivo novo, que passa a ser o publicado"
        if campo == "artifactId"
        else (_resumo_de_linha(alteracao.new_value) if alteracao.new_value is not None else "—"),
    }


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
        # O que a conferência do ato sabe e descartava (027, FR-336). A submissão de um rascunho
        # mostra as advertências dele; a Retificação as calculava e jogava fora, de modo que o
        # mesmo conteúdo dizia duas coisas diferentes conforme o caminho por onde chegava.
        "advertencias": advertencias_do_ato(item),
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
def _versao_por_identificador(identificador):
    """A versão que o motivo do registro nomeia, ou `None`.

    O motivo é campo de texto, e o que esta feature grava nele é sempre um identificador — mas a
    coluna não promete isso. Texto que não é UUID levanta `ValidationError` na consulta, e uma
    entrada antiga com outro conteúdo derrubaria a tela inteira: o que se perde aqui é o detalhe,
    nunca a página.
    """
    try:
        return (
            VersaoConsolidada.objects.filter(pk=identificador)
            .select_related("edital", "source_publication")
            .first()
        )
    except (ValidationError, ValueError, TypeError):
        return None


def _origem_reaproveitada(edital):
    """De qual Edital e de qual versão este Edital partiu, ou `None` (023, FR-014, FR-014a).

    Lido da **trilha**, e não de coluna nova: a origem é ato, e ato mora na auditoria. O registro
    guarda o identificador da **versão** para não envelhecer (FR-015a), e é aqui que ele volta a ser
    legível — resolver a versão dá o Edital de graça, porque o Edital deriva dela.

    Nada é interpretado do texto: o motivo é um identificador, e um identificador não muda de forma
    quando alguém renomeia um rótulo.
    """
    registro = (
        RegistroAuditoria.objects.filter(
            aggregate_type="Edital",
            aggregate_id=edital.id,
            operation=OPERACAO_DE_REAPROVEITAMENTO,
        )
        .order_by("-occurred_at")
        .first()
    )
    if registro is None:
        return None
    versao = _versao_por_identificador(registro.reason)
    if versao is None:
        # A versão não é apagável — é append-only —, mas um motivo que não resolve não pode derrubar
        # a composição: o que se perde é o detalhe, não a tela.
        return {"edital": None, "versao": None, "quando": registro.occurred_at}
    return {
        "edital": versao.edital,
        "versao": versao,
        # A mesma frase da trilha, pela mesma razão: sem as duas datas, duas versões distintas se
        # anunciam iguais.
        "versao_por_extenso": _versao_por_extenso(versao),
        "quando": registro.occurred_at,
        "ator": registro.actor_subject,
    }


def _motivo_legivel(registro):
    """O motivo como pessoa lê. Hoje só a origem precisa de tradução (023, FR-014a).

    **Só a entrada desta operação**, e não a trilha inteira: outras operações gravam identificador
    no motivo — a `020` grava `anexo <uuid>` —, e uniformizá-las é decisão de quem for dono delas.
    """
    if registro.operation != OPERACAO_DE_REAPROVEITAMENTO:
        return registro.reason
    versao = _versao_por_identificador(registro.reason)
    if versao is None:
        return registro.reason
    origem = versao.edital
    return f"a partir do Edital {origem.number}/{origem.year}, {_versao_por_extenso(versao)}"


def _versao_por_extenso(versao):
    """A versão nomeada pelo ato que a produziu e pela vigência dela (023, FR-014a, SC-005).

    **Data não nomeia versão.** Publicar uma Retificação rematerializa **uma versão por fronteira
    temporal** (`publicacoes/application/retificacoes.py`), e uma Retificação posterior refaz as
    mesmas fronteiras: duas linhas distintas — com identificadores distintos, e conteúdo distinto —
    apareceriam como a mesma *"versão de 09/09/2026"*. `SC-005` ficaria atendido no banco e não na
    tela, que é o inverso do que ele pede.

    O par `(publicação que a produziu, vigência)` é **único por construção**: dentro de uma
    materialização as fronteiras são um conjunto, e entre materializações a Publicação de origem
    muda. E é a língua que o resto da interface já fala — a lista de documentos do Edital nomeia os
    atos pela ordem de publicação.
    """
    publicacao = versao.source_publication
    vigencia = timezone.localtime(versao.valid_from).strftime("%d/%m/%Y %H:%M")
    return f"versão da publicação nº {publicacao.publication_order}, vigente desde {vigencia}"


# Os dois momentos declaráveis, com o rótulo em português que a etapa **Inscrição** mostra. A
# ausência de declaração é a **primeira** opção da lista, com valor vazio: ela é o padrão, e não um
# terceiro valor — o Edital que não pede requerimento é a esmagadora maioria dos casos.
MOMENTOS_DO_REQUERIMENTO = (
    (nomes_do_requerimento.NA_INSCRICAO, "No ato da inscrição"),
    (nomes_do_requerimento.NA_CONVOCACAO, "Quando o candidato for convocado"),
)


OPERACOES = {
    "CRIAR": "Criação",
    "ALTERAR_RASCUNHO": "Alteração do rascunho",
    "ALTERAR_IDENTIFICACAO": "Alteração da identificação",
    # A declaração do Requerimento de Matrícula (029). Sem rótulo, a trilha exibiria o código cru
    # a quem responde *"quando o Edital passou a pedir isto?"*.
    "ALTERAR_REQUERIMENTO": "Alteração do Requerimento de Matrícula",
    # A cópia de configuração de outro Edital (023). Sem esta entrada a trilha exibiria o
    # código cru, e `US3` ficaria atendida no banco e não no canal do ator.
    "REAPROVEITAR_EDITAL": "Criação a partir de Edital anterior",
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
    # A prévia da exportação de matrículas (031). Ela nomeia quem declarou cor/raça que o
    # formato de destino não comporta, e por isso é registrada — a razão está em
    # `matriculas/domain/nomes.py`.
    "MATRICULA_PREVER": "Prévia de exportação para matrícula",
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
    # A apuração de ocupação (016) e os quatro atos da convocação (019), na mesma trilha e pela
    # razão de sempre: quem investiga por que alguém perdeu uma vaga lê a mesma tela de quem
    # investiga uma publicação.
    #
    # **A `016` estava faltando aqui**, e a trilha exibia `OCUPACAO_APURAR` cru. O achado é da `019`
    # e a correção é de uma linha — deixá-la para depois manteria o código na tela de quem audita.
    "OCUPACAO_APURAR": "Apuração de ocupação de vagas",
    # **As quatro frases dizem o ato praticado, e não o nome da função** (`FR-296`). "Convocação
    # praticada" é o que aconteceu; `CONVOCACAO_CONVOCAR` é como o sistema o chama internamente, e
    # quem audita não tem por que aprender esse vocabulário.
    "CONVOCACAO_CONVOCAR": "Convocação praticada",
    "CONVOCACAO_DESFECHAR": "Desfecho de convocação registrado",
    "CONVOCACAO_COMUNICAR": "Comunicação de convocação emitida",
    "CONVOCACAO_ATESTAR": "Atestado de fato externo registrado",
    # A leitura do candidato (`FR-288b`). Entra na mesma trilha porque a pergunta que ela responde
    # — *"a pessoa teve como saber?"* — é feita por quem responde por todo o resto do certame.
    "CONVOCACAO_LER": "Convocação lida pela pessoa convocada",
    # O envio do Requerimento de Matrícula (029). Mesma trilha, pela razão de sempre: quem responde
    # *"o que esta pessoa declarou, e sob qual declaração?"* lê a mesma tela de quem investiga uma
    # publicação. **As duas frases dizem o ato, e não o nome da função** (`FR-296`).
    "REQUERIMENTO_ENVIAR": "Requerimento de Matrícula enviado",
    "REQUERIMENTO_SUCEDER": "Requerimento de Matrícula atualizado por sucessão",
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
    "ApuracaoDeOcupacao": "Apuração de ocupação",
    "Convocacao": "Convocação",
    "DesfechoDaConvocacao": "Desfecho de convocação",
    "ComunicacaoEmitida": "Comunicação de convocação",
    "AtestadoDeFatoExterno": "Atestado de fato externo",
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
                    "motivo": _motivo_legivel(registro),
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
            # **Um Processo reúne Editais, e o painel só sabia mostrar o primeiro.** O modelo
            # sempre admitiu mais de um — a suíte depende disso para demonstrar que "o total é a
            # soma dos Editais" — e `add_edital` já servia à API. Faltava a porta.
            #
            # Processo em estado final não a recebe: `ensure_processo_accepts_changes` recusaria, e
            # oferecer o botão convidaria a um ato que será recusado.
            "pode_criar_edital": (
                ator.can("edital:criar") and processo.status not in PROCESSO_FINAL
            ),
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
            # O outro lado da mesma pergunta. Quem não elabora via o painel oferecer só "Ativar" e
            # "Cancelar", sem nada dizer que o certame espera outra pessoa — enquanto a página do
            # Edital já sabe dizer exatamente isso ("Aguardando quem elabora"). Nomear a espera é o
            # que separa "não há o que fazer" de "não há o que **você** faça agora".
            "aguardando_elaboracao": (
                None
                if ator.can("edital:elaborar")
                else processo.editais.filter(status=Edital.Status.EM_ELABORACAO)
                .order_by("year", "number")
                .first()
            ),
        },
    )


@require_http_methods(["GET"])
def supervisao(request, processo_id):
    """O Pulso e a Atenção do Processo, numa leitura só (022, FR-001).

    **A porta é a mesma da página do Processo** — presidência deste Processo ou a permissão
    sistêmica de gerir comissão, cada uma suficiente sozinha (FR-002). Tudo o que o ator não
    alcança responde a mesma coisa que um Processo inexistente responderia: distinguir "não existe"
    de "você não pode" diria a quem não alcança que o Processo existe (FR-003, SC-012).

    Nada aqui grava: a resposta é idempotente e não gera trilha. Ler um agregado do próprio
    Processo que se preside não é ato sensível, e nenhuma tela de leitura existente registra.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    processo = _processo_do_ator(ator, processo_id)
    if supervisao_do_processo.pode_supervisionar(ator, processo) is None:
        raise Http404
    return render(
        request,
        "interface/supervisao.html",
        {
            "processo": processo,
            "pulso": supervisao_do_processo.pulso(processo),
            # Os sinais recebem o ator, e o Pulso não: a supressão por alcance é **por sinal**,
            # porque é o sinal que tem destino (FR-004, FR-004a).
            "sinais": supervisao_do_processo.sinais(processo, ator),
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


# ---------------------------------------------------------------------------
# A exportação de matrículas (031). Duas metades numa rota só: o GET escolhe a população e **lê as
# lacunas antes do download** (`UX-060`), e o POST gera o arquivo. Depois do download ninguém lê o
# resumo, e é por isso que ele não pode vir junto.
#
# **É aqui que `interface` passa a conhecer `matriculas`, e é a única porta.** O app é a ponta da
# leitura e ninguém o importa — `tests/test_matriculas_e_ponta.py` prende isso, com esta view como a
# exceção nomeada: `interface` é o canal do ator, e nenhum app de domínio a importa de volta, de
# modo que o ciclo continua impossível.
# ---------------------------------------------------------------------------


@require_http_methods(["GET", "POST"])
def exportar_matriculas(request, edital_id):
    """A tela que gera o arquivo de importação do Registro Acadêmico (031, `US1`, `US2`).

    **A recusa mora na aplicação, e a tela apenas a antecipa** (Princípio IV). Quem colar o endereço
    direto, sem a permissão própria, encontra a mesma recusa que o menu esconde — e quem não tem o
    Edital no escopo recebe 404, indistinguível de inexistente.
    """
    from processo_seletivo.matriculas.application import exportar as exportacao
    from processo_seletivo.matriculas.application import populacao as populacoes
    from processo_seletivo.matriculas.domain import nomes as nomes_da_exportacao

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
    # 403 quando falta a permissão própria, e a página de recusa diz qual é. Esconder a tela com um
    # 404 aqui confundiria *"você não pode"* com *"isto não existe"* — e a primeira é acionável.
    require_permission(ator, nomes_da_exportacao.EXPORTAR)

    dados = request.POST if request.method == "POST" else request.GET
    escolha = (dados.get("populacao") or "").strip()
    especie, _, referencia = escolha.partition(":")
    contexto = {
        "processo": edital.processo,
        "edital": edital,
        "populacoes": populacoes.opcoes(edital),
        "escolha": escolha,
    }
    if not escolha:
        return marcar_como_privada(render(request, "interface/matriculas.html", contexto))
    try:
        if request.method == "POST":
            arquivo = exportacao.gerar(
                ator=ator,
                edital=edital,
                especie=especie,
                referencia=referencia,
                # **A assinatura do que a pessoa conferiu** (`UX-060`). Ela viaja num campo oculto
                # da prévia; quem chega por `POST` sem passar por lá não a tem, e quem passou por
                # uma prévia que envelheceu tem a errada. Os dois são recusados pelo comando.
                confirmacao_do_resumo=request.POST.get("confirmacao_do_resumo", ""),
            )
            resposta = HttpResponse(
                arquivo.conteudo, content_type=nomes_da_exportacao.TIPO_DO_ARQUIVO
            )
            # `attachment`: o arquivo é para o Registro Acadêmico, e não para ser lido no navegador.
            resposta["Content-Disposition"] = f'attachment; filename="{arquivo.nome}"'
            return marcar_como_privada(resposta)
        composicao = exportacao.compor(
            ator=ator, edital=edital, especie=especie, referencia=referencia
        )
    except DomainError as recusa:
        # **A recusa volta para esta tela, e não para a página genérica** (`UX-061`): quem conduz
        # precisa ler quem falta com a escolha ainda à vista, para cobrar a pessoa ou trocar de
        # população sem refazer o caminho.
        contexto["erro"] = recusa.detail
        return marcar_como_privada(
            render(request, "interface/matriculas.html", contexto, status=recusa.status)
        )
    # **A prévia que nomeia pessoas é acesso a dado sensível, e fica registrada** (Princípio III).
    # Ela diz *"fulana declarou Indígena"* — cor/raça, nominalmente —, e a `GeracaoDeArquivo` não a
    # alcança de propósito: aquele registro é do **arquivo**, e a prévia não gera arquivo nenhum.
    # Sem esta linha, a leitura mais sensível desta tela seria a única que não deixa rastro.
    #
    # **O registro referencia e não copia**: ator, Edital, população e instante. Uma trilha que
    # repetisse a declaração multiplicaria a superfície em vez de protegê-la (`FR-401` da `029`).
    if composicao.nomeia_pessoas:
        record_event(
            actor=ator,
            permission=nomes_da_exportacao.EXPORTAR,
            operation=nomes_da_exportacao.OPERACAO_PREVIA,
            aggregate=edital,
            now=timezone.now(),
            correlation_id=request.correlation_id,
            reason=f"prévia de exportação: {composicao.populacao.rotulo}; "
            f"{composicao.quantidade} linha(s)",
            new_state=edital.status,
            new_revision=None,
        )
    contexto.update(
        {
            "composicao": composicao,
            "populacao": composicao.populacao,
            "relatorio": composicao.relatorio,
        }
    )
    return marcar_como_privada(render(request, "interface/matriculas.html", contexto))


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


# ---------------------------------------------------------------------------
# **As bases que as portas da gestão aceitam, nomeadas como a recusa as apresenta** (033).
#
# Ficam aqui, e não na camada de segurança, porque o conjunto aceito é **de quem chama** e não da
# porta: duas portas têm modo, e nelas o conjunto muda conforme a tela (`FR-479`, `FR-489`). O
# mecanismo mora em `seguranca/application`; a composição é de quem pergunta.
#
# A presidência é a única que não nasce de `base_de_permissao`, e a diferença é o ponto da
# `FR-485`: ela **não é papel**, vem da composição da comissão, e nenhum papel a concede. Mandar
# pedir "o papel de presidente" mandaria pedir o que não existe.
# ---------------------------------------------------------------------------

BASE_DE_GESTAO = base_de_permissao("gerir a comissão")
BASE_DA_PRESIDENCIA = Base("a presidência deste Processo", "a quem preside este Processo")
BASE_DE_AUDITORIA = base_de_permissao("consultar auditoria")
BASE_DE_PUBLICAR_RESULTADO = base_de_permissao("publicar resultado")

# O predicado de `pode_gerir_comissao`, dito como recusa: as duas bases que ela aceita.
BASES_DA_GESTAO_DA_COMISSAO = (BASE_DE_GESTAO, BASE_DA_PRESIDENCIA)
# E o mesmo, acrescido da leitura por auditoria — que serve em **algumas** chamadas, nunca em
# todas. É por isso que são duas constantes e não uma com argumento opcional.
BASES_DA_GESTAO_OU_AUDITORIA = (BASE_DE_GESTAO, BASE_DA_PRESIDENCIA, BASE_DE_AUDITORIA)


def _processo_para_gerir(request, processo_id):
    """Processo, ator e base — com 404 só para o que não existe ou é de outra unidade (D-017).

    **A negativa era 404 para tudo**, e ela confundia duas coisas diferentes. Processo de outro
    escopo institucional é 404 e continua sendo: `_processo_do_ator` filtra por escopo na própria
    consulta, e o ator não deve sequer saber que aquele Processo existe. Falta de base é sobre o
    ator, e responder "não encontrado" fazia a tela mentir sobre por que ela não abre (033,
    `FR-478`).

    A pergunta desta porta é **composta** — a permissão sistêmica de gerir a comissão **ou** a
    presidência deste Processo, cada uma suficiente sozinha —, e é por não haver como recusá-la
    num ponto só que esta porta improvisou o seu próprio `raise Http404`, igual às outras três.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, None, None
    processo = _processo_do_ator(ator, processo_id)
    base = pode_gerir_comissao(ator, processo)
    require_authorization_base(base is not None, bases=BASES_DA_GESTAO_DA_COMISSAO)
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
    # **Duas condições, duas respostas — e elas compartilhavam um `if`** (033, `FR-488`):
    #
    #     if edital is None or pode_gerir_comissao(ator, edital.processo) is None:
    #
    # Enquanto estivessem juntas, trocar o 404 por recusa explicada responderia recusa explicada
    # também para Edital de outra unidade, e isso é vazamento — não melhoria. **Separar veio
    # antes de mudar a gramática**, e não como arrumação: é a ordem que impede o vazamento.
    #
    # A de cima continua sendo 404 e continua sendo indistinguível de objeto inexistente, porque a
    # consulta acima filtra por `institution_scope` (`FR-487`). A de baixo é sobre o ator.
    if edital is None:
        raise Http404
    require_authorization_base(
        pode_gerir_comissao(ator, edital.processo) is not None,
        bases=BASES_DA_GESTAO_DA_COMISSAO,
    )
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

    **Confirmação em dois passos, como a ocorrência e como o impedimento da 012.** O primeiro passo
    declara o alcance — quantas viram Resultado, com que consequência, e quais ficam de fora e por
    quê — e o segundo pratica o ato. O botão ficava numa barra ao lado de "Distribuir as
    selecionadas", que se desfaz, e este não: consolidar é irreversível, e a V1 não oferece
    anulação.
    """
    ator, edital, etapa = _etapa_para_distribuir(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    destino = reverse("interface:distribuicao", args=[edital_id, etapa_id])
    marcadas = request.POST.getlist("inscricao_id")
    chave = request.POST.get("chave_idempotencia") or uuid4().hex
    if request.POST.get("confirmar") != "1":
        try:
            _etapa, consolidaveis, recusas = consolidacao_app.prever(
                edital=edital, etapa_id=etapa_id, inscricao_ids=marcadas
            )
        except DomainError as recusa:
            if recusa.status == 404:
                raise Http404 from recusa
            # Erro sobre o **pedido** — seleção vazia, Etapa bloqueada, inscrição que a tela não
            # deveria ter oferecido — volta para a tela que o produziu. Declarar o alcance de um
            # pedido que não se pode praticar seria oferecer a confirmação de coisa nenhuma.
            request.session["erro_da_consolidacao"] = recusa.detail
            return redirect(destino)
        return marcar_como_privada(
            render(
                request,
                "interface/consolidacao_confirmar.html",
                {
                    "edital": edital,
                    "processo": edital.processo,
                    "etapa": etapa,
                    "consolidaveis": consolidaveis,
                    "recusas": recusas,
                    "chave_idempotencia": chave,
                },
            )
        )
    try:
        request.session["resultado_da_consolidacao"] = consolidacao_app.consolidar(
            actor=ator,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            etapa_id=etapa_id,
            inscricao_ids=marcadas,
            idempotency_key=chave,
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

    **E uma confirmação antes**, como a inclusão na comissão já tinha. As caixas ficam numa lista
    em colunas, duas por inscrição, e marcar a errada é retirar trabalho de alguém sem que nada o
    pergunte. A conferência nomeia quem perde cada inscrição — e quais a via comum não alcança,
    que era a recusa que só se lia depois de tentar (FR-092).
    """
    ator, edital, etapa = _etapa_para_distribuir(request, edital_id, etapa_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    destino = reverse("interface:distribuicao", args=[edital_id, etapa_id])
    marcadas = request.POST.getlist("atribuicao_id")
    chave = request.POST.get("chave_idempotencia") or uuid4().hex
    if request.POST.get("confirmar") != "1":
        if not marcadas:
            request.session["erro_da_distribuicao"] = (
                "Selecione ao menos uma atribuição para remover."
            )
            return redirect(destino)
        return marcar_como_privada(
            render(
                request,
                "interface/distribuicao_remover_confirmar.html",
                {
                    "edital": edital,
                    "processo": edital.processo,
                    "etapa": etapa,
                    "etapa_id": etapa_id,
                    **_alcance_da_remocao(edital, etapa_id, marcadas),
                    "chave_idempotencia": chave,
                },
            )
        )
    try:
        request.session["resultado_da_distribuicao"] = distribuicao_app.remover_atribuicao(
            actor=ator,
            processo_id=edital.processo_id,
            atribuicao_ids=marcadas,
            idempotency_key=chave,
            correlation_id=getattr(request, "correlation_id", ""),
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        request.session["erro_da_distribuicao"] = recusa.detail
    return redirect(destino)


def _alcance_da_remocao(edital, etapa_id, atribuicao_ids):
    """O que a remoção alcança e o que ela não alcança, lido sem trava e sem inativar nada.

    **A palavra final continua sendo do comando**, que relê sob `select_for_update`: entre esta
    tela e a confirmação alguém pode concluir uma avaliação, e é a trava que impede a via comum de
    alcançar trabalho concluído (FR-092). O que se lê aqui é o alcance provável, e a recusa
    declarada na volta continua respondendo pelo que de fato aconteceu.
    """
    from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao

    atribuicoes = list(
        Atribuicao.objects.filter(
            pk__in=[item for item in atribuicao_ids if _e_identificador(item)],
            edital=edital,
            etapa_id=etapa_id,
            ativo=True,
        )
        .select_related("membro", "inscricao")
        .order_by("inscricao__protocolo", "membro__identity_subject")
    )
    concluidas = set(
        Avaliacao.objects.filter(
            atribuicao__in=atribuicoes, estado=Avaliacao.Estado.CONCLUIDA
        ).values_list("atribuicao_id", flat=True)
    )
    return {
        "removiveis": [item for item in atribuicoes if item.id not in concluidas],
        "intocaveis": [item for item in atribuicoes if item.id in concluidas],
    }


def _e_identificador(valor):
    """Um `atribuicao_id` que não é UUID não é recusa de linha: é pedido que a tela não fez."""
    try:
        UUID(str(valor))
    except (TypeError, ValueError):
        return False
    return True


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
    # O conteúdo publicado é lido **uma vez** e entregue: `effective_version` custa duas consultas,
    # e a condição do corte da 014 precisa dos marcos que governam esta Etapa (014, R-005).
    conteudo_publicado = conteudo_vigente(edital)
    panorama = prontidao_013.panorama_da_etapa(
        edital=edital, etapa=etapa, conteudo=conteudo_publicado
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
                # **O impedimento anunciado antes de alguém bater nele**, como a tela da Comissão
                # faz com a presidência ausente. Distribuir com o período aberto é recusado pelo
                # domínio nos três caminhos, e a tela oferecia os dois botões sem dizer nada: a
                # frase só aparecia depois do clique, com a seleção já montada. É a mesma recusa,
                # lida da mesma função — sem consulta nova, porque o conteúdo já está em mão.
                "inscricoes_em_curso": (
                    recusa_por_inscricoes_em_curso(conteudo_publicado, timezone.now())
                ),
                "bloqueio_da_etapa": panorama["bloqueio_da_etapa"],
                # Quem voltou ao certame por recurso aparece **nomeada** na Mesa: sem isso, ela
                # entraria na lista como mais uma pendente, e a presidência não saberia por que
                # alguém que estava eliminada reapareceu (FR-077).
                "reabilitadas": _reabilitadas_da_etapa(edital, etapa_id),
                # **O histórico do par não entra aqui**, e a razão não é custo: a Mesa organiza
                # trabalho — quem falta avaliar, quem falta consolidar —, e a pergunta "o que a
                # decisão alterou" é do painel de Resultados. Foi tentar respondê-la nas duas
                # telas que quebrou esta: aqui as linhas são dicionários de prontidão, e não
                # `ResultadoEtapa`.
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
                # A reabilitação por recurso, nomeada na própria linha: a nota mudou porque um
                # recurso foi deferido, e quem lê o painel precisa saber disso sem sair da tela
                # (FR-077). Uma consulta para a Etapa inteira, e nenhuma por linha.
                "reabilitadas": _reabilitadas_da_etapa(edital, etapa_id),
                # **O histórico do par, para quem responde a um recurso** (FR-064). Sem ele, a
                # tela mostra a nota corrigida e cala sobre a que foi corrigida — e quem precisa
                # conferir o que a decisão alterou teria de sair do sistema para fazê-lo.
                "historicos": _historicos_superados(linhas, etapa_id),
                "consequencia": request.GET.get("consequencia") or "",
                # Os rótulos que **este** Edital publicou: quem consulta o Resultado tem direito ao
                # vocabulário do Edital, e não ao enum do domínio (FR-118).
                "rotulo_favoravel": rotulos(etapa)[0],
                "rotulo_desfavoravel": rotulos(etapa)[1],
            },
        )
    )


def _historicos_superados(linhas, etapa_id):
    """`{inscricao_id: [linhas do par]}` — **somente** onde houve superação, numa consulta só.

    A leitura é feita só para quem tem sucessor: o par sem cadeia responde uma linha só, e pagar
    uma leitura por inscrição para descobrir isso devolveria à listagem o custo por linha que a
    012 tirou dela.

    **E é uma leitura para todos, e não uma por par.** A primeira versão chamava `historico_do_par`
    dentro do laço, e a página lista até vinte e cinco linhas: com metade delas vindas de recurso
    deferido, a tela pagava mais de uma dezena de consultas extras — e o custo crescia com o
    **sucesso** dos recursos, que é o que a instituição espera que aconteça (FR-061).
    """
    from processo_seletivo.resultados.application.selectors import historicos_dos_pares

    return historicos_dos_pares(
        [
            linha.inscricao_id
            for linha in linhas
            if getattr(linha, "resultado_anterior_id", None) is not None
        ],
        etapa_id,
    )


def _reabilitadas_da_etapa(edital, etapa_id):
    """`{inscricao_id: linha}` de quem voltou por recurso e é relevante para esta Etapa.

    Alcança **todas** as Etapas do Edital, e não só esta: quem foi reabilitada na Etapa 1 reaparece
    como pendência na Etapa 2, e é ali que a presidência precisa do aviso. Restringir à Etapa atual
    nomearia a reabilitação só onde ela já é evidente, e a esconderia onde ela surpreende.
    """
    from processo_seletivo.resultados.application.selectors import (
        reabilitacao_da_inscricao,
        reabilitadas_por_recurso,
    )

    return {
        identidade: reabilitacao_da_inscricao(resultado)
        for identidade, resultado in reabilitadas_por_recurso(edital=edital).items()
    }


def _decisoes_a_citar(edital, marco_id, marco):
    """O que a tela de emissão oferece para citar — e nada além.

    Só as providências **pendentes deste marco**: oferecer as já cumpridas convidaria a recitar por
    engano, e oferecer as de outro marco convidaria a liberar uma definitiva que ninguém corrigiu.
    """
    from processo_seletivo.divulgacao.models import PublicacaoResultado
    from processo_seletivo.recursos.application.selectors import decisoes_a_citar

    publicacoes = list(
        PublicacaoResultado.objects.filter(edital=edital, marco_id=marco_id).values_list(
            "id", flat=True
        )
    )
    return decisoes_a_citar(
        edital=edital, marco_id=marco_id, marco=marco, publicacoes_do_marco=publicacoes
    )


def _pode_ver_a_classificacao(ator, edital):
    """A porta das telas da 015, lida de fora delas.

    É o mesmo teste que `_edital_para_classificar` aplica, e existe separado porque as telas da
    017 precisam **oferecer ou não** o caminho antes de alguém batê-lo: link para porta fechada
    responde 404, e 404 não explica nada a quem o recebe (FR-022, E2E17-002).
    """
    return pode_gerir_comissao(ator, edital.processo) is not None or ator.can("auditoria:consultar")


def _edital_para_classificar(request, edital_id, *, somente_gestao=False):
    """A porta do marco: presidência ou auditoria lê; só a base de gestão emite.

    **O 404 fica com o escopo e com o que não existe**; falta de base é recusa explicada, como em
    toda porta desta família (033, `FR-478`). O identificador público do marco não confere
    autorização e, no POST, a aplicação volta a conferir a gestão depois de obter a trava.

    **Esta porta tem dois modos, e o conjunto de bases muda entre eles** (`FR-489`). Na consulta, a
    capacidade de auditoria é uma das bases aceitas; com `somente_gestao` — que é a maioria das
    chamadas, porque emitir é ato de quem gere — ela **não** serve. Recusar as duas com a mesma
    frase mandaria metade das pessoas pedir uma permissão que não abriria aquela tela.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, None, False
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=ator.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None:
        raise Http404
    pode_emitir = pode_gerir_comissao(ator, edital.processo) is not None
    bases = BASES_DA_GESTAO_DA_COMISSAO if somente_gestao else BASES_DA_GESTAO_OU_AUDITORIA
    require_authorization_base(
        pode_emitir or (not somente_gestao and ator.can("auditoria:consultar")),
        bases=bases,
    )
    return ator, edital, pode_emitir


def _recorte_pedido(edital, marco_id, pedido):
    """O recorte de `?lista=`, reduzido à grafia canônica — ou 404 (034, FR-499, FR-503).

    **Normalizar aqui, e não só no cálculo**, porque a tela faz duas perguntas com o mesmo recorte —
    "qual é o ato vigente?" e "qual é a proposta de agora?" — e elas precisam falar do mesmo. Pedida
    a Modalidade que o Perfil aponta como sendo a ampla, o cálculo a reduziria ao nulo e a busca do
    vigente continuaria procurando por ela: a tela mostraria a ordem da ampla ao lado de um vigente
    que nunca existiu.

    A derivação é a única (`editais/domain/recortes.py`), e é a mesma que a ocupação consome.

    **Marco que a norma vigente já não conhece devolve o pedido cru, e não 404.** A tela do marco
    removido existe de propósito (`015`, `E2E15-010`), e não há Perfil vigente contra o qual
    conferir recorte algum: exigi-lo aqui tornaria inalcançável justamente a tela do ato histórico,
    que é a que mais importa. O ato é buscado pela identidade, e não pela derivação.
    """
    from processo_seletivo.editais.domain.recortes import normalizar_recorte
    from processo_seletivo.publicacoes.application.selectors import effective_version

    lista_id = _identidade_ou_404(pedido)
    perfil, _ = _marco_publicado(edital, marco_id)
    if perfil is None:
        return lista_id
    try:
        return normalizar_recorte(
            effective_version(edital_id=edital.id).content,
            perfil_id=perfil["id"],
            lista_id=lista_id,
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        raise


def _recortes_navegaveis(edital, marco_id, *, rota, atual):
    """Os recortes do marco com o endereço de cada um — **derivados na view** (034, FR-497).

    **A decisão é da view, e não do template.** Repetir a derivação no template criaria duas
    verdades sobre a mesma lista, e elas divergem na primeira mudança: é a lição que a `033` pagou.
    O template recebe rótulo, endereço e qual é o atual, e não monta endereço nenhum.

    Devolve lista vazia quando o Perfil tem **um** recorte só. Um Edital sem reserva não ganha
    navegação nova — é a contraprova da `FR-493` vista na tela, e oferecer um seletor de um item
    seria dizer que há escolha onde não há.
    """
    from processo_seletivo.editais.domain.recortes import recortes_do_perfil
    from processo_seletivo.publicacoes.application.selectors import effective_version

    perfil, _ = _marco_publicado(edital, marco_id)
    if perfil is None:
        return []
    conteudo = effective_version(edital_id=edital.id).content
    recortes = recortes_do_perfil(conteudo, perfil_id=perfil["id"])
    if len(recortes) < 2:
        return []
    destino = reverse(rota, args=[edital.id, marco_id])
    return [
        {
            "lista_id": lista,
            "rotulo": rotulo,
            "href": destino if lista is None else f"{destino}?lista={lista}",
            "atual": lista == atual,
        }
        for lista, rotulo in recortes
    ]


def _navegacao_do_recorte(edital, marco_id, *, rota, atual):
    """`{recortes, recorte_atual, url_do_recorte}` — o que a navegação lê, derivado junto.

    **Juntas de propósito.** A tela do corte recebeu, numa primeira versão, só `recortes`, e o
    cabeçalho dela saiu com *"Recorte:"* seguido de nada: o template lia `recorte_atual`, que
    ninguém tinha passado, e o mecanismo trata variável ausente como vazia. Não houve erro, exceção
    nem teste vermelho — só uma tela que deixou de dizer em qual recorte se está, que é metade do
    que a `FR-497` pede. Foi o percurso do `quickstart` que o pegou.

    **`url_do_recorte` é o endereço desta mesma tela no recorte em que se está**, e existe para que
    nenhum template monte endereço com `?lista=` na mão. Quem volta de uma confirmação tem de voltar
    ao recorte que estava confirmando: um "Cancelar e voltar" que perde a `?lista=` devolve a pessoa
    à ampla concorrência, e ela reabre a conferência do recorte errado sem perceber.

    **Ela é calculada fora da lista de navegação, e não a partir dela.** A lista é vazia quando o
    Perfil tem um recorte só — é a contraprova da `FR-493` —, e derivar o endereço dali faria a
    volta sumir justamente no Edital sem reserva, que é onde ela sempre funcionou.
    """
    destino = reverse(rota, args=[edital.id, marco_id])
    recortes = _recortes_navegaveis(edital, marco_id, rota=rota, atual=atual)
    return {
        "recortes": recortes,
        "recorte_atual": next((item for item in recortes if item["atual"]), None),
        "url_do_recorte": f"{destino}?lista={atual}" if atual else destino,
    }


@require_http_methods(["GET"])
def ordenacao(request, edital_id, marco_id):
    """Calcula a ordem vigente de **um recorte**, sem constituir ato algum (015, FR-022).

    **O recorte vem em `?lista=`**, como na tela do corte (034, `FR-497`). A rota do corte já
    declarava esse padrão por escrito — "um marco de cotas tem três, e cada um tem a sua faixa" —, e
    inventar uma segunda gramática para a mesma coisa seria criar duas maneiras de dizer o mesmo.
    Ausente, o recorte é a ampla concorrência, que é o que esta tela sempre mostrou.
    """
    ator, edital, pode_emitir = _edital_para_classificar(request, edital_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    # **Marco de sorteio não se ordena por aqui, e a porta é esta.** A tela da `015` pende do
    # marco, e o Edital publica em quais marcos a ordem nasce de sorteio: aberta num deles, ela
    # calculava a ordem por Etapas e oferecia "Emitir ordem". O ato saía com `origem=COMPUTADO` e
    # `lista_id` nulo — que é exatamente a raiz que o sorteio da ampla concorrência precisa —, e
    # `constituir_sorteio` passava a recusar o certame inteiro com `ordering_act_already_exists`.
    # Não havia volta: a tabela é append-only, e a sucessão de um ato sorteado nasce da anulação
    # de um sorteio que nunca existiu (`021`, `D-006`, `FR-069`).
    if _e_marco_de_sorteio(edital, marco_id):
        return redirect(reverse("interface:sorteio", args=[edital_id, marco_id]))
    lista_id = _recorte_pedido(edital, marco_id, request.GET.get("lista"))
    try:
        estado = estado_do_marco(edital=edital, marco_id=marco_id, lista_id=lista_id)
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        raise
    proposta = estado["proposta"] or {"posicoes": [], "sem_posicao": []}
    navegacao = _navegacao_do_recorte(edital, marco_id, rota="interface:ordenacao", atual=lista_id)
    return marcar_como_privada(
        render(
            request,
            "interface/ordenacao.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "perfil": estado["perfil"],
                "marco": estado["marco"],
                "lista_id": lista_id,
                **navegacao,
                # **Ninguém concorreu aqui**, e é diferente de "ainda não emitiram" (`FR-492a`). Sem
                # esta distinção a tela do recorte vazio parece pendência, e a diferença entre as
                # duas frases é quem tem trabalho a fazer. Só faz sentido no recorte reservado: a
                # ampla vazia é um Edital sem inscrição nenhuma, que é outro assunto.
                "recorte_sem_ninguem": bool(
                    lista_id
                    and estado["proposta"] is not None
                    and not proposta["posicoes"]
                    and not proposta["sem_posicao"]
                ),
                # **A ordem única que já existe neste marco, quando este recorte não tem a sua**
                # (`FR-504`, `T032`). O ato da ampla não é corrigido nem substituído: emitir a
                # ordem deste recorte é ato novo, e o da ampla continua vigente. A tela diz isso em
                # vez de oferecer um conserto que a imutabilidade não permite — e a frase é
                # verdadeira tanto para o Edital do acervo quanto para o que está em andamento.
                "ordem_unica_do_marco": (
                    ato_vigente(edital=edital, marco_id=marco_id, lista_id=None)
                    if lista_id and estado["vigente"] is None
                    else None
                ),
                "posicoes": proposta["posicoes"],
                "sem_posicao": proposta["sem_posicao"],
                # O que se esgotou quando a ordem deixa gente empatada. Vem do marco e não da
                # linha, e por isso é uma leitura só para a tela inteira (015, FR-072).
                "criterios_do_desempate": estado.get("criterios_do_desempate") or [],
                "tem_empate_residual": any(
                    item.get("empate_residual") for item in proposta["posicoes"]
                ),
                "ato_vigente": estado["vigente"],
                "obsoleto": estado["obsoleto"],
                "recomputavel": estado["recomputavel"],
                "divergencias": estado["divergencias"],
                "posicoes_divergentes": estado["posicoes_divergentes"],
                "pode_emitir": pode_emitir,
                # **De quem é o ato de divulgar, lido contra quem está olhando** (033, `FR-477`).
                # Esta tela manda o operador à do ato, três vezes, para divulgar. Quem a lê é a
                # presidência — que é justamente quem **não** divulga na configuração segregada,
                # porque `resultado:publicar` não decorre de `comissao:gerir` nem da presidência.
                # Mandá-la a uma tela onde não haverá botão é o beco que o `ACH-38` descreve, e a
                # correção não é esconder a instrução: é dizer de quem o ato é.
                "pode_divulgar": ator.can("resultado:publicar"),
                # As providências a jusante pendentes deste marco: a emissão as oferece para que o
                # ato as cite, e é a citação **publicada** que prova o cumprimento (FR-089, T-015).
                "decisoes_a_citar": _decisoes_a_citar(edital, marco_id, estado["marco"]),
                "resultado": request.session.pop("resultado_da_ordenacao", None),
                "erro": request.session.pop("erro_da_ordenacao", None),
                "chave_idempotencia": uuid4().hex,
                "confirmacao_do_calculo": (
                    assinatura_da_proposta(proposta, ato_vigente=estado["vigente"])
                    if estado["proposta"] is not None
                    else ""
                ),
                "historico": historico_da_ordenacao(
                    edital=edital, marco_id=marco_id, lista_id=lista_id
                ),
                # Emitir não divulga, e a tela nunca dizia isso. Depois de um recurso deferido, a
                # sucessão do ato deixava a divulgação pública para trás — a página do candidato
                # seguia afirmando "Este é o resultado vigente" com a ordem anterior — e o marco
                # respondia apenas "Ordem emitida", sem mencionar publicação em lugar nenhum
                # (auditoria de 13/09). O estado é a correção; o botão sozinho não era.
                **_divulgacao_do_marco(edital, marco_id, estado["vigente"], lista_id=lista_id),
                # **A obsolescência do corte aparece ao abrir o marco** (014, UX-027). Sem isto,
                # quem sucede a ordem não fica sabendo que a faixa emitida leu o ato anterior:
                # descobriria ao tentar conduzir a Etapa governada, e a recusa chegaria no meio do
                # trabalho em vez de na tela que existe para conferir o marco.
                **_corte_do_marco(edital, marco_id, estado["marco"], lista_id=lista_id),
            },
        )
    )


def _divulgacao_do_marco(edital, marco_id, ato_vigente, *, lista_id=None):
    """Se o que está divulgado corresponde ao ato vigente deste marco.

    "Emitir" e "publicar" são atos distintos, em telas distintas, e essa é a distinção que o
    operador mais precisa trazer de fora. Aqui ela deixa de ser conhecimento prévio: a tela diz qual
    ordem o público está lendo.

    **Estado, e não ação.** A `017`, SC-002, declara que a tela de cálculo não oferece publicar, e
    o cenário de aceitação põe a ação na tela do ato. O que faltava aqui nunca foi o botão: era o
    operador não ter como saber que o ato e a divulgação tinham se separado — e descobrir isso pela
    página do candidato, que seguia afirmando "Este é o resultado vigente" com a ordem anterior.

    **Um ato por recorte, e a premissa mudou** (034, `FR-490`). Esta função comparava todas as
    publicações vigentes do marco contra um `ato_vigente` só, e dizia por escrito: *"se um dia um
    marco computado publicar por lista, esta função precisa comparar por lista"*. Esse dia é este.
    Sem o filtro, a divulgação da ordem da ampla apareceria como defasada ao se abrir o recorte de
    PPI — e a tela mandaria divulgar de novo um ato que já está divulgado.
    """
    if ato_vigente is None:
        return {"divulgacao": None}
    vigentes = [
        linha["publicacao"]
        for linha in historico_das_publicacoes(edital=edital, marco_id=marco_id)
        if linha["vigente"] and str(linha["publicacao"].ato.lista_id or "") == str(lista_id or "")
    ]
    defasadas = [
        publicacao for publicacao in vigentes if str(publicacao.ato_id) != str(ato_vigente.id)
    ]
    return {"divulgacao": {"nunca_divulgado": not vigentes, "defasadas": defasadas}}


def _com_o_corte(edital, marco, recortes):
    """Acrescenta a cada recorte o estado da faixa dele, sem exigir uma visita por lista (UX-029).

    Uma leitura por recorte, e não por participante: são no máximo as listas que o Perfil declara,
    e é a mesma pergunta que a tela do corte faz para um deles.
    """
    if not (marco or {}).get("cutRule"):
        return recortes
    perfil_id = _perfil_do_marco(edital, marco["id"])
    for recorte in recortes:
        estado = estado_do_corte(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco["id"],
            lista_id=recorte.get("lista_id") or None,
        )
        recorte["corte"] = {
            "faixas": estado["geracao"],
            "obsoleto": estado["obsoleto"],
            "causas": estado["causas"],
        }
    return recortes


def _corte_do_marco(edital, marco_id, marco, *, lista_id=None):
    """O estado da faixa vigente **deste recorte**, ou nada quando o marco não corta (014, UX-027).

    O recorte entra porque a faixa é dele (034, `FR-497`): sem ele, a tela do recorte de PPI
    anunciaria a obsolescência da faixa da ampla, que é de outra cadeia.
    """
    if not (marco or {}).get("cutRule"):
        return {"corte_obsoleto": False, "causas_do_corte": []}
    estado = estado_do_corte(
        edital=edital,
        perfil_id=_perfil_do_marco(edital, marco_id),
        marco_id=marco_id,
        lista_id=lista_id,
    )
    return {
        "corte_obsoleto": estado["obsoleto"],
        "causas_do_corte": estado["causas"],
        "tem_corte": bool(estado["geracao"]),
    }


def _marco_publicado(edital, marco_id):
    """`(perfil, marco)` como o Edital em vigor os publica, ou `(None, None)`.

    Devolver em vez de recusar porque nem todo chamador quer 404: a tela do marco removido existe
    justamente para o marco que a norma vigente já não conhece (`015`, `E2E15-010`).
    """
    from processo_seletivo.publicacoes.application.selectors import effective_version

    conteudo = effective_version(edital_id=edital.id).content
    alvo = str(marco_id)
    for perfil in conteudo.get("profiles") or []:
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) == alvo:
                return perfil, marco
    return None, None


def _e_marco_de_sorteio(edital, marco_id):
    """Se o Edital em vigor declara que a ordem daquele marco nasce de sorteio (`021`, `FR-014`).

    A pergunta é do **Edital publicado**, e não do que já foi emitido: um marco de sorteio ainda
    sem ato nenhum é o caso perigoso — é nele que a tela da `015` calculava uma ordem por Etapas
    para um marco que só o sorteio ordena.
    """
    from processo_seletivo.publicacoes.application.selectors import effective_version

    perfil, _ = _marco_publicado(edital, marco_id)
    if perfil is None:
        return False
    # **Pela resolução, e não pela chave do marco** (030, FR-429). Um marco que referencia o método
    # comum do Edital não tem `drawMethod` próprio, e ler a chave dele concluiria que ele não
    # sorteia — a tela da `015` voltaria a calcular uma ordem por Etapas para um marco que só o
    # sorteio ordena, que é o caso perigoso que esta função existe para desviar.
    return marcos.marco_ordena_por_sorteio(
        effective_version(edital_id=edital.id).content,
        perfil_id=perfil["id"],
        marco_id=marco_id,
    )


def _perfil_do_marco(edital, marco_id):
    """Resolve o pai normativo do marco sem depender da linha de elaboração."""
    perfil, _ = _marco_publicado(edital, marco_id)
    if perfil is None:
        raise Http404
    return perfil["id"]


@require_http_methods(["POST"])
def emitir_ordenacao(request, edital_id, marco_id):
    """Constitui o cálculo do servidor e volta à leitura pelo padrão POST-redirect-GET.

    **Confirmação em dois passos**, como a inclusão na comissão e a ocorrência da 013. O primeiro
    declara o alcance — quantos recebem posição, quantos ficam sem, o que este ato sucede e quais
    decisões ele executa — e o segundo pratica. A tela anterior mostra a ordem inteira, e é a razão
    de a confirmação não repeti-la: o que faltava não era ver as linhas, era ler, num lugar só, o
    que o clique constitui. O ato é imutável, e corrigi-lo é sucedê-lo.
    """
    ator, edital, _ = _edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    # Marco de sorteio não passa por aqui — ver a porta em `ordenacao`. Fechar só o GET deixaria
    # esta rota alcançável por quem tivesse a tela antiga aberta, e é ela que grava o ato.
    if _e_marco_de_sorteio(edital, marco_id):
        return redirect(reverse("interface:sorteio", args=[edital_id, marco_id]))
    # **O recorte vem no POST, e o destino volta para ele** (034, `FR-490`). Sem isso, emitir a
    # ordem de PPI devolveria o operador à tela da ampla — e a confirmação seria recomposta sobre
    # outro recorte, que é exatamente o que a `FR-495` existe para impedir.
    lista_id = _recorte_pedido(edital, marco_id, request.POST.get("lista"))
    destino = reverse("interface:ordenacao", args=[edital_id, marco_id]) + (
        f"?lista={lista_id}" if lista_id else ""
    )
    chave = request.POST.get("chave_idempotencia") or uuid4().hex
    motivo = request.POST.get("motivo", "")
    decisoes = request.POST.getlist("decisao")
    confirmacao_do_calculo = request.POST.get("confirmacao_do_calculo", "")
    if request.POST.get("confirmar") != "1":
        try:
            estado = estado_do_marco(edital=edital, marco_id=marco_id, lista_id=lista_id)
        except DomainError as recusa:
            if recusa.status == 404:
                raise Http404 from recusa
            request.session["erro_da_ordenacao"] = recusa.detail
            return redirect(destino)
        proposta = estado["proposta"] or {"posicoes": [], "sem_posicao": []}
        # As decisões chegam como identificadores; a confirmação precisa dizer **quais** são, e o
        # nome delas já está na lista que a tela anterior ofereceu. Citar por UUID na tela que
        # pergunta "confirma?" seria perguntar sobre o que não se pode ler.
        oferecidas = _decisoes_a_citar(edital, marco_id, estado["marco"])
        escolhidas = [item for item in oferecidas if str(item.id) in set(decisoes)]
        # **A assinatura é recomposta aqui**, e é a mesma razão que `_renderizar_previa` escreve:
        # o que a autoridade confirma é o que **esta** tela declarou, e não o que a anterior
        # calculou. Repassar a assinatura recebida faria a conferência declarar o alcance de agora
        # e enviar o token de antes — a emissão seria recusada por `proposta_mudou` depois de a
        # pessoa ter lido, e confirmado, números que estavam certos.
        recomposta = (
            assinatura_da_proposta(proposta, ato_vigente=estado["vigente"])
            if estado["proposta"] is not None
            else ""
        )
        return marcar_como_privada(
            render(
                request,
                "interface/ordenacao_confirmar.html",
                {
                    "processo": edital.processo,
                    "edital": edital,
                    "perfil": estado["perfil"],
                    "marco": estado["marco"],
                    "lista_id": lista_id,
                    **_navegacao_do_recorte(
                        edital, marco_id, rota="interface:ordenacao", atual=lista_id
                    ),
                    "quantas_com_posicao": len(proposta["posicoes"]),
                    "sem_posicao": proposta["sem_posicao"],
                    "ato_vigente": estado["vigente"],
                    "obsoleto": estado["obsoleto"],
                    "decisoes": escolhidas,
                    "motivo": motivo,
                    "chave_idempotencia": chave,
                    "confirmacao_do_calculo": recomposta,
                    # **Recompor não é esconder.** Quem abriu a tela anterior conferiu outra coisa,
                    # e confirmar em silêncio sobre um cálculo que mudou no caminho é o que a
                    # assinatura existe para impedir. A divergência é dita, e o alcance ao lado
                    # dela é o de agora.
                    "calculo_mudou": bool(
                        confirmacao_do_calculo and confirmacao_do_calculo != recomposta
                    ),
                },
            )
        )
    try:
        request.session["resultado_da_ordenacao"] = emitir_ordem(
            actor=ator,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=_perfil_do_marco(edital, marco_id),
            marco_id=marco_id,
            lista_id=lista_id,
            idempotency_key=chave,
            correlation_id=getattr(request, "correlation_id", ""),
            confirmacao_do_calculo=confirmacao_do_calculo,
            motivo=motivo,
            # As decisões que este ato executa. A tela as oferece; gravá-las é do comando, na mesma
            # transação do ato — citação é proveniência, e não passo humano separado (FR-089).
            decisoes=decisoes,
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        request.session["erro_da_ordenacao"] = recusa.detail
    return redirect(destino)


@require_http_methods(["GET"])
def corte_historico(request, edital_id, corte_id):
    """Um corte pela identidade dele — sucedido ou vigente —, com a proveniência inteira (UX-024).

    **Lido pela versão que ele congelou**, e não pela vigente: uma Retificação que renomeie o
    Perfil, o marco ou a Modalidade do recorte não reescreve como um corte antigo é lido. É a mesma
    regra que a `015` aplica ao ato de ordenação, e pela mesma razão — o ato é imutável, e a
    leitura dele também precisa ser.

    A reprodução aparece aqui porque é onde ela serve: registrar o que foi usado e **chegar de novo
    ao mesmo resultado** são coisas distintas, e a segunda é o que a Constituição pede (FR-199).
    """
    ator, edital, _ = _edital_para_classificar(request, edital_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    corte = corte_por_id(edital=edital, corte_id=corte_id)
    if corte is None:
        raise Http404
    itens = [
        {
            "inscricao_id": str(item.inscricao_id),
            "posicao": item.posicao,
            "consequencia": item.consequencia,
            "motivo": item.motivo,
            "excedente_por_empate": item.excedente_por_empate,
        }
        for item in corte.itens.all().order_by("posicao", "inscricao_id")
    ]
    _com_a_inscricao(itens)
    reproduzido = reproduzir_corte(corte)
    return marcar_como_privada(
        render(
            request,
            "interface/corte_historico.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "corte": corte,
                "nomes": nomes_do_corte(corte),
                "regra": (corte.universo or {}).get("cutRule") or {},
                "universo": corte.universo or {},
                "itens": itens,
                "geracao": geracao_do_corte(corte),
                # Quem abre um corte histórico precisa ler, **antes** dos valores, que a geração
                # dele já foi sucedida — sem isso dá para citar uma faixa superada sem perceber.
                "sucessores": list(corte.sucessores.all()) if corte.raiz_id is None else [],
                "reproduzido": reproduzido,
                "divergencias": divergencias_da_reproducao(corte, reproduzido=reproduzido),
            },
        )
    )


def _com_a_inscricao(itens):
    """Põe protocolo e nome ao lado da posição, no lugar do identificador interno (014, UX-025).

    O cálculo do corte é do domínio e não conhece `Inscricao` — ele fala em identidades, e é assim
    que o ato as congela. Quem lê a tela, porém, procura o protocolo: a tabela mostrava catorze
    UUIDs, e conferir quem progrediu exigia traduzi-los por fora (E2E14-006). Uma consulta só,
    como a tela do ato de ordenação faz na mesma coluna.
    """
    from processo_seletivo.inscricoes.models import Inscricao

    por_identidade = {
        str(inscricao.id): inscricao
        for inscricao in Inscricao.objects.filter(
            id__in=[item["inscricao_id"] for item in itens]
        ).only("id", "protocolo", "nome")
    }
    for item in itens:
        item["inscricao"] = por_identidade.get(item["inscricao_id"])
    return itens


def _identidade_ou_404(valor):
    """Uma identidade vinda da URL ou do formulário, ou `None` — e nunca lixo para o ORM.

    `?lista=abc` chegava ao banco como filtro de UUID e virava 500. O identificador público não
    confere autorização **e** não derruba o servidor: o que não é identidade é ausência.
    """
    if not valor:
        return None
    try:
        return str(UUID(str(valor)))
    except (TypeError, ValueError) as erro:
        raise Http404 from erro


def _inteiro_do_formulario(valor):
    """O que o campo numérico traz, ou `0` — a recusa é do domínio, e não do `int()`."""
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return 0


@require_http_methods(["GET"])
def corte(request, edital_id, marco_id):
    """Calcula a faixa para conferência, sem constituir ato algum (014, FR-190).

    Abrir a tela **não emite**: é o mesmo desenho da ordem, e pela mesma razão — um corte
    regenerado em silêncio quando a tela abre mudaria, sozinho, quem participa da Etapa seguinte.
    """
    ator, edital, pode_emitir = _edital_para_classificar(request, edital_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    # **Pela derivação única, e não só por `_identidade_ou_404`** (034, `FR-499`). Antes, um
    # identificador bem formado que não fosse Modalidade alguma do Perfil chegava ao corte como
    # recorte vazio — indistinguível de um recorte legítimo sem ordem, o que esconde erro de
    # digitação. E a Modalidade declarada como ampla, que o cálculo da linha já apelida para a linha
    # geral, procurava um ato vigente que nunca existiria.
    lista_id = _recorte_pedido(edital, marco_id, request.GET.get("lista"))
    perfil_id = _perfil_do_marco(edital, marco_id)
    # O estado traz a geração **e** as causas da obsolescência na mesma leitura: perguntá-las em
    # dois lugares daria duas respostas para a mesma faixa (014, UX-027).
    estado = estado_do_corte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    geracao = estado["geracao"]
    proposta, recusa = None, None
    try:
        proposta = calcular_corte(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
        )
    except DomainError as erro:
        if erro.status == 404:
            raise Http404 from erro
        # A recusa é **mostrada**, e não devolvida como erro de servidor: "este marco não corta" e
        # "a ordem está obsoleta" são estados legítimos da tela, e quem os lê precisa do motivo.
        recusa = erro.detail
    if proposta:
        _com_a_inscricao(proposta["itens"])
    return marcar_como_privada(
        render(
            request,
            "interface/corte.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "marco_id": marco_id,
                "lista_id": lista_id,
                **_navegacao_do_recorte(edital, marco_id, rota="interface:corte", atual=lista_id),
                # O caminho para emitir a ordem **deste** recorte, que é o que falta quando não há o
                # que cortar (`FR-498`). Nomear a pendência sem dizer onde ela se resolve manda o
                # operador procurar a tela — e a `033` registrou que esse é o beco do `ACH-40`.
                "para_a_ordenacao": reverse("interface:ordenacao", args=[edital.id, marco_id])
                + (f"?lista={lista_id}" if lista_id else ""),
                "proposta": proposta,
                "recusa": recusa,
                "geracao": geracao,
                "corte_obsoleto": estado["obsoleto"],
                "causas_do_corte": estado["causas"],
                "confirmacao": (assinatura_do_corte(proposta, geracao=geracao) if proposta else ""),
                # **A chave nasce aqui, e não no POST.** Gerada a cada POST, ela fazia de cada
                # clique um pedido novo: duplo clique ou reenvio do navegador produzia duas faixas
                # sucessivas, e a geração avançava duas vezes sem que ninguém pedisse. Nascida no
                # GET e enviada em campo oculto, a segunda tentativa da mesma leitura devolve o
                # desfecho da primeira — que é o que a idempotência existe para fazer.
                "chave_idempotencia": uuid4().hex,
                "pode_emitir": pode_emitir,
                "resultado": request.session.pop("resultado_do_corte", None),
                "erro": request.session.pop("erro_do_corte", None),
            },
        )
    )


@require_http_methods(["GET"])
def ocupacao(request, edital_id, marco_id):
    """Os quatro números de cada recorte do marco, e o estado de cada um (016, UX-031).

    **Abrir a tela não apura nada** (FR-261): é o mesmo desenho da ordem e do corte, e pela mesma
    razão — um número regenerado em silêncio quando a tela abre passaria a afirmar ocupação que ato
    nenhum sustenta.

    **Quantidade que nenhum ato produziu chega nula, e o template não a desenha.** Zero é afirmação
    — quer dizer "não há vaga a ocupar" —, e sem apuração emitida ninguém a fez (UX-032a).
    """
    from processo_seletivo.ocupacao.application.selectors import recortes_do_marco

    ator, edital, pode_emitir = _edital_para_classificar(request, edital_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    perfil_id = _perfil_do_marco(edital, marco_id)
    recortes = recortes_do_marco(edital=edital, perfil_id=perfil_id, marco_id=marco_id)
    return marcar_como_privada(
        render(
            request,
            "interface/ocupacao.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "marco_id": marco_id,
                "recortes": recortes,
                # **Quem pode retificar vê o caminho; quem não pode, vê o encaminhamento** (027,
                # FR-332). Critério da `026`: um link para quem não elabora Retificação terminaria
                # numa tela que se anuncia somente leitura, e trocar o beco sem saída por um beco
                # sinalizado não é ganho.
                "pode_retificar": ator.can("retificacao:elaborar"),
                # A chave nasce no GET pela razão que o corte já registra: gerada a cada POST, um
                # duplo clique produziria duas apurações sucessivas sem que ninguém pedisse.
                "chave_idempotencia": uuid4().hex,
                "pode_emitir": pode_emitir,
                "resultado": request.session.pop("resultado_da_ocupacao", None),
                # **Qual das duas ações aconteceu**, e não só que algo deu certo. As duas voltam
                # para esta tela, e um aviso único dizia "Apuração emitida" depois de causar a
                # faixa seguinte — frase falsa, porque apuração nenhuma foi emitida ali, e quem
                # acabara de pedir a faixa ficava sem confirmação de que ela saiu. Encontrado no
                # percurso conduzido da `016`.
                "acao": request.session.pop("acao_da_ocupacao", None),
                "erro": request.session.pop("erro_da_ocupacao", None),
            },
        )
    )


@require_http_methods(["GET"])
def ocupacao_historico(request, edital_id, marco_id):
    """Todas as apurações de um recorte, da mais antiga à mais nova (016, FR-259).

    **O recorte vem no caminho, e nada é resolvido no snapshot vigente.** A rota carrega o marco
    porque é ele que identifica a série, mas a busca é pelas **identidades publicadas** que as
    apurações guardaram — é o que mantém o histórico acessível depois de uma Retificação remover o
    marco, que é o precedente do `corte-historico`.

    **Lidas como foram emitidas.** Cada apuração guarda a versão do quadro, a ordem, o corte e os
    movimentos que considerou: uma Retificação posterior não reescreve o que uma apuração antiga
    apurou.
    """
    from processo_seletivo.ocupacao.application.selectors import historico_do_recorte

    ator, edital, _ = _edital_para_classificar(request, edital_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    lista_id = _identidade_ou_404(request.GET.get("lista"))
    # **Sem `_perfil_do_marco` aqui, e a ausência é a regra.** Aquele helper resolve o marco na
    # versão **vigente** e levanta 404 quando ele não está nela — de modo que uma Retificação que
    # removesse o marco faria o histórico antigo desaparecer, que é exatamente o que esta tela
    # existe para impedir. As apurações guardam Perfil e marco como identidades publicadas, e é por
    # elas que a série é encontrada.
    return marcar_como_privada(
        render(
            request,
            "interface/ocupacao_historico.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "marco_id": marco_id,
                "lista_id": lista_id,
                "serie": historico_do_recorte(edital=edital, marco_id=marco_id, lista_id=lista_id),
            },
        )
    )


@require_http_methods(["POST"])
def emitir_apuracao_view(request, edital_id, marco_id):
    """Emite a apuração de um recorte e volta à leitura, pelo padrão POST-redirect-GET."""
    from processo_seletivo.ocupacao.application.emissao import emitir_apuracao

    ator, edital, _ = _edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    lista_id = _identidade_ou_404(request.POST.get("lista"))
    destino = reverse("interface:ocupacao", args=[edital_id, marco_id])
    try:
        request.session["resultado_da_ocupacao"] = emitir_apuracao(
            actor=ator,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=_perfil_do_marco(edital, marco_id),
            marco_id=marco_id,
            lista_id=lista_id,
            idempotency_key=request.POST.get("chave") or uuid4().hex,
            correlation_id=f"interface-ocupacao-{edital_id}",
            motivo=(request.POST.get("motivo") or "").strip(),
        )
        request.session["acao_da_ocupacao"] = "apuracao"
    except DomainError as erro:
        request.session["erro_da_ocupacao"] = erro.detail
    return redirect(destino)


def convocacao(request, edital_id, marco_id):
    """A tela do recorte: quem foi chamado, o que respondeu, e quantas vagas ainda faltam (019).

    **Os quatro números são da `016`, e esta tela não os recalcula** (`UX-035`, `SC-092`). O que ela
    acrescenta é o que a planilha paralela guardava até hoje: quantas pessoas foram convocadas,
    quantas responderam, e quem é a próxima da fila.

    **Abrir a tela não convoca ninguém, e não apura nada.** É o mesmo desenho da ordem, do corte e
    da apuração — e pela mesma razão: um ato praticado por abrir uma página é um ato que ninguém
    decidiu praticar.
    """
    from processo_seletivo.convocacao.application.selectors import leitura_do_recorte

    ator, edital, pode_emitir = _edital_para_classificar(request, edital_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    perfil_id = _perfil_do_marco(edital, marco_id)
    lista_id = _identidade_ou_404(request.GET.get("lista"))
    leitura = leitura_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    return marcar_como_privada(
        render(
            request,
            "interface/convocacao.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "marco_id": marco_id,
                "lista_id": lista_id,
                "leitura": leitura,
                # **Se a fila esgotou porque o Edital não declarou quantidade** (027, FR-332).
                # "Não há mais quem chamar dentro da faixa que o corte alcançou" é verdadeiro e
                # manda a pessoa à Ocupação pedir a faixa seguinte — que responde "não há
                # quantidade declarada a apurar". Dois becos em sequência, e a causa em nenhum dos
                # dois. Dizer aqui qual é ela poupa a viagem.
                "sem_quadro_publicado": linha_do_quadro(
                    effective_version(edital_id=edital.id).content,
                    perfil_id=perfil_id,
                    lista_id=lista_id,
                )
                is None,
                "pode_retificar": ator.can("retificacao:elaborar"),
                # A chave nasce no GET pela razão que o corte e a ocupação já registram: gerada a
                # cada POST, um duplo clique praticaria dois atos sem que ninguém pedisse.
                "chave_idempotencia": uuid4().hex,
                "pode_emitir": pode_emitir,
                # **Qual ato aconteceu, e não só que algo deu certo** (`UX-036`). Foi o defeito
                # `E2E16-004` da `016`: três ações voltavam para a mesma tela com um aviso único, e
                # quem acabara de desfechar lia "Apuração emitida".
                "acao": request.session.pop("acao_da_convocacao", None),
                "resultado": request.session.pop("resultado_da_convocacao", None),
                "erro": request.session.pop("erro_da_convocacao", None),
            },
        )
    )


@require_http_methods(["GET"])
def convocacao_historico(request, edital_id, marco_id):
    """Todos os atos do recorte, com a proveniência de cada um (019, `FR-294`).

    **Inclusive os sucedidos.** Correção é sucessão, e é a linha anterior que explica o que foi
    corrigido e por quê — esconder as sucedidas deixaria a trilha contando metade da história.
    """
    from processo_seletivo.convocacao.application.selectors import (
        convocacoes_do_recorte,
        desfecho_de,
        envio_de,
        identidades_de,
        leitura_do_recorte,
        vigentes,
    )

    ator, edital, _ = _edital_para_classificar(request, edital_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    lista_id = _identidade_ou_404(request.GET.get("lista"))
    # **Sem `_perfil_do_marco` aqui, pela razão que a `016` já registra**: aquele helper resolve o
    # marco na versão vigente e levanta 404 quando ele não está nela, de modo que uma Retificação
    # que removesse o marco faria desaparecer o histórico que explica os atos daquela época.
    perfil_id = _perfil_do_marco(edital, marco_id)
    convocacoes = convocacoes_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    em_vigor = {c.id for c in vigentes(convocacoes)}
    # **A posição nova do reclassificado é derivada, e aparece no histórico** (019, `FR-291`). Ela
    # não é coluna: guardá-la exigiria `UPDATE` numa tabela append-only, e cada chamada seguinte a
    # deslocaria. O que o histórico mostra é onde ele está **agora** na fila — que é a pergunta que
    # quem conduz o certame faz ao ler a linha.
    contexto = leitura_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    posicoes = {str(item["id"]): indice for indice, item in enumerate(contexto["fila"], start=1)}
    identificadas = identidades_de({c.inscricao_id for c in convocacoes})
    return marcar_como_privada(
        render(
            request,
            "interface/convocacao_historico.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "marco_id": marco_id,
                "lista_id": lista_id,
                "serie": [
                    {
                        "inscricao": identificadas[convocacao.inscricao_id],
                        "convocacao": convocacao,
                        "desfecho": desfecho_de(convocacao),
                        "enviadaEm": envio_de(convocacao),
                        "comunicacoes": list(convocacao.comunicacoes.all()),
                        "vigente": convocacao.id in em_vigor,
                        "posicaoNaFila": posicoes.get(str(convocacao.inscricao_id)),
                    }
                    for convocacao in convocacoes
                ],
            },
        )
    )


@require_http_methods(["POST"])
def convocar_view(request, edital_id, marco_id):
    """Pratica a convocação e volta à leitura, pelo padrão POST-redirect-GET."""
    from processo_seletivo.convocacao.application.convocar import convocar

    ator, edital, _ = _edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    lista_id = _identidade_ou_404(request.POST.get("lista"))
    destino = _volta_para_convocacao(edital_id, marco_id, lista_id)
    try:
        request.session["resultado_da_convocacao"] = convocar(
            actor=ator,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=_perfil_do_marco(edital, marco_id),
            marco_id=marco_id,
            lista_id=lista_id,
            inscricao_id=_identidade_ou_404(request.POST.get("inscricao")),
            especie=request.POST.get("especie") or "",
            fundamento=request.POST.get("fundamento") or "",
            vencimento=_instante_ou_none(request.POST.get("vencimento")),
            motivo=(request.POST.get("motivo") or "").strip(),
            justifica_precedencia=bool(request.POST.get("justifica_precedencia")),
            idempotency_key=request.POST.get("chave") or uuid4().hex,
            correlation_id=f"interface-convocacao-{edital_id}",
        )
        request.session["acao_da_convocacao"] = "convocacao"
    except DomainError as erro:
        request.session["erro_da_convocacao"] = erro.detail
    return redirect(destino)


@require_http_methods(["POST"])
def desfechar_view(request, edital_id, marco_id, convocacao_id):
    """Registra o desfecho e volta à leitura."""
    from processo_seletivo.convocacao.application.desfechar import desfechar

    ator, edital, _ = _edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    lista_id = _identidade_ou_404(request.POST.get("lista"))
    destino = _volta_para_convocacao(edital_id, marco_id, lista_id)
    try:
        request.session["resultado_da_convocacao"] = desfechar(
            actor=ator,
            processo_id=edital.processo_id,
            convocacao_id=convocacao_id,
            especie=request.POST.get("especie") or "",
            fundamento=request.POST.get("fundamento") or "",
            atestado_id=_identidade_ou_404(request.POST.get("atestado")),
            idempotency_key=request.POST.get("chave") or uuid4().hex,
            correlation_id=f"interface-desfecho-{edital_id}",
        )
        request.session["acao_da_convocacao"] = "desfecho"
    except DomainError as erro:
        request.session["erro_da_convocacao"] = erro.detail
    return redirect(destino)


@require_http_methods(["POST"])
def comunicar_view(request, edital_id, marco_id, convocacao_id):
    """Emite a comunicação na forma declarada e volta à leitura."""
    from processo_seletivo.convocacao.application.comunicar import comunicar

    ator, edital, _ = _edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    lista_id = _identidade_ou_404(request.POST.get("lista"))
    destino = _volta_para_convocacao(edital_id, marco_id, lista_id)
    try:
        request.session["resultado_da_convocacao"] = comunicar(
            actor=ator,
            processo_id=edital.processo_id,
            convocacao_id=convocacao_id,
            idempotency_key=request.POST.get("chave") or uuid4().hex,
            correlation_id=f"interface-comunicar-{edital_id}",
            endereco_do_portal=request.build_absolute_uri(reverse("portal:inscricoes")),
            referencia_da_publicacao=request.POST.get("referencia_da_publicacao") or "",
        )
        request.session["acao_da_convocacao"] = "comunicacao"
    except DomainError as erro:
        request.session["erro_da_convocacao"] = erro.detail
    return redirect(destino)


@require_http_methods(["POST"])
def atestar_view(request, inscricao_id):
    """Registra o atestado de fato externo e volta para onde o pedido veio.

    **O atestado não cancela matrícula nenhuma**: ele é insumo do desfecho de inércia, que é outro
    ato — possivelmente de outra pessoa. Quem constata o fato e quem decide a consequência dele não
    precisam ser a mesma, e separá-los é o que torna a decisão auditável (`D-004`).
    """
    from processo_seletivo.convocacao.application.atestar import atestar
    from processo_seletivo.inscricoes.models import Inscricao

    inscricao = Inscricao.objects.filter(pk=inscricao_id).select_related("edital").first()
    if inscricao is None:
        raise Http404
    ator, edital, _ = _edital_para_classificar(request, inscricao.edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    destino = _destino_interno(
        request.POST.get("voltar"), reverse("interface:detalhe", args=[edital.id])
    )
    try:
        request.session["resultado_da_convocacao"] = atestar(
            actor=ator,
            processo_id=edital.processo_id,
            inscricao_id=inscricao_id,
            especie=request.POST.get("especie") or "",
            conclusao=request.POST.get("conclusao") or "",
            referencia_do_prazo=request.POST.get("referencia_do_prazo") or "",
            idempotency_key=request.POST.get("chave") or uuid4().hex,
            correlation_id=f"interface-atestado-{inscricao_id}",
        )
        request.session["acao_da_convocacao"] = "atestado"
    except DomainError as erro:
        request.session["erro_da_convocacao"] = erro.detail
    return redirect(destino)


def _destino_interno(pedido, padrao):
    """O destino do POST-redirect-GET, **conferido** antes de virar `Location`.

    **Um `voltar` vindo do corpo do pedido é entrada do usuário, e não configuração.** Sem esta
    conferência, um formulário forjado noutro domínio levaria quem está autenticado na gestão para
    fora do sistema com um clique — e a página de destino veria um visitante que acabou de praticar
    um ato administrativo.

    Aceita só caminho do próprio servidor: nem host, nem esquema, nem `//` que o navegador leria
    como origem.
    """
    from django.utils.http import url_has_allowed_host_and_scheme

    candidato = (pedido or "").strip()
    if candidato and url_has_allowed_host_and_scheme(candidato, allowed_hosts=None):
        return candidato
    return padrao


def _volta_para_convocacao(edital_id, marco_id, lista_id):
    """O destino do POST-redirect-GET, **preservando o recorte**.

    Sem o `?lista=`, desfechar numa lista reservada devolveria a pessoa à ampla concorrência — e ela
    leria a confirmação de um ato ao lado dos números de outro recorte.
    """
    destino = reverse("interface:convocacao", args=[edital_id, marco_id])
    return f"{destino}?lista={lista_id}" if lista_id else destino


def _instante_ou_none(valor):
    """O vencimento informado no formulário, ou `None` quando o Edital não publica prazo.

    **O sistema não calcula dias úteis** (`R-004`): o que entra aqui é a data e a hora que quem
    convoca digitou, interpretadas no fuso da instalação.
    """
    from django.utils.dateparse import parse_datetime

    texto = (valor or "").strip()
    if not texto:
        return None
    instante = parse_datetime(texto)
    if instante is None:
        raise Http404
    return instante if timezone.is_aware(instante) else timezone.make_aware(instante)


@require_http_methods(["POST"])
def causar_faixa_view(request, edital_id, marco_id):
    """Pede à `014` a faixa seguinte com o déficit apurado como causa (016, FR-255).

    **Esta ação não seleciona ninguém.** Ela entrega quantidade e motivo; quem lê a ordem e escolhe
    é a `014`, do outro lado da chamada.
    """
    from processo_seletivo.ocupacao.application.causar_faixa import causar_faixa_seguinte

    ator, edital, _ = _edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    lista_id = _identidade_ou_404(request.POST.get("lista"))
    destino = reverse("interface:ocupacao", args=[edital_id, marco_id])
    try:
        request.session["resultado_da_ocupacao"] = causar_faixa_seguinte(
            actor=ator,
            processo_id=edital.processo_id,
            edital=edital,
            perfil_id=_perfil_do_marco(edital, marco_id),
            marco_id=marco_id,
            lista_id=lista_id,
            idempotency_key=request.POST.get("chave") or uuid4().hex,
            correlation_id=f"interface-faixa-{edital_id}",
        )
        request.session["acao_da_ocupacao"] = "faixa"
    except DomainError as erro:
        request.session["erro_da_ocupacao"] = erro.detail
    return redirect(destino)


@require_http_methods(["POST"])
def emitir_corte_view(request, edital_id, marco_id):
    """Constitui a faixa conferida e volta à leitura pelo padrão POST-redirect-GET."""
    ator, edital, _ = _edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    lista_id = _identidade_ou_404(request.POST.get("lista"))
    destino = reverse("interface:corte", args=[edital_id, marco_id])
    if lista_id:
        destino = f"{destino}?lista={lista_id}"
    try:
        request.session["resultado_do_corte"] = emitir_corte(
            actor=ator,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=_perfil_do_marco(edital, marco_id),
            marco_id=marco_id,
            lista_id=lista_id,
            idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
            correlation_id=getattr(request, "correlation_id", ""),
            confirmacao_do_calculo=request.POST.get("confirmacao_do_calculo", ""),
            motivo=request.POST.get("motivo", ""),
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        request.session["erro_do_corte"] = recusa.detail
    return redirect(destino)


@require_http_methods(["POST"])
def continuar_corte_view(request, edital_id, marco_id):
    """A faixa seguinte, onde a regra publicada a admite (014, FR-202)."""
    ator, edital, _ = _edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    lista_id = _identidade_ou_404(request.POST.get("lista"))
    destino = reverse("interface:corte", args=[edital_id, marco_id])
    if lista_id:
        destino = f"{destino}?lista={lista_id}"
    try:
        request.session["resultado_do_corte"] = continuar_corte(
            actor=ator,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=_perfil_do_marco(edital, marco_id),
            marco_id=marco_id,
            lista_id=lista_id,
            idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
            correlation_id=getattr(request, "correlation_id", ""),
            # O texto chega como texto, e vira recusa de domínio — nunca `ValueError` no meio do
            # comando. `abc` no campo é erro de quem preenche, e não defeito de servidor.
            quantidade=_inteiro_do_formulario(request.POST.get("quantidade")),
            motivo=request.POST.get("motivo", ""),
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        request.session["erro_do_corte"] = recusa.detail
    return redirect(destino)


@require_http_methods(["GET"])
def ato_de_ordenacao(request, edital_id, marco_id, ato_id):
    """A proveniência inteira do snapshot, pela porta de presidência ou auditoria."""
    ator, edital, _ = _edital_para_classificar(request, edital_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    ato = ato_por_id(edital=edital, marco_id=marco_id, ato_id=ato_id)
    if ato is None:
        raise Http404
    pagina = posicoes_do_ato(
        ato=ato,
        pagina=request.GET.get("pagina") or 1,
    )
    return marcar_como_privada(
        render(
            request,
            "interface/ato_ordenacao.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "ato": ato,
                # Os nomes vêm da versão que **este** ato cita, e acompanham os identificadores
                # sem os substituir: na proveniência o UUID é a âncora de auditoria, e o nome é o
                # que torna a página citável fora da máquina (E2E15-006).
                "nomes": nomes_do_ato(ato),
                # Quem abre um ato histórico precisa ler, antes dos valores, que eles já foram
                # sucedidos — sem isso dá para citar um ato superado sem perceber (E2E15-010).
                "sucessor": sucessor_de(ato),
                # O critério de desempate é nomeado pela versão que o ato cita, como tudo o mais
                # nesta tela: o snapshot guarda o enum, e a FR-050 pede a frase (E2E15-006).
                "linhas": nomear_criterios(list(pagina), ato),
                "pagina": pagina,
                # A porta da divulgação é outra — `resultado:publicar` —, e por isso o conjunto de
                # ações é calculado com o ator desta requisição, e não com a porta que abriu a
                # tela: quem consulta o ato pode não poder divulgá-lo (017, FR-069).
                "acoes": list(acoes.do_ato_de_ordenacao(ato, ator, edital=edital)),
            },
        )
    )


# ---------------------------------------------------------------------------
# A divulgação do resultado (017). Três telas: a prévia, o ato e o histórico.
#
# **A porta é outra.** A da 015 é a presidência da comissão ou a auditoria; esta é a capacidade
# `resultado:publicar`, e ela não decorre de nenhuma outra: quem emitiu o ato não ganha, por
# tê-lo emitido, o poder de divulgá-lo (FR-025, FR-026).
# ---------------------------------------------------------------------------


def _edital_para_publicar(request, edital_id, *, consulta=False):
    """A porta da divulgação: `resultado:publicar` — e `auditoria:consultar` só para consultar.

    **Sem a capacidade é 403, e não 404**, inclusive para quem preside a comissão: a recusa é sobre
    o ator, e escondê-la atrás de "não encontrado" faria a tela mentir sobre por que ela não abre.
    O 404 fica para o que o ator **não alcança** — Edital de outro escopo institucional, que ele
    não deve sequer saber que existe (FR-026).
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, None, False
    pode_publicar = ator.can("resultado:publicar")
    pode_consultar = pode_publicar or (consulta and ator.can("auditoria:consultar"))
    # **O status desta porta sempre esteve certo; o que ela não dizia era o quê** (033, `FR-481`).
    # A frase genérica de antes — *"A operação não é permitida."* — nunca mentiu, porque não
    # nomeava nada. **É ao nomear que ela passa a poder mentir**, e esta porta tem modo: com
    # `consulta` a capacidade de auditoria serve, sem ele não serve. A única porta que não
    # precisava de conserto é a que esta mudança pode quebrar, e é por isso que o conjunto vem
    # daqui, do ponto de chamada, e não de uma constante da porta (`FR-489`).
    require_authorization_base(
        pode_consultar,
        bases=(
            (BASE_DE_PUBLICAR_RESULTADO, BASE_DE_AUDITORIA)
            if consulta
            else (BASE_DE_PUBLICAR_RESULTADO,)
        ),
    )
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=ator.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None:
        raise Http404
    return ator, edital, pode_publicar


def _ato_para_publicar(edital, marco_id, ato_id):
    ato = ato_por_id(edital=edital, marco_id=marco_id, ato_id=ato_id)
    if ato is None:
        raise Http404
    return ato


@require_http_methods(["GET"])
def previa_de_publicacao(request, edital_id, marco_id, ato_id):
    """O que **seria** divulgado, composto pela mesma função que o POST usa — e nada gravado.

    Não há rascunho a persistir (D-008, FR-035): a prévia é uma leitura, e sair dela não deixa
    nada para trás. Havendo impedimento, a tela mostra a recusa nomeada e **não** oferece o botão —
    não existe publicar mediante confirmação adicional (D-001).
    """
    ator, edital, _ = _edital_para_publicar(request, edital_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    ato = _ato_para_publicar(edital, marco_id, ato_id)
    return _renderizar_previa(request, ator, edital, ato, marco_id)


def _renderizar_previa(request, ator, edital, ato, marco_id, *, erro="", status=200):
    """A prévia composta agora — usada pelo GET e pela **recusa do POST**.

    Recusado, o POST volta a esta mesma tela com o status HTTP que o domínio declarou, e não com um
    redirect. Isso importa além da fidelidade ao contrato: a assinatura e a chave de idempotência
    são **recompostas aqui**, e é exatamente disso que a autoridade precisa depois de uma recusa por
    prévia obsoleta — a projeção que ela vai reconfirmar é a de agora, não a que envelheceu.
    """
    # **A lista vem do ato, e atravessa as duas leituras** (021, D-015, FR-068). Sem ela, a prévia
    # de um ato de PPI lia a cadeia da ampla concorrência: o ato aparecia como já sucedido, ou a
    # assinatura nascia do predecessor errado — e a lista simplesmente não se publicava pela tela.
    # O teste das três listas não pegava isso porque chamava o domínio direto, já com `lista_id`.
    sucede = publicacao_vigente_do_marco(edital=edital, marco_id=marco_id, lista_id=ato.lista_id)
    try:
        # `sucede` entra na aferição porque é ele que produz o degrau do meio da FR-005: publicar
        # sobre um marco já divulgado não impede nada, e ainda assim é o que a autoridade precisa
        # ler antes de confirmar.
        publicabilidade = aferir_publicabilidade(
            edital=edital,
            marco_id=marco_id,
            ato=ato,
            sucede=sucede,
            lista_id=ato.lista_id,
            # A tela oferece a natureza num `select`, e aferia como preliminar — o padrão seguro.
            # O efeito era anunciar "nada impede esta divulgação" ao lado de uma opção que o
            # comando recusaria depois do clique. Perguntar aqui custa as consultas da
            # definitividade e **não** recalcula o estado, que é a parte cara: ele já foi lido.
            prever_a_definitiva=True,
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        raise
    projecao = compor_divulgacao(ato)
    return marcar_como_privada(
        render(
            request,
            "interface/previa_de_publicacao.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "ato": ato,
                "marco_id": marco_id,
                "cabecalho": projecao["cabecalho"],
                "posicoes": projecao["posicoes"],
                "consideradas": len(projecao["situacoes"]),
                "publicabilidade": publicabilidade,
                # Quem alcança a tela da classificação. A porta dela é outra — presidência ou
                # auditoria —, e quem só publica recebe 404 lá. Oferecer o caminho a essa pessoa
                # é oferecer um beco, e foi o que a auditoria da 017 encontrou (E2E17-002).
                "pode_ver_a_classificacao": _pode_ver_a_classificacao(ator, edital),
                "sucede": sucede,
                "naturezas": _naturezas_oferecidas(sucede),
                "autoridades": autoridades.CATALOGO,
                "confirmacao_da_previa": assinatura_da_previa(
                    ato=ato, publicacao_anterior=sucede, projecao=projecao
                ),
                # O campo da declaração só existe onde ela é exigida: onde há janela computável o
                # sistema verifica, e oferecer o campo ali ensinaria a preenchê-lo sempre (FR-086).
                "exige_declaracao": janela_declarada(edital=edital, marco_id=marco_id) is None,
                "chave_idempotencia": uuid4().hex,
                "erro": erro,
            },
            status=status,
        )
    )


def _naturezas_oferecidas(sucede):
    """As duas desde a primeira publicação; a preliminar sai depois de uma definitiva.

    Um certame pode divulgar diretamente o resultado definitivo, e condicionar `DEFINITIVA` à
    existência de uma preliminar inventaria uma etapa que o Edital não declarou. O que se retira é
    a `PRELIMINAR` depois de uma definitiva — a ordem entre naturezas tem sentido único (D-007).
    """
    if sucede is not None and sucede.natureza == Natureza.DEFINITIVA:
        return [(Natureza.DEFINITIVA.value, Natureza.DEFINITIVA.label)]
    return [(valor, rotulo) for valor, rotulo in Natureza.choices]


@require_http_methods(["POST"])
def publicar_resultado(request, edital_id, marco_id, ato_id):
    """O ato, pelo padrão POST-redirect-GET: publicado, a tela seguinte é o histórico do marco."""
    ator, edital, _ = _edital_para_publicar(request, edital_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    ato = _ato_para_publicar(edital, marco_id, ato_id)
    try:
        publicacao = publicar_resultado_do_marco(
            actor=ator,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            marco_id=marco_id,
            ato_id=ato_id,
            natureza=request.POST.get("natureza", ""),
            autoridade=request.POST.get("autoridade", ""),
            confirmacao_da_previa=request.POST.get("confirmacao_da_previa", ""),
            idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
            correlation_id=getattr(request, "correlation_id", ""),
            # A declaração expressa de encerramento do prazo, exigida só na definitiva e só onde
            # não há janela computável (FR-085, FR-086). O comando decide se ela é exigida, se é
            # recusada ou se é gravada — a tela apenas a transporta.
            declaracao_de_encerramento=request.POST.get("declaracao_de_encerramento", ""),
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        # **A recusa devolve o status que o contrato declara**, e não um 302. O ato não aconteceu,
        # e responder "redirecione-se" a um 409 esconde do cliente — pessoa, script ou proxy — que
        # nada foi gravado. A tela volta composta de novo, com a recusa nomeada e com a assinatura
        # recalculada, que é o que a autoridade precisa para reconfirmar.
        return _renderizar_previa(
            request, ator, edital, ato, marco_id, erro=recusa.detail, status=recusa.status
        )
    request.session["resultado_da_publicacao"] = str(publicacao.id)
    return redirect(reverse("interface:publicacoes-do-marco", args=[edital_id, marco_id]))


@require_http_methods(["GET"])
def publicacoes_do_marco(request, edital_id, marco_id):
    """O que foi divulgado, quando, por quem — e o que vale hoje (FR-068).

    **Consultar é de dois; publicar é de um.** A auditoria lê esta página inteira e não age nela, e
    é por isso que a ação de publicar depende da capacidade que a rota de consulta não exige.
    """
    ator, edital, _ = _edital_para_publicar(request, edital_id, consulta=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    return marcar_como_privada(
        render(
            request,
            "interface/publicacoes_do_marco.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "marco_id": marco_id,
                "historico": historico_das_publicacoes(edital=edital, marco_id=marco_id),
                # Os dois caminhos para as telas da 015 — o **ato de origem** e a **classificação
                # do marco** — condicionados à autorização de quem lê: elas têm porta própria, e
                # oferecê-las a quem receberia 404 seria oferecer um beco (FR-022).
                #
                # O da classificação era condicionado a `pode_publicar`, invocando a FR-069:
                # publicar é de um, consultar é de dois. Mas a FR-069 governa a **ação** de
                # publicar, e este link não é ação — é navegação para uma tela de leitura, cuja
                # porta é a da presidência e da auditoria. Sob a capacidade errada, ele aparecia
                # exatamente para quem cairia no 404 e sumia para quem podia lê-la (E2E17-002).
                # A ação de publicar não vive nesta página: ela é do ato, e a porta dela continua
                # sendo `resultado:publicar`.
                "pode_ver_o_ato": _pode_ver_a_classificacao(ator, edital),
                "publicada_agora": request.session.pop("resultado_da_publicacao", None),
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


def _pode_auditar_a_etapa(ator, edital):
    """A porta das telas de Etapa: presidência **ou** auditoria (FR-091).

    Separada de `_etapa_para_auditar` porque a tela do recurso precisa **oferecer ou não** o
    caminho antes de alguém batê-lo: link para porta fechada responde 404, e 404 não explica nada
    a quem o recebe.
    """
    return pode_gerir_comissao(ator, edital.processo) is not None or ator.can("auditoria:consultar")


def _etapa_para_auditar(request, edital_id, etapa_id):
    """A porta da consulta: presidência **ou** auditoria — nunca as duas ao mesmo tempo (FR-091).

    Exigir a conjunção reduzia a trilha ao usuário híbrido: quem preside sem o papel de auditor
    lia 403, e quem audita sem gerir o Processo lia 404. Quem responde a um recurso é um dos dois,
    e quase nunca é os dois — o que a spec concede a cada um, a porta negava a ambos.

    **A recusa deixou de ser 404 para as duas** (033, `FR-478`). O que ela protegia — não revelar
    a existência do que o ator não alcança — continua protegido, e por outro mecanismo: a consulta
    abaixo filtra por `institution_scope`, de modo que Edital de outra unidade é indistinguível de
    Edital inexistente (`FR-487`). O que o 404 fazia **a mais** era esconder do ator do mesmo
    escopo a razão de a tela não abrir, e essa parte era ruído, não proteção.
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
    require_authorization_base(
        _pode_auditar_a_etapa(ator, edital), bases=BASES_DA_GESTAO_OU_AUDITORIA
    )
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
        # **O conteúdo publicado inteiro**, e não só a coleção de Etapas: é o que aquele wrapper
        # leria por dentro, a Mesa precisa das Etapas para resolver a progressão, e a condição do
        # corte da `014` precisa dos marcos que governam esta Etapa. Ler uma vez e repassar mantém
        # o custo onde estava — o orçamento de consulta desta tela é testado (013, FR-006).
        conteudo_da_mesa = conteudo_vigente(edital)
        vigentes = {UUID(str(item["id"])): item for item in conteudo_da_mesa.get("stages") or []}
    except DomainError:
        conteudo_da_mesa, vigentes = {}, {}
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
            conteudo=conteudo_da_mesa,
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


# ---------------------------------------------------------------------------
# Os recursos (018). Julgar é ato de autoridade **própria**: a capacidade `recurso:julgar` não
# deriva de presidir a comissão, de avaliar, de consolidar, de emitir nem de publicar — e é por
# isso que estas views não passam por `comando_de_comissao` (D-005, T-005, FR-037).
# ---------------------------------------------------------------------------


@require_http_methods(["GET"])
def recursos_do_edital(request, edital_id):
    """Os recursos recebidos, para escolher qual abrir.

    **Sem consulta de impedimento por linha** (T-006): a lista mostra recursos que o ator talvez
    não possa julgar, e quem nomeia o impedimento é a tela da peça. A fundamentação também não vem
    — ela é conteúdo do juízo, e a lista serve para escolher.
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404
    require_permission(ator, recursos_admitir.PERMISSAO)

    situacao = request.GET.get("situacao", "")
    return render(
        request,
        "interface/recursos.html",
        {
            "edital": edital,
            "recursos": recursos_selectors.recursos_do_edital(edital, situacao=situacao),
            "situacao": situacao,
            "situacoes": sorted(recursos_selectors.SITUACOES.items()),
        },
    )


def _peca_para_julgar(request, recurso_id):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, None
    peca = (
        Recurso.objects.filter(pk=recurso_id)
        .select_related(
            "inscricao",
            "inscricao__edital",
            # O Processo entra no `select_related` porque a tela pergunta pela presidência dele
            # para decidir quais caminhos oferecer: sem esta linha, a pergunta custaria uma
            # consulta a mais por leitura da peça.
            "inscricao__edital__processo",
            "versao",
            "resultado_atacado",
            "resultado_atacado__avaliacao",
            "publicacao_atacada",
            "publicacao_atacada__ato",
        )
        .prefetch_related("juizos", "decisoes")
        .first()
    )
    if peca is None or peca.inscricao.edital.institution_scope != ator.institution_scope:
        raise Http404
    require_permission(ator, recursos_admitir.PERMISSAO)
    return ator, peca


@require_http_methods(["GET"])
def recurso_recebido(request, recurso_id):
    """A peça, com a proveniência da FR-092 e o impedimento **antes de qualquer botão**.

    Nomear o impedimento depois do clique faria a pessoa escrever a motivação inteira para só
    então descobrir que não podia decidir (FR-042).
    """
    ator, peca = _peca_para_julgar(request, recurso_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))

    razao = impedimento(ator, peca)
    # **A resposta carrega a fundamentação e o protocolo de quem recorreu**, e por isso não fica no
    # cache do navegador: é o mesmo cuidado que a 013 aplicou às telas de Resultado, e a mesma razão
    # — computador compartilhado, e o botão "voltar" de quem já saiu (FR-105).
    return marcar_como_privada(
        render(
            request,
            "interface/recurso.html",
            {
                "edital": peca.inscricao.edital,
                "peca": peca,
                "resumo": recursos_selectors.resumo(peca),
                "proveniencia": recursos_selectors.proveniencia(peca),
                "impedimento": RAZOES.get(razao, ""),
                "pode_decidir": razao is None,
                "assinatura": recursos_selectors.assinatura_do_estado_da_peca(peca),
                **_alvo_da_correcao(peca),
                **_para_conferir_o_objeto(ator, peca),
            },
        )
    )


def _alvo_da_correcao(peca):
    """As Etapas que a decisão pode alcançar, e a forma que cada uma exige.

    **O objeto atacado e o lugar do erro são eixos distintos** (D-001). Um recurso contra a
    publicação cujo mérito é *"minha nota da Etapa 2 está errada"* corrige o `ResultadoEtapa` da
    Etapa 2 — e enquanto esta função só olhava para `resultado_atacado`, esse recurso chegava à tela
    sem alvo, e o formulário escondia as espécies `CORRECAO_FIXADA` e `REAVALIACAO_DETERMINADA`.
    Quem recorreu da divulgação por causa da própria nota não tinha, pelo canal real, como obter a
    correção que a decisão institucional prometeu.

    No ramo do Resultado há **uma** Etapa alcançável, e ela já vem escolhida. No ramo da publicação
    há as que o marco enumera, e o julgador escolhe: são elas que o ato divulgado ordena, e nenhuma
    outra.

    A tela pede **pontuação ou sentido conforme a forma que a Etapa publica**, e nunca as duas: um
    formulário que oferecesse os dois campos convidaria a preencher o errado, e a decisão nasceria
    incoerente com a própria norma que cita.
    """
    from processo_seletivo.recursos.domain.consequencia import etapa_publicada
    from processo_seletivo.resultados.models import ResultadoEtapa

    alcancaveis, etapas_do_objeto = [], []
    for etapa_id in _etapas_alcancaveis(peca):
        etapa = etapa_publicada(peca.versao, etapa_id) or {}
        # **A leitura é mais larga que a correção**, e por isso esta lista é montada antes do
        # `continue` abaixo: a Etapa sem Resultado vigente não pode ser corrigida, mas continua
        # sendo o que se contesta — e é justamente ela que quem julga precisa abrir para entender
        # por que não há vigente. Nenhuma consulta nova: o nome sai do conteúdo já carregado.
        nome = etapa.get("name") or str(etapa_id)
        etapas_do_objeto.append({"etapa_id": str(etapa_id), "nome": nome})
        vigente = ResultadoEtapa.vigentes.filter(
            inscricao_id=peca.inscricao_id, etapa_id=etapa_id
        ).first()
        if vigente is None:
            # Sem Resultado vigente não há o que corrigir naquela Etapa — e oferecê-la levaria a
            # uma recusa que a tela poderia ter evitado (FR-013).
            continue
        alcancaveis.append(
            {
                "resultado": vigente,
                "etapa_id": str(etapa_id),
                "nome": nome,
                # Vazia no ramo da Ocorrência: ali não há grandeza a fixar, e a decisão declara a
                # consequência diretamente (FR-059).
                "forma": "" if vigente.forma == "" else forma_publicada(etapa),
                "sentidos": rotulos(etapa),
            }
        )
    return {"alcancaveis": alcancaveis, "etapas_do_objeto": etapas_do_objeto}


def _para_conferir_o_objeto(ator, peca):
    """Quais caminhos até o objeto atacado esta pessoa pode abrir.

    **A tela do recurso tinha três links, e os três eram a migalha de navegação.** Quem julga
    abria a peça e não alcançava a nota atacada, a avaliação que a produziu nem os documentos que
    o candidato entregou: cada um exigia procurar por fora, num fluxo que corre contra prazo.

    A oferta é a **mesma decisão que a view de destino toma** — a porta da Etapa é presidência ou
    auditoria (FR-091), e a dos documentos é `inscricao:consultar` (FR-072). Oferecer o que a
    outra tela recusaria devolveria 404, e 404 não explica nada a quem o recebe.

    Nenhuma consulta nova: as duas bases já estão nos vínculos lidos, e as Etapas vêm do conteúdo
    que `_alvo_da_correcao` já resolveu.
    """
    return {
        "pode_auditar_a_etapa": _pode_auditar_a_etapa(ator, peca.inscricao.edital),
        "pode_ver_a_inscricao": ator.can(CONSULTAR),
    }


def _etapas_alcancaveis(peca):
    """As identidades de Etapa que o remédio pode alcançar, na versão que a peça cita.

    Contra o Resultado, a Etapa dele. Contra a publicação, as que o **marco daquela publicação**
    enumera: o ato divulgado ordena aquelas, e alcançar outras seria a decisão saindo do que se
    contestou.
    """
    if peca.resultado_atacado_id is not None:
        return [peca.resultado_atacado.etapa_id]
    publicacao = peca.publicacao_atacada
    if publicacao is None:
        return []
    for perfil in peca.versao.content.get("profiles") or []:
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) == str(publicacao.marco_id):
                return [item for item in marco.get("stages") or []]
    return []


@require_http_methods(["POST"])
def admitir_recurso(request, recurso_id):
    ator, peca = _peca_para_julgar(request, recurso_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))

    try:
        recursos_admitir.admitir(
            actor=ator,
            recurso_id=peca.id,
            admitido=request.POST.get("admitido") == "sim",
            motivo=request.POST.get("motivo", ""),
            assinatura_do_estado=request.POST.get("assinatura", ""),
            idempotency_key=f"admitir-{peca.id}",
            correlation_id=str(peca.id),
        )
    except DomainError as recusa:
        if recusa.status == 403 and recusa.code == "forbidden":
            raise
        return _recurso_com_recusa(request, ator, peca, recusa)
    return redirect(reverse("interface:recurso", args=[peca.id]))


def _recurso_com_recusa(request, ator, peca, recusa):
    """A recusa volta **na própria tela da peça**, e não numa página de erro.

    Quem escreveu a motivação precisa lê-la de volta junto da razão da recusa; mandá-la para uma
    página de erro obrigaria a escrever tudo de novo.
    """
    peca.refresh_from_db()
    razao = impedimento(ator, peca)
    resposta = marcar_como_privada(
        render(
            request,
            "interface/recurso.html",
            {
                "edital": peca.inscricao.edital,
                "peca": peca,
                "resumo": recursos_selectors.resumo(peca),
                "proveniencia": recursos_selectors.proveniencia(peca),
                "impedimento": RAZOES.get(razao, ""),
                "pode_decidir": razao is None,
                "assinatura": recursos_selectors.assinatura_do_estado_da_peca(peca),
                "erro": recusa.detail,
                "motivo": request.POST.get("motivo", ""),
                "motivacao": request.POST.get("motivacao", ""),
                **_alvo_da_correcao(peca),
                **_para_conferir_o_objeto(ator, peca),
            },
            status=recusa.status,
        )
    )
    return resposta


def _pontuacao_digitada(bruto):
    """O que a pessoa escreveu, com a vírgula traduzida — e `None` quando ela não escreveu nada.

    Não valida: o que não for número segue para o domínio, que recusa com motivo. Validar aqui
    duplicaria a regra e deixaria a recusa dependente da porta por onde o pedido entrou.
    """
    texto = (bruto or "").strip()
    return texto.replace(",", ".") if texto else None


@require_http_methods(["POST"])
def julgar_recurso(request, recurso_id):
    """A decisão de mérito, nas quatro espécies.

    A consequência **não** vem do formulário: o julgador fixa a conclusão, e a regra publicada da
    Etapa diz o que ela produz (FR-059). Um campo `consequencia` aqui permitiria declarar
    `HABILITADA` com nota abaixo da mínima.
    """
    ator, peca = _peca_para_julgar(request, recurso_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))

    # A opção carrega `etapa|resultado`: a Etapa que a decisão alcança e a assinatura do Resultado
    # vigente que a tela leu para ela. Separá-los em dois campos deixaria a assinatura descolar da
    # Etapa quando o julgador trocasse a escolha.
    etapa_id, _, assinatura = request.POST.get("etapa", "").partition("|")
    try:
        recursos_julgar.julgar(
            actor=ator,
            recurso_id=peca.id,
            especie=request.POST.get("especie", ""),
            motivacao=request.POST.get("motivacao", ""),
            etapa_id=etapa_id or None,
            # A vírgula é o separador decimal do país, e é o que estas telas imprimem — "8,5000",
            # "26,00". Passá-la adiante como veio derrubava o julgamento em `InvalidOperation`:
            # traduzi-la aqui é trabalho de apresentação, e o domínio segue recebendo número.
            pontuacao=_pontuacao_digitada(request.POST.get(f"pontuacao-{etapa_id}")),
            sentido=request.POST.get(f"sentido-{etapa_id}", ""),
            assinatura_do_resultado=assinatura,
            idempotency_key=f"julgar-{peca.id}",
            correlation_id=str(peca.id),
        )
    except DomainError as recusa:
        if recusa.status == 403 and recusa.code == "forbidden":
            raise
        return _recurso_com_recusa(request, ator, peca, recusa)
    return redirect(reverse("interface:recurso", args=[peca.id]))


# ---------------------------------------------------------------------------
# 021 — o sorteio público auditável
# ---------------------------------------------------------------------------


@require_http_methods(["GET"])
def sorteio(request, edital_id, marco_id):
    """O estado de cada recorte do marco, e o que falta em cada um (021, FR-062).

    **Não calcula ordem nenhuma**, e a ausência é a regra: depois de a semente ser conhecida, uma
    prévia da ordem seria o ensaio que a D-010 existe para impedir; antes dela não há o que
    calcular. O que esta tela mostra é o **universo** — quem entra, com que número — e o estado do
    compromisso.

    Um marco de sorteio com cotas tem três recortes, e cada um tem a sua relação, a sua ocorrência
    e o seu ato. Listá-los juntos é o que evita que alguém publique dois e esqueça o terceiro.
    """
    from processo_seletivo.sorteios.application.previa import recortes_do_marco

    ator, edital, pode_emitir = _edital_para_classificar(request, edital_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    perfil_id = _perfil_do_marco(edital, marco_id)
    try:
        estado = recortes_do_marco(edital=edital, perfil_id=perfil_id, marco_id=marco_id)
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        raise
    return marcar_como_privada(
        render(
            request,
            "interface/sorteio.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "perfil": estado["perfil"],
                "marco": estado["marco"],
                # Lido do Edital publicado e **exibido sem campo de edição**: quem conduz o sorteio
                # não declara o método, e alterá-lo é Retificação (D-013, FR-014).
                "metodo": estado["metodo"],
                # **Quem pode retificar vê o caminho; quem não pode, vê o encaminhamento** (026).
                #
                # A frase "alterá-lo é uma Retificação" fala a toda pessoa que abre esta tela — e
                # a presidência da comissão, que é quem mais a abre, não tem `retificacao:elaborar`.
                # Um link para ela terminaria numa tela que se anuncia somente leitura: trocar o
                # beco sem saída por um beco sinalizado não é ganho.
                "pode_retificar": ator.can("retificacao:elaborar"),
                "metodo_hash": estado["metodo_hash"],
                # A ocorrência da vez — a declarada, ou a que a regra de substituição pôs no
                # lugar dela —, é o que põe a semente à vista **antes** do ato, que é o que a
                # transmissão precisa mostrar.
                "ocorrencia": estado["ocorrencia"],
                # A referência que ainda falta observar, derivada pela regra publicada. É ela que a
                # tela nomeia no botão: quem observa precisa saber o que vai buscar, e não há campo
                # para trocá-la (FR-015, FR-017).
                "proxima_referencia": estado["proxima_referencia"],
                # E as que a indisponibilidade descartou, visíveis de propósito: o descarte de
                # ocorrência é justamente o que precisa ser auditável (R-006).
                "ocorrencias_descartadas": estado["ocorrencias_descartadas"],
                "ocorre_em": estado["ocorre_em"],
                # **Com o estado do corte de cada um** (014, UX-029). Esta é a tela que já reúne
                # os recortes do marco; sem o corte aqui, enxergar o estado das três listas exigia
                # uma visita por lista — e num certame com cotas é justamente onde o esforço se
                # multiplica.
                "recortes": _com_o_corte(edital, estado["marco"], estado["recortes"]),
                "pode_emitir": pode_emitir,
                # **Quem publica o resultado não é necessariamente quem conduz o sorteio**
                # (`017`, FR-025): a capacidade é própria, e oferecer o caminho a quem receberia
                # 403 seria oferecer um beco. Com ela, o passo seguinte fica **na tela em que o
                # sorteio terminou**, em vez de exigir que alguém reconstrua a navegação por cinco
                # telas com a transmissão no ar.
                "pode_publicar": ator.can("resultado:publicar"),
                "resultado": request.session.pop("resultado_do_sorteio", None),
                "erro": request.session.pop("erro_do_sorteio", None),
                # **A chave de idempotência nasce na leitura, e viaja no formulário** — como a tela
                # da `015` já fazia. Sem ela, cada envio gerava chave nova: o duplo clique no botão
                # de sortear não era reconhecido como repetição, batia em `draw_already_constituted`
                # e pintava a tela de vermelho **depois** de o sorteio ter dado certo, ao vivo. Com
                # ela, o segundo envio devolve o desfecho do primeiro.
                "chave_idempotencia": uuid4().hex,
            },
        )
    )


# Os quatro comandos da tela do sorteio, nomeados. **O desfecho de cada um é dele**, e a faixa que
# a tela mostra tem de dizer o que aconteceu — não o que aconteceria se o comando fosse outro
# (`021`, FR-062).
#
# Antes havia uma frase só, escrita para a publicação da relação, e ela respondia aos quatro: depois
# de observar a extração a tela anunciava *"Relação publicada e congelada, com  participante"*, e
# depois de **realizar o sorteio** anunciava *"Relação publicada e congelada, com 327
# participantes"* — no minuto mais visto do certame, com a transmissão aberta. A recusa tinha o
# mesmo vício, e prefixava *"Não foi possível publicar"* uma falha da fonte externa.
RELACAO, OCORRENCIA, SORTEIO, ANULACAO = "relacao", "ocorrencia", "sorteio", "anulacao"


def _desfecho_do_sorteio(request, tipo, declarado):
    request.session["resultado_do_sorteio"] = {"tipo": tipo, **(declarado or {})}


def _recusa_do_sorteio(request, tipo, recusa):
    request.session["erro_do_sorteio"] = {"tipo": tipo, "detalhe": recusa.detail}


@require_http_methods(["POST"])
def publicar_relacao_do_sorteio(request, edital_id, marco_id):
    """Publica — que é congelar — a relação de um recorte, e volta pela leitura (FR-001)."""
    from processo_seletivo.sorteios.application.relacao import publicar_relacao

    ator, edital, _ = _edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    destino = reverse("interface:sorteio", args=[edital_id, marco_id])
    lista_id = request.POST.get("lista_id") or None
    try:
        _desfecho_do_sorteio(
            request,
            RELACAO,
            publicar_relacao(
                actor=ator,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                perfil_id=_perfil_do_marco(edital, marco_id),
                marco_id=marco_id,
                lista_id=lista_id,
                idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
                correlation_id=getattr(request, "correlation_id", ""),
                motivo=request.POST.get("motivo", ""),
            ),
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        _recusa_do_sorteio(request, RELACAO, recusa)
    return redirect(destino)


@require_http_methods(["POST"])
def observar_ocorrencia_do_sorteio(request, edital_id, marco_id):
    """Busca a ocorrência declarada na fonte e a registra. **Não sorteia** (021, R-006).

    **A fonte e a ocorrência vêm do método publicado, e o formulário não as recebe.** O que a tela
    envia é a intenção de observar, e nunca *qual* ocorrência observar: escolher a extração no dia
    do sorteio seria a mesma fresta que escolher a semente. O Edital nomeia o concurso antes do
    congelamento, e `derivation` publica como ele foi escolhido a partir da data programada
    (FR-013, FR-017).
    """
    from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
    from processo_seletivo.sorteios.application.previa import recortes_do_marco

    ator, edital, _ = _edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    destino = reverse("interface:sorteio", args=[edital_id, marco_id])
    estado = recortes_do_marco(
        edital=edital, perfil_id=_perfil_do_marco(edital, marco_id), marco_id=marco_id
    )
    metodo = estado["metodo"] or {}
    # **A referência da vez, derivada pela regra publicada** — e não a declarada no Edital
    # (FR-015). Registrada uma indisponibilidade, é a regra que diz qual ocorrência a substitui, e
    # observar sempre a declarada travava o certame para sempre na primeira extração não publicada.
    referencia = estado["proxima_referencia"]
    if not referencia:
        request.session["erro_do_sorteio"] = {
            "tipo": OCORRENCIA,
            "detalhe": (
                "A ocorrência declarada e todas as substitutas previstas pela regra publicada "
                "estão indisponíveis. Prosseguir exige Retificação que declare outro método."
            ),
        }
        return redirect(destino)
    try:
        _desfecho_do_sorteio(
            request,
            OCORRENCIA,
            observar_ocorrencia(
                actor=ator,
                processo_id=edital.processo_id,
                fonte=metodo.get("source", ""),
                referencia=referencia,
                idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
                correlation_id=getattr(request, "correlation_id", ""),
                # O instante publicado da ocorrência: antes dele, a ausência não é definitiva.
                ocorre_em=estado["ocorre_em"],
            ),
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        _recusa_do_sorteio(request, OCORRENCIA, recusa)
    return redirect(destino)


@require_http_methods(["POST"])
def realizar_sorteio(request, edital_id, marco_id):
    """Um botão só. Calcula a ordem e constitui o ato, numa transação (FR-029).

    **Não há prévia, e não há confirmação de cálculo.** O fluxo da `015` — calcular, conferir
    assinatura, confirmar, emitir — admite calcular várias vezes antes de decidir emitir, e isso,
    depois da semente, é o ensaio que a D-010 existe para impedir.
    """
    from processo_seletivo.sorteios.application.sorteio import constituir_sorteio

    ator, edital, _ = _edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    destino = reverse("interface:sorteio", args=[edital_id, marco_id])
    try:
        _desfecho_do_sorteio(
            request,
            SORTEIO,
            constituir_sorteio(
                actor=ator,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                relacao_id=request.POST.get("relacao_id"),
                ocorrencia_id=request.POST.get("ocorrencia_id"),
                idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
                correlation_id=getattr(request, "correlation_id", ""),
            ),
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        _recusa_do_sorteio(request, SORTEIO, recusa)
    return redirect(destino)


@require_http_methods(["POST"])
def anular_o_sorteio(request, edital_id, marco_id):
    """Anular **é** constituir o sucessor, com motivo obrigatório (FR-052, FR-053)."""
    from processo_seletivo.sorteios.application.sorteio import anular_sorteio

    ator, edital, _ = _edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    destino = reverse("interface:sorteio", args=[edital_id, marco_id])
    try:
        _desfecho_do_sorteio(
            request,
            ANULACAO,
            anular_sorteio(
                actor=ator,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                sorteio_anterior_id=request.POST.get("sorteio_anterior_id"),
                relacao_id=request.POST.get("relacao_id"),
                ocorrencia_id=request.POST.get("ocorrencia_id"),
                motivo=request.POST.get("motivo", ""),
                idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
                correlation_id=getattr(request, "correlation_id", ""),
            ),
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        _recusa_do_sorteio(request, ANULACAO, recusa)
    return redirect(destino)
