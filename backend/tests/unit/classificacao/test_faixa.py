"""O cálculo da faixa: alvo, fronteira e o empate que a atravessa (014).

Puro, sem banco e sem norma — o que entra é a ordem como ela foi emitida, e o que sai é quem
progride. É aqui que mora a aritmética que decide quem continua no certame.
"""

import pytest

from processo_seletivo.classificacao.domain import faixa


def ordem(*posicoes):
    """`(identificador, posicao)` na ordem em que o ato as emitiu."""
    return [(f"i{indice}", posicao) for indice, posicao in enumerate(posicoes, start=1)]


def calcular(posicoes, *, alvo, excedente=0, desfecho=faixa.EMPATE_ESTRITO, desde=0):
    return faixa.calcular(posicoes, alvo=alvo, excedente=excedente, desfecho=desfecho, desde=desde)


# --- T036a · a faixa da primeira emissão é alvo + excedente (FR-180, SC-071) -----------------


def test_a_primeira_faixa_soma_o_alvo_e_o_excedente():
    """As 40 vagas e os até 30 suplentes, analisados **juntos** (D-011).

    É o que a cláusula 6.10 do 77/2026, a 8.13 do 57 e a 8.12 do 28 mandam com a palavra
    *imediata*: o suplente precisa estar com documentação deferida **antes** de a desistência
    acontecer, e não depois.
    """
    progrediram, _, primeira, ultima = calcular(ordem(*range(1, 101)), alvo=40, excedente=30)

    assert len(progrediram) == 70
    assert (primeira, ultima) == (1, 70)


def test_sem_excedente_a_faixa_e_o_alvo():
    progrediram, _, _, _ = calcular(ordem(*range(1, 21)), alvo=10)

    assert len(progrediram) == 10


# --- T037 · o alvo conta pessoas, e não números de posição -----------------------------------


def test_o_alvo_conta_pessoas_e_a_numeracao_pula():
    """`desempate.py` registra a convenção e já a explica por causa desta feature.

    A posição é o número de participantes à frente mais um, e as posições consumidas por um grupo
    empatado são puladas — `1, 1, 3`. Contar por número de posição entregaria nove pessoas onde o
    Edital manda dez.
    """
    posicoes = ordem(1, 1, 3, 4, 5, 6, 7, 8, 9, 9, 11, 12)

    progrediram, _, _, ultima = calcular(posicoes, alvo=10, desfecho=faixa.EMPATE_ADMITE_EXCEDENTE)

    assert len(progrediram) == 10
    assert ultima == 9


# --- T039 · o empate que atravessa a fronteira (FR-195, FR-196, SC-059, SC-060) --------------


def test_sob_alvo_estrito_o_empate_na_fronteira_recusa_e_nomeia_as_posicoes():
    posicoes = ordem(1, 2, 3, 3, 3)

    with pytest.raises(faixa.EmpateAtravessaOCorte) as erro:
        calcular(posicoes, alvo=3)

    assert erro.value.posicao == 3
    assert erro.value.quantas == 3


def test_sob_admite_excedente_todos_os_empatados_entram_e_o_excedente_e_registrado():
    posicoes = ordem(1, 2, 3, 3, 3)

    progrediram, excedentes, _, ultima = calcular(
        posicoes, alvo=3, desfecho=faixa.EMPATE_ADMITE_EXCEDENTE
    )

    assert len(progrediram) == 5
    assert len(excedentes) == 2
    assert ultima == 3


def test_a_fronteira_e_a_da_faixa_emitida_e_nao_a_do_alvo():
    """Ninguém analisa o suplente 21 porque o 20 empatou (D-011, R-008)."""
    posicoes = ordem(1, 2, 3, 4, 4)

    # Alvo 2 e excedente 2 fazem faixa 4 — e o empate está na posição 4, não na 2.
    with pytest.raises(faixa.EmpateAtravessaOCorte) as erro:
        calcular(posicoes, alvo=2, excedente=2)

    assert erro.value.posicao == 4


# --- T040 · o empate que não atravessa não impede nada ---------------------------------------


def test_empate_longe_do_corte_nao_impede():
    posicoes = ordem(1, 1, 3, 4, 5, 6)

    progrediram, _, _, _ = calcular(posicoes, alvo=5)

    assert len(progrediram) == 5


def test_empate_desfeito_por_criterio_publicado_nao_chega_a_comparacao():
    """Posições distintas são o que a ordem emite quando o critério separou."""
    posicoes = ordem(1, 2, 3, 4, 5)

    progrediram, _, _, _ = calcular(posicoes, alvo=3)

    assert len(progrediram) == 3


# --- T041 · menos participantes que o alvo, e o alvo zero ------------------------------------


def test_menos_participantes_que_o_alvo_faz_todos_progredirem():
    """O 14/2026 prevê literalmente esse caso, e ele não é erro."""
    progrediram, _, _, ultima = calcular(ordem(1, 2, 3), alvo=10)

    assert len(progrediram) == 3
    assert ultima == 3


def test_alvo_zero_nao_faz_ninguem_progredir():
    progrediram, _, primeira, ultima = calcular(ordem(1, 2, 3), alvo=0)

    assert progrediram == []
    assert (primeira, ultima) == (1, None)


# --- T042 · participante sem posição nunca entra na faixa (FR-191) ---------------------------


def test_participante_sem_posicao_nunca_entra():
    posicoes = [("sem", None), ("a", 1), ("b", 2)]

    progrediram, _, _, _ = calcular(posicoes, alvo=10)

    assert progrediram == ["a", "b"]


# --- a continuação começa depois da última posição alcançada (FR-202) ------------------------


def test_a_continuacao_comeca_depois_da_ultima_alcancada():
    posicoes = ordem(*range(1, 11))

    progrediram, _, primeira, ultima = calcular(posicoes, alvo=3, desde=4)

    assert progrediram == ["i5", "i6", "i7"]
    assert (primeira, ultima) == (5, 7)


def test_a_continuacao_sobre_ordem_esgotada_nao_alcanca_ninguem():
    progrediram, _, primeira, ultima = calcular(ordem(1, 2, 3), alvo=5, desde=3)

    assert progrediram == []
    assert (primeira, ultima) == (4, None)


# --- o vocabulário publicado ------------------------------------------------------------------


def test_a_etapa_governada_sai_da_declaracao_e_none_e_ausencia():
    assert faixa.etapa_governada({"governedStage": "abc"}) == "abc"
    assert faixa.etapa_governada({"governedStage": faixa.SEM_ETAPA_GOVERNADA}) is None
    assert faixa.etapa_governada({}) is None
    assert faixa.etapa_governada(None) is None


def test_a_normalizacao_emite_o_excedente_sempre_e_o_alvo_uma_vez_so():
    """Duas grafias do mesmo significado acusariam obsolescência onde não há (FR-193)."""
    derivada = faixa.normalizar({"targetKind": faixa.ALVO_DO_QUADRO, "targetCount": 10})
    fixa = faixa.normalizar({"targetKind": faixa.ALVO_FIXO, "targetCount": 10})

    assert derivada["targetCount"] is None
    assert derivada["surplusCount"] == 0
    assert fixa["targetCount"] == 10
    assert faixa.normalizar({}) is None


def test_o_alvo_derivado_registra_a_identidade_da_linha_lida():
    """Sem o `rowId`, retificado o quadro, não há como dizer se **aquele** corte ficou para trás."""
    quantidade, origem = faixa.alvo_apurado(
        {"targetKind": faixa.ALVO_DO_QUADRO},
        quantidade_do_quadro=40,
        linha_do_quadro="linha-1",
    )

    assert quantidade == 40
    assert origem == {"source": "VACANCY_TABLE_ROW", "rowId": "linha-1"}
