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
from processo_seletivo.shared.canonical import canonical_sha256

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
    confirmacao_do_calculo,
    motivo="",
):
    """Emite a proposta confirmada; havendo vigente, cria sucessor sem alterar o anterior."""
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "confirmacao": confirmacao_do_calculo or "",
        "motivo": (motivo or "").strip(),
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
        vigente = AtoDeOrdenacao.objects.filter(
            edital=edital,
            perfil_id=identificador(perfil_id),
            marco_id=identificador(marco_id),
            sucessores__isnull=True,
        ).first()

        proposta = calcular_ordem(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            at=ctx.now,
        )
        esperada = assinatura_da_proposta(proposta, ato_vigente=vigente)
        if not (confirmacao_do_calculo or "").strip():
            raise DomainError(
                "ordering_confirmation_required",
                "Confirme a ordem calculada antes de emitir.",
                422,
                campo="confirmacao_do_calculo",
            )
        if confirmacao_do_calculo != esperada:
            raise DomainError(
                "ordering_act_already_exists"
                if vigente is not None
                else "stale_ordering_calculation",
                (
                    "Outro ato foi emitido depois da sua leitura; confira a ordem atual "
                    "antes de tentar de novo."
                    if vigente is not None
                    else (
                        "A ordem mudou desde a sua leitura; confira o cálculo atual "
                        "antes de emitir."
                    )
                ),
                409 if vigente is not None else 422,
                campo="confirmacao_do_calculo",
            )
        texto_do_motivo = (motivo or "").strip()
        if vigente is not None and not texto_do_motivo:
            raise DomainError(
                "ordering_succession_reason_required",
                "Declare o motivo da sucessão do ato vigente.",
                422,
                campo="motivo",
            )
        ato = AtoDeOrdenacao.objects.create(
            edital=edital,
            perfil_id=proposta["perfil"]["id"],
            marco_id=proposta["marco"]["id"],
            versao=proposta["versao"],
            ato_anterior=vigente,
            motivo_da_sucessao=texto_do_motivo,
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
            reason=(
                texto_do_motivo
                or f"Ordem do marco {proposta['marco'].get('name') or marco_id} emitida."
            ),
            idempotency_key=idempotency_key,
        )
        declarado = resultado_declarado([ato], [], "emitida")
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


def assinatura_da_proposta(proposta, *, ato_vigente=None):
    """Identidade do que foi conferido, vinculada ao vigente visto naquela leitura."""
    linhas = proposta["posicoes"] + proposta["sem_posicao"]
    return canonical_sha256(
        {
            "atoVigente": str(ato_vigente.id) if ato_vigente is not None else None,
            "universo": proposta["universo"],
            "ordem": [
                {
                    "inscricaoId": item["inscricao_id"],
                    "posicao": item["posicao"],
                    "pontuacao": item["pontuacao"],
                    "consequencia": item["consequencia"],
                    "motivo": item["motivo"],
                    "empateResidual": item["empate_residual"],
                    "separadoPor": (item.get("separado_por") or {}).get("id"),
                }
                for item in linhas
            ],
        }
    )


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


__all__ = ["ATO", "EMITIR", "assinatura_da_proposta", "emitir_ordem"]
