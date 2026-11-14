"""A retenção do arquivo (166, US6, FR-7146 a FR-7149, SC-2375) e o append-only (FR-7151)."""

import os
from datetime import timedelta

import pytest
from django.core.management import CommandError, call_command
from django.db import connection, transaction
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import Edital
from processo_seletivo.verificacao.application import envio, retencao
from processo_seletivo.verificacao.models import EliminacaoDoVideo, VideoDaVerificacao
from tests.fixtures.verificacao import enviar_video, montar_com_video

pytestmark = pytest.mark.django_db


@pytest.fixture
def cenario(raiz_de_arquivos, gestor, api_client, manager_headers):
    cenario = montar_com_video(gestor, api_client, manager_headers, seed=6630, quantas=1)
    cenario["video"] = enviar_video(cenario["inscricoes"][0], cenario["hetero"])
    return cenario


def _encerrar(edital, ha_dias):
    """O encerramento como a trilha o registra, no passado: o que se testa é a conta do prazo."""
    Edital.objects.filter(pk=edital.pk).update(status=Edital.Status.ENCERRADO)
    edital.refresh_from_db()
    RegistroAuditoria.objects.create(
        occurred_at=timezone.now() - timedelta(days=ha_dias),
        actor_subject="maria",
        permission="edital:encerrar",
        institution_scope=edital.institution_scope,
        operation="ENCERRAR",
        aggregate_type="Edital",
        aggregate_id=edital.pk,
        previous_state="PUBLICADO",
        new_state="ENCERRADO",
        reason="teste",
        correlation_id="t",
    )


def test_sem_prazo_o_comando_recusa_e_elimina_zero(cenario):
    """SC-2375: P-10 aberta, nada sai."""
    with pytest.raises(CommandError, match="P-10"):
        call_command(
            "eliminar_videos_da_verificacao", edital=str(cenario["edital"].id), confirmar=True
        )
    assert not EliminacaoDoVideo.objects.exists()
    assert os.path.exists(envio.caminho(cenario["video"].arquivo))


def test_edital_nao_encerrado_recusa(cenario, settings):
    settings.VERIFICACAO_POR_VIDEO_RETENCAO_DIAS = 30
    with pytest.raises(CommandError, match="não está encerrado"):
        call_command(
            "eliminar_videos_da_verificacao", edital=str(cenario["edital"].id), confirmar=True
        )


def test_dentro_do_prazo_diz_a_data(cenario, settings):
    settings.VERIFICACAO_POR_VIDEO_RETENCAO_DIAS = 30
    _encerrar(cenario["edital"], 10)
    with pytest.raises(CommandError, match="só cabe a partir de"):
        call_command(
            "eliminar_videos_da_verificacao", edital=str(cenario["edital"].id), confirmar=True
        )


def test_sem_confirmar_so_lista(cenario, settings, capsys):
    settings.VERIFICACAO_POR_VIDEO_RETENCAO_DIAS = 30
    _encerrar(cenario["edital"], 40)
    call_command("eliminar_videos_da_verificacao", edital=str(cenario["edital"].id))
    assert "1 arquivos de vídeo seriam eliminados" in capsys.readouterr().out
    assert not EliminacaoDoVideo.objects.exists()


def test_com_o_prazo_vencido_elimina_o_arquivo_e_preserva_o_registro(cenario, settings):
    """FR-7148, FR-7149: some o arquivo; ficam o resumo, a duração e a trilha."""
    settings.VERIFICACAO_POR_VIDEO_RETENCAO_DIAS = 30
    _encerrar(cenario["edital"], 40)
    call_command("eliminar_videos_da_verificacao", edital=str(cenario["edital"].id), confirmar=True)
    video = VideoDaVerificacao.objects.get()
    assert video.sha256 == cenario["video"].sha256
    assert not os.path.exists(envio.caminho(video.arquivo))
    eliminacao = EliminacaoDoVideo.objects.get()
    assert eliminacao.prazo_em_dias == 30
    assert RegistroAuditoria.objects.filter(operation=retencao.ELIMINAR).count() == 1
    # A segunda rodada não repete.
    call_command("eliminar_videos_da_verificacao", edital=str(cenario["edital"].id), confirmar=True)
    assert EliminacaoDoVideo.objects.count() == 1


@pytest.mark.skipif(connection.vendor != "postgresql", reason="gatilho do PostgreSQL")
@pytest.mark.parametrize("tabela", ["verificacao_video", "verificacao_abertura_do_video"])
def test_as_tabelas_do_video_sao_append_only(cenario, tabela):
    from tests.integration.verificacao.test_mesa_e_r11 import abrir_como, distribuir_na_hetero

    if tabela == "verificacao_abertura_do_video":
        distribuir_na_hetero(cenario, _gestor(), cenario["inscricoes"], chave="d-6630")
        abrir_como(cenario, "ana")
    for comando in (f"UPDATE {tabela} SET id = id", f"DELETE FROM {tabela}"):
        with pytest.raises(Exception, match="append-only"), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(comando)


def _gestor():
    from tests.conftest import ator_institucional

    return ator_institucional("carlos", "comissao:gerir")
