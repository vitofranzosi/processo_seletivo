"""A página de gravação, o comprovante e o acesso no acompanhamento (166, US2, US5).

FR-7100, FR-7107, FR-7110, FR-7117, FR-7145; SC-2376.
"""

import pytest
from django.urls import reverse

from processo_seletivo.shared.politica_de_conteudo import CABECALHO, PERMISSOES
from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.verificacao import enviar_video, montar_com_video

pytestmark = pytest.mark.django_db


@pytest.fixture
def cenario(raiz_de_arquivos, gestor, api_client, manager_headers):
    return montar_com_video(gestor, api_client, manager_headers, seed=6640, quantas=2)


def _pagina(cenario, inscricao=None):
    inscricao = inscricao or cenario["inscricoes"][0]
    return reverse("portal:verificacao", args=[inscricao.id, cenario["hetero"]])


def test_so_a_pagina_de_gravacao_tem_a_excecao_de_csp(cenario, client):
    """FR-7117: `media-src 'self' blob:` e a câmera só aqui."""
    maria = cenario["inscricoes"][0]
    entrar_como_titular(client, maria)
    resposta = client.get(_pagina(cenario))
    assert resposta.status_code == 200
    assert "media-src 'self' blob:" in resposta[CABECALHO]
    assert "unsafe-inline" not in resposta[CABECALHO]
    assert resposta[PERMISSOES] == "camera=(self), microphone=(self)"
    corpo = resposta.content.decode()
    assert "As duas formas valem igual." in corpo
    assert "Gravar um vídeo curto" in corpo
    assert "Prefiro entrevista ao vivo" in corpo
    assert "Tenho menos de 18 anos" in corpo
    assert "Não consigo usar a câmera" in corpo
    acompanhamento = client.get(reverse("portal:acompanhamento", args=[maria.id]))
    assert "media-src" not in acompanhamento[CABECALHO]
    assert PERMISSOES not in acompanhamento


def test_o_acompanhamento_leva_a_verificacao(cenario, client):
    """FR-7145: o acesso, com o fim do período; não é o degrau da situação (entrega 4)."""
    maria = cenario["inscricoes"][0]
    entrar_como_titular(client, maria)
    corpo = client.get(reverse("portal:acompanhamento", args=[maria.id])).content.decode()
    assert "Verificação da autodeclaração" in corpo
    assert _pagina(cenario) in corpo


def test_depois_do_envio_o_acompanhamento_leva_ao_comprovante(cenario, client):
    maria = cenario["inscricoes"][0]
    enviar_video(maria, cenario["hetero"])
    entrar_como_titular(client, maria)
    corpo = client.get(reverse("portal:acompanhamento", args=[maria.id])).content.decode()
    assert "A comissão ainda não o abriu." in corpo
    comprovante = reverse("portal:verificacao-comprovante", args=[maria.id, cenario["hetero"]])
    assert comprovante in corpo
    pagina = client.get(comprovante)
    assert pagina.status_code == 200
    assert "isso não é reprovação" in pagina.content.decode()
    assert "Gravar outro vídeo" in pagina.content.decode()


def test_o_titular_assiste_pelo_comprovante(cenario, client):
    maria = cenario["inscricoes"][0]
    video = enviar_video(maria, cenario["hetero"])
    entrar_como_titular(client, maria)
    rota = reverse("portal:verificacao-abrir", args=[maria.id, cenario["hetero"]])
    resposta = client.post(rota)
    assert resposta.status_code == 302
    pagina = client.get(resposta["Location"])
    corpo = pagina.content.decode()
    assert "nodownload" in corpo
    fonte = corpo.split('class="video-do-titular" src="')[1].split('"')[0]
    entrega = client.get(fonte, HTTP_RANGE="bytes=0-9")
    assert entrega.status_code == 206
    assert b"".join(entrega.streaming_content) == open_bytes(video)[:10]


def open_bytes(video):
    from processo_seletivo.verificacao.application import envio

    with open(envio.caminho(video.arquivo), "rb") as arquivo:
        return arquivo.read()


def test_outra_pessoa_recebe_a_recusa_uniforme(cenario, client):
    """FR-7110: a página da inscrição alheia responde como inexistente."""
    maria, joao = cenario["inscricoes"][:2]
    entrar_como_titular(client, joao)
    assert client.get(_pagina(cenario, maria)).status_code == 404


def test_com_a_chave_desligada_nada_responde(cenario, client, settings):
    """FR-7100, SC-2376: nem a página, nem o cartão do acompanhamento."""
    maria = cenario["inscricoes"][0]
    entrar_como_titular(client, maria)
    settings.VERIFICACAO_POR_VIDEO = False
    assert client.get(_pagina(cenario)).status_code == 404
    corpo = client.get(reverse("portal:acompanhamento", args=[maria.id])).content.decode()
    assert "verificacao-no-acompanhamento" not in corpo
