"""T060 — a consulta de Resultado não fica no cache do navegador.

A varredura que já existe, `tests/test_armazenamento_no_navegador.py`, lê apenas o fonte do
**portal**: ela nunca alcança `interface/`. Esta garantia, portanto, não tinha cobertura automática
nenhuma — e a resposta aqui carrega pontuação e protocolo de candidato, que são dado pessoal.
"""

import pytest
from django.urls import reverse

from processo_seletivo.shared.http import SEM_ARMAZENAMENTO
from tests.fixtures.comissao import inscrever
from tests.fixtures.resultado import montar_etapa_de_leitura_unica
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_a_consulta_de_resultados_e_nao_armazenavel(
    client, seletor_ligado, gestor, api_client, manager_headers
):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1460, codigo="1460"
    )
    inscrever(cenario["edital"], 1, primeiro=1)
    identificar(client, "maria", ["gestor"])

    resposta = client.get(
        reverse("interface:resultados-da-etapa", args=[cenario["edital"].id, cenario["primeira"]])
    )
    assert resposta.status_code == 200
    assert resposta["Cache-Control"] == SEM_ARMAZENAMENTO
