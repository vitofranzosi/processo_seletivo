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

from collections import defaultdict

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
        # `decisao__recurso` entra na junção: o protocolo é o que identifica a decisão para quem a
        # recebe, e buscá-lo depois custaria uma consulta por Resultado corrigido — o tipo de custo
        # que só aparece quando o histórico cresce.
        .select_related("resultado_anterior", "decisao", "decisao__recurso")
        .order_by("consolidado_em")
    )
    return [
        {
            # O identificador vai no dicionário porque a tela precisa dele **no endereço** do
            # formulário de recurso — e endereço não é linguagem apresentada, que é a distinção
            # que a 017 já fixou. Nenhum template o imprime como texto.
            "id": resultado.id,
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
            #
            # E "explicável" não é uma frase genérica: quem recebe precisa saber **qual** decisão
            # corrigiu o seu Resultado e **quando** ela foi tomada. O protocolo é o identificador
            # humano dela — legível, ditável ao telefone e já conhecido de quem interpôs. O
            # identificador técnico da decisão não atravessa: ele não diz nada a quem lê, e a
            # FR-048 o mantém fora da linguagem institucional.
            "corrigido": resultado.resultado_anterior_id is not None,
            "corrigido_por": (resultado.decisao.recurso.protocolo if resultado.decisao_id else ""),
            # O instante **da decisão**, e não o da gravação do Resultado: é a decisão que corrige,
            # e é a data dela que o candidato reconhece.
            "corrigido_em": resultado.decisao.decidido_em if resultado.decisao_id else None,
        }
        for resultado in sorted(
            resultados,
            key=lambda item: (
                (etapas_autorizadas.get(str(item.etapa_id)) or {}).get("order") or 0,
                item.consolidado_em,
            ),
        )
    ]


def historico_do_par(inscricao_id, etapa_id):
    """Os Resultados do par, do mais antigo ao vigente — **e é aqui que o superado é lido**.

    A segunda exceção declarada do contrato de vigência, e por uma razão simétrica à primeira: as
    outras leituras respondem "o que vale hoje", e esta responde "o que já valeu". Filtrá-la por
    vigência devolveria uma linha só e destruiria justamente a informação que ela existe para dar
    (FR-064, T-004).

    O que cada linha carrega é o que permite conferir a correção sem sair da tela: consequência,
    pontuação, motivo, quem consolidou, quando — e, no sucessor, a decisão que o autorizou.

    A cadeia é percorrida por `resultado_anterior`, e não ordenada por instante: dois Resultados do
    mesmo par gravados no mesmo segundo teriam ordem indefinida, e a sucessão é o que define a
    ordem de verdade.
    """
    return historicos_dos_pares([inscricao_id], etapa_id).get(inscricao_id, [])


def historicos_dos_pares(inscricao_ids, etapa_id):
    """O mesmo histórico, para **vários pares numa consulta só** — `{inscricao_id: [linhas]}`.

    A leitura por par existe e continua correta; o que ela não suporta é o painel da Etapa, que a
    chamava uma vez por linha corrigida. Com metade das vinte e cinco linhas de uma página vindas
    de recurso deferido, a tela pagava mais de uma dezena de leituras extras — e o custo crescia
    com o **sucesso** dos recursos, que é o que a instituição espera que aconteça (FR-061).

    A montagem da cadeia continua sendo por `resultado_anterior`, par a par, e não por instante:
    dois Resultados do mesmo par gravados no mesmo segundo teriam ordem indefinida, e é a sucessão
    que define a ordem de verdade.

    Lista vazia não consulta: o painel sem correção nenhuma é o caso comum, e pagar uma leitura
    para descobrir que não há o que ler é o custo que este selector existe para tirar.
    """
    identidades = [identidade for identidade in inscricao_ids if identidade is not None]
    if not identidades:
        return {}

    linhas = list(
        ResultadoEtapa.objects.filter(inscricao_id__in=identidades, etapa_id=etapa_id)
        .select_related("decisao", "decisao__recurso")
        .order_by("consolidado_em", "id")
    )
    por_inscricao = defaultdict(list)
    for item in linhas:
        por_inscricao[item.inscricao_id].append(item)
    return {
        identidade: _cadeia_do_par(do_par) for identidade, do_par in por_inscricao.items() if do_par
    }


def _cadeia_do_par(linhas):
    por_anterior = {item.resultado_anterior_id: item for item in linhas}
    corrente = por_anterior.get(None)
    cadeia = []
    while corrente is not None and len(cadeia) <= len(linhas):
        cadeia.append(corrente)
        corrente = por_anterior.get(corrente.id)
    if not cadeia:
        return []
    return [_linha_do_historico(item, ultimo=item is cadeia[-1]) for item in cadeia]


def _linha_do_historico(resultado, *, ultimo):
    decisao = resultado.decisao
    return {
        "resultado": resultado,
        "vigente": ultimo,
        "consequencia": resultado.consequencia,
        "pontuacao": resultado.pontuacao,
        "motivo": resultado.motivo,
        "origem": resultado.origem,
        "consolidado_por": resultado.consolidado_por,
        "consolidado_em": resultado.consolidado_em,
        "motivo_da_superacao": resultado.motivo_da_superacao,
        "decisao": decisao,
        "recurso": decisao.recurso.protocolo if decisao is not None else "",
    }


def reabilitadas_por_recurso(*, edital, etapa_ids=None):
    """`{inscricao_id: resultado}` de quem voltou a participar porque um recurso a reabilitou.

    **Derivada, e sem estado de reintegração** (D-010, FR-076). Reabilitada é quem tem, hoje, um
    Resultado vigente que é **sucessor** e cuja consequência habilita. Não há "reintegrada": há um
    Resultado que sucedeu outro e que diz que a pessoa segue.

    Uma coluna de reintegração teria de ser mantida coerente com a cadeia de sucessão, e divergiria
    dela no primeiro caso em que o sucessor fosse ele próprio sucedido. A derivação não tem como
    divergir: ela **é** a cadeia.

    Uma consulta, e não uma por inscrição: quem chama é uma tela de Etapa, que lista dezenas.
    """
    consulta = ResultadoEtapa.vigentes.filter(
        edital=edital,
        resultado_anterior__isnull=False,
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
    ).select_related("decisao", "decisao__recurso", "resultado_anterior")
    if etapa_ids is not None:
        consulta = consulta.filter(etapa_id__in=list(etapa_ids))
    return {
        resultado.inscricao_id: resultado
        for resultado in consulta
        # **Só reabilita quem estava fora.** Corrigir a nota de quem já seguia é superação, e não
        # reingresso: nomeá-la como reabilitação faria a tela avisar sobre quem nunca saiu.
        if resultado.resultado_anterior.consequencia != ResultadoEtapa.Consequencia.HABILITADA
    }


def reabilitacao_da_inscricao(resultado):
    """A linha como as telas da operação a mostram: o que mudou, por qual recurso e quando.

    A data é a do **deferimento**, e não a da consolidação do sucessor: é a decisão que reabilitou,
    e é por ela que quem opera vai procurar quando quiser conferir (FR-077).
    """
    decisao = resultado.decisao
    return {
        "resultado": resultado,
        "recurso": decisao.recurso.protocolo if decisao is not None else "",
        "deferido_em": decisao.decidido_em if decisao is not None else None,
        "consequencia_anterior": resultado.resultado_anterior.consequencia,
    }
