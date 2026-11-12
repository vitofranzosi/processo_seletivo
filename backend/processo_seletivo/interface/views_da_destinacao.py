"""A porta da destinação da vaga à ampla concorrência: a conferência e o ato (155, US1, UX-601).

**Módulo próprio, e não mais uma função em `views.py`**: o #489 mexe no mesmo arquivo, e a porta é a
mesma da ocupação — `_edital_para_classificar`, com a gestão da comissão —, importada de lá. Nenhum
`Http404` nasce aqui: o recorte inexistente e o marco fora do Perfil são as negativas que as funções
de `views.py` já classificam no inventário da `033`.

**Dois passos na mesma rota**, como o acréscimo da `097`: sem `confirmar`, a conferência; com ele, o
ato. A conferência não abre sobre recorte que o ato recusaria — a recusa volta à ocupação, dita —, e
a leitura mudada entre a conferência e o clique volta à conferência, recalculada.
"""

from uuid import uuid4

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from processo_seletivo.interface import identidade
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import marcar_como_privada


@require_http_methods(["POST"])
def destinar_vaga(request, edital_id, marco_id):
    """A conferência da destinação, ou o ato quando ela foi confirmada (FR-6308, FR-6309)."""
    from processo_seletivo.interface import views
    from processo_seletivo.interface.destinacao_da_vaga import Composicao, rotulo_do_recorte
    from processo_seletivo.ocupacao.application import destinacao
    from processo_seletivo.ocupacao.domain import nomes as nomes_da_ocupacao

    ator, edital, _ = views._edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return identidade.pedir_identificacao(request)
    lista_id = views._identidade_ou_404(request.POST.get("lista"))
    perfil_id = views._perfil_do_marco(edital, marco_id)
    destino = reverse("interface:ocupacao", args=[edital_id, marco_id])
    chave = request.POST.get("chave") or uuid4().hex
    aviso = ""
    if request.POST.get("confirmar") == "1":
        try:
            request.session["resultado_da_ocupacao"] = destinacao.destinar_vaga(
                actor=ator,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                perfil_id=perfil_id,
                marco_id=marco_id,
                lista_id=lista_id,
                assinatura=request.POST.get("leitura", ""),
                # **Uma composição nova, lida sob a trava pelo próprio ato** (155, R-004): a da
                # conferência já é um fato velho no instante do clique.
                fatos_externos=Composicao(),
                idempotency_key=chave,
                correlation_id=f"interface-destinacao-{edital_id}",
            )
            request.session["acao_da_ocupacao"] = "destinacao"
            return redirect(destino)
        except DomainError as erro:
            if erro.code != nomes_da_ocupacao.LEITURA_DO_RECORTE_MUDOU:
                return views._recusa_da_ocupacao(request, destino, erro, "destinacao")
            aviso = erro.detail
    previa = destinacao.previa_da_destinacao(
        edital=edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        fatos_externos=Composicao(),
    )
    if previa["recusa"] is not None:
        codigo, frase = previa["recusa"]
        return views._recusa_da_ocupacao(
            request, destino, DomainError(codigo, frase, 409), "destinacao"
        )
    return marcar_como_privada(
        render(
            request,
            "interface/ocupacao_destinacao.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "marco_id": marco_id,
                "lista_id": lista_id,
                "rotulo": rotulo_do_recorte(previa["versao"].content, perfil_id, lista_id),
                "previa": previa,
                "chave_idempotencia": chave,
                "aviso": aviso,
                "pode_retificar": ator.can("retificacao:elaborar"),
            },
        )
    )


__all__ = ["destinar_vaga"]
