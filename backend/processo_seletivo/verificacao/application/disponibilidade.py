"""O estado do meio de uma inscrição numa Etapa que admite o vídeo (166, `data-model.md`, D-004).

**Derivado, e não guardado.** O meio sai do vídeo vigente, das aberturas da comissão, do
encaminhamento, dos pareceres e do Resultado — todos registros que já existem. Uma coluna de estado
seria a segunda fonte, livre para divergir da primeira justamente na transição que importa: a que
decide se um parecer é pelo vídeo ou ao vivo.

**Em modo vídeo** = vídeo vigente e sem encaminhamento. Nesse modo, todo parecer concluído é pelo
vídeo (research D-004), e a deliberação não produz "não confirmada" (FR-7139).
"""

from dataclasses import dataclass, field
from datetime import timedelta
from uuid import UUID

from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.verificacao.domain import admissao
from processo_seletivo.verificacao.models import (
    AberturaDoVideo,
    EncaminhamentoAoVivo,
    VideoDaVerificacao,
)

INDISPONIVEL = "INDISPONIVEL"
PODE_GRAVAR = "PODE_GRAVAR"
RECEBIDO = "RECEBIDO"
EM_ANALISE = "EM_ANALISE"
ENCAMINHADA = "ENCAMINHADA"
AO_VIVO = "AO_VIVO"

# A tolerância depois do fim do período para concluir o envio já iniciado (FR-7126): a última parte
# de quem começou às 23h59 não se perde por segundos, e nenhum envio novo começa depois do fim.
TOLERANCIA = timedelta(hours=1)


@dataclass
class Situacao:
    """O que o titular e as telas leem da verificação por vídeo de uma inscrição numa Etapa."""

    estado: str
    etapa: dict
    video: VideoDaVerificacao | None = None
    inicio: object = None
    fim: object = None
    motivo: str = ""
    aberturas_da_comissao: int = 0
    eliminado_em: object = None
    extras: dict = field(default_factory=dict)

    @property
    def pode_enviar(self) -> bool:
        return self.estado == PODE_GRAVAR or (self.estado == RECEBIDO and self.dentro_do_periodo)

    @property
    def dentro_do_periodo(self) -> bool:
        agora = timezone.now()
        return bool(self.inicio and self.fim and self.inicio <= agora <= self.fim)

    @property
    def em_modo_video(self) -> bool:
        return self.estado in (RECEBIDO, EM_ANALISE)

    @property
    def nome_da_etapa(self) -> str:
        return self.etapa.get("name") or "Verificação da autodeclaração"


def _uuid(valor):
    return valor if isinstance(valor, UUID) else UUID(str(valor))


def periodo(edital, etapa) -> tuple:
    """`(inicio, fim)` do Evento que a Etapa aponta, no conteúdo vigente; `(None, None)` sem ele."""
    from processo_seletivo.comissoes.domain.etapas import evento_vigente

    evento = evento_vigente(edital, etapa.get("scheduleEventId"))
    if not evento:
        return None, None
    inicio = parse_datetime(evento["startAt"]) if evento.get("startAt") else None
    fim = parse_datetime(evento["endAt"]) if evento.get("endAt") else None
    return inicio, fim


def video_vigente(*, edital, etapa_id, inscricao_id):
    """O vídeo que nenhum outro substitui, ou `None`."""
    return (
        VideoDaVerificacao.objects.filter(
            edital=edital,
            etapa_id=_uuid(etapa_id),
            inscricao_id=inscricao_id,
            substituido_por__isnull=True,
        )
        .select_related("eliminacao")
        .first()
    )


def videos_recebidos(*, edital, etapa_id) -> int:
    """Quantos vídeos a Etapa já recebeu, contando os trocados (FR-7105)."""
    return VideoDaVerificacao.objects.filter(edital=edital, etapa_id=_uuid(etapa_id)).count()


def em_modo_video(*, edital, etapa_id, inscricao_ids) -> set:
    """As inscrições, entre as dadas, com vídeo vigente e sem encaminhamento. Uma consulta."""
    encaminhadas = EncaminhamentoAoVivo.objects.filter(
        edital=edital, etapa_id=_uuid(etapa_id)
    ).values("inscricao_id")
    return set(
        VideoDaVerificacao.objects.filter(
            edital=edital,
            etapa_id=_uuid(etapa_id),
            inscricao_id__in=list(inscricao_ids),
            substituido_por__isnull=True,
        )
        .exclude(inscricao_id__in=encaminhadas)
        .values_list("inscricao_id", flat=True)
    )


def inscricao_em_modo_video(*, edital, etapa_id, inscricao_id) -> bool:
    return inscricao_id in em_modo_video(
        edital=edital, etapa_id=etapa_id, inscricao_ids=[inscricao_id]
    )


def _parecer_ja_concluido(edital, etapa_id, inscricao_id) -> bool:
    """A comissão já registrou algum parecer, ainda que reaberto depois (FR-7107)."""
    from processo_seletivo.avaliacoes.models import Avaliacao, ConclusaoAvaliacao

    filtro = {"etapa_id": _uuid(etapa_id), "inscricao_id": inscricao_id}
    return (
        Avaliacao.objects.filter(
            atribuicao__edital=edital, estado=Avaliacao.Estado.CONCLUIDA, **filtro
        ).exists()
        or ConclusaoAvaliacao.objects.filter(
            avaliacao__atribuicao__edital=edital,
            avaliacao__etapa_id=_uuid(etapa_id),
            avaliacao__inscricao_id=inscricao_id,
        ).exists()
    )


def _ha_resultado(edital, etapa_id, inscricao_id) -> bool:
    from processo_seletivo.resultados.models import ResultadoEtapa

    # Pelo manager de vigência: o Resultado superado por recurso tem sucessor, e o que importa é que
    # a inscrição tem desfecho nesta Etapa.
    return ResultadoEtapa.vigentes.filter(
        edital=edital, etapa_id=_uuid(etapa_id), inscricao_id=inscricao_id
    ).exists()


def etapas_que_admitem(conteudo) -> list[dict]:
    return [etapa for etapa in (conteudo or {}).get("stages") or [] if admissao.admite_video(etapa)]


def situacao(*, inscricao, etapa, conteudo, exigir_chave=True) -> Situacao | None:
    """A situação do meio, ou `None` quando a Etapa não alcança a inscrição ou não admite o vídeo.

    `exigir_chave=False` é a leitura da gestão: a chave fecha o portal, e não a Mesa (achado I1).
    """
    from processo_seletivo.editais.domain.alcance import alcanca_a_inscricao
    from processo_seletivo.inscricoes.models import Inscricao

    if not admissao.admite_video(etapa):
        return None
    if inscricao.status != Inscricao.Status.SUBMETIDA:
        return None
    if not alcanca_a_inscricao(conteudo, etapa, inscricao.modality_id):
        return None
    edital = inscricao.edital
    etapa_id = etapa.get("id")
    inicio, fim = periodo(edital, etapa)
    base = {"etapa": etapa, "inicio": inicio, "fim": fim}
    if exigir_chave and not settings.VERIFICACAO_POR_VIDEO:
        return Situacao(INDISPONIVEL, motivo="chave", **base)
    encaminhamento = EncaminhamentoAoVivo.objects.filter(
        edital=edital, etapa_id=_uuid(etapa_id), inscricao=inscricao
    ).first()
    video = video_vigente(edital=edital, etapa_id=etapa_id, inscricao_id=inscricao.id)
    eliminado_em = (
        video.eliminacao.eliminado_em
        if video is not None and hasattr(video, "eliminacao")
        else None
    )
    if encaminhamento is not None:
        return Situacao(ENCAMINHADA, video=video, eliminado_em=eliminado_em, **base)
    if video is not None:
        aberturas = AberturaDoVideo.objects.filter(
            video=video, papel=AberturaDoVideo.Papel.COMISSAO
        ).count()
        return Situacao(
            EM_ANALISE if aberturas else RECEBIDO,
            video=video,
            aberturas_da_comissao=aberturas,
            eliminado_em=eliminado_em,
            **base,
        )
    if _ha_resultado(edital, etapa_id, inscricao.id) or _parecer_ja_concluido(
        edital, etapa_id, inscricao.id
    ):
        return Situacao(AO_VIVO, motivo="parecer", **base)
    agora = timezone.now()
    if not inicio or not fim or agora < inicio:
        return Situacao(INDISPONIVEL, motivo="antes", **base)
    if agora > fim:
        return Situacao(AO_VIVO, motivo="periodo", **base)
    return Situacao(PODE_GRAVAR, **base)


def dentro_da_tolerancia(situacao_) -> bool:
    """O envio já iniciado ainda pode concluir (FR-7126)."""
    agora = timezone.now()
    return bool(
        situacao_.inicio
        and situacao_.fim
        and situacao_.inicio <= agora <= situacao_.fim + TOLERANCIA
    )


def situacoes_do_titular(inscricao, *, conteudo) -> list[Situacao]:
    """As situações da inscrição em toda Etapa que admite o vídeo e a alcança (FR-7145).

    `conteudo` é o que a tela já leu: sem Etapa que admita o vídeo nele — toda Etapa de hoje —,
    nenhuma consulta a mais, e o orçamento do acompanhamento não muda.
    """
    if not settings.VERIFICACAO_POR_VIDEO or not etapas_que_admitem(conteudo):
        return []
    resultado = []
    for etapa in etapas_que_admitem(conteudo):
        item = situacao(inscricao=inscricao, etapa=etapa, conteudo=conteudo)
        if item is not None:
            resultado.append(item)
    return resultado
