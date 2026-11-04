"""Designar e revogar quem do setor alcança os documentos de um Edital (117, US2, FR-3662).

**A mesma mão que concede o papel** (D-013): `acesso:gerir`, na unidade do Edital. A presidência só
vê. Quem conduz a seleção decidir quem recebe documentos de candidatos borraria a separação que a
`D-002` afirma.

**As recusas, na ordem da `107`**: sem `acesso:gerir` é 403, Edital de outra unidade é 404; a
autodesignação é recusada com código próprio; a pessoa sem o papel Formalização vigente na unidade
do Edital também (FR-3663). Mudar os Perfis é revogar e designar de novo.

**A pessoa trancada serializa duas designações** do mesmo Edital, como a concessão da `107`: trancar
a designação seria `FOR UPDATE` numa append-only, que a role de runtime não pode.
"""

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.formalizacao.application.definir import perfis_do_edital
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.domain.autorizacao import designacoes_vigentes
from processo_seletivo.formalizacao.models import (
    DesignacaoParaFormalizacao,
    RevogacaoDaDesignacao,
)
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.acessos import GERIR
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError


def _motivo(motivo):
    motivo = (motivo or "").strip()
    if not motivo:
        raise DomainError(
            nomes.MOTIVO_OBRIGATORIO,
            "Informe o motivo — por exemplo, o memorando que pediu o acesso. A trilha guarda por "
            "que o acesso foi dado ou tirado.",
            422,
            campo="motivo",
        )
    return motivo


def edital_da_unidade(actor, edital_id):
    """O Edital, se o ator tem `acesso:gerir` e está na unidade dele: 403 e 404 da matriz."""
    require_permission(actor, GERIR)
    edital = Edital.objects.filter(pk=edital_id, institution_scope=actor.institution_scope).first()
    if edital is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return edital


def tem_o_papel(pessoa, escopo):
    return nomes.PAPEL in acessos.papeis_vigentes(pessoa.pk, escopo)


def pessoas_com_o_papel(actor):
    """Quem tem o papel Formalização vigente na unidade do ator, para a tela escolher."""
    require_permission(actor, GERIR)
    return (
        acessos.vigentes()
        .filter(escopo=actor.institution_scope, papel=nomes.PAPEL, pessoa__is_active=True)
        .exclude(pessoa__username=actor.subject)
        .select_related("pessoa")
        .order_by("pessoa__first_name", "pessoa__username")
    )


def conferir(actor, *, edital, pessoa, perfis):
    """As recusas da designação, sem gravar nada. `designar` confere tudo de novo, sob a trava."""
    if pessoa.username == actor.subject:
        raise DomainError(
            nomes.AUTODESIGNACAO,
            "Ninguém designa a si mesmo. Peça a outra pessoa com a mesma permissão.",
            403,
        )
    if not pessoa.is_active:
        raise DomainError(
            nomes.PESSOA_INDISPONIVEL,
            "Esta pessoa está suspensa ou desativada, e não recebe designação.",
            409,
        )
    if not tem_o_papel(pessoa, edital.institution_scope):
        raise DomainError(
            nomes.DESIGNADO_SEM_PAPEL,
            f"Esta pessoa não tem o papel {nomes.NOME_DO_PAPEL} nesta unidade. Conceda o papel "
            "em Acessos da unidade antes de designá-la.",
            422,
        )
    conhecidos = {perfil.id for perfil in perfis_do_edital(edital)}
    pedidos = sorted({str(perfil) for perfil in perfis if str(perfil).strip()})
    if any(perfil not in conhecidos for perfil in pedidos):
        raise DomainError(
            nomes.PERFIL_FORA_DO_EDITAL,
            "Um dos Perfis marcados não é deste Edital. Abra a tela de novo.",
            422,
        )
    if designacoes_vigentes(pessoa=pessoa.username, edital=edital).exists():
        raise DomainError(
            nomes.DESIGNACAO_JA_VIGENTE,
            "Esta pessoa já está designada para este Edital. Para mudar os Perfis, revogue a "
            "designação e designe de novo.",
            409,
        )
    return pedidos


def designar(actor, *, edital_id, pessoa, perfis, motivo, now, correlation_id=""):
    """A designação nova, depois de todas as recusas, com a trilha da unidade e do Edital."""
    edital = edital_da_unidade(actor, edital_id)
    motivo = _motivo(motivo)
    with transaction.atomic():
        travada = get_user_model().objects.select_for_update().filter(pk=pessoa.pk).first()
        if travada is None:
            raise DomainError(nomes.PESSOA_INDISPONIVEL, "Esta pessoa não está disponível.", 409)
        pedidos = conferir(actor, edital=edital, pessoa=travada, perfis=perfis)
        designacao = DesignacaoParaFormalizacao.objects.create(
            edital=edital,
            pessoa=travada.username,
            perfis=pedidos,
            motivo=motivo,
            designado_por=actor.subject,
            unidade_de_atuacao=actor.institution_scope,
            designado_em=now,
        )
        _registrar(actor, nomes.DESIGNAR, designacao, now, correlation_id, motivo)
    return designacao


def revogar(actor, *, designacao_id, motivo, now, correlation_id=""):
    """A revogação, com a mesma autoridade da designação. A segunda o banco recusa."""
    require_permission(actor, GERIR)
    designacao = (
        DesignacaoParaFormalizacao.objects.filter(
            pk=designacao_id, edital__institution_scope=actor.institution_scope
        )
        .select_related("edital")
        .first()
    )
    if designacao is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    if designacao.pessoa == actor.subject:
        raise DomainError(
            nomes.AUTODESIGNACAO,
            "Ninguém revoga a própria designação. Peça a outra pessoa com a mesma permissão.",
            403,
        )
    motivo = _motivo(motivo)
    ja_revogada = DomainError(nomes.DESIGNACAO_JA_REVOGADA, "Esta designação já foi revogada.", 409)
    with transaction.atomic():
        get_user_model().objects.select_for_update().filter(username=designacao.pessoa).first()
        if RevogacaoDaDesignacao.objects.filter(designacao=designacao).exists():
            raise ja_revogada
        try:
            with transaction.atomic():
                revogacao = RevogacaoDaDesignacao.objects.create(
                    designacao=designacao,
                    motivo=motivo,
                    revogado_por=actor.subject,
                    unidade_de_atuacao=actor.institution_scope,
                    revogado_em=now,
                )
        except IntegrityError as erro:
            raise ja_revogada from erro
        _registrar(actor, nomes.REVOGAR, designacao, now, correlation_id, motivo)
    return revogacao


def _registrar(actor, operacao, designacao, now, correlation_id, motivo):
    """Sob a designação: a trilha do Edital a reúne, e a da unidade a lê pelo tipo (FR-3668)."""
    record_event(
        actor=actor,
        permission=GERIR,
        operation=operacao,
        aggregate=designacao,
        now=now,
        correlation_id=correlation_id,
        reason=motivo,
        new_state="revogada" if operacao == nomes.REVOGAR else "vigente",
        new_revision=None,
        detalhe={
            "edital": str(designacao.edital_id),
            "pessoa": designacao.pessoa,
            "perfis": [str(perfil) for perfil in designacao.perfis],
        },
    )
