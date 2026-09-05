"""O custo do cálculo é do conjunto, não uma consulta por participante (015, SC-002/SC-003)."""

import time

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.performance, pytest.mark.django_db(transaction=True)]

MARCO = "00000000-0000-4000-8000-000000000481"
BUDGET_SECONDS = 2.8


@pytest.fixture
def edital_em_escala(api_client, manager_headers, process_payload):
    rascunho = rascunho_com_etapas(avaliacoes=1, maxima="100.0000", minima="0.0000")
    etapa = rascunho["stages"][1]
    etapa["weight"] = "1.0000"
    rascunho["profiles"][0]["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [etapa["id"]],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
        }
    ]
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    _acrescentar_inscricoes(edital, quantidade=5, inicio=1)
    return edital


def _acrescentar_inscricoes(edital, *, quantidade, inicio):
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    agora = timezone.now()
    Inscricao.objects.bulk_create(
        [
            Inscricao(
                identity_subject=f"cpf:escala-{numero:04d}",
                edital=edital,
                profile_id=PROFILE_ID,
                status=Inscricao.Status.SUBMETIDA,
                protocolo=f"E{numero:04d}",
                nome=f"Participante {numero:04d}",
                cpf="111.444.777-35",
                cpf_normalizado="11144477735",
                email=f"escala{numero}@example.test",
                versao_aceita=versao,
                declaracoes_aceitas_em=agora,
                submitted_at=agora,
                created_at=agora,
            )
            for numero in range(inicio, inicio + quantidade)
        ]
    )


def _calcular(edital):
    return calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)


def test_numero_de_consultas_nao_cresce_ate_mil_participantes(edital_em_escala):
    with CaptureQueriesContext(connection) as pequeno:
        _calcular(edital_em_escala)
    _acrescentar_inscricoes(edital_em_escala, quantidade=995, inicio=6)
    with CaptureQueriesContext(connection) as grande:
        proposta = _calcular(edital_em_escala)

    assert len(proposta["universo"]["participants"]) == 1000
    assert len(grande) == len(pequeno)


def test_tela_de_mil_participantes_fica_abaixo_do_teto(
    edital_em_escala,
    client,
    seletor_ligado,
):
    _acrescentar_inscricoes(edital_em_escala, quantidade=995, inicio=6)
    identificar(client, "gestora", ["gestor"])

    inicio = time.monotonic()
    resposta = client.get(reverse("interface:ordenacao", args=[edital_em_escala.id, MARCO]))
    duracao = time.monotonic() - inicio

    assert resposta.status_code == 200
    assert duracao < BUDGET_SECONDS, f"a tela levou {duracao:.3f}s"
