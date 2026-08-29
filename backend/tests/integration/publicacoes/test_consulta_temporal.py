import time
from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import caminho_perfil
from tests.fixtures.publicacao import create_retification, publish_original, publish_retification

VACANCIES = caminho_perfil("immediateVacancies")


def vacancies_at(api_client, edital, instant=None):
    params = {} if instant is None else {"em": instant.isoformat()}
    response = api_client.get(
        f"/api/v1/public/editais/{edital.id}/versao-vigente", params, format="json"
    )
    assert response.status_code == 200, response.content
    return response.json()["content"]["profiles"][0]["immediateVacancies"]


def replace_vacancies(value):
    return [{"targetPath": VACANCIES, "operation": "REPLACE", "newValue": value}]


@pytest.fixture
def edital_publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_no_version_was_in_force_before_the_first_publication(api_client, edital_publicado):
    original = VersaoConsolidada.objects.get(edital=edital_publicado)
    response = api_client.get(
        f"/api/v1/public/editais/{edital_publicado.id}/versao-vigente",
        {"em": (original.valid_from - timedelta(seconds=1)).isoformat()},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "no_effective_version"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_validity_starts_inclusively_at_the_boundary(api_client, edital_publicado):
    original = VersaoConsolidada.objects.get(edital=edital_publicado)
    assert vacancies_at(api_client, edital_publicado, original.valid_from) == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_future_retification_only_takes_effect_from_its_declared_instant(
    api_client, edital_publicado
):
    vigencia = timezone.now() + timedelta(days=15)
    publish_retification(
        api_client,
        create_retification(
            api_client, edital_publicado, replace_vacancies(50), effective_at=vigencia.isoformat()
        ),
    )

    assert vacancies_at(api_client, edital_publicado) == 1
    assert vacancies_at(api_client, edital_publicado, vigencia - timedelta(seconds=1)) == 1
    assert vacancies_at(api_client, edital_publicado, vigencia) == 50
    assert vacancies_at(api_client, edital_publicado, vigencia + timedelta(days=365)) == 50


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_out_of_order_publications_compose_by_validity_not_by_publication_order(
    api_client, edital_publicado
):
    """FR-039: A é publicada antes de B mas vigora depois; cada instante tem versão própria."""
    vigencia_b = timezone.now() + timedelta(days=10)
    vigencia_a = timezone.now() + timedelta(days=20)

    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital_publicado,
            replace_vacancies(30),
            effective_at=vigencia_a.isoformat(),
            suffix="a",
        ),
        suffix="a",
    )
    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital_publicado,
            replace_vacancies(20),
            effective_at=vigencia_b.isoformat(),
            suffix="b",
            # B vigora antes de A: a versão que A materializou vale a partir de `vigencia_a` e
            # não é o que vigora quando B começa. B se elabora sobre a versão original, que é a
            # vigente em `vigencia_b` — e é contra ela que a precondição de conteúdo é medida.
            base=VersaoConsolidada.objects.filter(edital=edital_publicado).earliest("valid_from"),
        ),
        suffix="b",
    )

    assert vacancies_at(api_client, edital_publicado) == 1
    assert vacancies_at(api_client, edital_publicado, vigencia_b) == 20
    assert vacancies_at(api_client, edital_publicado, vigencia_a) == 30


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_history_query_does_not_apply_later_rules_to_earlier_instants(api_client, edital_publicado):
    """FR-030: consultar o passado reproduz a versão de então, não a atual."""
    original = VersaoConsolidada.objects.get(edital=edital_publicado)
    publish_retification(
        api_client, create_retification(api_client, edital_publicado, replace_vacancies(9))
    )

    assert vacancies_at(api_client, edital_publicado) == 9
    assert vacancies_at(api_client, edital_publicado, original.valid_from) == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_twenty_retifications_recompose_every_requested_version(api_client, edital_publicado):
    """SC-005: versão vigente e qualquer versão histórica em até 10 segundos por consulta."""
    fronteiras = []
    for numero in range(1, 21):
        vagas = 100 + numero
        retificacao = publish_retification(
            api_client,
            create_retification(
                api_client, edital_publicado, replace_vacancies(vagas), suffix=f"r{numero}"
            ),
            suffix=f"r{numero}",
        )
        fronteiras.append((retificacao.publication.effective_at, vagas))

    assert VersaoConsolidada.objects.filter(edital=edital_publicado).count() == 21

    inicio = time.monotonic()
    assert vacancies_at(api_client, edital_publicado) == 120
    for instante, esperado in fronteiras:
        assert vacancies_at(api_client, edital_publicado, instante) == esperado
    assert (time.monotonic() - inicio) / (len(fronteiras) + 1) < 10

    historico = api_client.get(
        f"/api/v1/public/editais/{edital_publicado.id}/historico", {"limit": 100}
    ).json()
    assert [item["kind"] for item in historico["items"]].count("RETIFICACAO") == 20
