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
from processo_seletivo.avaliacoes.models import Avaliacao, ConclusaoAvaliacao
from processo_seletivo.comissoes.domain.etapas import etapa_vigente
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


def _avaliacao_de(atribuicao, ator):
    """A Avaliação daquela Atribuição, criada no primeiro salvamento.

    Nasce rascunho, e a tripla que a identifica é copiada **uma vez** — é ela que sustenta a
    unicidade de conclusão por pessoa, inscrição e Etapa (FR-074).
    """
    avaliacao = getattr(atribuicao, "avaliacao", None)
    if avaliacao is not None:
        return avaliacao
    return Avaliacao.objects.create(
        atribuicao=atribuicao,
        identity_subject=ator.subject,
        etapa_id=atribuicao.etapa_id,
        inscricao_id=atribuicao.inscricao_id,
    )


def _versao_e_etapa(edital, etapa_id, agora):
    """A Versão Consolidada vigente **neste instante**, e a Etapa dentro dela.

    Lidas juntas e uma vez só: é a mesma versão que valida a pontuação e que fica gravada na
    Avaliação, e é isso que FR-096 exige.
    """
    versao = effective_version(edital_id=edital.id, at=agora)
    etapa = etapa_vigente(edital, etapa_id)
    if etapa is None:
        raise _nao_encontrado()
    return versao, etapa


def gravar(
    *, ator, edital, etapa_id, inscricao_id, pontuacao, parecer, expected_revision, correlation_id
):
    """O rascunho, gravado sem exigir conclusão (FR-031)."""
    atribuicao = _autorizar(ator, edital, etapa_id, inscricao_id)
    with command_context() as agora:
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
        # O rascunho valida a **forma**, e não a regra inteira: quem está no meio do trabalho
        # pode salvar um valor que ainda não decidiu, e recusá-lo aqui obrigaria a concluir para
        # descobrir. A regra publicada é cobrada na conclusão, que é o ato com efeito.
        valor = None if pontuacao in (None, "") else regras.validar(pontuacao, etapa)
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
    versao_reconhecida=None,
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
        avaliacao = _avaliacao_de(atribuicao, ator)
        if avaliacao.estado == Avaliacao.Estado.CONCLUIDA:
            raise DomainError(
                "avaliacao_concluida",
                "Esta avaliação já foi concluída. A reabertura é ato da presidência.",
                409,
            )
        versao, etapa = _versao_e_etapa(edital, etapa_id, agora)
        if versao_reconhecida is not None and str(versao_reconhecida) != str(versao.id):
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
