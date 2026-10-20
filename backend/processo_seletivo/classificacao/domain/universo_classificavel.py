"""Quem tem posição e quem não tem, a partir do que cada inscrito trouxe (094, D-004).

Função pura: recebe o marco e as Etapas do conteúdo publicado e os inscritos já lidos, e devolve
classificáveis e sem posição. Não consulta banco, não conhece modelo, não lê relógio.

**Existe para que haja uma montagem do universo só.** Ela morava dentro de `calcular_ordem`, e a
prévia da classificação precisa da mesma decisão sobre candidatos fictícios. Duas montagens
divergiriam na primeira regra nova de exclusão, em silêncio — e a prévia mostraria ao elaborador
uma ordem que o caminho oficial não produziria. A spec 094 tirou daqui as consultas e deixou a
regra; o caminho oficial e a prévia chamam esta função, e a equivalência entre os dois é teste.

**O recorte é parâmetro, e não só filtro de consulta.** No caminho oficial a consulta já filtrou, e
reaplicá-lo aqui é idempotente; é a prévia de um recorte reservado que vai depender dele.
"""

from processo_seletivo.classificacao.domain.combinacao import SEM_PONTUACAO, combinar

# O vocabulário da consequência, declarado aqui para que o módulo puro não importe modelo. Um teste
# prende que estes textos são os de `ResultadoEtapa.Consequencia`: divergir deles faria a eliminação
# gravada pela consolidação passar despercebida.
ELIMINADA = "ELIMINADA"
HABILITADA = "HABILITADA"


def preparar(marco, etapas, inscritos, *, recorte=None):
    """`(classificaveis, sem_posicao)` — o laço que `calcular_ordem` fazia, fora dele.

    `inscritos` traz, de cada um, `inscricao_id`, `protocolo`, `nome`, `identity_subject`,
    `modalidade_id`, `fatos` e `resultados` — os Resultados vigentes das Etapas enumeradas, cada um
    com `id`, `etapa_id`, `pontuacao`, `consequencia` e `motivo`. **A ordem dos inscritos é a do
    chamador, e a dos Resultados também**: as pontuações são indexadas por Etapa, e quando dois
    Resultados da mesma Etapa chegam, vale o último. O caminho oficial os ordena por
    `consolidado_em`, de modo que o último é o sucessor vigente.

    `RegraIncompleta` sobe sem captura, como sempre subiu: regra que não basta para calcular é
    defeito da publicação, e não um sem posição a mais.
    """
    enumeradas = [str(item) for item in marco.get("stages") or []]
    classificaveis, sem_posicao = [], []
    for inscrito in inscritos:
        if recorte is not None and inscrito["modalidade_id"] != str(recorte):
            continue
        resultados = inscrito["resultados"]
        pontuacoes = {
            str(resultado["etapa_id"]): resultado["pontuacao"] for resultado in resultados
        }
        base = {
            "inscricao_id": inscrito["inscricao_id"],
            "protocolo": inscrito["protocolo"],
            "nome": inscrito["nome"],
            "identity_subject": inscrito["identity_subject"],
            "modalidade_id": inscrito["modalidade_id"],
            "pontuacoes": pontuacoes,
            "fatos": inscrito["fatos"],
            "resultados": [str(resultado["id"]) for resultado in resultados],
        }
        eliminacao = _eliminacao_mais_recente(resultados, etapas)
        if eliminacao is not None:
            sem_posicao.append(
                {
                    **base,
                    "posicao": None,
                    "pontuacao": None,
                    "consequencia": eliminacao["consequencia"],
                    "motivo": eliminacao["motivo"],
                    "empate_residual": False,
                    "separado_por": None,
                }
            )
            continue

        pontuacao = combinar(marco, etapas, pontuacoes)
        if pontuacao is SEM_PONTUACAO:
            sem_posicao.append(
                {
                    **base,
                    "posicao": None,
                    "pontuacao": None,
                    "consequencia": "",
                    "motivo": _motivo_da_pontuacao_ausente(enumeradas, pontuacoes, etapas),
                    "empate_residual": False,
                    "separado_por": None,
                }
            )
            continue
        classificaveis.append(
            {
                **base,
                "pontuacao": pontuacao,
                "consequencia": HABILITADA,
                "motivo": "",
            }
        )
    return classificaveis, sem_posicao


def _eliminacao_mais_recente(resultados, etapas):
    eliminadas = [item for item in resultados if item["consequencia"] == ELIMINADA]
    if not eliminadas:
        return None
    return max(
        eliminadas,
        key=lambda item: (etapas.get(str(item["etapa_id"])) or {}).get("order") or 0,
    )


def _motivo_da_pontuacao_ausente(enumeradas, pontuacoes, etapas):
    # A Etapa decisória enumerada nunca tem pontuação e entra na lista também. É o texto que os atos
    # emitidos já gravaram, e mudá-lo aqui mudaria o motivo de quem recorre sobre o mesmo dado.
    faltantes = [
        (etapas.get(etapa_id) or {}).get("name") or etapa_id
        for etapa_id in enumeradas
        if pontuacoes.get(etapa_id) is None
    ]
    return "Sem pontuação nas Etapas enumeradas: " + ", ".join(faltantes) + "."


__all__ = ["ELIMINADA", "HABILITADA", "preparar"]
