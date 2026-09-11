"""Constitui a faixa calculada como ato imutável, e a continua quando a regra admite (014).

**A sucessão é de geração, e não de faixa** (FR-227). Uma geração é a raiz mais todas as suas
continuações, e o sucessor nasce como raiz nova apontando para a raiz anterior. Suceder a faixa
deixaria a outra metade da geração vigente, autorizando participantes de uma ordem já substituída.

Tudo o que é autoridade, idempotência e trilha vem de onde já vinha: o mesmo `comando_de_comissao`
que `emitir_ordem` percorre, e a mesma permissão. Uma capacidade nova aqui inventaria autoridade que
nenhum Edital distingue.
"""

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.classificacao.application.corte import calcular_corte, geracao_vigente
from processo_seletivo.classificacao.domain import faixa
from processo_seletivo.classificacao.models import Corte, ItemDoCorte
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256

EMITIR = "CORTE_EMITIR"
ATO = "classificacao:emitir"
CONTINUAR = "CORTE_CONTINUAR"


def assinatura_da_proposta(proposta, *, geracao=()):
    """Identidade do que foi conferido, vinculada à geração vista naquela leitura."""
    return canonical_sha256(
        {
            "geracao": [str(item.id) for item in geracao],
            "universo": proposta["universo"],
            "faixa": [
                {
                    "inscricaoId": item["inscricao_id"],
                    "posicao": item["posicao"],
                    "consequencia": item["consequencia"],
                    "excedente": item["excedente_por_empate"],
                }
                for item in proposta["itens"]
            ],
        }
    )


def emitir_corte(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    idempotency_key,
    correlation_id,
    confirmacao_do_calculo,
    lista_id=None,
    motivo="",
):
    """Emite a faixa confirmada; havendo geração vigente, cria a sucessora sem tocar nela."""
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else "",
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
        if ctx.repetido:
            return ctx.desfecho_anterior
        edital = _edital_do_processo(ctx.processo, edital_id)
        vigente = geracao_vigente(
            edital=edital,
            perfil_id=identificador(perfil_id),
            marco_id=identificador(marco_id),
            lista_id=identificador(lista_id) if lista_id else None,
        )
        proposta = _calcular(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id, at=ctx.now
        )
        _conferir(proposta, confirmacao_do_calculo, geracao=vigente, ja_existe=bool(vigente))
        texto_do_motivo = (motivo or "").strip()
        if vigente and not texto_do_motivo:
            raise DomainError(
                "sucessao_sem_motivo",
                "Declare o motivo da sucessão da geração vigente.",
                422,
                campo="motivo",
            )
        corte = _gravar(
            proposta,
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            actor=actor,
            now=ctx.now,
            # **Raiz a raiz**: o sucessor substitui a geração inteira. Apontá-lo para uma
            # continuação deixaria a raiz anterior vigente, autorizando participantes de uma ordem
            # já substituída (FR-227).
            corte_anterior=vigente[0] if vigente else None,
            motivo=texto_do_motivo,
        )
        return _concluir(ctx, corte, proposta, actor, correlation_id, idempotency_key, EMITIR)


def continuar_corte(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    idempotency_key,
    correlation_id,
    quantidade,
    motivo,
    lista_id=None,
):
    """Emite a faixa seguinte da mesma geração, onde a regra publicada a admite (FR-202, FR-226)."""
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else "",
        "quantidade": int(quantidade or 0),
        "motivo": (motivo or "").strip(),
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        edital = _edital_do_processo(ctx.processo, edital_id)
        texto_do_motivo = (motivo or "").strip()
        if not texto_do_motivo:
            raise DomainError(
                "continuacao_sem_motivo",
                "Declare por que a faixa seguinte é necessária: o sistema não o sabe.",
                422,
                campo="motivo",
            )
        vigente = geracao_vigente(
            edital=edital,
            perfil_id=identificador(perfil_id),
            marco_id=identificador(marco_id),
            lista_id=identificador(lista_id) if lista_id else None,
        )
        if not vigente:
            raise DomainError(
                "sem_faixa_anterior",
                "Não há geração vigente neste recorte: emita o corte antes de continuá-lo.",
                409,
            )
        anterior = vigente[-1]
        if anterior.continuacoes.exists():
            raise DomainError(
                "continuacao_ja_emitida",
                "Esta faixa já tem continuação.",
                409,
            )
        proposta = _calcular(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            at=ctx.now,
            desde=anterior.ultima_posicao or 0,
            faixa_anterior=anterior,
        )
        if not faixa.admite_continuacao(proposta["regra"]):
            raise DomainError(
                "continuacao_nao_publicada",
                "Este Edital não publicou que admite continuação além da faixa: a faixa é o que "
                "ele publicou.",
                422,
            )
        # **A ordem citada pela faixa anterior precisa ser a vigente** (FR-205). A geração sucedida
        # já é impossível por construção — `geracao_vigente` só devolve a que ninguém sucedeu.
        if str(anterior.ato_id) != str(proposta["ato"].id):
            raise DomainError(
                "continuacao_sobre_ordem_sucedida",
                "A ordem mudou desde a faixa anterior: emita a geração nova sobre a ordem nova.",
                409,
            )
        corte = _gravar(
            proposta,
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            actor=actor,
            now=ctx.now,
            raiz=anterior.raiz or anterior,
            faixa_anterior=anterior,
            motivo=texto_do_motivo,
            limite=int(quantidade or 0),
        )
        return _concluir(ctx, corte, proposta, actor, correlation_id, idempotency_key, CONTINUAR)


def _calcular(**kwargs):
    return calcular_corte(**kwargs)


def _conferir(proposta, confirmacao, *, geracao, ja_existe):
    esperada = assinatura_da_proposta(proposta, geracao=geracao)
    if not (confirmacao or "").strip():
        raise DomainError(
            "confirmacao_do_corte_exigida",
            "Confira a faixa calculada antes de emitir.",
            422,
            campo="confirmacao_do_calculo",
        )
    if confirmacao != esperada:
        raise DomainError(
            "corte_ja_emitido" if ja_existe else "calculo_divergente",
            (
                "Outro corte foi emitido depois da sua leitura; confira a faixa atual antes de "
                "tentar de novo."
                if ja_existe
                else "A faixa mudou desde a sua leitura; confira o cálculo atual antes de emitir."
            ),
            409 if ja_existe else 422,
            campo="confirmacao_do_calculo",
        )


def _gravar(
    proposta,
    *,
    edital,
    perfil_id,
    marco_id,
    lista_id,
    actor,
    now,
    motivo,
    corte_anterior=None,
    raiz=None,
    faixa_anterior=None,
    limite=None,
):
    itens = proposta["itens"]
    if limite is not None:
        itens = _limitar(itens, limite)
    corte = Corte.objects.create(
        edital=edital,
        perfil_id=identificador(perfil_id),
        marco_id=identificador(marco_id),
        lista_id=identificador(lista_id) if lista_id else None,
        ato=proposta["ato"],
        versao=proposta["versao"],
        etapa_governada_id=faixa.etapa_governada(proposta["regra"]),
        raiz=raiz,
        corte_anterior=corte_anterior,
        faixa_anterior=faixa_anterior,
        motivo=motivo,
        universo=proposta["universo"],
        primeira_posicao=proposta["primeira_posicao"],
        ultima_posicao=_ultima(itens) or proposta["ultima_posicao"],
        emitido_por=actor.subject,
        emitido_em=now,
    )
    ItemDoCorte.objects.bulk_create(
        [
            ItemDoCorte(
                corte=corte,
                inscricao_id=item["inscricao_id"],
                posicao=item["posicao"],
                consequencia=item["consequencia"],
                motivo=item["motivo"],
                excedente_por_empate=item["excedente_por_empate"],
            )
            for item in itens
        ]
    )
    return corte


def _limitar(itens, limite):
    """A continuação alcança **quantos quem emite declarou** — nunca mais do que isso (FR-203).

    A quantidade é pedida e conferida, e não inferida: o sistema não sabe quantas vagas foram
    ocupadas, e decidir sozinho quantos chamar é exatamente o que a `FR-206` proíbe.
    """
    restantes = limite
    ajustados = []
    for item in itens:
        if item["consequencia"] == ItemDoCorte.Consequencia.PROGREDIU and restantes <= 0:
            item = {**item, "consequencia": ItemDoCorte.Consequencia.FORA_DA_FAIXA}
            item["motivo"] = f"além dos {limite} que esta faixa alcançou"
        elif item["consequencia"] == ItemDoCorte.Consequencia.PROGREDIU:
            restantes -= 1
        ajustados.append(item)
    return ajustados


def _ultima(itens):
    posicoes = [
        item["posicao"]
        for item in itens
        if item["consequencia"] == ItemDoCorte.Consequencia.PROGREDIU and item["posicao"]
    ]
    return max(posicoes) if posicoes else None


def _concluir(ctx, corte, proposta, actor, correlation_id, idempotency_key, operacao):
    progrediram = sum(
        1 for item in corte.itens.all() if item.consequencia == ItemDoCorte.Consequencia.PROGREDIU
    )
    auditar(
        actor=actor,
        permissao=ctx.base.permissao,
        operation=operacao,
        aggregate=corte,
        now=ctx.now,
        correlation_id=correlation_id,
        reason=(
            corte.motivo or f"Corte do marco {corte.marco_id} emitido com alvo {proposta['alvo']}."
        ),
        idempotency_key=idempotency_key,
    )
    declarado = {
        "id": str(corte.id),
        "alvo": proposta["alvo"],
        "excedente": proposta["excedente"],
        "progrediram": progrediram,
        "primeiraPosicao": corte.primeira_posicao,
        "ultimaPosicao": corte.ultima_posicao,
        "universo": corte.universo,
    }
    ctx.concluir_sem_resultado(201, declarado)
    return declarado


def _edital_do_processo(processo, edital_id):
    try:
        return Edital.objects.get(processo=processo, id=identificador(edital_id))
    except Edital.DoesNotExist as erro:
        raise DomainError("edital_nao_encontrado", "Edital não encontrado.", 404) from erro


__all__ = ["assinatura_da_proposta", "continuar_corte", "emitir_corte"]
