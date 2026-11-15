"""Captura descartável das telas da 166 na main, para o antes e depois da 174 (FR-7893)."""

import os

import pytest

sync_api = pytest.importorskip("playwright.sync_api")
expect = sync_api.expect

from django.db import connections  # noqa: E402
from django.urls import reverse  # noqa: E402

from tests.fixtures.tela_do_navegador import Tela  # noqa: E402
from tests.fixtures.verificacao import enviar_video, montar_com_video  # noqa: E402

pytestmark = pytest.mark.django_db(transaction=True)

LARGURAS = {"375": (375, 667), "768": (768, 1024), "1280": (1280, 800), "1920": (1920, 1080)}


@pytest.fixture
def navegador_com_camera(monkeypatch):
    monkeypatch.setenv("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
    with sync_api.sync_playwright() as playwright:
        chromium = playwright.chromium.launch(
            args=["--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream"]
        )
        yield chromium
        chromium.close()
        connections.close_all()


@pytest.mark.parametrize("largura", list(LARGURAS))
def test_captura(navegador_com_camera, live_server, settings, raiz_de_arquivos, gestor, api_client, manager_headers, largura):
    settings.VERIFICACAO_POR_VIDEO = True
    w, h = LARGURAS[largura]
    tela = Tela(navegador_com_camera, live_server, f"antes-{largura}")
    cenario = montar_com_video(gestor, api_client, manager_headers, seed=7480, quantas=2)
    maria, joao = cenario["inscricoes"][:2]
    pagina = tela.candidato(maria, viewport={"width": w, "height": h})
    pagina.goto(live_server.url + reverse("portal:acompanhamento", args=[maria.id]))
    tela.capturar(pagina, "acompanhamento")
    pagina.get_by_role("link", name="Ver como funciona").click()
    expect(pagina.get_by_role("heading", name="Falta um passo seu")).to_be_visible()
    tela.capturar(pagina, "escolha")
    pagina.get_by_role("button", name="Gravar um vídeo curto").click()
    tela.capturar(pagina, "antes-de-gravar")
    pagina.get_by_text("Tenho 18 anos ou mais").click()
    pagina.get_by_role("button", name="Continuar").click()
    pagina.get_by_role("button", name="Abrir a câmera").click()
    pagina.wait_for_function("() => document.querySelector('[data-previa]').videoWidth > 0")
    tela.capturar(pagina, "camera")
    pagina.get_by_role("button", name="Ir para a gravação").click()
    pagina.get_by_role("button", name="Começar a gravar").click()
    pagina.wait_for_timeout(400)
    tela.capturar(pagina, "gravando")
    enviar_video(joao, cenario["hetero"], duracao=72.3)
    outra = tela.candidato(joao, viewport={"width": w, "height": h})
    outra.goto(live_server.url + reverse("portal:verificacao-comprovante", args=[joao.id, cenario["hetero"]]))
    tela.capturar(outra, "comprovante")
    tela.fechar()
