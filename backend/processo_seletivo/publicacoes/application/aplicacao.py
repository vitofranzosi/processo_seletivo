"""Criar a Retificação que leva gestos de "aplicar a todos", com o registro de cada um (051, US5).

**Um ato só** (FR-941). O gesto não cria ato próprio: as Alterações dele entram na mesma
Retificação que a pessoa compôs à mão, e `create_retification` as confere com as guardas de sempre.
O que este comando acrescenta é o registro de cada gesto na trilha (FR-921, R-016), na mesma
transação: a Retificação sem o registro apagaria a autoria do lote, e o registro sem a Retificação
atribuiria ao gesto um ato que não existe.
"""

from django.db import transaction
from django.utils import timezone

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.publicacoes.application.retificacoes import create_retification

OPERACAO = "APLICAR_A_TODOS"


def criar_retificacao_com_gestos(*, gestos, **criacao):
    """`create_retification(**criacao)`, e uma linha `APLICAR_A_TODOS` por `(detalhe, razão)`.

    A repetição com a mesma chave de idempotência devolve o ato já criado; o registro não se repete,
    porque o gesto foi um só. Devolve o que `create_retification` devolve.
    """
    with transaction.atomic():
        retificacao, status = create_retification(**criacao)
        ja_registrado = RegistroAuditoria.objects.filter(
            aggregate_type=retificacao.__class__.__name__,
            aggregate_id=retificacao.pk,
            operation=OPERACAO,
        ).exists()
        if not ja_registrado:
            for detalhe, razao in gestos:
                record_event(
                    actor=criacao["actor"],
                    permission="retificacao:elaborar",
                    operation=OPERACAO,
                    aggregate=retificacao,
                    now=timezone.now(),
                    correlation_id=criacao["correlation_id"],
                    previous_state=retificacao.status,
                    reason=razao,
                    detalhe={**detalhe, "retificacao": str(retificacao.pk)},
                )
    return retificacao, status
