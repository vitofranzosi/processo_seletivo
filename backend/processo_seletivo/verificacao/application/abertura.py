"""Abrir o vídeo é ato; assistir é a entrega desse ato (166, FR-7127 a FR-7131, D-007).

**Uma abertura, um evento.** O reprodutor faz dezenas de pedidos com `Range` por sessão de
reprodução, e registrar cada um afogaria a trilha; não registrar nenhum deixaria a leitura de dado
sensível sem rastro. Por isso a abertura é um `POST` que confere o resumo do arquivo, grava a
`AberturaDoVideo`, registra **um** evento e põe o identificador da abertura na sessão; os pedidos do
reprodutor apresentam esse identificador, e não registram nada.

**Quem abre**: na comissão, só quem está alocado à Etapa e tem a Atribuição ativa daquela inscrição
(FR-7129) — a mesma composição que a Mesa usa para o documento; no portal, só o titular (FR-7127). A
abertura do titular não encerra a troca: só a da comissão (FR-7124).
"""

import hashlib
import os

from django.db import transaction

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.verificacao.application import disponibilidade, envio
from processo_seletivo.verificacao.infrastructure import entrega
from processo_seletivo.verificacao.models import AberturaDoVideo, VideoDaVerificacao

VISUALIZAR = "VISUALIZAR_VIDEO_DA_VERIFICACAO"
INTEGRIDADE = "VIDEO_DA_VERIFICACAO_INTEGRIDADE"
PERMISSAO_DA_MESA = "avaliacao:atribuida"
SESSAO = "verificacao_aberturas"
# Quantas aberturas a sessão guarda: a Mesa vai de inscrição em inscrição, e a lista não cresce sem
# fim. A mais antiga sai; reabrir é um clique, e registra.
_NA_SESSAO = 20


def _nao_encontrado():
    return DomainError("not_found", "Recurso não encontrado.", 404)


def eliminado(video) -> bool:
    return hasattr(video, "eliminacao")


def _recusar_se_eliminado(video):
    if eliminado(video):
        data = video.eliminacao.eliminado_em
        raise DomainError(
            "video_eliminado",
            f"O arquivo deste vídeo foi eliminado em {data:%d/%m/%Y}, conforme o prazo de "
            "retenção. O resumo e a duração continuam registrados.",
            409,
        )


def _resumo(video) -> str | None:
    """O resumo do arquivo no disco, ou `None` se ele não está lá."""
    sha = hashlib.sha256()
    try:
        with open(envio.caminho(video.arquivo), "rb") as arquivo:
            for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
                sha.update(bloco)
    except OSError:
        return None
    return sha.hexdigest()


def _conferir_integridade(video, *, actor, permission, aggregate, correlation_id):
    """A cópia no disco é a que foi recebida; senão, o fato vai à trilha e a entrega é recusada.

    O evento é gravado **fora** da transação do ato, que a recusa desfaz: é o mesmo cuidado da
    entrega mediada de hoje, em que a divergência fica registrada mesmo sem abertura.
    """
    from django.utils import timezone

    from processo_seletivo.auditoria.application import record_event

    calculado = _resumo(video)
    if calculado == video.sha256:
        return
    record_event(
        actor=actor,
        permission=permission,
        operation=INTEGRIDADE,
        aggregate=aggregate,
        now=timezone.now(),
        correlation_id=correlation_id,
        reason=f"O arquivo do vídeo {video.id} não confere com o resumo registrado.",
        new_state="",
        new_revision=None,
        detalhe={"video": str(video.id), "ausente": calculado is None},
    )
    raise DomainError(
        "video_indisponivel",
        "O arquivo do vídeo não está disponível agora. A ocorrência foi registrada.",
        409,
    )


def _guardar_na_sessao(request, abertura):
    aberturas = [item for item in request.session.get(SESSAO, []) if item != str(abertura.id)]
    aberturas.append(str(abertura.id))
    request.session[SESSAO] = aberturas[-_NA_SESSAO:]


def da_sessao(request, abertura_id) -> bool:
    return str(abertura_id) in request.session.get(SESSAO, [])


def abrir_pela_comissao(request, *, ator, edital, etapa_id, inscricao_id, correlation_id):
    """A abertura do membro alocado com a Atribuição (FR-7129, FR-7130). Devolve a abertura."""
    from django.utils import timezone

    from processo_seletivo.auditoria.application import record_event
    from processo_seletivo.avaliacoes.domain.autorizacao import pode_avaliar_inscricao
    from processo_seletivo.inscricoes.models import Inscricao

    atribuicao = pode_avaliar_inscricao(ator, edital, etapa_id, inscricao_id)
    if atribuicao is None:
        raise _nao_encontrado()
    video = disponibilidade.video_vigente(
        edital=edital, etapa_id=etapa_id, inscricao_id=inscricao_id
    )
    if video is None:
        raise _nao_encontrado()
    _recusar_se_eliminado(video)
    _conferir_integridade(
        video,
        actor=ator,
        permission=PERMISSAO_DA_MESA,
        aggregate=atribuicao,
        correlation_id=correlation_id,
    )
    with transaction.atomic():
        # A trava da inscrição é a da conclusão do envio: a troca e a primeira abertura se
        # enfileiram, e a troca que chegar depois encontra a abertura e é recusada (FR-7152).
        Inscricao.objects.select_for_update(of=("self",)).filter(pk=inscricao_id).first()
        vigente = disponibilidade.video_vigente(
            edital=edital, etapa_id=etapa_id, inscricao_id=inscricao_id
        )
        if vigente is None or vigente.pk != video.pk:
            raise DomainError(
                "video_trocado",
                "O candidato trocou o vídeo agora há pouco. Abra de novo para ver o vigente.",
                409,
            )
        agora = timezone.now()
        abertura = AberturaDoVideo.objects.create(
            video=video, pessoa=ator.subject, papel=AberturaDoVideo.Papel.COMISSAO, aberta_em=agora
        )
        record_event(
            actor=ator,
            permission=PERMISSAO_DA_MESA,
            operation=VISUALIZAR,
            # Na Atribuição, como a consulta ao documento na Mesa: é a trilha da avaliação que a
            # comissão lê, e o vídeo é lido para avaliar (FR-7130).
            aggregate=atribuicao,
            now=agora,
            correlation_id=correlation_id,
            reason=f"video:{video.id}",
            new_state="",
            new_revision=None,
            detalhe={"papel": "COMISSAO", "video": str(video.id), "sha256": video.sha256},
        )
    _guardar_na_sessao(request, abertura)
    return abertura


def abrir_pelo_titular(request, *, identidade, inscricao_id, etapa_id, correlation_id):
    """A abertura do titular (FR-7127). Não encerra a troca."""
    from django.utils import timezone

    from processo_seletivo.auditoria.application import record_event
    from processo_seletivo.inscricoes.application.rascunho import ator_do_candidato

    inscricao, _etapa, situacao = envio.contexto_do_titular(
        identidade=identidade, inscricao_id=inscricao_id, etapa_id=etapa_id
    )
    video = situacao.video
    if video is None:
        raise _nao_encontrado()
    _recusar_se_eliminado(video)
    ator = ator_do_candidato(identidade, inscricao.edital)
    _conferir_integridade(
        video, actor=ator, permission="", aggregate=video, correlation_id=correlation_id
    )
    with transaction.atomic():
        agora = timezone.now()
        abertura = AberturaDoVideo.objects.create(
            video=video,
            pessoa=identidade.subject,
            papel=AberturaDoVideo.Papel.TITULAR,
            aberta_em=agora,
        )
        record_event(
            actor=ator,
            permission="",
            operation=VISUALIZAR,
            aggregate=video,
            now=agora,
            correlation_id=correlation_id,
            reason="O titular assistiu ao próprio vídeo.",
            new_state="",
            new_revision=None,
            detalhe={"papel": "TITULAR", "video": str(video.id)},
        )
    _guardar_na_sessao(request, abertura)
    return abertura


def _abertura(request, abertura_id, *, pessoa, papel, filtro):
    if not da_sessao(request, abertura_id):
        raise _nao_encontrado()
    abertura = (
        AberturaDoVideo.objects.select_related("video", "video__eliminacao")
        .filter(pk=abertura_id, pessoa=pessoa, papel=papel, **filtro)
        .first()
    )
    if abertura is None or eliminado(abertura.video):
        raise _nao_encontrado()
    return abertura


def entregar_a_comissao(request, *, ator, edital, etapa_id, inscricao_id, abertura_id):
    """Os bytes de uma abertura desta sessão, sem evento; a autorização é relida (FR-7129)."""
    from processo_seletivo.avaliacoes.domain.autorizacao import pode_avaliar_inscricao

    if pode_avaliar_inscricao(ator, edital, etapa_id, inscricao_id) is None:
        raise _nao_encontrado()
    abertura = _abertura(
        request,
        abertura_id,
        pessoa=ator.subject,
        papel=AberturaDoVideo.Papel.COMISSAO,
        filtro={
            "video__edital": edital,
            "video__etapa_id": etapa_id,
            "video__inscricao_id": inscricao_id,
        },
    )
    return _entregar(request, abertura.video)


def entregar_ao_titular(request, *, identidade, inscricao_id, etapa_id, abertura_id):
    envio.contexto_do_titular(identidade=identidade, inscricao_id=inscricao_id, etapa_id=etapa_id)
    abertura = _abertura(
        request,
        abertura_id,
        pessoa=identidade.subject,
        papel=AberturaDoVideo.Papel.TITULAR,
        filtro={"video__inscricao_id": inscricao_id, "video__etapa_id": etapa_id},
    )
    return _entregar(request, abertura.video)


def _entregar(request, video: VideoDaVerificacao):
    caminho = envio.caminho(video.arquivo)
    if not os.path.exists(caminho):
        raise _nao_encontrado()
    return entrega.entregar(request, caminho=caminho, formato=video.formato)


def abriu(*, video, pessoa) -> bool:
    """O membro abriu este vídeo — a condição de concluir o parecer pelo vídeo (FR-7134)."""
    return AberturaDoVideo.objects.filter(
        video=video, pessoa=pessoa, papel=AberturaDoVideo.Papel.COMISSAO
    ).exists()
