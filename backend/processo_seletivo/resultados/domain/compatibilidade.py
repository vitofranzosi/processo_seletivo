"""A norma que governou a Avaliação, comparada com a vigente — e só onde importa.

Versões Consolidadas diferentes descrevem, quase sempre, a mesma regra da Etapa: uma Retificação
que corrige a remuneração de um Perfil não muda nada do que esta feature calcula. Comparar
identidade de versão bloquearia toda consolidação pendente a cada Retificação, o que é o oposto do
que esta verificação existe para fazer.

**Quatro campos, e só eles**: caráter eliminatório, nota mínima, quantidade de avaliações e
pontuação máxima. São os que podem mudar o Resultado.

**Nome, cronograma, peso, caráter classificatório e ordem ficam de fora, de propósito.** Peso e
caráter classificatório pertencem à composição entre Etapas, que esta feature recusa; nome e
cronograma são descrição. Compará-los faria a correção de uma vírgula no nome da Etapa impedir toda
consolidação pendente e mandar avaliações corretas de volta à reabertura. A ordem é insumo da
progressão, lida sempre do vigente: mudá-la muda qual é a Etapa anterior, não a validade da
Avaliação.

A comparação é de **valores normalizados**. O conteúdo publicado guarda decimal como string
canônica de quatro casas, e `"60.0000" != "60.00"` como texto sem que haja diferença normativa
alguma. Os dois lados passam pelos mesmos leitores herdados da 012 antes de serem comparados.
"""

from processo_seletivo.avaliacoes.domain.previsao import avaliacoes_previstas, pontuacao_maxima
from processo_seletivo.resultados.domain.regra import eliminatoria, nota_minima

VERSAO_SEM_A_ETAPA = "versao_sem_a_etapa"
NORMA_DIVERGENTE = "norma_divergente"

# (rótulo exibível, leitor). O rótulo entra na frase da recusa: "a Etapa mudou de nota mínima".
CAMPOS_COMPARADOS = (
    ("caráter eliminatório", eliminatoria),
    ("nota mínima", nota_minima),
    ("quantidade de avaliações previstas", avaliacoes_previstas),
    ("pontuação máxima", pontuacao_maxima),
)


def etapa_na_versao(versao, etapa_id):
    """A Etapa daquela identidade no conteúdo da versão, ou `None`.

    `None` não é detalhe: significa que a versão sob a qual se avaliou não descreve esta Etapa, e
    portanto não há norma histórica a reproduzir.
    """
    alvo = str(etapa_id)
    conteudo = getattr(versao, "content", None) or {}
    for etapa in conteudo.get("stages") or []:
        if isinstance(etapa, dict) and str(etapa.get("id")) == alvo:
            return etapa
    return None


def incompatibilidade(*, versao, etapa_id, etapa_vigente):
    """`None` quando a Avaliação pode fundamentar Resultado; senão `(codigo, frase)`."""
    historica = etapa_na_versao(versao, etapa_id)
    if historica is None:
        return (
            VERSAO_SEM_A_ETAPA,
            "a avaliação foi concluída sob uma versão do Edital que não descreve esta Etapa",
        )
    divergentes = [
        rotulo for rotulo, ler in CAMPOS_COMPARADOS if ler(historica) != ler(etapa_vigente)
    ]
    if divergentes:
        return (
            NORMA_DIVERGENTE,
            "a avaliação foi concluída sob regra da Etapa diferente da vigente ("
            + ", ".join(divergentes)
            + ")",
        )
    return None
