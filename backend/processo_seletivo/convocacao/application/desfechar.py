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
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import (
    AtestadoDeFatoExterno,
    Convocacao,
    DesfechoDaConvocacao,
)
from processo_seletivo.ocupacao.application import efeitos as porta_de_efeitos
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
        _recusar_desfecho_repetido(convocacao)
        _recusar_convocacao_sucedida(convocacao)
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
            ato_de_origem_id=convocacao.id,
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


def _recusar_desfecho_repetido(convocacao):
    """`desfecho_ja_registrado` (`FR-273`).

    **Recusado aqui e no banco, e as duas não são redundantes.** A constraint vale para quem chegue
    por fora da aplicação; esta recusa é a que nomeia o que aconteceu para quem está na tela — e
    evita que a resposta seja um erro de integridade sem tradução.
    """
    if selectors.desfecho_de(convocacao) is not None:
        raise DomainError(
            nomes.DESFECHO_JA_REGISTRADO,
            "Esta convocação já tem desfecho registrado. Corrigi-lo é suceder a convocação, com "
            "motivo — e não sobrescrever o que foi respondido.",
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
