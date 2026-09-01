"""O custo de um comando em lote não pode crescer com o tamanho do lote.

Os testes de desempenho anteriores cobriam a leitura das telas. Este cobre a escrita — que é
onde o N+1 voltou: cada alocação removida abria a Versão Consolidada de novo.
"""

import pytest

from processo_seletivo.comissoes.application.alocacao import (
    alocar_varios,
    remover_varias_alocacoes,
)
from processo_seletivo.comissoes.application.comissao import adicionar_varios, remover_membro

pytestmark = [pytest.mark.django_db, pytest.mark.performance]

TAMANHO = 12


@pytest.fixture
def banca(gestor, processo_a, edital_a, etapa_a1, etapa_a2):
    adicionar_varios(
        actor=gestor,
        processo_id=processo_a.id,
        entradas=[("presidente", "Presidente")],
        funcao="PRESIDENTE",
        idempotency_key="lote-presidencia",
        correlation_id="c",
    )
    criados, _ = adicionar_varios(
        actor=gestor,
        processo_id=processo_a.id,
        entradas=[(f"servidor{i:03d}", f"Servidor {i:03d}") for i in range(TAMANHO)],
        funcao="MEMBRO",
        idempotency_key="lote-banca",
        correlation_id="c",
    )
    return criados


def _consultas_de_versao(queries):
    return sum(1 for q in queries if "versaoconsolidada" in q["sql"].lower())


def test_remover_em_lote_le_a_versao_uma_vez_por_edital(
    gestor, processo_a, edital_a, etapa_a1, banca, settings
):
    from django.db import connection, reset_queries

    alocadas, _ = alocar_varios(
        actor=gestor,
        processo_id=processo_a.id,
        membro_ids=[m.id for m in banca],
        edital_id=edital_a.id,
        etapa_id=etapa_a1,
        idempotency_key="lote-aloca",
        correlation_id="c",
    )
    settings.DEBUG = True
    reset_queries()

    remover_varias_alocacoes(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_ids=[a.id for a in alocadas],
        idempotency_key="lote-remove",
        correlation_id="c",
    )

    # Um Edital, uma leitura da versão — e não uma por alocação, que era o defeito.
    assert _consultas_de_versao(connection.queries) <= 2, len(alocadas)


def test_alocar_em_lote_le_a_versao_uma_vez(
    gestor, processo_a, edital_a, etapa_a1, banca, settings
):
    from django.db import connection, reset_queries

    settings.DEBUG = True
    reset_queries()

    alocar_varios(
        actor=gestor,
        processo_id=processo_a.id,
        membro_ids=[m.id for m in banca],
        edital_id=edital_a.id,
        etapa_id=etapa_a1,
        idempotency_key="lote-aloca-2",
        correlation_id="c",
    )

    assert _consultas_de_versao(connection.queries) <= 2


def test_a_cascata_da_remocao_de_membro_nao_le_por_etapa(
    gestor, processo_a, edital_a, etapa_a1, etapa_a2, banca, settings
):
    from django.db import connection, reset_queries

    pessoa = banca[0]
    for etapa in (etapa_a1, etapa_a2):
        alocar_varios(
            actor=gestor,
            processo_id=processo_a.id,
            membro_ids=[pessoa.id],
            edital_id=edital_a.id,
            etapa_id=etapa,
            idempotency_key=f"cascata-{etapa}",
            correlation_id="c",
        )
    settings.DEBUG = True
    reset_queries()

    remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=pessoa.id,
        idempotency_key="cascata-remove",
        correlation_id="c",
    )

    assert _consultas_de_versao(connection.queries) <= 2
