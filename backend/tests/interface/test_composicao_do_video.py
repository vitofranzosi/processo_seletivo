"""A composição admite o vídeo, e sem a chave diz por que não (166, US1, FR-7102 a FR-7106)."""

import pytest

from processo_seletivo.editais.models.etapas import EtapaAvaliacao
from processo_seletivo.interface.revisao import _etapa as linhas_da_revisao
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_compor import etapa, etapas_form, eventos, perfis
from tests.interface.test_composicao_da_deliberacao import DECISORIA


@pytest.fixture
def elaborando(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()
    return edital


def _colegiada(**extra):
    return etapas_form(
        **DECISORIA,
        **{
            "etapa-0-evaluationsPerRegistration": "3",
            "etapa-0-regraDeDeliberacao": "UNANIMOUS_FOR_FAVORABLE",
            **extra,
        },
    )


@pytest.mark.django_db
@pytest.mark.integration
def test_a_admissao_e_gravada_e_relida(client, elaborando, settings):
    settings.VERIFICACAO_POR_VIDEO = True
    resposta = client.post(etapa(elaborando, "etapas"), _colegiada(**{"etapa-0-admiteVideo": "1"}))
    assert resposta.status_code == 302, resposta.content
    assert EtapaAvaliacao.objects.order_by("order").first().admite_video is True
    corpo = client.get(etapa(elaborando, "etapas")).content.decode()
    assert "Admite vídeo gravado pelo candidato" in corpo
    assert 'name="etapa-0-admiteVideo" value="1"' in corpo
    assert "O vídeo só confirma" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_sem_a_chave_o_campo_aparece_desabilitado_com_a_razao(client, elaborando, settings):
    """FR-7104, e a jornada do operador do estudo: desabilitado, com a razão."""
    settings.VERIFICACAO_POR_VIDEO = False
    client.post(etapa(elaborando, "etapas"), _colegiada())
    corpo = client.get(etapa(elaborando, "etapas")).content.decode()
    campo = corpo.split('id="etapa-0-admiteVideo"')[1].split(">")[0]
    assert "disabled" in campo
    assert "o vídeo depende de protocolo institucional que ainda não existe" in corpo


def test_a_revisao_diz_a_admissao():
    linhas = linhas_da_revisao(
        {"name": "Hetero", "videoOption": True}, {"stages": [], "schedule": []}
    )
    assert "Vídeo" in repr(linhas)
    assert "as duas formas valem igual" in repr(linhas)
