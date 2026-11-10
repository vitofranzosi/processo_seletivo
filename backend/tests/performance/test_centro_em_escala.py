"""O custo do Centro de Controle do Edital (136, FR-4744, SC-1476).

**Fixo por Edital, e não por inscrição**, no molde da FR-4120 da `127`. O Centro chama as mesmas
funções que o detalhe, na mesma ordem (R-003), e a composição é pura: o que ele paga a mais que o
detalhe é só a segunda leitura do alcance (`Alcance.de`), que a view pede para dizer o papel.

**O teto é o do detalhe na mesma situação mais uma folga pequena**, e não um número solto: subiu
acima dele, alguma leitura nova entrou no Centro — e é ela que este teste existe para pegar. Desde a
`138` o Centro é a página do Edital (`interface:detalhe`), e o detalhe de antes é a página anterior:
é ela a medida de comparação, e não a mesma rota medida duas vezes.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from tests.fixtures.andamento import certame_p1, certame_s1
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.performance]

#: O que o Centro pode custar além do detalhe: o `Alcance.de` da view (poucas consultas fixas).
FOLGA_SOBRE_O_DETALHE = 6


def consultas(client, rota, edital):
    url = reverse(rota, args=[edital.id])
    client.get(url)  # aquece a sessão e o cache
    with CaptureQueriesContext(connection) as capturadas:
        resposta = client.get(url)
    assert resposta.status_code == 200
    return len(capturadas)


def test_o_sorteio_nao_cresce_com_as_inscricoes(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    from tests.fixtures.comissao import inscrever

    certame = certame_s1(gestor, api_client, manager_headers, process_payload, quantos=3)
    identificar(client, "carlos", ["gestor"])
    com_poucas = consultas(client, "interface:detalhe", certame["edital"])

    inscrever(certame["edital"], 27, primeiro=900)
    com_muitas = consultas(client, "interface:detalhe", certame["edital"])
    do_detalhe = consultas(client, "interface:pagina-anterior", certame["edital"])

    assert com_poucas == com_muitas, (com_poucas, com_muitas)
    assert com_muitas <= do_detalhe + FOLGA_SOBRE_O_DETALHE, (com_muitas, do_detalhe)


def test_a_pontuacao_com_etapas_nao_cresce_com_as_inscricoes(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    from tests.fixtures.comissao import inscrever

    certame = certame_p1(gestor, api_client, manager_headers, process_payload, quantos=3)
    identificar(client, "maria", [])
    com_poucas = consultas(client, "interface:detalhe", certame["edital"])

    inscrever(certame["edital"], 27, primeiro=900)
    com_muitas = consultas(client, "interface:detalhe", certame["edital"])
    do_detalhe = consultas(client, "interface:pagina-anterior", certame["edital"])

    assert com_poucas == com_muitas, (com_poucas, com_muitas)
    assert com_muitas <= do_detalhe + FOLGA_SOBRE_O_DETALHE, (com_muitas, do_detalhe)
