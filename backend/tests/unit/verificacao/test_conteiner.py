"""A conferência técnica do contêiner (166, FR-7120, T-003), sobre vídeos sintéticos."""

import io

import pytest

from processo_seletivo.verificacao.domain import conteiner
from tests.fixtures import videos_sinteticos as sinteticos


def _ler(dados):
    return conteiner.ler(io.BytesIO(dados))


def test_mp4_pela_assinatura_e_a_duracao_pelo_mvhd():
    lido = _ler(sinteticos.mp4(4.8))
    assert lido.formato == conteiner.MP4
    assert lido.duracao == pytest.approx(4.8)


def test_mp4_com_moov_depois_do_mdat():
    assert _ler(sinteticos.mp4(61.25, moov_no_fim=True)).duracao == pytest.approx(61.25)


def test_mp4_fragmentado_le_a_duracao_do_mehd():
    assert _ler(sinteticos.mp4(12.5, fragmentado=True)).duracao == pytest.approx(12.5)


def test_webm_com_duracao():
    lido = _ler(sinteticos.webm(30.0))
    assert lido.formato == conteiner.WEBM
    assert lido.duracao == pytest.approx(30.0)


def test_webm_do_chrome_sem_duracao_devolve_none():
    """O `MediaRecorder` não grava `Duration`: vale a medida do aparelho, contra o teto."""
    assert _ler(sinteticos.webm(30.0, com_duracao=False)).duracao is None


def test_webm_com_segmento_de_tamanho_desconhecido():
    assert _ler(sinteticos.webm(9.0, tamanho_desconhecido=True)).duracao == pytest.approx(9.0)


@pytest.mark.parametrize(
    "dados",
    [
        b"%PDF-1.7\n" + b"0" * 100,
        b"\x89PNG\r\n\x1a\n" + b"0" * 100,
        b"",
        b"\x1a\x45\xdf\xa3" + b"matroska" + b"0" * 60,
    ],
    ids=["pdf", "png", "vazio", "mkv-que-nao-e-webm"],
)
def test_o_que_nao_e_mp4_nem_webm_e_recusado(dados):
    with pytest.raises(conteiner.ConteinerInvalido):
        _ler(dados)


def test_mp4_truncado_e_recusado():
    with pytest.raises(conteiner.ConteinerInvalido):
        _ler(sinteticos.mp4(4.8)[:30])
