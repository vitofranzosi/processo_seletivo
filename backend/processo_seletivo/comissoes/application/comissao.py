"""Constituir e gerir a comissão do Processo.

Todo comando entra pelo invólucro de `application/__init__.py`, que impõe a ordem: bloquear,
autorizar, conferir o estado do Processo, reservar. O que fica aqui é só a regra de negócio.
"""

from django.db import IntegrityError

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.domain import funcoes
from processo_seletivo.comissoes.models import AlocacaoEtapa, Funcao, MembroComissao
from processo_seletivo.shared.api.problems import DomainError


def _membro_do_processo(processo, membro_id, *, exigir_ativo=True):
    """O membro deste Processo. `exigir_ativo=False` serve à repetição de uma remoção.

    A segunda chamada com a mesma chave de idempotência chega quando a linha já está inativa —
    e devolver 404 ali transformaria o duplo clique em erro, que é o oposto do que a
    idempotência existe para fazer.
    """
    consulta = MembroComissao.objects.filter(pk=membro_id, processo=processo)
    membro = consulta.filter(ativo=True).first() if exigir_ativo else consulta.first()
    if membro is None:
        # Membro de outro Processo responde como inexistente: quem não gere aquele Processo não
        # pode descobrir sua composição alterando o identificador (FR-057).
        raise nao_encontrado()
    return membro


def auditar(*, ctx, actor, operation, aggregate, reason, correlation_id, idempotency_key=""):
    record_event(
        actor=actor,
        # A base **efetivamente usada**, e nunca a sistêmica por padrão: com duas bases, é essa a
        # informação que a trilha existe para guardar (FR-016).
        permission=ctx.base.permissao,
        operation=operation,
        aggregate=aggregate,
        now=ctx.now,
        correlation_id=correlation_id,
        reason=reason,
        # Agregados sem ciclo de vida: estado e revisão são explícitos, e é para isso que a
        # sentinela existe (D-014).
        new_state="",
        new_revision=None,
        idempotency_key=idempotency_key,
    )


def adicionar_membro(
    *,
    actor,
    processo_id,
    identity_subject,
    funcao,
    display_label="",
    idempotency_key,
    correlation_id,
):
    identity_subject = (identity_subject or "").strip()
    if not identity_subject:
        raise DomainError(
            "identificador_ausente",
            "Informe o identificador institucional da pessoa.",
            422,
            campo="identity_subject",
        )
    if funcao not in Funcao.values:
        raise DomainError("funcao_invalida", "Função inválida.", 422, campo="funcao")
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="comissao:incluir-membro",
        payload={"subject": identity_subject, "funcao": funcao},
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return MembroComissao.objects.get(pk=ctx.reserva.result_id), 201
        try:
            membro = MembroComissao.objects.create(
                processo=ctx.processo,
                identity_subject=identity_subject,
                display_label=(display_label or "").strip(),
                funcao=funcao,
                criado_em=ctx.now,
                criado_por=actor.subject,
            )
        except IntegrityError as exc:
            # Chave de idempotência nova tentando criar vínculo equivalente: é conflito, e não
            # repetição. As duas coisas são diferentes e o contrato as separa.
            raise DomainError(
                "membro_ja_integra_a_comissao",
                "Esta pessoa já integra a comissão deste Processo.",
                409,
                campo="identity_subject",
            ) from exc
        auditar(
            ctx=ctx,
            actor=actor,
            operation="COMISSAO_INCLUIR_MEMBRO",
            aggregate=membro,
            reason=f"{identity_subject} incluído como {funcao}",
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        return ctx.concluir(membro, 201)


def alterar_funcao(*, actor, processo_id, membro_id, funcao, idempotency_key, correlation_id):
    if funcao not in Funcao.values:
        raise DomainError("funcao_invalida", "Função inválida.", 422, campo="funcao")
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="comissao:alterar-funcao",
        payload={"membro": str(membro_id), "funcao": funcao},
        idempotency_key=idempotency_key,
    ) as ctx:
        membro = _membro_do_processo(ctx.processo, membro_id)
        if ctx.repetido:
            return membro, 200
        anterior = membro.funcao
        if anterior != funcao:
            _exigir_presidencia_apos(ctx.processo, membro, nova_funcao=funcao)
            membro.funcao = funcao
            membro.save(update_fields=["funcao"])
        auditar(
            ctx=ctx,
            actor=actor,
            operation="COMISSAO_ALTERAR_FUNCAO",
            aggregate=membro,
            reason=f"{membro.identity_subject}: {anterior} → {funcao}",
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        return ctx.concluir(membro, 200)


def remover_membro(*, actor, processo_id, membro_id, idempotency_key, correlation_id):
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="comissao:remover-membro",
        payload={"membro": str(membro_id)},
        idempotency_key=idempotency_key,
    ) as ctx:
        membro = _membro_do_processo(ctx.processo, membro_id, exigir_ativo=not ctx.repetido)
        if ctx.repetido:
            return membro, 200
        _exigir_presidencia_apos(ctx.processo, membro, nova_funcao=None)
        # A cascata é atômica: alocação ativa sob membro inativo deixaria o acesso sobrevivendo
        # à remoção por uma janela, e atrapalharia a própria regra do último presidente, que
        # pergunta se há alocação ativa na comissão (EC-003).
        for alocacao in AlocacaoEtapa.objects.filter(membro=membro, ativo=True):
            alocacao.ativo = False
            alocacao.inativado_em = ctx.now
            alocacao.inativado_por = actor.subject
            alocacao.save(update_fields=["ativo", "inativado_em", "inativado_por"])
            auditar(
                ctx=ctx,
                actor=actor,
                operation="ALOCACAO_REMOVER",
                aggregate=alocacao,
                reason=(
                    f"{membro.identity_subject} — Etapa {alocacao.etapa_id} do Edital "
                    f"{alocacao.edital_id}; causa: saída da comissão"
                ),
                correlation_id=correlation_id,
            )
        membro.ativo = False
        membro.inativado_em = ctx.now
        membro.inativado_por = actor.subject
        membro.save(update_fields=["ativo", "inativado_em", "inativado_por"])
        auditar(
            ctx=ctx,
            actor=actor,
            operation="COMISSAO_REMOVER_MEMBRO",
            aggregate=membro,
            reason=f"{membro.identity_subject} removido da comissão",
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        return ctx.concluir(membro, 200)


def _exigir_presidencia_apos(processo, membro, *, nova_funcao):
    """A comissão não fica sem presidente enquanto houver trabalho distribuído (FR-029, FR-030).

    Constituir sem presidente é estado transitório legítimo — é o que evita obrigar que o
    primeiro membro adicionado seja o presidente. O que não pode é sobrar alocação ativa sem
    ninguém respondendo por ela.
    """
    if membro.funcao != Funcao.PRESIDENTE or nova_funcao == Funcao.PRESIDENTE:
        return
    if funcoes.tem_presidente(processo, exceto=membro):
        return
    if not funcoes.tem_alocacao_ativa(processo, exceto=membro):
        return
    raise DomainError(
        "comissao_ficaria_sem_presidente",
        "Esta comissão possui alocações ativas e ficaria sem presidente. "
        "Atribua a presidência a outro membro antes.",
        409,
        campo="funcao",
    )
