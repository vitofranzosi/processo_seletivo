"""A emissão da trilha da 012 — e o que ela nunca carrega.

`comando_de_comissao` abre a transação, bloqueia o Processo, reavalia a autorização e reserva a
idempotência. **Ele não audita**: quem grava a trilha é uma chamada explícita, como a 011 faz em
`comissoes/application/comissao.py`. Os sete atos de FR-052 passam por aqui.

Dois registros, e eles respondem coisas diferentes — a mesma divisão que
`processos/application/commands.py` já usa:

| | responde |
|---|---|
| `AtoAdministrativo` | **o ato**: agregado, operação, ator, **motivo obrigatório**, instante |
| `RegistroAuditoria` | **a trilha**: mais a base de autorização, o escopo e a correlação |

Impedir, reabrir e inativar Atribuição sob Avaliação concluída gravam os dois: é de
`AtoAdministrativo` que a organização do trabalho lê o motivo para mostrar ao lado da avaliação
tornada inelegível (FR-092, FR-093).

**O que a trilha não guarda: pontuação e parecer** (FR-054). Ela registra que o ato aconteceu; o
conteúdo do ato vive na Avaliação, que é o registro do domínio. Por isso esta função não tem
parâmetro por onde eles caibam — a omissão é de assinatura, e não de disciplina.
"""

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.processos.models import AtoAdministrativo


def auditar(
    *,
    actor,
    permissao,
    operation,
    aggregate,
    now,
    correlation_id,
    reason="",
    idempotency_key="",
    com_ato_administrativo=False,
):
    """Grava a trilha do ato, e o ato em si quando ele exige motivo.

    `new_state` e `new_revision` vão explícitos porque os agregados desta feature não têm ciclo de
    vida que o registrador possa ler — a sentinela existe para isso desde a 011 (D-014, FR-070).
    Nenhum estado é inventado para satisfazer a forma do registrador.
    """
    if com_ato_administrativo:
        if not reason:
            raise ValueError("Ato que exige motivo não pode ser auditado sem ele.")
        AtoAdministrativo.objects.create(
            aggregate_type=aggregate.__class__.__name__,
            aggregate_id=aggregate.pk,
            operation=operation,
            actor_subject=actor.subject,
            reason=reason,
            occurred_at=now,
        )
    record_event(
        actor=actor,
        permission=permissao,
        operation=operation,
        aggregate=aggregate,
        now=now,
        correlation_id=correlation_id,
        reason=reason,
        new_state="",
        new_revision=None,
        idempotency_key=idempotency_key,
    )
