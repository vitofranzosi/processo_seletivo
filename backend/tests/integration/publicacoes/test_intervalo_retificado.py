"""Recusa do cronograma não deixa ato, versão ou auditoria de sucesso parcial (101, FR-2612)."""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import (
    create_retification,
    publish_original,
    retify,
    try_publish_retification,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def test_publicacao_de_intervalo_invertido_recusa_sem_efeito_parcial(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    anterior = effective_version(edital_id=edital.id)
    evento = anterior.content["schedule"][0]
    recusada = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": f"/schedule/id={evento['id']}/endAt",
                "operation": "REPLACE",
                "newValue": "2020-01-01T12:00:00-03:00",
            }
        ],
        esperar=422,
    )
    assert recusada["code"] == "blocking_findings"
    assert "anterior ao início" in recusada["detail"]
    assert not Retificacao.objects.exists()
    assert Publicacao.objects.count() == 1
    assert VersaoConsolidada.objects.count() == 1
    assert effective_version(edital_id=edital.id).id == anterior.id


def test_um_evento_invalido_impede_publicacao_mesmo_com_outro_valido(
    api_client, manager_headers, process_payload
):
    rascunho = complete_draft()
    segundo_id = str(uuid4())
    rascunho["schedule"].append(
        {
            "id": segundo_id,
            "type": "SORTEIO",
            "description": "Sorteio",
            "startAt": (timezone.now() + timedelta(days=12)).isoformat(),
            "order": 2,
        }
    )
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    anterior = effective_version(edital_id=edital.id)
    evento = anterior.content["schedule"][0]
    recusada = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": f"/schedule/id={segundo_id}/startAt",
                "operation": "REPLACE",
                "newValue": (timezone.now() + timedelta(days=13)).isoformat(),
            },
            {
                "targetPath": f"/schedule/id={evento['id']}/endAt",
                "operation": "REPLACE",
                "newValue": "2020-01-01T12:00:00-03:00",
            },
        ],
        esperar=422,
    )
    assert recusada["code"] == "blocking_findings"
    assert effective_version(edital_id=edital.id).content == anterior.content


def test_publicacao_recusa_intervalo_invertido_por_ato_concorrente(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = effective_version(edital_id=edital.id)
    caminho = f"/schedule/id={base.content['schedule'][0]['id']}"
    agora = timezone.now()
    candidata = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": caminho + "/endAt",
                "operation": "REPLACE",
                "newValue": (agora + timedelta(days=5)).isoformat(),
            }
        ],
        suffix="candidata",
    )
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": caminho + "/startAt",
                "operation": "REPLACE",
                "newValue": (agora + timedelta(days=6)).isoformat(),
            }
        ],
        suffix="concorrente",
    )
    anterior = effective_version(edital_id=edital.id)
    versoes = VersaoConsolidada.objects.count()
    resposta = try_publish_retification(api_client, candidata, suffix="candidata")
    assert resposta.status_code == 422, resposta.content
    assert resposta.data["code"] == "blocking_findings"
    candidata.refresh_from_db()
    assert candidata.status == Retificacao.Status.HOMOLOGADA
    assert candidata.publication_id is None
    assert Publicacao.objects.count() == 2
    assert VersaoConsolidada.objects.count() == versoes
    assert effective_version(edital_id=edital.id).id == anterior.id
    assert not RegistroAuditoria.objects.filter(
        aggregate_id=candidata.id, operation="PUBLICAR"
    ).exists()


def test_intervalo_invalido_na_fronteira_futura_recusa_imediata_atomicamente(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = effective_version(edital_id=edital.id)
    evento = base.content["schedule"][0]
    caminho = f"/schedule/id={evento['id']}"
    agora = timezone.now()
    futura = retify(
        api_client,
        edital,
        [
            {
                "targetPath": caminho + "/endAt",
                "operation": "REPLACE",
                "newValue": (agora + timedelta(days=9)).isoformat(),
            }
        ],
        effective_at=agora + timedelta(days=3),
        suffix="futura",
    )
    imutavel = bytes(futura.publication.canonical_content)
    imediata = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": caminho + "/startAt",
                "operation": "REPLACE",
                "newValue": (agora + timedelta(days=10)).isoformat(),
            },
            {
                "targetPath": caminho + "/endAt",
                "operation": "REPLACE",
                "newValue": (agora + timedelta(days=11)).isoformat(),
            },
        ],
        base=base,
        suffix="imediata",
    )
    versoes = VersaoConsolidada.objects.count()
    resposta = try_publish_retification(api_client, imediata, suffix="imediata")
    assert resposta.status_code == 422, resposta.content
    assert "anterior ao início" in resposta.data["detail"]
    assert Publicacao.objects.filter(edital=edital).count() == 2
    assert VersaoConsolidada.objects.count() == versoes
    assert effective_version(edital_id=edital.id).id == base.id
    futura.publication.refresh_from_db()
    assert bytes(futura.publication.canonical_content) == imutavel


def test_evento_com_inicio_igual_ao_termino_continua_publicavel(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = effective_version(edital_id=edital.id)
    evento = base.content["schedule"][0]
    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": f"/schedule/id={evento['id']}/endAt",
                "operation": "REPLACE",
                "newValue": evento["startAt"],
            }
        ],
    )
    assert try_publish_retification(api_client, retificacao).status_code == 201
    vigente = effective_version(edital_id=edital.id).content["schedule"][0]
    assert vigente["startAt"] == vigente["endAt"]
