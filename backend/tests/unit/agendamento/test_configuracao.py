"""Os oito casos da FR-7204, e os três de forma, recusados com a frase do contrato (167, T008).

As frases são o contrato (`contracts/recusas.md` §1): a tela as mostra como estão, e estes casos as
conferem por trecho — salvo a do cenário 4 da US1, que a spec fixa literalmente, e que se confere
inteira.
"""

from datetime import date, time

import pytest

from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.domain.configuracao import problemas
from processo_seletivo.agendamento.domain.horarios import Banca, Configuracao

SEG = date(2026, 11, 23)
TER = date(2026, 11, 24)
PERIODO = (SEG, date(2026, 11, 25))
MANHA = ((time(8), time(12)),)


def config(*, dias=((SEG, MANHA),), duracao=10, intervalo=5, bancas=None):
    return Configuracao(
        "REMOTA",
        duracao,
        intervalo,
        tuple(dias),
        tuple(bancas) if bancas is not None else (Banca("b1", "Banca 1", "", 1),),
    )


def codigos(lista):
    return [recusa.codigo for recusa in lista]


def test_a_configuracao_valida_nao_tem_problema():
    assert problemas(config(), periodo=PERIODO) == []


@pytest.mark.parametrize(
    ("configuracao", "codigo", "trecho"),
    [
        (config(duracao=0), nomes.DURACAO_NAO_POSITIVA, "Informe a duração"),
        (config(duracao=None), nomes.DURACAO_NAO_POSITIVA, "em minutos"),
        (config(intervalo=-5), nomes.INTERVALO_NEGATIVO, "Use 0 para nenhum intervalo"),
        (config(dias=()), nomes.SEM_DIA, "ao menos um dia"),
        (config(bancas=()), nomes.SEM_BANCA, "ao menos uma banca"),
        (
            config(dias=((SEG, ((time(13), time(12)),)),)),
            nomes.JANELA_INVERTIDA,
            "Em Seg., 23/11, a janela 13:00–12:00 termina antes de começar.",
        ),
        (
            config(dias=((SEG, ((time(8), time(12)), (time(11, 30), time(14)))),)),
            nomes.JANELAS_SOBREPOSTAS,
            "Em Seg., 23/11, as janelas 08:00–12:00 e 11:30–14:00 se sobrepõem. Ajuste uma delas.",
        ),
        (
            config(bancas=(Banca("b1", "  ", "", 1),)),
            nomes.BANCA_SEM_NOME,
            'Dê um nome a cada banca, como "Banca 1".',
        ),
        (
            config(bancas=(Banca("b1", "Sala 1", "", 1), Banca("b2", " sala 1 ", "", 2))),
            nomes.BANCAS_COM_O_MESMO_NOME,
            'Duas bancas se chamam "Sala 1".',
        ),
        (
            config(dias=((SEG, MANHA), (SEG, ((time(13), time(17)),)))),
            nomes.DIA_REPETIDO,
            "Seg., 23/11 aparece duas vezes. Junte as janelas num dia só.",
        ),
    ],
)
def test_cada_caso_e_recusado_com_a_frase_do_contrato(configuracao, codigo, trecho):
    lista = problemas(configuracao, periodo=PERIODO)

    assert codigo in codigos(lista)
    assert any(trecho in recusa.frase for recusa in lista if recusa.codigo == codigo)


def test_a_janela_menor_que_a_duracao_tem_a_frase_literal_do_cenario_4():
    lista = problemas(config(dias=((SEG, ((time(12), time(12, 5)),)),)), periodo=PERIODO)

    assert [recusa.frase for recusa in lista] == [
        "A janela 12:00–12:05 não comporta um atendimento de 10 minutos. Amplie a janela ou "
        "reduza a duração."
    ]


def test_com_mais_de_um_dia_a_frase_diz_qual():
    lista = problemas(
        config(dias=((SEG, ((time(12), time(12, 5)),)), (TER, MANHA))), periodo=PERIODO
    )

    assert lista[0].frase.startswith("Em Seg., 23/11, a janela 12:00–12:05 não comporta")


def test_o_dia_fora_do_periodo_diz_o_periodo_e_a_retificacao():
    lista = problemas(config(dias=((date(2026, 11, 30), MANHA),)), periodo=PERIODO)

    assert codigos(lista) == [nomes.DIA_FORA_DO_PERIODO]
    assert lista[0].frase == (
        "Segunda-feira, 30/11/2026 está fora do período da Etapa no cronograma publicado "
        "(de 23 a 25/11/2026). Escolha um dia dentro dele; mudar o período pede Retificação."
    )


def test_a_etapa_sem_evento_nao_confere_o_periodo():
    """Edge Cases: sem Evento não há período, e a configuração é aceita."""
    assert problemas(config(dias=((date(2027, 3, 1), MANHA),)), periodo=None) == []


def test_todos_os_problemas_de_uma_vez_e_na_ordem_do_contrato():
    """UX-766: a comissão corrige tudo numa passada."""
    lista = problemas(
        config(
            dias=((date(2026, 12, 1), ((time(13), time(12)),)),),
            duracao=0,
            intervalo=-1,
            bancas=(Banca("b1", "", "", 1),),
        ),
        periodo=PERIODO,
    )

    assert codigos(lista) == [
        nomes.DURACAO_NAO_POSITIVA,
        nomes.INTERVALO_NEGATIVO,
        nomes.DIA_FORA_DO_PERIODO,
        nomes.JANELA_INVERTIDA,
        nomes.BANCA_SEM_NOME,
    ]


def test_encostar_nao_e_sobrepor():
    dias = ((SEG, ((time(8), time(12)), (time(12), time(14)))),)
    assert problemas(config(dias=dias), periodo=PERIODO) == []
