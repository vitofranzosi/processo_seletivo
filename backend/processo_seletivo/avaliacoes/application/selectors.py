"""A organização do trabalho — por agregação, e nunca por laço.

A escala desta feature é de mil inscrições e quarenta avaliadores, e ela decide o desenho: as
contagens saem de `GROUP BY`, a lista de inscrições é paginada, e nenhuma consulta chama o guard da
autorização por linha (P-004, FR-048, FR-049).

A pergunta que esta tela existe para responder, antes do detalhe: **o que falta**. Quantas
inscrições ainda não têm avaliador suficiente, quantas cada pessoa recebeu, e quantas faltam para
cumprir o que a Etapa declarou (FR-014).
"""

from django.core.paginator import Paginator
from django.db.models import Count, Q

from processo_seletivo.avaliacoes.domain.previsao import avaliacoes_previstas
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao
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
