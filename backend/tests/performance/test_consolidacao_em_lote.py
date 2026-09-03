"""T034 — mil inscrições num envio, e nenhuma consulta por linha.

O teto de SC-002 não é decorativo: a planilha que esta feature substitui tem mil linhas, e um lote
que exigisse uma leitura por inscrição pareceria rápido com três e sumiria com mil. O que se mede é
**a forma**, e não o relógio — o número de consultas não pode crescer com a seleção.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.django_db, pytest.mark.performance]

# Trinta, e não mil, para que a suíte continue rodando em segundos. O que o teste afirma é a
# **derivada**: se o custo não cresce de três para trinta, ele não cresce de trinta para mil, e é
# a derivada que o defeito N+1 revela.
LOTE = 30


def preparar(gestor, api_client, manager_headers, *, seed, quantas, primeiro):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=seed, codigo=str(seed)
    )
    inscricoes = inscrever(cenario["edital"], quantas, primeiro=primeiro)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave=f"lote-{seed}")
    for inscricao in inscricoes:
        concluir_como(cenario, "joao", inscricao, pontuacao="75")
    return cenario, inscricoes


def custo_de_consolidar(cenario, inscricoes, *, chave):
    with CaptureQueriesContext(connection) as capturadas:
        desfecho = consolidar(
            actor=ator_institucional("maria"),
            processo_id=cenario["processo"].id,
            edital_id=cenario["edital"].id,
            etapa_id=cenario["primeira"],
            inscricao_ids=[i.id for i in inscricoes],
            idempotency_key=chave,
            correlation_id="teste",
        )
    return len(capturadas), desfecho


def test_um_envio_consolida_o_lote_inteiro_sem_interacao_por_inscricao(
    gestor, api_client, manager_headers
):
    cenario, inscricoes = preparar(
        gestor, api_client, manager_headers, seed=1380, quantas=LOTE, primeiro=1
    )
    _, desfecho = custo_de_consolidar(cenario, inscricoes, chave="v1")
    assert desfecho["feitas"] == LOTE
    assert ResultadoEtapa.objects.filter(edital=cenario["edital"]).count() == LOTE


def test_a_leitura_do_panorama_nao_cresce_com_a_selecao(gestor, api_client, manager_headers):
    """As consultas **de leitura** são constantes; só as escritas acompanham o lote.

    A escrita por Resultado é inevitável e correta — cada linha é um ato, com seu evento. O que
    não pode crescer é o custo de **decidir**: elegíveis, Resultados existentes e conjuntos da
    progressão saem numa leitura só, antes do laço.
    """
    pequeno, poucas = preparar(
        gestor, api_client, manager_headers, seed=1381, quantas=3, primeiro=1
    )
    grande, muitas = preparar(
        gestor, api_client, manager_headers, seed=1382, quantas=LOTE, primeiro=500
    )
    custo_pequeno, _ = custo_de_consolidar(pequeno, poucas, chave="v2")
    custo_grande, _ = custo_de_consolidar(grande, muitas, chave="v3")

    # Dez vezes mais inscrições não podem custar dez vezes mais **leituras**. A folga cobre as
    # escritas — Resultado e evento por linha —, e nada além delas.
    por_linha = (custo_grande - custo_pequeno) / (LOTE - 3)
    assert por_linha <= 3, (custo_pequeno, custo_grande)
