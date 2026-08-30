"""A raiz responde ao que cada um pediu.

Ela é rota de conveniência e não está no `openapi.yaml` — serve para quem chega sem saber o que
existe. Quem chega, porém, é de dois tipos: um cliente de API, que precisa dos endpoints, e uma
pessoa que digitou o endereço no navegador, que precisa das telas e recebia um JSON.
"""

import pytest
from django.urls import reverse

NAVEGADOR = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8"


@pytest.mark.contract
def test_o_navegador_e_levado_para_as_telas(client):
    """Sem `django_db` de propósito: o desvio não consulta o banco, e o teste prova isso.

    O documento de serviço lista os Editais publicados e por isso precisa do banco. Quem só vai
    ser redirecionado não deveria pagar por essa consulta, e não paga.
    """
    resposta = client.get("/", headers={"Accept": NAVEGADOR})

    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("interface:lista")


@pytest.mark.contract
def test_o_redirecionamento_e_temporario(client):
    """A raiz não mudou de lugar: responde coisas diferentes a pedidos diferentes.

    Permanente faria o navegador guardar uma resposta que só valia para ele, e um cliente de API
    aberto depois no mesmo navegador deixaria de ver o documento de serviço.
    """
    resposta = client.get("/", headers={"Accept": NAVEGADOR})

    assert resposta.status_code == 302, "302, e não 301"


@pytest.mark.contract
@pytest.mark.django_db
@pytest.mark.parametrize(
    ("rotulo", "aceito"),
    [
        ("cliente de API", "application/json"),
        ("curl sem argumento", "*/*"),
        ("cliente que não declara nada", ""),
    ],
)
def test_quem_nao_pediu_tela_continua_recebendo_o_documento_de_servico(client, rotulo, aceito):
    """`*/*` é o caso que decide o desenho: aceitar qualquer coisa não é pedir tela."""
    resposta = client.get("/", headers={"Accept": aceito})

    assert resposta.status_code == 200, rotulo
    assert resposta["Content-Type"].startswith("application/json")
    assert "publicEndpoints" in resposta.json()


@pytest.mark.contract
@pytest.mark.django_db
def test_o_documento_de_servico_continua_listando_o_que_existe(client):
    corpo = client.get("/", headers={"Accept": "application/json"}).json()

    assert corpo["publicApi"] == "/api/v1/public"
    assert set(corpo["operational"]) == {"health", "readiness", "metrics"}
