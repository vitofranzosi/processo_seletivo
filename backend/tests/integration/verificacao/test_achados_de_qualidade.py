"""Os achados de qualidade do code review do #547 (166): reuso, consultas e altitude."""

import ast
import pathlib

import pytest

from processo_seletivo.verificacao.application import disponibilidade, envio
from tests.fixtures import videos_sinteticos
from tests.fixtures.verificacao import enviar_video, montar_com_video

pytestmark = pytest.mark.django_db

RAIZ = pathlib.Path(__file__).resolve().parents[3] / "processo_seletivo"


@pytest.fixture
def cenario(raiz_de_arquivos, gestor, api_client, manager_headers):
    return montar_com_video(gestor, api_client, manager_headers, seed=6650, quantas=1)


def _conteudo_e_etapa(cenario):
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    conteudo = conteudo_vigente(cenario["edital"])
    etapa = next(e for e in conteudo["stages"] if e["id"] == str(cenario["hetero"]))
    return conteudo, etapa


def test_o_periodo_sai_do_conteudo_ja_lido_sem_consulta(cenario, django_assert_num_queries):
    """Achado 8: `periodo` relia a Versão Consolidada por Etapa."""
    conteudo, etapa = _conteudo_e_etapa(cenario)
    with django_assert_num_queries(0):
        inicio, fim = disponibilidade.periodo(conteudo, etapa)
    assert inicio < fim


def test_o_parecer_concluido_e_uma_consulta_e_sobrevive_a_reabertura(
    cenario, gestor, django_assert_num_queries
):
    """Achado 9: a `ConclusaoAvaliacao` responde sozinha, inclusive depois de reabrir."""
    from tests.fixtures.deliberacao import concluir_pareceres, distribuir_na_hetero

    maria = cenario["inscricoes"][0]
    distribuir_na_hetero(cenario, gestor, [maria], chave="dist-6650")
    with django_assert_num_queries(1):
        assert not disponibilidade._parecer_ja_concluido(
            cenario["edital"], cenario["hetero"], maria.id
        )
    concluir_pareceres(cenario, maria, {"ana": "FAVORAVEL"})
    with django_assert_num_queries(1):
        assert disponibilidade._parecer_ja_concluido(cenario["edital"], cenario["hetero"], maria.id)


def test_o_resumo_e_o_do_helper_comum(cenario):
    """Achado 7: o SHA-256 sai de `shared/arquivos.resumo`, e não de uma terceira cópia."""
    dados = videos_sinteticos.mp4(4.8)
    video = enviar_video(cenario["inscricoes"][0], cenario["hetero"], dados=dados)
    assert envio.resumo_do_arquivo(video.arquivo) == videos_sinteticos.resumo(dados)
    fonte = (RAIZ / "verificacao").rglob("*.py")
    assert not [str(p) for p in fonte if "hashlib.sha256" in p.read_text(encoding="utf-8")]


def test_o_encaminhamento_nao_importa_privado_da_consolidacao():
    """Achado 10: o plano da consolidação se usa pela entrada pública `planejar`."""
    arvore = ast.parse((RAIZ / "verificacao/application/encaminhamento.py").read_text("utf-8"))
    privados = [
        alias.name
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module and "consolidacao" in no.module
        for alias in no.names
        if alias.name.startswith("_")
    ]
    assert privados == []
