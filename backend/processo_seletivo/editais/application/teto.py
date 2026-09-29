"""Declarar, no Edital em elaboração, quantas inscrições cada candidato pode enviar (015, FR-063).

**O RC-12 da auditoria de 26/09.** O teto era executado na submissão, saía no documento, aparecia
na Revisão e era retificável — e nenhuma tela da composição o declarava. O valor só nascia pelo ORM,
pelo `seed_demo` ou por Retificação depois de publicado: a `FR-063` diz que o Edital MUST poder
publicá-lo, e quem elabora não tinha onde.

**Comando próprio, e não `replace_draft`**, pela razão do Requerimento de Matrícula (029): o teto
é coluna de **raiz** do Edital, e aquele comando substitui o rascunho inteiro sem carregá-la. Por
isso gravar as outras etapas não o apaga — elas nunca passam por aqui.

**Vazio é sem limite, e não há valor por omissão.** É a ausência que a `FR-063` declara, e é o
comportamento de todo Edital anterior a este campo. O mínimo é 1: teto zero recusaria a primeira
inscrição de todo mundo, e um Edital que não recebe inscrição diz isso não designando o período.

**A regra mora no comando, e não só no formulário.** O `min` do HTML é conforto de quem digita; o
que impede o teto zero de chegar ao rascunho é esta recusa. A regra em si está em
`editais/domain/teto.py`, porque a conferência de publicação a invoca também — é ela que a faz
valer na Retificação.
"""

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.editais.domain.teto import teto_declarado
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.concurrency import compare_and_swap

OPERACAO = "ALTERAR_TETO_DE_INSCRICOES"


def atualizar_teto_de_inscricoes(*, actor, edital_id, expected_revision, teto, correlation_id=""):
    """Grava o teto. **Sem chave de idempotência**, como o Requerimento de Matrícula.

    Isto edita rascunho, e não pratica ato irreversível: repetir a mesma alteração escreve o mesmo
    valor, e quem a protege de gravação concorrente é o `compare_and_swap` de sempre.

    **O mesmo valor não grava nem audita.** A etapa Inscrição chama este comando a cada gravação,
    também quando só um Documento Exigido mudou; registrar "alteração do teto" em cada uma encheria
    a trilha de atos que não aconteceram, e quem pergunta *"quando o Edital passou a limitar?"*
    teria de procurar a resposta entre eles.
    """
    require_permission(actor, "edital:elaborar")
    # Antes da trava: valor recusado não chega a abrir transação.
    teto = teto_declarado(teto)
    with command_context() as now:
        try:
            edital = (
                Edital.objects.select_for_update()
                .select_related("processo")
                .get(pk=edital_id, institution_scope=actor.institution_scope)
            )
        except Edital.DoesNotExist as exc:
            raise DomainError("not_found", "Recurso não encontrado.", 404) from exc
        ensure_processo_accepts_changes(edital.processo)
        if edital.status != Edital.Status.EM_ELABORACAO:
            # **Publicado não se edita; retifica-se.** O teto é retificável (`CONTRATO`), e é pela
            # Retificação que ele muda depois da publicação — com ato publicado dizendo a mudança.
            raise DomainError(
                "invalid_state",
                "Somente o teto de inscrições de Edital em elaboração pode ser alterado.",
                409,
            )
        if edital.revision != expected_revision:
            raise DomainError("stale_revision", "A revisão informada está obsoleta.", 412)
        if edital.max_inscricoes_por_candidato == teto:
            return edital
        compare_and_swap(
            Edital.objects,
            pk=edital.pk,
            expected_revision=expected_revision,
            max_inscricoes_por_candidato=teto,
            last_edited_by=actor.subject,
        )
        edital.refresh_from_db()
        record_event(
            actor=actor,
            permission="edital:elaborar",
            operation=OPERACAO,
            aggregate=edital,
            now=now,
            correlation_id=correlation_id,
            previous_state=edital.status,
            previous_revision=expected_revision,
            reason=f"teto {teto}" if teto is not None else "sem teto",
        )
        return edital
