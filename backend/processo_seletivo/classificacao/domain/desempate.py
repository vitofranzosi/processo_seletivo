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


def particiona_o_grupo(criterio, grupo):
    """Este critério separa alguém **dentro deste grupo**? (FR-071)

    A pergunta é do **grupo**, e não do par. `CRITERIO_NAO_SE_APLICA` avaliado par a par produzia
    comparação não transitiva: bastava o critério não se aplicar a dois pares por ausência e
    aplicar-se ao terceiro para existir A > B > C > A — e aí as permutações da mesma entrada davam
    ordens diferentes, sob a mesma regra publicada.

    Avaliado por grupo, o critério ou particiona o grupo inteiro ou não particiona nenhum par dele,
    e a ordem volta a ser função só das entradas e da norma (FR-070).
    """
    valores = [_valor_do_criterio(criterio, item) for item in grupo]
    if criterio.get("whenMissing") == CRITERIO_NAO_SE_APLICA and any(v is None for v in valores):
        # Ausência em **qualquer** membro desliga o critério para este grupo — e só para ele. Quem
        # está noutro grupo não desativa nada, que é a diferença entre esta regra e a global.
        return False
    return len(_grupos_por_valor(criterio, grupo)) > 1


def _grupos_por_valor(criterio, grupo):
    """O grupo quebrado por valor, na ordem que o critério declara — ausentes sempre no fim.

    **Não se ordena negando o valor.** A primeira redação fazia `-valor` para inverter o sentido, e
    isso quebrava em dois lugares: `Decimal` não é `int` nem `float`, de modo que a inversão era
    silenciosamente ignorada para pontuações — o "maior primeiro" ordenava ao contrário —, e fato
    do tipo data não admite negação nenhuma. Ordenar os **valores distintos** e reverter a
    sequência funciona para os três tipos que o domínio conhece.
    """
    presentes, ausentes = {}, []
    for item in grupo:
        valor = _valor_do_criterio(criterio, item)
        if valor is None:
            ausentes.append(item)
        else:
            presentes.setdefault(valor, []).append(item)
    ordenados = sorted(presentes, reverse=criterio.get("type") in MAIOR_PRIMEIRO)
    saida = [presentes[valor] for valor in ordenados]
    if ausentes:
        # `ULTIMO_NO_CRITERIO`: quem não tem o valor fica atrás de quem tem, **neste** critério.
        saida.append(ausentes)
    return saida


def _particionar(grupo, criterios):
    """O grupo, quebrado pelo primeiro critério que o particiona, recursivamente.

    Devolve lista de `(subgrupo, criterio_que_separou)`. Um critério que não particiona **não
    encerra a sequência**: o próximo é oferecido ao mesmo grupo (FR-072).
    """
    if len(grupo) <= 1:
        return [(grupo, None)]
    ordenados = sorted(criterios, key=lambda item: item.get("order") or 0)
    for indice, criterio in enumerate(ordenados):
        if not particiona_o_grupo(criterio, grupo):
            continue
        saida = []
        for subgrupo in _grupos_por_valor(criterio, grupo):
            saida.extend(
                (sub, quem or criterio)
                for sub, quem in _particionar(subgrupo, ordenados[indice + 1 :])
            )
        return saida
    return [(grupo, None)]


def ordenar(participantes, criterios):
    """Os classificáveis em ordem, com posição, empate residual e o critério que separou.

    **Partição sucessiva de grupos, e não comparação par a par.** A pontuação combinada separa
    primeiro; dentro de cada grupo empatado, cada critério publicado é oferecido na ordem, e o
    primeiro que particiona o grupo o quebra em subgrupos — sobre os quais os critérios seguintes
    são oferecidos de novo. Um critério que não particiona não encerra a sequência.

    É essa forma que torna a ordem **transitiva**, e portanto determinística: ela não depende de
    comparar pares, e por isso não pode ter ciclo (FR-070, FR-071, FR-072).
    """
    por_pontuacao = {}
    for participante in participantes:
        chave = participante.get("pontuacao")
        por_pontuacao.setdefault(str(chave), []).append(participante)

    def _do_maior_para_o_menor(par):
        # Pontuação nula é o marco sem parcela numérica: todos entram no mesmo grupo, e a ordem
        # entre grupos não se coloca porque só existe um (FR-077, FR-078).
        valor = par[1][0].get("pontuacao")
        return Decimal("0") if valor is None else Decimal(str(valor))

    grupos = []
    for _, grupo in sorted(por_pontuacao.items(), key=_do_maior_para_o_menor, reverse=True):
        grupos.extend(_particionar(grupo, criterios))

    resultado = []
    for grupo, separou in grupos:
        # A posição é quantos estão à frente mais um: o grupo anterior consome as posições que
        # ocupou, e este começa na seguinte — `1, 1, 3` (FR-026).
        posicao = len(resultado) + 1
        empatado = len(grupo) > 1
        for item in grupo:
            resultado.append(
                {
                    **item,
                    "posicao": posicao,
                    "separado_por": separou,
                    "empate_residual": empatado,
                }
            )
    return resultado
