"""Os modelos de aviso da unidade: criar, editar, inativar, reativar — e nunca excluir (`FR-1260`).

**Mutáveis e auditados** (`FR-1277`). O modelo é instrumento de trabalho da seleção; o aviso guarda
o texto como saiu, e por isso editar o modelo não reescreve aviso nenhum (`FR-1261`). Cada mudança
vai à trilha com o antes e o depois.

**Por papel, e não pela presidência** (`D-004`). O acervo de modelos é da unidade, transversal aos
Processos; quem preside uma comissão usa os modelos no aviso, mas não os administra.
"""

from django.db import IntegrityError, transaction

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.domain.mensagem import validar_texto
from processo_seletivo.avisos.domain.modelos_iniciais import MODELOS_INICIAIS
from processo_seletivo.avisos.domain.variaveis import validar
from processo_seletivo.avisos.models import ModeloDeAviso
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context


def nao_encontrado():
    return DomainError(nomes.MODELO_NAO_ENCONTRADO, "Modelo de aviso não encontrado.", 404)


def exigir_quem_gere(actor):
    """`aviso:enviar` por papel: a presidência não chega aqui, e a resposta é a de inexistente."""
    if actor is None or not actor.can(nomes.PERMISSAO):
        raise nao_encontrado()


def modelos_da_unidade(actor):
    exigir_quem_gere(actor)
    return list(
        ModeloDeAviso.objects.filter(institution_scope=actor.institution_scope).order_by(
            "-ativo", "nome"
        )
    )


def modelo_da_unidade(actor, modelo_id):
    exigir_quem_gere(actor)
    modelo = ModeloDeAviso.objects.filter(
        pk=modelo_id, institution_scope=actor.institution_scope
    ).first()
    if modelo is None:
        raise nao_encontrado()
    return modelo


def _validar(nome, assunto, corpo):
    nome = (nome or "").strip()
    if not nome:
        raise DomainError(nomes.AVISO_TEXTO_INVALIDO, "Dê um nome ao modelo.", 422, campo="nome")
    if len(nome) > nomes.NOME_DO_MODELO_MAXIMO:
        raise DomainError(
            nomes.AVISO_TEXTO_INVALIDO,
            f"O nome tem mais de {nomes.NOME_DO_MODELO_MAXIMO} caracteres.",
            422,
            campo="nome",
        )
    assunto, corpo = validar_texto(assunto=assunto, corpo=corpo)
    # O modelo serve a qualquer aviso: só a variável desconhecida o recusa (`FR-1256`).
    validar(assunto, campo="assunto")
    validar(corpo, campo="corpo")
    return nome, assunto, corpo


def _estado(modelo):
    return "ATIVO" if modelo.ativo else "INATIVO"


def _auditar(actor, modelo, *, now, antes, razao, correlation_id):
    from processo_seletivo.auditoria.application import record_event

    record_event(
        actor=actor,
        permission=nomes.PERMISSAO,
        operation=nomes.OPERACAO_MODELO,
        aggregate=modelo,
        now=now,
        correlation_id=correlation_id,
        reason=razao,
        previous_state=_estado(antes) if antes is not None else "",
        new_state=_estado(modelo),
        new_revision=None,
        detalhe={
            "antes": _campos(antes) if antes is not None else None,
            "depois": _campos(modelo),
        },
    )


def _campos(modelo):
    return {
        "nome": modelo.nome,
        "assunto": modelo.assunto,
        "corpo": modelo.corpo,
        "ativo": modelo.ativo,
    }


def _nome_repetido():
    return DomainError(
        nomes.MODELO_COM_NOME_REPETIDO,
        "Já existe um modelo com este nome nesta unidade.",
        409,
        campo="nome",
    )


def criar(*, actor, nome, assunto, corpo, correlation_id="interface-modelos"):
    exigir_quem_gere(actor)
    nome, assunto, corpo = _validar(nome, assunto, corpo)
    try:
        with command_context() as now:
            modelo = ModeloDeAviso.objects.create(
                institution_scope=actor.institution_scope,
                nome=nome,
                assunto=assunto,
                corpo=corpo,
                criado_por=actor.subject,
                criado_em=now,
            )
            _auditar(
                actor,
                modelo,
                now=now,
                antes=None,
                razao="Modelo criado.",
                correlation_id=correlation_id,
            )
    except IntegrityError:
        raise _nome_repetido() from None
    return modelo


def salvar_como_novo_modelo(*, actor, nome, assunto, corpo):
    """ "Salvar este texto como novo modelo", na confirmação do aviso (`FR-1261`).

    Cria um modelo, e nunca toca no de origem. Quem só preside a comissão não gere modelos, e a
    recusa chega como mensagem na tela do aviso, que já foi confirmado.
    """
    return criar(
        actor=actor, nome=nome, assunto=assunto, corpo=corpo, correlation_id="interface-aviso"
    )


def editar(*, actor, modelo_id, nome, assunto, corpo, correlation_id="interface-modelos"):
    nome, assunto, corpo = _validar(nome, assunto, corpo)
    try:
        with command_context() as now:
            modelo = (
                ModeloDeAviso.objects.select_for_update()
                .filter(pk=modelo_id, institution_scope=getattr(actor, "institution_scope", ""))
                .first()
            )
            exigir_quem_gere(actor)
            if modelo is None:
                raise nao_encontrado()
            antes = ModeloDeAviso(**{**_campos(modelo)})
            modelo.nome, modelo.assunto, modelo.corpo = nome, assunto, corpo
            modelo.alterado_por, modelo.alterado_em = actor.subject, now
            modelo.save(update_fields=["nome", "assunto", "corpo", "alterado_por", "alterado_em"])
            _auditar(
                actor,
                modelo,
                now=now,
                antes=antes,
                razao="Modelo editado.",
                correlation_id=correlation_id,
            )
    except IntegrityError:
        raise _nome_repetido() from None
    return modelo


def mudar_situacao(*, actor, modelo_id, ativo, correlation_id="interface-modelos"):
    """Inativar tira do seletor e não apaga nada; reativar devolve (`FR-1260`)."""
    exigir_quem_gere(actor)
    with command_context() as now:
        modelo = (
            ModeloDeAviso.objects.select_for_update()
            .filter(pk=modelo_id, institution_scope=actor.institution_scope)
            .first()
        )
        if modelo is None:
            raise nao_encontrado()
        if modelo.ativo == ativo:
            return modelo
        antes = ModeloDeAviso(**{**_campos(modelo)})
        modelo.ativo = ativo
        modelo.alterado_por, modelo.alterado_em = actor.subject, now
        modelo.save(update_fields=["ativo", "alterado_por", "alterado_em"])
        _auditar(
            actor,
            modelo,
            now=now,
            antes=antes,
            razao="Modelo reativado." if ativo else "Modelo inativado.",
            correlation_id=correlation_id,
        )
    return modelo


def garantir_modelos_iniciais(*, correlation_id="sincronizar-unidades"):
    """Cria os três modelos iniciais em cada unidade que **nunca** teve modelo inicial (`R-012`).

    **Só insere.** Não relê, não atualiza e não sobrescreve texto: a unidade que editou ou inativou
    os três continua com os dela, porque a conferência é pela marca `modelo_inicial`, e modelo nunca
    se exclui. **Idempotente sob concorrência**: as unidades são travadas com `select_for_update`,
    como `sincronizar` já faz, e a segunda execução espera a primeira; se a trava faltasse, o índice
    único de nome por escopo recusaria a cópia.

    Devolve quantos modelos criou.
    """
    from processo_seletivo.auditoria.application import record_event
    from processo_seletivo.seguranca.domain import Actor
    from processo_seletivo.unidades.domain import nomes as nomes_das_unidades
    from processo_seletivo.unidades.models import Unidade

    criados = 0
    with transaction.atomic(), command_context() as now:
        for unidade in Unidade.objects.select_for_update().order_by("codigo"):
            if ModeloDeAviso.objects.filter(
                institution_scope=unidade.codigo, modelo_inicial=True
            ).exists():
                continue
            ator = Actor(nomes_das_unidades.IMPLANTACAO, unidade.codigo)
            for nome, assunto, corpo in MODELOS_INICIAIS:
                if ModeloDeAviso.objects.filter(
                    institution_scope=unidade.codigo, nome__iexact=nome
                ).exists():
                    # Um modelo que a unidade criou com o mesmo nome antes da 066 é dela: não se
                    # sobrescreve, e o inicial correspondente simplesmente não nasce.
                    continue
                modelo = ModeloDeAviso.objects.create(
                    institution_scope=unidade.codigo,
                    nome=nome,
                    assunto=assunto,
                    corpo=corpo,
                    modelo_inicial=True,
                    criado_por=nomes_das_unidades.IMPLANTACAO,
                    criado_em=now,
                )
                record_event(
                    actor=ator,
                    permission=nomes_das_unidades.IMPLANTACAO,
                    operation=nomes.OPERACAO_MODELO,
                    aggregate=modelo,
                    now=now,
                    correlation_id=correlation_id,
                    reason="Modelo inicial criado na sincronização das unidades (066, D-008).",
                    new_state="ATIVO",
                    new_revision=None,
                    detalhe={"depois": _campos(modelo)},
                )
                criados += 1
    return criados


__all__ = [
    "criar",
    "editar",
    "garantir_modelos_iniciais",
    "modelo_da_unidade",
    "modelos_da_unidade",
    "mudar_situacao",
    "salvar_como_novo_modelo",
]
