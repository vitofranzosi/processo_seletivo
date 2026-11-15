"""A gravação do vídeo da verificação de ponta a ponta, num navegador de verdade (174, T-015).

O candidato vai do acompanhamento ao comprovante com a câmera e o microfone **simulados** do
Chromium (`--use-fake-device-for-media-stream`, `--use-fake-ui-for-media-stream`): a permissão é
concedida sem diálogo, e o pedido de permissão — que é o que a FR-7866 muda — passa pelo caminho de
verdade, e não pela imagem de teste do desenvolvimento. O servidor da suíte responde em
`localhost`, que é contexto seguro, como a câmera exige.

Mede o que só o navegador mostra: a coluna centrada (SC-2650), o palco na altura da tela com a
instrução e os botões à vista (SC-2651), nenhum gesto entre "Continuar" e "Começar a gravar"
(SC-2652), nada escondido aparecendo em repouso (SC-2653), o pedido de envio igual ao de antes
(SC-2654), a faixa da instrução escura o bastante (SC-2656) e a confirmação no primeiro quadro do
comprovante (SC-2659). `NAVEGADOR_CAPTURAS=<pasta>` grava as telas de cada passo.
"""

import json
import os

import pytest

sync_api = pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador")
expect = sync_api.expect

from django.db import connections  # noqa: E402
from django.urls import reverse  # noqa: E402

from processo_seletivo.verificacao.domain import roteiro  # noqa: E402
from tests.fixtures.tela_do_navegador import Tela  # noqa: E402
from tests.fixtures.verificacao import montar_com_video  # noqa: E402

pytestmark = pytest.mark.django_db(transaction=True)

CELULAR = {"width": 375, "height": 667}
TABLET = {"width": 768, "height": 1024}
DESKTOP = {"width": 1280, "height": 800}
LARGO = {"width": 1920, "height": 1080}


@pytest.fixture
def navegador_com_camera(monkeypatch):
    """O Chromium com câmera e microfone simulados; o resto como a fixture `navegador`."""
    monkeypatch.setenv("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
    visivel = os.getenv("NAVEGADOR_VISIVEL") == "1"
    with sync_api.sync_playwright() as playwright:
        chromium = playwright.chromium.launch(
            headless=not visivel,
            slow_mo=300 if visivel else 0,
            args=["--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream"],
        )
        yield chromium
        chromium.close()
        # A conexão que o ORM abre com o Playwright ativo travava o `DROP DATABASE` do fim da suíte
        # (a armadilha do `CLAUDE.md`); a fixture `navegador` fecha pelo mesmo motivo.
        connections.close_all()


@pytest.fixture
def tela(navegador_com_camera, live_server, settings, request, raiz_de_arquivos):
    settings.VERIFICACAO_POR_VIDEO = True
    atual = Tela(navegador_com_camera, live_server, request.node.name)
    yield atual
    atual.fechar()
    assert atual.violacoes == [], "violação da política de conteúdo no console"


def _escondidos_visiveis(pagina):
    """Todo elemento com `hidden` que, mesmo assim, ocupa a tela (SC-2653, A-2)."""
    return pagina.evaluate(
        """() => Array.from(document.querySelectorAll('main [hidden]'))
             .filter(el => getComputedStyle(el).display !== 'none')
             .map(el => el.outerHTML.slice(0, 80))"""
    )


def _na_tela(pagina, localizador):
    """O elemento está inteiro dentro da janela, sem rolar."""
    caixa = localizador.bounding_box()
    altura = pagina.viewport_size["height"]
    largura = pagina.viewport_size["width"]
    return (
        caixa is not None
        and caixa["y"] >= 0
        and caixa["y"] + caixa["height"] <= altura + 0.5
        and caixa["x"] >= 0
        and caixa["x"] + caixa["width"] <= largura + 0.5
    )


def _sem_rolagem_horizontal(pagina):
    largura = pagina.evaluate("document.documentElement.scrollWidth")
    assert largura <= pagina.viewport_size["width"], f"a página rola na horizontal ({largura} px)"


def _contraste_da_faixa(pagina):
    """O contraste do texto branco sobre a faixa da instrução, no pior caso: um quadro branco."""
    fundo = pagina.evaluate(
        "getComputedStyle(document.querySelector('.instrucao-do-passo')).backgroundColor"
    )
    partes = [float(x) for x in fundo[fundo.index("(") + 1 : -1].split(",")]
    r, g, b = partes[:3]
    alfa = partes[3] if len(partes) == 4 else 1.0
    # A faixa composta sobre branco puro: cada canal é a mistura linear da cor com 255.
    mistura = [c * alfa + 255 * (1 - alfa) for c in (r, g, b)]

    def luminancia(canais):
        lineares = []
        for c in canais:
            c = c / 255
            lineares.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * lineares[0] + 0.7152 * lineares[1] + 0.0722 * lineares[2]

    return (1.05) / (luminancia(mistura) + 0.05)


@pytest.mark.parametrize(
    "viewport", [CELULAR, TABLET, DESKTOP, LARGO], ids=["375", "768", "1280", "1920"]
)
def test_do_acompanhamento_ao_comprovante(tela, gestor, api_client, manager_headers, viewport):
    cenario = montar_com_video(gestor, api_client, manager_headers, seed=7480, quantas=2)
    maria = cenario["inscricoes"][0]
    servidor = tela.servidor.url
    pagina = tela.candidato(maria, viewport=viewport)
    celular = viewport is CELULAR

    pedidos = []
    pagina.on(
        "request",
        lambda pedido: (
            pedidos.append(pedido.post_data)
            if pedido.method == "POST" and pedido.url.endswith("/envios")
            else None
        ),
    )

    # --- o acompanhamento: o selo, o prazo em linha própria e a ação que diz para onde leva
    pagina.goto(servidor + reverse("portal:acompanhamento", args=[maria.id]))
    expect(pagina.locator(".rotulo-da-situacao")).to_contain_text("Falta um passo seu")
    assert pagina.locator(".rotulo-da-situacao .icone").count() == 1
    expect(pagina.locator(".prazo-do-passo")).to_contain_text("Prazo:")
    tela.capturar(pagina, "acompanhamento")
    pagina.get_by_role("link", name="Escolher entre vídeo e entrevista ao vivo").click()

    # --- a escolha: a coluna centrada e nada escondido à vista
    expect(pagina.get_by_role("heading", name="Falta um passo seu")).to_be_visible()
    _sem_rolagem_horizontal(pagina)
    assert _escondidos_visiveis(pagina) == []
    if not celular:
        caixa = pagina.locator(".jornada").bounding_box()
        largura = pagina.evaluate("document.documentElement.clientWidth")
        esquerda, direita = caixa["x"], largura - (caixa["x"] + caixa["width"])
        assert abs(esquerda - direita) <= 1, (esquerda, direita)
    tela.capturar(pagina, "escolha")
    pagina.get_by_role("button", name="Gravar um vídeo curto").click()

    # --- "Antes de gravar": a recusa nasce escondida e só aparece depois do gesto
    expect(pagina.get_by_role("heading", name="Antes de gravar")).to_be_visible()
    recusa = pagina.locator("[data-erro-maioridade]")
    expect(recusa).to_be_hidden()
    assert _escondidos_visiveis(pagina) == []
    tela.capturar(pagina, "antes-de-gravar")
    pagina.get_by_role("button", name="Continuar").click()
    expect(recusa).to_be_visible()
    assert pagina.evaluate("document.activeElement.matches('[data-pergunta-maioridade]')")
    pagina.get_by_text("Tenho 18 anos ou mais").click()

    # --- o palco: "Continuar" já abre a câmera, e "Começar a gravar" aparece sem outro gesto
    pagina.get_by_role("button", name="Continuar").click()
    comecar = pagina.get_by_role("button", name="Começar a gravar")
    expect(comecar).to_be_visible()
    expect(pagina.locator("[data-momento='gravar']")).to_have_attribute("aria-current", "step")
    pagina.wait_for_function("() => document.querySelector('[data-previa]').videoWidth > 0")
    # O gesto principal fica na faixa de baixo do vídeo, como "Próximo" depois: dentro do palco, e
    # não no pé do painel, cuja altura muda com a fonte do sistema (a CI do #568, no Linux).
    assert pagina.locator(".palco [data-comecar]").count() == 1
    assert _na_tela(pagina, comecar)
    assert _na_tela(pagina, pagina.locator(".link-no-palco"))
    tela.capturar(pagina, "palco-preparo")
    comecar.click()

    palco = pagina.locator("[data-tela='palco']")
    expect(palco).to_have_attribute("data-estado", "gravando")
    proximo = pagina.locator("[data-proximo]")
    titulos = [passo.titulo for passo in roteiro.PASSOS]
    for indice, titulo in enumerate(titulos):
        expect(pagina.locator("[data-passo-rotulo]")).to_have_text(f"Passo {indice + 1} de 4")
        expect(pagina.locator("[data-passo-titulo]")).to_have_text(titulo)
        expect(pagina.locator("[data-passo-atual]")).to_have_text(roteiro.PASSOS[indice].instrucao)
        anuncio = f"Passo {indice + 1} de 4: {titulo}."
        expect(pagina.locator("[data-anuncio]")).to_contain_text(anuncio)
        if celular:
            altura = palco.bounding_box()["height"]
            assert abs(altura - viewport["height"]) <= 1, altura
            assert _na_tela(pagina, pagina.locator(".texto-do-passo"))
            assert _na_tela(pagina, proximo)
            assert _na_tela(pagina, pagina.locator(".link-no-palco"))
        assert pagina.locator(".passos-do-roteiro").is_hidden()
        assert pagina.evaluate("document.activeElement.hasAttribute('data-proximo')")
        if indice == 0:
            assert _contraste_da_faixa(pagina) >= 4.5
            tela.capturar(pagina, "palco-gravando")
        pagina.wait_for_timeout(600)
        if celular:
            proximo.click()
        else:
            # No computador, Espaço avança: o foco fica em "Próximo" (FR-7869).
            pagina.keyboard.press("Space")
    expect(pagina.get_by_role("heading", name="Assista antes de enviar")).to_be_visible()
    expect(pagina.locator("[data-dados-da-tomada]")).to_contain_text(" s.")
    expect(pagina.locator("[data-dados-da-tomada]")).to_contain_text("MB da sua internet")
    tela.capturar(pagina, "revisao")

    # --- o envio: o pedido é o de antes (SC-2654), e o comprovante abre pela confirmação
    pagina.get_by_role("button", name="Enviar este vídeo").click()
    pagina.wait_for_url("**/comprovante*", timeout=30_000)
    corpo = json.loads(pedidos[-1])
    assert corpo["roteiro"] == roteiro.VERSAO
    assert [marca["passo"] for marca in corpo["marcas"]] == list(roteiro.CHAVES)
    assert corpo["formato"] in ("video/webm", "video/mp4")
    assert corpo["maioridade"] is True

    confirmacao = pagina.get_by_role("heading", name="Seu vídeo foi enviado")
    expect(confirmacao).to_be_visible()
    assert _na_tela(pagina, pagina.locator(".confirmacao-do-envio"))
    agora = pagina.get_by_role("heading", name="E agora?").bounding_box()
    dados = pagina.get_by_role("heading", name="Dados para conferência").bounding_box()
    assert dados["y"] > agora["y"]
    expect(pagina.locator(".dados-do-video")).to_contain_text("Código de conferência do arquivo")
    _sem_rolagem_horizontal(pagina)
    tela.capturar(pagina, "comprovante")


# --- a detecção do giro do rosto (176) ---------------------------------------------------------


def _ate_o_palco(tela, pagina, cenario, maria, *, imagem_de_teste=False):
    """Da página da gravação ao palco, pelo caminho do candidato."""
    pagina.goto(
        tela.servidor.url + reverse("portal:verificacao", args=[maria.id, cenario["hetero"]])
    )
    pagina.get_by_role("button", name="Gravar um vídeo curto").click()
    pagina.get_by_text("Tenho 18 anos ou mais").click()
    if imagem_de_teste:
        pagina.get_by_label("Usar imagem de teste").check()
    pagina.get_by_role("button", name="Continuar").click()
    expect(pagina.get_by_role("button", name="Começar a gravar")).to_be_visible()


def test_o_motor_de_verdade_carrega_da_propria_origem_e_sem_rosto_vale_o_toque(
    tela, gestor, api_client, manager_headers, settings
):
    """176, SC-2751, SC-2754, SC-2756; research T-003, T-004, T-010.

    O motor de verdade, baixado do servidor da suíte e compilado sob a política da página — a
    fixture `tela` recusa qualquer violação no console. A câmera simulada do Chromium não mostra
    rosto: os perfis não avançam sozinhos, e o toque continua valendo (FR-8014)."""
    settings.VERIFICACAO_DETECCAO_DO_GIRO = True
    cenario = montar_com_video(gestor, api_client, manager_headers, seed=17610, quantas=2)
    maria = cenario["inscricoes"][0]
    pagina = tela.candidato(maria, viewport=DESKTOP)
    pedidos = []
    pagina.on("request", lambda pedido: pedidos.append(pedido.url))

    _ate_o_palco(tela, pagina, cenario, maria)
    raiz = pagina.locator("[data-verificacao]")
    expect(raiz).to_have_attribute("data-deteccao", "pronta", timeout=90_000)
    aviso = pagina.locator("[data-aviso-deteccao]")
    expect(aviso).to_be_visible()
    expect(aviso).to_contain_text("nada dessa leitura é enviado nem guardado")
    expect(pagina.locator("[data-ajuda-deteccao]")).to_be_visible()
    tela.capturar(pagina, "deteccao-pronta")

    # Nenhum pedido a outra origem; o motor veio, uma vez cada arquivo (SC-2754).
    origem = tela.servidor.url
    assert [url for url in pedidos if not url.startswith((origem, "blob:", "data:"))] == []
    for arquivo in (
        "vision_bundle.mjs",
        "vision_wasm_internal.js",
        "vision_wasm_internal.wasm",
        "face_landmarker-float16-1.task",
    ):
        assert sum(arquivo in url for url in pedidos) == 1, arquivo

    pagina.get_by_role("button", name="Começar a gravar").click()
    proximo = pagina.locator("[data-proximo]")
    expect(pagina.locator("[data-passo-rotulo]")).to_have_text("Passo 1 de 4")
    pagina.wait_for_timeout(600)
    proximo.click()
    expect(pagina.locator("[data-passo-titulo]")).to_have_text("Perfil esquerdo")
    # Sem rosto, nada avança sozinho e nada aparece (FR-8014, UX-923).
    pagina.wait_for_timeout(2_000)
    expect(pagina.locator("[data-passo-titulo]")).to_have_text("Perfil esquerdo")
    expect(pagina.locator("[data-confirmacao]")).to_be_hidden()
    proximo.click()
    expect(pagina.locator("[data-passo-titulo]")).to_have_text("Perfil direito")
    pagina.wait_for_timeout(600)
    proximo.click()
    pagina.wait_for_timeout(600)
    proximo.click()
    expect(pagina.get_by_role("heading", name="Assista antes de enviar")).to_be_visible()

    # "Gravar de novo" volta ao palco com o mesmo motor: nada é baixado de novo, e a detecção já
    # está pronta (achado da revisão do #573, que recriava e reaquecia o motor a cada tomada).
    pagina.get_by_role("button", name="Gravar de novo").click()
    expect(pagina.get_by_role("button", name="Começar a gravar")).to_be_visible()
    expect(raiz).to_have_attribute("data-deteccao", "pronta")
    expect(pagina.locator("[data-aviso-deteccao]")).to_be_visible()
    for arquivo in (
        "vision_bundle.mjs",
        "vision_wasm_internal.js",
        "vision_wasm_internal.wasm",
        "face_landmarker-float16-1.task",
    ):
        assert sum(arquivo in url for url in pedidos) == 1, arquivo


def test_prefiro_avancar_so_tocando_desliga_a_deteccao(
    tela, gestor, api_client, manager_headers, settings
):
    """176, FR-8005, D-003: o aviso vira a confirmação da escolha, e nada avança sozinho."""
    settings.DEBUG = True
    settings.VERIFICACAO_DETECCAO_DO_GIRO = True
    cenario = montar_com_video(gestor, api_client, manager_headers, seed=17620, quantas=2)
    maria = cenario["inscricoes"][0]
    pagina = tela.candidato(maria, viewport=CELULAR)
    _ate_o_palco(tela, pagina, cenario, maria, imagem_de_teste=True)
    raiz = pagina.locator("[data-verificacao]")
    expect(raiz).to_have_attribute("data-deteccao", "simulada")
    # O aviso fica no topo do painel do preparo, à vista sem rolar no celular (US3).
    assert _na_tela(pagina, pagina.get_by_role("button", name="Prefiro avançar só tocando"))
    pagina.get_by_role("button", name="Prefiro avançar só tocando").click()
    expect(raiz).to_have_attribute("data-deteccao", "recusada")
    expect(pagina.locator("[data-aviso-deteccao]")).to_contain_text("Combinado")
    expect(pagina.locator("[data-ajuda-deteccao]")).to_be_hidden()
    pagina.get_by_role("button", name="Começar a gravar").click()
    pagina.wait_for_timeout(600)
    pagina.locator("[data-proximo]").click()
    expect(pagina.locator("[data-passo-titulo]")).to_have_text("Perfil esquerdo")
    # O vulto gira à esquerda entre 3 e 5 segundos do ciclo: em 11 segundos ele passou por lá.
    pagina.wait_for_timeout(11_000)
    expect(pagina.locator("[data-passo-titulo]")).to_have_text("Perfil esquerdo")


@pytest.mark.parametrize("viewport", [CELULAR, DESKTOP], ids=["375", "1280"])
def test_com_a_imagem_de_teste_os_perfis_avancam_sozinhos(
    tela, gestor, api_client, manager_headers, settings, viewport
):
    """176, SC-2750, SC-2752; FR-8011 a FR-8013, FR-8040.

    A imagem de teste gira o vulto, e a detecção simulada lê o giro desenhado: dois toques além de
    "Começar a gravar" — o "Próximo" do documento e o "Terminar a gravação" —, e o pedido de envio
    com as mesmas chaves e marcas que o gravado pelo toque."""
    settings.DEBUG = True
    settings.VERIFICACAO_DETECCAO_DO_GIRO = True
    cenario = montar_com_video(gestor, api_client, manager_headers, seed=17630, quantas=2)
    maria = cenario["inscricoes"][0]
    pagina = tela.candidato(maria, viewport=viewport)
    pedidos = []
    pagina.on(
        "request",
        lambda pedido: (
            pedidos.append(pedido.post_data)
            if pedido.method == "POST" and pedido.url.endswith("/envios")
            else None
        ),
    )
    motor = []
    pagina.on(
        "request", lambda pedido: motor.append(pedido.url) if "deteccao/" in pedido.url else None
    )

    _ate_o_palco(tela, pagina, cenario, maria, imagem_de_teste=True)
    expect(pagina.locator("[data-verificacao]")).to_have_attribute("data-deteccao", "simulada")
    expect(pagina.locator("[data-oval]")).to_have_attribute("data-rosto", "dentro", timeout=15_000)
    expect(pagina.locator("[data-guia-do-oval]")).to_have_text(
        "Rosto no oval. Ele não aparece no vídeo."
    )
    tela.capturar(pagina, "deteccao-rosto-no-oval")
    toques = 0
    pagina.get_by_role("button", name="Começar a gravar").click()
    pagina.wait_for_timeout(600)
    pagina.locator("[data-proximo]").click()
    toques += 1
    expect(pagina.locator("[data-passo-titulo]")).to_have_text("Perfil esquerdo")
    confirmacao = pagina.locator("[data-confirmacao]")
    expect(confirmacao).to_have_text("Perfil esquerdo visto", timeout=15_000)
    tela.capturar(pagina, "deteccao-perfil-visto")
    expect(pagina.locator("[data-passo-titulo]")).to_have_text("Perfil direito", timeout=5_000)
    expect(pagina.locator("[data-anuncio]")).to_contain_text("Perfil esquerdo visto. Passo 3 de 4")
    expect(pagina.locator("[data-passo-titulo]")).to_have_text("De frente", timeout=20_000)
    expect(pagina.locator("[data-anuncio]")).to_contain_text("Perfil direito visto. Passo 4 de 4")
    # O passo de frente não termina sozinho (FR-8013).
    pagina.wait_for_timeout(1_500)
    expect(pagina.locator("[data-passo-titulo]")).to_have_text("De frente")
    pagina.locator("[data-proximo]").click()
    toques += 1
    assert toques == 2
    expect(pagina.get_by_role("heading", name="Assista antes de enviar")).to_be_visible()
    pagina.get_by_role("button", name="Enviar este vídeo").click()
    pagina.wait_for_url("**/comprovante*", timeout=30_000)
    corpo = json.loads(pedidos[-1])
    assert set(corpo) == {"tamanho", "formato", "duracao", "marcas", "roteiro", "maioridade"}
    assert corpo["roteiro"] == roteiro.VERSAO
    assert [marca["passo"] for marca in corpo["marcas"]] == list(roteiro.CHAVES)
    assert all(set(marca) == {"passo", "instante"} for marca in corpo["marcas"])
    # A imagem de teste não baixa o motor (research T-010).
    assert motor == []
