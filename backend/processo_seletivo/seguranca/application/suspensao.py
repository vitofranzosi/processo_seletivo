"""Suspender e reativar uma pessoa em todas as unidades (107, incremento 2, US6 e US7).

As regras são as que o usuário decidiu em 30/10/2026 (spec da 107, P1 e P2):

- **A suspensão é global, e não revoga nada** (`FR-3135`, `FR-3139`). A pessoa suspensa não tem
  ator em escopo nenhum e não entra; os vínculos dela ficam vigentes e inertes. A revogação por
  unidade continua ao lado, sem mudança.
- **Quem suspende**: o administrador institucional, pela tela, a qualquer pessoa que não seja ele
  mesmo nem outro administrador institucional; a implantação, pelo comando, a qualquer pessoa
  (`FR-3136`, `FR-3137`).
- **A suspensão mata todas as sessões, e a reativação não as devolve** (`FR-3138`, `FR-3144`,
  `D-015`). Suspender troca a senha inutilizável da pessoa por outra, e com ela o hash de sessão
  que o Django confere a cada requisição: toda sessão aberta antes carrega o hash velho e é apagada
  na requisição seguinte — inclusive a que ficou parada durante a suspensão e só volta depois da
  reativação. `is_active` falso sozinho não bastaria para esta última.
- **Reativar devolve só a entrada** (`FR-3143`): voltam a valer os vínculos ainda vigentes; os
  revogados, antes ou durante a suspensão, continuam revogados.

A suspensão e a reativação são registros append-only (`D-016`); o `is_active` é o efeito, escrito
na mesma transação, e a trilha também.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.seguranca.acessos import (
    ADMINISTRADOR_INSTITUCIONAL,
    ADMINISTRAR,
    ESCOPO_INSTITUCIONAL,
)
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.seguranca.models import ReativacaoDePessoa, SuspensaoDePessoa
from processo_seletivo.shared.api.problems import DomainError

# As recusas (`FR-3136`, `FR-3146`).
PROPRIA_SUSPENSAO = "propria_suspensao"
SO_POR_IMPLANTACAO = "suspensao_so_por_implantacao"
JA_SUSPENSA = "pessoa_ja_suspensa"
NAO_SUSPENSA = "pessoa_nao_suspensa"


def suspensao_aberta(pessoa_id):
    """A suspensão sem reativação da pessoa, ou None."""
    return (
        SuspensaoDePessoa.objects.filter(pessoa_id=pessoa_id, reativacao__isnull=True)
        .order_by("-suspensa_em")
        .first()
    )


def suspensas(pessoas_ids):
    """Quais destas pessoas estão suspensas, numa consulta."""
    return set(
        SuspensaoDePessoa.objects.filter(
            pessoa_id__in=list(pessoas_ids), reativacao__isnull=True
        ).values_list("pessoa_id", flat=True)
    )


def _e_administracao_institucional(pessoa):
    return (
        acessos.vigentes()
        .filter(pessoa=pessoa, escopo=ESCOPO_INSTITUCIONAL, papel=ADMINISTRADOR_INSTITUCIONAL)
        .exists()
    )


def _autoridade(ator, pessoa, *, por_implantacao):
    """A permissão com que o ator suspende ou reativa esta pessoa, ou a recusa (`FR-3136`)."""
    if por_implantacao:
        return acessos.IMPLANTACAO
    require_permission(ator, ADMINISTRAR, institution_scope=ESCOPO_INSTITUCIONAL)
    if pessoa.username == ator.subject:
        raise DomainError(
            PROPRIA_SUSPENSAO,
            "Ninguém suspende nem reativa a si mesmo. Peça a outra pessoa com a mesma permissão.",
            403,
        )
    if _e_administracao_institucional(pessoa):
        raise DomainError(
            SO_POR_IMPLANTACAO,
            "A suspensão e a reativação de quem administra os acessos institucionais se fazem só "
            "pela implantação, com o ato que as determina.",
            403,
        )
    return ADMINISTRAR


def _ator_de_implantacao():
    return Actor(acessos.IMPLANTACAO, ESCOPO_INSTITUCIONAL)


def conferir_suspensao(ator, *, pessoa, por_implantacao=False):
    """As recusas da suspensão, sem gravar — a primeira etapa da tela."""
    _autoridade(ator, pessoa, por_implantacao=por_implantacao)
    if suspensao_aberta(pessoa.pk) is not None:
        raise DomainError(JA_SUSPENSA, "Esta pessoa já está suspensa.", 409)


def conferir_reativacao(ator, *, pessoa, por_implantacao=False):
    """As recusas da reativação, sem gravar."""
    _autoridade(ator, pessoa, por_implantacao=por_implantacao)
    if suspensao_aberta(pessoa.pk) is None:
        raise DomainError(NAO_SUSPENSA, "Esta pessoa não está suspensa.", 409)


def suspender(ator, *, pessoa, motivo, now, correlation_id="", por_implantacao=False):
    """A suspensão global, com o fim de todas as sessões e a trilha (`FR-3135` a `FR-3138`)."""
    ator = _ator_de_implantacao() if por_implantacao else ator
    permissao = _autoridade(ator, pessoa, por_implantacao=por_implantacao)
    motivo = acessos._exigir_motivo(motivo)
    with transaction.atomic():
        # A pessoa trancada serializa duas suspensões: a segunda vê a primeira (`FR-3146`).
        get_user_model().objects.select_for_update().filter(pk=pessoa.pk).first()
        # **A autoridade de novo, sob a trava** (revisão do #346): a concessão e a substituição da
        # administração institucional trancam a mesma linha, e uma que chegasse entre a primeira
        # conferência e a trava deixaria a tela suspender uma administradora institucional.
        _autoridade(ator, pessoa, por_implantacao=por_implantacao)
        if suspensao_aberta(pessoa.pk) is not None:
            raise DomainError(JA_SUSPENSA, "Esta pessoa já está suspensa.", 409)
        suspensao = SuspensaoDePessoa.objects.create(
            pessoa=pessoa, suspensa_em=now, suspensa_por=ator.subject, motivo=motivo
        )
        # O efeito: sem `is_active`, a pessoa não entra nem tem ator; com a senha inutilizável
        # trocada, o hash de toda sessão aberta deixa de conferir (`D-015`). `update`, e não `save`,
        # pela razão de `_atualizar` na autenticação: a escrita mínima.
        get_user_model().objects.filter(pk=pessoa.pk).update(
            is_active=False, password=make_password(None)
        )
        _registrar(ator, permissao, "PESSOA_SUSPENDER", suspensao, now, correlation_id, motivo)
    return suspensao


def reativar(ator, *, pessoa, motivo, now, correlation_id="", por_implantacao=False):
    """O fim da suspensão: a entrada de volta, nenhuma sessão de volta (`FR-3143`, `FR-3144`)."""
    ator = _ator_de_implantacao() if por_implantacao else ator
    permissao = _autoridade(ator, pessoa, por_implantacao=por_implantacao)
    motivo = acessos._exigir_motivo(motivo)
    nao_suspensa = DomainError(NAO_SUSPENSA, "Esta pessoa não está suspensa.", 409)
    with transaction.atomic():
        get_user_model().objects.select_for_update().filter(pk=pessoa.pk).first()
        _autoridade(ator, pessoa, por_implantacao=por_implantacao)
        suspensao = suspensao_aberta(pessoa.pk)
        if suspensao is None:
            raise nao_suspensa
        try:
            with transaction.atomic():
                reativacao = ReativacaoDePessoa.objects.create(
                    suspensao=suspensao, reativada_em=now, reativada_por=ator.subject, motivo=motivo
                )
        except IntegrityError as erro:
            raise nao_suspensa from erro
        # **A senha não volta** (`FR-3144`): a que a suspensão gravou continua, e a sessão aberta
        # antes dela continua com o hash que não confere.
        get_user_model().objects.filter(pk=pessoa.pk).update(is_active=True)
        _registrar(ator, permissao, "PESSOA_REATIVAR", suspensao, now, correlation_id, motivo)
    return reativacao


def acessos_que_voltam(pessoa):
    """Os vínculos vigentes da pessoa, por escopo — o que a reativação devolve (`FR-3145`)."""
    catalogo = acessos.catalogo()
    por_escopo = {}
    for vinculo in acessos.vigentes().filter(pessoa=pessoa).order_by("escopo", "papel"):
        por_escopo.setdefault(vinculo.escopo, []).append(
            catalogo.get(vinculo.papel, (vinculo.papel,))[0]
        )
    return por_escopo


def _registrar(ator, permissao, operacao, suspensao, now, correlation_id, motivo):
    record_event(
        actor=ator,
        permission=permissao,
        operation=operacao,
        aggregate=suspensao,
        now=now,
        correlation_id=correlation_id,
        reason=motivo,
        new_state="suspensa" if operacao == "PESSOA_SUSPENDER" else "ativa",
        new_revision=None,
        detalhe={"pessoa": suspensao.pessoa.username},
    )
