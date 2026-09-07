"""Os conjuntos que a progressão consulta, e os Resultados que a presidência lê.

**Todas as leituras daqui são de vigência**, e consomem o manager `ResultadoEtapa.vigentes` —
declarado no modelo, e não aqui: manager é do modelo, e o selector o consome. Um Resultado superado
por recurso deferido não habilita, não elimina, não conta como "já consolidado" e não aparece na
listagem da Etapa: ele é histórico, e histórico não produz efeito (018, T-004, FR-061).

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
    return ResultadoEtapa.vigentes.filter(edital=edital, etapa_id=etapa_id).exists()


def habilitadas_em(*, edital, etapa_id):
    """Identidades das inscrições com Resultado `HABILITADA` naquela Etapa."""
    return set(
        ResultadoEtapa.vigentes.filter(
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
        ResultadoEtapa.vigentes.filter(
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
        ResultadoEtapa.vigentes.filter(edital=edital, etapa_id=etapa_id).values_list(
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

    consulta = ResultadoEtapa.vigentes.filter(edital=edital, etapa_id=etapa_id).select_related(
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
    # **A chave inclui a Etapa**, e sem ela dois Resultados da mesma inscrição — em Etapas
    # diferentes, ou o superado e o superador do mesmo par — colidiriam, e um perderia a
    # marcação de contestação em silêncio. Antes da 018 a colisão era impossível pela unicidade
    # incondicional do par; agora ela é alcançável (018, T-004).
    pares = {
        (r.avaliacao.identity_subject, r.inscricao_id, r.etapa_id): r.id
        for r in resultados
        if r.avaliacao_id is not None
    }
    if not pares:
        return {}
    achados = Impedimento.objects.filter(
        identity_subject__in={subject for subject, _, _ in pares},
        inscricao_id__in={inscricao for _, inscricao, _ in pares},
    )
    # O `Impedimento` é por pessoa × inscrição, e não conhece Etapa: um impedimento alcança
    # **todos** os Resultados daquele par de pessoa e inscrição, e cada um recebe a sua marcação.
    return {
        identificador: imp
        for imp in achados
        for (subject, inscricao, _etapa), identificador in pares.items()
        if (subject, inscricao) == (imp.identity_subject, imp.inscricao_id)
    }


def resultados_visiveis(inscricao):
    """O que o titular pode consultar do próprio Resultado de Etapa, e sob que autorização.

    **O fato autorizador é um ato que já existe** (018, D-003): havendo `PublicacaoResultado`
    vigente de um marco do Perfil da Inscrição, e enumerando esse marco a Etapa N, o titular passa
    a ver o seu `ResultadoEtapa` vigente da Etapa N. Não é divulgação, não é ato novo e não nomeia
    terceiros — é acesso do titular ao próprio dado, autorizado por uma decisão que a instituição
    já tomou.

    **Alcança quem ficou fora do universo do ato**, e é essa a propriedade que a torna a resposta
    certa. `SituacaoDivulgada` só existe para quem estava no universo; quem foi eliminado numa Etapa
    anterior não tem linha lá, e por isso não via absolutamente nada — nem que houve resultado
    (E2E17-004). Aqui a porta é a **enumeração normativa** do marco, que não depende de quem
    participou do ato.

    **A enumeração vem da versão que o ato cita, e não da vigente.** É a norma que governou a
    publicação que autoriza mostrar; ler a vigente faria uma Retificação posterior alargar ou
    estreitar, em silêncio, o que já foi autorizado.

    Três consultas, e o número **não cresce** com a quantidade de marcos: as publicações, os
    conteúdos das versões distintas — por `conteudos_das_versoes`, e não por `select_related`, que
    traria uma cópia do Edital por linha — e os Resultados vigentes (T-009).
    """
    from processo_seletivo.classificacao.domain.universo import por_identidade
    from processo_seletivo.divulgacao.models import PublicacaoResultado

    publicacoes = list(
        PublicacaoResultado.objects.filter(
            # `edital_id`, e não `edital`: a segunda dispararia um carregamento tardio da
            # Inscrição só para chegar à chave que já está na linha. Uma consulta a mais por
            # acompanhamento aberto, invisível em qualquer perfil de tempo.
            edital_id=inscricao.edital_id,
            perfil_id=inscricao.profile_id,
            sucessoras__isnull=True,
        )
        .select_related("ato")
        .order_by("publicado_em")
    )
    if not publicacoes:
        return []

    conteudos = conteudos_das_versoes({p.ato.versao_id for p in publicacoes})
    etapas_autorizadas = {}
    for publicacao in publicacoes:
        conteudo = conteudos.get(publicacao.ato.versao_id) or {}
        perfil = por_identidade(conteudo.get("profiles"), publicacao.perfil_id)
        marco = por_identidade(
            perfil.get("classificationMilestones") if perfil else None, publicacao.marco_id
        )
        rotulos = {str(item.get("id")): item for item in conteudo.get("stages") or []}
        for etapa_id in (marco or {}).get("stages") or []:
            # Um marco basta para autorizar: dois marcos que enumerem a mesma Etapa não a mostram
            # duas vezes. O primeiro a chegar carrega o rótulo, e a ordem é a de publicação.
            etapas_autorizadas.setdefault(str(etapa_id), rotulos.get(str(etapa_id)) or {})

    if not etapas_autorizadas:
        return []

    resultados = (
        ResultadoEtapa.vigentes.filter(inscricao=inscricao, etapa_id__in=list(etapas_autorizadas))
        .select_related("resultado_anterior", "decisao")
        .order_by("consolidado_em")
    )
    return [
        {
            "etapa": (etapas_autorizadas.get(str(resultado.etapa_id)) or {}).get("name", ""),
            "ordem": (etapas_autorizadas.get(str(resultado.etapa_id)) or {}).get("order") or 0,
            "consequencia": resultado.consequencia,
            "habilitada": resultado.consequencia == ResultadoEtapa.Consequencia.HABILITADA,
            "motivo": resultado.motivo,
            # Só quando a forma a tiver: a Etapa decisória não produz número, e a Ocorrência não
            # produz grandeza nenhuma. Inventar um zero afirmaria o que ninguém mediu.
            "pontuacao": resultado.pontuacao,
            # **A superação precisa ser explicável a quem a recebe.** Mostrar a nota nova sem dizer
            # que ela mudou porque o recurso foi deferido transforma a correção em erro aparente
            # (D-003, FR-016).
            "corrigido": resultado.resultado_anterior_id is not None,
            "corrigido_em": resultado.consolidado_em if resultado.resultado_anterior_id else None,
        }
        for resultado in sorted(
            resultados,
            key=lambda item: (
                (etapas_autorizadas.get(str(item.etapa_id)) or {}).get("order") or 0,
                item.consolidado_em,
            ),
        )
    ]
