"""O consolidado lê o banco na proporção dos Editais, e não das inscrições (100, SC-942).

**A afirmação é de igualdade, e não de teto**, como na Visão Geral: com Editais da mesma estrutura,
cada Edital a mais custa o mesmo número de consultas, e dez vezes mais inscrições não custam
nenhuma. Uma consulta por inscrição — o defeito que se quer pegar — quebraria a segunda igualdade;
uma consulta por par de Editais, a primeira. Tempo não é medido aqui: oscila sob carga (CLAUDE.md).
A medição de tempo que fixou o limite de Editais está na pesquisa da feature (R-006).
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.interface import relatorio_consolidado as rc
from processo_seletivo.unidades.models import Unidade
from tests.fixtures.relatorio import REFERENCIA, montar_cenario
from tests.integration.relatorio_consolidado.conftest import conjunto

pytestmark = [pytest.mark.django_db, pytest.mark.performance]


def _consultas(editais):
    escolhido = conjunto("criterio=manual&" + "&".join(f"edital={e.pk}" for e in editais))
    unidade = Unidade.objects.get(codigo="cefor")
    with CaptureQueriesContext(connection) as consultas:
        rc.ler(escolhido, agora=REFERENCIA, unidade=unidade)
    return len(consultas.captured_queries)


def test_cada_edital_a_mais_custa_o_mesmo():
    editais = [montar_cenario(final="pendente", numero=n).edital for n in ("61", "62", "63")]
    um, dois, tres = (_consultas(editais[:k]) for k in (1, 2, 3))
    assert dois - um == tres - dois > 0


def test_inscricoes_nao_custam_consulta():
    pequeno = montar_cenario(final="pendente").edital
    grande = montar_cenario(final="pendente", numero="62", escala=10).edital
    assert _consultas([pequeno]) == _consultas([grande])
