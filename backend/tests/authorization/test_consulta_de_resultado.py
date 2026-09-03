"""T059 — quem lê o Resultado, e o que ler **não** concede.

Consultar é de dois — presidência e auditoria, que são as duas que respondem a recurso. Consolidar
é de um. A separação é o menor privilégio dito em rota: reconstruir a decisão não dá o poder de
tomá-la.
"""

import pytest
from django.urls import reverse

from tests.fixtures.comissao import inscrever
from tests.fixtures.resultado import montar_etapa_de_leitura_unica
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.authorization, pytest.mark.django_db]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    montado = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1450, codigo="1450"
    )
    inscrever(montado["edital"], 1, primeiro=1)
    return montado


def consulta(cenario):
    return reverse(
        "interface:resultados-da-etapa", args=[cenario["edital"].id, cenario["primeira"]]
    )


@pytest.mark.parametrize(("subject", "papeis"), [("maria", ["gestor"]), ("iris", ["auditor"])])
def test_presidencia_e_auditoria_consultam(client, seletor_ligado, cenario, subject, papeis):
    identificar(client, subject, papeis)
    assert client.get(consulta(cenario)).status_code == 200


def test_a_auditoria_nao_ganha_o_botao_de_consolidar(client, seletor_ligado, cenario):
    """A porta da consulta é a mesma; a do ato não é."""
    identificar(client, "iris", ["auditor"])
    resposta = client.post(
        reverse(
            "interface:consolidar-resultados", args=[cenario["edital"].id, cenario["primeira"]]
        ),
        {"inscricao_id": []},
    )
    # A view redireciona para a organização, e nada é criado — a recusa vem do comando.
    assert resposta.status_code in (302, 404)
    from processo_seletivo.resultados.models import ResultadoEtapa

    assert ResultadoEtapa.objects.count() == 0


def test_quem_nao_tem_nada_recebe_a_resposta_uniforme(client, seletor_ligado, cenario):
    identificar(client, "estranho", [])
    assert client.get(consulta(cenario)).status_code == 404
