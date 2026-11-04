"""Uma verificação ou montagem por servidor de cada vez (117, FR-3692, US4 cenário 9).

A trava ocupada é simulada por outra conexão segurando a mesma chave, como a segunda aba do mesmo
operador seguraria; a de outro servidor não interfere.
"""

import pytest
from django.db import connection

from processo_seletivo.formalizacao.application import exportar
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.formalizacao import (
    definir_documentos,
    designar_direto,
    montar_cenario_da_formalizacao,
)
from tests.integration.formalizacao.test_ciclo_de_vida import outra_conexao

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def pronto(gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    if connection.vendor != "postgresql":
        pytest.skip("trava consultiva só no PostgreSQL")
    cenario = montar_cenario_da_formalizacao(
        gestor, api_client, manager_headers, process_payload, aptas=2, prefixo="conc-117"
    )
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, "rui")
    designar_direto(cenario.edital, "bia")
    return cenario


def _segurando(subject):
    conexao = outra_conexao()
    conexao.autocommit = False
    conexao.execute(
        "SELECT pg_advisory_xact_lock(%s, %s)",
        [nomes.CLASSE_DA_TRAVA, nomes.chave_da_trava(subject)],
    )
    return conexao


def test_a_segunda_verificacao_do_mesmo_servidor_e_recusada(pronto, rui):
    segurando = _segurando("rui")
    try:
        with pytest.raises(DomainError) as recusa:
            exportar.verificar(rui, edital_id=pronto.edital.id, alcance=nomes.RECORTE)
        assert recusa.value.code == nomes.EXPORTACAO_EM_ANDAMENTO
        assert recusa.value.detail.startswith("Uma exportação sua já está em andamento")
    finally:
        segurando.close()


def test_a_segunda_montagem_do_mesmo_servidor_e_recusada(pronto, rui):
    _, comprovante = exportar.verificar(rui, edital_id=pronto.edital.id, alcance=nomes.RECORTE)
    segurando = _segurando("rui")
    try:
        with pytest.raises(DomainError) as recusa:
            exportar.baixar(rui, edital_id=pronto.edital.id, token=comprovante)
        assert recusa.value.code == nomes.EXPORTACAO_EM_ANDAMENTO
    finally:
        segurando.close()


def test_a_de_outro_servidor_nao_e_recusada(pronto, rui):
    segurando = _segurando("rui")
    try:
        bia = Actor("bia", "cefor", frozenset({nomes.CAPACIDADE}))
        verificacao, comprovante = exportar.verificar(
            bia, edital_id=pronto.edital.id, alcance=nomes.RECORTE
        )
        assert verificacao.resultado == nomes.COMPLETO
        assert comprovante
    finally:
        segurando.close()
