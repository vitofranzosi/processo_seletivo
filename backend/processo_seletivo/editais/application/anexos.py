"""Os comandos que mantêm a coleção de Anexos do Edital em elaboração (020, FR-015).

**Por que não é `replace_draft`.** As outras cinco coleções viajam inteiras a cada gravação de
etapa: o formulário devolve o que desenhou, e o command apaga e recria. Bytes não fazem essa
viagem — o formulário teria de reenviar megabytes a cada `Salvar`, ou o `replace_draft` apagaria os
anexos ao gravar qualquer outra etapa. Por isso a coleção tem comandos próprios e estreitos, e o
precedente é da `009`: `anexar_documento` grava na hora, sem `Salvar`, com validação e auditoria
próprias (R-006).

**O que continua igual.** Autorização verificada aqui, e não na view; estado do Edital conferido
depois do bloqueio; `compare_and_swap` na revisão, para que o assistente continue tendo controle
otimista honesto; e trilha de auditoria por operação. Ficar fora do `replace_draft` não é ficar
fora das garantias.
"""

import hashlib

from django.conf import settings

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.editais.models.anexos import AnexoEdital, ArtefatoAnexo
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.arquivos import aceitar
from processo_seletivo.shared.concurrency import compare_and_swap

PERMISSAO = "edital:elaborar"
BLOCO = 64 * 1024


def _edital_em_elaboracao(actor, edital_id, expected_revision):
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
        raise DomainError("invalid_state", "Somente Edital em elaboração pode ser editado.", 409)
    if edital.revision != expected_revision:
        raise DomainError("stale_revision", "A revisão informada está obsoleta.", 412)
    return edital


def _anexo_do_edital(edital, anexo_id):
    try:
        return edital.anexos.select_related("artefato").get(pk=anexo_id)
    except (AnexoEdital.DoesNotExist, ValueError, TypeError) as exc:
        raise DomainError("not_found", "Recurso não encontrado.", 404) from exc


def _guardar_artefato(arquivo, *, actor, now):
    """Lê, confere e grava os bytes. O resumo é do que foi guardado, e não do que foi prometido."""
    aceitar(
        arquivo,
        nome_original=arquivo.name,
        limite_em_bytes=settings.EDITAL_ANEXOS_LIMITE_BYTES,
    )
    arquivo.seek(0)
    conteudo = arquivo.read()
    return ArtefatoAnexo.objects.create(
        bytes=conteudo,
        content_type="application/pdf",
        tamanho=len(conteudo),
        document_hash=hashlib.sha256(conteudo).hexdigest(),
        nome_original=arquivo.name[:255],
        enviado_por=actor.subject,
        enviado_em=now,
    )


def _descartar(artefato):
    """Apaga o artefato que nenhuma versão publicou. O congelado a trigger recusa, e é o certo."""
    if artefato is not None and artefato.congelado_em is None:
        artefato.delete()


def _proxima_ordem(edital):
    ultima = edital.anexos.order_by("-order").values_list("order", flat=True).first()
    return (ultima or 0) + 1


def _concluir(edital, *, actor, now, expected_revision, operation, reason, correlation_id):
    compare_and_swap(
        Edital.objects,
        pk=edital.pk,
        expected_revision=expected_revision,
        last_edited_by=actor.subject,
    )
    edital.refresh_from_db()
    record_event(
        actor=actor,
        permission=PERMISSAO,
        operation=operation,
        aggregate=edital,
        now=now,
        correlation_id=correlation_id,
        previous_state=edital.status,
        previous_revision=expected_revision,
        # O que aconteceu com qual Anexo, e **não** o nome do arquivo: o nome é escolha de quem
        # sobe, muda entre duas versões do mesmo formulário, e não responde nada que a trilha
        # precise responder.
        reason=reason,
    )
    return edital


def anexar(*, actor, edital_id, expected_revision, arquivo, rotulo="", correlation_id=""):
    """Cria o Anexo a partir do arquivo. **Não existe Anexo sem artefato** (FR-015a)."""
    require_permission(actor, PERMISSAO)
    with command_context() as now:
        edital = _edital_em_elaboracao(actor, edital_id, expected_revision)
        artefato = _guardar_artefato(arquivo, actor=actor, now=now)
        anexo = AnexoEdital.objects.create(
            edital=edital,
            rotulo=rotulo.strip()[:255],
            order=_proxima_ordem(edital),
            artefato=artefato,
        )
        _concluir(
            edital,
            actor=actor,
            now=now,
            expected_revision=expected_revision,
            operation="ANEXAR_AO_EDITAL",
            reason=f"anexo {anexo.id}",
            correlation_id=correlation_id,
        )
        return anexo


def substituir(*, actor, edital_id, expected_revision, anexo_id, arquivo, correlation_id=""):
    """Troca os bytes preservando a identidade — e **apaga o artefato anterior** (FR-010a).

    Não há histórico de elaboração de artefato: artefato que nenhuma publicação referencia não é
    histórico de nada, e guardá-lo encheria o acervo de bytes que ninguém alcança. O artefato já
    congelado é outra história — a trigger o defende, e `_descartar` nem tenta.
    """
    require_permission(actor, PERMISSAO)
    with command_context() as now:
        edital = _edital_em_elaboracao(actor, edital_id, expected_revision)
        anexo = _anexo_do_edital(edital, anexo_id)
        anterior = anexo.artefato
        anexo.artefato = _guardar_artefato(arquivo, actor=actor, now=now)
        anexo.save(update_fields=["artefato"])
        _descartar(anterior)
        _concluir(
            edital,
            actor=actor,
            now=now,
            expected_revision=expected_revision,
            operation="SUBSTITUIR_ANEXO",
            reason=f"anexo {anexo.id}",
            correlation_id=correlation_id,
        )
        return anexo


def rotular(*, actor, edital_id, expected_revision, anexo_id, rotulo, correlation_id=""):
    """O rótulo é texto único, escrito inteiro pelo autor. O sistema não o interpreta (FR-005)."""
    require_permission(actor, PERMISSAO)
    with command_context() as now:
        edital = _edital_em_elaboracao(actor, edital_id, expected_revision)
        anexo = _anexo_do_edital(edital, anexo_id)
        anexo.rotulo = rotulo.strip()[:255]
        anexo.save(update_fields=["rotulo"])
        _concluir(
            edital,
            actor=actor,
            now=now,
            expected_revision=expected_revision,
            operation="ROTULAR_ANEXO",
            reason=f"anexo {anexo.id}",
            correlation_id=correlation_id,
        )
        return anexo


def reordenar(*, actor, edital_id, expected_revision, ordem, correlation_id=""):
    """A nova ordem editorial, pela identidade de cada Anexo.

    **Reordenar não toca em rótulo nenhum** (FR-007). A ordem é campo próprio justamente para isso:
    o PDF pode trazer "ANEXO VI" impresso, e derivar o rótulo da posição faria o conteúdo publicado
    divergir dos bytes em silêncio.

    A gravação passa por um **deslocamento acima do maior valor em uso** porque `(edital, order)` é
    único: escrever a ordem final direto colidiria com a linha que ainda ocupa aquele número. Não
    dá para deslocar para baixo — `order` é positivo, e o banco tem a checagem —, então a primeira
    passagem sobe todo mundo para fora do intervalo final, e a segunda desce cada um para o seu.
    """
    require_permission(actor, PERMISSAO)
    with command_context() as now:
        edital = _edital_em_elaboracao(actor, edital_id, expected_revision)
        anexos = {str(anexo.id): anexo for anexo in edital.anexos.all()}
        pedidos = [str(identificador) for identificador in ordem]
        if sorted(pedidos) != sorted(anexos):
            raise DomainError(
                "invalid_order",
                "A ordem precisa citar cada Anexo do Edital exatamente uma vez.",
                422,
            )
        deslocamento = max((anexo.order for anexo in anexos.values()), default=0) + 1
        for posicao, identificador in enumerate(pedidos):
            AnexoEdital.objects.filter(pk=identificador).update(order=deslocamento + posicao)
        for posicao, identificador in enumerate(pedidos):
            AnexoEdital.objects.filter(pk=identificador).update(order=posicao + 1)
        _concluir(
            edital,
            actor=actor,
            now=now,
            expected_revision=expected_revision,
            operation="REORDENAR_ANEXOS",
            reason=f"{len(pedidos)} anexos",
            correlation_id=correlation_id,
        )
        return edital


def remover(*, actor, edital_id, expected_revision, anexo_id, correlation_id=""):
    """Tira o Anexo do Edital em elaboração, e **deixa lacuna** na sequência (FR-008).

    Renumerar os remanescentes é o que o sistema não faz: o rótulo é campo do autor, e mexer nele
    aqui faria a numeração publicada divergir do que está impresso dentro do PDF.

    O requisito que apontava o Anexo **sobrevive**, sem modelo: é `SET_NULL` no banco, e é a forma
    da resposta que `EtapaAvaliacao.evento` já deu (FR-022).
    """
    require_permission(actor, PERMISSAO)
    with command_context() as now:
        edital = _edital_em_elaboracao(actor, edital_id, expected_revision)
        anexo = _anexo_do_edital(edital, anexo_id)
        artefato = anexo.artefato
        identificador = anexo.id
        anexo.delete()
        _descartar(artefato)
        _concluir(
            edital,
            actor=actor,
            now=now,
            expected_revision=expected_revision,
            operation="REMOVER_ANEXO",
            reason=f"anexo {identificador}",
            correlation_id=correlation_id,
        )
        return edital
