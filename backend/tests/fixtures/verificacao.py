"""O Edital da spec 166: a Heteroidentificação colegiada da `165`, que admite o vídeo.

É o Edital de `tests/fixtures/deliberacao.py` com duas coisas a mais: o Evento "Verificação da
autodeclaração", com início ontem e fim amanhã — o período da Etapa —, e `videoOption = true`. A
regra padrão é a unanimidade para o favorável, a do cenário da spec.

**Nenhum vídeo real** (research T-007): o arquivo é o MP4 sintético de `videos_sinteticos.py`, que
tem contêiner e duração, e nenhuma imagem.
"""

import json
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from processo_seletivo.verificacao.application import envio
from processo_seletivo.verificacao.domain import roteiro
from tests.fixtures import videos_sinteticos
from tests.fixtures.deliberacao import montar_colegiada, rascunho_colegiado
from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.edital import identificador

EVENTO = 403


def rascunho_com_video(seed, *, regra="UNANIMOUS_FOR_FAVORABLE", inicio=None, fim=None, video=True):
    agora = timezone.now()
    rascunho = rascunho_colegiado(seed, regra=regra)
    evento = identificador(EVENTO, seed)
    rascunho["schedule"].append(
        {
            "id": evento,
            "type": "VERIFICACAO",
            "description": "Verificação da autodeclaração",
            "startAt": (inicio or agora - timedelta(days=1)).isoformat(),
            "endAt": (fim or agora + timedelta(days=1)).isoformat(),
            "order": 2,
        }
    )
    hetero = rascunho["stages"][1]
    hetero["scheduleEventId"] = evento
    hetero["videoOption"] = video
    return rascunho


def montar_com_video(gestor, api_client, manager_headers, *, seed, quantas=2, **opcoes):
    """O cenário da `165` com o vídeo. `opcoes` vai a `rascunho_com_video`."""
    regra = opcoes.get("regra", "UNANIMOUS_FOR_FAVORABLE")
    return montar_colegiada(
        gestor,
        api_client,
        manager_headers,
        seed=seed,
        regra=regra,
        quantas=quantas,
        rascunho=rascunho_com_video(seed, **opcoes),
    )


def marcas(duracao=4.8):
    passo = duracao / len(roteiro.CHAVES)
    return [
        {"passo": chave, "instante": round(i * passo, 3)} for i, chave in enumerate(roteiro.CHAVES)
    ]


def identidade_de(inscricao):
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato

    return IdentidadeDoCandidato(
        subject=inscricao.identity_subject, nome=inscricao.nome, cpf="", email=""
    )


def enviar_video(inscricao, etapa_id, *, dados=None, duracao=4.8, parte=None, sha=None):
    """O envio inteiro pelo serviço, em partes; devolve o `VideoDaVerificacao`."""
    dados = dados if dados is not None else videos_sinteticos.mp4(duracao)
    identidade = identidade_de(inscricao)
    novo = envio.iniciar(
        identidade=identidade,
        inscricao_id=inscricao.id,
        etapa_id=etapa_id,
        tamanho=len(dados),
        formato="video/mp4",
        duracao=duracao,
        marcas=marcas(duracao),
        roteiro_versao=roteiro.VERSAO,
        maioridade=True,
    )
    parte = parte or len(dados)
    for inicio in range(0, len(dados), parte):
        envio.receber_parte(
            identidade=identidade,
            inscricao_id=inscricao.id,
            etapa_id=etapa_id,
            envio_id=novo.id,
            deslocamento=inicio,
            dados=dados[inicio : inicio + parte],
        )
    return envio.concluir(
        identidade=identidade,
        inscricao_id=inscricao.id,
        etapa_id=etapa_id,
        envio_id=novo.id,
        sha256=sha or videos_sinteticos.resumo(dados),
        correlation_id="teste",
    )


def enviar_pelo_portal(client, inscricao, etapa_id, *, dados=None, duracao=4.8, parte=None):
    """O mesmo envio, pelas rotas do portal, com a sessão do titular."""
    dados = dados if dados is not None else videos_sinteticos.mp4(duracao)
    entrar_como_titular(client, inscricao)
    inicio = client.post(
        reverse("portal:verificacao-envios", args=[inscricao.id, etapa_id]),
        data=json.dumps(
            {
                "tamanho": len(dados),
                "formato": "video/mp4;codecs=avc1",
                "duracao": duracao,
                "marcas": marcas(duracao),
                "roteiro": roteiro.VERSAO,
                "maioridade": True,
            }
        ),
        content_type="application/json",
    )
    assert inicio.status_code == 201, inicio.content
    rotas = inicio.json()
    parte = parte or len(dados)
    for deslocamento in range(0, len(dados), parte):
        resposta = client.put(
            f"{rotas['partes']}?deslocamento={deslocamento}",
            data=dados[deslocamento : deslocamento + parte],
            content_type="application/octet-stream",
        )
        assert resposta.status_code == 200, resposta.content
    fim = client.post(
        rotas["concluir"],
        data=json.dumps({"sha256": videos_sinteticos.resumo(dados)}),
        content_type="application/json",
    )
    return fim, rotas
