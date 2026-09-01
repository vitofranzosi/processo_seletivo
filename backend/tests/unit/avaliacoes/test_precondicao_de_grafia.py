"""A equivalência de grafias vale para a Etapa — e para mais nada (T-017).

Três recusas, e cada uma fecha um modo de falha diferente: objeto de outra coleção que por acaso
carregue os dois nomes; Etapa cujos campos novos já declaram norma; e o hash de conteúdo realmente
diferente, que é a regra de sempre.
"""

from processo_seletivo.publicacoes.domain.conflicts import HASH_MISMATCH, content_conflicts
from processo_seletivo.shared.canonical import canonical_sha256

ETAPA_LITERAL = {
    "id": "00000000-0000-0000-0000-0000000000e1",
    "name": "Análise documental",
    "minimumScore": "70.0000",
}
ETAPA_ELEVADA = {**ETAPA_LITERAL, "evaluationsPerRegistration": 1, "maximumScore": None}
CAMINHO = "/stages/id=00000000-0000-0000-0000-0000000000e1"


def conteudo(etapa, extra=None):
    base = {"schemaVersion": 5, "stages": [etapa]}
    return {**base, **(extra or {})}


def alteracao(caminho, declarado, novo="Outro nome"):
    return [
        {
            "targetPath": caminho,
            "operation": "REPLACE",
            "newValue": novo,
            "expectedPreviousHash": declarado,
        }
    ]


def test_as_duas_grafias_da_etapa_passam():
    atual = conteudo(ETAPA_ELEVADA)
    novo = {**ETAPA_ELEVADA, "name": "Outro nome"}

    for grafia in (ETAPA_LITERAL, ETAPA_ELEVADA):
        conflitos = content_conflicts(atual, alteracao(CAMINHO, canonical_sha256(grafia), novo))

        assert HASH_MISMATCH not in conflitos, grafia


def test_a_grafia_literal_nao_vale_quando_a_norma_foi_declarada():
    declarada = {**ETAPA_ELEVADA, "maximumScore": "100.0000"}
    atual = conteudo(declarada)

    conflitos = content_conflicts(
        atual, alteracao(CAMINHO, canonical_sha256(ETAPA_LITERAL), {**declarada, "name": "Outro"})
    )

    assert HASH_MISMATCH in conflitos


def test_quantidade_declarada_tambem_encerra_a_equivalencia():
    declarada = {**ETAPA_ELEVADA, "evaluationsPerRegistration": 2}
    atual = conteudo(declarada)

    conflitos = content_conflicts(
        atual, alteracao(CAMINHO, canonical_sha256(ETAPA_LITERAL), {**declarada, "name": "Outro"})
    )

    assert HASH_MISMATCH in conflitos


def test_quantidade_nula_e_ausencia_dizem_a_mesma_coisa():
    """O contrato declara `null` equivalente à ausência, e a precondição precisa concordar."""
    nula = {**ETAPA_LITERAL, "evaluationsPerRegistration": None, "maximumScore": None}
    atual = conteudo(nula)

    conflitos = content_conflicts(
        atual, alteracao(CAMINHO, canonical_sha256(nula), {**nula, "name": "Outro"})
    )

    assert HASH_MISMATCH not in conflitos


def test_objeto_que_nao_e_etapa_nao_ganha_segunda_grafia():
    """O modo de falha que a classificação por caminho fecha.

    Um objeto de outra coleção que carregue os dois nomes nos valores legados não é uma Etapa, e
    conceder-lhe a grafia reduzida faria um hash obsoleto passar por ali.
    """
    outro = {"id": "x", "evaluationsPerRegistration": 1, "maximumScore": None, "campo": "antes"}
    atual = conteudo(ETAPA_ELEVADA, {"other": outro})
    reduzido = {
        chave: valor
        for chave, valor in outro.items()
        if chave not in ("evaluationsPerRegistration", "maximumScore")
    }

    conflitos = content_conflicts(
        atual,
        alteracao("/other", canonical_sha256(reduzido), {**outro, "campo": "depois"}),
    )

    assert HASH_MISMATCH in conflitos
