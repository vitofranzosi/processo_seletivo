"""O histórico da convocação lê a série pela identidade gravada, e não pela norma de agora.

A tela ativa e o comando passaram a reduzir o `?lista=` pela derivação vigente (034, FR-499,
FR-503) — e a primeira versão desta correção fez o mesmo no histórico. Ali está errado: os atos
guardam o recorte do dia em que foram praticados, e uma Retificação que depois removesse a
Modalidade faria o histórico dela responder 404, escondendo a série que explica aqueles atos. É o
mesmo cuidado que `ocupacao-historico` tem com o marco removido.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao_sorteada import LINHA_GERAL, LINHA_PPI, LISTA_PPI, MARCO
from tests.fixtures.publicacao import retify
from tests.integration.convocacao.test_suplencia import (  # noqa: F401 — a fixture é importada
    apurar,
    certame,
    chamar,
    contexto,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def test_o_historico_sobrevive_a_retificacao_que_remove_a_modalidade(
    client,
    seletor_ligado,
    certame,  # noqa: F811 — a fixture importada de `test_suplencia`
    gestor,
    api_client,
):
    edital = certame["edital"]
    apurar(certame, gestor, lista_id=LISTA_PPI, chave="historico-apura-ppi")
    titular = contexto(certame, LISTA_PPI)["fila"][0]
    convocada = chamar(certame, gestor, titular, lista_id=LISTA_PPI, chave="historico-titular")
    identificar(client, "carlos", ["gestor"])
    historico = f"{reverse('interface:convocacao-historico', args=[edital.id, MARCO])}?lista="
    protocolo = Inscricao.objects.get(pk=titular).protocolo
    assert protocolo in client.get(historico + LISTA_PPI).content.decode(), "a premissa"

    retify(
        api_client,
        edital,
        [
            {
                "operation": "REPLACE",
                "targetPath": (
                    f"/profiles/id={PROFILE_ID}/vacancyTable/id={LINHA_GERAL}/immediateVacancies"
                ),
                "newValue": 2,
            },
            {
                "operation": "REMOVE",
                "targetPath": f"/profiles/id={PROFILE_ID}/vacancyTable/id={LINHA_PPI}",
            },
            {
                "operation": "REMOVE",
                "targetPath": f"/profiles/id={PROFILE_ID}/competitionModalities/id={LISTA_PPI}",
            },
        ],
        suffix="remove-ppi-019",
    )

    # **A prova de que o teste não é vácuo**: a PPI saiu da norma vigente, e a tela ativa — que
    # resolve o recorte pela norma de agora, e deve — passa a dar 404. O histórico, não.
    ativa = reverse("interface:convocacao", args=[edital.id, MARCO])
    assert client.get(f"{ativa}?lista={LISTA_PPI}").status_code == 404

    resposta = client.get(historico + LISTA_PPI)

    assert resposta.status_code == 200, "o histórico da Modalidade removida continua acessível"
    assert protocolo in resposta.content.decode(), "com a série gravada"
    assert convocada["id"]
