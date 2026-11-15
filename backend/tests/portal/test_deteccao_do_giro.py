"""A detecção do giro do rosto na página da gravação (176).

FR-8003 a FR-8006, FR-8020, FR-8022, FR-8023, FR-8030, FR-8031; SC-2751, SC-2756. O servidor não
detecta nada: o que se testa aqui é **se** a página oferece a detecção, de onde o motor vem, o que a
política de conteúdo abre e o que **não** muda — o contrato do envio. O comportamento no aparelho é
de `tests/javascript/deteccao.test.js` e da jornada no navegador.
"""

import hashlib
import re

import pytest
from django.contrib.staticfiles import finders
from django.urls import reverse

from processo_seletivo.portal import deteccao
from processo_seletivo.shared.politica_de_conteudo import (
    CABECALHO,
    POLITICA_COM_MIDIA_LOCAL,
    POLITICA_COM_MIDIA_LOCAL_E_WASM,
)
from processo_seletivo.verificacao.domain import roteiro
from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.verificacao import enviar_video, montar_com_video

# --- o manifesto e a chave, sem banco ---------------------------------------------------------


@pytest.mark.parametrize("caminho", sorted(deteccao.ARQUIVOS))
def test_cada_arquivo_do_motor_tem_o_resumo_do_manifesto(caminho):
    """FR-8023: o arquivo servido é o do pacote publicado, sem alteração."""
    arquivo = finders.find(caminho)
    assert arquivo, caminho
    with open(arquivo, "rb") as f:
        assert hashlib.sha256(f.read()).hexdigest() == deteccao.ARQUIVOS[caminho]


def test_os_passos_que_giram_sao_os_dois_perfis_do_roteiro():
    """D-002: só os perfis avançam sozinhos; o documento e o passo de frente, pelo toque."""
    assert set(deteccao.GIRO_DO_PASSO) <= set(roteiro.CHAVES)
    assert deteccao.GIRO_DO_PASSO == {"perfil-esquerdo": "esquerda", "perfil-direito": "direita"}


@pytest.mark.parametrize(
    ("video", "propria", "esperado"),
    [(True, True, True), (True, False, False), (False, True, False), (False, False, False)],
)
def test_a_deteccao_exige_as_duas_chaves(settings, video, propria, esperado):
    """FR-8020, D-004: a chave própria só vale debaixo da do vídeo."""
    settings.VERIFICACAO_POR_VIDEO = video
    settings.VERIFICACAO_DETECCAO_DO_GIRO = propria
    assert deteccao.ligada() is esperado


def test_a_politica_com_wasm_difere_so_na_compilacao():
    """FR-8022: `'wasm-unsafe-eval'` em `script-src`, e nenhuma outra diretiva muda."""
    sem = dict(d.split(" ", 1) for d in POLITICA_COM_MIDIA_LOCAL.split("; "))
    com = dict(d.split(" ", 1) for d in POLITICA_COM_MIDIA_LOCAL_E_WASM.split("; "))
    assert com.pop("script-src") == "'self' 'wasm-unsafe-eval'"
    assert sem.pop("script-src") == "'self'"
    assert com == sem
    assert "unsafe-eval'" not in POLITICA_COM_MIDIA_LOCAL_E_WASM.replace("wasm-unsafe-eval", "")
    assert "unsafe-inline" not in POLITICA_COM_MIDIA_LOCAL_E_WASM


# --- a página ------------------------------------------------------------------------------


@pytest.fixture
def cenario(db, raiz_de_arquivos, gestor, api_client, manager_headers):
    return montar_com_video(gestor, api_client, manager_headers, seed=17600, quantas=2)


def _pagina(cenario, inscricao=None):
    inscricao = inscricao or cenario["inscricoes"][0]
    return reverse("portal:verificacao", args=[inscricao.id, cenario["hetero"]])


def _abrir(client, cenario):
    entrar_como_titular(client, cenario["inscricoes"][0])
    resposta = client.get(_pagina(cenario))
    assert resposta.status_code == 200
    return resposta


FRASES = (
    "A tela acompanha o giro do seu rosto para passar sozinha aos passos seguintes. Isso acontece "
    "só neste aparelho: nada dessa leitura é enviado nem guardado.",
    "Prefiro avançar só tocando",
    "Nos dois perfis, a tela passa sozinha quando vê o giro. Você também pode tocar em «Próximo».",
)


def test_sem_a_chave_a_pagina_e_a_da_174(cenario, client, settings):
    """SC-2751, FR-8020: nenhum gancho, nenhum script, nenhuma frase, e a política de hoje."""
    settings.VERIFICACAO_DETECCAO_DO_GIRO = False
    resposta = _abrir(client, cenario)
    corpo = resposta.content.decode()
    assert resposta[CABECALHO] == POLITICA_COM_MIDIA_LOCAL
    assert "data-deteccao" not in corpo
    assert "deteccao.js" not in corpo
    assert "data-giro" not in corpo
    assert "data-confirmacao" not in corpo
    for frase in FRASES:
        assert frase not in corpo


def test_com_a_chave_a_pagina_traz_o_motor_e_as_frases(cenario, client, settings):
    """FR-8004, FR-8005, FR-8022, FR-8023; contracts/pagina.md."""
    settings.VERIFICACAO_DETECCAO_DO_GIRO = True
    resposta = _abrir(client, cenario)
    corpo = resposta.content.decode()
    assert resposta[CABECALHO] == POLITICA_COM_MIDIA_LOCAL_E_WASM
    for chave, caminho in (
        ("motor", deteccao.MOTOR),
        ("carregador", deteccao.CARREGADOR),
        ("binario", deteccao.BINARIO),
        ("modelo", deteccao.MODELO),
    ):
        assert re.search(
            rf'data-deteccao-{chave}="/static/{re.escape(caminho)}\?v=\w{{12}}"', corpo
        )
    # O script da detecção antes do da gravação, que o consome.
    assert corpo.index("portal/deteccao.js") < corpo.index("portal/gravacao.js")
    for frase in FRASES:
        assert frase in corpo
    # Tudo escondido até o motor ficar pronto (UX-923).
    assert re.search(r'class="aviso-da-deteccao" data-aviso-deteccao hidden', corpo)
    assert re.search(r"data-ajuda-deteccao hidden", corpo)
    assert re.search(r"data-confirmacao hidden", corpo)


def test_so_os_dois_perfis_levam_o_lado_do_giro(cenario, client, settings):
    """D-002, D-005."""
    settings.VERIFICACAO_DETECCAO_DO_GIRO = True
    corpo = _abrir(client, cenario).content.decode()
    giros = dict(re.findall(r'data-passo="([\w-]+)"[^>]*?data-giro="(\w+)"', corpo))
    assert giros == {"perfil-esquerdo": "esquerda", "perfil-direito": "direita"}


def test_o_motor_so_vale_na_gravacao(cenario, client, settings):
    """FR-8003, SC-2756: nem o comprovante nem o acompanhamento compilam WebAssembly."""
    settings.VERIFICACAO_DETECCAO_DO_GIRO = True
    maria = cenario["inscricoes"][0]
    enviar_video(maria, cenario["hetero"])
    entrar_como_titular(client, maria)
    comprovante = client.get(
        reverse("portal:verificacao-comprovante", args=[maria.id, cenario["hetero"]])
    )
    acompanhamento = client.get(reverse("portal:acompanhamento", args=[maria.id]))
    for resposta in (comprovante, acompanhamento):
        assert resposta.status_code == 200
        assert "wasm-unsafe-eval" not in resposta[CABECALHO]
        assert "deteccao.js" not in resposta.content.decode()


def test_a_chave_da_deteccao_sem_a_do_video_nao_abre_nada(cenario, client, settings):
    """FR-8020: a do vídeo continua mandando; desligada, a rota é inexistente, como na 166."""
    settings.VERIFICACAO_POR_VIDEO = False
    settings.VERIFICACAO_DETECCAO_DO_GIRO = True
    entrar_como_titular(client, cenario["inscricoes"][0])
    assert client.get(_pagina(cenario)).status_code == 404


def test_nenhuma_frase_chama_a_deteccao_de_biometria_ou_prova_de_vida(cenario, client, settings):
    """FR-8006: a detecção é descrita pelo que faz, e não como conferência de identidade."""
    settings.VERIFICACAO_DETECCAO_DO_GIRO = True
    corpo = _abrir(client, cenario).content.decode().lower()
    texto = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", " ", corpo, flags=re.S))
    for termo in (
        "prova de vida",
        "biometria",
        "biométric",
        "reconhecimento",
        "verificação facial",
    ):
        assert termo not in texto, termo


def test_o_video_nao_guarda_nada_da_deteccao(cenario, client, settings):
    """FR-8030, FR-8031: o contrato do envio é o da 166, e nenhum campo do vídeo diz como um passo
    avançou — pelo giro ou pelo toque."""
    settings.VERIFICACAO_DETECCAO_DO_GIRO = True
    maria = cenario["inscricoes"][0]
    video = enviar_video(maria, cenario["hetero"])
    campos = {campo.name for campo in type(video)._meta.get_fields()}
    assert not {c for c in campos if {"deteccao", "giro", "detectado"} & set(c.split("_"))}
