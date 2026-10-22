"""A fixture do cenário da ocupação. As funções moram em `tests/fixtures/ocupacao.py`."""

import pytest

from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao import montar_cenario_da_ocupacao


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return montar_cenario_da_ocupacao(gestor, api_client, manager_headers, process_payload)


@pytest.fixture
def recorte():
    """O recorte da ampla concorrência do cenário: Perfil, marco e lista nula."""
    return {"perfil_id": PROFILE_ID, "marco_id": MARCO, "lista_id": None}


@pytest.fixture
def cenario_reserva(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O Perfil do TMD: **0 vagas publicadas e cadastro de reserva**, ordem e corte emitidos (097).

    Três habilitadas na Etapa governada, faixa de dois, e **nenhuma apuração**: é o recorte que o
    Edital de remanescentes deixa depois de divulgar a ordem, quando ainda não há vaga a apurar.
    """
    from tests.fixtures.convocacao import habilitar_na_etapa_governada

    edital, pontuada, inscricoes = montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ocupacao-097",
        geral=0,
        reserva="UNLIMITED",
    )
    habilitar_na_etapa_governada(edital, inscricoes[:3])
    return edital, pontuada, inscricoes
