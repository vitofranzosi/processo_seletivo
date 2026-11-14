"""O degrau do passo no acompanhamento, com banco (168, US1; FR-7300 a FR-7311; SC-2414).

O Edital é o da `166` **sem** o vídeo (`rascunho_com_video(video=False)`): a Etapa restrita e
colegiada da `165`, com o Evento que lhe dá período. É a camada A, o caminho real de hoje.
"""

from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.portal import passo_da_etapa
from processo_seletivo.resultados.application.selectors import resultados_visiveis
from tests.fixtures.comissao import inscrever
from tests.fixtures.deliberacao import (
    concluir_pareceres,
    distribuir_na_hetero,
    montar_colegiada,
)
from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.verificacao import rascunho_com_video

pytestmark = pytest.mark.django_db


def _montar(gestor, api_client, manager_headers, *, seed, inicio, fim):
    return montar_colegiada(
        gestor,
        api_client,
        manager_headers,
        seed=seed,
        regra="UNANIMOUS_FOR_FAVORABLE",
        quantas=2,
        rascunho=rascunho_com_video(seed, inicio=inicio, fim=fim, video=False),
    )


@pytest.fixture
def antes(gestor, api_client, manager_headers):
    agora = timezone.now()
    return _montar(
        gestor,
        api_client,
        manager_headers,
        seed=6801,
        inicio=agora + timedelta(days=2),
        fim=agora + timedelta(days=5),
    )


@pytest.fixture
def vencido(gestor, api_client, manager_headers):
    agora = timezone.now()
    return _montar(
        gestor,
        api_client,
        manager_headers,
        seed=6802,
        inicio=agora - timedelta(days=5),
        fim=agora - timedelta(days=1),
    )


def _acompanhamento(client, inscricao):
    entrar_como_titular(client, inscricao)
    resposta = client.get(reverse("portal:acompanhamento", args=[inscricao.id]))
    assert resposta.status_code == 200
    return resposta.content.decode()


def _passos(inscricao):
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    return passo_da_etapa.passos_da_inscricao(
        inscricao,
        conteudo=conteudo_vigente(inscricao.edital),
        resultados_visiveis=resultados_visiveis(inscricao),
        agora=timezone.now(),
    )


def test_o_alcancado_ve_o_passo_antes_do_periodo(antes, client, seletor_ligado):
    """US1, cenário 1: porquê, quando, como, consequência e o Edital."""
    maria = antes["inscricoes"][0]
    corpo = _acompanhamento(client, maria)
    assert "Falta um passo seu" in corpo
    assert "Você se inscreveu em Pretos e pardos" in corpo
    assert "A comissão vai informar o dia, a hora e como participar." in corpo
    assert "continua concorrendo pela ampla concorrência" in corpo
    assert reverse("portal:selecao", args=[antes["edital"].id]) in corpo
    # O cartão provisório da `166` não existe mais (FR-7314).
    assert "verificacao-no-acompanhamento" not in corpo


def test_quem_esta_so_na_ampla_nao_ve_nada(antes, client, seletor_ligado):
    """US1, cenário 5; FR-7301."""
    (pedro,) = inscrever(antes["edital"], 1, primeiro=90, perfil=antes["perfil"])
    corpo = _acompanhamento(client, pedro)
    assert "Falta um passo seu" not in corpo
    assert "Heteroidentificação" not in corpo.split("<h2", 2)[1]


def test_o_periodo_vencido_sem_registro_aguarda_a_comissao(vencido, client, seletor_ligado):
    """US1, cenário 3; FR-7306: e não diz que a análise começou."""
    corpo = _acompanhamento(client, vencido["inscricoes"][0])
    assert "Aguardando a comissão" in corpo
    assert "O período desta etapa terminou em" in corpo
    assert "analisando" not in corpo


def test_com_parecer_concluido_aguarda_o_resultado(antes, gestor, client, seletor_ligado):
    """US1, cenário 3a; FR-7306: um parecer basta, e nenhum sentido aparece."""
    maria = antes["inscricoes"][0]
    distribuir_na_hetero(antes, gestor, [maria], chave="hetero-6801")
    concluir_pareceres(antes, maria, {"ana": "FAVORAVEL"})
    corpo = _acompanhamento(client, maria)
    assert "Aguardando o resultado" in corpo
    assert "Falta um passo seu" not in corpo
    assert "Deferido" not in corpo.split('class="situacao', 1)[-1].split("</section>", 1)[0]


def test_o_passo_e_derivado_e_nao_guardado(antes, gestor):
    """FR-7308: a mesma inscrição muda de passo sem nenhum registro do passo."""
    maria = antes["inscricoes"][0]
    assert [p.estado for p in _passos(maria)] == [passo_da_etapa.FALTA]
    distribuir_na_hetero(antes, gestor, [maria], chave="hetero-6801-b")
    concluir_pareceres(antes, maria, {"ana": "FAVORAVEL"})
    assert [p.estado for p in _passos(maria)] == [passo_da_etapa.AGUARDA_RESULTADO]


def test_sem_etapa_restrita_que_alcance_nenhuma_consulta(antes):
    """FR-7311, SC-2414: quem está só na ampla não custa consulta ao acompanhamento."""
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    (pedro,) = inscrever(antes["edital"], 1, primeiro=91, perfil=antes["perfil"])
    conteudo = conteudo_vigente(antes["edital"])
    with CaptureQueriesContext(connection) as consultas:
        passos = passo_da_etapa.passos_da_inscricao(
            pedro, conteudo=conteudo, resultados_visiveis=[], agora=timezone.now()
        )
    assert passos == []
    assert len(consultas) == 0


def test_o_alcancado_custa_poucas_consultas(antes):
    """T-001: participação com o conteúdo dado, parecer e Resultado — sem reler a versão."""
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    maria = antes["inscricoes"][0]
    conteudo = conteudo_vigente(antes["edital"])
    # A view já leu o Edital da inscrição (a unidade, o canal): a medida começa depois dele.
    assert maria.edital is not None
    with CaptureQueriesContext(connection) as consultas:
        passo_da_etapa.passos_da_inscricao(
            maria, conteudo=conteudo, resultados_visiveis=[], agora=timezone.now()
        )
    assert len(consultas) <= 6, "\n".join(c["sql"][:160] for c in consultas)
    assert not any("publicacoes_" in c["sql"] for c in consultas)
