"""Administrar o registro de Unidades pela aplicação (110, `D-006` a `D-008`).

**A permissão é conferida aqui, e não só na tela** (FR-3309). Cada ato e cada leitura exige
`unidade:administrar` com o escopo ativo institucional, como recusa explicada (403) — a mesma da
gestão de acessos da `107`, e não a de objeto inexistente, porque o que falta é a base, e não o
objeto. A tela é a segunda barreira.

**Duas etapas, como na `107`.** As conferências só leem; o ato reconfere tudo sob a trava da linha,
e grava a unidade e o evento na mesma transação (FR-3332). A edição, a desativação e a reativação
recebem a versão que a conferência mostrou (`D-007`): se outra pessoa mudou a unidade entre as duas
etapas, o ato recusa em vez de sobrescrever.

**O evento é da unidade, e não do nível institucional** (`D-008`). Grava-se com o ator no escopo da
unidade — o mesmo `subject`, as mesmas permissões —, como a semente já faz com a implantação: é o
que põe o ato diante do auditor da unidade, e na trilha da `108` sem mudança nela.
"""

import hashlib
import json

from django.db import IntegrityError, transaction

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.seguranca.acessos import ESCOPO_INSTITUCIONAL
from processo_seletivo.seguranca.application.authorization import (
    base_de_permissao,
    require_authorization_base,
)
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.unidades.domain import nomes
from processo_seletivo.unidades.domain.registro import EDITAVEIS, validar_campos, validar_codigo
from processo_seletivo.unidades.models import Unidade

BASE = base_de_permissao("administrar o registro de unidades")
CAMPOS = (*EDITAVEIS, "ativa")
SIGLA_DA_INSTITUICAO = "Ifes"


def exigir_permissao(ator):
    require_authorization_base(
        ator is not None
        and ator.can(nomes.ADMINISTRAR)
        and ator.institution_scope == ESCOPO_INSTITUCIONAL,
        bases=[BASE],
    )


def _motivo(motivo):
    motivo = (motivo or "").strip()
    if not motivo:
        raise DomainError(
            nomes.MOTIVO_OBRIGATORIO,
            "Informe o motivo — por exemplo, o ato ou o pedido que determinou a mudança.",
            422,
            campo="motivo",
        )
    return motivo


def _nao_registrada():
    return DomainError(nomes.UNIDADE_NAO_REGISTRADA, "Esta unidade não está registrada.", 404)


def campos_de(unidade):
    return {campo: getattr(unidade, campo) for campo in CAMPOS}


def versao(unidade):
    """O resumo dos valores (`D-007`): sem coluna nova, e sem `alterada_em`, que é efeito."""
    canonico = json.dumps(campos_de(unidade), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonico.encode()).hexdigest()


def _situacao(ativa):
    return "ATIVA" if ativa else "DESATIVADA"


def _da_unidade(ator, codigo):
    return Actor(ator.subject, codigo, ator.permissions)


def _gravar_evento(ator, unidade, operacao, *, antes, now, motivo, correlation_id):
    record_event(
        actor=_da_unidade(ator, unidade.codigo),
        permission=nomes.ADMINISTRAR,
        operation=operacao,
        aggregate=unidade,
        now=now,
        correlation_id=correlation_id,
        reason=motivo,
        previous_state=_situacao(antes["ativa"]) if antes else "",
        new_state=_situacao(unidade.ativa),
        new_revision=None,
        detalhe=(
            {"antes": antes, "depois": campos_de(unidade)}
            if antes
            else {"depois": campos_de(unidade)}
        ),
    )


def _rotulo(siglas):
    return f"{siglas[0]}/{SIGLA_DA_INSTITUICAO}" if len(siglas) == 1 else SIGLA_DA_INSTITUICAO


def mudanca_da_moldura(*, codigo, ativa_depois, sigla_depois):
    """Como as telas sem unidade passam a se identificar, se o ato muda isso (FR-3330, EC-7).

    A regra é a da `109`: exatamente uma unidade ativa dá a marca dela; nenhuma ou várias, só o
    Ifes. Devolve `(antes, depois)`, ou `None` quando o ato não muda a moldura.
    """
    ativas = dict(Unidade.objects.filter(ativa=True).values_list("codigo", "sigla"))
    antes = _rotulo(list(ativas.values()))
    if ativa_depois:
        ativas[codigo] = sigla_depois
    else:
        ativas.pop(codigo, None)
    depois = _rotulo(list(ativas.values()))
    return (antes, depois) if antes != depois else None


# --- Leituras ----------------------------------------------------------------------------------


def listar(ator):
    exigir_permissao(ator)
    return list(Unidade.objects.order_by("sigla", "codigo"))


def ficha(ator, *, codigo):
    """A unidade, a versão e os eventos dela, do mais recente ao mais antigo (FR-3315, `D-009`)."""
    from processo_seletivo.auditoria.models import RegistroAuditoria

    exigir_permissao(ator)
    unidade = Unidade.objects.filter(codigo=str(codigo or "")).first()
    if unidade is None:
        raise _nao_registrada()
    eventos = RegistroAuditoria.objects.filter(aggregate_type="Unidade", aggregate_id=unidade.pk)
    eventos = list(eventos.order_by("-occurred_at", "-event_id"))
    return unidade, versao(unidade), eventos


def _unidade(codigo, *, travar=False):
    consulta = Unidade.objects.filter(codigo=str(codigo or ""))
    if travar:
        consulta = consulta.select_for_update()
    unidade = consulta.first()
    if unidade is None:
        raise _nao_registrada()
    return unidade


def processos_nao_encerrados(codigo):
    from processo_seletivo.processos.models import ProcessoSeletivo

    encerrados = (ProcessoSeletivo.Status.ENCERRADO, ProcessoSeletivo.Status.CANCELADO)
    return (
        ProcessoSeletivo.objects.filter(institution_scope=codigo)
        .exclude(status__in=encerrados)
        .count()
    )


# --- Cadastrar ---------------------------------------------------------------------------------


def conferir_registro(ator, *, campos):
    """Os valores aparados do cadastro, ou a primeira recusa, sem gravar (FR-3316, FR-3317)."""
    exigir_permissao(ator)
    codigo = validar_codigo(campos.get("codigo"))
    valores = validar_campos(campos)
    if Unidade.objects.filter(codigo=codigo).exists():
        raise _ja_registrado()
    return {"codigo": codigo, **valores}


def _ja_registrado():
    return DomainError(
        nomes.CODIGO_JA_REGISTRADO,
        "Já há uma unidade com este código. O código é permanente: escolha outro.",
        409,
        campo="codigo",
    )


def registrar(ator, *, campos, motivo, correlation_id=""):
    """A unidade nova, ativa, com os modelos iniciais e o evento, tudo ou nada (FR-3316–FR-3319)."""
    from processo_seletivo.avisos.application.modelos import criar_modelos_iniciais

    valores = conferir_registro(ator, campos=campos)
    motivo = _motivo(motivo)
    with command_context() as now:
        try:
            # Aninhado: a unicidade violada por um cadastro simultâneo do mesmo código não envenena
            # a transação de fora, e vira a recusa de código já registrado (EC-2).
            with transaction.atomic():
                unidade = Unidade.objects.create(registrada_em=now, ativa=True, **valores)
        except IntegrityError as erro:
            raise _ja_registrado() from erro
        _gravar_evento(
            ator,
            unidade,
            "REGISTRAR_UNIDADE",
            antes=None,
            now=now,
            motivo=motivo,
            correlation_id=correlation_id,
        )
        criar_modelos_iniciais(
            unidade.codigo,
            actor=_da_unidade(ator, unidade.codigo),
            permission=nomes.ADMINISTRAR,
            now=now,
            correlation_id=correlation_id,
            razao="Modelo inicial criado no cadastro da unidade (110).",
        )
    return unidade


# --- Editar ------------------------------------------------------------------------------------


def _mudados(antes, depois):
    return [campo for campo in EDITAVEIS if antes[campo] != depois[campo]]


def conferir_alteracao(ator, *, codigo, campos):
    """O antes, o depois, os campos mudados e a versão — sem gravar nada (FR-3321, FR-3322).

    O código vem da rota; um `codigo` nos campos é ignorado (EC-9).
    """
    exigir_permissao(ator)
    unidade = _unidade(codigo)
    depois = validar_campos(campos)
    antes = campos_de(unidade)
    mudados = _mudados(antes, depois)
    if not mudados:
        raise DomainError(
            nomes.NADA_MUDOU,
            "Nenhum campo mudou. Altere ao menos um, ou volte sem salvar.",
            422,
        )
    return {
        "unidade": unidade,
        "antes": antes,
        "depois": {**depois, "ativa": unidade.ativa},
        "mudados": mudados,
        "versao": versao(unidade),
    }


def _conferir_versao(unidade, versao_conferida):
    if versao(unidade) != (versao_conferida or ""):
        raise DomainError(
            nomes.UNIDADE_ALTERADA,
            "Outra pessoa alterou esta unidade depois da sua conferência. Confira de novo antes "
            "de confirmar.",
            409,
        )


def alterar(ator, *, codigo, campos, versao, motivo, correlation_id=""):
    """Grava os campos mudados e o evento com o antes e o depois (FR-3321 a FR-3325)."""
    conferir_alteracao(ator, codigo=codigo, campos=campos)
    motivo = _motivo(motivo)
    with command_context() as now:
        unidade = _unidade(codigo, travar=True)
        _conferir_versao(unidade, versao)
        depois = validar_campos(campos)
        antes = campos_de(unidade)
        if not _mudados(antes, depois):
            raise DomainError(nomes.NADA_MUDOU, "Nenhum campo mudou.", 422)
        for campo, valor in depois.items():
            setattr(unidade, campo, valor)
        unidade.alterada_em = now
        unidade.save(update_fields=[*EDITAVEIS, "alterada_em"])
        _gravar_evento(
            ator,
            unidade,
            "ALTERAR_UNIDADE",
            antes=antes,
            now=now,
            motivo=motivo,
            correlation_id=correlation_id,
        )
    return unidade


# --- Desativar e reativar ----------------------------------------------------------------------


def consequencias(ator, *, codigo, ato):
    """O que a tela diz antes de desativar ou reativar (FR-3326, FR-3327, FR-3330)."""
    exigir_permissao(ator)
    unidade = _unidade(codigo)
    ativa_depois = ato == "reativar"
    return {
        "unidade": unidade,
        "versao": versao(unidade),
        "processos_nao_encerrados": processos_nao_encerrados(unidade.codigo),
        "moldura": mudanca_da_moldura(
            codigo=unidade.codigo, ativa_depois=ativa_depois, sigla_depois=unidade.sigla
        ),
    }


def _mudar_situacao(ator, *, codigo, ativa, versao, motivo, correlation_id):
    exigir_permissao(ator)
    motivo = _motivo(motivo)
    with command_context() as now:
        unidade = _unidade(codigo, travar=True)
        if unidade.ativa == ativa:
            raise DomainError(
                nomes.UNIDADE_JA_ATIVA if ativa else nomes.UNIDADE_JA_DESATIVADA,
                "A unidade já está ativa." if ativa else "A unidade já está desativada.",
                409,
            )
        _conferir_versao(unidade, versao)
        antes = campos_de(unidade)
        unidade.ativa = ativa
        unidade.alterada_em = now
        unidade.save(update_fields=["ativa", "alterada_em"])
        _gravar_evento(
            ator,
            unidade,
            "ALTERAR_UNIDADE",
            antes=antes,
            now=now,
            motivo=motivo,
            correlation_id=correlation_id,
        )
    return unidade


def desativar(ator, *, codigo, versao, motivo, correlation_id=""):
    """A unidade não recebe Processo, Edital nem acesso novos; o que existe continua (FR-3326)."""
    return _mudar_situacao(
        ator,
        codigo=codigo,
        ativa=False,
        versao=versao,
        motivo=motivo,
        correlation_id=correlation_id,
    )


def reativar(ator, *, codigo, versao, motivo, correlation_id=""):
    """A unidade volta a receber Processo, Edital e acesso (FR-3327)."""
    return _mudar_situacao(
        ator,
        codigo=codigo,
        ativa=True,
        versao=versao,
        motivo=motivo,
        correlation_id=correlation_id,
    )
