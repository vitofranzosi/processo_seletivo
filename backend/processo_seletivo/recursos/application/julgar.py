"""A decisão de mérito — e, na correção fixada, o Resultado sucessor **na mesma transação**.

```text
require_permission(recurso:julgar)                          ← fora da transação
────────────────────────────────────────────────────────────
abre transação
  select_for_update no ProcessoSeletivo   ← serializa com emitir, publicar, consolidar
  reavalia autorização e as cinco perguntas do impedimento  ← FR-043
  revalida a assinatura do que foi lido                     ← FR-100
  reserve(chave)
  grava a DecisaoRecurso, imutável
  se CORRECAO_FIXADA:
      lê e trava o Resultado vigente do par
      verifica non reformatio contra ele                    ← FR-070; pior ⇒ indeferimento
      cria EXATAMENTE UM sucessor, citando-o e citando a decisão
  se REAVALIACAO_DETERMINADA:
      nenhum sucessor; a decisão declara o efeito e cita o Resultado protegido
  se PROVIDENCIA_A_JUSANTE ou INDEFERIDO:
      nenhum efeito sobre Resultado
  audita — um evento por agregado
  finish(chave)
────────────────────────────────────────────────────────────
qualquer invariante que falhe derruba a transação inteira:
não fica decisão sem efeito, nem efeito sem decisão.
```

**A atomicidade é a substância, e não um detalhe de implementação.** Decisão sem sucessor é um
deferimento que o candidato lê e que não valeu; sucessor sem decisão é um Resultado alterado sem
fonte jurídica. As duas metades são inúteis, e a única forma de nunca ter uma delas é nunca gravar
uma sem a outra (FR-056).

**A quarta espécie nomeia a providência e não a executa** (FR-049). Executá-la aqui daria a quem
julga a autoridade da 015 e da 017 — que é exatamente a separação que a D-005 protege. O
cumprimento se prova pela citação que o ato sucessor carrega, quando ele é publicado.
"""

from django.db import IntegrityError, transaction

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.publicacoes.application.selectors import selecao_publica
from processo_seletivo.recursos.application.porta import exigir_elegibilidade, travar
from processo_seletivo.recursos.domain.consequencia import derivar
from processo_seletivo.recursos.domain.pejus import MENSAGEM as PIORARIA
from processo_seletivo.recursos.domain.pejus import PIORA, piora
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.idempotency import finish, reserve

PERMISSAO = "recurso:julgar"
OPERACAO = "recurso:julgar"

SEM_MOTIVACAO = "Toda decisão é motivada, inclusive o indeferimento: escreva a razão."
NAO_ADMITIDO = "Este recurso não foi admitido, ou ainda não teve a admissibilidade apreciada."
JA_JULGADO = "Este recurso já foi julgado."
RESULTADO_MUDOU = (
    "O resultado vigente desta Etapa mudou enquanto esta página estava aberta. Recarregue e "
    "confira antes de decidir."
)
SEM_RESULTADO = "Não há resultado vigente desta Etapa para corrigir."

# O que a trilha escreve de cada espécie: o **efeito**, em uma frase, e nada do conteúdo.
ESPECIE_NA_TRILHA = {
    DecisaoRecurso.Especie.INDEFERIDO: "indeferido",
    DecisaoRecurso.Especie.CORRECAO_FIXADA: "deferido com correção fixada",
    DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA: "deferido com reavaliação determinada",
    DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE: "deferido com providência a jusante",
}

COM_EFEITO = {
    DecisaoRecurso.Especie.CORRECAO_FIXADA,
    DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
}


def julgar(
    *,
    actor,
    recurso_id,
    especie,
    motivacao,
    etapa_id=None,
    pontuacao=None,
    sentido="",
    assinatura_do_resultado="",
    idempotency_key,
    correlation_id="",
):
    """Grava a decisão e o que ela produz, ou não grava nada."""
    require_permission(actor, PERMISSAO)
    if not (motivacao or "").strip():
        raise DomainError("appeal_reason_required", SEM_MOTIVACAO, 422)
    especie = _especie(especie)

    with command_context() as agora:
        peca = travar(actor, recurso_id)
        # **O impedimento é reavaliado pelo par que a decisão alcança**, e não só pelo objeto
        # atacado (FR-039, FR-043). Um recurso contra a publicação que corrige a Etapa 2 é julgado
        # sobre o Resultado da Etapa 2 — e quem o avaliou ou consolidou não pode julgá-lo.
        exigir_elegibilidade(actor, peca, etapa_id=etapa_id)
        _exigir_admissao(peca)

        reserva = reserve(
            actor=actor,
            operation=f"{OPERACAO}:{peca.pk}",
            key=idempotency_key,
            payload={
                "especie": str(especie),
                "motivacao": motivacao,
                "etapa": str(etapa_id or ""),
                "pontuacao": str(pontuacao or ""),
                "sentido": str(sentido or ""),
            },
        )
        if reserva.result_id:
            return DecisaoRecurso.objects.get(pk=reserva.result_id), None

        # **A norma da decisão é a vigente no instante do julgamento, e não a da interposição**
        # (FR-045, FR-059). Havendo Retificação entre as duas, gravar `peca.versao` faria a decisão
        # afirmar ter sido tomada sob regra que já não vale — e a consequência sairia de uma nota
        # mínima revogada. A versão que a peça cita continua registrada nela: é a regra sob a qual
        # se **recorreu**, e responde outra pergunta.
        versao = selecao_publica(edital_id=peca.inscricao.edital_id)
        protegido = _protegido(peca, especie, etapa_id, assinatura_do_resultado)
        efeito, motivo_da_regra, conclusao = _conclusao(
            peca, versao, especie, etapa_id, pontuacao, sentido
        )
        _recusar_se_piora(especie, protegido, efeito, conclusao)

        decisao = _gravar(
            recurso=peca,
            especie=especie,
            motivacao=motivacao.strip(),
            versao=versao,
            decidido_por=actor.subject,
            decidido_em=agora,
            resultado_protegido=protegido if especie in COM_EFEITO else None,
            etapa_id=etapa_id if especie in COM_EFEITO else None,
            consequencia=efeito,
            forma=conclusao.forma if conclusao is not None else "",
            pontuacao=conclusao.pontuacao if conclusao is not None else None,
            sentido=conclusao.sentido if conclusao is not None else "",
        )
        sucessor = None
        if especie == DecisaoRecurso.Especie.CORRECAO_FIXADA:
            sucessor = _superar(protegido, decisao, motivo_da_regra, agora, actor)

        auditar(
            actor=actor,
            permissao=PERMISSAO,
            operation=OPERACAO,
            aggregate=decisao,
            now=agora,
            correlation_id=correlation_id,
            # **O ato, e não a motivação nem a grandeza** (FR-094, FR-095): a trilha diz que houve
            # decisão, de que espécie e sobre qual peça. A motivação e a pontuação são conteúdo, e
            # copiá-las aqui criaria uma segunda cópia sob outro regime de acesso.
            reason=f"Recurso {peca.protocolo} julgado: {ESPECIE_NA_TRILHA[especie]}.",
            idempotency_key=idempotency_key,
        )
        if sucessor is not None:
            # **Um evento por agregado** (FR-094): a decisão e a superação são dois atos gravados,
            # e a trilha que registrasse só um deixaria a alteração do Resultado sem rastro.
            auditar(
                actor=actor,
                permissao=PERMISSAO,
                operation="resultado:superar",
                aggregate=sucessor,
                now=agora,
                correlation_id=correlation_id,
                reason=(
                    f"Resultado superado em cumprimento da decisão no recurso {peca.protocolo}."
                ),
                idempotency_key=idempotency_key,
            )
        finish(reserva, decisao, 201)
        return decisao, sucessor


def _especie(valor):
    escolhas = {str(item) for item in DecisaoRecurso.Especie}
    if str(valor) not in escolhas:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return DecisaoRecurso.Especie(str(valor))


def _exigir_admissao(peca):
    """Julgar o mérito exige juízo positivo — e a recusa acontece antes de gravar (FR-036).

    A trigger `decisao_recurso_coerente` também responde, e é ela que vale contra qualquer caminho
    de gravação. Aqui a leitura existe para que a tela receba uma frase em vez de um erro de banco.
    """
    juizo = next(iter(peca.juizos.all()), None)
    if juizo is None or not juizo.admitido:
        raise DomainError("appeal_not_admitted", NAO_ADMITIDO, 409)


def _protegido(peca, especie, etapa_id, assinatura):
    """O Resultado vigente do par, travado — e conferido contra o que a tela leu (FR-100).

    `select_for_update` porque entre ler e gravar outra consolidação pode criar sucessor do mesmo
    par; travá-lo é o que faz a corrida esperar em vez de produzir dois sucessores. A unicidade
    ainda responde no banco, e é ela a garantia — o bloqueio é o que transforma a corrida numa fila
    em vez de num erro.

    **`of=("self",)` não é enfeite.** O manager de vigência filtra por `sucessor__isnull=True`, o
    que o ORM traduz em junção externa — e o PostgreSQL recusa `FOR UPDATE` sobre o lado anulável
    de uma junção externa. Sem o `of`, o comando quebrava com `NotSupportedError` na primeira
    correção fixada; com ele, o bloqueio recai sobre a linha do Resultado, que é a que se quer
    travar.
    """
    if especie not in COM_EFEITO:
        return None
    if etapa_id is None:
        raise DomainError(
            "appeal_correction_incomplete", "A decisão precisa dizer a que Etapa se refere.", 422
        )
    vigente = (
        ResultadoEtapa.vigentes.select_for_update(of=("self",))
        .filter(inscricao_id=peca.inscricao_id, etapa_id=etapa_id)
        .first()
    )
    if vigente is None:
        raise DomainError("appeal_correction_incomplete", SEM_RESULTADO, 422)
    # **A ausência da assinatura é recusa, e não dispensa** (FR-100). Enquanto ela era opcional, um
    # `POST` que omitisse o campo decidia sobre qualquer Resultado do par — inclusive um que já
    # tivesse sido corrigido entre a leitura da tela e a confirmação.
    if str(vigente.pk) != str(assinatura or ""):
        raise DomainError("stale_stage_result", RESULTADO_MUDOU, 409)
    return vigente


def _conclusao(peca, versao, especie, etapa_id, pontuacao, sentido):
    """A consequência **derivada** da regra publicada, e nunca digitada (FR-059).

    O desfecho sem grandeza é o ramo do recurso contra Ocorrência: nem a decisão nem o sucessor
    carregam forma, pontuação ou sentido, e a consequência é declarada diretamente porque não há
    conclusão a converter. Distingui-lo pela **origem do Resultado protegido**, e não por um
    interruptor no pedido, é o que impede alguém de declarar `HABILITADA` sem grandeza numa Etapa
    que tem uma.
    """
    if especie != DecisaoRecurso.Especie.CORRECAO_FIXADA:
        return "", "", None

    protegido = _vigente_do_par(peca, etapa_id)
    if protegido is not None and protegido.forma == "":
        efeito = ResultadoEtapa.Consequencia.HABILITADA
        return str(efeito), "recurso deferido: a ocorrência não subsiste", None

    efeito, motivo, conclusao = derivar(
        versao=versao, etapa_id=etapa_id, pontuacao=pontuacao, sentido=sentido
    )
    return str(efeito), motivo, conclusao


def _vigente_do_par(peca, etapa_id):
    return ResultadoEtapa.vigentes.filter(inscricao_id=peca.inscricao_id, etapa_id=etapa_id).first()


def _recusar_se_piora(especie, protegido, efeito, conclusao):
    """A correção que pioraria não vira sucessor — e **nenhum** sucessor nasce (FR-070).

    A recusa é da decisão inteira, e não só do efeito: gravar a decisão e omitir o sucessor deixaria
    um deferimento sem efeito, que é a metade que a atomicidade existe para impedir. Quem quer
    manter o resultado como está indefere, e é isso que a espécie `INDEFERIDO` diz.
    """
    if especie != DecisaoRecurso.Especie.CORRECAO_FIXADA or protegido is None:
        return
    if piora(
        protegido=protegido,
        consequencia=efeito,
        pontuacao=conclusao.pontuacao if conclusao is not None else None,
    ):
        raise DomainError(PIORA, PIORARIA, 422)


def _gravar(**campos):
    """A segunda barreira: `uq_decisao_por_recurso` responde a dois julgadores simultâneos."""
    try:
        with transaction.atomic():
            return DecisaoRecurso.objects.create(**campos)
    except IntegrityError as exc:
        raise DomainError("appeal_already_judged", JA_JULGADO, 409) from exc


def _superar(protegido, decisao, motivo_da_regra, agora, actor):
    """O sucessor, com origem `RECURSO` e **sem citar Avaliação nenhuma** (FR-057, FR-058).

    Ele não é uma correção do anterior: é um Resultado novo, que cita o que superou e a decisão que
    o autorizou. O anterior permanece íntegro, com a pontuação, a consequência e o motivo que
    afirmou — e é isso que distingue superar de reescrever (D-003 da decisão C).

    `consolidado_em` é o instante do julgamento, e a trigger exige que ele seja posterior ao do
    superado: sem a cronologia monotônica, "o mais recente" e "o vigente" poderiam divergir na
    auditoria.
    """
    motivo_da_superacao = (
        f"Resultado corrigido em cumprimento da decisão no recurso {decisao.recurso.protocolo}"
    )
    try:
        with transaction.atomic():
            return ResultadoEtapa.objects.create(
                inscricao_id=protegido.inscricao_id,
                edital_id=protegido.edital_id,
                etapa_id=protegido.etapa_id,
                origem=ResultadoEtapa.Origem.RECURSO,
                avaliacao=None,
                versao=decisao.versao,
                forma=decisao.forma,
                pontuacao=decisao.pontuacao,
                sentido=decisao.sentido,
                consequencia=decisao.consequencia,
                motivo=motivo_da_regra or motivo_da_superacao,
                consolidado_em=max(agora, protegido.consolidado_em),
                consolidado_por=actor.subject,
                resultado_anterior=protegido,
                motivo_da_superacao=motivo_da_superacao,
                decisao=decisao,
            )
    except IntegrityError as exc:
        # `uq_resultado_sucessor_unico` — dois deferimentos sobre o mesmo Resultado. A corrida é
        # resolvida no banco, e não por leitura prévia, exatamente como `uq_ato_sucessor_unico` já
        # resolve a emissão simultânea de dois sucessores do mesmo ato (FR-099).
        raise DomainError("stale_stage_result", RESULTADO_MUDOU, 409) from exc
