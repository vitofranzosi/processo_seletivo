"""A norma histórica contra a vigente — e o que **não** entra na comparação.

Metade destes casos existe para provar exclusões. Comparar demais é tão defeituoso quanto comparar
de menos: uma vírgula corrigida no nome da Etapa mandaria avaliações corretas de volta à reabertura.
"""

from processo_seletivo.resultados.domain.compatibilidade import (
    NORMA_DIVERGENTE,
    VERSAO_SEM_A_ETAPA,
    incompatibilidade,
)

ETAPA = "11111111-1111-1111-1111-111111111111"


def conteudo(*etapas):
    """A comparação é sobre **conteúdo publicado**, e não sobre a linha da Versão Consolidada.

    A função recebe o dicionário direto: quem compara mil avaliações resolve os conteúdos distintos
    — dois ou três por Edital — em vez de carregar mil cópias do Edital inteiro.
    """
    return {"stages": list(etapas)}


def etapa(**kwargs):
    base = {
        "id": ETAPA,
        "name": "Análise de Títulos",
        "order": 0,
        "eliminatory": True,
        "classificatory": True,
        "minimumScore": "60.0000",
    }
    base.update(kwargs)
    return base


def test_norma_identica_e_compativel():
    assert (
        incompatibilidade(conteudo=conteudo(etapa()), etapa_id=ETAPA, etapa_vigente=etapa()) is None
    )


def test_decimal_em_forma_diferente_e_a_mesma_norma():
    """`"60.0000"` e `"60.00"` são o mesmo valor; comparar texto inventaria uma divergência."""
    assert (
        incompatibilidade(
            conteudo=conteudo(etapa(minimumScore="60.00")),
            etapa_id=ETAPA,
            etapa_vigente=etapa(minimumScore="60.0000"),
        )
        is None
    )


def test_ausencia_de_quantidade_equivale_a_uma():
    """O incremento da 012 é aditivo: conteúdo anterior a ele não carrega a chave, e vale 1."""
    assert (
        incompatibilidade(
            conteudo=conteudo(etapa()),
            etapa_id=ETAPA,
            etapa_vigente=etapa(evaluationsPerRegistration=1),
        )
        is None
    )


def test_nota_minima_diferente_e_incompativel():
    codigo, frase = incompatibilidade(
        conteudo=conteudo(etapa(minimumScore="50.0000")),
        etapa_id=ETAPA,
        etapa_vigente=etapa(minimumScore="60.0000"),
    )
    assert codigo == NORMA_DIVERGENTE
    assert "nota mínima" in frase


def test_carater_eliminatorio_diferente_e_incompativel():
    codigo, _ = incompatibilidade(
        conteudo=conteudo(etapa(eliminatory=False)), etapa_id=ETAPA, etapa_vigente=etapa()
    )
    assert codigo == NORMA_DIVERGENTE


def test_quantidade_prevista_diferente_e_incompativel():
    codigo, _ = incompatibilidade(
        conteudo=conteudo(etapa(evaluationsPerRegistration=2)),
        etapa_id=ETAPA,
        etapa_vigente=etapa(evaluationsPerRegistration=1),
    )
    assert codigo == NORMA_DIVERGENTE


def test_pontuacao_maxima_diferente_e_incompativel():
    codigo, _ = incompatibilidade(
        conteudo=conteudo(etapa(maximumScore="100.0000")),
        etapa_id=ETAPA,
        etapa_vigente=etapa(maximumScore="80.0000"),
    )
    assert codigo == NORMA_DIVERGENTE


def test_nome_cronograma_peso_classificatorio_e_ordem_nao_criam_incompatibilidade():
    """Nenhum dos cinco altera a pontuação ou a consequência que esta feature produz."""
    historica = etapa(
        name="Análise de Titulos",
        scheduleEventId="22222222-2222-2222-2222-222222222222",
        weight="1.0000",
        classificatory=False,
        order=7,
    )
    assert (
        incompatibilidade(conteudo=conteudo(historica), etapa_id=ETAPA, etapa_vigente=etapa())
        is None
    )


def test_versao_que_nao_descreve_a_etapa_impede():
    """Sem a identidade no conteúdo histórico, não há norma a reproduzir."""
    codigo, _ = incompatibilidade(
        conteudo=conteudo(etapa(id="99999999-9999-9999-9999-999999999999")),
        etapa_id=ETAPA,
        etapa_vigente=etapa(),
    )
    assert codigo == VERSAO_SEM_A_ETAPA


def test_retificacao_fora_da_etapa_nao_cria_incompatibilidade():
    """Outra Etapa alterada na mesma versão não diz nada sobre esta."""
    outra = {"id": "33333333-3333-3333-3333-333333333333", "order": 1, "minimumScore": "10.0000"}
    assert (
        incompatibilidade(conteudo=conteudo(etapa(), outra), etapa_id=ETAPA, etapa_vigente=etapa())
        is None
    )
