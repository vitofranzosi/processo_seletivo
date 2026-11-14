"""O que a Mesa da `012` lê da verificação por vídeo (166, FR-7128 a FR-7134, UX-774).

A Mesa é a mesma: o vídeo entra no painel do documento, e os rótulos do parecer mudam enquanto a
inscrição está em modo vídeo. Fora da Etapa que admite o vídeo, nada — nem consulta.
"""

from processo_seletivo.verificacao.application import abertura, disponibilidade
from processo_seletivo.verificacao.domain import admissao, roteiro
from processo_seletivo.verificacao.models import AberturaDoVideo

CONFIRMO = "Confirmo"
NAO_DA = "Não dá para confirmar pelo vídeo"


def contexto(request, *, ator, edital, etapa, inscricao_id):
    """O vídeo da inscrição na Mesa, ou `None`. A chave não pesa aqui (achado I1)."""
    if not admissao.admite_video(etapa):
        return None
    video = disponibilidade.video_vigente(
        edital=edital, etapa_id=etapa["id"], inscricao_id=inscricao_id
    )
    if video is None:
        return None
    em_modo_video = disponibilidade.inscricao_em_modo_video(
        edital=edital, etapa_id=etapa["id"], inscricao_id=inscricao_id
    )
    abertura_pedida = request.GET.get("abertura", "")
    aberta = (
        AberturaDoVideo.objects.filter(
            pk=abertura_pedida,
            video=video,
            pessoa=ator.subject,
            papel=AberturaDoVideo.Papel.COMISSAO,
        ).first()
        if abertura_pedida and abertura.da_sessao(request, abertura_pedida)
        else None
    )
    return {
        "video": video,
        "em_modo_video": em_modo_video,
        "ja_abriu": abertura.abriu(video=video, pessoa=ator.subject),
        "abertura": aberta,
        "marcas": roteiro.marcas_com_titulo(video.marcas),
        "eliminado_em": video.eliminacao.eliminado_em if abertura.eliminado(video) else None,
    }
