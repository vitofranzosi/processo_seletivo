"""A página "Assistente do Edital" da administração institucional (170, contracts/tela.md).

**No molde de Unidades da `110`** (R-10): o ator do nível institucional com a permissão, depois a
recusa da sessão de demonstração, as duas antes de ler qualquer coisa; a confirmação que mostra a
consequência e pede o motivo, e o caso de uso, que confere tudo de novo
(`duvidas/application/habilitacao.py`). A tela é a segunda barreira, e não a primeira (FR-7511).

**A página não chama o modelo** (FR-7502). Ela diz se a configuração do ambiente está completa, ou o
que falta, e manda verificar a conexão pelo comando da `073`: "completa" não é "disponível".

**Nada de painel de configurações** (FR-7513): os valores do ambiente aparecem para leitura, a
credencial só como presença, e nenhum se edita aqui.
"""

from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from processo_seletivo.duvidas.application import habilitacao
from processo_seletivo.duvidas.domain import habilitacao as nomes
from processo_seletivo.interface import identidade
from processo_seletivo.shared.api.problems import DomainError

ATOS = {"habilitar": True, "desabilitar": False}


def _ator(request):
    """O Administrador institucional na entrada institucional, ou a recusa que diz o que falta."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None
    habilitacao.exigir_permissao(ator)
    if identidade.resolucao_institucional(request).pessoa is None:
        raise DomainError(
            nomes.SO_ENTRADA_INSTITUCIONAL,
            "A habilitação do assistente é da entrada institucional; a demonstração não a alcança.",
            403,
        )
    return ator


def _faltas(configuracao):
    return [nomes.FALTAS[falta] for falta in configuracao["faltas"]]


@require_http_methods(["GET"])
def pagina(request):
    """A configuração, o piloto, os Editais, os requisitos e o histórico (contracts/tela.md)."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    dados = habilitacao.ler(ator)
    return render(
        request,
        "interface/habilitacao_do_assistente.html",
        {
            **dados,
            "faltas": _faltas(dados["configuracao"]),
            "piloto_habilitado": dados["piloto"] is not None and dados["piloto"].habilitada,
            "feito": request.GET.get("feito", ""),
        },
    )


def _confirmacao(request, *, frente, edital_id=None, ato):
    if ato not in ATOS:
        raise Http404
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    habilitar = ATOS[ato]
    erro, status = None, 200
    if request.method == "POST":
        funcao = habilitacao.habilitar if habilitar else habilitacao.desabilitar
        try:
            funcao(
                ator,
                frente=frente,
                edital_id=edital_id,
                motivo=request.POST.get("motivo", ""),
                correlation_id=getattr(request, "correlation_id", ""),
            )
        except DomainError as recusa:
            if recusa.status in (403, 404):
                raise
            erro, status = recusa, recusa.status
        else:
            feito = "habilitado" if habilitar else "desabilitado"
            return redirect(f"{reverse('interface:administracao-do-assistente')}?feito={feito}")
    # A conferência repete o que o ato recusaria, e a confirmação só oferece o botão quando nada
    # recusa: em produção, sem configuração, ou com o estado mudado, ela diz por quê (UX-811).
    edital, recusa = None, None
    try:
        edital = habilitacao.conferir(ator, frente=frente, edital_id=edital_id, habilitar=habilitar)
    except DomainError as conferida:
        if conferida.status in (403, 404):
            raise
        recusa = conferida
    if recusa is not None:
        erro, status = recusa, recusa.status
    if edital is None and frente == nomes.PAGINA_PUBLICA:
        from processo_seletivo.processos.models import Edital

        edital = Edital.objects.filter(id=edital_id).first()
    return render(
        request,
        "interface/habilitacao_do_assistente_confirmacao.html",
        {
            "frente": frente,
            "edital": edital,
            "habilitar": habilitar,
            "ato": ato,
            "motivo": request.POST.get("motivo", ""),
            "erro": erro,
            "pode_confirmar": recusa is None,
            "requisitos": nomes.REQUISITOS_DA_ABERTURA
            if erro is not None and erro.code == nomes.ABERTURA_PUBLICA_EM_PRODUCAO
            else (),
        },
        status=status,
    )


@require_http_methods(["GET", "POST"])
def piloto(request, ato):
    return _confirmacao(request, frente=nomes.PILOTO, ato=ato)


@require_http_methods(["GET", "POST"])
def pagina_publica(request, edital_id, ato):
    return _confirmacao(request, frente=nomes.PAGINA_PUBLICA, edital_id=edital_id, ato=ato)
