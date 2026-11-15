"""A página de gravação, o comprovante e o acesso no acompanhamento (166, US2, US5).

FR-7100, FR-7107, FR-7110, FR-7117, FR-7145; SC-2376. O acesso no acompanhamento é o degrau da
`171` desde a entrega 4 (FR-7312 a FR-7314; SC-2415).
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
    """FR-7145, absorvido pelo degrau da `171` (FR-7312, FR-7314): o passo leva à página."""
    maria = cenario["inscricoes"][0]
    entrar_como_titular(client, maria)
    corpo = client.get(reverse("portal:acompanhamento", args=[maria.id])).content.decode()
    assert "Falta um passo seu" in corpo
    assert "As duas formas valem igual." in corpo
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
    """FR-7100, SC-2376; e a `171` (FR-7313, SC-2415): o degrau é o do rito sem vídeo."""
    maria = cenario["inscricoes"][0]
    entrar_como_titular(client, maria)
    settings.VERIFICACAO_POR_VIDEO = False
    assert client.get(_pagina(cenario)).status_code == 404
    corpo = client.get(reverse("portal:acompanhamento", args=[maria.id])).content.decode()
    assert "Falta um passo seu" in corpo
    assert _pagina(cenario) not in corpo
    assert "vídeo" not in corpo.lower()


def test_com_a_chave_desligada_quem_enviou_aguarda_o_resultado(cenario, client, settings):
    """FR-7313; achado U1 do `/speckit-analyze` da `171`: o vídeo enviado continua sendo fato."""
    maria = cenario["inscricoes"][0]
    enviar_video(maria, cenario["hetero"])
    settings.VERIFICACAO_POR_VIDEO = False
    entrar_como_titular(client, maria)
    corpo = client.get(reverse("portal:acompanhamento", args=[maria.id])).content.decode()
    assert "Aguardando o resultado" in corpo
    assert "Falta um passo seu" not in corpo
    assert "vídeo" not in corpo.lower()


# --- O polimento da 174 ---------------------------------------------------------------------------


def _escolha(cenario, client):
    maria = cenario["inscricoes"][0]
    entrar_como_titular(client, maria)
    return client.get(_pagina(cenario)).content.decode()


def test_a_pagina_leva_os_nomes_publicados_e_nao_o_texto_fixo(cenario, client):
    """FR-7853 da 174: o título é o nome da Etapa, e a frase cita a Modalidade pelo nome dela."""
    corpo = _escolha(cenario, client)
    assert "<h1>Heteroidentificação</h1>" in corpo
    assert "Você se inscreveu em Pretos e pardos" in corpo
    assert "pessoas pretas e pardas" not in corpo
    assert 'class="jornada"' in corpo
    assert 'data-momento="preparar" aria-current="step"' in corpo


def test_a_escolha_tem_dois_cartoes_iguais_e_o_preparo_pede_o_documento(cenario, client):
    """FR-7860, FR-7863, FR-7864 e D-010 da 174: nenhuma frase da 166 sai, e o documento entrou."""
    corpo = _escolha(cenario, client)
    assert corpo.count('<article class="forma"') == 2
    assert corpo.count('class="forma-acao"') == 2
    assert "Prazo:" in corpo
    assert "O seu documento de identidade com foto." in corpo
    for frase in (
        "A comissão olha só a sua aparência.",
        "boné ou filtro",
        "Não há pressa em nenhum passo.",
        "Só a comissão da verificação assiste ao vídeo",
        "O vídeo fica guardado pelo prazo",
        "Isso não é reprovação.",
    ):
        assert frase in corpo, frase


def test_a_recusa_da_idade_nasce_escondida_e_o_palco_e_uma_tela_so(cenario, client):
    """FR-7854, FR-7865 e FR-7866 da 174."""
    corpo = _escolha(cenario, client)
    assert "data-erro-maioridade hidden" in corpo
    assert 'data-tela="palco" data-estado="preparo" hidden' in corpo
    assert corpo.count("<video") == 2  # a prévia do palco e a revisão
    saem = ("data-ir-gravar", "data-previa-gravacao", "data-checagem-camera", "Abrir a câmera")
    for gancho in saem:
        assert gancho not in corpo, gancho
    assert corpo.count('data-ir="nao-consigo"') >= 3


def test_o_acompanhamento_tem_o_prazo_em_linha_propria_e_a_acao_que_diz_para_onde_leva(
    cenario, client
):
    """FR-7856 a FR-7858 da 174."""
    maria = cenario["inscricoes"][0]
    entrar_como_titular(client, maria)
    corpo = client.get(reverse("portal:acompanhamento", args=[maria.id])).content.decode()
    assert 'class="prazo-do-passo"><strong>Prazo:</strong> até ' in corpo
    assert "Escolher entre vídeo e entrevista ao vivo" in corpo
    assert "Ver como funciona" not in corpo
    assert "O vídeo pode ser enviado até" not in corpo
    assert '<svg class="icone"' in corpo
    assert corpo.index("prazo-do-passo") < corpo.index("<h3>Por quê</h3>")


def test_o_comprovante_abre_pela_confirmacao(cenario, client):
    """FR-7882 e FR-7883 da 174; a FR-7123 da 166 continua: os dados estão lá, no fim."""
    maria = cenario["inscricoes"][0]
    video = enviar_video(maria, cenario["hetero"], duracao=72.3)
    entrar_como_titular(client, maria)
    rota = reverse("portal:verificacao-comprovante", args=[maria.id, cenario["hetero"]])
    corpo = client.get(rota).content.decode()
    confirmacao = corpo.index("Seu vídeo foi enviado")
    agora = corpo.index("E agora?")
    dados = corpo.index("Dados para conferência")
    assert confirmacao < agora < dados
    assert str(video.id) in corpo[dados:]
    assert video.sha256 in corpo[dados:]
    assert "Código de conferência do arquivo (SHA-256)" in corpo
    assert "1 min 12 s" in corpo
    assert "segundos" not in corpo
