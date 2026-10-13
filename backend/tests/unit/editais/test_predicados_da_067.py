"""Os dois predicados de que as correções de norma da `067` dependem (D-004, D-007).

Cada um responde a uma pergunta que três superfícies fazem — a validação, o documento e a Revisão —,
e responder em três lugares é como as três passam a discordar sobre o mesmo marco ou o mesmo Perfil.
"""

import pytest

from processo_seletivo.editais.domain.marcos import declara_sorteio
from processo_seletivo.editais.domain.quadro import sem_vaga_imediata

METODO_PROPRIO = {"algorithm": "IFES-SORTEIO-SHA256-v1", "source": "Loteria Federal"}


@pytest.mark.parametrize(
    ("marco", "esperado"),
    [
        ({"orderProduction": "POR_SORTEIO"}, True),
        ({"orderProduction": "POR_SORTEIO", "drawMethod": None}, True),
        ({"orderProduction": "POR_PONTUACAO"}, False),
        ({"orderProduction": ""}, False),
        ({}, False),
        # O acervo anterior à `030`: sem forma declarada, ainda que carregue método próprio. Ele
        # continua exigindo e imprimindo arredondamento, como sempre saiu (D-004).
        ({"orderProduction": "", "drawMethod": METODO_PROPRIO}, False),
        ({"drawMethod": METODO_PROPRIO}, False),
    ],
)
def test_sorteio_e_a_forma_declarada(marco, esperado):
    assert declara_sorteio(marco) is esperado


def test_marco_que_nao_e_objeto_nao_sorteia():
    assert declara_sorteio(None) is False


def _perfil(total, *linhas, reserva="LIMITED"):
    perfil = {"immediateVacancies": total, "reserveType": reserva}
    if linhas != (None,):
        perfil["vacancyTable"] = [
            {"id": f"l{indice}", "modalityId": None if indice == 0 else f"m{indice}", **linha}
            for indice, linha in enumerate({"immediateVacancies": n} for n in linhas)
        ]
    return perfil


@pytest.mark.parametrize(
    ("perfil", "esperado"),
    [
        (_perfil(0, 0, 0, 0, 0), True),
        (_perfil(0, 0), True),
        # Com vaga, inclusive com uma lista em zero: o quadro sai inteiro (FR-1323).
        (_perfil(6, 3, 2, 1, 0), False),
        # Incoerente — a validação o recusa, e o quadro continua saindo para que o erro se veja.
        (_perfil(0, 0, 2), False),
        # Sem quadro declarado (acervo anterior à `025`): o quadro já não sai, e nada muda.
        ({"immediateVacancies": 0, "reserveType": "LIMITED"}, False),
        ({"immediateVacancies": 0, "vacancyTable": []}, False),
        # O booleano não é número, e a ausência não é zero.
        ({"immediateVacancies": False, "vacancyTable": [{"immediateVacancies": 0}]}, False),
        ({"vacancyTable": [{"immediateVacancies": 0}]}, False),
        # Sem cadastro de reserva, a regra é a mesma: nenhuma vaga, nenhum quadro.
        (_perfil(0, 0, 0, reserva="NONE"), True),
    ],
)
def test_sem_vaga_imediata(perfil, esperado):
    assert sem_vaga_imediata(perfil) is esperado
