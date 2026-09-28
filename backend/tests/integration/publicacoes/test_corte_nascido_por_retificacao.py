"""A regra de corte não nasce sobre Etapa já avaliada (048, US2, FR-789, D-002).

O cenário é o da `015` com o marco intermediário: ele mede a primeira Etapa e não corta — o Cenário
D da `046`, o marco que legitimamente não corta num Perfil que corta. Fazer nascer a regra dele
governando a segunda Etapa, quando ela já tem Resultado, é o que a guarda recusa: emitido o corte,
ele tiraria da segunda Etapa quem já foi avaliado nela.
"""

import pytest

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.divulgacao import montar_marco, pontuar
from tests.fixtures.publicacao import (
    create_retification,
    publish_retification,
    try_publish_retification,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return montar_marco(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=149,
        codigo="0849",
        com_intermediario=True,
    )


def _nascer(cenario, *, governa):
    caminho = (
        f"/profiles/id={cenario['perfil']}/classificationMilestones/id="
        f"{cenario['marco_intermediario']}/cutRule"
    )
    regra = {
        "targetKind": "FIXED",
        "targetCount": 1,
        "surplusCount": 0,
        "tieOutcome": "STRICT",
        "governedStage": governa,
        "continuation": "NONE",
    }
    return [{"targetPath": caminho, "operation": "REPLACE", "newValue": regra}]


def _corte_do_intermediario(cenario):
    conteudo = (
        VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("materialized_at").content
    )
    marco = next(
        marco
        for perfil in conteudo["profiles"]
        for marco in perfil["classificationMilestones"]
        if str(marco["id"]) == str(cenario["marco_intermediario"])
    )
    return marco.get("cutRule")


def test_a_contraprova_o_intermediario_nasceu_sem_corte(cenario):
    assert _corte_do_intermediario(cenario) is None


def test_governando_etapa_com_resultado_e_recusado_na_elaboracao(cenario, gestor, api_client):
    pontuar(cenario, gestor, ["80.0000"], primeiro=1491, sufixo="149")

    recusa = create_retification(
        api_client, cenario["edital"], _nascer(cenario, governa=cenario["segunda"]), esperar=422
    )

    assert recusa["code"] == "cut_rule_born_over_evaluated_stage"
    assert "já tem Resultado registrado" in recusa["detail"]
    assert "Classificação da análise documental" in recusa["detail"]
    assert _corte_do_intermediario(cenario) is None


def test_resultado_registrado_depois_da_elaboracao_e_recusado_na_publicacao(
    cenario, gestor, api_client
):
    """Edge Case da spec: entre a confirmação e a publicação, o mundo muda."""
    retificacao = create_retification(
        api_client, cenario["edital"], _nascer(cenario, governa=cenario["segunda"])
    )
    pontuar(cenario, gestor, ["80.0000"], primeiro=1492, sufixo="149b")

    resposta = try_publish_retification(api_client, retificacao)

    assert resposta.status_code == 422, resposta.content
    assert resposta.json()["code"] == "cut_rule_born_over_evaluated_stage"
    assert _corte_do_intermediario(cenario) is None


def test_a_regra_que_nao_governa_etapa_nasce_mesmo_com_resultado(cenario, gestor, api_client):
    pontuar(cenario, gestor, ["80.0000"], primeiro=1493, sufixo="149c")

    publish_retification(
        api_client,
        create_retification(api_client, cenario["edital"], _nascer(cenario, governa="NONE")),
    )

    assert _corte_do_intermediario(cenario)["governedStage"] == "NONE"


def test_governando_etapa_ainda_sem_resultado_a_regra_nasce(cenario, api_client):
    publish_retification(
        api_client,
        create_retification(
            api_client, cenario["edital"], _nascer(cenario, governa=cenario["segunda"])
        ),
    )

    assert _corte_do_intermediario(cenario)["governedStage"] == str(cenario["segunda"])
