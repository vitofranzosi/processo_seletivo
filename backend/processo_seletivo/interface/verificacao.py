"""As rotas da Mesa para o vídeo da verificação (166, FR-7128 a FR-7131; `contracts/rotas.md`).

**Abrir é ato, e assistir é a entrega dele** (D-007): o `POST` confere o resumo, grava a abertura e
registra um evento; o `<video>` pede os bytes com `Range`, sem evento. Só quem está alocado à Etapa e
tem a Atribuição ativa da inscrição chega aqui — todo o resto responde como inexistente, inclusive a
presidência sem Atribuição (FR-7129).

**A chave não fecha a Mesa** (achado I1 do `/speckit-analyze`): os vídeos já recebidos continuam
sendo analisados, porque o parecer sobre eles é ato do certame.
"""

import uuid

from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from processo_seletivo.interface import identidade
from processo_seletivo.interface.views import _mesa_do_avaliador
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import marcar_como_privada
from processo_seletivo.verificacao.application import abertura


def _volta_a_mesa(edital_id, etapa_id, inscricao_id, sufixo=""):
    destino = reverse("interface:mesa-inscricao", args=[edital_id, etapa_id, inscricao_id])
    return redirect(f"{destino}{sufixo}")


@require_POST
def abrir_video(request, edital_id, etapa_id, inscricao_id):
    ator, edital = _mesa_do_avaliador(request, edital_id, etapa_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    try:
        aberta = abertura.abrir_pela_comissao(
            request,
            ator=ator,
            edital=edital,
            etapa_id=etapa_id,
            inscricao_id=inscricao_id,
            correlation_id=str(uuid.uuid4()),
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        request.session["aviso_da_avaliacao"] = {"tipo": "erro", "texto": recusa.detail}
        return _volta_a_mesa(edital_id, etapa_id, inscricao_id)
    return _volta_a_mesa(edital_id, etapa_id, inscricao_id, f"?abertura={aberta.id}#video")


@require_GET
def video(request, edital_id, etapa_id, inscricao_id, abertura_id):
    ator, edital = _mesa_do_avaliador(request, edital_id, etapa_id)
    if ator is None:
        raise Http404
    try:
        return abertura.entregar_a_comissao(
            request,
            ator=ator,
            edital=edital,
            etapa_id=etapa_id,
            inscricao_id=inscricao_id,
            abertura_id=abertura_id,
        )
    except DomainError as recusa:
        raise Http404 from recusa


@require_http_methods(["GET", "POST"])
def encaminhar(request, edital_id, etapa_id):
    """O encaminhamento à entrevista ao vivo, em dois passos (166, FR-7138, FR-7140; D-005).

    A porta é a de consolidar — a gestão da comissão —, e o alcance aparece antes do ato: a lista das
    inscrições que o vídeo não confirmou. **Sem contagem dos sentidos**: a presidência pode ser
    membro, e a entrevista ao vivo ainda vai ser dada às cegas (FR-7082 da `165`).
    """
    from processo_seletivo.interface.views import _etapa_para_distribuir
    from processo_seletivo.verificacao.application import encaminhamento

    ator, edital, etapa = _etapa_para_distribuir(request, edital_id, etapa_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    destino = reverse("interface:distribuicao", args=[edital_id, etapa_id])
    if request.method == "POST" and request.POST.get("confirmar") == "1":
        try:
            request.session["resultado_da_consolidacao"] = encaminhamento.encaminhar(
                actor=ator,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                etapa_id=etapa_id,
                inscricao_ids=request.POST.get("inscricoes", "").split(),
                idempotency_key=request.POST.get("chave_idempotencia") or uuid.uuid4().hex,
                correlation_id=getattr(request, "correlation_id", ""),
            )
        except DomainError as recusa:
            if recusa.status == 404:
                raise Http404 from recusa
            request.session["erro_da_consolidacao"] = recusa.detail
        return redirect(destino)
    try:
        lista = encaminhamento.a_encaminhar(edital=edital, etapa_id=etapa_id)
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        request.session["erro_da_consolidacao"] = recusa.detail
        return redirect(destino)
    return marcar_como_privada(
        render(
            request,
            "interface/encaminhar_ao_vivo.html",
            {
                "edital": edital,
                "processo": edital.processo,
                "etapa": etapa,
                "inscricoes": lista,
                "chave_idempotencia": uuid.uuid4().hex,
            },
        )
    )
