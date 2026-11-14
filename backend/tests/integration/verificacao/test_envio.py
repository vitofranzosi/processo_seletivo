"""O envio do vídeo em partes, e a conclusão que o torna vídeo (166, US2, FR-7107 a FR-7126).

Contra PostgreSQL, com o MP4 sintético: nenhum vídeo real (research T-007).
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.verificacao.application import disponibilidade, envio
from processo_seletivo.verificacao.domain import roteiro
from processo_seletivo.verificacao.models import EnvioDoVideo, VideoDaVerificacao
from tests.fixtures import videos_sinteticos
from tests.fixtures.verificacao import (
    enviar_pelo_portal,
    enviar_video,
    identidade_de,
    marcas,
    montar_com_video,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def cenario(raiz_de_arquivos, gestor, api_client, manager_headers):
    return montar_com_video(gestor, api_client, manager_headers, seed=6601)


def _iniciar(inscricao, etapa, **mudancas):
    argumentos = {
        "identidade": identidade_de(inscricao),
        "inscricao_id": inscricao.id,
        "etapa_id": etapa,
        "tamanho": 1000,
        "formato": "video/mp4",
        "duracao": 4.8,
        "marcas": marcas(4.8),
        "roteiro_versao": roteiro.VERSAO,
        "maioridade": True,
    }
    argumentos.update(mudancas)
    return envio.iniciar(**argumentos)


def test_o_envio_em_partes_vira_video_com_o_resumo_do_aparelho(cenario):
    """SC-2371: o resumo final é o do aparelho, e o vídeo guarda o que a conferência leu."""
    maria = cenario["inscricoes"][0]
    dados = videos_sinteticos.mp4(4.8, corpo=50_000)
    video = enviar_video(maria, cenario["hetero"], dados=dados, parte=7_000)

    assert video.sha256 == videos_sinteticos.resumo(dados)
    assert video.tamanho == len(dados)
    assert float(video.duracao) == pytest.approx(4.8)
    assert video.formato == "video/mp4"
    assert video.roteiro == roteiro.VERSAO
    assert [m["passo"] for m in video.marcas] == list(roteiro.CHAVES)
    assert video.declarou_maioridade is True
    assert not EnvioDoVideo.objects.exists()
    with open(envio.caminho(video.arquivo), "rb") as arquivo:
        assert arquivo.read() == dados


def test_a_parte_fora_do_deslocamento_responde_onde_retomar(cenario):
    """FR-7118, FR-7119: a retomada continua do recebido, e não do começo."""
    maria = cenario["inscricoes"][0]
    dados = videos_sinteticos.mp4(4.8, corpo=30_000)
    novo = _iniciar(maria, cenario["hetero"], tamanho=len(dados))
    identidade = identidade_de(maria)
    comum = {
        "identidade": identidade,
        "inscricao_id": maria.id,
        "etapa_id": cenario["hetero"],
        "envio_id": novo.id,
    }
    assert envio.receber_parte(deslocamento=0, dados=dados[:10_000], **comum) == 10_000
    with pytest.raises(envio.ForaDoDeslocamento) as fora:
        envio.receber_parte(deslocamento=0, dados=dados[:10_000], **comum)
    assert fora.value.deslocamento == 10_000
    assert envio.consultar(**comum).recebido == 10_000
    envio.receber_parte(deslocamento=10_000, dados=dados[10_000:], **comum)
    video = envio.concluir(sha256=videos_sinteticos.resumo(dados), correlation_id="t", **comum)
    assert video.sha256 == videos_sinteticos.resumo(dados)


@pytest.mark.parametrize(
    ("dados", "codigo"),
    [
        (b"%PDF-1.7\n" + b"0" * 2000, "formato"),
        (videos_sinteticos.mp4(240.0), "duracao"),
    ],
    ids=["pdf-com-tipo-de-video", "acima-do-teto-no-conteiner"],
)
def test_a_conclusao_confere_o_conteiner_e_a_duracao(cenario, dados, codigo):
    """FR-7120: o servidor confere de novo, e a extensão ou o tipo declarado não bastam."""
    maria = cenario["inscricoes"][0]
    with pytest.raises(DomainError) as recusa:
        enviar_video(maria, cenario["hetero"], dados=dados)
    assert recusa.value.code == codigo
    assert not VideoDaVerificacao.objects.exists()


def test_resumo_divergente_e_recusado(cenario):
    maria = cenario["inscricoes"][0]
    with pytest.raises(DomainError) as recusa:
        enviar_video(maria, cenario["hetero"], sha="0" * 64)
    assert recusa.value.code == "resumo"


@pytest.mark.parametrize(
    ("mudancas", "codigo"),
    [
        ({"maioridade": False}, "maioridade"),
        ({"maioridade": None}, "maioridade"),
        ({"formato": "video/quicktime"}, "formato"),
        ({"duracao": roteiro.TETO_SEGUNDOS + 5}, "duracao"),
        ({"tamanho": 10**12}, "tamanho"),
        ({"roteiro_versao": "outro"}, "marcas"),
        ({"marcas": []}, "marcas"),
    ],
)
def test_a_declaracao_do_inicio_e_conferida(cenario, mudancas, codigo):
    """FR-7109 (maioridade, sem data de nascimento), FR-7112, FR-7120, FR-7122."""
    with pytest.raises(DomainError) as recusa:
        _iniciar(cenario["inscricoes"][0], cenario["hetero"], **mudancas)
    assert recusa.value.code == codigo


def test_quem_nao_e_titular_recebe_a_recusa_indistinguivel(cenario):
    """FR-7110: a inscrição de outra pessoa responde como a que não existe."""
    maria, joao = cenario["inscricoes"][:2]
    with pytest.raises(DomainError) as alheia:
        _iniciar(maria, cenario["hetero"], identidade=identidade_de(joao))
    with pytest.raises(DomainError) as inexistente:
        _iniciar(maria, cenario["hetero"], inscricao_id=cenario["analise"])
    assert alheia.value.code == inexistente.value.code == "not_found"
    assert alheia.value.status == inexistente.value.status == 404


def test_etapa_que_nao_admite_o_video_responde_como_inexistente(cenario):
    with pytest.raises(DomainError) as recusa:
        _iniciar(cenario["inscricoes"][0], cenario["analise"])
    assert recusa.value.status == 404


def test_com_a_chave_desligada_nada_responde(cenario, settings):
    """FR-7100, SC-2376."""
    settings.VERIFICACAO_POR_VIDEO = False
    with pytest.raises(DomainError) as recusa:
        _iniciar(cenario["inscricoes"][0], cenario["hetero"])
    assert recusa.value.status == 404


def test_iniciar_de_novo_descarta_o_envio_incompleto(cenario):
    """FR-7125: um envio aberto por inscrição e Etapa."""
    maria = cenario["inscricoes"][0]
    primeiro = _iniciar(maria, cenario["hetero"])
    segundo = _iniciar(maria, cenario["hetero"])
    assert list(EnvioDoVideo.objects.values_list("id", flat=True)) == [segundo.id]
    import os

    assert not os.path.exists(envio.caminho(primeiro.arquivo))


def test_a_troca_antes_da_abertura_substitui_e_preserva_o_anterior(cenario):
    """FR-7124: o novo é o vigente, o anterior continua registrado."""
    maria = cenario["inscricoes"][0]
    primeiro = enviar_video(maria, cenario["hetero"])
    segundo = enviar_video(maria, cenario["hetero"], dados=videos_sinteticos.mp4(6.0), duracao=6.0)
    assert segundo.substitui_id == primeiro.id
    vigente = disponibilidade.video_vigente(
        edital=cenario["edital"], etapa_id=cenario["hetero"], inscricao_id=maria.id
    )
    assert vigente.id == segundo.id
    assert VideoDaVerificacao.objects.count() == 2


def test_parecer_ao_vivo_concluido_antes_fecha_o_video(cenario, gestor):
    """FR-7107: a comissão já está vendo a pessoa ao vivo."""
    from tests.fixtures.deliberacao import concluir_pareceres, distribuir_na_hetero

    maria = cenario["inscricoes"][0]
    distribuir_na_hetero(cenario, gestor, [maria], chave="dist-6601")
    concluir_pareceres(cenario, maria, {"ana": "FAVORAVEL"})
    with pytest.raises(DomainError) as recusa:
        _iniciar(maria, cenario["hetero"])
    assert recusa.value.code == "indisponivel"


def test_fora_do_periodo_nao_comeca(raiz_de_arquivos, gestor, api_client, manager_headers):
    agora = timezone.now()
    cenario = montar_com_video(
        gestor,
        api_client,
        manager_headers,
        seed=6602,
        inicio=agora - timedelta(days=3),
        fim=agora - timedelta(days=2),
    )
    with pytest.raises(DomainError) as recusa:
        _iniciar(cenario["inscricoes"][0], cenario["hetero"])
    assert recusa.value.code == "indisponivel"
    situacao = disponibilidade.situacao(
        inscricao=cenario["inscricoes"][0],
        etapa=_etapa(cenario),
        conteudo=_conteudo(cenario),
    )
    assert situacao.estado == disponibilidade.AO_VIVO


def _conteudo(cenario):
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    return conteudo_vigente(cenario["edital"])


def _etapa(cenario):
    return next(e for e in _conteudo(cenario)["stages"] if e["id"] == str(cenario["hetero"]))


def test_inscricao_fora_do_alcance_nao_ve_a_verificacao(
    raiz_de_arquivos, gestor, api_client, manager_headers
):
    """A ampla concorrência e a PCD não fazem autodeclaração de cor (FR-7107)."""
    cenario = montar_com_video(gestor, api_client, manager_headers, seed=6603, quantas=1)
    pedro = cenario["inscricoes"][0]
    # Em memória: a inscrição enviada é imutável no banco (A-03), e a pergunta é só a do alcance.
    pedro.modality_id = None
    situacao = disponibilidade.situacao(
        inscricao=pedro, etapa=_etapa(cenario), conteudo=_conteudo(cenario)
    )
    assert situacao is None


def test_o_envio_pelas_rotas_do_portal(cenario, client):
    """As rotas JSON do portal, com a sessão do titular, chegam ao comprovante."""
    maria = cenario["inscricoes"][0]
    fim, _rotas = enviar_pelo_portal(
        client,
        maria,
        cenario["hetero"],
        dados=videos_sinteticos.mp4(5.0, corpo=40_000),
        parte=9_000,
    )
    assert fim.status_code == 201, fim.content
    assert fim.json()["comprovante"].endswith("/comprovante")
    resposta = client.get(fim.json()["comprovante"])
    assert resposta.status_code == 200
    video = VideoDaVerificacao.objects.get()
    assert video.sha256 in resposta.content.decode()


def test_a_parte_de_8_mib_passa_sem_mexer_no_limite_global(cenario, client, settings):
    """FR-7118, achado 1 do code review: o corpo cru não passa pelo `DATA_UPLOAD_MAX_MEMORY_SIZE`.

    Ler `request.body` aplicava a todo corpo os 2,5 MB do Django, e toda parte acima disso voltava
    400 — com partes de 8 MiB, nenhum vídeo real chegava. O limite global continua o mesmo.
    """
    assert settings.DATA_UPLOAD_MAX_MEMORY_SIZE < envio.PARTE_MAXIMA
    maria = cenario["inscricoes"][0]
    dados = videos_sinteticos.mp4(30.0, corpo=envio.PARTE_MAXIMA + 300_000)
    fim, _rotas = enviar_pelo_portal(
        client, maria, cenario["hetero"], dados=dados, duracao=30.0, parte=envio.PARTE_MAXIMA
    )
    assert fim.status_code == 201, fim.content
    assert VideoDaVerificacao.objects.get().tamanho == len(dados)


def test_a_parte_acima_de_8_mib_e_recusada_antes_de_ler(cenario, client):
    from django.urls import reverse

    from tests.fixtures.divulgacao import entrar_como_titular

    maria = cenario["inscricoes"][0]
    novo = _iniciar(maria, cenario["hetero"], tamanho=envio.PARTE_MAXIMA + 10)
    entrar_como_titular(client, maria)
    rota = reverse("portal:verificacao-envio-partes", args=[maria.id, cenario["hetero"], novo.id])
    resposta = client.put(
        f"{rota}?deslocamento=0",
        data=b"\0" * (envio.PARTE_MAXIMA + 1),
        content_type="application/octet-stream",
    )
    assert resposta.status_code == 413
    assert (
        envio.consultar(
            identidade=identidade_de(maria),
            inscricao_id=maria.id,
            etapa_id=cenario["hetero"],
            envio_id=novo.id,
        ).recebido
        == 0
    )


def test_o_video_que_chega_ao_teto_comeca_a_enviar(cenario):
    """Achado 3 do code review do #547: o temporizador passa do teto por milissegundos.

    A mesma folga da conclusão vale no início; acima dela, a recusa continua.
    """
    maria = cenario["inscricoes"][0]
    teto = roteiro.TETO_SEGUNDOS
    marcas_no_teto = marcas(teto)
    assert _iniciar(maria, cenario["hetero"], duracao=teto + 0.004, marcas=marcas_no_teto)
    with pytest.raises(DomainError) as recusa:
        _iniciar(maria, cenario["hetero"], duracao=teto + 1.5, marcas=marcas_no_teto)
    assert recusa.value.code == "duracao"


def test_a_falha_depois_da_conferencia_nao_deixa_arquivo_orfao(cenario, monkeypatch):
    """Achado 4 do code review do #547: o arquivo só se move depois dos registros.

    Uma falha ao registrar o recebimento desfaz a transação; o envio continua inteiro, o temporário
    continua no lugar, e a nova tentativa conclui — antes, caía em `FileNotFoundError`.
    """
    import os

    from processo_seletivo import auditoria

    maria = cenario["inscricoes"][0]
    identidade = identidade_de(maria)
    dados = videos_sinteticos.mp4(4.8)
    novo = _iniciar(maria, cenario["hetero"], tamanho=len(dados))
    comum = {
        "identidade": identidade,
        "inscricao_id": maria.id,
        "etapa_id": cenario["hetero"],
        "envio_id": novo.id,
    }
    envio.receber_parte(deslocamento=0, dados=dados, **comum)

    def falha(**_):
        raise RuntimeError("a trilha caiu")

    monkeypatch.setattr(auditoria.application, "record_event", falha)
    with pytest.raises(RuntimeError):
        envio.concluir(sha256=videos_sinteticos.resumo(dados), correlation_id="t", **comum)
    assert os.path.exists(envio.caminho(novo.arquivo))
    assert envio.consultar(**comum).recebido == len(dados)
    assert not VideoDaVerificacao.objects.exists()
    monkeypatch.undo()
    video = envio.concluir(sha256=videos_sinteticos.resumo(dados), correlation_id="t", **comum)
    assert os.path.exists(envio.caminho(video.arquivo))
    assert not os.path.exists(envio.caminho(novo.arquivo))


def _etapa_publicada(cenario, **campos):
    return {**_etapa(cenario), **campos}


@pytest.mark.parametrize("como", ["retirada", "etapa-removida"])
def test_a_retificacao_nao_tira_o_video_de_quem_o_enviou(cenario, como):
    """FR-7105, e o achado 5 do code review do #547: retirar a admissão, ou remover a Etapa inteira,
    depois do primeiro vídeo recebido é recusado; antes dele, cabe."""
    from processo_seletivo.publicacoes.application.retificacoes import (
        _recusar_video_retirado_apos_recebido as recusar,
    )

    base = {"stages": [_etapa_publicada(cenario)]}
    depois = (
        {"stages": [_etapa_publicada(cenario, videoOption=False)]}
        if como == "retirada"
        else {"stages": []}
    )
    recusar(cenario["edital"], base, depois)
    enviar_video(cenario["inscricoes"][0], cenario["hetero"])
    with pytest.raises(DomainError) as recusa:
        recusar(cenario["edital"], base, depois)
    assert recusa.value.code == "video_ja_recebido"
