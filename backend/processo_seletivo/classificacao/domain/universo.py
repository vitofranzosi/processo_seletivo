"""O recorte que torna a obsolescência uma comparação, e não estado a manter.

O ato guarda identidades e aponta a versão histórica. A regra continua tendo uma fonte só: o
conteúdo publicado. Para saber se o vigente ficou para trás, comparamos apenas o marco e as Etapas
que ele enumera — Retificação alheia ao recorte não obsoleta esta ordem.
"""

from processo_seletivo.shared.canonical import canonical_sha256


def por_identidade(itens, identidade):
    alvo = str(identidade)
    return next((item for item in itens or [] if str(item.get("id")) == alvo), None)


def recorte_da_regra(conteudo, *, perfil_id, marco_id):
    """A norma relevante para um marco, ou ``None`` quando ele não existe nesta versão."""
    perfil = por_identidade(conteudo.get("profiles"), perfil_id)
    marco = por_identidade(
        perfil.get("classificationMilestones") if perfil else None,
        marco_id,
    )
    if marco is None:
        return None
    etapas = {str(item.get("id")): item for item in conteudo.get("stages") or []}
    enumeradas = [str(item) for item in marco.get("stages") or []]
    return {
        # **Sem a regra de corte** (014, FR-205). Ela mora no mesmo objeto desde o degrau 13, e não
        # é insumo da ordem: o corte **lê** a ordem, e não a produz. Mantê-la aqui fazia retificar
        # `targetCount` obsoletar o ato de ordenação — e como não se corta sobre ordem obsoleta,
        # a sucessão da geração por Retificação da regra, que a `FR-205` descreve, ficava
        # inalcançável: exigia emitir ordem nova que sairia byte a byte igual à anterior.
        "milestone": {chave: valor for chave, valor in marco.items() if chave != "cutRule"},
        # O peso vive na Etapa, fora do marco, e por isso precisa entrar explicitamente no
        # recorte. Os demais campos preservam a interpretação de porta/parcela e a ordem.
        "stages": [
            {
                "id": etapa_id,
                "weight": (etapas.get(etapa_id) or {}).get("weight"),
                "forma": (etapas.get(etapa_id) or {}).get("forma"),
                "classificatory": (etapas.get(etapa_id) or {}).get("classificatory"),
                "order": (etapas.get(etapa_id) or {}).get("order"),
            }
            for etapa_id in enumeradas
        ],
    }


REINGRESSO = "participante reingressou"
# A causa irmã, e a que aparece primeiro na prática: o deferimento que **corrige** a nota de quem
# já participava não muda o conjunto de participantes — muda quais Resultados o universo cita. Sem
# nomeá-la, a tela diria "os Resultados oficiais mudaram" e quem lê sairia procurando por quê, que
# é exatamente o que a FR-078 recusa. A reintegração de quem estava fora é a outra metade, e tem
# nome próprio porque é outra coisa: ali muda quem participa, e não o que se cita.
SUPERACAO = "resultado superado por recurso"


def comparar(*, gravado, atual, regra_gravada, regra_atual, reingressos=frozenset()):
    """Diferenças relevantes entre o ato e a proposta de agora, em forma legível pela tela.

    `reingressos` são as inscrições cujo Resultado vigente é **sucessor** de outro — quem voltou ao
    universo porque um recurso removeu a eliminação que a excluía. Sem esse conjunto, a divergência
    diria apenas "o conjunto de participantes mudou", e quem lê a tela do marco teria de sair
    procurando por quê. Nomear a causa é o que transforma um aviso genérico em informação
    acionável (FR-078).

    O conjunto vem de **fora** de propósito: `comparar` é função pura sobre dois universos e uma
    regra, e ensiná-la a consultar recursos a faria conhecer um agregado de outro app para produzir
    uma frase.
    """
    diferencas = []
    if regra_atual is None:
        diferencas.append(
            {"tipo": "regra_ausente", "descricao": "O marco não existe na norma vigente."}
        )
        return diferencas
    if regra_gravada is None or canonical_sha256(regra_gravada) != canonical_sha256(regra_atual):
        diferencas.append(
            {"tipo": "regra_alterada", "descricao": "A regra publicada do marco mudou."}
        )

    participantes_antes = set(gravado.get("participants") or [])
    participantes_agora = set(atual.get("participants") or [])
    if participantes_antes != participantes_agora:
        entraram = sorted(participantes_agora - participantes_antes)
        reingressaram = [str(item) for item in entraram if str(item) in reingressos]
        diferencas.append(
            {
                "tipo": "participantes_alterados",
                "descricao": (
                    f"O conjunto de participantes considerados mudou: {REINGRESSO}."
                    if reingressaram
                    else "O conjunto de participantes considerados mudou."
                ),
                "causa": REINGRESSO if reingressaram else "",
                "entraram": entraram,
                "reingressaram": reingressaram,
                "sairam": sorted(participantes_antes - participantes_agora),
            }
        )

    resultados_antes = {item.get("id") for item in gravado.get("stageResults") or []}
    resultados_agora = {item.get("id") for item in atual.get("stageResults") or []}
    if resultados_antes != resultados_agora:
        entrantes = [
            item
            for item in atual.get("stageResults") or []
            if item.get("id") in (resultados_agora - resultados_antes)
        ]
        superados = [item for item in entrantes if str(item.get("registrationId")) in reingressos]
        diferencas.append(
            {
                "tipo": "resultados_alterados",
                "descricao": (
                    f"Os Resultados oficiais do universo mudaram: {SUPERACAO}."
                    if superados
                    else "Os Resultados oficiais do universo mudaram."
                ),
                "causa": SUPERACAO if superados else "",
                "entraram": sorted(resultados_agora - resultados_antes),
                "sairam": sorted(resultados_antes - resultados_agora),
            }
        )
    return diferencas


__all__ = ["REINGRESSO", "SUPERACAO", "comparar", "por_identidade", "recorte_da_regra"]
