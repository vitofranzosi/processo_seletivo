"""Leituras administrativas de Processos e Editais.

A API da 001 não expõe listagem — todos os endpoints administrativos são commands. A interface
precisa de uma, então ela nasce aqui, na camada de aplicação, e não como consulta solta na view:
o escopo institucional precisa ser aplicado no mesmo lugar em que os commands o aplicam, senão a
listagem vira a brecha por onde se enxerga o que não se pode alcançar.
"""

from dataclasses import dataclass
from datetime import datetime

from processo_seletivo.processos.models import AtoAdministrativo, Edital, ProcessoSeletivo


def listar_processos(*, actor):
    """Processos do escopo do ator, com seus Editais, do mais recente para o mais antigo."""
    return (
        ProcessoSeletivo.objects.filter(institution_scope=actor.institution_scope)
        .prefetch_related(
            # Sem o prefetch ordenado, cada Processo custaria uma consulta por lista de Editais.
            models_prefetch()
        )
        .order_by("-created_at")
    )


def models_prefetch():
    from django.db.models import Prefetch

    return Prefetch("editais", queryset=Edital.objects.order_by("year", "number"))


def contar_por_situacao(processos):
    """Quantos Editais em cada situação, para a visão geral da lista."""
    contagem = {}
    for processo in processos:
        for edital in processo.editais.all():
            contagem[edital.status] = contagem.get(edital.status, 0) + 1
    return contagem


def obter_edital(*, actor, edital_id):
    """Edital do escopo do ator, ou None. O escopo é aplicado aqui, como nos commands."""
    return (
        Edital.objects.filter(pk=edital_id, institution_scope=actor.institution_scope)
        .select_related("processo")
        .first()
    )


# ---------------------------------------------------------------------------
# O desfecho, para quem lê de fora (047, `FR-760` a `FR-762`)
# ---------------------------------------------------------------------------

EDITAL, PROCESSO = "EDITAL", "PROCESSO"
ENCERRADO, CANCELADO = "ENCERRADO", "CANCELADO"
# O estado final e a operação do ato que o produziu (`processos/application/finalizacao.py`).
OPERACAO_DO_DESFECHO = {ENCERRADO: "ENCERRAR", CANCELADO: "CANCELAR"}


@dataclass(frozen=True)
class Desfecho:
    """O fim de um Edital, ou do Processo dele, como a página pública o diz.

    `em` é o instante do ato imutável que registrou o desfecho, e `None` quando ele não é
    encontrado: a página diz o desfecho sem data, e não inventa uma (`FR-775`). Motivo e autor do
    ato **não** viajam aqui — a página não os diz (`FR-764`, `FR-776`), e minimização estrutural
    é não carregar o que não se mostra.
    """

    alcance: str
    operacao: str
    em: datetime | None


def desfechos(editais):
    """`{edital_id: Desfecho | None}` — o desfecho aplicável a cada Edital (047, `D-003`).

    **O estado diz se; o ato diz quando** (`research.md`, `R-2`). Os estados finais são terminais e
    mudam por CAS, e já vêm carregados com o Edital e o Processo: decidem sem consulta nenhuma na
    imensa maioria dos casos. A data vem do `AtoAdministrativo`, que é append-only nas duas camadas;
    `last_changed_at` seria a data da última transição, sobrescrita a cada uma.

    **Precedência**: o desfecho do Edital vence o do Processo, porque é o mais específico. Sem
    ele, o Processo encerrado ou cancelado vale para o Edital publicado: a partir dele nenhum
    Edital do Processo muda (`finalizacao.ensure_processo_accepts_changes`).

    **Uma consulta, e só quando há estado final**: a vitrine chama isto uma vez para todos os
    cartões, e o número de idas ao banco não cresce com eles.
    """
    aplicaveis = {}
    for edital in editais:
        if edital.status in (Edital.Status.ENCERRADO, Edital.Status.CANCELADO):
            aplicaveis[edital.id] = (EDITAL, str(edital.status), edital.id)
        elif edital.processo.status in (
            ProcessoSeletivo.Status.ENCERRADO,
            ProcessoSeletivo.Status.CANCELADO,
        ):
            aplicaveis[edital.id] = (PROCESSO, str(edital.processo.status), edital.processo_id)
    if not aplicaveis:
        return {edital.id: None for edital in editais}

    instantes = {}
    for agregado, operacao, ocorrido in (
        AtoAdministrativo.objects.filter(
            aggregate_id__in={agregado for _, _, agregado in aplicaveis.values()},
            operation__in=OPERACAO_DO_DESFECHO.values(),
        )
        .order_by("occurred_at")
        .values_list("aggregate_id", "operation", "occurred_at")
    ):
        # Em ordem cronológica, o último vence. Há um só por agregado — o estado final não admite
        # transição —, e a ordem existe para não depender disso.
        instantes[(agregado, operacao)] = ocorrido

    return {
        edital.id: (
            Desfecho(
                alcance=aplicaveis[edital.id][0],
                operacao=aplicaveis[edital.id][1],
                em=instantes.get(
                    (aplicaveis[edital.id][2], OPERACAO_DO_DESFECHO[aplicaveis[edital.id][1]])
                ),
            )
            if edital.id in aplicaveis
            else None
        )
        for edital in editais
    }
