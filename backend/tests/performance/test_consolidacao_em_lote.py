"""SC-002 no teto declarado: **mil** inscrições num envio.

Duas perguntas diferentes, e cada uma precisa do seu teste:

1. **a derivada** — o custo de decidir não pode crescer com a seleção, que é o defeito N+1;
2. **o teto** — mil inscrições cabem mesmo num envio, que é o que SC-002 promete e o que a
   planilha substituída tem. A derivada não responde a isso: limites de parâmetro, tamanho de
   pedido e comportamento no volume real só aparecem no volume real.

O cenário é semeado em massa de propósito. Percorrer os comandos mil vezes mediria o custo de
montar o estado, e não o de consolidá-lo — e as invariantes daqueles comandos já têm testes seus.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.resultado import montar_etapa_de_leitura_unica, semear_prontas

pytestmark = [pytest.mark.django_db, pytest.mark.performance]

TETO = 1000


def consolidar_lote(cenario, inscricoes, *, chave):
    return consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_mil_inscricoes_cabem_num_unico_envio(gestor, api_client, manager_headers):
    """O teto de SC-002, exercido — e não estimado por extrapolação."""
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1520, codigo="1520"
    )
    inscricoes = semear_prontas(cenario, TETO, primeiro=1)

    desfecho = consolidar_lote(cenario, inscricoes, chave="teto")
    assert desfecho["feitas"] == TETO
    assert desfecho["recusadas"] == 0
    assert ResultadoEtapa.objects.filter(edital=cenario["edital"]).count() == TETO


def test_o_custo_de_decidir_nao_cresce_com_a_selecao(gestor, api_client, manager_headers):
    """A derivada. As escritas acompanham o lote — Resultado e evento por linha —; as leituras não.

    Se o custo de decidir não cresce de três para trezentas, ele não cresce de trezentas para mil,
    e é a derivada que o N+1 revela.
    """
    pequeno = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1521, codigo="1521"
    )
    poucas = semear_prontas(pequeno, 3, primeiro=1)
    grande = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1522, codigo="1522"
    )
    muitas = semear_prontas(grande, 300, primeiro=5000)

    with CaptureQueriesContext(connection) as poucas_consultas:
        consolidar_lote(pequeno, poucas, chave="d1")
    with CaptureQueriesContext(connection) as muitas_consultas:
        consolidar_lote(grande, muitas, chave="d2")

    por_linha = (len(muitas_consultas) - len(poucas_consultas)) / (300 - 3)
    assert por_linha <= 3, (len(poucas_consultas), len(muitas_consultas))
