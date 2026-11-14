"""A retenção do arquivo de vídeo (166, FR-7146 a FR-7149, D-008).

**O prazo não tem valor padrão.** É a P-10 — a guarda do vídeo pede o arquivo institucional e o
encarregado de dados —, e um número escrito aqui seria o sistema decidindo a retenção de dado sensível
por quem ainda não decidiu. Sem o prazo no ambiente, nada se elimina.

**Elimina-se o arquivo, e não o registro.** O ato é o Resultado da Etapa, append-only, e o vídeo era
a evidência dele (R-23 do estudo): o resumo, o tamanho, a duração, as marcas, as aberturas e a trilha
ficam, e a eliminação ganha a linha dela. Não contraria o "nada se exclui" do projeto, que é sobre
dado normativo.

**Contado do encerramento do Edital**, o único fim de certame que o sistema registra. Se a P-10
escolher outro marco — o trânsito do último recurso, por exemplo —, ele entra como parâmetro.
"""

import os
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.verificacao.application import envio
from processo_seletivo.verificacao.models import EliminacaoDoVideo, VideoDaVerificacao

ELIMINAR = "ELIMINAR_VIDEO_DA_VERIFICACAO"
SEM_PRAZO = (
    "O prazo de retenção do vídeo ainda não foi decidido (P-10): defina "
    "VERIFICACAO_POR_VIDEO_RETENCAO_DIAS depois da decisão do arquivo institucional e do "
    "encarregado de dados."
)


def prazo_em_dias():
    return getattr(settings, "VERIFICACAO_POR_VIDEO_RETENCAO_DIAS", None)


def encerramento(edital):
    """O instante do evento `ENCERRAR` do Edital, ou `None`."""
    from processo_seletivo.auditoria.models import RegistroAuditoria

    registro = (
        RegistroAuditoria.objects.filter(
            aggregate_type="Edital", aggregate_id=edital.pk, operation="ENCERRAR"
        )
        .order_by("occurred_at")
        .first()
    )
    return registro.occurred_at if registro else None


def elegiveis(edital):
    """`(prazo, encerramento, vídeos)` — ou a recusa que diz por que nada se elimina ainda."""
    from processo_seletivo.processos.models import Edital

    prazo = prazo_em_dias()
    if prazo is None:
        raise DomainError("retencao_sem_prazo", SEM_PRAZO, 409)
    if edital.status != Edital.Status.ENCERRADO:
        raise DomainError(
            "edital_nao_encerrado",
            "O Edital não está encerrado, e a retenção conta do encerramento.",
            409,
        )
    encerrado_em = encerramento(edital)
    if encerrado_em is None:
        raise DomainError(
            "encerramento_sem_registro",
            "O encerramento do Edital não está na trilha, e sem ele o prazo não tem de onde contar.",
            409,
        )
    liberada = encerrado_em + timedelta(days=prazo)
    if timezone.now() < liberada:
        raise DomainError(
            "dentro_do_prazo",
            f"A eliminação só cabe a partir de {timezone.localtime(liberada):%d/%m/%Y}, {prazo} dias "
            f"depois do encerramento do Edital.",
            409,
        )
    videos = list(
        VideoDaVerificacao.objects.filter(edital=edital, eliminacao__isnull=True).order_by(
            "recebido_em", "id"
        )
    )
    return prazo, encerrado_em, videos


def eliminar(*, edital, actor):
    """Elimina o arquivo de cada vídeo do Edital, e registra cada eliminação. Devolve quantos."""
    from processo_seletivo.auditoria.application import record_event
    from processo_seletivo.shared.application.commands import command_context

    prazo, encerrado_em, videos = elegiveis(edital)
    eliminados = 0
    for video in videos:
        with command_context() as agora:
            EliminacaoDoVideo.objects.create(
                video=video, eliminado_em=agora, prazo_em_dias=prazo, encerramento_em=encerrado_em
            )
            record_event(
                actor=actor,
                permission=actor.subject,
                operation=ELIMINAR,
                aggregate=video,
                now=agora,
                correlation_id="",
                reason=f"Arquivo eliminado pelo prazo de retenção de {prazo} dias.",
                new_state="",
                new_revision=None,
                detalhe={"sha256": video.sha256, "prazo_em_dias": prazo},
            )
        # O arquivo sai depois do registro gravado: se a remoção falhar, o registro diz o que devia
        # ter saído, e a próxima rodada não o repete — quem confere é o operador, pelo disco.
        try:
            os.remove(envio.caminho(video.arquivo))
        except FileNotFoundError:
            pass
        eliminados += 1
    return eliminados
