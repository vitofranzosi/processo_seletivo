"""As portas do kit de divulgação do Edital: ler a tela e exportar o material (111).

**A porta** (`FR-3402`, contrato em `specs/111-kit-de-divulgacao/contracts/kit.md`):

1. Edital inexistente ou de outra unidade responde "não encontrado" (`033`);
2. quem é da unidade sem `material:gerar` recebe a recusa que diz o que falta;
3. Edital ainda não publicado responde 409, como o relatório do Edital (`099`).

Encerrado e cancelado passam: a tela diz o motivo e, se houve exportação, que ela não deve mais
circular (`FR-3445`).

**Exportar é o que registra, e abrir não** (`FR-3435`). O material sai do sistema numa exportação, e
a trilha precisa dizer quem o levou, sobre qual versão e com qual impressão. A desatualização
compara a ficha de agora com essas exportações (`FR-3439`). Abrir a tela e copiar um texto não
registram (P-5).

**A impressão conferida viaja da tela à exportação** (`FR-3446`, `D-019`). São duas requisições, e
na passagem de uma vigência a pessoa conferiria um Edital e baixaria outro.

**A peça é a mesma composição na prévia e na exportação** (`D-014`). A prévia é um `<img>` que
pede o PNG por GET, com a impressão conferida, e não registra; a exportação é o POST que registra.
O SVG sai só como anexo, com uma política própria que admite só a fonte e a marca embutidas
(`D-021`): a do projeto só se aplica a `text/html`. Com a chave desligada, em host local, sem
material ou com a peça recusada, a prévia e a exportação da peça respondem 404 — o motivo é dito na
tela (contrato).

**Nada aqui toca a publicação** (`FR-3405`): a única escrita é o evento da trilha.
"""

import hashlib

from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface import identidade, kit_familias, kit_pacote, kit_peca, kit_textos
from processo_seletivo.interface.kit_familias import institucional
from processo_seletivo.portal import ficha as fichas
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.application.authorization import (
    base_de_permissao,
    require_authorization_base,
)
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import host_local, marcar_como_privada

PERMISSAO = "material:gerar"
OPERACAO = "EXPORTAR_MATERIAL"
BASE = base_de_permissao("gerar o material de divulgação")

#: Os estados em que o kit abre. Antes da publicação não há o que divulgar; encerrado e cancelado
#: abrem para dizer que o material exportado não deve mais circular.
ESTADOS_COM_KIT = frozenset(
    {Edital.Status.PUBLICADO, Edital.Status.ENCERRADO, Edital.Status.CANCELADO}
)
INDISPONIVEL = "O kit de divulgação fica disponível quando o Edital for publicado."
MUDOU = (
    "O Edital mudou desde que você abriu o kit. Abra o kit de novo e confira as informações "
    "antes de exportar."
)

PECA_EM_VALIDACAO = (
    "A peça visual está em validação pela comunicação e não está disponível neste ambiente. Os "
    "textos continuam disponíveis."
)
SEM_RASTERIZADOR = (
    "O rasterizador da peça não está instalado neste ambiente: a peça sai só em SVG. Os textos "
    "continuam disponíveis."
)
MANCHETE_INVALIDA = "A manchete escolhida não está entre as oferecidas. Abra o kit de novo."

TEXTOS = {
    "md": ("text/markdown; charset=utf-8", "md"),
    "txt": ("text/plain; charset=utf-8", "txt"),
}
PECAS = {
    "png": ("image/png", "png"),
    "svg": ("image/svg+xml", "svg"),
}
#: O pacote (incremento C): sai também sem a peça, e diz por quê (EC-21).
PACOTE = {"zip": ("application/zip", "zip")}
FORMATOS = {**TEXTOS, **PECAS, **PACOTE}
#: A política do anexo SVG (FR-3442, `D-014`, `D-021`): nada de fora, nenhum script; só o estilo
#: que declara a fonte, a fonte em `data:` e a marca em `data:`.
POLITICA_DO_SVG = "default-src 'none'; style-src 'unsafe-inline'; font-src data:; img-src data:"


def _edital_do_kit(request, edital_id):
    """Ator e Edital, na ordem da porta. `(None, None)` pede identificação."""
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
    require_authorization_base(ator.can(PERMISSAO), bases=[BASE])
    if edital.status not in ESTADOS_COM_KIT:
        raise DomainError("kit_indisponivel", INDISPONIVEL, 409)
    return ator, edital


def _base_url(request):
    """O endereço público da requisição, ou nenhum em host local (`FR-3447`, `D-020`)."""
    if host_local(request):
        return None
    return request.build_absolute_uri("/").rstrip("/")


def _indice_da_manchete(dados):
    """O índice pedido, ou `None`. Texto que não é índice tem a recusa do índice fora da lista."""
    bruto = dados.get("manchete", "")
    if bruto == "":
        return None
    try:
        return int(bruto)
    except ValueError:
        raise DomainError("kit_manchete_invalida", MANCHETE_INVALIDA, 422) from None


def _motivo_da_institucional():
    """A Institucional também passa pela liberação (119, FR-3835): `liberados()` decide.

    A versão 1 com o resumo congelado continua da chave da `111`; qualquer outra versão, ou outro
    resumo, só sai pela configuração nova, que a nomeia — a chave da `111` não a alcança. Sem isto,
    a versão 2 da Institucional com o resumo congelado atualizado sairia só pela chave antiga.
    """
    if institucional.POST in kit_familias.liberados():
        return ""
    if kit_familias.institucional_v1(institucional.POST):
        return PECA_EM_VALIDACAO
    return kit_familias.VERSAO_EM_APROVACAO


def _motivo_sem_peca(request):
    """Por que a peça não existe neste acesso, antes de compor: não liberada ou host local."""
    motivo = _motivo_da_institucional()
    if motivo:
        return motivo
    if host_local(request):
        return kit_peca.HOST_LOCAL
    return ""


def _compor(ficha, indice):
    """A peça, ou `DomainError` 422 para manchete fora da lista."""
    try:
        return kit_peca.compor(ficha, manchete=indice)
    except kit_peca.MancheteInvalida:
        raise DomainError("kit_manchete_invalida", MANCHETE_INVALIDA, 422) from None


def _secao_da_peca(request, ficha, indice):
    """O que a tela mostra da peça: a peça, as manchetes oferecidas e o motivo quando não há."""
    motivo = _motivo_sem_peca(request)
    if motivo or not ficha.tem_material:
        return {"peca": None, "motivo": motivo, "manchetes": ()}
    try:
        peca = _compor(ficha, indice)
    except kit_peca.PecaRecusada as recusa:
        return {"peca": None, "motivo": recusa.motivo, "manchetes": ()}
    return {
        "peca": peca,
        "motivo": "" if kit_pacote.disponivel() else SEM_RASTERIZADOR,
        "png": kit_pacote.disponivel(),
        "manchetes": kit_peca.manchetes(ficha),
        "manchete": indice,
    }


def exportacoes(edital):
    """A exportação mais recente de cada impressão registrada, da mais nova à mais antiga (`D-005`).

    **O leve primeiro.** A faixa compara por impressão (`FR-3439`), e de cada impressão só a mais
    recente conta. Ler o `detalhe` inteiro de todos os eventos — com os campos de todos os Perfis —
    custaria cada vez mais a cada exportação; lê-se o instante e a impressão de todos, e o `detalhe`
    completo só de um evento por impressão, que são tantas quantas as versões do material.
    """
    base = RegistroAuditoria.objects.filter(
        aggregate_type="Edital", aggregate_id=edital.pk, operation=OPERACAO
    )
    escolhidos, vistas = [], set()
    for identificador, impressao in base.order_by("-occurred_at").values_list(
        "pk", "detalhe__impressao"
    ):
        if impressao not in vistas:
            vistas.add(impressao)
            escolhidos.append(identificador)
    detalhes = {
        identificador: (quando, detalhe)
        for identificador, quando, detalhe in base.filter(pk__in=escolhidos).values_list(
            "pk", "occurred_at", "detalhe"
        )
    }
    return [
        {
            **(detalhes[i][1] or {}),
            "exportado_em": fichas.instante_por_extenso(detalhes[i][0]),
        }
        for i in escolhidos
    ]


def _material(ficha):
    textos = kit_textos.compor(ficha)
    notas = kit_textos.notas_para_quem_divulga(ficha)
    return textos, notas


@require_http_methods(["GET"])
def kit(request, edital_id):
    """A tela única do kit (`FR-3443`): conferência, textos, faixas e exportações."""
    ator, edital = _edital_do_kit(request, edital_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    ficha = fichas.ler(edital, agora=timezone.now(), base_url=_base_url(request))
    indice = _indice_da_manchete(request.GET)
    textos, notas = _material(ficha)
    anteriores = exportacoes(edital)
    desatualizadas, mais = fichas.desatualizacoes(anteriores, ficha)
    return marcar_como_privada(
        render(
            request,
            "interface/kit_de_divulgacao.html",
            {
                "edital": edital,
                "processo": edital.processo,
                "ficha": ficha,
                "conferencia": kit_textos.conferencia(ficha),
                "textos": [
                    (chave, kit_textos.TITULOS[chave], textos[chave])
                    for chave in kit_textos.TITULOS
                    if chave in textos
                ],
                "notas": notas,
                "desatualizadas": desatualizadas,
                "mais_desatualizadas": mais,
                # O desfecho depois de uma exportação: o material não deve mais circular (FR-3445).
                "exportado_sem_material": (not ficha.tem_material) and bool(anteriores),
                "ultima_exportacao": anteriores[0]["exportado_em"] if anteriores else "",
                "formatos": list(TEXTOS),
                "formatos_da_peca": list(PECAS),
                "formato_do_pacote": next(iter(PACOTE)),
                "secao_da_peca": _secao_da_peca(request, ficha, indice),
            },
        )
    )


@require_http_methods(["GET"])
def previa(request, edital_id):
    """O PNG da peça para a tela, com a impressão conferida, sem registro (`D-014`, FR-3446)."""
    ator, edital = _edital_do_kit(request, edital_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    if _motivo_sem_peca(request) or not kit_pacote.disponivel():
        raise Http404
    indice = _indice_da_manchete(request.GET)
    ficha = fichas.ler(edital, agora=timezone.now(), base_url=_base_url(request))
    if not ficha.tem_material:
        raise Http404
    if request.GET.get("impressao", "") != ficha.impressao:
        raise DomainError("kit_desatualizado", MUDOU, 409)
    try:
        peca = _compor(ficha, indice)
    except kit_peca.PecaRecusada:
        raise Http404 from None
    resposta = HttpResponse(
        kit_pacote.rasterizar(kit_peca.svg(peca, ficha), kit_peca.fontes_da_peca(peca)), "image/png"
    )
    resposta["Content-Disposition"] = "inline"
    resposta["X-Content-Type-Options"] = "nosniff"
    return marcar_como_privada(resposta)


def _arquivo_da_peca(ficha, peca, formato):
    if formato == "svg":
        return kit_peca.svg(peca, ficha, fonte_embutida=True).encode()
    return kit_pacote.rasterizar(kit_peca.svg(peca, ficha), kit_peca.fontes_da_peca(peca))


def pacote(ficha, *, manchete, motivo_sem_peca):
    """O ZIP do material, a peça que entrou e o motivo de ela faltar (`FR-3435`, EC-21).

    **A recusa da peça não recusa o pacote** (contrato): a composição que não cabe sai do ZIP com o
    motivo nomeado no manifesto, e os textos seguem. Manchete fora da lista continua 422 — é pedido
    inválido, e não peça que não cabe.
    """
    peca, motivo = None, motivo_sem_peca
    if not motivo:
        try:
            peca = _compor(ficha, manchete)
        except kit_peca.PecaRecusada as recusa:
            motivo = recusa.motivo
    png = svg = None
    if peca is not None:
        svg = kit_peca.svg(peca, ficha, fonte_embutida=True).encode()
        if kit_pacote.disponivel():
            png = kit_pacote.rasterizar(kit_peca.svg(peca, ficha), kit_peca.fontes_da_peca(peca))
        else:
            motivo = SEM_RASTERIZADOR
    textos, notas = _material(ficha)
    dados = kit_pacote.montar(
        ficha,
        markdown=kit_textos.em_markdown(ficha, textos, notas),
        texto=kit_textos.em_texto(ficha, textos, notas),
        peca=peca,
        svg=svg,
        png=png,
        motivo_sem_peca=motivo,
    )
    return dados, peca, motivo


@require_http_methods(["POST"])
def exportar(request, edital_id, formato):
    """O material num arquivo, registrado na trilha do Edital (`FR-3435`, `FR-3436`)."""
    if formato not in FORMATOS:
        raise Http404
    ator, edital = _edital_do_kit(request, edital_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    e_peca = formato in PECAS
    if e_peca and (_motivo_sem_peca(request) or (formato == "png" and not kit_pacote.disponivel())):
        raise Http404
    agora = timezone.now()
    ficha = fichas.ler(edital, agora=agora, base_url=_base_url(request))
    if not ficha.tem_material:
        raise DomainError("kit_sem_material", ficha.motivo, 409)
    if request.POST.get("impressao", "") != ficha.impressao:
        raise DomainError("kit_desatualizado", MUDOU, 409)
    peca, sem_peca = None, None
    if formato in PACOTE:
        dados, peca, motivo = pacote(
            ficha,
            manchete=_indice_da_manchete(request.POST),
            motivo_sem_peca=_motivo_sem_peca(request),
        )
        sem_peca = motivo or None
    elif e_peca:
        indice = _indice_da_manchete(request.POST)
        try:
            peca = _compor(ficha, indice)
        except kit_peca.PecaRecusada as recusa:
            raise DomainError("kit_peca_recusada", recusa.motivo, 409) from None
        dados = _arquivo_da_peca(ficha, peca, formato)
    else:
        textos, notas = _material(ficha)
        if formato == "md":
            conteudo = kit_textos.em_markdown(ficha, textos, notas)
        else:
            conteudo = kit_textos.em_texto(ficha, textos, notas)
        dados = conteudo.encode()
    record_event(
        actor=ator,
        permission=PERMISSAO,
        operation=OPERACAO,
        aggregate=edital,
        now=agora,
        correlation_id=request.correlation_id,
        # Não é transição: o estado e a revisão anteriores são os de agora (FR-3436).
        previous_state=edital.status,
        previous_revision=edital.revision,
        detalhe={
            "formato": formato,
            "referencia": ficha.referencia,
            "versao": {
                "id": ficha.versao_id,
                "content_hash": ficha.versao_hash,
                "vigente_desde": ficha.versao_desde,
                "ato": ficha.versao_ato,
            },
            "template": kit_peca.TEMPLATE if peca else None,
            "impressao": ficha.impressao,
            "versao_da_impressao": ficha.versao_da_impressao,
            "campos": ficha.campos,
            "manchete": peca.manchete if peca else None,
            "sha256": hashlib.sha256(dados).hexdigest(),
            **({"sem_peca": sem_peca} if formato in PACOTE else {}),
        },
    )
    tipo, extensao = FORMATOS[formato]
    resposta = HttpResponse(dados, content_type=tipo)
    resposta["Content-Disposition"] = (
        f'attachment; filename="kit-{ficha.numero}-{ficha.ano}.{extensao}"'
    )
    resposta["X-Content-Type-Options"] = "nosniff"
    if formato == "svg":
        resposta["Content-Security-Policy"] = POLITICA_DO_SVG
    return marcar_como_privada(resposta)
