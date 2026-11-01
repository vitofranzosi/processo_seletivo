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

**Nada aqui toca a publicação** (`FR-3405`): a única escrita é o evento da trilha.
"""

import hashlib

from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface import identidade, kit_textos
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

#: Os formatos do incremento A (`D-001`). A peça e o pacote entram nos incrementos B e C.
FORMATOS = {
    "md": ("text/markdown; charset=utf-8", "md"),
    "txt": ("text/plain; charset=utf-8", "txt"),
}


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
                "formatos": list(FORMATOS),
            },
        )
    )


@require_http_methods(["POST"])
def exportar(request, edital_id, formato):
    """O material num arquivo, registrado na trilha do Edital (`FR-3435`, `FR-3436`)."""
    if formato not in FORMATOS:
        raise Http404
    ator, edital = _edital_do_kit(request, edital_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    agora = timezone.now()
    ficha = fichas.ler(edital, agora=agora, base_url=_base_url(request))
    if not ficha.tem_material:
        raise DomainError("kit_sem_material", ficha.motivo, 409)
    if request.POST.get("impressao", "") != ficha.impressao:
        raise DomainError("kit_desatualizado", MUDOU, 409)
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
            "template": None,
            "impressao": ficha.impressao,
            "versao_da_impressao": ficha.versao_da_impressao,
            "campos": ficha.campos,
            "manchete": None,
            "sha256": hashlib.sha256(dados).hexdigest(),
        },
    )
    tipo, extensao = FORMATOS[formato]
    resposta = HttpResponse(dados, content_type=tipo)
    resposta["Content-Disposition"] = (
        f'attachment; filename="kit-{ficha.numero}-{ficha.ano}.{extensao}"'
    )
    resposta["X-Content-Type-Options"] = "nosniff"
    return marcar_como_privada(resposta)
