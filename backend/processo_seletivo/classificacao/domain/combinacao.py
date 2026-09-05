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

from decimal import Decimal

SOMA_PONDERADA = "SOMA_PONDERADA"
MEDIA_PONDERADA = "MEDIA_PONDERADA"
PELA_SOMA_DOS_PESOS = "PELA_SOMA_DOS_PESOS"

SEM_PONTUACAO = object()
"""O que se devolve quando falta pontuação.

Distinto de `Decimal(0)`, e por isso irredutível a ele.
"""


def peso_da_etapa(etapa):
    """O peso publicado, ou 1 quando a Etapa não o declara.

    Ausência de peso é "pesa como as outras", e não "não pesa": um Edital que não declara peso
    nenhum tem Etapas equivalentes, e tratá-las como zero anularia a pontuação inteira.
    """
    bruto = etapa.get("weight")
    return Decimal("1") if bruto is None else Decimal(str(bruto))


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
    return _normalizar(marco, total, soma_dos_pesos, len(enumeradas))


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
