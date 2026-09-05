"""A ordem entre participantes: pontuação, critérios publicados e o empate que sobrevive a todos.

Função pura, e a tabela-verdade inteira cabe num teste unitário.

**A ordem dos critérios é a norma.** Eles são aplicados na sequência que o Edital publicou, e o
código não decide quais existem, em que ordem se aplicam nem qual parâmetro cada um recebe — isso
viaja no snapshot e é retificável (D-004).

**Valor ausente é declarado, nunca inferido.** `whenMissing` diz o que fazer quando o valor que o
critério consome não existe: `ULTIMO_NO_CRITERIO` põe quem não tem por último **naquele critério**,
e `CRITERIO_NAO_SE_APLICA` faz o critério não separar aquele par. O silêncio não vira zero, não vira
último lugar e não vira critério pulado — ele nem chega aqui, porque impede a publicação da regra.

**O empate que sobrevive a todos os critérios não é resolvido.** O sistema não ordena por
identificador, nome, instante de criação nem ordem de retorno do banco: os empatados compartilham
posição, e o ato registra que ali não existe ordem normativa (D-005).

**A numeração é a padrão.** A posição de alguém é o número de participantes à frente dele mais um,
e as posições consumidas por um grupo empatado são puladas — `1, 1, 3`. É o que preserva a contagem
do corte: "os N primeiros" seleciona N pessoas quando nenhum empate atravessa a N-ésima posição.
"""

from decimal import Decimal

ULTIMO_NO_CRITERIO = "ULTIMO_NO_CRITERIO"
CRITERIO_NAO_SE_APLICA = "CRITERIO_NAO_SE_APLICA"

MAIOR_PONTUACAO_NA_ETAPA = "MAIOR_PONTUACAO_NA_ETAPA"
MAIOR_VALOR_DE_FATO = "MAIOR_VALOR_DE_FATO"
MENOR_VALOR_DE_FATO = "MENOR_VALOR_DE_FATO"

MAIOR_PRIMEIRO = {MAIOR_PONTUACAO_NA_ETAPA, MAIOR_VALOR_DE_FATO}


def _valor_do_criterio(criterio, participante):
    """O valor que este critério consome deste participante, ou `None` quando não existe."""
    parametros = criterio.get("parameters") or {}
    if criterio.get("type") == MAIOR_PONTUACAO_NA_ETAPA:
        return (participante.get("pontuacoes") or {}).get(str(parametros.get("stageId")))
    return (participante.get("fatos") or {}).get(str(parametros.get("factId")))


def _comparar_por(criterio, esquerda, direita):
    """-1, 0 ou 1: qual vem primeiro por este critério. Zero quando ele não separa este par."""
    a, b = _valor_do_criterio(criterio, esquerda), _valor_do_criterio(criterio, direita)
    if a is None and b is None:
        return 0
    if a is None or b is None:
        if criterio.get("whenMissing") == CRITERIO_NAO_SE_APLICA:
            return 0
        # `ULTIMO_NO_CRITERIO`: quem não tem valor fica atrás de quem tem, **neste** critério.
        return 1 if a is None else -1
    if a == b:
        return 0
    maior_primeiro = criterio.get("type") in MAIOR_PRIMEIRO
    return -1 if (a > b) == maior_primeiro else 1


def comparar(criterios, esquerda, direita):
    """A comparação completa: pontuação combinada e, empatada, os critérios na ordem publicada.

    Devolve `(ordem, separou_em)`: `ordem` é -1, 0 ou 1, e `separou_em` é o critério que decidiu,
    ou `None` quando foi a pontuação ou quando o empate sobreviveu a todos. É esse segundo valor
    que a consulta mostra depois: quem lê a ordem precisa saber **o que** separou duas posições
    vizinhas (FR-050).
    """
    a, b = esquerda.get("pontuacao"), direita.get("pontuacao")
    if a is not None and b is not None and a != b:
        return (-1 if Decimal(str(a)) > Decimal(str(b)) else 1), None
    for criterio in sorted(criterios, key=lambda item: item.get("order") or 0):
        decisao = _comparar_por(criterio, esquerda, direita)
        if decisao != 0:
            return decisao, criterio
    return 0, None


def ordenar(participantes, criterios):
    """Os classificáveis em ordem, com posição, empate residual e o critério que separou.

    Devolve a lista de participantes acrescida de `posicao`, `empate_residual` e `separado_por`.
    Quem não tem pontuação combinada não entra: ele é considerado do universo, mas não recebe
    posição — e essa distinção é do chamador, não daqui.
    """
    import functools

    ordenados = sorted(
        participantes,
        key=functools.cmp_to_key(lambda a, b: comparar(criterios, a, b)[0]),
    )
    resultado = []
    posicao_do_grupo = 0
    for indice, participante in enumerate(ordenados):
        if indice == 0:
            posicao_do_grupo = 1
            separado_por = None
            empatado_com_anterior = False
        else:
            decisao, criterio = comparar(criterios, ordenados[indice - 1], participante)
            empatado_com_anterior = decisao == 0
            separado_por = None if empatado_com_anterior else criterio
            if not empatado_com_anterior:
                # A posição é quantos estão à frente mais um: o grupo empatado consome as posições
                # que ocuparia, e a seguinte pula para o índice real.
                posicao_do_grupo = indice + 1
        resultado.append(
            {
                **participante,
                "posicao": posicao_do_grupo,
                "separado_por": separado_por,
                "empate_residual": empatado_com_anterior,
            }
        )
    # Marca o **primeiro** de cada grupo empatado também: um empate é do grupo, e não só de quem
    # chega depois — sem isto, o primeiro de um par empatado apareceria como se tivesse posição
    # própria (FR-027).
    for indice, item in enumerate(resultado[:-1]):
        if resultado[indice + 1]["empate_residual"]:
            item["empate_residual"] = True
    return resultado
