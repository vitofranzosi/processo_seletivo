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
    lista_id=None,
    motivo="",
    decisoes=(),
):
    """Emite a proposta confirmada de **um recorte**; havendo vigente, cria sucessor sem alterá-lo.

    **Uma ordem por recorte** (034, `FR-490`): a da ampla concorrência e a de cada Modalidade
    reservada, cada uma com raiz, sucessão e proveniência próprias. É o mesmo desenho que a `021`
    aplica ao sorteio desde que três listas de concorrência podem produzir três atos raiz no mesmo
    marco — e não um mecanismo novo.

    **Emitir num recorte não constitui ato sobre os outros** (`FR-494`). As três ordens de um marco
    nascem do mesmo cálculo e da mesma versão normativa, e é natural tratá-las como uma coisa só —
    tratá-las assim faria uma sucessão num recorte revogar em silêncio duas ordens que ninguém
    decidiu revogar. A obsolescência é por cadeia, e a cadeia é do recorte: quem garante isso é o
    `lista_id` do filtro do vigente, logo abaixo, e as duas `UniqueConstraint` parciais do modelo.

    `lista_id` nulo é a ampla concorrência, e é o que todo ato emitido antes desta feature é.
    """
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        # **O recorte entra no payload da idempotência** (`FR-494`). Sem ele, emitir a ordem de
        # PPI com a chave que emitiu a da ampla seria lido como repetição, e a segunda emissão
        # devolveria o desfecho da primeira — um recorte ficaria sem ato, e ninguém saberia por quê.
        "lista": str(lista_id) if lista_id else "",
        "confirmacao": confirmacao_do_calculo or "",
        "motivo": (motivo or "").strip(),
        "decisoes": sorted(str(item) for item in decisoes or ()),
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
        # **O cálculo vem antes da busca do vigente, e a ordem passou a importar** (034, `FR-491`).
        # O vigente é o **daquele recorte**, e quem diz qual recorte é — depois de reduzir ao nulo a
        # Modalidade que o Perfil aponta como sendo a ampla, e de recusar o identificador que não
        # corresponde a Modalidade alguma — é o próprio cálculo. Resolver o recorte aqui também
        # criaria um segundo lugar que responde "quais são os recortes deste marco", que é
        # exatamente o defeito que a derivação única existe para fechar.
        proposta = calcular_ordem(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            at=ctx.now,
        )
        _recusar_marco_de_sorteio(proposta)
        recorte = proposta["lista_id"]
        vigente = AtoDeOrdenacao.objects.filter(
            edital=edital,
            perfil_id=identificador(perfil_id),
            marco_id=identificador(marco_id),
            # **A lista entra aqui pelo mesmo motivo que entrou em `ato_vigente`** (`021`, `D-006`):
            # um marco de cotas tem uma raiz por lista de concorrência, e perguntar pelo vigente sem
            # dizer de qual delas devolveria uma das três pela ordem de emissão.
            #
            # *Aqui havia `lista_id=None` fixo, com o comentário "um ato computado é sempre o de
            # ampla concorrência — só o sorteio emite por lista". Era decisão de escopo tomada
            # entre a `015` e a `021`, e a `034` é a feature que a revisita: o computado passa a
            # emitir por recorte também. O comentário sai junto da decisão que ele explicava —
            # comentário que sobrevive à decisão passa a mentir.*
            lista_id=recorte,
            sucessores__isnull=True,
        ).first()
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
            lista_id=recorte,
            versao=proposta["versao"],
            ato_anterior=vigente,
            motivo_da_sucessao=texto_do_motivo,
            universo=proposta["universo"],
            emitido_por=actor.subject,
            emitido_em=ctx.now,
        )
        _citar(ato, proposta["marco"], decisoes)
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
                or (
                    f"Ordem do marco {proposta['marco'].get('name') or marco_id} emitida"
                    + (f", no recorte {recorte}." if recorte else ", na ampla concorrência.")
                )
            ),
            idempotency_key=idempotency_key,
        )
        declarado = resultado_declarado([ato], [], "emitida")
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


def assinatura_da_proposta(proposta, *, ato_vigente=None):
    """Identidade do que foi conferido, vinculada ao recorte e ao vigente daquela leitura.

    **A confirmação é do recorte** (034, `FR-495`). Uma assinatura comum aceitaria, no recorte B, a
    conferência lida no A — e o operador emitiria a ordem certa com a conferência errada, sem que
    nada acusasse. O caso não é hipotético: dois recortes reservados **sem nenhum autodeclarado** no
    mesmo marco produzem universo e ordem idênticos, e só o recorte os distingue.

    O recorte entra **aqui**, e não no resumo do universo que o ato grava: lá ele faria a comparação
    de obsolescência confrontar um universo gravado sem a chave com um calculado com ela, e o acervo
    inteiro apareceria obsoleto de uma vez. A assinatura é efêmera — nasce no GET, morre no POST —,
    e por isso mudar a forma dela não alcança ato nenhum já emitido.
    """
    linhas = proposta["posicoes"] + proposta["sem_posicao"]
    return canonical_sha256(
        {
            "atoVigente": str(ato_vigente.id) if ato_vigente is not None else None,
            "recorte": proposta.get("lista_id"),
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


def _recusar_marco_de_sorteio(proposta):
    """A ordem de um marco de sorteio não se emite por cálculo (`021`, `D-006`, `FR-069`).

    **A recusa é aqui porque o dano é irreversível.** O ato saía com `origem=COMPUTADO` e
    `lista_id` nulo, que é a raiz da ampla concorrência: dali em diante `constituir_sorteio`
    recusava o certame com `ordering_act_already_exists`, e não havia desfazer — a tabela é
    append-only, e a sucessão de uma ordem sorteada nasce da anulação de um sorteio que, nesse
    caminho, nunca chegou a existir. Fechar só a tela deixaria a porta do comando aberta.

    **Recebe a proposta inteira, e não só o marco** (030, FR-429). O marco pode referenciar o
    método comum do Edital em vez de declarar o próprio, e a resolução precisa do conteúdo inteiro
    para enxergá-lo: lendo só a chave do marco, um marco de sorteio que referencia o comum passaria
    por aqui e a ordem dele seria emitida por cálculo — que é exatamente o dano irreversível que
    esta recusa existe para impedir.
    """
    from processo_seletivo.editais.domain import marcos

    if not marcos.marco_ordena_por_sorteio(
        proposta["versao"].content,
        perfil_id=proposta["perfil"]["id"],
        marco_id=proposta["marco"]["id"],
    ):
        return
    raise DomainError(
        "ordering_milestone_is_drawn",
        "Este marco tem o método de sorteio declarado no Edital: a ordem dele nasce do sorteio "
        "público, e não do cálculo por Etapas. Conduza o sorteio na tela do marco.",
        422,
        campo="marco",
    )


def _citar(ato, marco, decisoes):
    """Grava, na mesma transação do ato, quais decisões de recurso ele executa (T-015, FR-089).

    **Proveniência, e não passo humano separado.** Ela nasce com o ato, pela mão de quem já tem
    autoridade para emiti-lo — do mesmo tipo de `motivo_da_sucessao`, que também não tem autoridade,
    instante nem motivo próprios. Um passo separado seria um passo que se esquece, e o esquecimento
    deixaria a definitiva do marco impedida sem que ninguém soubesse por quê.

    A pertinência é conferida **no banco**, pela trigger `citacao_coerente`: uma gravação ligando
    decisão de um marco a ato de outro liberaria indevidamente a definitiva daquele outro, e a
    verificação que morasse só aqui não alcançaria os demais caminhos de escrita.
    """
    from processo_seletivo.classificacao.models import CitacaoDeDecisao

    for identificador_da_decisao in sorted({str(item) for item in decisoes or ()}):
        CitacaoDeDecisao.objects.create(ato=ato, decisao_id=identificador_da_decisao)


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
