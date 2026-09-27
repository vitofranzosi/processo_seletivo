"""Perfil só de cadastro de reserva: a Revisão diz que a convocação é externa (RC-58, DP-05).

O Edital publica, classifica e divulga o resultado. O que ele não faz é convocar: a convocação
exige vaga faltante apurada, e com zero vagas imediatas não há déficit nunca. A DP-05 deixou essa
família fora do piloto, e o que sobra ao sistema é dizê-lo antes de publicar — **advertência**,
porque o Edital é legítimo.
"""

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    validate_for_publication,
)
from tests.unit.editais.test_invariantes_do_quadro import geral, perfil, snapshot

CODIGO = "reserve_only_convocation_external"


def achados(um_perfil, *, ato=ATO_DE_PUBLICACAO):
    return [
        item
        for item in validate_for_publication(snapshot(um_perfil), ato=ato)
        if item.code == CODIGO
    ]


def so_reserva(**alteracoes):
    return perfil(
        **{
            "immediateVacancies": 0,
            "reserveType": "UNLIMITED",
            "vacancyTable": [geral(0)],
            **alteracoes,
        }
    )


@pytest.mark.parametrize(
    ("especie", "limite"),
    [("UNLIMITED", None), ("LIMITED", 30), ("LIMITED", 0)],
)
def test_zero_vaga_com_reserva_e_advertido(especie, limite):
    encontrados = achados(so_reserva(reserveType=especie, reserveLimit=limite))

    assert len(encontrados) == 1
    achado = encontrados[0]
    assert achado.severity == Severity.WARNING, "o Edital é legítimo; recusar diria o contrário"
    assert "'C1'" in achado.message
    assert "convocação dos classificados será feita fora dele" in achado.message
    assert achado.path.endswith("/immediateVacancies"), "o destino é a etapa dos Perfis"


def test_zero_vaga_sem_reserva_nao_e_este_aviso():
    """Oferta sem vaga e sem cadastro é outra pergunta; este aviso a responderia errado."""
    assert achados(so_reserva(reserveType="NONE")) == []


def test_oferta_com_vagas_e_reserva_nao_e_advertida():
    """A convencional convoca pelo déficit, e a reserva dela são os suplentes da faixa."""
    um_perfil = perfil(immediateVacancies=40, reserveType="UNLIMITED", vacancyTable=[geral(40)])

    assert achados(um_perfil) == []


def test_a_retificacao_nao_repete_o_aviso():
    """Dito antes de publicar; repeti-lo a cada correção de data seria ruído."""
    assert achados(so_reserva(), ato=ATO_DE_RETIFICACAO) == []
