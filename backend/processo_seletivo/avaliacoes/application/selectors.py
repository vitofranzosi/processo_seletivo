"""A organização do trabalho — por agregação, e nunca por laço.

A escala desta feature é de mil inscrições e quarenta avaliadores, e ela decide o desenho: as
contagens saem de `GROUP BY`, a lista de inscrições é paginada, e nenhuma consulta chama o guard da
autorização por linha (P-004, FR-048, FR-049).

A pergunta que esta tela existe para responder, antes do detalhe: **o que falta**. Quantas
inscrições ainda não têm avaliador suficiente, quantas cada pessoa recebeu, e quantas faltam para
cumprir o que a Etapa declarou (FR-014).
"""

from uuid import UUID

from django.core.paginator import Paginator
from django.db.models import Count, Max, Prefetch, Q

from processo_seletivo.avaliacoes.domain.previsao import avaliacoes_previstas
from processo_seletivo.avaliacoes.models import (
    Atribuicao,
    Avaliacao,
    ConclusaoAvaliacao,
    Impedimento,
)
from processo_seletivo.comissoes.models import AlocacaoEtapa
from processo_seletivo.inscricoes.models import Inscricao

POR_PAGINA = 25

# Os três estados de cobertura de uma inscrição. São derivados da contagem, e não persistidos:
# guardar "está coberta" criaria estado a manter em toda distribuição e toda remoção.
SEM_NENHUM = "sem_nenhum"
INCOMPLETA = "incompleta"
COMPLETA = "completa"


def carga_por_avaliador(*, edital, etapa_id):
    """Quantas atribuições ativas cada pessoa alocada tem — inclusive quem tem zero.

    Quem está alocado e não recebeu nada é justamente quem a presidência procura, então a lista
    parte da **alocação** e traz a contagem, em vez de partir das atribuições e perder quem não
    tem nenhuma.
    """
    alocados = (
        AlocacaoEtapa.objects.filter(edital=edital, etapa_id=etapa_id, ativo=True)
        .select_related("membro")
        .order_by("membro__identity_subject")
    )
    contagem = dict(
        Atribuicao.objects.filter(edital=edital, etapa_id=etapa_id, ativo=True)
        .values_list("membro_id")
        .annotate(total=Count("id"))
        .values_list("membro_id", "total")
    )
    concluidas = dict(
        Avaliacao.objects.filter(
            atribuicao__edital=edital,
            atribuicao__etapa_id=etapa_id,
            atribuicao__ativo=True,
            estado=Avaliacao.Estado.CONCLUIDA,
        )
        .values_list("atribuicao__membro_id")
        .annotate(total=Count("id"))
        .values_list("atribuicao__membro_id", "total")
    )
    return [
        {
            "membro": alocacao.membro,
            "atribuidas": contagem.get(alocacao.membro_id, 0),
            "concluidas": concluidas.get(alocacao.membro_id, 0),
        }
        for alocacao in alocados
    ]


def _cobertura(atribuidas, previstas):
    if atribuidas == 0:
        return SEM_NENHUM
    return COMPLETA if atribuidas >= previstas else INCOMPLETA


def inscricoes_da_etapa(*, edital, etapa, pagina=1, cobertura=None, avaliador=None):
    """As inscrições submetidas do Edital, com quantas avaliações cada uma já tem.

    Paginada e filtrável (FR-049): mil inscrições não cabem numa tela, e a pergunta operacional
    quase nunca é "todas" — é "quais ainda não têm ninguém" ou "quais são de fulano".
    """
    previstas = avaliacoes_previstas(etapa)
    consulta = (
        Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA)
        .annotate(
            atribuidas=Count(
                "atribuicoes",
                filter=Q(atribuicoes__etapa_id=etapa["id"], atribuicoes__ativo=True),
                distinct=True,
            )
        )
        .prefetch_related(
            # Quem já avalia cada inscrição, para que a tela ofereça a remoção sem uma consulta
            # por linha. O `Prefetch` traz o membro junto, senão a listagem paga N+1 no rótulo.
            Prefetch(
                "atribuicoes",
                queryset=Atribuicao.objects.filter(etapa_id=etapa["id"], ativo=True)
                .select_related("membro")
                .order_by("membro__identity_subject"),
                to_attr="atribuicoes_da_etapa",
            )
        )
        .order_by("protocolo", "id")
    )
    if avaliador:
        consulta = consulta.filter(
            atribuicoes__membro__identity_subject=avaliador,
            atribuicoes__etapa_id=etapa["id"],
            atribuicoes__ativo=True,
        )
    if cobertura == SEM_NENHUM:
        consulta = consulta.filter(atribuidas=0)
    elif cobertura == INCOMPLETA:
        consulta = consulta.filter(atribuidas__gt=0, atribuidas__lt=previstas)
    elif cobertura == COMPLETA:
        consulta = consulta.filter(atribuidas__gte=previstas)
    paginas = Paginator(consulta, POR_PAGINA)
    pagina_atual = paginas.get_page(pagina)
    linhas = [
        {
            "inscricao": inscricao,
            "atribuidas": inscricao.atribuidas,
            "faltam": max(previstas - inscricao.atribuidas, 0),
            "cobertura": _cobertura(inscricao.atribuidas, previstas),
            "atribuicoes": inscricao.atribuicoes_da_etapa,
        }
        for inscricao in pagina_atual
    ]
    return linhas, pagina_atual


def resumo_da_etapa(*, edital, etapa):
    """O que falta, em três números — antes do detalhe (FR-014).

    Uma consulta agregada sobre as inscrições submetidas, e não um laço sobre elas: com mil
    inscrições, contar em Python custaria mil objetos para produzir três inteiros.
    """
    previstas = avaliacoes_previstas(etapa)
    por_inscricao = (
        Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA)
        .annotate(
            atribuidas=Count(
                "atribuicoes",
                filter=Q(atribuicoes__etapa_id=etapa["id"], atribuicoes__ativo=True),
                distinct=True,
            )
        )
        .aggregate(
            total=Count("id"),
            sem_nenhum=Count("id", filter=Q(atribuidas=0)),
            completas=Count("id", filter=Q(atribuidas__gte=previstas)),
        )
    )
    total = por_inscricao["total"]
    completas = por_inscricao["completas"]
    return {
        "previstas": previstas,
        "inscricoes": total,
        "sem_nenhum": por_inscricao["sem_nenhum"],
        "completas": completas,
        # "Sem avaliador suficiente" é a pergunta da véspera do prazo (EC-001), e ela não é a
        # mesma que "sem nenhum": uma inscrição com uma das duas avaliações também está carente.
        "carentes": total - completas,
        "atribuicoes": Atribuicao.objects.filter(
            edital=edital, etapa_id=etapa["id"], ativo=True
        ).count(),
    }


# Os dois filtros da Mesa. São derivados do estado da Avaliação, e não colunas: "pendente" é a
# ausência de conclusão, e persistí-la criaria estado a manter a cada gravação (FR-021).
PENDENTES = "pendentes"
CONCLUIDAS = "concluidas"


def mesa(*, ator, edital, etapa_id, pagina=1, filtro=None):
    """A lista de trabalho de quem avalia: **todas e somente** as inscrições dela (FR-020).

    A autorização vem da forma **em lote** que a 011 entregou — `etapas_autorizadas` responde a
    mesma regra do guard para o conjunto, numa leitura só. Chamar `pode_atuar_na_etapa` aqui faria
    dele o gargalo da feature: com quinhentas atribuições seriam quinhentas verificações para
    responder uma pergunta que já foi respondida (FR-024, FR-048).

    Devolve `(linhas, pagina, contagens)`. `None` no lugar da página significa que esta pessoa não
    atua nesta Etapa — quem chama decide se isso é 404 ou estado vazio, porque a distinção é da
    tela: alcançar a Etapa é da alocação, alcançar a inscrição é da Atribuição (FR-023).
    """
    from processo_seletivo.comissoes.domain.autorizacao import etapas_autorizadas, membro_ativo

    # `etapas_autorizadas` devolve `UUID`, e o identificador chega como texto quando o chamador não
    # é a rota — comparar sem normalizar responderia "sem acesso" **em silêncio**, que é o pior
    # modo de falha possível para uma verificação de autorização.
    identidade_da_etapa = etapa_id if isinstance(etapa_id, UUID) else UUID(str(etapa_id))
    if identidade_da_etapa not in etapas_autorizadas(ator, edital):
        return None, None, None
    membro = membro_ativo(ator, edital.processo)
    minhas = Atribuicao.objects.filter(
        membro=membro, edital=edital, etapa_id=identidade_da_etapa, ativo=True
    ).select_related("inscricao", "avaliacao")
    contagens = minhas.aggregate(
        total=Count("id"),
        concluidas=Count("id", filter=Q(avaliacao__estado=Avaliacao.Estado.CONCLUIDA)),
    )
    contagens["pendentes"] = contagens["total"] - contagens["concluidas"]
    if filtro == CONCLUIDAS:
        minhas = minhas.filter(avaliacao__estado=Avaliacao.Estado.CONCLUIDA)
    elif filtro == PENDENTES:
        minhas = minhas.exclude(avaliacao__estado=Avaliacao.Estado.CONCLUIDA)
    paginas = Paginator(minhas.order_by("inscricao__protocolo", "inscricao_id"), POR_PAGINA)
    pagina_atual = paginas.get_page(pagina)
    linhas = [
        {
            "atribuicao": atribuicao,
            "inscricao": atribuicao.inscricao,
            "avaliacao": getattr(atribuicao, "avaliacao", None),
            "concluida": getattr(atribuicao, "avaliacao", None) is not None
            and atribuicao.avaliacao.estado == Avaliacao.Estado.CONCLUIDA,
        }
        for atribuicao in pagina_atual
    ]
    return linhas, pagina_atual, contagens


def avaliacoes_elegiveis(*, edital, etapa_id, inscricao_id=None):
    """**O contrato que a 013 herda** (contrato §6).

    As Avaliações concluídas, sob Atribuição **ativa**, cada uma com autoria, instante e a Versão
    Consolidada que a governou. O que está fora deste conjunto está fora por ato nomeado, com autor
    e motivo — nunca por efeito colateral de reorganizar o trabalho (FR-092, FR-093).

    A `012` para aqui: ela não soma, não tira média, não conta quórum e não diz se alguém está
    apto. Transformar isto em consequência é da feature seguinte (FR-037, P-006).
    """
    consulta = Avaliacao.objects.filter(
        atribuicao__edital=edital,
        atribuicao__etapa_id=etapa_id,
        atribuicao__ativo=True,
        estado=Avaliacao.Estado.CONCLUIDA,
    ).select_related("atribuicao", "atribuicao__inscricao", "versao")
    if inscricao_id is not None:
        consulta = consulta.filter(inscricao_id=inscricao_id)
    return consulta.order_by("atribuicao__inscricao__protocolo", "concluida_em")


def avaliacoes_inelegiveis(*, edital, etapa_id, pagina=1):
    """As que ficaram de fora — **com o ato, o autor e o motivo ao lado** (FR-093).

    Invalidação apenas registrada não impede seleção silenciosa; invalidação **visível** impede. É
    por isso que este seletor não devolve só as linhas: ele traz o `AtoAdministrativo` que as tirou
    do conjunto, que é onde o motivo obrigatório está.

    **Paginada** (FR-049), ainda que na prática ela seja curta: o que entra aqui entra por ato de
    exceção. "Na prática é curta" é suposição sobre o uso, e uma Etapa que troque a banca inteira a
    torna longa de uma vez — que é justamente a hora em que alguém vai querer lê-la.
    """
    from processo_seletivo.processos.models import AtoAdministrativo

    paginas = Paginator(
        Avaliacao.objects.filter(
            atribuicao__edital=edital,
            atribuicao__etapa_id=etapa_id,
            atribuicao__ativo=False,
            estado=Avaliacao.Estado.CONCLUIDA,
        )
        .select_related("atribuicao", "atribuicao__inscricao", "atribuicao__membro", "versao")
        .order_by("atribuicao__inscricao__protocolo", "atribuicao_id"),
        POR_PAGINA,
    )
    pagina_atual = paginas.get_page(pagina)
    atos = {}
    for ato in AtoAdministrativo.objects.filter(
        aggregate_type="Atribuicao",
        aggregate_id__in=[avaliacao.atribuicao_id for avaliacao in pagina_atual],
    ).order_by("occurred_at"):
        atos[ato.aggregate_id] = ato
    linhas = [
        {
            "avaliacao": avaliacao,
            "inscricao": avaliacao.atribuicao.inscricao,
            "membro": avaliacao.atribuicao.membro,
            "ato": atos.get(avaliacao.atribuicao_id),
        }
        for avaliacao in pagina_atual
    ]
    return linhas, pagina_atual


def conclusoes_preservadas(*, edital, etapa_id, inscricao_id=None, pagina=1):
    """O que havia sido concluído — **consultável**, e não apenas existente no banco (FR-091).

    Sem esta consulta a preservação de FR-094 era uma promessa que só o banco cumpria. Depois de
    uma reabertura a Avaliação corrente volta a rascunho e perde pontuação, versão e instante; a
    linha some da consulta de inelegíveis, e a pergunta que um recurso faz — "o que aquela pessoa
    havia registrado, quando e sob qual versão" — deixava de ter resposta pela interface.

    A trilha **não** responde por isto, e é de propósito: ela guarda que o ato aconteceu e nunca a
    pontuação nem o parecer (FR-054). O conteúdo vive aqui, no registro append-only do domínio.

    **Paginada, como as outras listagens da feature** (FR-048). Este acervo é o maior de todos:
    cresce com toda conclusão de toda Atribuição da Etapa, e mais uma linha a cada reabertura —
    numa Etapa de mil inscrições com dupla avaliação, são dois mil registros de partida. Devolver
    o conjunto inteiro numa página faria a tela que existe para responder a recurso ser a mais
    pesada da 012.

    Cada linha diz também **o que aconteceu com aquela conclusão**, porque preservar não é o mesmo
    que continuar valendo:

    - `em_vigor` — é a conclusão corrente, sob Atribuição ativa;
    - `reaberta` — foi substituída por reabertura, e a Avaliação voltou a ser trabalho pendente;
    - `inelegivel` — continua sendo a conclusão corrente, e a Atribuição foi inativada por ato
      nomeado: ela permanece íntegra e fora do conjunto que a 013 consome (FR-075, FR-093).
    """
    consulta = ConclusaoAvaliacao.objects.filter(
        avaliacao__atribuicao__edital=edital,
        avaliacao__atribuicao__etapa_id=etapa_id,
    ).select_related(
        "avaliacao",
        "avaliacao__atribuicao",
        "avaliacao__atribuicao__inscricao",
        "avaliacao__atribuicao__membro",
        "versao",
    )
    if inscricao_id is not None:
        consulta = consulta.filter(avaliacao__atribuicao__inscricao_id=inscricao_id)
    paginas = Paginator(
        consulta.order_by("avaliacao__atribuicao__inscricao__protocolo", "avaliacao_id", "ordem"),
        POR_PAGINA,
    )
    pagina_atual = paginas.get_page(pagina)
    # A última ordem de cada Avaliação, por agregação e não por laço: só ela pode estar em vigor —
    # as anteriores foram, cada uma, substituídas por uma reabertura. Deduzir isso das linhas da
    # página estaria errado, porque a conclusão mais recente pode estar na página seguinte.
    ultima = dict(
        ConclusaoAvaliacao.objects.filter(
            avaliacao_id__in=[conclusao.avaliacao_id for conclusao in pagina_atual]
        )
        .values_list("avaliacao_id")
        .annotate(ultima=Max("ordem"))
    )
    linhas = []
    for conclusao in pagina_atual:
        avaliacao = conclusao.avaliacao
        atribuicao = avaliacao.atribuicao
        corrente = (
            conclusao.ordem == ultima[conclusao.avaliacao_id]
            and avaliacao.estado == Avaliacao.Estado.CONCLUIDA
        )
        linhas.append(
            {
                "conclusao": conclusao,
                "inscricao": atribuicao.inscricao,
                "membro": atribuicao.membro,
                "situacao": (
                    "em_vigor"
                    if corrente and atribuicao.ativo
                    else "inelegivel"
                    if corrente
                    else "reaberta"
                ),
            }
        )
    return linhas, pagina_atual


def rotulos_dos_agregados(registros):
    """A que cada evento da trilha se refere — em nome de gente, e não em identificador.

    A trilha nomeia a operação e o tipo do agregado, e o identificador que ela guarda é um UUID
    que a tela não mostrava. Quem lê via "Conclusão de avaliação, por joao" sem saber **de qual
    inscrição** — e a pergunta que traz alguém à trilha é quase sempre sobre uma inscrição.

    Resolver por evento seria uma consulta por linha. Aqui são três, uma por tipo de agregado,
    qualquer que seja o tamanho da página (FR-048).
    """
    por_tipo = {}
    for registro in registros:
        por_tipo.setdefault(registro.aggregate_type, []).append(registro.aggregate_id)
    rotulos = {}
    for atribuicao in Atribuicao.objects.filter(
        id__in=por_tipo.get("Atribuicao", [])
    ).select_related("inscricao", "membro"):
        rotulos[atribuicao.id] = _rotulo(atribuicao.inscricao, atribuicao.membro.identity_subject)
    for avaliacao in Avaliacao.objects.filter(id__in=por_tipo.get("Avaliacao", [])).select_related(
        "atribuicao__inscricao"
    ):
        rotulos[avaliacao.id] = _rotulo(avaliacao.atribuicao.inscricao, avaliacao.identity_subject)
    for impedimento in Impedimento.objects.filter(
        id__in=por_tipo.get("Impedimento", [])
    ).select_related("inscricao"):
        rotulos[impedimento.id] = _rotulo(impedimento.inscricao, impedimento.identity_subject)
    return rotulos


def _rotulo(inscricao, subject):
    """A inscrição pelo protocolo, que é o que a pessoa tem em mãos ao perguntar."""
    return f"inscrição {inscricao.protocolo or inscricao.id} — {subject}"


def atribuicoes_orfas(*, edital, etapa_id):
    """Atribuições ativas de quem já não está alocado na Etapa (EC-003).

    A revogação é computada, e por isso as linhas continuam ativas e inertes: elas não somem, e
    quem organiza precisa vê-las para redistribuir. É a diferença entre "o acesso acabou" e "o
    trabalho desapareceu".
    """
    alocados = set(
        AlocacaoEtapa.objects.filter(edital=edital, etapa_id=etapa_id, ativo=True).values_list(
            "membro_id", flat=True
        )
    )
    return [
        atribuicao
        for atribuicao in Atribuicao.objects.filter(
            edital=edital, etapa_id=etapa_id, ativo=True
        ).select_related("membro", "inscricao")
        if atribuicao.membro_id not in alocados
    ]
