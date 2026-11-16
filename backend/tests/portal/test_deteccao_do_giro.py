"""A detecção do giro do rosto na página da gravação (176).

FR-8003 a FR-8006, FR-8020, FR-8022, FR-8023, FR-8030, FR-8031; SC-2751, SC-2756. O servidor não
detecta nada: o que se testa aqui é **se** a página oferece a detecção, de onde o motor vem, o que a
política de conteúdo abre e o que **não** muda — o contrato do envio. O comportamento no aparelho é
de `tests/javascript/deteccao.test.js` e da jornada no navegador.
"""

import hashlib
import re
from pathlib import Path

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
    """D-002: só os perfis giram; o documento avança pela contagem (D-009); a frente, pelo toque."""
    assert set(deteccao.GIRO_DO_PASSO) <= set(roteiro.CHAVES)
    assert deteccao.GIRO_DO_PASSO == {"perfil-esquerdo": "esquerda", "perfil-direito": "direita"}


def test_o_passo_do_documento_e_o_primeiro_do_roteiro():
    """FR-8060, D-009: o documento é o primeiro passo, e não é um dos que giram."""
    assert deteccao.PASSO_DO_DOCUMENTO == roteiro.CHAVES[0] == "documento"
    assert deteccao.PASSO_DO_DOCUMENTO not in deteccao.GIRO_DO_PASSO


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


# As frases da FR-8004 e da ajuda, revistas pela emenda (D-009): o documento também avança sozinho,
# e a pessoa lê que ele não é lido.
FRASES = (
    "A tela percebe quando você mostra o documento e quando vira o rosto, para passar sozinha aos "
    "passos seguintes. Ela não lê o documento. Isso acontece só neste aparelho: nada dessa leitura "
    "é enviado nem guardado.",
    "Prefiro avançar só tocando",
    "No documento e nos dois perfis, a tela passa sozinha. Você também pode tocar em «Próximo», "
    "no seu tempo.",
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
    assert "data-documento" not in corpo
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
    # O documento leva a sua marca, e só ele (emenda, FR-8060).
    assert re.findall(r'data-passo="([\w-]+)"[^>]*?data-documento[ >]', corpo) == ["documento"]


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
    """FR-8031: nenhum campo do vídeo diz como um passo avançou — pelo giro ou pelo toque."""
    settings.VERIFICACAO_DETECCAO_DO_GIRO = True
    maria = cenario["inscricoes"][0]
    video = enviar_video(maria, cenario["hetero"])
    campos = {campo.name for campo in type(video)._meta.get_fields()}
    assert not {c for c in campos if {"deteccao", "giro", "detectado"} & set(c.split("_"))}


# --- o que sai do aparelho, lido no fonte ------------------------------------------------------
#
# A jornada no navegador confere o pedido de envio de verdade, mas pula sem o grupo `navegador`.
# Os dois casos abaixo leem o fonte, como `test_armazenamento_no_navegador.py`: a propriedade é
# negativa ("nada da detecção sai"), e o fonte a prova em todo ambiente (achado da revisão do #573).

ESTATICOS = (
    Path(__file__).resolve().parents[2] / "processo_seletivo" / "portal" / "static" / "portal"
)


def _sem_comentarios(texto):
    return re.sub(r"//[^\n]*|/\*.*?\*/", "", texto, flags=re.S)


def test_o_corpo_do_envio_tem_so_os_campos_do_contrato_da_166():
    """FR-8030, FR-8031, SC-2752: os seis campos de sempre, e as marcas só com passo e instante."""
    fonte = _sem_comentarios((ESTATICOS / "gravacao.js").read_text(encoding="utf-8"))
    corpos = re.findall(r"JSON\.stringify\(\{(.*?)\}\)", fonte, flags=re.S)
    inicio = [c for c in corpos if "tamanho" in c]
    assert len(inicio) == 1, corpos
    campos = re.findall(r"(\w+)\s*:", inicio[0])
    assert campos == ["tamanho", "formato", "duracao", "marcas", "roteiro", "maioridade"]
    marcas = re.search(r"function marcasEmSegundos.*?return \{(.*?)\}", fonte, flags=re.S)
    assert re.findall(r"(\w+)\s*:", marcas.group(1)) == ["passo", "instante"]


def test_a_deteccao_nao_faz_pedido_de_rede():
    """FR-8000: o único pedido de `deteccao.js` é o `import()` do motor; nada de `fetch`,
    `XMLHttpRequest`, `sendBeacon` nem `WebSocket`, e nenhuma menção às rotas do envio."""
    fonte = _sem_comentarios((ESTATICOS / "deteccao.js").read_text(encoding="utf-8"))
    for proibido in ("fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "envios", "pedir("):
        assert proibido not in fonte, proibido


# --- o sinal do gesto (emenda de 15/11) ---------------------------------------------------------


def test_os_gestos_sao_de_passos_do_roteiro_e_a_frente_nao_tem():
    """FR-8050, D-008: o sinal é dos três passos de gesto; a frase do passo de frente é a fala."""
    from processo_seletivo.portal.verificacao import GESTO_DO_PASSO

    assert set(GESTO_DO_PASSO) <= set(roteiro.CHAVES)
    assert "frente" not in GESTO_DO_PASSO


@pytest.mark.parametrize("ligada", [False, True], ids=["sem-deteccao", "com-deteccao"])
def test_o_sinal_do_gesto_vale_com_ou_sem_a_deteccao(cenario, client, settings, ligada):
    """FR-8050, FR-8054, SC-2751: navegação, e não leitura do rosto — e decorativo para o leitor."""
    settings.VERIFICACAO_DETECCAO_DO_GIRO = ligada
    corpo = _abrir(client, cenario).content.decode()
    gestos = dict(re.findall(r'data-passo="([\w-]+)"[^>]*?data-gesto="(\w+)"', corpo))
    assert gestos == {
        "documento": "documento",
        "perfil-esquerdo": "esquerda",
        "perfil-direito": "direita",
    }
    assert re.search(r'class="gesto-do-passo" data-so-gravando aria-hidden="true"', corpo)
    for palavra in ("Sua esquerda", "Sua direita", "Mostre o documento"):
        assert palavra in corpo


# --- a fala e o microfone (emenda de 15/11) -------------------------------------------------------


@pytest.mark.parametrize("ligada", [False, True], ids=["sem-deteccao", "com-deteccao"])
def test_a_fala_e_o_microfone_valem_com_ou_sem_a_deteccao(cenario, client, settings, ligada):
    """FR-8070, FR-8073, FR-8080, FR-8083: a faixa da fala embaixo, a frase do preparo, e as duas
    barras do microfone — a do preparo, com a marca, e a do selo —, todas da página."""
    settings.VERIFICACAO_DETECCAO_DO_GIRO = ligada
    corpo = _abrir(client, cenario).content.decode()
    faixa_de_baixo = corpo[corpo.index('class="faixa-de-baixo"') :]
    assert faixa_de_baixo.index("data-fala-do-passo") < faixa_de_baixo.index("data-proximo")
    assert (
        "No último passo, você diz o seu nome e a frase da sua autodeclaração. Se preferir, "
        "mostre a frase escrita num papel, ou diga em Libras."
    ) in corpo
    assert "<meter" not in corpo
    assert corpo.count("data-volume") == 2
    assert corpo.count("data-marca-do-volume") == 1
    assert re.search(r'class="medidor-do-som" aria-hidden="true"', corpo)
    assert re.search(r'class="microfone-do-selo" aria-hidden="true"', corpo)
    # A frase do roteiro continua a mesma, e é dela que a faixa sai (D-010, a D-003 da 174).
    frente = roteiro.PASSOS[-1]
    assert frente.chave == "frente"
    assert f'data-texto="{frente.instrucao}"' in corpo.replace("&#x27;", "'")
