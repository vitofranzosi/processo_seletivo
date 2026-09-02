"""O invólucro que todo comando da 011 usa, e a ordem que ele impõe.

```text
command_context()                            # transação
  ↓
select_for_update() no Processo              # bloqueia o contêiner
  ↓
pode_gerir_comissao(ator, processo)          # reavalia a base DEPOIS do bloqueio
  ↓
ensure_processo_accepts_changes(processo)    # Processo final não recebe alteração (FR-067)
  ↓
reserve(...)                                 # idempotência, DEPOIS de autorizar
```

**Por que reavaliar depois do bloqueio.** A base pode ser contextual, e a presidência é dado que
esta mesma feature altera: entre a verificação da view e a gravação, outro gestor pode ter
rebaixado o presidente — e ele concluiria a alteração com uma autorização que já não existe.

**Por que reservar depois de autorizar**, invertendo a ordem de `processos/application/commands.py`.
Lá `reserve()` vem primeiro e a repetição devolve o resultado memorizado sem reexecutar nada, o que
é seguro porque `require_permission` correu antes, fora da transação. Aqui não: reservar primeiro
faria a repetição responder a quem perdeu a presidência nesse meio-tempo.

**Por que bloquear o Processo, e não a linha.** O invariante de presidência lê membros e alocações
antes de decidir, e não há linha única a bloquear. A escala é de ata — dezenas de membros,
alterações esporádicas —, então o contêiner inteiro é a granularidade barata e correta.
"""

from contextlib import contextmanager

from processo_seletivo.comissoes.domain.autorizacao import pode_gerir_comissao
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import ProcessoSeletivo
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.idempotency import finish as finalizar_idempotencia
from processo_seletivo.shared.idempotency import reserve


def nao_encontrado():
    """A mesma resposta para tudo que o ator não alcança (FR-057, D-017)."""
    return DomainError("not_found", "Recurso não encontrado.", 404)


@contextmanager
def comando_de_comissao(*, actor, processo_id, operation, payload, idempotency_key):
    """Abre a transação, bloqueia, autoriza, confere estado e reserva. Cede `(contexto)`."""
    with command_context() as now:
        processo = (
            ProcessoSeletivo.objects.select_for_update()
            .filter(pk=processo_id, institution_scope=actor.institution_scope)
            .first()
            if actor is not None
            else None
        )
        if processo is None:
            raise nao_encontrado()
        base = pode_gerir_comissao(actor, processo)
        if base is None:
            raise nao_encontrado()
        ensure_processo_accepts_changes(processo)
        reserva = reserve(actor=actor, operation=operation, key=idempotency_key, payload=payload)
        yield Contexto(now=now, processo=processo, base=base, reserva=reserva)


class Contexto:
    def __init__(self, *, now, processo, base, reserva):
        self.now = now
        self.processo = processo
        self.base = base
        self.reserva = reserva

    @property
    def repetido(self):
        """Se esta chave já foi concluída: a repetição devolve o desfecho original.

        O critério é o **status**, e não o resultado: um lote em que tudo já existia conclui sem
        criar objeto nenhum, e checar `result_id` faria a repetição refazer consulta e laço
        inteiros para chegar ao mesmo nada.
        """
        return self.reserva.response_status is not None

    def concluir(self, resultado, status):
        finalizar_idempotencia(self.reserva, resultado, status)
        return resultado, status

    def concluir_sem_resultado(self, status, payload=None):
        """Fecha a reserva de um lote — o desfecho existe, o objeto único não.

        `payload` guarda o resultado declarado quando o ato tem um: a repetição devolve o que o
        ato respondeu, e não um vazio (012, FR-084, FR-097).
        """
        from processo_seletivo.shared.idempotency import finish_batch

        finish_batch(self.reserva, status, payload)

    @property
    def desfecho_anterior(self):
        """O resultado guardado por esta chave, quando havia um."""
        return self.reserva.result_payload
