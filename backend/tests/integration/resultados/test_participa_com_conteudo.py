"""`participa_da_etapa` com o conteúdo e a Modalidade dados (168, T-001).

A resposta é a mesma, e a versão vigente não é relida: é o que deixa o degrau do acompanhamento
caber no orçamento.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.comissoes.domain.etapas import conteudo_vigente
from processo_seletivo.resultados.application.prontidao import participa_da_etapa
from tests.fixtures.comissao import inscrever
from tests.fixtures.deliberacao import montar_colegiada

pytestmark = pytest.mark.django_db


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_colegiada(gestor, api_client, manager_headers, seed=6803, quantas=1)


def test_a_mesma_resposta_sem_reler_a_versao(cenario):
    (maria,) = cenario["inscricoes"]
    (pedro,) = inscrever(cenario["edital"], 1, primeiro=90, perfil=cenario["perfil"])
    conteudo = conteudo_vigente(cenario["edital"])
    for inscricao, esperado in ((maria, True), (pedro, False)):
        base = participa_da_etapa(
            edital=cenario["edital"], etapa_id=cenario["hetero"], inscricao_id=inscricao.id
        )
        with CaptureQueriesContext(connection) as consultas:
            dado = participa_da_etapa(
                edital=cenario["edital"],
                etapa_id=cenario["hetero"],
                inscricao_id=inscricao.id,
                conteudo=conteudo,
                modalidade=inscricao.modality_id,
            )
        assert base is dado is esperado
        assert not any("publicacoes_" in c["sql"] for c in consultas)
        assert not any(
            'FROM "inscricoes_inscricao" WHERE' in c["sql"]
            and "modality_id" in c["sql"].split("FROM")[0]
            for c in consultas
        )
