"""Qual é a Etapa anterior — e quais são todas as anteriores.

Função pura sobre o conteúdo publicado: recebe `{UUID: Etapa}` como `etapas_vigentes` devolve, e
responde sem tocar banco. Quem consulta Resultados é o seletor da camada de aplicação, e a
separação não é purismo: a escolha da Etapa anterior é lógica sobre conteúdo normativo e merece
teste sem banco; a leitura dos conjuntos é consulta e merece teste de custo.

**A anterior é a de maior `order` estritamente menor — nunca `order - 1`.** A ordem publicada não é
contígua: a Retificação pode remover uma Etapa do conteúdo sem reordenar as demais, e `order - 1`
apontaria para o vazio, fazendo a Etapa 3 se comportar como se fosse a primeira.

**Duas regras vivem aqui, e elas têm alcances diferentes** (013, D-003):

1. a **eliminação** em qualquer Etapa anterior exclui, sempre — por isso `etapas_anteriores` no
   plural existe;
2. a **exigência de habilitação** é da imediatamente anterior, e só vale depois que ela produz
   Resultado — por isso `etapa_anterior` no singular existe.

Fundi-las custou um buraco concreto: eliminada na Etapa 1, com a Etapa 2 ainda não consolidada, a
inscrição reaparecia na Etapa 3.
"""

from uuid import UUID


def _identidade(valor):
    """A identidade como `etapas_vigentes` a chaveia.

    `etapas_vigentes` devolve `{UUID: dados}`, e `etapa["id"]` vem do JSON publicado como
    **string**. Sem normalizar, a busca não acha a Etapa corrente e a função responde "não há
    anterior" para todas — a progressão inteira ficaria silenciosamente inerte, que é o pior modo
    de falhar: nada quebra, e a eliminação simplesmente não produz efeito.
    """
    if isinstance(valor, UUID):
        return valor
    try:
        return UUID(str(valor))
    except (AttributeError, TypeError, ValueError):
        return None


def _ordem(etapa):
    valor = etapa.get("order") if isinstance(etapa, dict) else None
    return valor if isinstance(valor, int) and not isinstance(valor, bool) else 0


def etapas_anteriores(etapas_vigentes, etapa_id):
    """As Etapas de `order` menor, da **mais próxima para a mais distante**.

    Devolve lista vazia para a primeira Etapa e para identidade ausente do vigente — nos dois casos
    não há anterior, e inventar uma seria pior do que não ter.
    """
    alvo = _identidade(etapa_id)
    corrente = etapas_vigentes.get(alvo)
    if corrente is None:
        return []
    limite = _ordem(corrente)
    anteriores = [
        (identidade, etapa)
        for identidade, etapa in etapas_vigentes.items()
        if _identidade(identidade) != alvo and _ordem(etapa) < limite
    ]
    anteriores.sort(key=lambda par: _ordem(par[1]), reverse=True)
    return anteriores


def etapa_anterior(etapas_vigentes, etapa_id):
    """`(identidade, Etapa)` imediatamente anterior, ou `None` na primeira."""
    anteriores = etapas_anteriores(etapas_vigentes, etapa_id)
    return anteriores[0] if anteriores else None
