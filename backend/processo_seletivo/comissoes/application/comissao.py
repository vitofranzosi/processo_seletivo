"""Constituir e gerir a comissão do Processo.

Todo comando entra pelo invólucro de `application/__init__.py`, que impõe a ordem: bloquear,
autorizar, conferir o estado do Processo, reservar. O que fica aqui é só a regra de negócio.
"""

from uuid import UUID

from django.db import IntegrityError

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.domain import funcoes
from processo_seletivo.comissoes.domain.etapas import nome_da_etapa, nomes_das_etapas
from processo_seletivo.comissoes.models import AlocacaoEtapa, Funcao, MembroComissao
from processo_seletivo.shared.api.problems import DomainError


def identificador(valor):
    """Um UUID, ou a recusa de sempre.

    Sem isto, um `membro_id` vazio ou malformado chega a `filter(pk=...)` e levanta
    `ValidationError` — que não é `DomainError`, não é tratada por ninguém e vira 500 onde o
    contrato promete 404. Identificador que não tem forma de identificador não identifica nada.
    """
    try:
        return UUID(str(valor))
    except (TypeError, ValueError) as exc:
        raise nao_encontrado() from exc


def _membro_do_processo(processo, membro_id, *, exigir_ativo=True):
    """O membro deste Processo. `exigir_ativo=False` serve à repetição de uma remoção.

    A segunda chamada com a mesma chave de idempotência chega quando a linha já está inativa —
    e devolver 404 ali transformaria o duplo clique em erro, que é o oposto do que a
    idempotência existe para fazer.
    """
    consulta = MembroComissao.objects.filter(pk=identificador(membro_id), processo=processo)
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


def adicionar_varios(*, actor, processo_id, entradas, funcao, idempotency_key, correlation_id):
    """Inclui muitas pessoas de uma vez, com a mesma função.

    Incluir pessoa a pessoa eram dois envios por servidor — o formulário e a conferência —, e
    oitenta passos para montar uma banca de quarenta. Isso é pior que o custo de alocar, que já
    foi resolvido, e a razão é a mesma: a operação real é coletiva.

    `entradas` é uma lista de `(identificador, rótulo)`. Quem já integra a comissão não faz o
    conjunto falhar: numa inclusão em lote, recusar oitenta porque uma pessoa já estava seria
    punir o caminho normal.

    Devolve `(criados, ja_eram)`.
    """
    if funcao not in Funcao.values:
        raise DomainError("funcao_invalida", "Função inválida.", 422, campo="funcao")
    limpas = [
        ((subject or "").strip(), (rotulo or "").strip())
        for subject, rotulo in entradas
        if (subject or "").strip()
    ]
    if not limpas:
        raise DomainError(
            "identificador_ausente",
            "Informe ao menos um identificador institucional.",
            422,
            campo="identity_subject",
        )
    vistos = {}
    for subject, rotulo in limpas:
        # A mesma pessoa repetida na lista colada é engano de quem colou, e não conflito: a
        # primeira ocorrência vale, e o rótulo dela também.
        vistos.setdefault(subject, rotulo)
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="comissao:incluir-varios",
        payload={"subjects": sorted(vistos), "funcao": funcao},
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return [], []
        ja = set(
            MembroComissao.objects.filter(
                processo=ctx.processo, ativo=True, identity_subject__in=list(vistos)
            ).values_list("identity_subject", flat=True)
        )
        criados = []
        for subject, rotulo in vistos.items():
            if subject in ja:
                continue
            membro = MembroComissao.objects.create(
                processo=ctx.processo,
                identity_subject=subject,
                display_label=rotulo,
                funcao=funcao,
                criado_em=ctx.now,
                criado_por=actor.subject,
            )
            # Um evento por pessoa: a trilha responde por agregado, e um evento de lote não
            # diria quem entrou na comissão (FR-070).
            auditar(
                ctx=ctx,
                actor=actor,
                operation="COMISSAO_INCLUIR_MEMBRO",
                aggregate=membro,
                reason=f"{subject} incluído como {funcao}; em lote",
                correlation_id=correlation_id,
            )
            criados.append(membro)
        if criados:
            ctx.concluir(criados[0], 201)
        else:
            ctx.concluir_sem_resultado(200)
        return criados, sorted(ja)


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
            # As alocações dela **sobrevivem** ao rebaixamento — ao contrário da remoção, onde
            # são inativadas na mesma transação. Por isso elas contam aqui.
            _exigir_presidencia_apos(
                ctx.processo, membro, nova_funcao=funcao, alocacoes_sobrevivem=True
            )
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
        _exigir_presidencia_apos(
            ctx.processo, membro, nova_funcao=None, alocacoes_sobrevivem=False
        )
        # A cascata é atômica: alocação ativa sob membro inativo deixaria o acesso sobrevivendo
        # à remoção por uma janela, e atrapalharia a própria regra do último presidente, que
        # pergunta se há alocação ativa na comissão (EC-003).
        da_pessoa = list(
            AlocacaoEtapa.objects.filter(membro=membro, ativo=True).select_related("edital")
        )
        nomes = nomes_das_etapas(da_pessoa)
        for alocacao in da_pessoa:
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
                    f"{membro.identity_subject} — Etapa “{nome_da_etapa(alocacao, nomes)}” do "
                    f"Edital {alocacao.edital.number}/{alocacao.edital.year}; "
                    f"causa: saída da comissão"
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


def _exigir_presidencia_apos(processo, membro, *, nova_funcao, alocacoes_sobrevivem):
    """A comissão não fica sem presidente enquanto houver trabalho distribuído (FR-029, FR-030).

    Constituir sem presidente é estado transitório legítimo — é o que evita obrigar que o
    primeiro membro adicionado seja o presidente. O que não pode é sobrar alocação ativa sem
    ninguém respondendo por ela.

    **`alocacoes_sobrevivem` é a diferença entre os dois caminhos, e ignorá-la era um defeito.**
    Na remoção, as alocações do próprio membro são inativadas na mesma transação, então não
    contam para "sobrou trabalho distribuído". No rebaixamento elas ficam — e excluí-las deixava
    passar o caso da única presidente que também era a única alocada, exatamente o estado que
    esta função existe para impedir.
    """
    if membro.funcao != Funcao.PRESIDENTE or nova_funcao == Funcao.PRESIDENTE:
        return
    if funcoes.tem_presidente(processo, exceto=membro):
        return
    exceto = None if alocacoes_sobrevivem else membro
    if not funcoes.tem_alocacao_ativa(processo, exceto=exceto):
        return
    raise DomainError(
        "comissao_ficaria_sem_presidente",
        "Esta comissão possui alocações ativas e ficaria sem presidente. "
        "Atribua a presidência a outro membro antes.",
        409,
        campo="funcao",
    )
