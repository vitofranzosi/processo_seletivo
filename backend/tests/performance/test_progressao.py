"""T016 e T045 — o custo da progressão não cresce com a população.

Contagem de consultas, e não tempo de parede. A propriedade que importa é negativa: **nenhuma
consulta por linha**. A 012 fechou a cadeia de autorização em duas condições exatamente para
preservá-la, e a 013 acrescenta uma terceira regra sem reabrir a porta — os conjuntos são
resolvidos uma vez, e o filtro é de conjunto.

Um teste que medisse tempo passaria com dez inscrições e esconderia o defeito até as mil.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.resultados.application.selectors import (
    eliminadas_ate,
    ha_resultado_em,
    habilitadas_em,
)
from tests.fixtures.comissao import inscrever
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.django_db, pytest.mark.performance]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1310, codigo="1310"
    )


def consultas(funcao):
    with CaptureQueriesContext(connection) as capturadas:
        funcao()
    return len(capturadas)


def test_cada_conjunto_custa_uma_consulta(cenario):
    edital, etapa = cenario["edital"], cenario["primeira"]
    assert consultas(lambda: ha_resultado_em(edital=edital, etapa_id=etapa)) == 1
    assert consultas(lambda: habilitadas_em(edital=edital, etapa_id=etapa)) == 1


def test_as_eliminadas_de_varias_etapas_custam_uma_consulta_so(cenario):
    """A exclusão é transitiva, e o custo dela não pode crescer com as Etapas já percorridas."""
    anteriores = [cenario["primeira"], cenario["segunda"]]
    assert consultas(lambda: eliminadas_ate(edital=cenario["edital"], etapas_ids=anteriores)) == 1


def test_sem_etapas_anteriores_nao_ha_consulta(cenario):
    """A primeira Etapa não pergunta ao banco por uma anterior que não existe."""
    assert consultas(lambda: eliminadas_ate(edital=cenario["edital"], etapas_ids=[])) == 0


def test_o_custo_dos_conjuntos_nao_cresce_com_a_populacao(cenario):
    edital, etapa = cenario["edital"], cenario["primeira"]
    com_poucas = consultas(lambda: habilitadas_em(edital=edital, etapa_id=etapa))
    inscrever(edital, 30, primeiro=100)
    assert consultas(lambda: habilitadas_em(edital=edital, etapa_id=etapa)) == com_poucas
