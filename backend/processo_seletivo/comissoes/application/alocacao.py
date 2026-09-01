"""Alocar membros às Etapas, e desfazer a alocação.

A Etapa é sempre lida do conteúdo vigente, nunca de `edital.etapas` — ver `domain/etapas.py`.
"""

from django.db import IntegrityError

from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.application.comissao import auditar, identificador
from processo_seletivo.comissoes.domain import funcoes
from processo_seletivo.comissoes.domain.etapas import (
    etapas_vigentes,
    nome_da_etapa,
    nomes_das_etapas,
)
from processo_seletivo.comissoes.models import AlocacaoEtapa, MembroComissao
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.api.problems import DomainError


def alocar(*, actor, processo_id, membro_id, edital_id, etapa_id, idempotency_key, correlation_id):
    etapa_id = identificador(etapa_id)
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="comissao:alocar",
        payload={"membro": str(membro_id), "edital": str(edital_id), "etapa": str(etapa_id)},
        idempotency_key=idempotency_key,
    ) as ctx:
        membro = MembroComissao.objects.filter(
            pk=identificador(membro_id), processo=ctx.processo, ativo=True
        ).first()
        if membro is None:
            # Pessoa que não é membro ativo não recebe alocação: a jornada é
            # pessoa → comissão → Etapa, e nunca pessoa → Etapa (FR-034, EC-005).
            raise DomainError(
                "pessoa_nao_e_membro_ativo",
                "Só membros ativos da comissão podem ser alocados.",
                422,
                campo="membro_id",
            )
        # A coerência percorre `etapa → edital → processo`: alocar em Etapa de Edital de outro
        # Processo é inconsistência determinável, e responde como inexistente (FR-004, EC-004).
        edital = Edital.objects.filter(
            pk=identificador(edital_id),
            processo=ctx.processo,
            institution_scope=ctx.processo.institution_scope,
        ).first()
        if edital is None:
            raise nao_encontrado()
        if ctx.repetido:
            return AlocacaoEtapa.objects.get(pk=ctx.reserva.result_id), 201
        # Levanta `edital_sem_versao_vigente` quando o Edital nunca foi publicado (FR-032).
        vigentes = etapas_vigentes(edital)
        if etapa_id not in vigentes:
            raise nao_encontrado()
        nome_da_etapa = vigentes[etapa_id].get("name") or str(etapa_id)
        if not funcoes.tem_presidente(ctx.processo):
            raise DomainError(
                "comissao_sem_presidente",
                "Esta comissão ainda não tem presidente. "
                "Designe a presidência antes de distribuir trabalho.",
                409,
            )
        try:
            alocacao = AlocacaoEtapa.objects.create(
                membro=membro,
                edital=edital,
                etapa_id=etapa_id,
                criado_em=ctx.now,
                criado_por=actor.subject,
            )
        except IntegrityError as exc:
            raise DomainError(
                "alocacao_ja_existe",
                "Esta pessoa já está alocada nesta Etapa.",
                409,
                campo="etapa_id",
            ) from exc
        auditar(
            ctx=ctx,
            actor=actor,
            operation="ALOCACAO_INCLUIR",
            aggregate=alocacao,
            # O nome **de então**: quem audita precisa saber que Etapa era, e o identificador
            # sozinho não informa. O nome pode mudar depois; o registro guarda o que valia no ato.
            reason=(
                f"{membro.identity_subject} — Etapa “{nome_da_etapa}” do Edital "
                f"{edital.number}/{edital.year}"
            ),
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        return ctx.concluir(alocacao, 201)


def alocar_varios(
    *, actor, processo_id, membro_ids, edital_id, etapa_id, idempotency_key, correlation_id
):
    """A mesma operação de `alocar`, para várias pessoas na mesma Etapa e numa submissão.

    **Continua sendo `membro → Etapa`** — é agrupamento de envio, e não distribuição: nada aqui
    escolhe quem vai onde, nem olha carga, nem conhece candidato (§22 e FR-042). O que muda é o
    custo: montar uma banca de quarenta em quatro Etapas eram cento e sessenta submissões, cada
    uma recarregando a página.

    Devolve `(criadas, ja_estavam)`. Quem já está na Etapa não é erro: numa operação em lote,
    recusar o conjunto inteiro porque uma pessoa já estava seria punir o caminho normal.
    """
    etapa_id = identificador(etapa_id)
    ids = [identificador(m) for m in membro_ids]
    if not ids:
        raise DomainError(
            "nenhum_membro_selecionado",
            "Selecione ao menos uma pessoa para alocar.",
            422,
            campo="membro_id",
        )
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="comissao:alocar-varios",
        payload={"membros": sorted(str(i) for i in ids), "etapa": str(etapa_id)},
        idempotency_key=idempotency_key,
    ) as ctx:
        edital = Edital.objects.filter(
            pk=identificador(edital_id),
            processo=ctx.processo,
            institution_scope=ctx.processo.institution_scope,
        ).first()
        if edital is None:
            raise nao_encontrado()
        if ctx.repetido:
            return [], []
        vigentes = etapas_vigentes(edital)
        if etapa_id not in vigentes:
            raise nao_encontrado()
        if not funcoes.tem_presidente(ctx.processo):
            raise DomainError(
                "comissao_sem_presidente",
                "Esta comissão ainda não tem presidente. "
                "Designe a presidência antes de distribuir trabalho.",
                409,
            )
        nome_da_etapa = vigentes[etapa_id].get("name") or str(etapa_id)
        membros = list(
            MembroComissao.objects.filter(pk__in=ids, processo=ctx.processo, ativo=True)
        )
        if len(membros) != len(set(ids)):
            raise DomainError(
                "pessoa_nao_e_membro_ativo",
                "Só membros ativos da comissão podem ser alocados.",
                422,
                campo="membro_id",
            )
        ja = set(
            AlocacaoEtapa.objects.filter(
                membro__in=membros, edital=edital, etapa_id=etapa_id, ativo=True
            ).values_list("membro_id", flat=True)
        )
        criadas = []
        for membro in membros:
            if membro.id in ja:
                continue
            alocacao = AlocacaoEtapa.objects.create(
                membro=membro,
                edital=edital,
                etapa_id=etapa_id,
                criado_em=ctx.now,
                criado_por=actor.subject,
            )
            # Um evento por alocação, como na criação avulsa: a trilha responde por agregado, e
            # um evento de lote não diria quem ganhou acesso a quê (FR-070).
            auditar(
                ctx=ctx,
                actor=actor,
                operation="ALOCACAO_INCLUIR",
                aggregate=alocacao,
                reason=(
                    f"{membro.identity_subject} — Etapa “{nome_da_etapa}” do Edital "
                    f"{edital.number}/{edital.year}; em lote"
                ),
                correlation_id=correlation_id,
            )
            criadas.append(alocacao)
        if criadas:
            ctx.concluir(criadas[0], 201)
        else:
            ctx.concluir_sem_resultado(200)
        return criadas, [m for m in membros if m.id in ja]


def remover_alocacao(*, actor, processo_id, alocacao_id, idempotency_key, correlation_id):
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="comissao:remover-alocacao",
        payload={"alocacao": str(alocacao_id)},
        idempotency_key=idempotency_key,
    ) as ctx:
        # Sem `ativo=True` quando é repetição: a segunda chamada com a mesma chave chega
        # depois da inativação, e responder 404 ali faria o duplo clique virar erro.
        consulta = AlocacaoEtapa.objects.filter(
            pk=identificador(alocacao_id), membro__processo=ctx.processo
        ).select_related("membro", "edital")
        alocacao = (consulta if ctx.repetido else consulta.filter(ativo=True)).first()
        if alocacao is None:
            raise nao_encontrado()
        if ctx.repetido:
            return alocacao, 200
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
                f"{alocacao.membro.identity_subject} — Etapa "
                f"“{nome_da_etapa(alocacao, nomes_das_etapas([alocacao]))}” do Edital "
                f"{alocacao.edital.number}/{alocacao.edital.year}"
            ),
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        return ctx.concluir(alocacao, 200)


def remover_varias_alocacoes(
    *, actor, processo_id, alocacao_ids, idempotency_key, correlation_id
):
    """Desfaz em lote o que se faz em lote.

    Alocar a Etapa inteira virou uma submissão; desfazer continuava custando uma por pessoa. A
    assimetria é o que torna a ida arriscada — quem aloca quarenta na Etapa errada precisa de
    volta pelo mesmo preço.
    """
    ids = [identificador(i) for i in alocacao_ids]
    if not ids:
        raise DomainError(
            "nenhuma_alocacao_selecionada",
            "Selecione ao menos uma alocação para remover.",
            422,
            campo="alocacao_id",
        )
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="comissao:remover-alocacoes",
        payload={"alocacoes": sorted(str(i) for i in ids)},
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return []
        alocacoes = list(
            AlocacaoEtapa.objects.filter(
                pk__in=ids, membro__processo=ctx.processo, ativo=True
            ).select_related("membro", "edital")
        )
        # Recusa o conjunto quando algum identificador não corresponde, como `alocar_varios` faz:
        # remover quatro de cinco e responder sucesso deixa a quinta pessoa com acesso, e quem
        # operou acreditando que a tirou.
        #
        # **409, e não 404.** A causa quase sempre é concorrência — duas pessoas gerindo a mesma
        # comissão, e uma delas com a tela de antes. Responder "recurso não encontrado" derruba a
        # página inteira e não diz o que fazer; aqui a recusa é do estado, e a tela a exibe sem
        # perder o resto da seleção.
        if len(alocacoes) != len(set(ids)):
            raise DomainError(
                "selecao_desatualizada",
                "Parte da seleção já não está ativa — provavelmente alguém alterou esta comissão "
                "enquanto você trabalhava. Recarregue a página e refaça a seleção.",
                409,
                campo="alocacao_id",
            )
        nomes = nomes_das_etapas(alocacoes)
        for alocacao in alocacoes:
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
                    f"{alocacao.membro.identity_subject} — Etapa "
                    f"“{nome_da_etapa(alocacao, nomes)}” do Edital "
                    f"{alocacao.edital.number}/{alocacao.edital.year}; em lote"
                ),
                correlation_id=correlation_id,
            )
        ctx.concluir(alocacoes[0], 200)
        return alocacoes
