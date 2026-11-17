"""A leitura da data de nascimento (180, FR-8305, FR-8306, FR-8307; R4 da pesquisa).

Função pura: `hoje` vem de quem chama. Os casos-limite da spec estão aqui um a um, porque a matriz
de rastreabilidade não os cobra sozinha.
"""

from datetime import date

import pytest

from processo_seletivo.inscricoes.domain.pessoais import (
    RECUSA_ANTIGA,
    RECUSA_FORMATO,
    RECUSA_FUTURA,
    RECUSA_INEXISTENTE,
    RECUSA_VAZIA,
    DataDeNascimentoRecusada,
    formatar_data,
    ler_data_de_nascimento,
)

HOJE = date(2026, 11, 17)


def _recusa(texto, hoje=HOJE):
    with pytest.raises(DataDeNascimentoRecusada) as recusa:
        ler_data_de_nascimento(texto, hoje)
    return str(recusa.value)


@pytest.mark.parametrize(
    ("texto", "esperada"),
    [
        ("07/03/1998", date(1998, 3, 7)),
        ("7/3/1998", date(1998, 3, 7)),
        (" 07/03/1998 ", date(1998, 3, 7)),
        # A forma em que alguns navegadores preenchem `autocomplete="bday"`.
        ("1998-03-07", date(1998, 3, 7)),
        ("29/02/2000", date(2000, 2, 29)),
    ],
)
def test_aceita_o_dia_mes_ano_e_a_forma_do_preenchimento_automatico(texto, esperada):
    assert ler_data_de_nascimento(texto, HOJE) == esperada


@pytest.mark.parametrize("texto", ["", "   ", None])
def test_vazia_e_recusada(texto):
    assert _recusa(texto) == RECUSA_VAZIA


@pytest.mark.parametrize(
    "texto",
    # O ano de dois dígitos é o caso-limite: "03" pode ser 1903 ou 2003.
    ["01/02/03", "07031998", "07.03.1998", "07/03", "aa/bb/cccc", "07/03/1998/1", "1998-3-7-1"],
)
def test_fora_do_formato_e_recusada(texto):
    assert _recusa(texto) == RECUSA_FORMATO


@pytest.mark.parametrize(
    "texto", ["31/02/2000", "29/02/2001", "00/01/2000", "32/01/2000", "10/13/2000"]
)
def test_data_que_nao_existe_e_recusada(texto):
    assert _recusa(texto) == RECUSA_INEXISTENTE


def test_hoje_e_recusado_e_ontem_e_aceito():
    assert _recusa("17/11/2026") == RECUSA_FUTURA
    assert _recusa("18/11/2026") == RECUSA_FUTURA
    assert ler_data_de_nascimento("16/11/2026", HOJE) == date(2026, 11, 16)


def test_o_teto_e_cento_e_vinte_anos_completos():
    # "Mais de 120 anos" conta anos completos: quem faz 121 amanhã ainda tem 120.
    assert ler_data_de_nascimento("18/11/1905", HOJE) == date(1905, 11, 18)
    assert _recusa("17/11/1905") == RECUSA_ANTIGA
    assert _recusa("01/01/1898") == RECUSA_ANTIGA


def test_menor_de_idade_e_aceito():
    """Quem pode se inscrever é o Edital que decide, e não o cadastro (FR-8306)."""
    assert ler_data_de_nascimento("01/06/2012", HOJE) == date(2012, 6, 1)


def test_toda_recusa_diz_o_que_conferir():
    for frase in (RECUSA_VAZIA, RECUSA_FORMATO, RECUSA_INEXISTENTE, RECUSA_FUTURA, RECUSA_ANTIGA):
        assert frase.endswith(".")
        assert "erro" not in frase.lower()


def test_formatar_data():
    assert formatar_data(date(1998, 3, 7)) == "07/03/1998"
    assert formatar_data(None) == ""
