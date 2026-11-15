"""Os horários derivados da configuração (167, T006, SC-2391, FR-7203, FR-7205, FR-7206).

O número de horários que a tela mostra é o desta função, e não uma segunda conta: o SC-2391 pede
que os dois coincidam em 100% dos casos, e a forma de garanti-lo é haver uma conta só.
"""

from datetime import date, time

import pytest

from processo_seletivo.agendamento.domain import recusas
from processo_seletivo.agendamento.domain.horarios import (
    Banca,
    Configuracao,
    derivar,
    dia_curto,
    dia_por_extenso,
    janelas,
    periodo_por_extenso,
    sobras,
    zona,
)

SEG = date(2026, 11, 23)
TER = date(2026, 11, 24)
MANHA_E_TARDE = ((time(8), time(12)), (time(13), time(17)))


def bancas(quantas):
    return tuple(Banca(f"b{n}", f"Banca {n}", "", n) for n in range(1, quantas + 1))


def configuracao(dias, *, duracao=10, intervalo=5, n_bancas=1):
    return Configuracao("REMOTA", duracao, intervalo, tuple(dias), bancas(n_bancas))


def test_o_dia_do_teste_independente_rende_32_horarios():
    """23/11, 08:00–12:00 e 13:00–17:00, 10 + 5, uma banca: 16 por janela (US1)."""
    horarios = derivar(configuracao([(SEG, MANHA_E_TARDE)]))

    assert len(horarios) == 32
    assert [janela.por_banca for janela in janelas(configuracao([(SEG, MANHA_E_TARDE)]))] == [
        16,
        16,
    ]


def test_acrescentar_o_dia_seguinte_leva_a_64():
    assert len(derivar(configuracao([(SEG, MANHA_E_TARDE), (TER, MANHA_E_TARDE)]))) == 64


def test_duas_bancas_em_08_12_com_20_e_10_rendem_16_oito_por_banca():
    """US1, cenário 3."""
    config = configuracao([(SEG, ((time(8), time(12)),))], duracao=20, intervalo=10, n_bancas=2)
    horarios = derivar(config)

    assert len(horarios) == 16
    assert sum(1 for h in horarios if h.banca_id == "b1") == 8
    assert sum(1 for h in horarios if h.banca_id == "b2") == 8


def test_cada_seguinte_comeca_depois_da_duracao_mais_o_intervalo():
    horarios = derivar(configuracao([(SEG, ((time(8), time(9)),))]))

    assert [f"{h.inicio.astimezone(zona()):%H:%M}" for h in horarios] == [
        "08:00",
        "08:15",
        "08:30",
        "08:45",
    ]
    assert f"{horarios[-1].fim.astimezone(zona()):%H:%M}" == "08:55"


def test_as_bancas_ficam_lado_a_lado_em_cada_horario():
    horarios = derivar(configuracao([(SEG, ((time(8), time(8, 30)),))], n_bancas=3))

    assert [(f"{h.inicio.astimezone(zona()):%H:%M}", h.banca_id) for h in horarios] == [
        ("08:00", "b1"),
        ("08:00", "b2"),
        ("08:00", "b3"),
        ("08:15", "b1"),
        ("08:15", "b2"),
        ("08:15", "b3"),
    ]


@pytest.mark.parametrize(
    ("inicio", "fim", "duracao", "intervalo", "n_bancas", "esperados"),
    [
        (time(8), time(12), 10, 5, 1, 16),
        (time(8), time(12), 30, 0, 1, 8),
        (time(8), time(12), 45, 15, 2, 8),
        (time(13), time(17), 20, 10, 3, 24),
        (time(9), time(10), 60, 0, 1, 1),
        (time(9), time(9, 59), 60, 0, 1, 0),
        (time(8), time(18), 25, 5, 2, 40),
    ],
)
def test_o_numero_de_horarios_e_o_da_fr_7203(inicio, fim, duracao, intervalo, n_bancas, esperados):
    """SC-2391: durações, intervalos e bancas variados; a conta à mão está na coluna `esperados`."""
    config = configuracao(
        [(SEG, ((inicio, fim),))], duracao=duracao, intervalo=intervalo, n_bancas=n_bancas
    )

    assert len(derivar(config)) == esperados


def test_o_instante_e_o_da_zona_institucional():
    primeiro = derivar(configuracao([(SEG, MANHA_E_TARDE)]))[0]

    assert primeiro.inicio.utcoffset().total_seconds() == -3 * 3600
    assert primeiro.dia == SEG


def test_a_sobra_e_informada_quando_nao_cabe_outro_atendimento():
    """13:00–17:00 com 20 + 0 cabe 12 e não sobra; com 20 + 5, o exemplo do contrato (FR-7206)."""
    sem_sobra = configuracao([(SEG, ((time(13), time(17)),))], duracao=20, intervalo=0)
    com_sobra = configuracao([(SEG, ((time(13), time(17)),))], duracao=20, intervalo=5)

    assert sobras(sem_sobra) == []
    [janela] = sobras(com_sobra)
    assert janela.ultimo_fim == time(16, 40)
    assert janela.sobra == 15
    assert recusas.sobra_no_fim(janela) == (
        "Em Seg., 23/11, o último atendimento da janela 13:00–17:00 termina às 16:40: sobram 15 "
        "minutos, que não cabem outro atendimento."
    )


def test_o_intervalo_depois_do_ultimo_atendimento_nao_e_sobra():
    """08:00–12:00 com 10 + 5 termina às 11:55, e os cinco minutos são a pausa pedida (T-004)."""
    assert sobras(configuracao([(SEG, MANHA_E_TARDE)])) == []


def test_configuracao_invalida_nao_inventa_horario():
    assert derivar(configuracao([(SEG, MANHA_E_TARDE)], duracao=0)) == ()
    assert derivar(configuracao([(SEG, MANHA_E_TARDE)], intervalo=-1)) == ()
    assert derivar(configuracao([(SEG, ((time(12), time(8)),))])) == ()


def test_dia_repetido_nao_duplica_horario():
    assert len(derivar(configuracao([(SEG, MANHA_E_TARDE), (SEG, MANHA_E_TARDE)]))) == 32


def test_as_datas_se_escrevem_como_a_tela():
    assert dia_curto(SEG) == "Seg., 23/11"
    assert dia_por_extenso(TER) == "Terça-feira, 24/11/2026"
    assert periodo_por_extenso((SEG, date(2026, 11, 25))) == "de 23 a 25/11/2026"
    assert periodo_por_extenso((date(2026, 11, 30), date(2026, 12, 2))) == "de 30/11 a 02/12/2026"
    assert periodo_por_extenso((SEG, SEG)) == "em 23/11/2026"
