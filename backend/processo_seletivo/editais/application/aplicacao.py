"""Gravar um gesto de "aplicar a todos" — a etapa e o registro do gesto, numa transação (051).

**Um caminho de gravação só** (`D-001` da spec). O gesto não grava por conta própria: ele entrega à
gravação da etapa o conteúdo com os valores materializados, e `replace_draft` valida e grava como
em qualquer outro envio. O que este comando acrescenta é o registro, e a garantia de que os dois
acontecem juntos ou nenhum (FR-920): um registro sem a gravação faria a Revisão atribuir ao gesto o
que ele não gravou, e a gravação sem o registro apagaria a autoria (FR-921).
"""

from django.db import transaction
from django.utils import timezone

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.editais.application.draft import replace_draft

OPERACAO = "APLICAR_A_TODOS"


def gravar_aplicacao(*, registro, razao, **gravacao):
    """Grava a etapa com `replace_draft(**gravacao)` e o registro do gesto na trilha.

    `registro` é o `detalhe` do contrato (`contracts/registro-do-gesto.md`); `razao` é a frase que a
    trilha exibe. Devolve o Edital gravado. Uma recusa de `replace_draft` desfaz tudo.
    """
    with transaction.atomic():
        edital = replace_draft(**gravacao)
        record_event(
            actor=gravacao["actor"],
            permission="edital:elaborar",
            operation=OPERACAO,
            aggregate=edital,
            now=timezone.now(),
            correlation_id=gravacao["correlation_id"],
            previous_state=edital.status,
            # A revisão que o gesto encontrou, e não a que ele deixou: é o que encadeia este
            # registro com o `ALTERAR_RASCUNHO` da mesma gravação.
            previous_revision=gravacao["expected_revision"],
            reason=razao,
            detalhe=registro,
        )
    return edital
