"""A consulta pública diz a unidade do ato como estava no dia (060, US4; FR-1131).

O contrato da resposta está em `tests/contract/test_consulta_publica_api.py`; aqui, que a unidade
vem da Publicação, e não do registro de Unidades — renomeada depois, a consulta não muda.
"""

import pytest

from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.unidades.models import Unidade
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def test_a_consulta_diz_a_unidade_do_dia_mesmo_depois_de_renomeada(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    publicacao = Publicacao.objects.get(edital=edital)
    Unidade.objects.filter(codigo="cefor").update(nome="Outro nome", sigla="Outra")

    corpo = api_client.get(f"/api/v1/public/publicacoes/{publicacao.id}").json()

    assert corpo["unit"]["acronym"] == "Cefor"
    assert corpo["unit"]["name"] == "Centro de Referência em Formação e em Educação a Distância"
    assert corpo["signatory"]["name"] == "Diretora"
