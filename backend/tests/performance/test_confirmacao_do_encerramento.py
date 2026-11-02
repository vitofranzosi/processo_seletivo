"""A confirmação de encerrar lê o banco tantas vezes com 38 quanto com 362 inscrições (SC-1072).

**Consultas, e não segundos.** O SC-1072 pede menos de um segundo com 400 inscrições; tempo de
relógio oscila na suíte paralela (CLAUDE.md, *Um teste de tempo oscila sob carga*), e a forma é o
que garante o tempo: uma consulta por inscrição é o defeito que faria a tela crescer com o Edital.
O tempo em si é medido isolado, e registrado no `verificacao.md` da `113`.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.interface import encerramento
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.relatorio import REFERENCIA_ABERTA, montar_cenario

pytestmark = [pytest.mark.django_db, pytest.mark.performance]

GESTORA = Actor("gabi.gestora", "cefor", frozenset({"edital:encerrar", "edital:cancelar"}))


def consultas_da_confirmacao(escala):
    # `aberto`: o Edital fica publicado, com o período correndo no instante de referência dele.
    cenario = montar_cenario(escala=escala, final="aberto")
    with CaptureQueriesContext(connection) as consultas:
        confirmacao = encerramento.da_confirmacao(
            cenario.edital, GESTORA, acao="encerrar", agora=REFERENCIA_ABERTA
        )
    assert confirmacao.impedimentos
    return len(consultas.captured_queries)


# Medido em 01/11/2026: 23 consultas com 38 e com 362 inscrições, no Edital com o período correndo.
ORCAMENTO = 23


@pytest.mark.parametrize("escala", [1, 10])
def test_o_numero_de_consultas_nao_cresce_com_as_inscricoes(escala):
    assert consultas_da_confirmacao(escala) == ORCAMENTO
