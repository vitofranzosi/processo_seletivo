"""A advertência do "Encerrar Processo" custa por Edital, e não por inscrição (130, SC-1324, D-007).

**Consultas, e não segundos**, como na `113`: o tempo de relógio oscila na suíte paralela, e a forma
é o que garante o tempo. Uma consulta por inscrição, por convocação ou por recurso seria o defeito
que faria a tela crescer com o certame.

A lista e o detalhe do Processo não pagam nada: a composição só roda na confirmação. Isso se prende
pela ausência da chamada, e não por um número de consultas que mudaria com qualquer outra feature.
"""

from unittest import mock

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.interface import encerramento
from processo_seletivo.interface.relatorio_do_edital import leitura_consistente
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.relatorio import REFERENCIA, em, montar_cenario
from tests.interface.test_auditoria_passagem_da_retificacao import sessao

pytestmark = [pytest.mark.django_db, pytest.mark.performance]

GESTORA = Actor("gabi.gestora", "cefor", frozenset({"processo:encerrar"}))


def consultas(processo):
    with CaptureQueriesContext(connection) as capturadas, leitura_consistente():
        advertencia = encerramento.do_processo(processo, GESTORA, agora=REFERENCIA)
    assert not advertencia.vazia, "a prova precisa de algo em aberto"
    return len(capturadas.captured_queries)


# Medido em 06/11/2026: 145 consultas com um Edital encerrado com convocação aguardando, com 38 e
# com 362 inscrições. Por Edital a mais, 142: a busca dos Editais é uma só, e o resto é a leitura do
# relatório da `099` e da regra da `113`, inteiras, por Edital. É caro, e foi aceito (D-007 da
# `130`): a tela é rara, e o Processo tem poucos Editais. A leitura em lote é da Frente B.
ORCAMENTO_DE_UM = 145
POR_EDITAL = 142


@pytest.mark.parametrize("escala", [1, 10])
def test_o_numero_de_consultas_nao_cresce_com_as_inscricoes(escala):
    cenario = montar_cenario(escala=escala, final="pendente")
    assert consultas(cenario.processo) == ORCAMENTO_DE_UM


def test_cada_edital_a_mais_custa_o_mesmo():
    cenario = montar_cenario(final="pendente")
    outro = montar_cenario(final="pendente", numero="65")
    Edital.objects.filter(pk=outro.edital.id).update(processo=cenario.processo)
    assert consultas(cenario.processo) == ORCAMENTO_DE_UM + POR_EDITAL


@pytest.mark.usefixtures("seletor_ligado")
def test_a_lista_e_o_detalhe_nao_leem_a_advertencia():
    cenario = montar_cenario(final="pendente")
    cliente = sessao("gabi.gestora", ["gestor"])
    with (
        mock.patch.object(encerramento, "do_processo", side_effect=AssertionError("lida")),
        em(REFERENCIA),
    ):
        for url in (
            reverse("interface:lista"),
            reverse("interface:processo-detalhe", args=[cenario.processo.id]),
        ):
            assert cliente.get(url).status_code == 200
