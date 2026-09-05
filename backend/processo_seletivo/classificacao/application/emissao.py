"""Constitui a proposta calculada como um único ato imutável e auditado."""

from datetime import date, datetime
from decimal import Decimal

from processo_seletivo.avaliacoes.application.distribuicao import resultado_declarado
from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.api.problems import DomainError

EMITIR = "CLASSIFICACAO_EMITIR"
ATO = "classificacao:emitir"


def emitir_ordem(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    idempotency_key,
    correlation_id,
):
    """Emite o primeiro ato do marco; sucessão deliberada entra na US6."""
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        # Antes de buscar Edital, recalcular ou perguntar pelo ato atual: uma repetição devolve o
        # desfecho que o primeiro pedido declarou, e não uma leitura do mundo depois dele.
        if ctx.repetido:
            return ctx.desfecho_anterior
        edital = _edital_do_processo(ctx.processo, edital_id)
        if AtoDeOrdenacao.objects.filter(
            edital=edital,
            perfil_id=identificador(perfil_id),
            marco_id=identificador(marco_id),
            sucessores__isnull=True,
        ).exists():
            raise DomainError(
                "ordering_act_already_exists",
                "Este marco já possui ato vigente; uma nova emissão exige recálculo e sucessão "
                "confirmados.",
                409,
            )

        proposta = calcular_ordem(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            at=ctx.now,
        )
        ato = AtoDeOrdenacao.objects.create(
            edital=edital,
            perfil_id=proposta["perfil"]["id"],
            marco_id=proposta["marco"]["id"],
            versao=proposta["versao"],
            universo=proposta["universo"],
            emitido_por=actor.subject,
            emitido_em=ctx.now,
        )
        PosicaoNaOrdem.objects.bulk_create(
            [_posicao(ato, item, proposta["marco"]) for item in proposta["posicoes"]]
            + [_posicao(ato, item, proposta["marco"]) for item in proposta["sem_posicao"]]
        )
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=EMITIR,
            aggregate=ato,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=f"Ordem do marco {proposta['marco'].get('name') or marco_id} emitida.",
            idempotency_key=idempotency_key,
        )
        declarado = resultado_declarado([ato], [], "emitida")
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


def _edital_do_processo(processo, edital_id):
    edital = Edital.objects.filter(
        pk=identificador(edital_id),
        processo=processo,
        institution_scope=processo.institution_scope,
    ).first()
    if edital is None:
        raise nao_encontrado()
    return edital


def _posicao(ato, item, marco):
    return PosicaoNaOrdem(
        ato=ato,
        inscricao_id=item["inscricao_id"],
        posicao=item["posicao"],
        pontuacao_combinada=item["pontuacao"],
        modalidade_id=item["modalidade_id"],
        consequencia=item["consequencia"],
        motivo=item["motivo"],
        empate_residual=item["empate_residual"],
        desempate=_proveniencia_do_desempate(item, marco.get("tiebreakers") or []),
    )


def _proveniencia_do_desempate(item, criterios):
    separou = item.get("separado_por") or {}
    return [
        {
            "criterionId": str(criterio.get("id")),
            "order": criterio.get("order"),
            "type": criterio.get("type"),
            "value": _valor_serializavel(_valor_do_criterio(criterio, item)),
            "separated": str(criterio.get("id")) == str(separou.get("id")),
        }
        for criterio in criterios
    ]


def _valor_do_criterio(criterio, item):
    parametros = criterio.get("parameters") or {}
    if criterio.get("type") == "MAIOR_PONTUACAO_NA_ETAPA":
        return item["pontuacoes"].get(str(parametros.get("stageId")))
    return item["fatos"].get(str(parametros.get("factId")))


def _valor_serializavel(valor):
    if isinstance(valor, Decimal):
        return f"{valor:f}"
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    return valor


__all__ = ["ATO", "EMITIR", "emitir_ordem"]
