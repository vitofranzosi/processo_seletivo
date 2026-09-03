"""T023 — o resumo continua sendo agregação, e a prontidão não o transforma em laço.

A 013 acrescenta seis dimensões ao mesmo resumo. A propriedade a proteger é que o custo não passe a
crescer com a população: com mil inscrições, uma consulta por linha para descobrir compatibilidade
normativa seria mil leituras de Versão Consolidada para produzir seis inteiros.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.avaliacoes.application.selectors import resumo_da_etapa
from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from processo_seletivo.resultados.application.prontidao import panorama_da_etapa
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.django_db, pytest.mark.performance]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    montado = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1330, codigo="1330"
    )
    vigentes = etapas_vigentes(montado["edital"])
    montado["vigentes"] = vigentes
    montado["etapa_publicada"] = next(
        etapa for chave, etapa in vigentes.items() if str(chave) == str(montado["primeira"])
    )
    return montado


def custo(cenario):
    with CaptureQueriesContext(connection) as capturadas:
        panorama = panorama_da_etapa(
            edital=cenario["edital"],
            etapa=cenario["etapa_publicada"],
            etapas_vigentes=cenario["vigentes"],
        )
        resumo_da_etapa(
            edital=cenario["edital"], etapa=cenario["etapa_publicada"], panorama=panorama
        )
    return len(capturadas)


def test_o_custo_nao_cresce_com_a_populacao(cenario, gestor):
    """Duas inscrições e trinta e duas custam o mesmo: a diferença seria N+1."""
    inscricoes = inscrever(cenario["edital"], 2, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1330")
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")
    com_duas = custo(cenario)

    muitas = inscrever(cenario["edital"], 30, primeiro=100)
    distribuir_para(cenario, gestor, ["joao"], muitas, chave="lote-1330-b")
    for inscricao in muitas[:10]:
        concluir_como(cenario, "joao", inscricao, pontuacao="75")

    assert custo(cenario) == com_duas


def test_a_primeira_etapa_nao_consulta_progressao(cenario, gestor):
    """Sem Etapa anterior, não há conjunto a resolver — e não se paga por perguntar."""
    inscrever(cenario["edital"], 2, primeiro=1)
    assert custo(cenario) <= 5
