"""O relatório do Edital lê o banco num número de vezes que não cresce com as inscrições (SC-936).

**O orçamento é o mesmo número nos dois volumes**: 119 consultas com 38 e com 362 inscrições,
medido em 24/10/2026 — contado o `SAVEPOINT` do bloco, e sem o `SET` do `REPEATABLE READ`, que
dentro da transação do caso não é emitido. Uma consulta por inscrição — o defeito que se quer
pegar — faria o caso de escala 10 passar de quinhentas. Tempo não é medido: oscila sob carga, e a
forma é o que importa.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.fixtures.relatorio import montar_cenario
from tests.integration.relatorio.conftest import ler

pytestmark = [pytest.mark.django_db, pytest.mark.performance]

# 118 desde a homologação de 24/10/2026: as publicações de resultado saem numa consulta só, que a
# linha do tempo e o cronograma do anexo leem juntos (eram duas, uma por natureza).
ORCAMENTO = 118


@pytest.mark.parametrize("escala", [1, 10])
def test_o_numero_de_consultas_nao_cresce_com_as_inscricoes(escala):
    cenario = montar_cenario(escala=escala)
    with CaptureQueriesContext(connection) as consultas:
        relatorio = ler(cenario)
    assert sum(p.inscricoes.valor for p in relatorio.perfis) == 38 * escala - 2 * (escala - 1)
    assert len(consultas.captured_queries) == ORCAMENTO
