"""A janela que nasce pela API concede — e a guarda não julga a história (048, D-003, FR-787).

A tela não oferece *"não admite"* no nascimento (a janela nasce só com o prazo). A API ofereceria,
e é aqui que a guarda existe. O segundo caso é o que decidiu **onde** ela mora: se estivesse no
motor de alterações, que também reproduz atos já publicados, um nascimento feito antes dela
recusaria toda Retificação futura do mesmo Edital.
"""

from unittest import mock

import pytest

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import corte_que_nao_governa
from tests.fixtures.publicacao import create_retification, publish_original, publish_retification
from tests.fixtures.snapshot import ETAPA, PERFIL, rascunho_com_etapas

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

MARCO = "00000000-0000-0000-0000-000000000641"
JANELA = f"/profiles/id={PERFIL['B']}/classificationMilestones/id={MARCO}/appealWindow"
NAO_ADMITE = {"admits": False, "durationDays": None, "unit": "DIAS_CORRIDOS"}
CONCEDE = {"admits": True, "durationDays": 3, "unit": "DIAS_CORRIDOS"}


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    """Um Edital publicado com um marco que não declara janela recursal."""
    rascunho = rascunho_com_etapas()
    perfil = next(item for item in rascunho["profiles"] if item["id"] == PERFIL["B"])
    perfil["classificationMilestones"] = [
        {
            "cutRule": corte_que_nao_governa(),
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [ETAPA["A"]],
            "orderProduction": "POR_PONTUACAO",
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
        }
    ]
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho)


def janela_vigente(edital):
    conteudo = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content
    perfil = next(item for item in conteudo["profiles"] if item["id"] == PERFIL["B"])
    return perfil["classificationMilestones"][0].get("appealWindow")


def test_a_contraprova_o_marco_publicado_nao_tem_janela(publicado):
    assert janela_vigente(publicado) is None


def test_a_janela_que_nasce_sem_admitir_e_recusada_na_elaboracao(api_client, publicado):
    recusa = create_retification(
        api_client,
        publicado,
        [{"targetPath": JANELA, "operation": "REPLACE", "newValue": NAO_ADMITE}],
        esperar=422,
    )

    assert recusa["code"] == "invalid_change"
    assert "concede prazo de recurso onde não havia" in recusa["detail"]
    assert janela_vigente(publicado) is None


def test_a_janela_que_nasce_concedendo_publica(api_client, publicado):
    publish_retification(
        api_client,
        create_retification(
            api_client,
            publicado,
            [{"targetPath": JANELA, "operation": "REPLACE", "newValue": CONCEDE}],
        ),
    )

    assert janela_vigente(publicado) == CONCEDE


def test_um_nascimento_anterior_a_guarda_nao_impede_a_retificacao_seguinte(api_client, publicado):
    """A guarda está no ato, e não no motor que reproduz atos publicados (portão 1 da 048).

    O primeiro ato é publicado com a guarda neutralizada — é o Edital que alguém retificou pela API
    antes desta feature existir. O segundo é uma Retificação legítima de outro campo, e publicar
    materializa de novo as versões, reproduzindo o primeiro.
    """
    with mock.patch(
        "processo_seletivo.publicacoes.application.retificacoes.recusar_janela_que_nasce_sem_recurso"
    ):
        publish_retification(
            api_client,
            create_retification(
                api_client,
                publicado,
                [{"targetPath": JANELA, "operation": "REPLACE", "newValue": NAO_ADMITE}],
                suffix="antiga",
            ),
            suffix="antiga",
        )
    assert janela_vigente(publicado) == NAO_ADMITE

    publish_retification(
        api_client,
        create_retification(
            api_client,
            publicado,
            [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Título corrigido"}],
            suffix="nova",
        ),
        suffix="nova",
    )

    assert janela_vigente(publicado) == NAO_ADMITE
