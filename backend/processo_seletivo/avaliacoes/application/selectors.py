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
# E o quarto filtro, que não é sobre cobertura e sim sobre **progresso**: quais inscrições ainda
# não têm todas as avaliações **concluídas**. É a pergunta da véspera do resultado, e ela não se
# respondia — cobertura fala de atribuição, e ter avaliador não é ter avaliação.
AVALIACAO_PENDENTE = "avaliacao_pendente"


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


def inscricoes_da_etapa(
    *, edital, etapa, pagina=1, cobertura=None, avaliador=None, panorama=None, prontidao=None
):
    """As inscrições submetidas do Edital, com quantas avaliações cada uma já tem.

    Paginada e filtrável (FR-049): mil inscrições não cabem numa tela, e a pergunta operacional
    quase nunca é "todas" — é "quais ainda não têm ninguém" ou "quais são de fulano".

    **`panorama` é o acréscimo da 013**, e ele chega por parâmetro em vez de ser consultado aqui
    por dois motivos. O primeiro é dependência: `resultados` lê este módulo, e lê-lo de volta seria
    ciclo. O segundo é custo: quem monta a tela resolve o panorama **uma vez** e o entrega ao
    resumo e à listagem, de modo que os dois contem a mesma coisa e nenhum deles consulte por
    linha (013, FR-006, FR-009).

    Com o panorama, a listagem passa a mostrar **participantes** por padrão — quem foi eliminado
    numa Etapa anterior ou ainda aguarda a anterior sai do conjunto (013, FR-005) — e o filtro de
    prontidão é o que traz cada grupo de volta, nomeado.
    """
    previstas = avaliacoes_previstas(etapa)
    consulta = (
        Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA)
        .annotate(
            atribuidas=Count(
                "atribuicoes",
                filter=Q(atribuicoes__etapa_id=etapa["id"], atribuicoes__ativo=True),
                distinct=True,
            ),
            concluidas=Count(
                "atribuicoes",
                filter=Q(
                    atribuicoes__etapa_id=etapa["id"],
                    atribuicoes__ativo=True,
                    atribuicoes__avaliacao__estado=Avaliacao.Estado.CONCLUIDA,
                ),
                distinct=True,
            ),
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
    if panorama is not None:
        consulta = consulta.filter(id__in=_recorte_da_prontidao(panorama, prontidao))
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
    elif cobertura == AVALIACAO_PENDENTE:
        consulta = consulta.filter(concluidas__lt=previstas)
    paginas = Paginator(consulta, POR_PAGINA)
    pagina_atual = paginas.get_page(pagina)
    linhas = [
        {
            "inscricao": inscricao,
            "atribuidas": inscricao.atribuidas,
            "concluidas": inscricao.concluidas,
            "faltam": max(previstas - inscricao.atribuidas, 0),
            "faltam_concluir": max(previstas - inscricao.concluidas, 0),
            "cobertura": _cobertura(inscricao.atribuidas, previstas),
            "atribuicoes": inscricao.atribuicoes_da_etapa,
            # `(estado, motivo)` da 013, ou `None` quando quem chamou não pediu prontidão. A
            # segunda posição é o que a tela mostra: "erro" não diz a ação seguinte, "1 de 2
            # avaliações concluída" diz (013, FR-012).
            "prontidao": (panorama or {}).get("estados", {}).get(inscricao.id),
        }
        for inscricao in pagina_atual
    ]
    return linhas, pagina_atual


def _recorte_da_prontidao(panorama, prontidao):
    """As identidades que a listagem deve mostrar, dado o filtro pedido.

    Sem filtro, os participantes — e não a população inteira. Com filtro, exatamente o grupo
    nomeado, inclusive os dois que **não** são participantes: quem foi eliminado antes e quem
    aguarda a Etapa anterior precisam ser alcançáveis, senão a presidência sabe que existem pelo
    resumo e não consegue vê-los.
    """
    if not prontidao:
        return panorama["participantes"]
    return {
        identidade for identidade, (estado, _) in panorama["estados"].items() if estado == prontidao
    }


def resumo_da_etapa(*, edital, etapa, panorama=None):
    """O que falta, em três números — antes do detalhe (FR-014).

    Uma consulta agregada sobre as inscrições submetidas, e não um laço sobre elas: com mil
    inscrições, contar em Python custaria mil objetos para produzir três inteiros.

    **A 013 acrescenta dimensões a este mesmo resumo**, e não um painel ao lado dele: cobertura,
    conclusão e prontidão são perguntas sobre a mesma população, e contá-las em lugares diferentes
    daria dois números para a mesma Etapa (013, D-004, FR-009).
    """
    previstas = avaliacoes_previstas(etapa)
    por_inscricao = (
        Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA)
        .annotate(
            atribuidas=Count(
                "atribuicoes",
                filter=Q(atribuicoes__etapa_id=etapa["id"], atribuicoes__ativo=True),
                distinct=True,
            ),
            concluidas=Count(
                "atribuicoes",
                filter=Q(
                    atribuicoes__etapa_id=etapa["id"],
                    atribuicoes__ativo=True,
                    atribuicoes__avaliacao__estado=Avaliacao.Estado.CONCLUIDA,
                ),
                distinct=True,
            ),
        )
        .aggregate(
            total=Count("id"),
            sem_nenhum=Count("id", filter=Q(atribuidas=0)),
            completas=Count("id", filter=Q(atribuidas__gte=previstas)),
            avaliadas=Count("id", filter=Q(concluidas__gte=previstas)),
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
        # Cobertura e progresso são perguntas diferentes: ter avaliador não é ter avaliação, e é
        # esta que a presidência faz na véspera do resultado.
        "sem_conclusao": total - por_inscricao["avaliadas"],
        "atribuicoes": Atribuicao.objects.filter(
            edital=edital, etapa_id=etapa["id"], ativo=True
        ).count(),
        # As contagens da 013 vêm do panorama, e não de uma segunda agregação: é o mesmo
        # dicionário que a listagem filtra, e é isso que torna a partição verificável (FR-010).
        **((panorama or {}).get("contagens") or {}),
    }


# Os três filtros da Mesa. São derivados do estado da Avaliação, e não colunas: "pendente" é a
# ausência de conclusão, e persistí-la criaria estado a manter a cada gravação (FR-021).
#
# **Rascunho é o terceiro**, e ele não é conforto. Sem distingui-lo, uma avaliação começada aparece
# igual às que ninguém abriu: numa Mesa de 230 itens, retomar o trabalho vira memória, e uma
# avaliação em andamento pode ficar esquecida sem que nada indique.
PENDENTES = "pendentes"
CONCLUIDAS = "concluidas"
RASCUNHOS = "rascunhos"
# O que sobra do pendente depois de separar o rascunho. Os três somam o total, e é isso que faz as
# contagens fecharem: "3 pendentes, 1 em rascunho" sobre um total de 3 pedia que quem lesse somasse
# quatro.
NAO_INICIADAS = "nao-iniciadas"


def mesa(*, ator, edital, etapa_id, pagina=1, filtro=None, vigentes=None):
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
    # `vigentes` chega da view, que já leu o conteúdo publicado para resolver a Etapa. Relê-lo aqui
    # custaria uma consulta a mais por abertura da Mesa — fixa, mas gratuita de evitar, e o
    # orçamento de consulta desta tela é testado desde a 012 (013, FR-006).
    minhas = _so_participantes(
        Atribuicao.objects.filter(
            membro=membro, edital=edital, etapa_id=identidade_da_etapa, ativo=True
        ),
        edital,
        identidade_da_etapa,
        vigentes=vigentes,
    ).select_related("inscricao", "avaliacao")
    contagens = minhas.aggregate(
        total=Count("id"),
        concluidas=Count("id", filter=Q(avaliacao__estado=Avaliacao.Estado.CONCLUIDA)),
        rascunhos=Count("id", filter=Q(avaliacao__estado=Avaliacao.Estado.RASCUNHO)),
    )
    contagens["pendentes"] = contagens["total"] - contagens["concluidas"]
    contagens["nao_iniciadas"] = contagens["pendentes"] - contagens["rascunhos"]
    if filtro == CONCLUIDAS:
        minhas = minhas.filter(avaliacao__estado=Avaliacao.Estado.CONCLUIDA)
    elif filtro == RASCUNHOS:
        minhas = minhas.filter(avaliacao__estado=Avaliacao.Estado.RASCUNHO)
    elif filtro == NAO_INICIADAS:
        minhas = minhas.filter(avaliacao__isnull=True)
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
            "rascunho": getattr(atribuicao, "avaliacao", None) is not None
            and atribuicao.avaliacao.estado == Avaliacao.Estado.RASCUNHO,
        }
        for atribuicao in pagina_atual
    ]
    return linhas, pagina_atual, contagens


def carga_nas_etapas(*, ator, atribuicoes):
    """Quantas pendentes e quantas concluídas em cada Etapa alocada — por agregação (FR-048).

    A tela inicial de quem avalia listava as Etapas e um botão “Abrir”, sem número nenhum: com 230
    pendentes, saber quanto falta exigia entrar. É a primeira pergunta de quem trabalha.
    """
    from django.db.models import Count, Q

    from processo_seletivo.comissoes.models import MembroComissao

    chaves = {(item["edital"].id, str(item["etapa_id"])) for item in atribuicoes}
    if not chaves:
        return {}
    membros = MembroComissao.objects.filter(
        identity_subject=ator.subject,
        processo__institution_scope=ator.institution_scope,
        ativo=True,
    )
    # **A progressão vale aqui também**, e sem ela a Mesa ficaria corretamente vazia enquanto esta
    # tela anunciaria o mesmo trabalho como pendente — duas telas dizendo coisas diferentes sobre a
    # mesma Etapa. Uma restrição por Etapa em que a pessoa atua, e não por linha: são poucas Etapas
    # por pessoa, e a alternativa seria contar errado (013, FR-005).
    # O conteúdo publicado é lido **uma vez por Edital**, e não uma por Etapa: uma pessoa alocada
    # em quatro Etapas do mesmo Edital pagaria quatro leituras idênticas do mesmo conteúdo.
    from processo_seletivo.comissoes.domain.etapas import etapas_vigentes

    conteudos = {}
    por_etapa = Q(pk__in=[])
    for item in atribuicoes:
        edital = item["edital"]
        if edital.id not in conteudos:
            try:
                conteudos[edital.id] = etapas_vigentes(edital)
            except Exception:  # noqa: BLE001 — Edital sem versão vigente não restringe nada
                conteudos[edital.id] = {}
        por_etapa |= Q(edital=edital, etapa_id=item["etapa_id"]) & Q(
            pk__in=_so_participantes(
                Atribuicao.objects.filter(edital=edital, etapa_id=item["etapa_id"]),
                edital,
                item["etapa_id"],
                vigentes=conteudos[edital.id],
            ).values("pk")
        )
    contagens = (
        Atribuicao.objects.filter(
            membro__in=membros,
            ativo=True,
            edital_id__in={edital_id for edital_id, _ in chaves},
        )
        .filter(por_etapa)
        .values("edital_id", "etapa_id")
        .annotate(
            total=Count("id"),
            concluidas=Count("id", filter=Q(avaliacao__estado=Avaliacao.Estado.CONCLUIDA)),
        )
    )
    return {
        (linha["edital_id"], str(linha["etapa_id"])): _completude(
            linha["total"], linha["concluidas"]
        )
        for linha in contagens
    }


def _so_participantes(consulta, edital, etapa_id, prefixo="inscricao", vigentes=None):
    """As duas regras de progressão da `013`, **dobradas na consulta** que já ia acontecer.

    Materializar o conjunto e passá-lo em `__in` custaria duas leituras de população inteira por
    listagem, e os orçamentos de consulta da 011 e da 012 existem justamente para que uma feature
    seguinte não os corroa em silêncio — foram eles que denunciaram a primeira versão disto.

    Import local pelo motivo de sempre: `resultados` lê este módulo, e lê-lo de volta no topo seria
    ciclo (013, T-001).
    """
    from processo_seletivo.resultados.application.prontidao import restringir_a_participantes

    return restringir_a_participantes(
        consulta, edital=edital, etapa_id=etapa_id, prefixo=prefixo, vigentes=vigentes
    )


def _completude(total, concluidas):
    """As contagens e a fração entre elas, que é o que se compara de relance entre Etapas.

    O percentual arredonda, e arredondar mente nas duas pontas: uma de 255 concluída vira "0%" e
    dá a Etapa por não começada; 254 de 255 vira "100%" e a dá por encerrada. As duas guardas
    reservam os extremos para os extremos — só quem tem zero mostra 0%, só quem não deve nada
    mostra 100%.
    """
    if not total:
        return {"total": 0, "concluidas": 0, "pendentes": 0, "percentual": 0}
    percentual = round(concluidas * 100 / total)
    if percentual == 0 and concluidas:
        percentual = 1
    elif percentual == 100 and concluidas < total:
        percentual = 99
    return {
        "total": total,
        "concluidas": concluidas,
        "pendentes": total - concluidas,
        "percentual": percentual,
    }


def proxima_pendente(*, ator, edital, etapa_id, depois_de):
    """A próxima inscrição sem conclusão desta pessoa, na ordem em que a Mesa lista.

    Sem isto, quem tem 230 para avaliar volta pela trilha de navegação a cada uma — e o caminho de
    trabalho fica mais longo que o trabalho.
    """
    from processo_seletivo.comissoes.domain.autorizacao import membro_ativo

    membro = membro_ativo(ator, edital.processo)
    if membro is None:
        return None
    atual = (
        Atribuicao.objects.filter(
            membro=membro, edital=edital, etapa_id=etapa_id, inscricao_id=depois_de, ativo=True
        )
        .select_related("inscricao")
        .first()
    )
    pendentes = (
        # **A porta que mais importa fechar.** As demais superfícies entregam a inscrição porque
        # alguém pediu por ela; esta a entrega sem que ninguém peça — e oferecer uma inscrição
        # eliminada como "próximo trabalho" é o pior modo de a exclusão falhar.
        _so_participantes(
            Atribuicao.objects.filter(membro=membro, edital=edital, etapa_id=etapa_id, ativo=True),
            edital,
            etapa_id,
        )
        .exclude(avaliacao__estado=Avaliacao.Estado.CONCLUIDA)
        .exclude(inscricao_id=depois_de)
        .select_related("inscricao")
        .order_by("inscricao__protocolo", "inscricao_id")
    )
    if atual is not None:
        # A seguinte na ordem da Mesa; se esta era a última, volta-se à primeira pendente, porque
        # o trabalho é circular e não linear.
        adiante = pendentes.filter(inscricao__protocolo__gt=atual.inscricao.protocolo or "").first()
        if adiante is not None:
            return adiante.inscricao
    return pendentes.first().inscricao if pendentes.exists() else None


def retiradas_do_avaliador(*, ator, edital, etapa_id):
    """O que saiu da Mesa desta pessoa, e por qual ato — para ela, e não só para a auditoria.

    A revogação é imediata e silenciosa: a Atribuição some da Mesa e a contagem muda, sem nada
    dizer o que houve. A trilha registra o ato com autor e motivo e responde 404 para quem avalia,
    corretamente — de modo que a pessoa cujo trabalho foi retirado era a única sem canal para saber
    disso. Isto é o mesmo registro, mostrado a quem ele afeta.

    O que é lido aqui é o `AtoAdministrativo`, e não a trilha de auditoria: o ato é o que tem
    motivo obrigatório, e é o motivo que responde à pergunta “por quê”.
    """
    from processo_seletivo.comissoes.domain.autorizacao import membro_ativo
    from processo_seletivo.processos.models import AtoAdministrativo

    membro = membro_ativo(ator, edital.processo)
    if membro is None:
        return []
    inativas = list(
        Atribuicao.objects.filter(
            membro=membro, edital=edital, etapa_id=etapa_id, ativo=False
        ).select_related("inscricao")
    )
    if not inativas:
        return []
    atos = {}
    for ato in AtoAdministrativo.objects.filter(
        aggregate_type="Atribuicao", aggregate_id__in=[a.id for a in inativas]
    ).order_by("occurred_at"):
        atos[ato.aggregate_id] = ato
    return [
        {
            "inscricao": atribuicao.inscricao,
            "quando": atribuicao.inativado_em,
            "por": atribuicao.inativado_por,
            "ato": atos.get(atribuicao.id),
        }
        for atribuicao in sorted(
            inativas, key=lambda a: a.inativado_em or a.criado_em, reverse=True
        )
    ]


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
                "avaliacao": avaliacao,
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
