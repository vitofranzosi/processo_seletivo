"""A Retificação do teto de inscrições por candidato obedece à regra da composição (015, FR-063).

A composição recusa teto abaixo de 1 desde o PR 224. A Retificação convertia o campo por `int()` e
publicava `0` ou negativo: com `0`, o envio recusa a primeira inscrição de todo mundo, sob um Edital
que anuncia o período aberto e diz no portal *"Limite atingido: você já enviou 0 inscrições"*
(RC-12, registro pré-piloto de 28/09).

A recusa é da conferência de publicação, e não da tela — a API chega ao mesmo ato sem passar por
formulário nenhum. Os dois caminhos estão aqui.
"""

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.publicacao import create_retification, publish_original, retify
from tests.interface.conftest import identificar
from tests.interface.test_retificar import campos

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

TETO = "/maxInscricoesPorCandidato"


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


def _alterar_teto(valor):
    return [{"targetPath": TETO, "operation": "REPLACE", "newValue": valor}]


def _vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


@pytest.mark.parametrize("valor", [0, -1])
def test_a_api_recusa_teto_abaixo_de_um(api_client, edital, valor):
    recusa = create_retification(
        api_client, edital, _alterar_teto(valor), suffix=f"teto{valor}", esperar=422
    )

    assert recusa["code"] == "blocking_findings"
    assert "a partir de 1" in recusa["detail"]
    assert not Retificacao.objects.exists()


def test_teto_valido_e_a_retirada_do_teto_continuam_retificaveis(api_client, edital):
    """Vazio é *sem limite* (FR-063): retificar para vazio é retirar o teto, e não um erro."""
    retify(api_client, edital, _alterar_teto(2), suffix="teto-dois")
    assert _vigente(edital).content["maxInscricoesPorCandidato"] == 2

    retify(api_client, edital, _alterar_teto(None), suffix="teto-nenhum")
    assert _vigente(edital).content["maxInscricoesPorCandidato"] is None


def test_a_tela_de_retificacao_diz_a_recusa_e_nao_cria_o_ato(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(_vigente(edital), **{TETO: "0"}),
            "justificativa": "Teto zerado por engano",
            "confirmar": "1",
        },
    )

    assert resposta.status_code == 200
    assert "a partir de 1" in resposta.content.decode()
    assert not Retificacao.objects.exists()
