"""O que a pessoa respondeu, ou o que a Administração concluiu — e o que isso faz na contagem (019).

**Um desfecho por convocação** (`FR-273`), e a constraint o garante. Dois desfechos para a mesma
chamada seriam duas respostas contraditórias sobre a mesma vaga, e o sistema não teria como dizer
qual vale.

**O efeito de cada espécie é declarado, nunca inferido** (`R-006`). Duas linhas incluem — aceite e
regularização — e cinco excluem. Sem a inclusão, quatro desfechos desceriam o número e nenhum o
subiria: a suplente que aceita nunca entraria na contagem.

**Nenhuma apuração é reescrita aqui** (`D-006`). O efeito entra pela porta da `016`, a apuração
vigente passa a aparecer **obsoleta** com a causa nomeada, e o número novo sai na emissão seguinte.
Escrever na apuração seria `UPDATE` em tabela append-only, e a proibição está instalada no banco em
duas camadas.

**O desfecho e o efeito são um fato só**, e por isso nascem na mesma transação: gravar um sem o
outro deixaria ou uma exclusão sem causa, ou um desfecho que prometeu mexer no número e não mexeu.
"""

from datetime import timedelta
from uuid import uuid4

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.domain import nomes, prazo
from processo_seletivo.convocacao.models import (
    AtestadoDeFatoExterno,
    Convocacao,
    DesfechoDaConvocacao,
)
from processo_seletivo.ocupacao.application import efeitos as porta_de_efeitos
from processo_seletivo.ocupacao.domain.apuracao import chave_da_inscricao
from processo_seletivo.shared.api.problems import DomainError

DESFECHAR = "CONVOCACAO_DESFECHAR"
ATO = "convocacao:desfechar"

#: O rótulo que a porta da `016` guarda ao lado do `ato_de_origem_id` opaco. Sem ele a trilha diria
#: *"efeito de origem `3f2a…`"*, que não é linguagem humana nenhuma (`FR-296`).
ROTULO_DA_ORIGEM = "desfecho de convocação"


def desfechar(
    *,
    actor,
    processo_id,
    convocacao_id,
    especie,
    fundamento,
    idempotency_key,
    correlation_id,
    atestado_id=None,
    resultado_sucessor=None,
    motivo="",
):
    """Registra o desfecho, escreve o efeito na porta, e devolve o que o ato declarou."""
    payload = {
        "convocacao": str(convocacao_id),
        "especie": (especie or "").strip(),
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
        convocacao = _convocacao_do_processo(ctx.processo, convocacao_id)
        especie = _especie(especie)
        texto = (fundamento or "").strip()
        if not texto:
            raise DomainError(
                nomes.FUNDAMENTO_OBRIGATORIO,
                "Declare o fundamento do desfecho.",
                422,
                campo="fundamento",
            )
        _recusar_convocacao_sucedida(convocacao)
        anterior = _vigente_da_convocacao(convocacao)
        texto_do_motivo = (motivo or "").strip()
        if anterior is not None and not texto_do_motivo:
            raise DomainError(
                nomes.DESFECHO_JA_REGISTRADO,
                "Esta convocação já tem desfecho registrado. Um fato posterior — o cancelamento "
                "por inércia de quem havia aceitado, por exemplo — o sucede, e a sucessão exige "
                "motivo; o desfecho anterior continua legível.",
                409,
            )
        _recusar_desfecho_incompativel(convocacao, especie=especie)
        _recusar_nao_atendimento_prematuro(convocacao, especie=especie, agora=ctx.now)
        _recusar_inercia_sem_ocupacao(convocacao, especie=especie, agora=ctx.now)
        atestado = _atestado(especie, atestado_id, convocacao)
        # **O identificador do desfecho nasce antes dele**, e a ordem é a mesma que a `016` usa para
        # o movimento de vaga: o Resultado sucessor precisa citar o desfecho que o produziu, e o
        # desfecho precisa citar o Resultado. Gerar o id primeiro quebra o ovo sem afrouxar
        # constraint nenhuma — as duas linhas nascem completas, na mesma transação.
        identidade = uuid4()
        if especie == nomes.REGULARIZACAO and resultado_sucessor is None:
            resultado_sucessor = _suceder_o_resultado(
                convocacao, desfecho_id=identidade, actor=actor, agora=ctx.now, fundamento=texto
            )

        efeito = porta_de_efeitos.registrar_efeito(
            edital=convocacao.edital,
            perfil_id=convocacao.perfil_id,
            marco_id=convocacao.marco_id,
            lista_id=convocacao.lista_id,
            inscricao_id=convocacao.inscricao_id,
            especie=nomes.EFEITO_POR_DESFECHO[especie],
            fundamento=texto,
            # **O ato de origem é o desfecho, e não a convocação** — é ele que produz o efeito, e
            # é o que o rótulo ao lado diz. Apontar para a convocação faria a trilha da `016` citar
            # a chamada como causa de uma exclusão que ela não causou: quem convoca não exclui
            # ninguém, e a mesma chamada pode ter um desfecho sucedido por outro.
            ato_de_origem_id=identidade,
            rotulo_da_origem=ROTULO_DA_ORIGEM,
            registrado_por=str(getattr(actor, "subject", actor)),
            registrado_em=ctx.now,
        )
        desfecho = DesfechoDaConvocacao(
            id=identidade,
            convocacao=convocacao,
            especie=especie,
            fundamento=texto,
            atestado=atestado,
            resultado_sucessor=resultado_sucessor,
            efeito=efeito,
            desfecho_anterior=anterior,
            motivo_da_sucessao=texto_do_motivo if anterior is not None else "",
            registrado_por=str(getattr(actor, "subject", actor)),
            registrado_em=ctx.now,
        )
        desfecho.save()
        return _concluir(ctx, desfecho, actor, correlation_id, idempotency_key)


def _suceder_o_resultado(convocacao, *, desfecho_id, actor, agora, fundamento):
    """O Resultado sucessor que a regularização produz (019, `D-008`, `R-005`).

    **Pelo mecanismo da `018`, e não por um caminho próprio de habilitação.** A alternativa — um
    ato só da `019` que marcasse a pessoa como apta — criaria um segundo caminho de habilitação,
    invisível para a contagem da `016`: a `Q-3` a recusou por escrito.

    **A fonte jurídica é o desfecho, e não uma `DecisaoRecurso`.** Ninguém interpôs recurso aqui;
    reusar aquela FK com um recurso sintético registraria um recurso que não existiu.

    **O indeferido continua existindo, sucedido.** Nada é apagado: a linha anterior permanece
    legível, com o motivo do indeferimento, e é ela que explica por que houve convocação para
    regularizar.
    """
    from processo_seletivo.classificacao.models import Corte
    from processo_seletivo.resultados.models import ResultadoEtapa

    etapa = (
        Corte.objects.filter(id=convocacao.corte_id)
        .values_list("etapa_governada_id", flat=True)
        .first()
        if convocacao.corte_id
        else None
    )
    if etapa is None:
        # Marco que não corta não tem Etapa governada, e sem ela não há Resultado a suceder. A
        # regularização ali não teria o que regularizar — e inventar a Etapa seria decidir qual
        # requisito a pessoa deixou de cumprir.
        raise DomainError(
            nomes.REGULARIZACAO_EXIGE_SUCESSOR,
            "Este recorte não tem Etapa governada pelo corte: não há Resultado a suceder, e a "
            "regularização não tem o que regularizar.",
            409,
        )
    superado = (
        ResultadoEtapa.vigentes.filter(
            inscricao_id=convocacao.inscricao_id, edital=convocacao.edital, etapa_id=etapa
        )
        .order_by("-consolidado_em")
        .first()
    )
    if superado is None or superado.consequencia != ResultadoEtapa.Consequencia.ELIMINADA:
        raise DomainError(
            nomes.REGULARIZACAO_EXIGE_SUCESSOR,
            "Esta Inscrição não tem Resultado indeferido vigente nesta Etapa: não há o que "
            "regularizar.",
            409,
        )
    # **Posterior ao superado, e por forma**: a trigger exige a cronologia monotônica, sem a qual
    # "o mais recente" e "o vigente" poderiam divergir na auditoria.
    consolidado_em = max(agora, superado.consolidado_em + timedelta(seconds=1))
    return ResultadoEtapa.objects.create(
        inscricao_id=convocacao.inscricao_id,
        edital=convocacao.edital,
        etapa_id=etapa,
        origem=ResultadoEtapa.Origem.REGULARIZACAO,
        avaliacao=None,
        versao=convocacao.versao,
        # Sem forma, sem pontuação e sem sentido: a regularização não mede nada — ela constata que
        # o que faltava foi entregue. É o mesmo ramo que a Ocorrência usa.
        forma="",
        pontuacao=None,
        sentido="",
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        motivo=fundamento,
        consolidado_em=consolidado_em,
        consolidado_por=str(getattr(actor, "subject", actor)),
        resultado_anterior=superado,
        motivo_da_superacao=fundamento,
        decisao=None,
        desfecho_de_convocacao_id=desfecho_id,
    )


def _especie(valor):
    especie = (valor or "").strip()
    if especie not in nomes.ESPECIES_DE_DESFECHO:
        raise DomainError(
            nomes.ESPECIE_DE_DESFECHO_INVALIDA,
            "O desfecho é um dos sete que os Editais nomeiam, e nada mais.",
            422,
            campo="especie",
        )
    return especie


def _vigente_da_convocacao(convocacao):
    """O desfecho que ninguém sucedeu, ou `None` — a mesma leitura que a tela faz."""
    return selectors.desfecho_de(convocacao)


def _recusar_desfecho_incompativel(convocacao, *, especie):
    """Nem toda espécie cabe em toda chamada (`nomes.DESFECHOS_POR_ESPECIE`).

    **O enum diz que a espécie existe; esta recusa diz que ela não cabe aqui.** Sem ela, uma
    convocação **para regularizar** podia terminar em `ACEITE` — incluindo a pessoa na contagem de
    ocupantes sem que Resultado nenhum a habilitasse —, e uma chamada para vaga podia terminar em
    `REGULARIZACAO`, produzindo sucessor de um Resultado que não estava indeferido.

    O registro é append-only: a transição impossível entraria uma vez e ficaria.
    """
    admitidos = nomes.DESFECHOS_POR_ESPECIE.get(convocacao.especie, ())
    if especie in admitidos:
        return
    raise DomainError(
        nomes.DESFECHO_INCOMPATIVEL_COM_A_CHAMADA,
        f"Uma convocação da espécie {convocacao.get_especie_display().lower()} não admite este "
        "desfecho.",
        422,
        campo="especie",
    )


def _recusar_nao_atendimento_prematuro(convocacao, *, especie, agora):
    """Não atender pressupõe ter tido como atender (`FR-269a`, `FR-269b`).

    **Duas condições, e as duas são do prazo.** A comunicação precisa ter sido enviada — sem envio
    o relógio não corre, e dar por não atendida uma chamada que nunca partiu puniria a pessoa por
    uma falha do sistema. E o vencimento informado precisa ter passado: antes dele, a pessoa ainda
    está dentro do prazo dela.

    **Sem vencimento informado, basta o envio.** O Edital que não publica prazo deixa o juízo a
    quem conduz o certame, e não é o sistema que vai inventar um.

    Isto não contraria a `FR-274`: o decurso continua **não produzindo** desfecho nenhum sozinho.
    O que ele faz é abrir a porta para o ato de quem conduz.
    """
    if especie != nomes.NAO_ATENDIMENTO:
        return
    enviado_em = selectors.envio_de(convocacao)
    if not prazo.prazo_corre(enviado_em=enviado_em):
        raise DomainError(
            nomes.NAO_ATENDIMENTO_ANTES_DO_VENCIMENTO,
            "A comunicação desta convocação não foi enviada com sucesso: o prazo não começou a "
            "correr, e não há não atendimento a registrar.",
            409,
        )
    if convocacao.vencimento is not None and not prazo.decorrido(
        vencimento=convocacao.vencimento, enviado_em=enviado_em, agora=agora
    ):
        raise DomainError(
            nomes.NAO_ATENDIMENTO_ANTES_DO_VENCIMENTO,
            "O vencimento informado nesta convocação ainda não passou: a pessoa está dentro do "
            "prazo dela.",
            409,
        )


def _recusar_inercia_sem_ocupacao(convocacao, *, especie, agora):
    """O cancelamento por inércia alcança **quem já ocupava** e desapareceu (§6 da spec).

    Registrá-lo sobre quem nunca ocupou vaga nenhuma cancelaria uma matrícula que não existe — e o
    desfecho certo ali é outro: não atendimento à convocação, que é a resposta que falta.
    """
    if especie != nomes.INERCIA:
        return
    contexto = selectors.contexto_do_recorte(
        edital=convocacao.edital,
        perfil_id=convocacao.perfil_id,
        marco_id=convocacao.marco_id,
        lista_id=convocacao.lista_id,
        at=agora,
    )
    if chave_da_inscricao(convocacao.inscricao_id) in contexto["ocupando"]:
        return
    raise DomainError(
        nomes.INERCIA_SEM_OCUPACAO,
        "Esta Inscrição não consta ocupando vaga neste recorte: não há matrícula a cancelar por "
        "inércia. Quem foi chamado e não respondeu tem desfecho próprio — não atendimento à "
        "convocação.",
        409,
    )


def _recusar_convocacao_sucedida(convocacao):
    """Desfechar um ato já corrigido registraria a resposta contra a chamada errada.

    **Não está no contrato, e é uma consequência da sucessão.** Corrigida a convocação, é a
    sucessora que vale; gravar o desfecho na anterior o deixaria invisível para a leitura do
    recorte, que só olha as vigentes — e a pessoa apareceria como não tendo respondido.
    """
    if convocacao.sucessoras.exists():
        raise DomainError(
            nomes.CONVOCACAO_SUCEDIDA,
            "Esta convocação foi corrigida por uma sucessora: registre o desfecho na convocação "
            "vigente desta Inscrição.",
            409,
        )


def _atestado(especie, atestado_id, convocacao):
    """O atestado de fato externo, obrigatório na inércia (`FR-277`, `atestado_obrigatorio`).

    **Fato externo sem atestante não entra.** O cancelamento por inércia decide a vaga de alguém, e
    *"o prazo venceu"* não é uma pessoa responsável — a `D-004` exige que alguém competente tenha
    concluído, e a constraint do banco diz o mesmo por forma.
    """
    if especie != nomes.INERCIA:
        return None
    if atestado_id is None:
        raise DomainError(
            nomes.ATESTADO_OBRIGATORIO,
            "O cancelamento de matrícula por inércia exige atestado de fato externo: registre "
            "quem atestou e o que concluiu.",
            422,
            campo="atestado",
        )
    atestado = AtestadoDeFatoExterno.objects.filter(id=identificador(atestado_id)).first()
    if atestado is None or atestado.inscricao_id != convocacao.inscricao_id:
        # O atestado é de **outra** pessoa: aceitá-lo cancelaria a matrícula de quem nunca foi
        # atestado, com a trilha apontando para o fato de um terceiro.
        raise DomainError(
            nomes.ATESTADO_OBRIGATORIO,
            "O atestado informado não é desta Inscrição.",
            422,
            campo="atestado",
        )
    return atestado


def _concluir(ctx, desfecho, actor, correlation_id, idempotency_key):
    convocacao = desfecho.convocacao
    auditar(
        actor=actor,
        permissao=ctx.base.permissao,
        operation=DESFECHAR,
        aggregate=desfecho,
        now=ctx.now,
        correlation_id=correlation_id,
        reason=(
            f"Desfecho {desfecho.especie} da convocação {convocacao.id}, inscrição "
            f"{convocacao.inscricao_id} no marco {convocacao.marco_id}, lista "
            f"{convocacao.lista_id or 'ampla concorrência'}. Efeito na ocupação: "
            f"{desfecho.efeito.especie}. Fundamento: {desfecho.fundamento}"
        ),
        idempotency_key=idempotency_key,
    )
    declarado = {
        "id": str(desfecho.id),
        "convocacao": str(convocacao.id),
        "especie": desfecho.especie,
        "efeito": desfecho.efeito.especie,
    }
    ctx.concluir_sem_resultado(201, declarado)
    return declarado


def _convocacao_do_processo(processo, convocacao_id):
    convocacao = (
        Convocacao.objects.filter(id=identificador(convocacao_id), edital__processo=processo)
        .select_related("edital")
        .first()
    )
    if convocacao is None:
        raise DomainError("convocacao_nao_encontrada", "Convocação não encontrada.", 404)
    return convocacao


__all__ = ["desfechar"]
