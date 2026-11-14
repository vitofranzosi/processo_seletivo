"""Os três pontos em que as apps existentes perguntam à verificação por vídeo (166, T-001).

A Avaliação, a consolidação e o recurso **não** dependem desta app: chamam estas funções por
importação local, e cada uma responde de graça quando a Etapa não admite o vídeo — nenhuma consulta
a mais na Etapa sem vídeo, que é toda Etapa de hoje.
"""

from processo_seletivo.avaliacoes.domain.formas import Sentido
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.verificacao.application import abertura, disponibilidade
from processo_seletivo.verificacao.domain import admissao

# A frase da conferência para a inscrição que o vídeo não confirmou (FR-7138). **Sem contagem**: a
# conferência a mostra à presidência, que pode ser membro, e a contagem diria como os colegas
# votaram antes da entrevista ao vivo que eles ainda vão dar (D-005).
ENCAMINHAR_AO_VIVO = "o vídeo não confirmou; encaminhe à entrevista ao vivo"


def exigir_abertura_para_concluir(*, ator, edital, etapa, inscricao_id):
    """Em modo vídeo, o parecer pelo vídeo exige ter aberto o vídeo (FR-7134).

    Trava a inscrição, como a conclusão do envio: o vídeo que chegasse no mesmo instante não
    transformaria em "pelo vídeo" um parecer dado sem vê-lo.
    """
    from processo_seletivo.inscricoes.models import Inscricao

    if not admissao.admite_video(etapa):
        return
    Inscricao.objects.select_for_update(of=("self",)).filter(pk=inscricao_id).first()
    if not disponibilidade.inscricao_em_modo_video(
        edital=edital, etapa_id=etapa["id"], inscricao_id=inscricao_id
    ):
        return
    video = disponibilidade.video_vigente(
        edital=edital, etapa_id=etapa["id"], inscricao_id=inscricao_id
    )
    if not abertura.abriu(video=video, pessoa=ator.subject):
        raise DomainError("video_nao_aberto", "Abra o vídeo antes de dar o parecer.", 409)


def em_modo_video_na_selecao(etapa, inscricoes) -> set:
    """As inscrições da seleção em modo vídeo; vazio, sem consulta, na Etapa sem vídeo."""
    inscricoes = list(inscricoes)
    if not admissao.admite_video(etapa) or not inscricoes:
        return set()
    return disponibilidade.em_modo_video(
        edital=inscricoes[0].edital_id,
        etapa_id=etapa["id"],
        inscricao_ids=[item.id for item in inscricoes],
    )


def recusar_desfavoravel_pelo_video(*, edital, etapa_id, inscricao_id, sentido):
    """Nenhum caminho grava Resultado desfavorável sobre inscrição em modo vídeo (FR-7139, R-11).

    É a garantia que dá segurança jurídica ao experimento: ninguém perde a reserva sem ter sido
    visto ao vivo. O plano da consolidação já separa estas inscrições; esta recusa cobre a chamada
    direta e a correção fixada do recurso.
    """
    if str(sentido) != Sentido.DESFAVORAVEL:
        return
    if disponibilidade.inscricao_em_modo_video(
        edital=edital, etapa_id=etapa_id, inscricao_id=inscricao_id
    ):
        raise DomainError(
            "desfavoravel_pelo_video",
            "O vídeo só confirma: o desfecho desfavorável só existe depois da entrevista ao vivo. "
            "Encaminhe a inscrição à entrevista ao vivo.",
            409,
        )
