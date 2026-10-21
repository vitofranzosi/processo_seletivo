"""A vaga acrescida depois da publicação: a prévia, o ato e o ato que a desfaz (097).

**A autoridade é a de quem apura, e nenhuma nova** (`D-004`, `T-007`). Os dois atos percorrem o
mesmo `comando_de_comissao` da emissão: transação, Processo travado, gestão da comissão e reserva da
chave. Uma capacidade concedida por papel tiraria o ato da presidência, que apura o próprio certame.

**O ato emite a apuração seguinte, pela mesma conta** (`FR-2454`, `T-004`), e só quando nada além
dele mudou: apuração obsoleta por outra causa é um fato que alguém precisa ver na ocupação, e não
algo que o acréscimo deva varrer para baixo do tapete. A emissão corre num *savepoint*: a recusa
dela não desfaz o acréscimo, que é fato de outro certame e aconteceu.

**Este módulo não conhece a chamada de ninguém** (`UX-034`). A trava do desfazimento precisa saber
quantas pessoas do recorte já foram chamadas, e a pergunta chega como argumento — a seta entre os
dois apps corre da convocação para a ocupação, e não o contrário (`T-005`).
"""

from django.db import transaction

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.classificacao.application.corte import linha_do_quadro
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.classificacao.domain.universo import por_identidade
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.application.emissao import (
    _edital_do_processo,
    emitir_sucessora_por_efeito,
)
from processo_seletivo.ocupacao.domain import acrescimo as conta
from processo_seletivo.ocupacao.domain import apuracao as calculo
from processo_seletivo.ocupacao.domain import nomes, reversao
from processo_seletivo.ocupacao.models import AcrescimoDeVagas
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256

ACRESCENTAR = "OCUPACAO_ACRESCENTAR_VAGAS"
DESFAZER = "OCUPACAO_DESFAZER_ACRESCIMO"
ATO_DE_ACRESCENTAR = "ocupacao:acrescentar_vagas"
ATO_DE_DESFAZER = "ocupacao:desfazer_acrescimo"

RESERVAS = ("LIMITED", "UNLIMITED")


# --- O Perfil aceita? --------------------------------------------------------------------------


def impedimento(conteudo, *, perfil_id, lista_id=None):
    """`(codigo, frase)` quando o Perfil não aceita vaga acrescida, ou `None`.

    **Duas perguntas, nesta ordem** (`FR-2463`, `FR-2464`). Sem cadastro de reserva publicado,
    chamar além das vagas não tem fundamento no Edital (`D-002`). E só a ampla concorrência de
    Perfil cujo quadro tem só a linha geral: com qualquer linha de Modalidade — até com zero —, a
    vaga acrescida na ampla mudaria quem ocupa a reservada pela concorrência concomitante, e
    repartir vaga entre modalidades está fora desta feature (`D-003`, `T-006`).

    A tela a usa para trocar o formulário pela frase, e o ato para recusar: uma resposta só.
    """
    perfil = por_identidade((conteudo or {}).get("profiles"), perfil_id) or {}
    if perfil.get("reserveType") not in RESERVAS:
        return (
            nomes.ACRESCIMO_SEM_CADASTRO_DE_RESERVA,
            "Este Perfil não publicou cadastro de reserva: sem ele, não há norma que autorize "
            "chamar além das vagas publicadas. Para mudar a quantidade, é preciso Retificação do "
            "Perfil.",
        )
    linhas = perfil.get("vacancyTable") or []
    ampla = perfil.get("generalCompetitionModalityId")
    fora = (
        any(linha.get("modalityId") for linha in linhas)
        or reversao.declarada(perfil) is not None
        or (lista_id is not None and str(lista_id) != str(ampla or ""))
    )
    if fora:
        return (
            nomes.ACRESCIMO_FORA_DA_LINHA_GERAL,
            "A vaga acrescida alcança só a ampla concorrência de Perfil cujo quadro tem só a linha "
            "geral. Este Perfil reparte vagas entre modalidades, e essa repartição está fora do "
            "acréscimo.",
        )
    return None


# --- A prévia ----------------------------------------------------------------------------------


def previa_do_acrescimo(*, edital, perfil_id, marco_id, quantidade, lista_id=None, at=None):
    """O que o ato faria agora — **sem gravar nada** (`FR-2456`)."""
    return _previa(
        edital=edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        variacao=_inteiro(quantidade),
        gesto="acrescimo",
        at=at,
    )


def _previa(*, edital, perfil_id, marco_id, lista_id, variacao, gesto, at):
    versao = effective_version(edital_id=edital.id, at=at)
    linha = linha_do_quadro(versao.content, perfil_id=perfil_id, lista_id=lista_id)
    vigente = selectors.apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    causas = selectors.causas_de_obsolescencia(vigente, at=at)
    acrescimos = selectors.acrescimos_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    publicadas = linha.get("immediateVacancies") if linha is not None else None
    acrescidas = conta.saldo((a.especie, a.quantidade) for a in acrescimos)
    # **Sem movimento de vaga, de propósito**: o Perfil que aceita o acréscimo não tem linha de
    # Modalidade nem reversão (`impedimento`), e nada move vaga para a linha geral dele.
    depois = (publicadas or 0) + acrescidas + (variacao or 0)
    ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    ordenadas, _, _ = selectors.progrediram_em_ordem(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    janela = calculo.titulares_iniciais(progrediram_em_ordem=ordenadas, efetivas=max(depois, 0))
    outras = [c for c in causas if c["causa"] != nomes.CAUSA_ACRESCIMO_POSTERIOR]
    return {
        "versao": versao,
        "temQuadro": linha is not None,
        "temOrdem": ato is not None,
        "impedimento": impedimento(versao.content, perfil_id=perfil_id, lista_id=lista_id),
        "apuracao": vigente,
        "acrescimos": selectors.com_o_restante(acrescimos),
        "publicadas": publicadas,
        "acrescidasLiquidas": acrescidas,
        "efetivasDepois": depois,
        "alcancados": _identificadas(janela, ato),
        "faltamPessoas": max(depois - len(janela), 0),
        "emissao": (
            {"codigo": nomes.OUTRA_CAUSA_DE_OBSOLESCENCIA, "causas": outras}
            if vigente is not None and outras
            else None
        ),
        "assinatura": canonical_sha256(
            {
                "gesto": gesto,
                "apuracao": str(vigente.id) if vigente is not None else None,
                "acrescimos": [str(a.id) for a in acrescimos],
                "variacao": variacao,
            }
        ),
    }


def _identificadas(janela, ato):
    """Quem a ordem alcança para as vagas, pelo nome e pela posição na ordem (`UX-221`).

    **Duas consultas, e nenhuma por pessoa** (`SC-924`): os nomes de uma vez, e as posições do ato
    que a leitura da ordem já carregou.
    """
    if not janela:
        return []
    nomes_por_id = dict(Inscricao.objects.filter(id__in=janela).values_list("id", "nome"))
    posicoes = (
        {str(p.inscricao_id): p.posicao for p in ato.posicoes.all()} if ato is not None else {}
    )
    return [
        {
            "id": str(inscricao),
            "nome": nomes_por_id.get(inscricao) or nomes_por_id.get(str(inscricao)) or "",
            "posicao": posicoes.get(str(inscricao)),
        }
        for inscricao in janela
    ]


# --- O ato ------------------------------------------------------------------------------------


def acrescentar_vagas(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    quantidade,
    origem,
    fundamento,
    leitura_confirmada,
    idempotency_key,
    correlation_id,
    lista_id=None,
    referencia="",
):
    """Grava a vaga acrescida e, quando nada além dela mudou, a apuração seguinte."""
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else "",
        "quantidade": str(quantidade),
        "origem": (origem or "").strip(),
        "fundamento": (fundamento or "").strip(),
        "referencia": (referencia or "").strip(),
        "leitura": leitura_confirmada or "",
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO_DE_ACRESCENTAR,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        quantidade = conferir_campos(
            quantidade=quantidade, origem=payload["origem"], fundamento=payload["fundamento"]
        )
        edital = _edital_do_processo(ctx.processo, edital_id)
        perfil, marco = identificador(perfil_id), identificador(marco_id)
        lista = identificador(lista_id) if lista_id else None
        previa = _previa(
            edital=edital,
            perfil_id=perfil,
            marco_id=marco,
            lista_id=lista,
            variacao=quantidade,
            gesto="acrescimo",
            at=ctx.now,
        )
        conferir_recorte(previa)
        _conferir_leitura(previa, leitura_confirmada)
        registro = AcrescimoDeVagas.objects.create(
            edital=edital,
            perfil_id=perfil,
            marco_id=marco,
            lista_id=lista,
            especie=nomes.ACRESCIMO,
            quantidade=quantidade,
            origem=payload["origem"],
            fundamento=payload["fundamento"],
            referencia=payload["referencia"],
            versao=previa["versao"],
            registrado_por=str(getattr(actor, "subject", actor)),
            registrado_em=ctx.now,
        )
        seguinte = _emitir_seguinte(
            ctx,
            actor,
            registro,
            motivo=f"Vaga acrescida depois da publicação: {quantidade}, de {payload['origem']}.",
            correlation_id=correlation_id,
        )
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=ACRESCENTAR,
            aggregate=registro,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=_razao(registro, previa["apuracao"], seguinte),
            idempotency_key=idempotency_key,
        )
        declarado = _declarado(registro, seguinte)
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


def conferir_campos(*, quantidade, origem, fundamento):
    """A quantidade como inteiro, ou a recusa do campo que falta (`FR-2450`, `FR-2451`).

    Pública porque a tela a chama antes de abrir a conferência: conferir uma vaga sem origem é
    mostrar uma prévia que o ato recusaria.
    """
    quantidade = _quantidade_do_ato(quantidade)
    if not (origem or "").strip():
        raise DomainError(
            nomes.ORIGEM_OBRIGATORIA,
            "Diga de onde a vaga veio: o número do Edital e o campus.",
            422,
            campo="origem",
        )
    if not (fundamento or "").strip():
        raise DomainError(
            nomes.FUNDAMENTO_OBRIGATORIO,
            "Diga por que a vaga existe.",
            422,
            campo="fundamento",
        )
    return quantidade


def _quantidade_do_ato(valor):
    quantidade = _inteiro(valor)
    if quantidade is None or quantidade < 1:
        raise DomainError(
            nomes.QUANTIDADE_INVALIDA,
            "A quantidade é um número inteiro de vagas, a partir de 1.",
            422,
            campo="quantidade",
        )
    return quantidade


def _inteiro(valor):
    if isinstance(valor, bool):
        return None
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return None


def conferir_recorte(previa):
    """As recusas do recorte, na ordem do contrato: a mais específica primeiro.

    Pública pela razão de `conferir_campos`: a conferência não abre sobre recorte que o ato recusa.
    """
    if previa["impedimento"]:
        codigo, frase = previa["impedimento"]
        raise DomainError(codigo, frase, 409)
    if not previa["temOrdem"]:
        raise DomainError(
            nomes.ORDEM_NAO_VIGENTE,
            "Este recorte não tem ordem vigente: não há a quem a vaga acrescida alcançar.",
            409,
        )
    if not previa["temQuadro"]:
        raise DomainError(
            nomes.SEM_QUADRO_PUBLICADO,
            "Este Edital não publicou quadro de vagas para este recorte. A quantidade é declarada "
            "por Retificação do Perfil, acrescentando a linha deste recorte ao quadro de vagas.",
            409,
        )


def _conferir_leitura(previa, leitura_confirmada):
    if (leitura_confirmada or "") != previa["assinatura"]:
        raise DomainError(
            nomes.LEITURA_DO_RECORTE_MUDOU,
            "As vagas deste recorte mudaram desde que a conferência foi aberta: confira de novo "
            "antes de confirmar.",
            409,
        )


def _emitir_seguinte(ctx, actor, registro, *, motivo, correlation_id):
    """A apuração seguinte, ou o que a impede — `{apuracaoSeguinte, apuracaoPendente}` (`T-004`)."""
    vigente = selectors.apuracao_vigente(
        edital=registro.edital,
        perfil_id=registro.perfil_id,
        marco_id=registro.marco_id,
        lista_id=registro.lista_id,
    )
    causas = {c["causa"] for c in selectors.causas_de_obsolescencia(vigente, at=ctx.now)}
    if vigente is not None and causas - {nomes.CAUSA_ACRESCIMO_POSTERIOR}:
        return _pendente(
            nomes.OUTRA_CAUSA_DE_OBSOLESCENCIA,
            "A apuração deste recorte já estava obsoleta por outra causa: emita a seguinte na "
            "ocupação, onde a causa é dita.",
        )
    try:
        with transaction.atomic():
            declarado = emitir_sucessora_por_efeito(
                actor=actor,
                permissao=ctx.base.permissao,
                edital=registro.edital,
                perfil_id=registro.perfil_id,
                marco_id=registro.marco_id,
                lista_id=registro.lista_id,
                motivo=motivo,
                now=ctx.now,
                correlation_id=correlation_id,
            )
    except DomainError as recusa:
        return _pendente(recusa.code, recusa.detail)
    if declarado is None:
        # A linha geral não cede vaga pela reversão, e o Perfil que aceita o acréscimo não a
        # declara: este ramo é guarda, e não caminho vivo (`T-004`).
        return _pendente(nomes.OUTRA_CAUSA_DE_OBSOLESCENCIA, "A apuração seguinte moveria vaga.")
    return {"apuracaoSeguinte": declarado, "apuracaoPendente": None}


# --- O desfazimento (US3) -----------------------------------------------------------------------


def previa_do_desfazimento(*, edital, acrescimo_id, quantidade, pessoas_chamadas, at=None):
    """O que o desfazimento faria agora, e a recusa que ele daria — sem gravar nada (`FR-2460`).

    `pessoas_chamadas` é a pergunta que só a convocação responde (`T-005`): quantas pessoas do
    recorte têm chamada em aberto ou atendida. A tela a passa, e a prévia diz antes do clique se o
    ato seria recusado.
    """
    registro = _acrescimo_do_edital(edital, acrescimo_id)
    variacao = _inteiro(quantidade)
    previa = _previa(
        edital=edital,
        perfil_id=registro.perfil_id,
        marco_id=registro.marco_id,
        lista_id=registro.lista_id,
        variacao=-(variacao or 0),
        gesto="desfazimento",
        at=at,
    )
    restante = next(
        (item["restante"] for item in previa["acrescimos"] if item["registro"].id == registro.id),
        0,
    )
    chamadas = pessoas_chamadas(
        edital=edital,
        perfil_id=registro.perfil_id,
        marco_id=registro.marco_id,
        lista_id=registro.lista_id,
        at=at,
    )
    efetivas = (previa["publicadas"] or 0) + previa["acrescidasLiquidas"]
    if variacao is not None and variacao > restante:
        recusa = nomes.DESFAZIMENTO_ALEM_DO_ACRESCIMO
    elif variacao is not None:
        recusa = conta.recusa_do_desfazimento(
            efetivas=efetivas, quantidade=variacao, chamadas=chamadas
        )
    else:
        recusa = nomes.QUANTIDADE_INVALIDA
    return {
        **previa,
        "acrescimo": registro,
        "restante": restante,
        "chamadas": chamadas,
        "recusa": recusa,
    }


def desfazer_acrescimo(
    *,
    actor,
    processo_id,
    edital_id,
    acrescimo_id,
    quantidade,
    motivo,
    pessoas_chamadas,
    leitura_confirmada,
    idempotency_key,
    correlation_id,
):
    """Grava o desfazimento, citando o acréscimo, e a apuração seguinte quando nada além mudou."""
    payload = {
        "edital": str(edital_id),
        "acrescimo": str(acrescimo_id),
        "quantidade": str(quantidade),
        "motivo": (motivo or "").strip(),
        "leitura": leitura_confirmada or "",
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO_DE_DESFAZER,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        quantidade = _quantidade_do_ato(quantidade)
        if not payload["motivo"]:
            raise DomainError(
                nomes.MOTIVO_OBRIGATORIO,
                "Diga por que a vaga acrescida está sendo desfeita.",
                422,
                campo="motivo",
            )
        edital = _edital_do_processo(ctx.processo, edital_id)
        # **A trava é avaliada aqui, sob o lock do Processo**, e não na tela: calculada antes, ela
        # seria um número velho no instante do ato (`T-005`, Princípio IV).
        previa = previa_do_desfazimento(
            edital=edital,
            acrescimo_id=acrescimo_id,
            quantidade=quantidade,
            pessoas_chamadas=pessoas_chamadas,
            at=ctx.now,
        )
        conferir_desfazimento(previa)
        _conferir_leitura(previa, leitura_confirmada)
        acrescimo = previa["acrescimo"]
        registro = AcrescimoDeVagas.objects.create(
            edital=edital,
            perfil_id=acrescimo.perfil_id,
            marco_id=acrescimo.marco_id,
            lista_id=acrescimo.lista_id,
            especie=nomes.DESFAZIMENTO,
            quantidade=quantidade,
            fundamento=payload["motivo"],
            desfaz=acrescimo,
            versao=previa["versao"],
            registrado_por=str(getattr(actor, "subject", actor)),
            registrado_em=ctx.now,
        )
        seguinte = _emitir_seguinte(
            ctx,
            actor,
            registro,
            motivo=f"Vaga acrescida desfeita: {quantidade}. Motivo: {payload['motivo']}",
            correlation_id=correlation_id,
        )
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=DESFAZER,
            aggregate=registro,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=_razao(registro, previa["apuracao"], seguinte),
            idempotency_key=idempotency_key,
        )
        declarado = _declarado(registro, seguinte)
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


def conferir_desfazimento(previa):
    """As recusas do desfazimento, ditas antes do clique e repetidas sob a trava (`FR-2462`)."""
    if previa["recusa"] == nomes.QUANTIDADE_INVALIDA:
        _quantidade_do_ato(None)
    if previa["recusa"] == nomes.DESFAZIMENTO_ALEM_DO_ACRESCIMO:
        raise DomainError(
            nomes.DESFAZIMENTO_ALEM_DO_ACRESCIMO,
            f"Este acréscimo tem só {previa['restante']} vaga(s) a desfazer.",
            409,
            campo="quantidade",
        )
    if previa["recusa"] == nomes.DESFAZIMENTO_COM_PESSOAS_CHAMADAS:
        raise DomainError(
            nomes.DESFAZIMENTO_COM_PESSOAS_CHAMADAS,
            f"Há {previa['chamadas']} pessoa(s) já chamada(s) para as vagas deste recorte, e o "
            "desfazimento as deixaria sem vaga. Registre antes o desfecho de quem não vai "
            "ocupá-la.",
            409,
        )


def _acrescimo_do_edital(edital, acrescimo_id):
    registro = (
        AcrescimoDeVagas.objects.filter(
            edital=edital, id=identificador(acrescimo_id), especie=nomes.ACRESCIMO
        ).first()
        if acrescimo_id
        else None
    )
    if registro is None:
        raise DomainError(
            nomes.ACRESCIMO_INEXISTENTE, "Não há esta vaga acrescida neste Edital.", 404
        )
    return registro


def _pendente(codigo, detalhe):
    return {"apuracaoSeguinte": None, "apuracaoPendente": {"codigo": codigo, "detalhe": detalhe}}


def _razao(registro, anterior, seguinte):
    """O que a trilha guarda para reconstruir o número sem abrir o banco (`FR-2466`)."""
    emitida = seguinte["apuracaoSeguinte"]
    return (
        f"{registro.get_especie_display()} de {registro.quantidade} vaga(s) no marco "
        f"{registro.marco_id}, Perfil {registro.perfil_id}, "
        f"lista {registro.lista_id or 'ampla concorrência'}. "
        + (f"Origem: {registro.origem}. " if registro.origem else "")
        + f"Fundamento: {registro.fundamento}. "
        + f"Apuração anterior: {anterior.id if anterior is not None else 'nenhuma'}; "
        + (
            f"seguinte: {emitida['id']}."
            if emitida
            else f"seguinte pendente: {seguinte['apuracaoPendente']['codigo']}."
        )
    )


def _declarado(registro, seguinte):
    return {
        "acrescimo": str(registro.id),
        "especie": registro.especie,
        "quantidade": registro.quantidade,
        **seguinte,
    }


__all__ = [
    "ACRESCENTAR",
    "DESFAZER",
    "acrescentar_vagas",
    "conferir_campos",
    "conferir_desfazimento",
    "conferir_recorte",
    "desfazer_acrescimo",
    "impedimento",
    "previa_do_acrescimo",
    "previa_do_desfazimento",
]
