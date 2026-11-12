"""Designar e revogar quem do setor alcança os documentos de um Edital (117, US2, FR-3662).

**Duas mãos, desde a revisão de 12/11/2026** (D-025, FR-6700): `acesso:gerir` na unidade do
Edital, e a presidência da comissão do Processo do Edital. A D-013, de 04/11, dava a designação só a
quem concede o papel; o usuário a reabriu, e a separação de funções que ela protegia ficou no
**papel**, que continua só com a gestão de acessos. A presidência escolhe só entre quem já o tem, e
designar não lhe dá acesso aos documentos (FR-6704). `comissao:gerir` sem presidir não designa.

**As recusas**: Edital ou designação de outra unidade é 404, pelo filtro da consulta; no escopo, sem
nenhuma das duas bases, 403 nomeando as duas (FR-6707). A autodesignação é recusada com código
próprio; a pessoa sem o papel Formalização vigente na unidade do Edital também (FR-3663). Mudar os
Perfis é revogar e designar de novo. A redação anterior desta docstring dizia "a presidência só vê".

**A pessoa trancada serializa duas designações** do mesmo Edital, como a concessão da `107`: trancar
a designação seria `FOR UPDATE` numa append-only, que a role de runtime não pode.

**O Processo é trancado antes da pessoa, e a base é reavaliada sob a trava** (a ordem da `011`, em
`comissoes/application/__init__.py`). A presidência é vínculo que muda: entre a conferência da view
e a gravação, um gestor pode rebaixar ou remover a presidente, e a designação sairia gravada com a
base `comissao:presidir` por quem já não preside. A conferência de fora da transação continua, para
não trabalhar por quem não pode; a que decide é a de dentro, e é a base dela que vai à trilha. O
Processo vem antes da pessoa porque é a ordem dos comandos da comissão, e a mesma ordem nos dois
lados não deixa trava cruzada.
"""

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.formalizacao.application.definir import perfis_do_edital
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.domain.autorizacao import (
    designacoes_vigentes,
    exigir_quem_designa,
)
from processo_seletivo.formalizacao.models import (
    DesignacaoParaFormalizacao,
    RevogacaoDaDesignacao,
)
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
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


def _trancar_o_processo_e_reavaliar(actor, edital):
    """A trava do Processo do Edital e a base relida depois dela (`011`). Dentro da transação."""
    ProcessoSeletivo.objects.select_for_update().filter(pk=edital.processo_id).first()
    return exigir_quem_designa(actor, edital)


def edital_da_unidade(actor, edital_id):
    """O Edital e a base que autoriza designar nele: 404 fora do escopo, 403 sem base (FR-6707).

    O escopo vem **antes**, pelo filtro da consulta: a presidência só se sabe depois de conhecido o
    Processo, e um Edital de outra unidade não pode responder diferente de um inexistente (`033`).
    """
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=actor.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return edital, exigir_quem_designa(actor, edital)


def tem_o_papel(pessoa, escopo):
    return nomes.PAPEL in acessos.papeis_vigentes(pessoa.pk, escopo)


def pessoas_com_o_papel(actor, *, edital=None):
    """Quem tem o papel Formalização vigente na unidade do ator, para a tela escolher (FR-6701).

    Com `edital`, pergunta o predicado de designar nele — é o que a tela da presidência pede; sem,
    exige `acesso:gerir`, como a tela de acessos, que não tem Edital escolhido de início.
    """
    if edital is None:
        require_permission(actor, GERIR)
    else:
        exigir_quem_designa(actor, edital)
    return (
        acessos.vigentes()
        .filter(escopo=actor.institution_scope, papel=nomes.PAPEL, pessoa__is_active=True)
        .exclude(pessoa__username=actor.subject)
        .select_related("pessoa")
        .order_by("pessoa__first_name", "pessoa__username")
    )


#: Os estados em que um Edital recebe designação: publicado, e encerrado, que não fecha a página
#: nem a exportação (FR-3710). Antes de publicado não há Perfil nem documento a alcançar.
ESTADOS_DESIGNAVEIS = frozenset({Edital.Status.PUBLICADO, Edital.Status.ENCERRADO})


def conferir(actor, *, edital, pessoa, perfis):
    """As recusas da designação, sem gravar nada. `designar` confere tudo de novo, sob a trava.

    O estado do Edital é regra do comando, e não só da tela que oferece os Editais: um caminho que
    chegasse aqui direto designaria para um rascunho, sem Perfil publicado a conferir.
    """
    if edital.status not in ESTADOS_DESIGNAVEIS:
        raise DomainError(
            nomes.EDITAL_SEM_PUBLICACAO,
            "Só um Edital publicado ou encerrado recebe designação para a formalização.",
            409,
        )
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
    edital, _ = edital_da_unidade(actor, edital_id)
    motivo = _motivo(motivo)
    with transaction.atomic():
        base = _trancar_o_processo_e_reavaliar(actor, edital)
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
        _registrar(actor, base, nomes.DESIGNAR, designacao, now, correlation_id, motivo)
    return designacao


def revogar(actor, *, designacao_id, motivo, now, correlation_id="", edital_id=None):
    """A revogação, com a mesma autoridade da designação. A segunda o banco recusa.

    **Qualquer designação do Edital**, quem quer que a tenha concedido e por qual base (FR-6703).
    `edital_id`, quando dado, é o Edital da tela que pediu: designação de outro Edital é inexistente
    ali, como a de outra unidade (FR-6707).
    """
    designacoes = DesignacaoParaFormalizacao.objects.filter(
        pk=designacao_id, edital__institution_scope=actor.institution_scope
    )
    if edital_id is not None:
        designacoes = designacoes.filter(edital_id=edital_id)
    designacao = designacoes.select_related("edital__processo").first()
    if designacao is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    exigir_quem_designa(actor, designacao.edital)
    if designacao.pessoa == actor.subject:
        raise DomainError(
            nomes.AUTODESIGNACAO,
            "Ninguém revoga a própria designação. Peça a outra pessoa com a mesma permissão.",
            403,
        )
    motivo = _motivo(motivo)
    ja_revogada = DomainError(nomes.DESIGNACAO_JA_REVOGADA, "Esta designação já foi revogada.", 409)
    with transaction.atomic():
        base = _trancar_o_processo_e_reavaliar(actor, designacao.edital)
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
        _registrar(actor, base, nomes.REVOGAR, designacao, now, correlation_id, motivo)
    return revogacao


def _registrar(actor, base, operacao, designacao, now, correlation_id, motivo):
    """Sob a designação: a trilha do Edital a reúne, e a da unidade a lê pelo tipo (FR-3668).

    `base` é a que autorizou, `acesso:gerir` ou `comissao:presidir` (FR-6705), como a `011` registra
    a base da gestão da comissão.
    """
    record_event(
        actor=actor,
        permission=base,
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
