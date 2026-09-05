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


def inscricoes_com_resultado(*, edital, etapa_id):
    """As identidades já consolidadas nesta Etapa.

    Identidades, e não objetos: a prontidão só pergunta "já tem?", e materializar o modelo inteiro
    para responder a uma pergunta de pertinência é o que a 012 recusou ao fazer o resumo por
    agregação.
    """
    return set(
        ResultadoEtapa.objects.filter(edital=edital, etapa_id=etapa_id).values_list(
            "inscricao_id", flat=True
        )
    )


def conteudos_das_versoes(ids):
    """`{versao_id: conteúdo}` para as versões referenciadas — **uma linha por versão distinta**.

    Um Edital tem duas ou três Versões Consolidadas; mil avaliações apontam para elas. Trazer a
    versão junto de cada avaliação carregaria mil cópias do Edital inteiro em JSON, mais os bytes
    canônicos, para comparar quatro campos — e nenhum teste de contagem de consultas denunciaria,
    porque o número de consultas continuaria o mesmo.
    """
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    identidades = {identidade for identidade in ids if identidade is not None}
    if not identidades:
        return {}
    return dict(VersaoConsolidada.objects.filter(pk__in=identidades).values_list("id", "content"))


def vigencias_das_versoes(ids):
    """`{versao_id: valid_from}` para as versões referenciadas — **uma linha por versão distinta**.

    O irmão de `conteudos_das_versoes`, e existe pela mesma razão dita ao contrário: agora que a
    norma é campo do Resultado, `select_related("versao")` seria a leitura óbvia — e traria uma
    cópia do Edital inteiro em JSON, mais os bytes canônicos, **por linha da página**, para
    imprimir uma data. Nenhum teste de contagem de consultas denunciaria, porque o número de
    consultas continuaria o mesmo (D-1).
    """
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    identidades = {identidade for identidade in ids if identidade is not None}
    if not identidades:
        return {}
    return dict(
        VersaoConsolidada.objects.filter(pk__in=identidades).values_list("id", "valid_from")
    )


def resultados_da_etapa(*, edital, etapa_id, consequencia=None, pagina=1):
    """Os Resultados da Etapa, com a proveniência ao lado — paginados.

    **A norma vem do próprio Resultado**, e não mais por `avaliacao__versao`: desde D-1 ela é campo
    dele, e o Resultado por Ocorrência não tem Avaliação por onde alcançá-la. A junção que sobra é
    a da fonte, e ela é `LEFT` — a Ocorrência traz `avaliacao` nula, de propósito.

    `versao` fica **fora** do `select_related` de propósito: ver `vigencias_das_versoes`, que
    resolve a vigência uma vez por versão distinta em vez de uma cópia do Edital por linha.
    """
    from django.core.paginator import Paginator

    consulta = ResultadoEtapa.objects.filter(edital=edital, etapa_id=etapa_id).select_related(
        "inscricao", "avaliacao", "avaliacao__atribuicao"
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
