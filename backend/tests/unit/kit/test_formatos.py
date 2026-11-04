"""Os formatos da peça: post, story e banner (119, FR-3801, FR-3819, D-007)."""

import pytest

from processo_seletivo.interface import kit_formatos
from processo_seletivo.interface.kit_formatos import BANNER, FORMATOS, POST, STORY


def test_os_tres_formatos_na_ordem_do_zip():
    assert tuple(FORMATOS) == ("post", "story", "banner")


@pytest.mark.parametrize(
    ("formato", "largura", "altura", "margem", "corpo_minimo", "chamada"),
    [
        (POST, 1080, 1350, 80, 24, "Acesse o link na bio"),
        (STORY, 1080, 1920, 80, 24, "Acesse o link na bio"),
        # O dobro dos 750 × 425 do arquivo da comunicação, até a P-3 (D-007).
        (BANNER, 1500, 850, 60, 28, "Acesse o edital"),
    ],
)
def test_tamanho_margem_corpo_minimo_e_chamada(
    formato, largura, altura, margem, corpo_minimo, chamada
):
    assert (formato.largura, formato.altura) == (largura, altura)
    assert formato.margem == margem
    assert formato.util == largura - 2 * margem
    assert formato.corpo_minimo == corpo_minimo
    assert formato.chamada_a_acao == chamada


def test_so_o_story_tem_zonas_reservadas_e_elas_sao_as_da_rede():
    assert POST.zonas_reservadas == ()
    assert BANNER.zonas_reservadas == ()
    assert STORY.zonas_reservadas == ((0, 0, 1080, 250), (0, 1670, 1080, 1920))


def test_area_util_dentro_das_margens():
    assert POST.area_util == (80, 80, 1000, 1270)
    assert BANNER.area_util == (60, 60, 1440, 790)
    # No story, a margem é só lateral: em cima e embaixo valem as zonas, maiores que ela.
    assert STORY.area_util == (80, 0, 1000, 1920)


def test_o_post_e_o_tamanho_da_peca_da_111():
    """A Institucional continua desenhada no post, e o post é o 1080 × 1350 da `111`."""
    assert (kit_formatos.POST.largura, kit_formatos.POST.altura) == (1080, 1350)
