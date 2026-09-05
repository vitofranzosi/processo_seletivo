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
        "milestone": marco,
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


def comparar(*, gravado, atual, regra_gravada, regra_atual):
    """Diferenças relevantes entre o ato e a proposta de agora, em forma legível pela tela."""
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
        diferencas.append(
            {
                "tipo": "participantes_alterados",
                "descricao": "O conjunto de participantes considerados mudou.",
                "entraram": sorted(participantes_agora - participantes_antes),
                "sairam": sorted(participantes_antes - participantes_agora),
            }
        )

    resultados_antes = {item.get("id") for item in gravado.get("stageResults") or []}
    resultados_agora = {item.get("id") for item in atual.get("stageResults") or []}
    if resultados_antes != resultados_agora:
        diferencas.append(
            {
                "tipo": "resultados_alterados",
                "descricao": "Os Resultados oficiais do universo mudaram.",
                "entraram": sorted(resultados_agora - resultados_antes),
                "sairam": sorted(resultados_antes - resultados_agora),
            }
        )
    return diferencas


__all__ = ["comparar", "por_identidade", "recorte_da_regra"]
