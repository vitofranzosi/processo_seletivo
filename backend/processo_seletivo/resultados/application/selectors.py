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


def resultados_da_etapa(*, edital, etapa_id, consequencia=None, pagina=1):
    """Os Resultados da Etapa, com a proveniência ao lado — paginados.

    `select_related` até a versão: a norma histórica é alcançada **pela fonte**, e não copiada para
    o Resultado. Sem isto, reconstruir a decisão de mil Resultados custaria mil leituras de Versão
    Consolidada; com isto, custa a mesma consulta.
    """
    from django.core.paginator import Paginator

    consulta = ResultadoEtapa.objects.filter(edital=edital, etapa_id=etapa_id).select_related(
        "inscricao", "avaliacao", "avaliacao__versao", "avaliacao__atribuicao"
    )
    if consequencia:
        consulta = consulta.filter(consequencia=consequencia)
    paginas = Paginator(consulta.order_by("inscricao__protocolo", "inscricao_id"), 25)
    return paginas.get_page(pagina)


def contestacoes_supervenientes(resultados):
    """`{resultado_id: Impedimento}` para os Resultados cuja fonte foi depois alcançada.

    **Declaração, e não decisão.** Nada aqui altera pontuação ou consequência: o Resultado é
    histórico e permanece. O que muda é a leitura — quem consulta precisa saber que a origem foi
    contestada depois de consolidada, porque essa é a única forma pela qual a V1, sem anulação,
    registra que algo saiu errado (FR-032).

    Uma consulta para o conjunto, e não uma por linha.
    """
    from processo_seletivo.avaliacoes.models import Impedimento

    if not resultados:
        return {}
    pares = {
        (r.avaliacao.identity_subject, r.inscricao_id): r.id
        for r in resultados
        if r.avaliacao_id is not None
    }
    if not pares:
        return {}
    achados = Impedimento.objects.filter(
        identity_subject__in={subject for subject, _ in pares},
        inscricao_id__in={inscricao for _, inscricao in pares},
    )
    return {
        pares[(imp.identity_subject, imp.inscricao_id)]: imp
        for imp in achados
        if (imp.identity_subject, imp.inscricao_id) in pares
    }
