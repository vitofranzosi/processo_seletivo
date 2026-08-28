from datetime import timedelta

import pytest
from django.db import DatabaseError, connection
from django.utils import timezone

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import (
    ProvenienciaConteudo,
    Retificacao,
    VersaoConsolidada,
)
from tests.fixtures.edital import actor_headers, complete_draft


def publish_original(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    preparer = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**preparer, "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparer, "HTTP_IF_MATCH": '"2"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{**actor_headers("homologador", ["edital:homologar"]), "HTTP_IF_MATCH": '"3"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {
            "signatory": {
                "authorityId": "00000000-0000-0000-0000-000000000601",
                "name": "Diretora",
                "role": "Diretora",
            }
        },
        format="json",
        **{**actor_headers("publicador", ["edital:publicar"]), "HTTP_IF_MATCH": '"4"'},
    )
    return Edital.objects.get(pk=edital.pk)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_published_retification_preserves_original_and_creates_consolidated_version(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    create = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Correção",
            "changes": [
                {"targetPath": "/title", "operation": "REPLACE", "newValue": "Título retificado"}
            ],
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"]),
    )
    assert create.status_code == 201
    retificacao = Retificacao.objects.get()
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/submissoes",
        format="json",
        **{**actor_headers("retificador", ["retificacao:submeter"]), "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{**actor_headers("homologador-r", ["retificacao:homologar"]), "HTTP_IF_MATCH": '"2"'},
    )
    published = api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/publicacoes",
        {
            "signatory": {
                "authorityId": "00000000-0000-0000-0000-000000000602",
                "name": "Diretora",
                "role": "Diretora",
            }
        },
        format="json",
        **{**actor_headers("publicador-r", ["retificacao:publicar"]), "HTTP_IF_MATCH": '"3"'},
    )
    assert published.status_code == 201
    assert Publicacao.objects.filter(edital=edital).count() == 2
    assert list(
        Publicacao.objects.filter(edital=edital)
        .order_by("publication_order")
        .values_list("publication_order", flat=True)
    ) == [1, 2]
    assert VersaoConsolidada.objects.filter(edital=edital).count() >= 2
    assert (
        VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content["title"]
        == "Título retificado"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_stale_retification_revision_is_rejected(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    payload = {
        "baseSnapshotId": str(base.id),
        "justification": "Correção",
        "changes": [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Novo"}],
    }
    created = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        payload,
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"]),
    )
    retificacao_id = created.data["id"]
    headers = actor_headers("retificador", ["retificacao:elaborar"], if_match=1)
    assert (
        api_client.put(
            f"/api/v1/admin/retificacoes/{retificacao_id}/rascunho",
            payload,
            format="json",
            **headers,
        ).status_code
        == 200
    )
    assert (
        api_client.put(
            f"/api/v1/admin/retificacoes/{retificacao_id}/rascunho",
            payload,
            format="json",
            **headers,
        ).status_code
        == 412
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_consolidated_version_is_append_only_on_postgresql(
    api_client, manager_headers, process_payload
):
    if connection.vendor != "postgresql":
        pytest.skip("Invariante de infraestrutura PostgreSQL")
    edital = publish_original(api_client, manager_headers, process_payload)
    version = VersaoConsolidada.objects.get(edital=edital)
    with pytest.raises(DatabaseError):
        VersaoConsolidada.objects.filter(pk=version.pk).update(content={"changed": True})


def publish_retification(api_client, edital, changes, *, effective_at=None, suffix=""):
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    payload = {
        "baseSnapshotId": str(base.id),
        "justification": "Correção de vagas",
        "changes": changes,
    }
    if effective_at is not None:
        payload["effectiveAt"] = effective_at
    create = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        payload,
        format="json",
        **actor_headers(
            "retificador", ["retificacao:elaborar"], key=f"retificacao-key-00{suffix}1"
        ),
    )
    assert create.status_code == 201, create.content
    retificacao = Retificacao.objects.get(pk=create.json()["id"])
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/submissoes",
        format="json",
        **{
            **actor_headers(
                "retificador", ["retificacao:submeter"], key=f"retificacao-key-00{suffix}2"
            ),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{
            **actor_headers(
                "homologador-r", ["retificacao:homologar"], key=f"retificacao-key-00{suffix}3"
            ),
            "HTTP_IF_MATCH": '"2"',
        },
    )
    published = api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/publicacoes",
        {
            "signatory": {
                "authorityId": "00000000-0000-0000-0000-000000000602",
                "name": "Diretora",
                "role": "Diretora",
            }
        },
        format="json",
        **{
            **actor_headers(
                "publicador-r", ["retificacao:publicar"], key=f"retificacao-key-00{suffix}4"
            ),
            "HTTP_IF_MATCH": '"3"',
        },
    )
    assert published.status_code == 201, published.content
    return retificacao


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retification_changes_vacancies_and_schedule_inside_snapshot_lists(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    original = VersaoConsolidada.objects.get(edital=edital).content
    assert original["profiles"][0]["immediateVacancies"] == 1

    publish_retification(
        api_client,
        edital,
        [
            {
                "targetPath": "/profiles/0/immediateVacancies",
                "operation": "REPLACE",
                "newValue": 12,
            },
            {
                "targetPath": "/schedule/0/description",
                "operation": "REPLACE",
                "newValue": "Inscrições prorrogadas",
            },
        ],
    )

    consolidada = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert consolidada.content["profiles"][0]["immediateVacancies"] == 12
    assert consolidada.content["schedule"][0]["description"] == "Inscrições prorrogadas"
    assert consolidada.content["profiles"][0]["code"] == "P1"

    primeira = VersaoConsolidada.objects.filter(edital=edital).earliest("materialized_at")
    assert primeira.content["profiles"][0]["immediateVacancies"] == 1
    assert (
        ProvenienciaConteudo.objects.filter(
            versao=consolidada, target_path="/profiles/0/immediateVacancies"
        ).count()
        == 1
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retification_with_future_effective_date_materializes_version_at_that_boundary(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    vigencia = timezone.now() + timedelta(days=30)

    publish_retification(
        api_client,
        edital,
        [{"targetPath": "/profiles/0/immediateVacancies", "operation": "REPLACE", "newValue": 40}],
        effective_at=vigencia.isoformat(),
    )

    retificada = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert retificada.valid_from == vigencia
    assert retificada.content["profiles"][0]["immediateVacancies"] == 40

    vigente_hoje = (
        VersaoConsolidada.objects.filter(edital=edital, valid_from__lte=timezone.now())
        .order_by("-valid_from")
        .first()
    )
    assert vigente_hoje.content["profiles"][0]["immediateVacancies"] == 1
