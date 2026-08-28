"""Leituras administrativas de Processos e Editais.

A API da 001 não expõe listagem — todos os endpoints administrativos são commands. A interface
precisa de uma, então ela nasce aqui, na camada de aplicação, e não como consulta solta na view:
o escopo institucional precisa ser aplicado no mesmo lugar em que os commands o aplicam, senão a
listagem vira a brecha por onde se enxerga o que não se pode alcançar.
"""

from processo_seletivo.processos.models import Edital, ProcessoSeletivo


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
