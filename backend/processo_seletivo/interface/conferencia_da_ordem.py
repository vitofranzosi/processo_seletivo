"""O que a confirmação da ordem diz sobre quem fica sem posição (126, FR-4035 a FR-4038).

**A confirmação mostrava só as contagens.** No marco por pontuação de um Edital sem nenhuma Etapa
avaliada, ela dizia "com posição: 0; sem posição: 12" e oferecia "Emitir a ordem", irreversível. A
tela anterior lista o motivo de cada um; a confirmação, que é onde se decide, não dizia por que
todos ficavam de fora — e a ordem emitida assim fica obsoleta assim que os resultados chegam.

**Só leitura, da proposta que a confirmação já calculou.** Nada aqui recalcula a ordem nem consulta
o banco, e nada recusa: a recusa da emissão sem nenhum resultado, decidida pelo usuário (G-01), é
da `128`, no comando, e esta confirmação lê a mesma regra.

**"Sem resultado" é a chave da Etapa ausente em `pontuacoes`, e não o motivo gravado.** O motivo
("Sem pontuação nas Etapas enumeradas: X, Y.") lista também a Etapa decisória com resultado, porque
ela nunca tem pontuação; para contar quem está sem resultado, ele diria a mais. A chave existe
sempre que há Resultado vigente da Etapa, com ou sem pontuação (`universo_classificavel.preparar`).
"""

from processo_seletivo.classificacao.domain import universo_classificavel

ROTULOS_DA_CONSEQUENCIA = {
    "HABILITADA": "Habilitada",
    "ELIMINADA": "Eliminada",
    "RETIRADA_DA_RESERVA": "Retirada da reserva",
}


def resumo(proposta):
    """`{consideradas, sem_resultado, por_etapa, nenhuma_com_resultado, grupos}` da proposta.

    `por_etapa` é `[(nome publicado, quantas sem Resultado nela)]`, na ordem em que o marco enumera
    as Etapas, só as que têm alguém sem Resultado. `grupos` é `[(motivo, consequência, protocolos)]`
    dos sem posição, na ordem em que aparecem.
    """
    marco = proposta.get("marco") or {}
    etapas = proposta.get("etapas") or {}
    enumeradas = [str(item) for item in marco.get("stages") or []]
    posicoes = proposta.get("posicoes") or []
    sem_posicao = proposta.get("sem_posicao") or []
    # **A eliminada tem resultado** (FR-4038): é ele que a tirou da ordem.
    sem_resultado = [
        item
        for item in sem_posicao
        if not item.get("consequencia")
        and any(etapa not in (item.get("pontuacoes") or {}) for etapa in enumeradas)
    ]
    por_etapa = []
    for etapa in enumeradas:
        quantas = sum(1 for item in sem_resultado if etapa not in (item.get("pontuacoes") or {}))
        if quantas:
            nome = (etapas.get(etapa) or {}).get("name") or etapa
            por_etapa.append((nome, quantas))
    consideradas = len(posicoes) + len(sem_posicao)
    # **A mesma regra que recusa a emissão** (128, FR-4217): com ela, este caso deixa de chegar à
    # confirmação; se chegar por outro caminho, a frase daqui e a recusa do comando concordam.
    nenhuma_com_resultado = universo_classificavel.nenhuma_com_resultado(
        marco, list(posicoes) + list(sem_posicao)
    )
    grupos = {}
    for item in sem_posicao:
        chave = (item.get("motivo") or "", item.get("consequencia") or "")
        grupos.setdefault(chave, []).append(item.get("protocolo") or str(item.get("inscricao_id")))
    return {
        "consideradas": consideradas,
        "sem_resultado": len(sem_resultado),
        "por_etapa": por_etapa,
        "nenhuma_com_resultado": nenhuma_com_resultado,
        "grupos": [
            {
                "motivo": motivo,
                # O nome, e não o enum (164): "retirada_da_reserva" em minúsculas não é palavra.
                "consequencia": ROTULOS_DA_CONSEQUENCIA.get(consequencia, consequencia),
                "protocolos": protocolos,
            }
            for (motivo, consequencia), protocolos in grupos.items()
        ],
    }


__all__ = ["resumo"]
