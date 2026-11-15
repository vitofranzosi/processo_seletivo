"""O cenário C19: a Etapa restrita admitindo o vídeo, para a equipe gravar e avaliar (171, FR-7337).

O teste confere os estados que o cenário promete — o 01 pode gravar, o 02 tem vídeo que ninguém
abriu, o 03 espera o encaminhamento à entrevista ao vivo, e o 04, na ampla, não vê nada —, pelo
comando de carga, como o do C18. E que, sem a chave do vídeo, o cenário é recusado antes de gravar.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import andamento as a
from processo_seletivo.processos.models import Edital
from processo_seletivo.treinamento import catalogo
from processo_seletivo.treinamento import construcao as k
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from processo_seletivo.verificacao.application import disponibilidade
from processo_seletivo.verificacao.models import AberturaDoVideo, VideoDaVerificacao
from tests.conftest import ator_institucional
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.treinamento import carregar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def c19(treinamento):
    treinamento.INTERFACE_SELETOR_IDENTIDADE = True
    treinamento.VERIFICACAO_POR_VIDEO = True
    saida = carregar("C19", autoridade=str(AUTORIDADE_DA_SUITE))
    assert "C19  CRIADO" in saida, saida
    manifesto = CenarioDeTreinamento.objects.get(codigo="C19")
    edital = Edital.objects.get(processo=manifesto.processo)
    inscricoes = list(Inscricao.objects.filter(edital=edital).order_by("submitted_at", "id"))
    return edital, inscricoes


def _situacao(edital, inscricao):
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    conteudo = conteudo_vigente(edital)
    (etapa,) = disponibilidade.etapas_que_admitem(conteudo)
    return disponibilidade.situacao(inscricao=inscricao, etapa=etapa, conteudo=conteudo)


def test_cada_alcancado_esta_num_ponto_do_caminho_do_video(c19):
    edital, inscricoes = c19
    estados = [
        _situacao(edital, inscricoes[posicao - 1]).estado
        for posicao in (
            catalogo.VAI_GRAVAR_DO_C19,
            catalogo.VIDEO_A_ASSISTIR_DO_C19,
            catalogo.VIDEO_QUE_NAO_CONFIRMOU_DO_C19,
        )
    ]
    # O 03 tem as aberturas dos dois avaliadores: está em análise, à espera do encaminhamento.
    assert estados == [
        disponibilidade.PODE_GRAVAR,
        disponibilidade.RECEBIDO,
        disponibilidade.EM_ANALISE,
    ]
    assert _situacao(edital, inscricoes[catalogo.NA_AMPLA_DO_C19 - 1]) is None
    assert VideoDaVerificacao.objects.filter(edital=edital).count() == 2
    assert AberturaDoVideo.objects.filter(video__edital=edital).count() == 2


def test_o_video_de_treinamento_e_o_arquivo_que_a_comissao_assiste(c19):
    """O vídeo guardado é o arquivo de treinamento: a conferência do envio é a do portal."""
    import hashlib

    edital, _ = c19
    esperado = hashlib.sha256(k.VIDEO_DE_TREINAMENTO.read_bytes()).hexdigest()
    resumos = VideoDaVerificacao.objects.filter(edital=edital).values_list("sha256", flat=True)
    assert set(resumos) == {esperado}


def test_o_centro_pede_o_encaminhamento_e_o_aviso(c19):
    """R-11: o parecer que não confirma leva à entrevista ao vivo, e não a Resultado."""
    edital, _ = c19
    atos = {
        p.ato
        for p in a.do_edital(edital, ator_institucional(k.PRESIDENCIA)).providencias
        if p.onde == k.NOME_DA_VERIFICACAO
    }
    assert "Encaminhar 1 inscrição à entrevista ao vivo" in atos
    assert f"Avisar 3 inscrições sobre {k.NOME_DA_VERIFICACAO}" in atos


def test_o_01_pode_gravar_pelo_portal(c19, client):
    edital, inscricoes = c19
    primeiro = inscricoes[catalogo.VAI_GRAVAR_DO_C19 - 1]
    entrar_como_titular(client, primeiro)
    corpo = client.get(reverse("portal:acompanhamento", args=[primeiro.id])).content.decode()
    assert "Falta um passo seu" in corpo
    assert "Você pode gravar um vídeo curto ou fazer a entrevista ao vivo." in corpo


def test_sem_a_chave_do_video_o_cenario_e_recusado_sem_gravar(treinamento):
    from django.core.management.base import CommandError

    treinamento.VERIFICACAO_POR_VIDEO = False
    try:
        saida = carregar("C19", autoridade=str(AUTORIDADE_DA_SUITE))
    except CommandError as erro:
        saida = str(erro)
    assert "VERIFICACAO_POR_VIDEO" in saida, saida
    assert not CenarioDeTreinamento.objects.filter(codigo="C19").exists()
