"""Os conjuntos que a progressão consulta, e os Resultados que a presidência lê.

**Um conjunto por consulta, uma vez por listagem.** A 012 fechou a cadeia de autorização em duas
condições e manteve o impedimento fora dela por uma razão de escala — somá-lo custaria uma
verificação por linha em toda listagem. A progressão não reabre essa porta: quem desenha lista
resolve os dois conjuntos aqui, uma vez, e filtra; a rota individual pergunta pelo par, onde uma
consulta a mais não é gargalo.
"""

from processo_seletivo.resultados.models import ResultadoEtapa


def ha_resultado_em(*, edital, etapa_id):
    """A Etapa já começou a produzir Resultado?

    É o gate de D-003, e ele incide **apenas** sobre a exigência de habilitação. Enquanto a
    resposta é `False`, a Etapa seguinte conserva o conjunto da 012 — todas as submetidas, menos as
    eliminadas antes —, e é isso que impede esta feature de esvaziar permanentemente a Etapa
    seguinte de um Edital de leitura múltipla, que a V1 não consolida.
    """
    return ResultadoEtapa.objects.filter(edital=edital, etapa_id=etapa_id).exists()


def habilitadas_em(*, edital, etapa_id):
    """Identidades das inscrições com Resultado `HABILITADA` naquela Etapa."""
    return set(
        ResultadoEtapa.objects.filter(
            edital=edital,
            etapa_id=etapa_id,
            consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        ).values_list("inscricao_id", flat=True)
    )


def eliminadas_ate(*, edital, etapas_ids):
    """Identidades eliminadas em **qualquer** das Etapas dadas.

    Uma consulta para todas as anteriores, e não uma por Etapa: a exclusão é transitiva, e o custo
    dela não pode crescer com o número de Etapas já percorridas.
    """
    if not etapas_ids:
        return set()
    return set(
        ResultadoEtapa.objects.filter(
            edital=edital,
            etapa_id__in=list(etapas_ids),
            consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
        ).values_list("inscricao_id", flat=True)
    )


def resultados_por_inscricao(*, edital, etapa_id):
    """`{inscricao_id: ResultadoEtapa}` da Etapa — o que já foi consolidado."""
    return {
        resultado.inscricao_id: resultado
        for resultado in ResultadoEtapa.objects.filter(edital=edital, etapa_id=etapa_id)
    }
