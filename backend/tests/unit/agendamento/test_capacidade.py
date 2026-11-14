"""O veredito do simulador e o ganho de cada atalho (167, T014, FR-7205, UX-760)."""

from datetime import date, time

from processo_seletivo.agendamento.domain import capacidade
from processo_seletivo.agendamento.domain.horarios import Banca, Configuracao

SEG = date(2026, 11, 23)
TER = date(2026, 11, 24)
PERIODO = (SEG, date(2026, 11, 25))
MANHA_E_TARDE = ((time(8), time(12)), (time(13), time(17)))


def config(dias=((SEG, MANHA_E_TARDE),), *, duracao=10, intervalo=5, n_bancas=1):
    return Configuracao(
        "REMOTA",
        duracao,
        intervalo,
        tuple(dias),
        tuple(Banca(f"b{n}", f"Banca {n}", "", n) for n in range(1, n_bancas + 1)),
    )


def test_faltam_11_para_as_43():
    resultado = capacidade.calcular(config(), 43)

    assert resultado.horarios == 32
    assert resultado.falta == 11
    assert resultado.veredito == "Faltam 11 horários para as 43 pessoas."
    assert resultado.explicacao == "43 pessoas participam hoje, e a agenda tem 32 horários."


def test_cabem_as_43_e_sobram_21():
    resultado = capacidade.calcular(config(((SEG, MANHA_E_TARDE), (TER, MANHA_E_TARDE))), 43)

    assert resultado.veredito == "Cabem todas as 43 pessoas. Sobram 21 horários."
    assert resultado.cabe


def test_a_conta_por_janela_numa_linha():
    resultado = capacidade.calcular(config(), 43)

    assert [linha["frase"] for linha in resultado.conta] == [
        "16 atendimentos por banca × 1 banca",
        "16 atendimentos por banca × 1 banca",
    ]
    assert resultado.conta[0]["dia"] == "Seg., 23/11"


def test_lista_aberta_diz_que_a_lista_pode_mudar():
    resultado = capacidade.calcular(config(), 43, lista_aberta=True)

    assert resultado.frase_da_lista_aberta == (
        "A Etapa anterior ainda não tem Resultado: as 43 pessoas são as que participam hoje, e a "
        "lista ainda pode mudar."
    )


def test_os_tres_atalhos_com_uma_banca():
    atalhos = capacidade.atalhos(config(), 43, PERIODO)

    assert [(a.codigo, a.rotulo, a.ganho) for a in atalhos] == [
        ("dia", "Acrescentar Ter., 24/11", 32),
        ("banca", "Acrescentar uma banca", 32),
        ("intervalo", "Tirar o intervalo", 16),
    ]
    # O que resolve sozinho ganha destaque: +32 cobre a falta de 11; +16 também.
    assert [a.resolve for a in atalhos] == [True, True, True]


def test_os_atalhos_com_duas_bancas():
    """O cenário B: duas bancas em 08–12 de 20 + 10, para 23 pessoas — +16, +8, +8."""
    dias = ((SEG, ((time(8), time(12)),)),)
    atalhos = capacidade.atalhos(config(dias, duracao=20, intervalo=10, n_bancas=2), 23, PERIODO)

    assert [(a.codigo, a.ganho) for a in atalhos] == [("dia", 16), ("banca", 8), ("intervalo", 8)]
    assert [a.resolve for a in atalhos] == [True, True, True]


def test_o_atalho_que_nao_resolve_sozinho_nao_tem_destaque():
    atalhos = capacidade.atalhos(config(), 60, PERIODO)

    assert {a.codigo: a.resolve for a in atalhos} == {
        "dia": True,
        "banca": True,
        "intervalo": False,
    }


def test_sem_falta_nao_ha_atalho():
    assert capacidade.atalhos(config(), 20, PERIODO) == []


def test_o_dia_seguinte_fora_do_periodo_nao_e_oferecido():
    ultimo = date(2026, 11, 25)
    atalhos = capacidade.atalhos(config(((ultimo, MANHA_E_TARDE),)), 43, PERIODO)

    assert "dia" not in [a.codigo for a in atalhos]


def test_o_dia_acrescentado_repete_as_janelas_do_ultimo():
    acrescida = capacidade.com_dia(config(), TER)

    assert acrescida.dias[-1] == (TER, MANHA_E_TARDE)


def test_a_banca_acrescentada_tem_nome_novo():
    acrescida = capacidade.com_banca(config(n_bancas=2))

    assert acrescida.bancas[-1].nome == "Banca 3"
    assert acrescida.bancas[-1].ordem == 3
