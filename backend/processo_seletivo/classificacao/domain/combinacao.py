"""A pontuação combinada de um participante, a partir da regra publicada (015, D-001).

Função pura: recebe o marco no conteúdo publicado, as Etapas publicadas e as pontuações que os
Resultados oficiais trouxeram. Não consulta banco, não conhece modelo, e é por isso que a tabela
inteira de casos cabe num teste unitário.

**O peso não é do marco.** Ele é lido da Etapa, que o publica desde sempre — o marco enumera quais
Etapas entram e declara o que se faz com os pesos (FR-009). Duas fontes para o mesmo número seriam
duas respostas para a mesma pergunta.

**Ausência não é zero.** Etapa decisória não produz número, e participante sem Resultado numa Etapa
enumerada não tem pontuação ali. Somar zero afirmaria que ele tirou zero, que é uma nota — e uma
nota que ninguém atribuiu. Quem não tem pontuação em Etapa enumerada não é classificável, e quem
chama recebe isso dito, e não um número inventado (FR-023).
"""

from decimal import ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

# A grafia publicada e a da biblioteca são coisas distintas de propósito: o Edital publica
# `MEIO_PARA_CIMA`, e `ROUND_HALF_UP` é detalhe de implementação que não deve vazar para a norma.
MODOS = {
    "MEIO_PARA_CIMA": ROUND_HALF_UP,
    "MEIO_PARA_PAR": ROUND_HALF_EVEN,
    "TRUNCAR": ROUND_DOWN,
}
ESCALA_MINIMA, ESCALA_MAXIMA = 0, 6

SOMA_PONDERADA = "SOMA_PONDERADA"
MEDIA_PONDERADA = "MEDIA_PONDERADA"
PELA_SOMA_DOS_PESOS = "PELA_SOMA_DOS_PESOS"

SEM_PONTUACAO = object()
"""O que se devolve quando falta pontuação.

Distinto de `Decimal(0)`, e por isso irredutível a ele.
"""


class RegraIncompleta(ValueError):
    """A regra publicada não basta para calcular, e o cálculo não a completa por conta própria.

    Existe para que a falta apareça na **publicação**, e não no dia em que alguém executa o marco:
    se o cálculo escolhesse um padrão, o padrão seria do código e não do Edital (FR-067, FR-068).
    """


def peso_da_etapa(etapa):
    """O peso publicado da Etapa. Ausência é recusa, e não interpretação (FR-067).

    A redação anterior devolvia 1 e chamava isso de equivalência. Era decisão do código escrita como
    se fosse norma: a spec diz que os pesos não precisam somar 1, e não diz o que `null` significa.
    Quem enumera a Etapa num marco declara o peso dela.
    """
    bruto = etapa.get("weight")
    if bruto is None:
        raise RegraIncompleta(
            "Etapa enumerada pelo marco sem peso declarado: quem enumera declara o peso."
        )
    return Decimal(str(bruto))


def arredondamento_publicado(marco):
    """`(escala, modo)` do marco, ou `RegraIncompleta` quando a publicação não os declarou."""
    rounding = marco.get("rounding") or {}
    escala, modo = rounding.get("scale"), rounding.get("mode")
    if not isinstance(escala, int) or isinstance(escala, bool):
        raise RegraIncompleta("O arredondamento do marco deve declarar `scale` como inteiro.")
    if not ESCALA_MINIMA <= escala <= ESCALA_MAXIMA:
        raise RegraIncompleta(
            f"A escala do arredondamento deve estar entre {ESCALA_MINIMA} e {ESCALA_MAXIMA}."
        )
    if modo not in MODOS:
        raise RegraIncompleta(
            "O modo do arredondamento deve ser MEIO_PARA_CIMA, MEIO_PARA_PAR ou TRUNCAR."
        )
    return escala, modo


def arredondar(valor, marco):
    """A pontuação na escala e no modo publicados — **uma vez**, e sobre o resultado final.

    Arredondar parcelas antes de combiná-las dá resultado diferente, e num lugar onde a pontuação
    decide quem passa. A conta roda em precisão plena e perde precisão uma única vez (FR-069).
    """
    escala, modo = arredondamento_publicado(marco)
    return valor.quantize(Decimal(1).scaleb(-escala), rounding=MODOS[modo])


def combinar(marco, etapas_publicadas, pontuacoes):
    """A pontuação combinada, ou `SEM_PONTUACAO` quando falta alguma parcela.

    `etapas_publicadas` é `{id: etapa}` do conteúdo; `pontuacoes` é `{etapa_id: Decimal | None}`,
    com `None` onde o Resultado não trouxe número — Etapa decisória, ou ausência de Resultado.
    """
    enumeradas = [str(identificador) for identificador in marco.get("stages") or []]
    if not enumeradas:
        return SEM_PONTUACAO
    total = Decimal("0")
    soma_dos_pesos = Decimal("0")
    for etapa_id in enumeradas:
        etapa = etapas_publicadas.get(etapa_id)
        if etapa is None:
            return SEM_PONTUACAO
        valor = pontuacoes.get(etapa_id)
        if valor is None:
            return SEM_PONTUACAO
        peso = peso_da_etapa(etapa)
        total += Decimal(str(valor)) * peso
        soma_dos_pesos += peso
    combinada = _normalizar(marco, total, soma_dos_pesos, len(enumeradas))
    if combinada is SEM_PONTUACAO:
        return SEM_PONTUACAO
    # Depois da operação e da normalização, e só aqui.
    return arredondar(combinada, marco)


def _normalizar(marco, total, soma_dos_pesos, quantas):
    operacao = marco.get("operation")
    normalizacao = marco.get("normalization")
    if operacao == MEDIA_PONDERADA:
        # A média divide pela soma dos pesos por definição; normalizar de novo seria dividir duas
        # vezes. Soma dos pesos zero só acontece se todas as Etapas declararem peso zero, e aí não
        # há média a tirar — não é divisão por zero a evitar, é regra sem sentido a recusar.
        if soma_dos_pesos == 0:
            return SEM_PONTUACAO
        return total / soma_dos_pesos
    if normalizacao == PELA_SOMA_DOS_PESOS:
        if soma_dos_pesos == 0:
            return SEM_PONTUACAO
        return total / soma_dos_pesos
    return total
