"""Emite a apuração de ocupação como ato imutável, e a sucede quando já há uma (016, `D-008`).

**Tudo o que é autoridade, idempotência e trilha vem de onde já vinha**: o mesmo
`comando_de_comissao` que a emissão da ordem e a do corte percorrem, e a mesma permissão. Uma
capacidade nova aqui inventaria autoridade que nenhum Edital distingue — é a decisão que a `014` já
tomou, e esta feature a herda.

**Esta feature não seleciona ninguém.** Ela lê a faixa que o corte vigente produziu e o Resultado
que a `013` consolidou, e conta. Quem escolhe é a `014`; quem convoca é a `019`.
"""

from uuid import uuid4

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.classificacao.application.corte import linha_do_quadro
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.ocupacao.application import movimento as movimento_de_vaga
from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.domain import apuracao as calculo
from processo_seletivo.ocupacao.domain import reversao
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError

APURAR = "OCUPACAO_APURAR"
# A mesma permissão da ordem e do corte. A autoridade é consumida, não inventada.
ATO = "classificacao:emitir"


def emitir_apuracao(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    idempotency_key,
    correlation_id,
    lista_id=None,
    motivo="",
):
    """Apura o recorte e grava o ato. Havendo apuração vigente, cria a sucessora sem tocar nela."""
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else "",
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
        perfil = identificador(perfil_id)
        marco = identificador(marco_id)
        lista = identificador(lista_id) if lista_id else None

        # **A ordem tem de ser a vigente** (`FR-243`): apurar sobre ordem sucedida contaria
        # ocupação de uma ordem que o próprio sistema já sabe estar para trás.
        ato = ato_vigente(edital=edital, marco_id=marco, lista_id=lista)
        if ato is None:
            raise DomainError(
                "ordem_nao_vigente",
                "Este recorte não tem ordem vigente: não há ocupação a apurar.",
                409,
            )

        versao = effective_version(edital_id=edital.id, at=ctx.now)
        linha = linha_do_quadro(versao.content, perfil_id=perfil, lista_id=lista)
        if linha is None:
            # **Ausência de quadro não é zero** (`FR-242`, `UX-032`). Edital publicado antes do
            # degrau 12 não declarou quantidade nenhuma, e apurar ali afirmaria o que ele não disse.
            raise DomainError(
                "sem_quadro_publicado",
                "Este Edital não publicou quadro de vagas para este recorte: não há quantidade "
                "declarada a apurar.",
                409,
            )

        vigente = selectors.apuracao_vigente(
            edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista
        )
        texto_do_motivo = (motivo or "").strip()
        if vigente and not texto_do_motivo:
            raise DomainError(
                "motivo_da_sucessao_obrigatorio",
                "Declare o motivo da sucessão da apuração vigente.",
                422,
                campo="motivo",
            )

        progrediram, corte = selectors.dentro_da_faixa(
            edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista
        )
        etapa = corte.etapa_governada_id if corte is not None else None
        habilitadas = selectors.habilitadas_na_etapa(edital=edital, etapa_id=etapa)

        movimentos = _movimentos_a_ler(edital=edital, perfil=perfil, marco=marco, lista=lista)
        lidos = [
            (m.especie, calculo.mesma_lista(m.destino_lista_id, lista), m.quantidade)
            for m in movimentos
        ]
        # **A concorrência concomitante é exclusão, e não transferência** (`FR-252`). Num recorte
        # reservado, quem já ocupou pela ampla não é computado aqui — item 8.9 do 28/2026, que diz
        # "não constarão na lista de classificados como autodeclarados, abrindo vaga para o próximo
        # suplente autodeclarado". A vaga reservada **continua sendo da reserva**, e o que muda é
        # que ele não a ocupou.
        ocupantes_da_ampla = (
            _ocupantes_da_ampla(edital=edital, perfil=perfil, marco=marco)
            if lista is not None
            else set()
        )
        publicadas, efetivas, ocupadas = calculo.apurar(
            publicadas=_quantidade(linha),
            dentro_da_faixa=progrediram,
            habilitadas=habilitadas,
            movimentos_lidos=lidos,
            ocupantes_da_ampla=ocupantes_da_ampla,
        )

        # **A cessão é calculada antes de a apuração existir, e o id do movimento nasce aqui.**
        # É o que permite a apuração citar o próprio movimento em `movimentosLidos` e nascer com a
        # `efetivas` líquida — sem isso ela nascia obsoleta pelo movimento que ela mesma causou.
        especie_da_reversao = _declaracao(versao.content, perfil_id=perfil)
        cede = (
            movimento_de_vaga.quantidade_que_a_cota_cede(
                especie=especie_da_reversao,
                efetivas=efetivas,
                ocupadas=ocupadas,
                ha_quem_ocupar=movimento_de_vaga.ha_quem_ocupar(
                    edital=edital, marco_id=marco, lista_id=lista, ja_ocupadas=ocupadas
                ),
            )
            if lista is not None
            else 0
        )
        identidade_do_movimento = uuid4() if cede else None
        if cede:
            efetivas -= cede

        apuracao = ApuracaoDeOcupacao(
            edital=edital,
            perfil_id=perfil,
            marco_id=marco,
            lista_id=lista,
            ato=ato,
            corte=corte,
            versao=versao,
            apuracao_anterior=vigente,
            motivo_da_sucessao=texto_do_motivo,
            publicadas=publicadas,
            efetivas=efetivas,
            ocupadas=ocupadas,
            linha_do_quadro_id=linha.get("id"),
            universo={
                "rowId": str(linha.get("id")) if linha.get("id") else None,
                "immediateVacancies": publicadas,
                "vacancyReversion": _declaracao(versao.content, perfil_id=perfil),
                "governedStage": str(etapa) if etapa else None,
                "orderId": str(ato.id),
                "cutId": str(corte.id) if corte is not None else None,
                # **Os ids, e não "os movimentos de hoje"**: reproduzir é reler estes
                # (`FR-244`). Sem o congelamento, uma apuração antiga relida devolveria o número
                # que o mundo virou depois, e não o que ela apurou.
                "movimentosLidos": [str(m.id) for m in movimentos]
                + ([str(identidade_do_movimento)] if identidade_do_movimento else []),
            },
            emitida_por=str(getattr(actor, "subject", actor)),
            emitida_em=ctx.now,
        )
        apuracao.save()
        movimento = (
            movimento_de_vaga.gravar_reversao(
                identidade=identidade_do_movimento,
                apuracao=apuracao,
                quantidade=cede,
                origem_lista_id=lista,
                publicadas=publicadas,
                especie=especie_da_reversao,
                registrado_por=str(getattr(actor, "subject", actor)),
                registrado_em=ctx.now,
            )
            if cede
            else None
        )
        return _concluir(ctx, apuracao, actor, correlation_id, idempotency_key, movimento=movimento)


def _ocupantes_da_ampla(*, edital, perfil, marco):
    """Quem ocupa vaga pela ampla concorrência: dentro da faixa dela **e** habilitado.

    É a mesma conta que a apuração da ampla faz, lida de fora — e é ela que a reservada subtrai.
    """
    progrediram, corte = selectors.dentro_da_faixa(
        edital=edital, perfil_id=perfil, marco_id=marco, lista_id=None
    )
    etapa = corte.etapa_governada_id if corte is not None else None
    return progrediram & selectors.habilitadas_na_etapa(edital=edital, etapa_id=etapa)


def _movimentos_a_ler(*, edital, perfil, marco, lista):
    """Os movimentos que alcançam este recorte, cedendo ou recebendo.

    **A busca é pelo recorte, e não pela apuração.** O movimento nasce com a apuração da origem, e
    é a apuração do destino que o lê: procurá-lo por `apuracao` devolveria só o que a própria origem
    gravou, e o destino nunca veria o que recebeu.
    """
    from processo_seletivo.ocupacao.models import MovimentoDeVaga

    candidatos = MovimentoDeVaga.objects.filter(
        apuracao__edital=edital, apuracao__perfil_id=perfil, apuracao__marco_id=marco
    ).order_by("registrado_em")
    return [
        m
        for m in candidatos
        if calculo.mesma_lista(m.origem_lista_id, lista)
        or calculo.mesma_lista(m.destino_lista_id, lista)
    ]


def _declaracao(conteudo, *, perfil_id):
    from processo_seletivo.classificacao.domain.universo import por_identidade

    perfil = por_identidade((conteudo or {}).get("profiles"), perfil_id) or {}
    return reversao.declarada(perfil)


def _quantidade(linha):
    """A quantidade publicada da linha, ou recusa.

    **Nunca devolve zero por omissão.** A conferência da `025` garante que a linha publicada tem
    quantidade inteira; se ela chegar aqui malformada, escrever `0` num ato append-only afirmaria
    que o Edital publicou nenhuma vaga — e num ato imutável isso não tem conserto. Recusar é o
    único desfecho reversível.
    """
    quantidade = linha.get("immediateVacancies")
    if isinstance(quantidade, int) and not isinstance(quantidade, bool):
        return quantidade
    raise DomainError(
        "recorte_sem_linha",
        "A linha do quadro deste recorte não publica quantidade inteira de vagas.",
        409,
    )


def _concluir(ctx, apuracao, actor, correlation_id, idempotency_key, *, movimento=None):
    auditar(
        actor=actor,
        permissao=ctx.base.permissao,
        operation=APURAR,
        aggregate=apuracao,
        now=ctx.now,
        correlation_id=correlation_id,
        # **O que a `FR-259` exige entra na razão, e não só no agregado.** Ator, ação e instante o
        # registro genérico já guarda; recorte, ordem citada e as quantidades são desta feature, e
        # sem eles a auditoria não reconstrói o número sem abrir o banco.
        reason=(
            f"Ocupação do marco {apuracao.marco_id}, Perfil {apuracao.perfil_id}, "
            f"lista {apuracao.lista_id or 'ampla concorrência'}: {apuracao.publicadas} publicadas, "
            f"{apuracao.efetivas} efetivas, {apuracao.ocupadas} ocupadas, "
            f"{apuracao.faltando} a ocupar, sobre a ordem {apuracao.ato_id}."
            + (
                f" Motivo da sucessão: {apuracao.motivo_da_sucessao}"
                if apuracao.motivo_da_sucessao
                else ""
            )
            + (
                f" Reversão: {movimento.quantidade} vaga(s) para a ampla concorrência."
                if movimento is not None
                else ""
            )
        ),
        idempotency_key=idempotency_key,
    )
    declarado = {
        "id": str(apuracao.id),
        "publicadas": apuracao.publicadas,
        "efetivas": apuracao.efetivas,
        "ocupadas": apuracao.ocupadas,
        "faltando": apuracao.faltando,
        "universo": apuracao.universo,
        "reverteu": movimento.quantidade if movimento is not None else 0,
    }
    ctx.concluir_sem_resultado(201, declarado)
    return declarado


def _edital_do_processo(processo, edital_id):
    try:
        return Edital.objects.get(processo=processo, id=identificador(edital_id))
    except Edital.DoesNotExist as erro:
        raise DomainError("edital_nao_encontrado", "Edital não encontrado.", 404) from erro


__all__ = ["emitir_apuracao"]
