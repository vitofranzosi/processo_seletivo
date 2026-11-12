"""A destinação da vaga reservada sem quem a ocupe: a leitura, a prévia e o ato (155, US1, R-001).

**A destinação é ato próprio, e não efeito da apuração** (155, D-001, D-005, FR-6308). A apuração
informa a ocupação; quem move a vaga é a presidência, depois de ver origem, destino, quantidade e a
frase que o Edital publicou. O ato grava o mesmo `MovimentoDeVaga` que a apuração gravava — a conta
da ocupação já o sabe ler, e o movimento antigo e o novo contam igual (FR-6316).

**A autoridade é a de quem apura, e nenhuma nova** (FR-6341): o mesmo `comando_de_comissao` da
emissão — transação, Processo travado, gestão da comissão e reserva da chave. É a trava do Processo
que faz duas confirmações simultâneas darem um registro só (FR-6314): a segunda lê, sob a trava, o
movimento da primeira e a sucessora que ela emitiu, e o saldo é zero.

**Este módulo não conhece a condução** (FR-6344, `UX-034` da `016`). O que só a divulgação, os
recursos e a condução respondem — o resultado é definitivo? corre prazo? alguém foi chamado para a
vaga e ainda não respondeu? — chega por `fatos_externos`, um *callable* que a interface compõe, como
`pessoas_chamadas` no acréscimo (155, R-004). O ato o chama **sob a trava**: calculado na tela,
seria um fato velho no instante do ato.

**Só o esgotamento** (155, R-010). Sob a reversão por saldo, o ato recusa com
`reversao_por_saldo_aguarda_decisao`, e a emissão continua movendo vaga como antes: é a parada da
parte que a decisão do usuário governa, e não regra adotada.
"""

from django.db import transaction

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.classificacao.application.corte import admite_continuacao, regra_do_marco
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.classificacao.domain.universo import por_identidade
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.ocupacao.application import efeitos as efeitos_de_ocupacao
from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.application.emissao import (
    _edital_do_processo,
    emitir_sucessora_por_efeito,
)
from processo_seletivo.ocupacao.domain import apuracao as calculo
from processo_seletivo.ocupacao.domain import destinacao as conta
from processo_seletivo.ocupacao.domain import nomes, reversao
from processo_seletivo.ocupacao.models import MovimentoDeVaga
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256

DESTINAR = "OCUPACAO_DESTINAR_VAGA"
ATO_DE_DESTINAR = "ocupacao:destinar_vaga"


# --- A leitura ---------------------------------------------------------------------------------


def frase_publicada(versao, declaracao):
    """A frase da reversão como a versão a publicou, na redação do documento dela (FR-6309).

    **A redação é a da Publicação que a versão cita**, e não a de hoje: um Edital publicado antes da
    `069` publicou a redação 1, e citar a 2 no fundamento do ato seria citar texto que ele não tem.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import frase_da_reversao

    if not declaracao:
        return ""
    origem = getattr(versao, "source_publication", None)
    redacao = getattr(origem, "redacao_do_documento", None)
    return (
        frase_da_reversao(declaracao, redacao=redacao) if redacao else frase_da_reversao(declaracao)
    )


def leitura_da_vaga(*, edital, perfil_id, marco_id, lista_id, fatos_externos=None, at=None):
    """A situação da vaga do recorte, com tudo o que a conferência e o ato leem (155, R-004).

    `fatos_externos(edital=, perfil_id=, marco_id=, lista_id=, etapa_governada_id=, eliminados=,
    at=)` devolve o dicionário dos fatos que só outros módulos respondem (ver
    `domain.destinacao.impedimentos`), e mais `chamados` — as inscrições chamadas para a vaga e sem
    desfecho. `None` é ninguém para perguntar: a prévia da classificação e a equivalência dela leem
    só a condição (`quantidadePelaCondicao`), que não depende deles.
    """
    versao = effective_version(edital_id=edital.id, at=at)
    perfil = por_identidade((versao.content or {}).get("profiles"), perfil_id) or {}
    declaracao = reversao.declarada(perfil)
    vigente = selectors.apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    movimentos = selectors._movimentos_que_alcancam(
        edital=edital, perfil=perfil_id, marco=marco_id, lista=lista_id
    )
    base = {
        "versao": versao,
        "declaracao": declaracao,
        "frase": frase_publicada(versao, declaracao),
        "apuracao": vigente,
        "movimentos": movimentos,
        "destinadas": _destinadas(movimentos, lista_id),
    }
    if vigente is None or lista_id is None:
        # Sem apuração não há saldo afirmado; a linha geral não é origem de destinação — a vaga
        # dela é a da declaração de não preenchida, no incremento seguinte (155, D-014).
        situacao = conta.situacao(
            declaracao=declaracao,
            lista_id=lista_id,
            saldo=None if vigente is None else 0,
            destinadas=base["destinadas"],
        )
        return {**base, "situacao": situacao, "quantidadePelaCondicao": 0, "restantes": []}

    causas = selectors.causas_de_obsolescencia(vigente, at=at)
    saldo = calculo.faltando(
        efetivas=vigente.efetivas,
        ocupadas=vigente.ocupadas,
        nao_preenchidas=vigente.nao_preenchidas,
    )
    fatos = _condicao(
        edital=edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        versao=versao,
        efetivas=vigente.efetivas,
    )
    externos = (
        fatos_externos(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            etapa_governada_id=fatos["etapaGovernada"],
            eliminados=fatos["eliminados"],
            at=at,
        )
        if fatos_externos is not None
        else {}
    )
    # **Os inabilitados só saem da conta com o prazo e os recursos da eliminação fechados** (155,
    # D-007): enquanto o recurso pode devolvê-los à lista, a vaga não é "sem quem a ocupe", e o
    # impedimento diz até quando.
    inabilitados = (
        set()
        if externos.get("prazo_da_eliminacao_ate") or externos.get("recursos_da_eliminacao")
        else fatos["eliminados"]
    )
    restantes = conta.quem_ainda_pode_ocupar(
        posicoes=fatos["posicoes"],
        excluidos=fatos["excluidos"],
        ocupam_a_ampla_confirmados=fatos["confirmadosNaAmpla"],
        alcancaveis=fatos["alcancaveis"],
        inabilitados=inabilitados,
        ocupantes=fatos["ocupantes"],
    )
    pela_condicao = conta.quem_ainda_pode_ocupar(
        posicoes=fatos["posicoes"],
        excluidos=fatos["excluidos"],
        ocupam_a_ampla_confirmados=fatos["confirmadosNaAmpla"],
        alcancaveis=fatos["alcancaveis"],
        inabilitados=fatos["eliminados"],
        ocupantes=fatos["ocupantes"],
    )
    chamados = {conta.chave(i) for i in externos.get("chamados") or ()}
    sem_confirmacao = fatos["semConfirmacaoNaAmpla"]
    # O eliminado com recurso possível é pendente, e não livre: a vaga não é dele agora, e o caminho
    # não é chamá-lo — é esperar o prazo ou a decisão que o impedimento nomeia (US3.5).
    em_recurso = fatos["eliminados"] - inabilitados
    impedimentos = conta.impedimentos(
        {
            **externos,
            "ocupam_a_ampla_sem_confirmacao": len(sem_confirmacao),
            "apuracao_obsoleta": bool(causas),
        }
    )
    situacao = conta.situacao(
        declaracao=declaracao,
        lista_id=lista_id,
        saldo=saldo,
        restantes=restantes,
        pendentes=chamados | sem_confirmacao | em_recurso,
        impedimentos=impedimentos,
        destinadas=base["destinadas"],
    )
    return {
        **base,
        "causas": causas,
        "saldo": saldo,
        "situacao": situacao,
        "restantes": restantes,
        # **A condição sozinha, sem os impedimentos** (155, R-011): é o que a prévia da
        # classificação e a do sorteio fazem sobre a ordem fictícia, onde não há desfecho, recurso
        # nem chamada a simular; a equivalência delas com o caminho oficial lê este número.
        "quantidadePelaCondicao": conta.quantidade_destinavel(
            gatilho=reversao.especie_que_move(perfil),
            saldo=saldo,
            ainda_podem_ocupar=len(pela_condicao),
        ),
    }


def _condicao(*, edital, perfil_id, marco_id, lista_id, versao, efetivas):
    """Os fatos da ocupação que a condição da FR-6304 lê, consultados uma vez por recorte."""
    ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    posicoes = [(p.inscricao_id, p.posicao) for p in ato.posicoes.all()] if ato else []
    membros = {conta.chave(i) for i, _ in posicoes}
    progrediram, corte, empates = selectors.progrediram_em_ordem(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    habilitadas = selectors.habilitadas_pelo_corte(
        edital=edital, corte=corte, progrediram=progrediram
    )
    efeitos = efeitos_de_ocupacao.efeitos_lidos_por(
        efeitos_de_ocupacao.efeitos_do_recorte(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
        )
    )
    da_ampla = efeitos_de_ocupacao.efeitos_lidos_por(
        efeitos_de_ocupacao.efeitos_do_recorte(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=None
        )
    )
    try:
        ocupantes_da_ampla = {
            conta.chave(i)
            for i in selectors.ocupantes_da_ampla(
                edital=edital, perfil_id=perfil_id, marco_id=marco_id, versao=versao
            )
        }
    except calculo.EmpateNaFronteiraDoAlvo:
        # A ampla não apura com o empate não julgado, e a reserva também não: a vigente dela está
        # obsoleta, e a causa impede o ato. Ninguém conta como ocupante da ampla, e a conta segue.
        ocupantes_da_ampla = set()
    confirmados = conta.incluidos_por_efeito(da_ampla) & membros
    # **Os ocupantes da reserva, pela conta da apuração** (`apuracao.titulares_iniciais` e
    # `ocupantes`), sobre as efetivas que a vigente gravou: a pergunta é se há alguém para a vaga
    # que **sobra**, e quem já ocupa outra não responde por ela.
    try:
        titulares = calculo.titulares_iniciais(
            progrediram_em_ordem=progrediram,
            efetivas=efetivas,
            ocupantes_da_ampla=ocupantes_da_ampla,
            empates_residuais=empates,
            habilitadas=habilitadas,
        )
    except calculo.EmpateNaFronteiraDoAlvo:
        # A apuração vigente não seria emitida hoje: ela está obsoleta, e a causa impede o ato.
        titulares = []
    ocupantes = calculo.ocupantes(
        titulares=titulares, habilitadas=habilitadas, efeitos_lidos=efeitos
    )
    regra = regra_do_marco(versao.content, perfil_id=perfil_id, marco_id=marco_id)
    # **Alcançável é quem a faixa alcançou, ou a ordem inteira** quando o Edital admite continuação
    # (FR-6304) — e mais quem entrou por efeito: a pessoa chamada além da faixa foi alcançada.
    alcancaveis = (
        None
        if admite_continuacao(regra)
        else {conta.chave(i) for i in progrediram} | conta.incluidos_por_efeito(efeitos)
    )
    etapa = corte.etapa_governada_id if corte is not None else None
    # **`vigentes`, e não `objects`** — a varredura `test_vigencia_do_resultado.py` o cobra: o
    # Resultado superado por recurso deferido não elimina mais ninguém.
    eliminados = (
        {
            conta.chave(r.inscricao_id)
            for r in ResultadoEtapa.vigentes.filter(
                edital=edital,
                etapa_id=etapa,
                inscricao_id__in=[i for i, _ in posicoes],
                consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
            )
        }
        if etapa is not None and posicoes
        else set()
    )
    return {
        "posicoes": posicoes,
        "excluidos": conta.excluidos_por_efeito(efeitos),
        "confirmadosNaAmpla": confirmados,
        "semConfirmacaoNaAmpla": (ocupantes_da_ampla & membros) - confirmados,
        "alcancaveis": alcancaveis,
        "eliminados": eliminados,
        "ocupantes": ocupantes,
        "etapaGovernada": etapa,
    }


def _destinadas(movimentos, lista_id):
    """O saldo do que a reserva cedeu à ampla — pelo movimento antigo ou pelo ato (FR-6316)."""
    if lista_id is None:
        return 0
    total = 0
    for movimento in movimentos:
        if calculo.mesma_lista(movimento.origem_lista_id, lista_id):
            total += movimento.quantidade
        elif calculo.mesma_lista(movimento.destino_lista_id, lista_id):
            total -= movimento.quantidade
    return max(total, 0)


# --- A prévia ----------------------------------------------------------------------------------


def previa_da_destinacao(*, edital, perfil_id, marco_id, lista_id, fatos_externos, at=None):
    """O que o ato faria agora, e a recusa que daria — **sem gravar nada** (FR-6309, UX-601)."""
    leitura = leitura_da_vaga(
        edital=edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        fatos_externos=fatos_externos,
        at=at,
    )
    situacao = leitura["situacao"]
    ampla = selectors.apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=None
    )
    quantidade = situacao["quantidade"] if situacao["estado"] == conta.DESTINACAO_DISPONIVEL else 0
    return {
        **leitura,
        "quantidade": quantidade,
        "recusa": _recusa(leitura),
        "ampla": ampla,
        "amplaDepois": (ampla.efetivas + quantidade) if ampla is not None else None,
        "origemDepois": (
            leitura["apuracao"].efetivas - quantidade if leitura["apuracao"] is not None else None
        ),
        # **A assinatura cobre o que o ato lê** (FR-6342): a apuração, os movimentos, a versão e a
        # declaração. Qualquer um que mude entre a conferência e o clique é leitura nova, e o ato
        # recusa com `leitura_do_recorte_mudou` em vez de confirmar o que a pessoa não viu.
        "assinatura": canonical_sha256(
            {
                "gesto": "destinacao",
                "apuracao": str(leitura["apuracao"].id) if leitura["apuracao"] else None,
                "movimentos": [str(m.id) for m in leitura["movimentos"]],
                "versao": str(leitura["versao"].id),
                "declaracao": leitura["declaracao"],
                "quantidade": quantidade,
            }
        ),
    }


def _recusa(leitura):
    """`(codigo, frase)` da recusa que o ato daria, na ordem do contrato, ou `None` (FR-6312)."""
    situacao = leitura["situacao"]
    declaracao = leitura["declaracao"]
    if declaracao is None:
        return (
            nomes.SEM_REVERSAO_DECLARADA,
            "Este Edital não declara o que acontece com a vaga reservada não preenchida: sem a "
            "declaração, nenhum ato a move para a ampla concorrência.",
        )
    if declaracao == nomes.PASSAGEM_ENTRE_COTAS:
        return (
            nomes.RECUSA_PASSAGEM_ENTRE_COTAS,
            "Este Edital manda a vaga passar antes por outras cotas, e o GPS ainda não aplica essa "
            "ordem: a vaga não vai direto à ampla concorrência.",
        )
    if declaracao == nomes.REVERSAO_POR_SALDO:
        # **Sem frase sobre decisões** na tela: a recusa diz o que o ato não faz aqui, e a tela não
        # chega a oferecê-lo.
        return (
            nomes.REVERSAO_POR_SALDO_AGUARDA_DECISAO,
            "A destinação por ato próprio não se aplica à reversão pelo saldo não preenchido.",
        )
    if leitura["apuracao"] is None or leitura.get("saldo") is None:
        return (
            nomes.SEM_SALDO_A_DESTINAR,
            "Esta lista ainda não tem apuração: não há vaga a ocupar afirmada para destinar.",
        )
    if situacao["estado"] == conta.IMPEDIDA and situacao["impedimentos"]:
        primeiro = situacao["impedimentos"][0]
        return (nomes.DESTINACAO_IMPEDIDA, _frase_do_impedimento(primeiro))
    if not leitura["saldo"]:
        return (
            nomes.SEM_SALDO_A_DESTINAR,
            "Esta lista não tem vaga a ocupar"
            + (": a vaga já foi destinada à ampla concorrência." if leitura["destinadas"] else "."),
        )
    if situacao["aindaPodemOcupar"]:
        quantas = situacao["aindaPodemOcupar"]
        return (
            nomes.AINDA_HA_QUEM_OCUPAR,
            f"Ainda há {quantas} pessoa{'s' if quantas != 1 else ''} na ordem desta lista que "
            f"{'podem' if quantas != 1 else 'pode'} ocupar a vaga: a lista não está esgotada.",
        )
    if situacao["estado"] != conta.DESTINACAO_DISPONIVEL:
        return (
            nomes.DESTINACAO_IMPEDIDA,
            "A vaga desta lista não está disponível para destinação.",
        )
    return None


def _frase_do_impedimento(impedimento):
    from processo_seletivo.shared.tempo import ZONA

    frase = impedimento.frase[:1].upper() + impedimento.frase[1:]
    if impedimento.ate is not None:
        frase += f", até {impedimento.ate.astimezone(ZONA).strftime('%d/%m/%Y às %Hh%M')}"
    return frase + "."


# --- O ato -------------------------------------------------------------------------------------


def destinar_vaga(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    lista_id,
    assinatura,
    fatos_externos,
    idempotency_key,
    correlation_id,
):
    """Grava a destinação e emite a sucessora da apuração de origem, num *savepoint* (FR-6310)."""
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else "",
        "leitura": assinatura or "",
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO_DE_DESTINAR,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        edital = _edital_do_processo(ctx.processo, edital_id)
        perfil, marco = identificador(perfil_id), identificador(marco_id)
        lista = identificador(lista_id) if lista_id else None
        # **Os fatos externos são reavaliados aqui, sob a trava** (155, R-004): a chamada aberta ou
        # o recurso interposto entre a conferência e o clique impedem o ato que a tela ofereceu.
        previa = previa_da_destinacao(
            edital=edital,
            perfil_id=perfil,
            marco_id=marco,
            lista_id=lista,
            fatos_externos=fatos_externos,
            at=ctx.now,
        )
        if previa["recusa"] is not None:
            codigo, frase = previa["recusa"]
            raise DomainError(codigo, frase, 409)
        if (assinatura or "") != previa["assinatura"]:
            raise DomainError(
                nomes.LEITURA_DO_RECORTE_MUDOU,
                "As vagas desta lista mudaram desde que a conferência foi aberta: confira de novo "
                "antes de confirmar.",
                409,
            )
        quantidade = previa["quantidade"]
        versao = previa["versao"]
        movimento = MovimentoDeVaga.objects.create(
            # A apuração **lida** pelo ato, e não a que o causou (155, R-001): reproduzir o ato é
            # reler esta, com a versão e a frase que ele citou (FR-6342).
            apuracao=previa["apuracao"],
            edital=edital,
            perfil_id=perfil,
            marco_id=marco,
            especie=nomes.MOVIMENTO_REVERSAO,
            origem_lista_id=lista,
            destino_lista_id=None,
            quantidade=quantidade,
            causa=(
                f"Destinação à ampla concorrência por ato próprio: {quantidade} de "
                f"{previa['apuracao'].publicadas}."
            ),
            gatilho=previa["declaracao"],
            fundamento=_fundamento(previa),
            versao=versao,
            registrado_por=str(getattr(actor, "subject", actor)),
            registrado_em=ctx.now,
        )
        seguinte = _emitir_seguinte(
            ctx,
            actor,
            edital=edital,
            perfil_id=perfil,
            marco_id=marco,
            lista_id=lista,
            motivo=f"Destinação de {quantidade} vaga(s) à ampla concorrência.",
            correlation_id=correlation_id,
        )
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=DESTINAR,
            aggregate=movimento,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=_razao(movimento, previa, seguinte),
            idempotency_key=idempotency_key,
        )
        declarado = {
            "movimento": str(movimento.id),
            "quantidade": quantidade,
            "gatilho": movimento.gatilho,
            **seguinte,
        }
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


def _fundamento(previa):
    """A frase publicada e a versão que a disse — o que a FR-6310 manda registrar."""
    from processo_seletivo.shared.tempo import ZONA

    versao = previa["versao"]
    return (
        f"{previa['frase']} (versão do Edital vigente desde "
        f"{versao.valid_from.astimezone(ZONA).strftime('%d/%m/%Y %H:%M')})"
    )


def _emitir_seguinte(ctx, actor, *, edital, perfil_id, marco_id, lista_id, motivo, correlation_id):
    """A sucessora da apuração de origem, ou o que a impede — o molde do acréscimo (`T-004`).

    **Só quando o movimento é a única causa**: o ato só é aceito sobre apuração vigente sem
    obsolescência, e a causa nova é a dele. Num *savepoint*: a recusa da emissão não desfaz a
    destinação, que aconteceu, e a origem aparece obsoleta pela causa dita.
    """
    vigente = selectors.apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    causas = {c["causa"] for c in selectors.causas_de_obsolescencia(vigente, at=ctx.now)}
    if vigente is not None and causas - {nomes.CAUSA_MOVIMENTO_POSTERIOR}:
        return _pendente(
            nomes.OUTRA_CAUSA_DE_OBSOLESCENCIA,
            "A apuração desta lista já estava obsoleta por outra causa: emita a seguinte na "
            "ocupação, onde a causa é dita.",
        )
    try:
        with transaction.atomic():
            declarado = emitir_sucessora_por_efeito(
                actor=actor,
                permissao=ctx.base.permissao,
                edital=edital,
                perfil_id=perfil_id,
                marco_id=marco_id,
                lista_id=lista_id,
                motivo=motivo,
                now=ctx.now,
                correlation_id=correlation_id,
            )
    except DomainError as recusa:
        return _pendente(recusa.code, recusa.detail)
    if declarado is None:
        # Por esgotamento a emissão não move vaga desde a `155` (FR-6315): este ramo é guarda.
        return _pendente(nomes.OUTRA_CAUSA_DE_OBSOLESCENCIA, "A apuração seguinte moveria vaga.")
    return {"apuracaoSeguinte": declarado, "apuracaoPendente": None}


def _pendente(codigo, detalhe):
    return {"apuracaoSeguinte": None, "apuracaoPendente": {"codigo": codigo, "detalhe": detalhe}}


def _razao(movimento, previa, seguinte):
    """O que a trilha guarda para reconstruir o ato sem abrir o banco (FR-6310, FR-6341)."""
    emitida = seguinte["apuracaoSeguinte"]
    return (
        f"Destinação de {movimento.quantidade} vaga(s) da lista {movimento.origem_lista_id} à "
        f"ampla concorrência, no marco {movimento.marco_id}, Perfil {movimento.perfil_id}, por "
        f"esgotamento. Fundamento: {movimento.fundamento}. "
        f"Apuração lida: {previa['apuracao'].id}; "
        + (
            f"sucessora: {emitida['id']}."
            if emitida
            else f"sucessora pendente: {seguinte['apuracaoPendente']['codigo']}."
        )
    )


__all__ = [
    "DESTINAR",
    "destinar_vaga",
    "frase_publicada",
    "leitura_da_vaga",
    "previa_da_destinacao",
]
