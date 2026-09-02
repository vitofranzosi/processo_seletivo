"""Gravar, concluir — e a versão que governou o ato.

**Salvar e concluir são atos distintos** (FR-031, FR-032). O rascunho é gravado sem exigir nada
além da pontuação bem formada; concluir é explícito, valida contra a regra publicada e encerra.

**A concorrência é do avaliador, e não do contêiner.** Aqui não há invariante que atravesse linhas:
é uma Avaliação, de uma Atribuição, e `compare_and_swap` sobre a revisão basta. Duas abas do mesmo
avaliador não se sobrescrevem em silêncio, e concluir sobre uma avaliação que a presidência reabriu
no intervalo é recusado pela mesma comparação (FR-081, FR-082).

**A versão é lida dentro da transação que grava** (FR-096). Ler para avisar e outra para gravar
produziria uma Avaliação que afirma obedecer a uma regra contra a qual nunca foi verificada — pior
do que não registrar versão alguma.
"""

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.avaliacoes.domain import pontuacao as regras
from processo_seletivo.avaliacoes.domain.autorizacao import pode_avaliar_inscricao
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, ConclusaoAvaliacao
from processo_seletivo.comissoes.domain.autorizacao import pode_atuar_na_etapa
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.concurrency import compare_and_swap

GRAVAR = "AVALIACAO_GRAVAR"
CONCLUIR = "AVALIACAO_CONCLUIR"
BASE_DA_MESA = "avaliacao:atribuida"


def _nao_encontrado():
    return DomainError("not_found", "Recurso não encontrado.", 404)


def _obsoleta():
    return DomainError("stale_revision", "A revisão informada está obsoleta.", 412)


def _autorizar(ator, edital, etapa_id, inscricao_id):
    atribuicao = pode_avaliar_inscricao(ator, edital, etapa_id, inscricao_id)
    if atribuicao is None:
        raise _nao_encontrado()
    return atribuicao


def _travar_e_reautorizar(ator, edital, etapa_id, atribuicao):
    """Bloqueia a Atribuição e **reavalia a autorização depois do bloqueio**.

    É a mesma razão que levou a 011 a reautorizar depois do `select_for_update`, aplicada ao par
    que esta feature precisa serializar: **concluir** e **remover atribuição** disputam a mesma
    linha, e sem trava comum a remoção pode ler "pendente", inativar, e a conclusão gravar depois.
    O resultado seria uma avaliação concluída **e** inelegível pela via comum — exatamente o efeito
    sem ato que FR-092 existe para impedir.

    Quem chega depois encontra a Atribuição já inativa e é recusado; quem chega antes conclui, e a
    remoção passa a ver a conclusão e recusa com o motivo nomeado.
    """
    travada = (
        Atribuicao.objects.select_for_update(of=("self",))
        .filter(pk=atribuicao.pk, ativo=True)
        .first()
    )
    if travada is None:
        raise _nao_encontrado()
    if not pode_atuar_na_etapa(ator, edital, etapa_id):
        raise _nao_encontrado()
    return travada


def _avaliacao_de(atribuicao, ator):
    """A Avaliação daquela Atribuição, criada no primeiro salvamento.

    Nasce rascunho, e a tripla que a identifica é copiada **uma vez** — é ela que sustenta a
    unicidade de conclusão por pessoa, inscrição e Etapa (FR-074).
    """
    # `get_or_create` porque a primeira gravação **corre**: duas abas abertas na mesma inscrição
    # disputam o `OneToOne`, e "consultar e depois criar" faria uma delas receber `IntegrityError`
    # — erro interno onde deveria haver a recusa por revisão obsoleta. O Django trata a colisão
    # relendo, e as duas seguem para a comparação de revisão, que é quem decide.
    avaliacao, _ = Avaliacao.objects.get_or_create(
        atribuicao=atribuicao,
        defaults={
            "identity_subject": ator.subject,
            "etapa_id": atribuicao.etapa_id,
            "inscricao_id": atribuicao.inscricao_id,
        },
    )
    return avaliacao


def _versao_e_etapa(edital, etapa_id, agora):
    """A Versão Consolidada vigente **neste instante**, e a Etapa **dentro dela**.

    Uma leitura só, e a Etapa extraída do conteúdo dessa versão — não de uma segunda consulta.
    Resolver a Etapa por fora reabriria a janela que FR-096 fecha: uma Retificação consolidada
    entre as duas leituras faria a pontuação ser validada pela Etapa nova e a versão **antiga**
    ficar gravada, produzindo uma Avaliação que afirma obedecer a uma regra contra a qual nunca
    foi verificada.
    """
    versao = effective_version(edital_id=edital.id, at=agora)
    etapa = next(
        (
            item
            for item in versao.content.get("stages") or []
            if str(item.get("id")) == str(etapa_id)
        ),
        None,
    )
    if etapa is None:
        raise _nao_encontrado()
    return versao, etapa


def gravar(
    *, ator, edital, etapa_id, inscricao_id, pontuacao, parecer, expected_revision, correlation_id
):
    """O rascunho, gravado sem exigir conclusão (FR-031)."""
    atribuicao = _autorizar(ator, edital, etapa_id, inscricao_id)
    with command_context() as agora:
        atribuicao = _travar_e_reautorizar(ator, edital, etapa_id, atribuicao)
        avaliacao = _avaliacao_de(atribuicao, ator)
        if avaliacao.estado == Avaliacao.Estado.CONCLUIDA:
            # Concluída é imutável para o avaliador (FR-035). Reabrir é ato da presidência.
            raise DomainError(
                "avaliacao_concluida",
                "Esta avaliação foi concluída e não pode mais ser alterada por você. "
                "A reabertura é ato da presidência.",
                409,
            )
        versao, etapa = _versao_e_etapa(edital, etapa_id, agora)
        # O rascunho valida a **forma**, e não a regra publicada: quem está no meio do trabalho
        # pode salvar um valor que ainda não decidiu, e cobrar a máxima aqui obrigaria a concluir
        # para descobrir se o número passa. A regra normativa é cobrada na conclusão, que é o ato
        # com efeito (FR-031, FR-032, FR-033).
        valor = None if pontuacao in (None, "") else regras.normalizar(pontuacao)
        nova = compare_and_swap(
            Avaliacao.objects,
            pk=avaliacao.pk,
            expected_revision=expected_revision,
            pontuacao=valor,
            parecer=parecer or "",
        )
        auditar(
            actor=ator,
            permissao=BASE_DA_MESA,
            operation=GRAVAR,
            aggregate=avaliacao,
            now=agora,
            correlation_id=correlation_id,
            reason=_motivo(atribuicao),
        )
        avaliacao.refresh_from_db()
        return avaliacao, nova


def concluir(
    *,
    ator,
    edital,
    etapa_id,
    inscricao_id,
    pontuacao,
    parecer,
    expected_revision,
    versao_reconhecida,
    correlation_id,
):
    """Ato explícito, distinto de salvar (FR-032).

    `versao_reconhecida` é o que o avaliador viu quando escreveu. Se a versão vigente mudou desde
    então, a conclusão é recusada **antes** de gravar: ele reconhece a mudança e conclui de novo,
    contra a regra nova (FR-073). Descobrir a Retificação depois, no parecer de outra pessoa, é o
    que isso existe para impedir.
    """
    atribuicao = _autorizar(ator, edital, etapa_id, inscricao_id)
    with command_context() as agora:
        # A trava é aqui, e não só na gravação: é a conclusão que a remoção comum não pode
        # atropelar (FR-092).
        atribuicao = _travar_e_reautorizar(ator, edital, etapa_id, atribuicao)
        avaliacao = _avaliacao_de(atribuicao, ator)
        if avaliacao.estado == Avaliacao.Estado.CONCLUIDA:
            raise DomainError(
                "avaliacao_concluida",
                "Esta avaliação já foi concluída. A reabertura é ato da presidência.",
                409,
            )
        versao, etapa = _versao_e_etapa(edital, etapa_id, agora)
        # **Obrigatório, e não opcional.** Deixá-lo cair quando ausente permitiria concluir sem
        # reconhecimento apenas omitindo o campo do envio — desligar FR-073 pelo cliente.
        if not versao_reconhecida:
            raise DomainError(
                "versao_nao_reconhecida",
                "A conclusão precisa declarar a versão do Edital contra a qual foi escrita. "
                "Recarregue a página e conclua novamente.",
                422,
                campo="versao_reconhecida",
            )
        if str(versao_reconhecida) != str(versao.id):
            raise DomainError(
                "versao_mudou",
                "O Edital foi retificado enquanto você avaliava. Confira a pontuação máxima e a "
                "nota mínima que passaram a valer e confirme a conclusão.",
                409,
            )
        valor = regras.validar(pontuacao, etapa)
        texto = (parecer or "").strip()
        if regras.exige_parecer(valor, etapa) and not texto:
            raise DomainError(
                "parecer_obrigatorio",
                "Esta Etapa é eliminatória e a pontuação ficou abaixo da nota mínima: o parecer "
                "é obrigatório, porque é ele que responde a um recurso.",
                422,
                campo="parecer",
            )
        nova = compare_and_swap(
            Avaliacao.objects,
            pk=avaliacao.pk,
            expected_revision=expected_revision,
            estado=Avaliacao.Estado.CONCLUIDA,
            pontuacao=valor,
            parecer=texto,
            # **A versão validada é a versão gravada** (FR-071, FR-096).
            versao=versao,
            concluida_em=agora,
            concluida_por=ator.subject,
        )
        # A conclusão preservada: reabrir não destrói o que foi concluído (FR-094).
        ConclusaoAvaliacao.objects.create(
            avaliacao=avaliacao,
            ordem=avaliacao.conclusoes.count() + 1,
            pontuacao=valor,
            parecer=texto,
            versao=versao,
            concluida_em=agora,
            concluida_por=ator.subject,
        )
        auditar(
            actor=ator,
            permissao=BASE_DA_MESA,
            operation=CONCLUIR,
            aggregate=avaliacao,
            now=agora,
            correlation_id=correlation_id,
            reason=_motivo(atribuicao),
        )
        avaliacao.refresh_from_db()
        return avaliacao, nova


def _motivo(atribuicao):
    """O que a trilha guarda do ato: quem, qual inscrição — **nunca** a nota nem o parecer.

    A trilha registra que o ato aconteceu; o conteúdo vive na Avaliação, que é o registro do
    domínio (FR-054). Por isso o motivo é montado aqui, e não recebido de fora.
    """
    inscricao = atribuicao.inscricao
    return f"inscrição {inscricao.protocolo or inscricao.id}"


def eventos_da_avaliacao(avaliacao):
    """Os atos registrados sobre esta Avaliação — para a trilha e para os testes."""
    return RegistroAuditoria.objects.filter(
        aggregate_type="Avaliacao", aggregate_id=avaliacao.pk
    ).order_by("occurred_at")


REABRIR = "AVALIACAO_REABRIR"


def reabrir(
    *, actor, processo_id, avaliacao_id, motivo, expected_revision, idempotency_key, correlation_id
):
    """Ato da presidência, com motivo, registrado (FR-036).

    Recurso e erro material existem; o que não pode existir é reabertura silenciosa. Por isso o
    invólucro de comando da 011 — que bloqueia, reavalia a autorização depois do bloqueio e
    reserva a idempotência — e por isso o `AtoAdministrativo` com motivo obrigatório.

    **Reabrir não destrói o que foi concluído** (FR-094): a `ConclusaoAvaliacao` daquela conclusão
    já está gravada e é append-only, de modo que "o que aquela pessoa havia concluído antes" segue
    sendo uma consulta, e não arqueologia de trilha.
    """
    from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
    from processo_seletivo.comissoes.application.comissao import identificador

    texto = (motivo or "").strip()
    if not texto:
        raise DomainError(
            "motivo_obrigatorio",
            "A reabertura exige motivo: é ele que separa recurso e erro material de reabertura "
            "silenciosa.",
            422,
            campo="motivo",
        )
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="avaliacao:reabrir",
        # O motivo e a revisão entram no conteúdo da chave: sem eles, reenviar a mesma chave com
        # outro motivo seria tratado como repetição, e o ato registrado não seria o que se pediu
        # (FR-084).
        payload={
            "avaliacao": str(avaliacao_id),
            "motivo": texto,
            "revisao": expected_revision,
        },
        idempotency_key=idempotency_key,
    ) as ctx:
        avaliacao = (
            Avaliacao.objects.filter(
                pk=identificador(avaliacao_id), atribuicao__edital__processo=ctx.processo
            )
            .select_related("atribuicao")
            .first()
        )
        if avaliacao is None:
            raise nao_encontrado()
        if ctx.repetido:
            return avaliacao
        if avaliacao.estado != Avaliacao.Estado.CONCLUIDA:
            # Transição inválida, e não "nada a fazer": reabrir um rascunho não tem significado, e
            # responder sucesso faria a tela afirmar um ato que não aconteceu (FR-083).
            raise DomainError(
                "transicao_invalida",
                "Só uma avaliação concluída pode ser reaberta.",
                409,
            )
        compare_and_swap(
            Avaliacao.objects,
            pk=avaliacao.pk,
            expected_revision=expected_revision,
            estado=Avaliacao.Estado.RASCUNHO,
            concluida_em=None,
            concluida_por="",
            # A versão sai do registro **corrente**: o que governou a conclusão anterior está na
            # `ConclusaoAvaliacao`, e mantê-la aqui afirmaria uma conclusão que já não existe.
            versao=None,
        )
        # A Avaliação volta a ser trabalho pendente **na Mesa de quem ainda tem a Atribuição**.
        # Reabrir uma cuja Atribuição já foi inativada é possível e não ressuscita o acesso: a
        # conjunção da autorização continua valendo, e a avaliação segue inelegível até que a
        # presidência redistribua (FR-075, D-004).
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=REABRIR,
            aggregate=avaliacao,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=texto,
            idempotency_key=idempotency_key,
            com_ato_administrativo=True,
        )
        avaliacao.refresh_from_db()
        ctx.concluir(avaliacao, 200)
        return avaliacao
