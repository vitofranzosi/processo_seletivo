"""A porta comum dos dois atos de julgamento: bloquear, achar a peça, conferir o impedimento.

Admitir e julgar fazem a mesma coisa antes de decidir qualquer coisa — travam o Processo, carregam
a peça com o que a verificação precisa, e reavaliam as cinco perguntas **depois** do bloqueio
(FR-043). Escrever isso duas vezes faria as duas divergirem no primeiro ajuste; deixá-lo dentro de
um dos dois comandos faria o outro importar o privado do primeiro, que é a mesma dependência com
outro nome.
"""

from processo_seletivo.processos.models import ProcessoSeletivo
from processo_seletivo.recursos.domain.elegibilidade import BARRADO, RAZOES, impedimento
from processo_seletivo.recursos.models import Recurso
from processo_seletivo.shared.api.problems import DomainError


def travar(actor, recurso_id):
    """Bloqueia o Processo e devolve a peça — a serialização com emitir, publicar e consolidar.

    O bloqueio é no `ProcessoSeletivo`, e não no `Recurso`: é o mesmo ponto que a 015 e a 017 já
    travam, e travar em outro lugar criaria uma segunda ordem de bloqueio — que é como nascem os
    *deadlocks* entre comandos que hoje convivem.

    O `select_related` traz o que as cinco perguntas leem. Sem ele, cada pergunta faria a sua
    consulta, e o custo por ato de julgamento seria cinco leituras onde uma basta.
    """
    peca = (
        Recurso.objects.filter(pk=recurso_id)
        .select_related(
            "inscricao",
            "inscricao__edital",
            "versao",
            "resultado_atacado",
            "resultado_atacado__avaliacao",
            "publicacao_atacada",
            "publicacao_atacada__ato",
        )
        .prefetch_related("juizos", "decisoes")
        .first()
    )
    if peca is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)

    processo = (
        ProcessoSeletivo.objects.select_for_update()
        .filter(pk=peca.inscricao.edital.processo_id, institution_scope=actor.institution_scope)
        .first()
    )
    if processo is None:
        # Escopo alheio responde 404, e não 403: a existência do recurso de outra instituição não
        # é informação que se entregue a quem não é dela.
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return peca


def exigir_elegibilidade(actor, peca, *, etapa_id=None):
    """`etapa_id` é o par que a decisão alcança — ver `impedimento`."""
    razao = impedimento(actor, peca, etapa_id=etapa_id)
    if razao is not None:
        raise DomainError(BARRADO, RAZOES[razao], 403)
