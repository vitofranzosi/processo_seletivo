"""A extração declarada é viável? A regra pura, sem banco (102, FR-2650, FR-2651, SC-954).

**A matriz é a do Edital 72/2026.** As inscrições terminaram em 28/10 às 9h e a extração foi
declarada para o mesmo dia, às 20h05. A Loteria Federal publica só a data, e a data vale a partir de
00h00: nenhum congelamento posterior às 9h é anterior a ela. Cada linha da matriz desloca a extração
em relação a esse fim, e a regra precisa acertar todas. Falso positivo prende Edital que sortearia;
falso negativo é o 72 de novo.
"""

from datetime import datetime, timedelta

import pytest

from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.sorteios.domain import viabilidade

FIM = datetime(2026, 10, 28, 9, 0, tzinfo=ZONA)


@pytest.mark.parametrize(
    ("extracao", "inviavel"),
    [
        ("2026-10-27T20:05:00-03:00", True),  # dia anterior ao fim
        ("2026-10-28T08:00:00-03:00", True),  # mesmo dia, antes do fim
        ("2026-10-28T20:05:00-03:00", True),  # mesmo dia, depois do fim: o Edital 72
        ("2026-10-29T00:00:00-03:00", False),  # meia-noite do dia seguinte
        ("2026-10-29T20:05:00-03:00", False),  # dia seguinte
    ],
)
def test_a_matriz_do_fim_das_inscricoes_com_fonte_que_publica_so_a_data(extracao, inviavel):
    limite = viabilidade.limite_previsto(extracao, so_a_data=True)

    assert viabilidade.inviavel(limite, FIM) is inviavel


@pytest.mark.parametrize(
    "extracao",
    [
        "2026-10-27T20:05:00-03:00",
        "2026-10-28T20:05:00-03:00",
        "2020-01-01T20:00:00-03:00",
    ],
)
def test_fonte_com_horario_nao_tem_limite_previsto_e_nunca_e_inviavel(extracao):
    """A D-006: a fonte que publica a hora fica fora, e a recusa continua valendo para ela."""
    limite = viabilidade.limite_previsto(extracao, so_a_data=False)

    assert limite is None
    assert viabilidade.inviavel(limite, FIM) is False


def test_granularidade_desconhecida_nao_tem_limite_previsto():
    """Fonte fora do vocabulário tem achado próprio; esta regra não empilha outro sobre ela."""
    assert viabilidade.limite_previsto("2026-10-28T20:05:00-03:00", so_a_data=None) is None


def test_o_limite_e_a_meia_noite_do_dia_no_fuso_institucional():
    limite = viabilidade.limite_previsto("2026-10-28T20:05:00-03:00", so_a_data=True)

    assert limite == datetime(2026, 10, 28, 0, 0, tzinfo=ZONA)


@pytest.mark.parametrize(
    ("extracao", "dia"),
    [
        # 01h30 em UTC ainda é 27/10 em Vitória: o dia é o do fuso institucional, e não o do texto.
        ("2026-10-28T01:30:00+00:00", 27),
        # 23h30 em -02:00 já é 29/10 em Vitória? Não: é 22h30 de 28/10. O texto e o dia coincidem.
        ("2026-10-28T23:30:00-02:00", 28),
        # 23h30 em -05:00 é 01h30 de 29/10 em Vitória.
        ("2026-10-28T23:30:00-05:00", 29),
    ],
)
def test_o_dia_e_tomado_depois_de_converter_para_o_fuso_institucional(extracao, dia):
    limite = viabilidade.limite_previsto(extracao, so_a_data=True)

    assert limite == datetime(2026, 10, dia, 0, 0, tzinfo=ZONA)


@pytest.mark.parametrize("texto", ["", None, "28/10/2026", "2026-10-28T20:05:00", "amanhã"])
def test_instante_ilegivel_ou_sem_fuso_nao_tem_limite(texto):
    """Quem acusa a forma é a conferência de forma; aqui o recuo é silencioso, de propósito."""
    assert viabilidade.limite_previsto(texto, so_a_data=True) is None


def test_limite_igual_ao_congelamento_e_inviavel():
    """A constituição recusa com `<=`: igualdade não prova que a semente veio depois."""
    limite = datetime(2026, 10, 29, 0, 0, tzinfo=ZONA)

    assert viabilidade.inviavel(limite, limite) is True
    assert viabilidade.inviavel(limite, limite - timedelta(microseconds=1)) is False


def test_sem_instante_de_congelamento_nao_ha_o_que_comparar():
    limite = datetime(2026, 10, 29, 0, 0, tzinfo=ZONA)

    assert viabilidade.inviavel(limite, None) is False


def test_na_tela_o_congelamento_mais_cedo_espera_o_fim_das_inscricoes():
    """FR-2651: com as inscrições correndo, congelar agora é impossível; o primeiro é o fim."""
    agora = datetime(2026, 10, 27, 15, 0, tzinfo=ZONA)

    assert viabilidade.congelamento_mais_cedo(agora=agora, fim_das_inscricoes=FIM) == FIM
    depois = FIM + timedelta(hours=2)
    assert viabilidade.congelamento_mais_cedo(agora=depois, fim_das_inscricoes=FIM) == depois
    assert viabilidade.congelamento_mais_cedo(agora=agora, fim_das_inscricoes=None) == agora
