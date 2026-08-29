"""US6 — Consultar Conteúdo Vigente e Histórico. Rastreia FR-028 a FR-031 e FR-039."""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import caminho_perfil
from tests.fixtures.publicacao import create_retification, publish_original, publish_retification

VACANCIES = caminho_perfil("immediateVacancies")


def replace_vacancies(value):
    return [{"targetPath": VACANCIES, "operation": "REPLACE", "newValue": value}]


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us6_current_version_identifies_the_acts_that_compose_it(
    api_client, manager_headers, process_payload
):
    """Cenário 1: a versão vigente é a última consolidada e identifica os atos que a compõem."""
    edital = publish_original(api_client, manager_headers, process_payload)
    publish_retification(
        api_client,
        create_retification(api_client, edital, replace_vacancies(8), suffix="a"),
        suffix="a",
    )

    vigente = api_client.get(f"/api/v1/public/editais/{edital.id}/versao-vigente").json()
    retificacao_publicacao = Publicacao.objects.get(retificacao__isnull=False, edital=edital)

    assert vigente["content"]["profiles"][0]["immediateVacancies"] == 8
    assert str(retificacao_publicacao.id) in vigente["appliedPublications"]
    assert {
        "targetPath": VACANCIES,
        "publicationId": str(retificacao_publicacao.id),
    } in vigente["provenance"]
    assert vigente["contentHash"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us6_past_instant_reproduces_the_version_then_in_force(
    api_client, manager_headers, process_payload
):
    """Cenário 2: consultar uma data passada não aplica regras posteriores (FR-030)."""
    edital = publish_original(api_client, manager_headers, process_payload)
    original = VersaoConsolidada.objects.get(edital=edital)
    publish_retification(
        api_client,
        create_retification(api_client, edital, replace_vacancies(8), suffix="a"),
        suffix="a",
    )

    url = f"/api/v1/public/editais/{edital.id}/versao-vigente"
    passado = api_client.get(url, {"em": original.valid_from.isoformat()}).json()

    assert passado["id"] == str(original.id)
    assert passado["content"]["profiles"][0]["immediateVacancies"] == 1
    assert api_client.get(url).json()["content"]["profiles"][0]["immediateVacancies"] == 8


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us6_anonymous_reaches_original_retifications_and_every_consolidated_version(
    api_client, manager_headers, process_payload
):
    """Cenário 3: sem permissão administrativa o público alcança todo o histórico publicado."""
    edital = publish_original(api_client, manager_headers, process_payload)
    futura = timezone.now() + timedelta(days=30)
    publish_retification(
        api_client,
        create_retification(api_client, edital, replace_vacancies(8), suffix="a"),
        suffix="a",
    )
    publish_retification(
        api_client,
        create_retification(
            api_client, edital, replace_vacancies(12), effective_at=futura.isoformat(), suffix="b"
        ),
        suffix="b",
    )

    historico = api_client.get(
        f"/api/v1/public/editais/{edital.id}/historico", {"limit": 100}
    ).json()
    por_tipo = {}
    for item in historico["items"]:
        por_tipo.setdefault(item["kind"], []).append(item)

    assert len(por_tipo["PUBLICACAO"]) == 3
    assert len(por_tipo["RETIFICACAO"]) == 2
    assert (
        len(por_tipo["VERSAO_CONSOLIDADA"])
        == VersaoConsolidada.objects.filter(edital=edital).count()
    )

    for item in por_tipo["VERSAO_CONSOLIDADA"]:
        assert api_client.get(f"/api/v1/public/versoes/{item['id']}").status_code == 200
    for item in por_tipo["RETIFICACAO"]:
        assert api_client.get(f"/api/v1/public/retificacoes/{item['id']}").status_code == 200
    for item in por_tipo["PUBLICACAO"]:
        detalhe = api_client.get(f"/api/v1/public/publicacoes/{item['id']}")
        assert detalhe.status_code == 200
        assert api_client.get(detalhe.json()["documentUrl"]).status_code == 200


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us6_reports_absence_of_effective_version_without_substituting_the_current_one(
    api_client, manager_headers, process_payload
):
    """FR-038: consulta sem versão vigente informa a ausência em vez de devolver a atual."""
    edital = publish_original(api_client, manager_headers, process_payload)
    original = VersaoConsolidada.objects.get(edital=edital)

    response = api_client.get(
        f"/api/v1/public/editais/{edital.id}/versao-vigente",
        {"em": (original.valid_from - timedelta(days=1)).isoformat()},
    )
    assert response.status_code == 404
    corpo = response.json()
    assert corpo["code"] == "no_effective_version"
    assert "content" not in corpo
