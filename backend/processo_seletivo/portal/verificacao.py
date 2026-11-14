"""As telas e as rotas do candidato na verificação por vídeo (166, US2, US5; `contracts/rotas.md`).

**A chave fecha tudo aqui** (FR-7100): desligada, toda rota responde como inexistente, pela mesma
recusa da titularidade — "não existe", "não é seu" e "não está ligado" não se distinguem (FR-7110).

**A página de gravação é a única do sistema com a exceção de CSP** (FR-7117): ela põe o cabeçalho
antes do middleware, com `media-src 'self' blob:` para a revisão local e a `Permissions-Policy` da
câmera e do microfone. O comprovante assiste pela entrega mediada, da própria origem, e não precisa
dela.

As rotas do envio falam JSON, porque quem as chama é o `gravacao.js`; a recusa volta com o código do
contrato e a frase, e a página a mostra.
"""

import json
import uuid

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from processo_seletivo.portal import identidade as identidade_do_candidato
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import marcar_como_privada
from processo_seletivo.shared.politica_de_conteudo import com_midia_local
from processo_seletivo.verificacao.application import abertura, disponibilidade, envio
from processo_seletivo.verificacao.domain import roteiro

PARTE = envio.PARTE_MAXIMA


def _identidade(request):
    return identidade_do_candidato.identidade_da_sessao(request)


def _json(dados, status=200):
    return marcar_como_privada(JsonResponse(dados, status=status))


def _recusa_em_json(erro: DomainError):
    return _json({"codigo": erro.code, "mensagem": erro.detail, "campo": erro.campo}, erro.status)


def _corpo(request) -> dict:
    try:
        dados = json.loads(request.body or b"{}")
    except ValueError:
        return {}
    return dados if isinstance(dados, dict) else {}


def _rotas(inscricao_id, etapa_id):
    argumentos = [inscricao_id, etapa_id]
    return {
        "pagina": reverse("portal:verificacao", args=argumentos),
        "envios": reverse("portal:verificacao-envios", args=argumentos),
        "comprovante": reverse("portal:verificacao-comprovante", args=argumentos),
        "acompanhamento": reverse("portal:acompanhamento", args=[inscricao_id]),
    }


@require_GET
def pagina(request, inscricao_id, etapa_id):
    """A escolha, o acolhimento, a maioridade, a câmera, a gravação, a revisão e o envio."""
    inscricao, etapa, situacao = envio.contexto_do_titular(
        identidade=_identidade(request), inscricao_id=inscricao_id, etapa_id=etapa_id
    )
    resposta = render(
        request,
        "portal/verificacao.html",
        {
            "inscricao": inscricao,
            "situacao": situacao,
            "pode_gravar": situacao.pode_enviar,
            "passos": roteiro.PASSOS,
            "roteiro_versao": roteiro.VERSAO,
            "teto_minutos": roteiro.TETO_SEGUNDOS // 60,
            "teto_segundos": roteiro.TETO_SEGUNDOS,
            "limite_bytes": settings.VERIFICACAO_POR_VIDEO_LIMITE_BYTES,
            "parte_bytes": PARTE,
            # A imagem de teste da prova de conceito, para verificar sem câmera e sem gravar
            # ninguém (research T-007). Só no desenvolvimento, que é o único lugar onde a chave liga.
            "fonte_sintetica": settings.DEBUG,
            "rotas": _rotas(inscricao.id, etapa["id"]),
        },
    )
    return marcar_como_privada(com_midia_local(resposta))


@require_POST
def iniciar(request, inscricao_id, etapa_id):
    dados = _corpo(request)
    try:
        novo = envio.iniciar(
            identidade=_identidade(request),
            inscricao_id=inscricao_id,
            etapa_id=etapa_id,
            tamanho=dados.get("tamanho"),
            formato=dados.get("formato"),
            duracao=dados.get("duracao"),
            marcas=dados.get("marcas"),
            roteiro_versao=dados.get("roteiro"),
            maioridade=dados.get("maioridade"),
        )
    except DomainError as erro:
        return _recusa_em_json(erro)
    return _json(
        {
            "envio": str(novo.id),
            "deslocamento": 0,
            "parte": PARTE,
            "estado": reverse("portal:verificacao-envio", args=[inscricao_id, etapa_id, novo.id]),
            "partes": reverse(
                "portal:verificacao-envio-partes", args=[inscricao_id, etapa_id, novo.id]
            ),
            "concluir": reverse(
                "portal:verificacao-envio-concluir", args=[inscricao_id, etapa_id, novo.id]
            ),
        },
        201,
    )


@require_GET
def estado_do_envio(request, inscricao_id, etapa_id, envio_id):
    try:
        atual = envio.consultar(
            identidade=_identidade(request),
            inscricao_id=inscricao_id,
            etapa_id=etapa_id,
            envio_id=envio_id,
        )
    except DomainError as erro:
        return _recusa_em_json(erro)
    return _json({"deslocamento": atual.recebido, "tamanho": atual.tamanho})


@require_http_methods(["PUT"])
def parte(request, inscricao_id, etapa_id, envio_id):
    """Uma parte do envio, no corpo cru (research T-002).

    O tamanho é conferido pelo `Content-Length` **antes** de ler o corpo: uma parte grande demais não
    chega à memória.
    """
    try:
        declarado = int(request.headers.get("Content-Length") or 0)
        deslocamento = int(request.GET.get("deslocamento", ""))
    except ValueError:
        return _json({"codigo": "parte", "mensagem": "A parte não declara o deslocamento."}, 422)
    if declarado > PARTE:
        return _json({"codigo": "parte", "mensagem": "Cada parte tem no máximo 8 MiB."}, 413)
    try:
        recebido = envio.receber_parte(
            identidade=_identidade(request),
            inscricao_id=inscricao_id,
            etapa_id=etapa_id,
            envio_id=envio_id,
            deslocamento=deslocamento,
            dados=request.body,
        )
    except envio.ForaDoDeslocamento as fora:
        return _json(
            {
                "codigo": "deslocamento",
                "mensagem": "Esta parte já chegou. O envio continua de onde parou.",
                "deslocamento": fora.deslocamento,
            },
            409,
        )
    except DomainError as erro:
        return _recusa_em_json(erro)
    return _json({"deslocamento": recebido})


@require_POST
def concluir(request, inscricao_id, etapa_id, envio_id):
    try:
        video = envio.concluir(
            identidade=_identidade(request),
            inscricao_id=inscricao_id,
            etapa_id=etapa_id,
            envio_id=envio_id,
            sha256=_corpo(request).get("sha256"),
            correlation_id=str(uuid.uuid4()),
        )
    except DomainError as erro:
        return _recusa_em_json(erro)
    return _json(
        {
            "video": str(video.id),
            "comprovante": reverse("portal:verificacao-comprovante", args=[inscricao_id, etapa_id]),
        },
        201,
    )


@require_GET
def comprovante(request, inscricao_id, etapa_id):
    """O comprovante do vídeo vigente; com `?abertura=`, o vídeo para assistir (FR-7123, FR-7127)."""
    inscricao, etapa, situacao = envio.contexto_do_titular(
        identidade=_identidade(request), inscricao_id=inscricao_id, etapa_id=etapa_id
    )
    if situacao.video is None:
        return redirect(reverse("portal:verificacao", args=[inscricao.id, etapa["id"]]))
    abertura_id = request.GET.get("abertura", "")
    fonte = ""
    if abertura_id and abertura.da_sessao(request, abertura_id):
        fonte = reverse(
            "portal:verificacao-video", args=[inscricao.id, etapa["id"], abertura_id]
        )
    resposta = render(
        request,
        "portal/verificacao_comprovante.html",
        {
            "inscricao": inscricao,
            "situacao": situacao,
            "video": situacao.video,
            "marcas": roteiro.marcas_com_titulo(situacao.video.marcas),
            "fonte": fonte,
            "pode_trocar": situacao.estado == disponibilidade.RECEBIDO and situacao.pode_enviar,
            "rotas": _rotas(inscricao.id, etapa["id"]),
            "abrir": reverse("portal:verificacao-abrir", args=[inscricao.id, etapa["id"]]),
        },
    )
    return marcar_como_privada(resposta)


@require_POST
def abrir(request, inscricao_id, etapa_id):
    aberta = abertura.abrir_pelo_titular(
        request,
        identidade=_identidade(request),
        inscricao_id=inscricao_id,
        etapa_id=etapa_id,
        correlation_id=str(uuid.uuid4()),
    )
    destino = reverse("portal:verificacao-comprovante", args=[inscricao_id, etapa_id])
    return redirect(f"{destino}?abertura={aberta.id}#assistir")


@require_GET
def video(request, inscricao_id, etapa_id, abertura_id):
    return abertura.entregar_ao_titular(
        request,
        identidade=_identidade(request),
        inscricao_id=inscricao_id,
        etapa_id=etapa_id,
        abertura_id=abertura_id,
    )
