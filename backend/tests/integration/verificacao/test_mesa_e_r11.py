"""A comissão abre o vídeo e dá o parecer; o vídeo só confirma (166, US3, US4, US5).

FR-7124, FR-7127 a FR-7144; SC-2372, SC-2373, SC-2374. Contra PostgreSQL, com o MP4 sintético.
"""

import pytest
from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.models import Avaliacao, ConclusaoAvaliacao
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.verificacao.application import (
    abertura,
    disponibilidade,
    encaminhamento,
    ganchos,
)
from processo_seletivo.verificacao.models import AberturaDoVideo, EncaminhamentoAoVivo
from tests.conftest import ator_institucional
from tests.fixtures import videos_sinteticos
from tests.fixtures.deliberacao import (
    concluir_pareceres,
    consolidar_na,
    distribuir_na_hetero,
    na_hetero,
)
from tests.fixtures.mesa import concluir_como
from tests.fixtures.verificacao import enviar_video, montar_com_video
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db

PARECERISTAS = ("ana", "bruno", "carla")


@pytest.fixture
def cenario(raiz_de_arquivos, gestor, api_client, manager_headers):
    cenario = montar_com_video(gestor, api_client, manager_headers, seed=6610, quantas=2)
    distribuir_na_hetero(cenario, gestor, cenario["inscricoes"], chave="dist-6610")
    cenario["video"] = enviar_video(cenario["inscricoes"][0], cenario["hetero"])
    return cenario


def _pedido():
    pedido = RequestFactory().post("/")
    pedido.session = SessionStore()
    return pedido


def abrir_como(cenario, subject, inscricao=None):
    inscricao = inscricao or cenario["inscricoes"][0]
    return abertura.abrir_pela_comissao(
        _pedido(),
        ator=ator_institucional(subject),
        edital=cenario["edital"],
        etapa_id=cenario["hetero"],
        inscricao_id=inscricao.id,
        correlation_id="t",
    )


def pareceres_pelo_video(cenario, sentidos):
    for subject in sentidos:
        abrir_como(cenario, subject)
    return concluir_pareceres(cenario, cenario["inscricoes"][0], sentidos)


# --- A abertura ----------------------------------------------------------------------------


def test_concluir_pelo_video_exige_ter_aberto(cenario):
    """FR-7134: «Abra o vídeo antes de dar o parecer.»"""
    with pytest.raises(DomainError) as recusa:
        concluir_pareceres(cenario, cenario["inscricoes"][0], {"ana": "FAVORAVEL"})
    assert recusa.value.code == "video_nao_aberto"
    abrir_como(cenario, "ana")
    concluir_pareceres(cenario, cenario["inscricoes"][0], {"ana": "FAVORAVEL"})


def test_a_inscricao_sem_video_conclui_como_hoje(cenario):
    """A entrevista ao vivo de quem não enviou nada não muda (R-12)."""
    joao = cenario["inscricoes"][1]
    concluir_pareceres(cenario, joao, {"ana": "DESFAVORAVEL"})


@pytest.mark.parametrize("quem", ["davi", "maria", "joao"])
def test_so_o_alocado_com_atribuicao_abre(cenario, quem):
    """SC-2374: membro sem a Atribuição, a presidência sem ela e o avaliador de outra Etapa."""
    with pytest.raises(DomainError) as recusa:
        abrir_como(cenario, quem)
    assert recusa.value.status == 404
    assert not AberturaDoVideo.objects.exists()


def test_abrir_registra_um_evento_por_abertura_e_os_pedidos_nao_registram(
    cenario, client, seletor_ligado
):
    """SC-2372 e FR-7131, pelo canal da comissão: um evento; N pedidos com `Range`, nenhum."""
    maria = cenario["inscricoes"][0]
    edital, etapa = cenario["edital"], cenario["hetero"]
    identificar(client, "ana", [])
    resposta = client.post(reverse("interface:mesa-video-abrir", args=[edital.id, etapa, maria.id]))
    assert resposta.status_code == 302
    aberta = AberturaDoVideo.objects.get()
    assert f"abertura={aberta.id}" in resposta["Location"]
    rota = reverse("interface:mesa-video", args=[edital.id, etapa, maria.id, aberta.id])
    eventos = RegistroAuditoria.objects.filter(operation=abertura.VISUALIZAR).count()
    assert eventos == 1
    tamanho = cenario["video"].tamanho
    inteiro = client.get(rota)
    assert inteiro.status_code == 200
    assert inteiro["Accept-Ranges"] == "bytes"
    assert inteiro["Content-Type"] == "video/mp4"
    assert int(inteiro["Content-Length"]) == tamanho
    assert len(b"".join(inteiro.streaming_content)) == tamanho
    parcial = client.get(rota, HTTP_RANGE="bytes=0-99")
    assert parcial.status_code == 206
    assert parcial["Content-Range"] == f"bytes 0-99/{tamanho}"
    assert len(b"".join(parcial.streaming_content)) == 100
    assert client.get(rota, HTTP_RANGE="bytes=-10").status_code == 206
    assert client.get(rota, HTTP_RANGE=f"bytes={tamanho}-").status_code == 416
    assert RegistroAuditoria.objects.filter(operation=abertura.VISUALIZAR).count() == 1
    # A Mesa mostra o reprodutor e os rótulos do vídeo, e não oferece baixar.
    pagina = reverse("interface:mesa-inscricao", args=[edital.id, etapa, maria.id])
    mesa = client.get(f"{pagina}?abertura={aberta.id}")
    corpo = mesa.content.decode()
    assert "nodownload" in corpo
    assert "Confirmo" in corpo
    assert "Não dá para confirmar pelo vídeo" in corpo
    assert "baixar=1" not in corpo.split('id="video"')[1].split("</section>")[0]


def test_a_abertura_alheia_nao_entrega_byte(cenario, client, seletor_ligado):
    """A abertura de Ana, apresentada por Bruno, responde como inexistente."""
    maria = cenario["inscricoes"][0]
    edital, etapa = cenario["edital"], cenario["hetero"]
    identificar(client, "ana", [])
    client.post(reverse("interface:mesa-video-abrir", args=[edital.id, etapa, maria.id]))
    aberta = AberturaDoVideo.objects.get()
    client.logout()
    identificar(client, "bruno", [])
    rota = reverse("interface:mesa-video", args=[edital.id, etapa, maria.id, aberta.id])
    assert client.get(rota).status_code == 404


def test_resumo_divergente_recusa_a_abertura_e_fica_na_trilha(cenario):
    from processo_seletivo.verificacao.application import envio

    with open(envio.caminho(cenario["video"].arquivo), "ab") as arquivo:
        arquivo.write(b"adulterado")
    with pytest.raises(DomainError) as recusa:
        abrir_como(cenario, "ana")
    assert recusa.value.code == "video_indisponivel"
    assert RegistroAuditoria.objects.filter(operation=abertura.INTEGRIDADE).count() == 1
    assert not AberturaDoVideo.objects.exists()


# --- A troca e o titular -------------------------------------------------------------------


def test_a_abertura_do_titular_nao_encerra_a_troca(cenario):
    """FR-7124, FR-7127: o titular assiste e ainda troca; depois da comissão, não."""
    from tests.fixtures.verificacao import identidade_de

    maria = cenario["inscricoes"][0]
    abertura.abrir_pelo_titular(
        _pedido(),
        identidade=identidade_de(maria),
        inscricao_id=maria.id,
        etapa_id=cenario["hetero"],
        correlation_id="t",
    )
    trocado = enviar_video(maria, cenario["hetero"], dados=videos_sinteticos.mp4(5.5), duracao=5.5)
    assert trocado.substitui_id == cenario["video"].id
    abrir_como(cenario, "ana")
    with pytest.raises(DomainError) as recusa:
        enviar_video(maria, cenario["hetero"])
    assert recusa.value.code == "ja_aberto"


# --- A deliberação pelo vídeo (R-11) -------------------------------------------------------


def test_tres_confirmacoes_consolidam_o_favoravel_da_165(cenario):
    """FR-7137: sem diferença do Resultado deliberado."""
    pareceres_pelo_video(cenario, dict.fromkeys(PARECERISTAS, "FAVORAVEL"))
    consolidar_na(cenario, cenario["hetero"], cenario["inscricoes"][:1], chave="c-6610-fav")
    resultado = ResultadoEtapa.objects.get(etapa_id=cenario["hetero"])
    assert resultado.origem == ResultadoEtapa.Origem.DELIBERACAO
    assert resultado.sentido == "FAVORAVEL"


def test_o_video_que_nao_confirma_vai_a_entrevista_e_nao_a_nao_confirmada(cenario):
    """FR-7138: na conferência, «encaminhe à entrevista ao vivo»; nenhum Resultado."""
    pareceres_pelo_video(
        cenario, {"ana": "FAVORAVEL", "bruno": "DESFAVORAVEL", "carla": "FAVORAVEL"}
    )
    declarado = consolidar_na(cenario, cenario["hetero"], cenario["inscricoes"][:1], chave="c-6610")
    assert declarado["feitas"] == 0
    assert declarado["motivos"][0]["motivo"] == ganchos.ENCAMINHAR_AO_VIVO
    assert not ResultadoEtapa.objects.filter(etapa_id=cenario["hetero"]).exists()
    assert "1" not in declarado["motivos"][0]["motivo"]  # sem contagem (D-005)


def test_a_chamada_direta_tambem_e_recusada(cenario):
    """FR-7139: a guarda está no ato, e não só no plano."""
    maria = cenario["inscricoes"][0]
    with pytest.raises(DomainError) as recusa:
        ganchos.recusar_desfavoravel_pelo_video(
            edital=cenario["edital"],
            etapa_id=cenario["hetero"],
            inscricao_id=maria.id,
            sentido="DESFAVORAVEL",
        )
    assert recusa.value.code == "desfavoravel_pelo_video"


def _encaminhar(cenario, *, chave="enc-6610", ator="maria"):
    return encaminhamento.encaminhar(
        actor=ator_institucional(ator),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["hetero"],
        inscricao_ids=[cenario["inscricoes"][0].id],
        idempotency_key=chave,
        correlation_id="t",
    )


def test_o_encaminhamento_reabre_e_a_entrevista_ao_vivo_pode_nao_confirmar(cenario):
    """FR-7140 a FR-7142: os pareceres pelo vídeo ficam; o ao vivo decide, com o efeito da `164`."""
    maria = cenario["inscricoes"][0]
    pareceres_pelo_video(
        cenario, {"ana": "FAVORAVEL", "bruno": "DESFAVORAVEL", "carla": "FAVORAVEL"}
    )
    assert [
        i.id
        for i in encaminhamento.a_encaminhar(edital=cenario["edital"], etapa_id=cenario["hetero"])
    ] == [maria.id]
    declarado = _encaminhar(cenario)
    assert declarado["feitas"] == 1, declarado
    registro = EncaminhamentoAoVivo.objects.get()
    assert registro.video_id == cenario["video"].id
    assert len(registro.pareceres) == 3
    assert not Avaliacao.objects.filter(
        inscricao_id=maria.id, etapa_id=cenario["hetero"], estado=Avaliacao.Estado.CONCLUIDA
    ).exists()
    assert (
        ConclusaoAvaliacao.objects.filter(
            avaliacao__inscricao_id=maria.id, avaliacao__etapa_id=cenario["hetero"]
        ).count()
        == 3
    )
    assert not disponibilidade.inscricao_em_modo_video(
        edital=cenario["edital"], etapa_id=cenario["hetero"], inscricao_id=maria.id
    )
    # O ao vivo: sem exigir a abertura do vídeo, e o desfavorável vira Resultado.
    for subject, sentido in {
        "ana": "DESFAVORAVEL",
        "bruno": "DESFAVORAVEL",
        "carla": "FAVORAVEL",
    }.items():
        revisao = Avaliacao.objects.get(
            inscricao_id=maria.id, etapa_id=cenario["hetero"], identity_subject=subject
        ).revision
        concluir_como(
            na_hetero(cenario),
            subject,
            maria,
            sentido=sentido,
            parecer=f"Ao vivo: {sentido}",
            revisao=revisao,
        )
    consolidar_na(cenario, cenario["hetero"], [maria], chave="c-6610-vivo")
    resultado = ResultadoEtapa.objects.get(etapa_id=cenario["hetero"], inscricao=maria)
    assert resultado.sentido == "DESFAVORAVEL"
    assert resultado.consequencia == ResultadoEtapa.Consequencia.RETIRADA_DA_RESERVA


def test_o_encaminhamento_e_unico_e_so_do_que_o_video_nao_confirmou(cenario):
    """FR-7143; e quem o vídeo confirmou não se encaminha."""
    pareceres_pelo_video(
        cenario, {"ana": "FAVORAVEL", "bruno": "DESFAVORAVEL", "carla": "FAVORAVEL"}
    )
    assert _encaminhar(cenario)["feitas"] == 1
    segunda = _encaminhar(cenario, chave="enc-6610-b")
    assert segunda["feitas"] == 0
    assert EncaminhamentoAoVivo.objects.count() == 1


def test_o_titular_encaminhado_le_que_nao_e_reprovacao(cenario, client, seletor_ligado):
    """FR-7144: e não pode mais enviar vídeo."""
    from tests.fixtures.divulgacao import entrar_como_titular

    maria = cenario["inscricoes"][0]
    pareceres_pelo_video(
        cenario, {"ana": "FAVORAVEL", "bruno": "DESFAVORAVEL", "carla": "FAVORAVEL"}
    )
    _encaminhar(cenario)
    entrar_como_titular(client, maria)
    corpo = client.get(reverse("portal:acompanhamento", args=[maria.id])).content.decode()
    assert "A comissão quer conversar com você ao vivo. Isso não é reprovação." in corpo
    with pytest.raises(DomainError) as recusa:
        enviar_video(maria, cenario["hetero"])
    assert recusa.value.code == "indisponivel"


def test_a_tela_de_encaminhar_mostra_o_alcance_sem_contagem(cenario, client, seletor_ligado):
    pareceres_pelo_video(
        cenario, {"ana": "FAVORAVEL", "bruno": "DESFAVORAVEL", "carla": "FAVORAVEL"}
    )
    identificar(client, "maria", ["presidente"])
    rota = reverse("interface:encaminhar-ao-vivo", args=[cenario["edital"].id, cenario["hetero"]])
    resposta = client.get(rota)
    assert resposta.status_code == 200, resposta.status_code
    corpo = resposta.content.decode()
    assert cenario["inscricoes"][0].protocolo in corpo
    assert "favor" not in corpo.split("<main")[1].lower().replace("favorável", "")
    confirmado = client.post(
        rota,
        {
            "confirmar": "1",
            "inscricoes": str(cenario["inscricoes"][0].id),
            "chave_idempotencia": "tela-6610",
        },
    )
    assert confirmado.status_code == 302
    assert EncaminhamentoAoVivo.objects.count() == 1
