"""A Supervisão cobra só o que existe para fazer (122, FR-3909, FR-3910; SC-1168).

O ato que o sorteio fazia na Modalidade apontada como a ampla gerava "não divulgado" e "sem
apuração" para sempre: a ocupação não tem linha para ele, e a divulgação o recusa. Um sinal que não
se resolve ensina a ignorar a Supervisão inteira.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface import supervisao
from tests.conftest import ator_institucional
from tests.fixtures.recorte_excedente import LISTA_AC, certame_com_ac

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

ESPECIES = (supervisao.UX_004, supervisao.UX_065, supervisao.UX_066)


@pytest.fixture
def com_acervo(gestor, api_client, manager_headers, process_payload):
    return certame_com_ac(
        gestor, api_client, manager_headers, process_payload, acervo=True, prefixo="sup"
    )


def _sinais_do_marco(certame, ator):
    return [
        sinal
        for sinal in supervisao.sinais(certame["processo"], ator)
        if sinal.especie in ESPECIES and sinal.edital.id == certame["edital"].id
    ]


def _previa(certame, lista):
    return reverse(
        "interface:previa-de-publicacao",
        args=[certame["edital"].id, certame["marco"], certame["atos"][lista].id],
    )


@pytest.mark.parametrize(
    "ator",
    [
        ator_institucional("maria", "recurso:julgar"),
        ator_institucional("paula.publicadora", "resultado:publicar"),
    ],
    ids=["presidencia", "publicador-puro"],
)
def test_nenhum_sinal_aponta_o_recorte_excedente(com_acervo, ator):
    """FR-3909: nem o sinal de divulgação, que é a quarta porta da FR-3901, nem os outros dois."""
    excedente = _previa(com_acervo, LISTA_AC)

    for sinal in _sinais_do_marco(com_acervo, ator):
        assert "Ampla Concorrência" not in sinal.alvo, sinal
        assert not (sinal.destino and sinal.destino.url == excedente), sinal


def test_o_recorte_operacional_nao_divulgado_continua_sinalizado(com_acervo):
    """FR-3910: o sinal continua, com destino na prévia **daquele** ato."""
    publicadora = ator_institucional("paula.publicadora", "resultado:publicar")

    sinais = [
        sinal
        for sinal in _sinais_do_marco(com_acervo, publicadora)
        if sinal.especie == supervisao.UX_066
    ]

    assert {sinal.destino.url for sinal in sinais} == {
        _previa(com_acervo, lista) for lista in com_acervo["atos"] if lista != LISTA_AC
    }
