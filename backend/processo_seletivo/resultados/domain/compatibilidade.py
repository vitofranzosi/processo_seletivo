"""A norma que governou a Avaliação, comparada com a vigente — e só onde importa.

Versões Consolidadas diferentes descrevem, quase sempre, a mesma regra da Etapa: uma Retificação
que corrige a remuneração de um Perfil não muda nada do que esta feature calcula. Comparar
identidade de versão bloquearia toda consolidação pendente a cada Retificação, o que é o oposto do
que esta verificação existe para fazer.

**Seis campos, e só eles**: forma da conclusão, caráter eliminatório, nota mínima, quantidade de
avaliações, pontuação máxima e — desde a 146 — o barema. São os que podem mudar o Resultado.

**Nome, cronograma, peso, caráter classificatório, ordem e os rótulos ficam de fora, de
propósito.** Peso e
caráter classificatório pertencem à composição entre Etapas, que esta feature recusa; nome e
cronograma são descrição. Compará-los faria a correção de uma vírgula no nome da Etapa impedir toda
consolidação pendente e mandar avaliações corretas de volta à reabertura. A ordem é insumo da
progressão, lida sempre do vigente: mudá-la muda qual é a Etapa anterior, não a validade da
Avaliação.

A comparação é de **valores normalizados**. O conteúdo publicado guarda decimal como string
canônica de quatro casas, e `"60.0000" != "60.00"` como texto sem que haja diferença normativa
alguma. Os dois lados passam pelos mesmos leitores herdados da 012 antes de serem comparados.
"""

from decimal import Decimal, InvalidOperation

from processo_seletivo.avaliacoes.domain.barema import criterios_da_etapa
from processo_seletivo.avaliacoes.domain.previsao import (
    avaliacoes_previstas,
    forma_publicada,
    pontuacao_maxima,
)
from processo_seletivo.resultados.domain.regra import eliminatoria, nota_minima


def _decimal(valor):
    if valor in (None, ""):
        return None
    try:
        return Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        return str(valor)


def _texto(valor):
    return (valor or "").strip() if isinstance(valor, str) else valor


def barema_comparavel(etapa):
    """O barema da Etapa como **conjunto**, para comparar sem a ordem (146, D-006, FR-5221).

    **Tudo menos a ordem**: a identidade e, de cada critério, nome, descrição, máxima, pontos por
    unidade, unidade e documento ligado. A descrição é onde mora a condição material ("só
    experiência em EaD"), e o sistema não distingue redação de regra; a recusa custa reabrir e
    concluir de novo, com a ficha já preenchida, e o contrário custaria um Resultado consolidado sob
    regra que não é a publicada. A ordem só muda onde a linha aparece.

    Os decimais são normalizados como os outros campos daqui — `"20.0000"` e `"20"` são a mesma
    máxima —, e a Etapa sem barema, ou do acervo sem a chave, é o conjunto vazio.
    """
    return frozenset(
        (
            str(criterio.get("id")),
            _texto(criterio.get("name")),
            _texto(criterio.get("description")) or "",
            _decimal(criterio.get("maximumScore")),
            _decimal(criterio.get("pointsPerUnit")),
            _texto(criterio.get("unitLabel")) or "",
            str(criterio.get("documentRequirementId") or ""),
        )
        for criterio in criterios_da_etapa(etapa)
    )


VERSAO_SEM_A_ETAPA = "versao_sem_a_etapa"
NORMA_DIVERGENTE = "norma_divergente"

# (rótulo exibível, leitor). O rótulo entra na frase da recusa: "a Etapa mudou de nota mínima".
CAMPOS_COMPARADOS = (
    # A **forma** é o campo mais grave da lista, e por isso vem primeiro. Sem ela, uma Retificação
    # que trocasse `PONTUADA` por `DECISORIA` não seria detectada, e a 013 fundamentaria Resultado
    # numa conclusão cuja espécie a norma vigente já não admite — não uma nota fora do limite novo,
    # mas uma nota onde a norma não prevê nota nenhuma (D-008).
    #
    # Os **rótulos ficam de fora**, pelo mesmo critério que mantém nome e cronograma fora: trocar
    # "Deferido" por "Deferido(a)" não altera consequência alguma, e compará-los faria correção de
    # redação bloquear toda consolidação pendente.
    ("forma da conclusão", forma_publicada),
    ("caráter eliminatório", eliminatoria),
    ("nota mínima", nota_minima),
    ("quantidade de avaliações previstas", avaliacoes_previstas),
    ("pontuação máxima", pontuacao_maxima),
    # O barema da 146 entra **inteiro**, salvo a ordem (D-006). Sem ele, uma Retificação que
    # mudasse a máxima de um critério, ou a condição escrita na descrição dele, deixaria consolidar
    # a conclusão feita sob o barema anterior — e o total dela seria a soma de outra regra.
    ("barema", barema_comparavel),
)


def etapa_no_conteudo(conteudo, etapa_id):
    """A Etapa daquela identidade no conteúdo publicado, ou `None`.

    Recebe o **conteúdo**, e não a Versão Consolidada. A diferença não é estética: a versão carrega
    o Edital inteiro em JSON mais os bytes canônicos, e quem compara mil avaliações precisa dos
    conteúdos **distintos** — que são dois ou três —, e não de mil cópias deles.

    `None` não é detalhe: significa que a versão sob a qual se avaliou não descreve esta Etapa, e
    portanto não há norma histórica a reproduzir.
    """
    alvo = str(etapa_id)
    for etapa in (conteudo or {}).get("stages") or []:
        if isinstance(etapa, dict) and str(etapa.get("id")) == alvo:
            return etapa
    return None


def incompatibilidade(*, conteudo, etapa_id, etapa_vigente):
    """`None` quando a Avaliação pode fundamentar Resultado; senão `(codigo, frase)`."""
    historica = etapa_no_conteudo(conteudo, etapa_id)
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
