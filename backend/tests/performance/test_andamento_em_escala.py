"""O custo do detalhe do Edital com o andamento (127, FR-4120, SC-1239, R-011).

**Fixo por Edital, e não por inscrição.** A derivação lê muitas funções — o sorteio, a condução, a
distribuição, a convocação —, e cada uma já tem o seu orçamento. O que se prende aqui é que o
detalhe inteiro não cresce com o número de inscrições, e que fica abaixo de um teto medido. Ele
cresce com a configuração (Perfis, marcos, listas, Etapas), como a condução do marco já cresce.

**O teto tem folga de ~20% sobre a medição de 06/11/2026**, a do R-011. Subiu? Antes de mexer no
número, procure a consulta por inscrição que entrou: é o que este teste existe para pegar.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from tests.fixtures.andamento import certame_p1, certame_s1
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.performance]

#: Medidos em 06/11/2026 (R-011): 46 e 57 consultas, com a folga de ~20%.
TETO_DO_SORTEIO = 55
TETO_DA_PONTUACAO = 70
#: A convocação lê, por lista apurada, a leitura do recorte e as três prévias da tela, e cada uma
#: relê a versão vigente (item 9 da revisão do B1): 199 consultas num Perfil de três listas. É o
#: que a tela da convocação já paga para **uma** lista; passar a versão adiante é a otimização que
#: fica registrada em `verificacao.md`.
TETO_DA_CONVOCACAO = 240


def consultas_do_detalhe(client, edital):
    client.get(reverse("interface:detalhe", args=[edital.id]))  # aquece a sessão e o cache
    with CaptureQueriesContext(connection) as capturadas:
        resposta = client.get(reverse("interface:detalhe", args=[edital.id]))
    assert resposta.status_code == 200
    assert resposta.context["andamento"] is not None
    return len(capturadas)


def test_o_sorteio_nao_cresce_com_as_inscricoes(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """Um cenário por teste (a idempotência da publicação colide com dois): as inscrições crescem
    no mesmo Edital, entre as duas medições."""
    from tests.fixtures.comissao import inscrever

    certame = certame_s1(gestor, api_client, manager_headers, process_payload, quantos=3)
    identificar(client, "carlos", ["gestor"])
    com_poucas = consultas_do_detalhe(client, certame["edital"])

    inscrever(certame["edital"], 27, primeiro=900)
    com_muitas = consultas_do_detalhe(client, certame["edital"])

    assert com_poucas == com_muitas, (com_poucas, com_muitas)
    assert com_muitas <= TETO_DO_SORTEIO, com_muitas


def test_a_pontuacao_com_etapas_nao_cresce_com_as_inscricoes(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    poucas = certame_p1(gestor, api_client, manager_headers, process_payload, quantos=3)
    identificar(client, "maria", [])
    com_poucas = consultas_do_detalhe(client, poucas["edital"])

    from tests.fixtures.comissao import inscrever

    inscrever(poucas["edital"], 27, primeiro=900)
    com_muitas = consultas_do_detalhe(client, poucas["edital"])

    assert com_poucas == com_muitas, (com_poucas, com_muitas)
    assert com_muitas <= TETO_DA_PONTUACAO, com_muitas


def test_a_convocacao_nao_cresce_com_as_convocacoes(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """O cenário mais caro (item 8 da revisão do B1): ordem, corte, Etapa governada, apuração e
    convocação. Convocar mais uma pessoa acrescenta uma linha à leitura do recorte, e nenhuma
    consulta: a leitura da convocação e a dos documentos são por recorte."""
    from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao

    edital, _, inscricoes = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="escala-127"
    )
    identificar(client, "carlos", ["gestor"])
    convocar(edital, gestor, inscricoes[0], idempotency_key="escala-127-1")
    com_uma = consultas_do_detalhe(client, edital)

    convocar(edital, gestor, inscricoes[1], idempotency_key="escala-127-2")
    com_duas = consultas_do_detalhe(client, edital)

    # **Não cresce, e pode diminuir**: com a segunda convocação a prévia dos titulares fica vazia, e
    # um ramo dela deixa de consultar (199 → 198, medido em 06/11).
    assert com_duas <= com_uma, (com_uma, com_duas)
    assert com_uma <= TETO_DA_CONVOCACAO, com_uma
