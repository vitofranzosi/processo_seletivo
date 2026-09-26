"""A vitrine lê o desfecho de todos os cartões numa consulta só (047, `R-2`, `R-7`).

Até a 047 nenhum teste media as consultas da vitrine. O desfecho acrescenta uma leitura aos atos
administrativos, e o risco clássico é ela virar uma por cartão — invisível com três seleções,
caro com cem.
"""

from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.processos.application.finalizacao import close_edital
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.selecao import identificador, publicar_selecao, rascunho_de_selecao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

GESTORA = Actor("gestora.vitrine", "cefor", frozenset({"edital:encerrar"}))


def publicar_e_encerrar(api_client, manager_headers, process_payload, seed):
    agora = timezone.now()
    rascunho = rascunho_de_selecao(seed)
    rascunho["schedule"] = [
        {
            "id": identificador(490 + seed, seed),
            "type": "Inscrições",
            "description": "Período de inscrições",
            "startAt": (agora - timedelta(days=1)).isoformat(),
            "endAt": (agora + timedelta(days=9)).isoformat(),
            "order": 0,
            "isRegistrationPeriod": True,
        }
    ]
    carga = {
        **process_payload,
        "institutionalCode": f"PS-VIT-{seed}",
        "firstEdital": {**process_payload["firstEdital"], "number": f"9{seed}"},
    }
    # A chave de idempotência da criação é fixa no `manager_headers`: cada Processo pede a sua.
    cabecalhos = {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"vitrine-047-{seed:04d}"}
    publicado = publicar_selecao(api_client, cabecalhos, carga, rascunho=rascunho)
    edital = Edital.objects.get(pk=publicado.id)
    close_edital(
        actor=GESTORA,
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Encerramento do teste de consultas.",
        idempotency_key=f"encerrar-vitrine-{seed}",
        correlation_id="047-vitrine",
    )


def consultas_da_vitrine(client):
    with CaptureQueriesContext(connection) as consultas:
        resposta = client.get(reverse("portal:vitrine"))
    assert resposta.status_code == 200
    return consultas.captured_queries


def aos_atos(consultas):
    return [item for item in consultas if "processos_atoadministrativo" in item["sql"]]


def test_um_e_cinco_encerrados_custam_as_mesmas_consultas_aos_atos(
    client, api_client, manager_headers, process_payload
):
    publicar_e_encerrar(api_client, manager_headers, process_payload, 1)
    com_um = consultas_da_vitrine(client)

    for seed in range(2, 6):
        publicar_e_encerrar(api_client, manager_headers, process_payload, seed)
    com_cinco = consultas_da_vitrine(client)

    assert len(aos_atos(com_um)) == 1
    assert len(aos_atos(com_cinco)) == 1
    assert len(com_cinco) == len(com_um), "a vitrine passou a consultar por cartão"
