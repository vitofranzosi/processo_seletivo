"""T059 — quem lê o Resultado, e o que ler **não** concede.

Consultar é de dois — presidência e auditoria, que são as duas que respondem a recurso. Consolidar
é de um. A separação é o menor privilégio dito em rota: reconstruir a decisão não dá o poder de
tomá-la.

**As recusas passaram a dizer por quê** (033, `FR-478`): quem é do mesmo escopo e não tem a base lê
o que falta, em vez de um "não encontrado" que o faz duvidar do link. A separação acima é a mesma,
e nenhuma rota passou a abrir para quem não a abria.
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
    # **403 exato, e não um conjunto alargado.** A primeira escrita desta alteração acrescentou o
    # 403 à lista `(302, 404)` — e alargar um conjunto aceito é enfraquecer a asserção, que é
    # exatamente o tipo de afrouxamento que o cenário 4 do quickstart manda procurar. A porta é a
    # da gestão da comissão, Íris é do mesmo escopo e não tem a base: a resposta é uma só.
    assert resposta.status_code == 403
    from processo_seletivo.resultados.models import ResultadoEtapa

    assert ResultadoEtapa.objects.count() == 0


def test_quem_nao_tem_nada_recebe_a_recusa_explicada(client, seletor_ligado, cenario):
    """O nome mudou com a doutrina: era `..._recebe_a_resposta_uniforme` (033).

    O ator é do mesmo escopo e não tem base nenhuma. Ele continua **não entrando**; o que mudou é
    que agora sabe por quê.
    """
    identificar(client, "estranho", [])
    assert client.get(consulta(cenario)).status_code == 403


# ------------------------- o ato por ocorrência: quem constata, e quem não (D-1)


def ocorrencia(cenario):
    return reverse(
        "interface:registrar-ocorrencia", args=[cenario["edital"].id, cenario["primeira"]]
    )


def test_a_auditoria_le_o_resultado_e_nao_alcanca_a_ocorrencia(client, seletor_ligado, cenario):
    """Ler não concede o poder de constatar, aqui pela mesma razão que não concede o de consolidar.

    **A resposta passou a ser 403** (033, `FR-478`). Ela era 404 pela doutrina uniforme da `011`,
    e o que essa doutrina protegia — não confirmar que a Etapa existe a quem não a alcança —
    continua protegido pelo filtro de escopo na consulta que a busca. Íris é do **mesmo** escopo e
    já sabe que a Etapa existe: ela acabou de ler o Resultado dela, na linha acima. Esconder dela a
    razão não protegia nada; só a fazia duvidar do link.
    """
    identificar(client, "iris", ["auditor"])
    assert client.get(consulta(cenario)).status_code == 200
    assert client.get(ocorrencia(cenario)).status_code == 403

    resposta = client.post(
        ocorrencia(cenario),
        {"confirmar": "1", "inscricao_id": [], "motivo": "não compareceu"},
    )
    assert resposta.status_code == 403
    from processo_seletivo.resultados.models import ResultadoEtapa

    assert ResultadoEtapa.objects.count() == 0


def test_a_presidencia_alcanca_a_ocorrencia(client, seletor_ligado, cenario):
    identificar(client, "maria", ["gestor"])
    assert client.get(ocorrencia(cenario)).status_code == 200


def test_quem_nao_tem_nada_recebe_a_recusa_explicada_na_ocorrencia(client, seletor_ligado, cenario):
    """Era `..._recebe_a_uniforme_na_ocorrencia`; a asserção de que ele não entra é a mesma."""
    identificar(client, "estranho", [])
    assert client.get(ocorrencia(cenario)).status_code == 403
