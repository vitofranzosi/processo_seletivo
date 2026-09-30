"""A data do fecho do ato (054, FR-989, D-004)."""

from datetime import UTC, date, datetime

import pytest

from processo_seletivo.publicacoes.infrastructure.humano import data_por_extenso
from processo_seletivo.shared.tempo import ZONA


@pytest.mark.parametrize(
    ("data", "esperado"),
    [
        (date(2026, 4, 7), "7 de abril de 2026"),
        (date(2026, 3, 1), "1 de março de 2026"),
        (date(2026, 9, 29), "29 de setembro de 2026"),
        (date(2026, 12, 31), "31 de dezembro de 2026"),
    ],
)
def test_a_data_sai_por_extenso_sem_zero_no_dia(data, esperado):
    assert data_por_extenso(data) == esperado


def test_o_dia_e_o_do_fuso_institucional_e_nao_o_do_relogio_em_utc():
    """Publicado às 22h30 de Vitória, o ato é daquele dia — em UTC já seria o seguinte."""
    instante = datetime(2026, 9, 30, 1, 30, tzinfo=UTC)
    assert data_por_extenso(instante.astimezone(ZONA).date()) == "29 de setembro de 2026"
