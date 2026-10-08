"""Quando uma autoridade responde, e como ela é dita (060, FR-1119, FR-1120, UX-148, UX-149).

Regras puras: nenhuma consulta, nenhum relógio. A data é sempre a do ato no fuso institucional, e
quem a calcula é quem chama — aqui ela chega pronta.
"""

from dataclasses import dataclass
from datetime import date

import pytest

from processo_seletivo.unidades.domain.rotulos import quem_assinou, rotulo_da_autoridade
from processo_seletivo.unidades.domain.vigencia import (
    ENCERRADA,
    FUTURA,
    VIGENTE,
    periodo,
    situacao,
    vigente,
)


@dataclass
class Registro:
    inicio_vigencia: date
    fim_vigencia: date | None = None
    nome: str = ""
    cargo: str = "Reitora"
    ato_de_nomeacao: str = ""


INICIO = date(2026, 10, 6)


@pytest.mark.parametrize(
    "fim, dia, esperado",
    [
        (None, date(2026, 10, 5), False),  # antes do início
        (None, INICIO, True),  # o início é inclusivo
        (None, date(2030, 1, 1), True),  # fim aberto
        (date(2026, 10, 9), date(2026, 10, 9), True),  # o fim é inclusivo (FR-1120)
        (date(2026, 10, 9), date(2026, 10, 10), False),  # o dia seguinte ao fim, não
    ],
)
def test_a_vigencia_e_inclusiva_nas_duas_pontas(fim, dia, esperado):
    assert vigente(Registro(INICIO, fim), dia) is esperado


def test_encerrar_com_fim_hoje_mantem_hoje_e_retira_amanha():
    """FR-1120: o fim inclusivo é o que torna o encerramento de hoje sem efeito retroativo."""
    hoje = date(2026, 10, 6)
    encerrada_hoje = Registro(date(2026, 1, 1), hoje)
    assert vigente(encerrada_hoje, hoje)
    assert not vigente(encerrada_hoje, date(2026, 10, 7))


def test_a_situacao_e_derivada_da_data_de_hoje():
    """UX-149: futura, vigente e encerrada — sem coluna que divirja da vigência à meia-noite."""
    hoje = date(2026, 10, 6)
    assert situacao(Registro(date(2026, 10, 7)), hoje) == FUTURA
    assert situacao(Registro(hoje), hoje) == VIGENTE
    assert situacao(Registro(date(2026, 1, 1), hoje), hoje) == VIGENTE
    assert situacao(Registro(date(2026, 1, 1), date(2026, 10, 5)), hoje) == ENCERRADA


def test_o_periodo_diz_desde_quando_e_ate_quando():
    assert periodo(Registro(INICIO)) == "desde 06/10/2026"
    assert periodo(Registro(INICIO, date(2026, 12, 31))) == "de 06/10/2026 a 31/12/2026"


def test_o_rotulo_distingue_duas_autoridades_do_mesmo_cargo():
    """UX-148: o ato de nomeação vai no rótulo, depois de um ponto médio, quando houver."""
    titular = Registro(INICIO, cargo="Diretora-Geral", ato_de_nomeacao="Portaria nº 1/2026")
    substituta = Registro(INICIO, cargo="Diretora-Geral", ato_de_nomeacao="Portaria nº 2/2026")
    assert rotulo_da_autoridade(titular) == "Diretora-Geral · Portaria nº 1/2026"
    assert rotulo_da_autoridade(titular) != rotulo_da_autoridade(substituta)
    assert rotulo_da_autoridade(Registro(INICIO, cargo="Reitora")) == "Reitora"


def test_quem_assinou_sem_nome_e_so_o_cargo():
    """FR-994 da 054, que a 060 levou para `unidades` com o resto do catálogo."""
    assert quem_assinou("", "Reitora") == "Reitora"
    assert quem_assinou("Maria", "Reitora") == "Maria — Reitora"
