"""Declarar, no Edital em elaboração, se e quando o Requerimento de Matrícula é pedido (029, `US3`).

**Comando próprio, e não `replace_draft`.** Aquele substitui o rascunho inteiro — *"o que não for
reenviado é apagado"* —, e estes são campos de **raiz** do Edital, que ele não carrega. Passar por
ele apagaria coleções inteiras a cada gravação da declaração; é um caminho que já produziu perda de
dado neste repositório, e a `T-003` o registrou antes de esta feature existir.

**O Edital liga e agenda; ele não desenha formulário.** Dois valores mais a ausência, e o texto da
declaração. Quais campos o requerimento tem é decisão de domínio, escrita em spec — a `D-002`
recusou o construtor de formulários, e a ausência de qualquer campo configurável aqui é o que
mantém essa recusa real.

**Momento vazio é a ausência de declaração**, e não um terceiro valor: `""` na coluna, `null` na
chave do conteúdo publicado. Duas grafias do mesmo fato seriam a contradição que a regra evita.

**Apagar o momento apaga o texto junto.** Texto de declaração sem momento é norma órfã: ninguém a
leria, ninguém a aceitaria, e ela apareceria na tela de Retificação como campo de um requerimento
que o Edital não pede. Deixá-la para trás seria guardar o que não tem consumidor.
"""

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import Edital
from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.concurrency import compare_and_swap

OPERACAO = "ALTERAR_REQUERIMENTO"


def atualizar_requerimento_de_matricula(
    *, actor, edital_id, expected_revision, momento, declaracao, correlation_id=""
):
    """Grava o momento e o texto. **Sem chave de idempotência**, como a identificação.

    A ausência é deliberada e pela mesma razão: isto edita rascunho, e não pratica ato
    irreversível. Repetir a mesma alteração escreve o mesmo valor, e quem a protege de gravação
    concorrente é o `compare_and_swap` de sempre.
    """
    require_permission(actor, "edital:elaborar")
    momento = (momento or "").strip()
    if momento and momento not in nomes.MOMENTOS:
        raise DomainError(
            "field_constraint_violated",
            "O momento do Requerimento de Matrícula é *na inscrição* ou *na convocação*.",
            422,
            campo="requerimento_momento",
        )
    declaracao = (declaracao or "").strip()
    if not momento:
        declaracao = ""
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
            # **Publicado não se edita; retifica-se.** O texto da declaração é retificável, e o
            # momento não — a classificação está no `CONTRATO`, com a razão escrita lá.
            raise DomainError(
                "invalid_state",
                "Somente o Requerimento de Matrícula de Edital em elaboração pode ser alterado.",
                409,
            )
        if edital.revision != expected_revision:
            raise DomainError("stale_revision", "A revisão informada está obsoleta.", 412)
        compare_and_swap(
            Edital.objects,
            pk=edital.pk,
            expected_revision=expected_revision,
            requerimento_momento=momento,
            requerimento_declaracao=declaracao,
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
            # **O momento entra na razão; o texto não.** Quem audita precisa saber que o Edital
            # passou a pedir o requerimento e quando — e o texto inteiro dentro do registro
            # duplicaria norma que o conteúdo publicado já guarda, por inteiro e com versão.
            reason=f"requerimento {momento or 'não exigido'}",
        )
        return edital
