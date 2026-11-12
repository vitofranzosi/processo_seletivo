"""As portas da vaga sem quem a ocupe: a destinação, a não preenchida e os desfazimentos (155).

(US1, US2, US6, UX-601.)

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
                "modo": "destinacao",
            },
        )
    )


@require_http_methods(["POST"])
def declarar_nao_preenchida(request, edital_id, marco_id):
    """A conferência da declaração de vaga não preenchida, ou o ato (FR-6323, FR-6325).

    **O fundamento se escreve na conferência**, como o motivo da sucessão (o controle da `058`):
    é ao ver o efeito que a pessoa diz por que a vaga fica sem ocupante. Faltando, a conferência
    volta com a recusa no lugar do campo, e nada é gravado.
    """
    from processo_seletivo.interface import acoes, views
    from processo_seletivo.interface.destinacao_da_vaga import Composicao, rotulo_do_recorte
    from processo_seletivo.ocupacao.application import destinacao
    from processo_seletivo.ocupacao.domain import nomes as nomes_da_ocupacao

    ator, edital, _ = views._edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return identidade.pedir_identificacao(request)
    lista_id = (
        views._identidade_ou_404(request.POST.get("lista")) if request.POST.get("lista") else None
    )
    perfil_id = views._perfil_do_marco(edital, marco_id)
    destino = reverse("interface:ocupacao", args=[edital_id, marco_id])
    chave = request.POST.get("chave") or uuid4().hex
    fundamento = (request.POST.get("fundamento") or "").strip()
    aviso = ""
    if request.POST.get("confirmar") == "1":
        try:
            request.session["resultado_da_ocupacao"] = destinacao.declarar_nao_preenchida(
                actor=ator,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                perfil_id=perfil_id,
                marco_id=marco_id,
                lista_id=lista_id,
                fundamento=fundamento,
                assinatura=request.POST.get("leitura", ""),
                fatos_externos=Composicao(),
                idempotency_key=chave,
                correlation_id=f"interface-nao-preenchida-{edital_id}",
            )
            request.session["acao_da_ocupacao"] = "nao_preenchida"
            return redirect(destino)
        except DomainError as erro:
            if erro.code not in (
                nomes_da_ocupacao.LEITURA_DO_RECORTE_MUDOU,
                nomes_da_ocupacao.FUNDAMENTO_OBRIGATORIO,
            ):
                return views._recusa_da_ocupacao(request, destino, erro, "nao_preenchida")
            aviso = erro.detail
    previa = destinacao.previa_da_nao_preenchida(
        edital=edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        fatos_externos=Composicao(),
    )
    if previa["recusa"] is not None:
        codigo, frase = previa["recusa"]
        return views._recusa_da_ocupacao(
            request, destino, DomainError(codigo, frase, 409), "nao_preenchida"
        )
    return _conferencia(
        request,
        edital,
        marco_id,
        modo="nao_preenchida",
        previa=previa,
        lista_id=lista_id,
        rotulo=rotulo_do_recorte(previa["versao"].content, perfil_id, lista_id),
        chave=chave,
        aviso=aviso,
        texto=fundamento,
        retificacao_admitida=acoes.pode_retificar(edital, ator),
    )


@require_http_methods(["POST"])
def desfazer_destinacao(request, edital_id, marco_id):
    """A conferência do desfazimento da destinação, ou o ato (FR-6334 a FR-6336)."""
    return _desfazer(request, edital_id, marco_id, modo="desfazer_destinacao")


@require_http_methods(["POST"])
def desfazer_nao_preenchida(request, edital_id, marco_id):
    """A conferência do desfazimento da declaração de não preenchida, ou o ato (FR-6334)."""
    return _desfazer(request, edital_id, marco_id, modo="desfazer_nao_preenchida")


def _desfazer(request, edital_id, marco_id, *, modo):
    """Os dois desfazimentos, na mesma forma: conferência com motivo, e o ato.

    **A recusa por chamada dependente volta à ocupação dita** (FR-6335): ela nomeia cada pessoa
    chamada para esta vaga e diz que a chamada precisa do seu desfecho antes. O pedido recusado já
    está na trilha quando a tela o diz — é o ato que o registra, e não a tela.
    """
    from processo_seletivo.interface import views
    from processo_seletivo.interface.destinacao_da_vaga import (
        chamadas_dependentes,
        rotulo_do_recorte,
    )
    from processo_seletivo.ocupacao.application import destinacao
    from processo_seletivo.ocupacao.domain import nomes as nomes_da_ocupacao

    ator, edital, _ = views._edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return identidade.pedir_identificacao(request)
    views._perfil_do_marco(edital, marco_id)
    destino = reverse("interface:ocupacao", args=[edital_id, marco_id])
    chave = request.POST.get("chave") or uuid4().hex
    motivo = (request.POST.get("motivo") or "").strip()
    alvo = (request.POST.get("ato") or "").strip()
    da_destinacao = modo == "desfazer_destinacao"
    aviso = ""
    if request.POST.get("confirmar") == "1":
        comando = (
            destinacao.desfazer_destinacao if da_destinacao else destinacao.desfazer_nao_preenchida
        )
        alvo_do_comando = {"movimento_id": alvo} if da_destinacao else {"declaracao_id": alvo}
        try:
            request.session["resultado_da_ocupacao"] = comando(
                actor=ator,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                motivo=motivo,
                assinatura=request.POST.get("leitura", ""),
                chamadas_dependentes=chamadas_dependentes,
                idempotency_key=chave,
                correlation_id=f"interface-{modo.replace('_', '-')}-{edital_id}",
                **alvo_do_comando,
            )
            request.session["acao_da_ocupacao"] = modo
            return redirect(destino)
        except DomainError as erro:
            if erro.code not in (
                nomes_da_ocupacao.LEITURA_DO_RECORTE_MUDOU,
                nomes_da_ocupacao.MOTIVO_OBRIGATORIO,
            ):
                return views._recusa_da_ocupacao(request, destino, erro, modo)
            aviso = erro.detail
    try:
        previa = (
            destinacao.previa_do_desfazimento_da_destinacao(
                edital=edital, movimento_id=alvo, chamadas_dependentes=chamadas_dependentes
            )
            if da_destinacao
            else destinacao.previa_do_desfazimento_da_nao_preenchida(
                edital=edital, declaracao_id=alvo, chamadas_dependentes=chamadas_dependentes
            )
        )
    except DomainError as erro:
        return views._recusa_da_ocupacao(request, destino, erro, modo)
    if previa["recusa"] is not None and (
        previa["recusa"][0] != nomes_da_ocupacao.DESTINACAO_COM_CHAMADA_DEPENDENTE
    ):
        codigo, frase = previa["recusa"]
        return views._recusa_da_ocupacao(request, destino, DomainError(codigo, frase, 409), modo)
    registro = previa["movimento"] if da_destinacao else previa["declaracao"]
    lista_id = registro.origem_lista_id if da_destinacao else registro.lista_id
    return _conferencia(
        request,
        edital,
        marco_id,
        modo=modo,
        previa=previa,
        lista_id=lista_id,
        rotulo=rotulo_do_recorte(previa["versao"].content, registro.perfil_id, lista_id),
        chave=chave,
        aviso=aviso,
        texto=motivo,
        registro=registro,
    )


def _conferencia(
    request, edital, marco_id, *, modo, previa, lista_id, rotulo, chave, aviso, **extra
):
    """A conferência comum dos quatro atos da vaga sem quem a ocupe (155, UX-601)."""
    return marcar_como_privada(
        render(
            request,
            "interface/ocupacao_destinacao.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "marco_id": marco_id,
                "lista_id": lista_id,
                "rotulo": rotulo,
                "previa": previa,
                "chave_idempotencia": chave,
                "aviso": aviso,
                "modo": modo,
                **extra,
            },
        )
    )


__all__ = [
    "declarar_nao_preenchida",
    "desfazer_destinacao",
    "desfazer_nao_preenchida",
    "destinar_vaga",
]
