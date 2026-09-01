"""Alocar membros às Etapas, e desfazer a alocação.

A Etapa é sempre lida do conteúdo vigente, nunca de `edital.etapas` — ver `domain/etapas.py`.
"""

from django.db import IntegrityError

from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.application.comissao import auditar, identificador
from processo_seletivo.comissoes.domain import funcoes
from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
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
        if etapa_id not in etapas_vigentes(edital):
            raise nao_encontrado()
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
            reason=(
                f"{membro.identity_subject} — Etapa {etapa_id} do Edital {edital.number}/"
                f"{edital.year}"
            ),
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        return ctx.concluir(alocacao, 201)


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
        )
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
                f"{alocacao.membro.identity_subject} — Etapa {alocacao.etapa_id} do Edital "
                f"{alocacao.edital_id}"
            ),
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        return ctx.concluir(alocacao, 200)
