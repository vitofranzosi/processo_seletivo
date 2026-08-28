import pytest

from processo_seletivo.processos.models import AtoAdministrativo, Edital, ProcessoSeletivo
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import publish_original

GESTOR = ["processo:encerrar", "processo:cancelar", "edital:encerrar", "edital:cancelar"]


def act(api_client, url, *, revision, reason="Ato motivado", key="finalizacao-key-0001"):
    return api_client.post(
        url,
        {"reason": reason},
        format="json",
        **actor_headers("gestor", GESTOR, if_match=revision, key=key),
    )


@pytest.mark.django_db
@pytest.mark.contract
def test_closing_an_edital_returns_the_admin_projection_and_new_etag(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    response = act(
        api_client, f"/api/v1/admin/editais/{edital.id}/encerramentos", revision=edital.revision
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"id", "processoId", "status", "revision"}
    assert body["status"] == "ENCERRADO"
    assert body["revision"] == edital.revision + 1
    assert response["ETag"] == f'"{edital.revision + 1}"'


@pytest.mark.django_db
@pytest.mark.contract
def test_cancelling_an_edital_records_the_administrative_act(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    response = act(
        api_client,
        f"/api/v1/admin/editais/{edital.id}/cancelamentos",
        revision=edital.revision,
        reason="Interrupção por decisão superior",
    )
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELADO"
    ato = AtoAdministrativo.objects.get(aggregate_id=edital.id, operation="CANCELAR")
    assert ato.reason == "Interrupção por decisão superior"
    assert ato.actor_subject == "gestor"


@pytest.mark.django_db
@pytest.mark.contract
def test_closing_a_process_returns_the_process_projection(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    processo = edital.processo
    api_client.post(
        f"/api/v1/admin/processos/{processo.id}/ativacoes",
        {"reason": "Abertura"},
        format="json",
        **{**manager_headers, "HTTP_IF_MATCH": '"1"', "HTTP_IDEMPOTENCY_KEY": "ativacao-key-00001"},
    )
    response = act(
        api_client,
        f"/api/v1/admin/processos/{processo.id}/encerramentos",
        revision=2,
        key="finalizacao-key-0002",
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"id", "institutionalCode", "status", "revision"}
    assert body["status"] == "ENCERRADO"


@pytest.mark.django_db
@pytest.mark.contract
def test_finalization_requires_if_match(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    response = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/encerramentos",
        {"reason": "Sem precondição"},
        format="json",
        **actor_headers("gestor", GESTOR),
    )
    assert response.status_code == 428
    assert response.json()["code"] == "precondition_required"


@pytest.mark.django_db
@pytest.mark.contract
def test_finalization_rejects_stale_revision(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    response = act(api_client, f"/api/v1/admin/editais/{edital.id}/encerramentos", revision=1)
    assert response.status_code == 412
    assert response.json()["code"] == "stale_revision"


@pytest.mark.django_db
@pytest.mark.contract
def test_finalization_requires_a_reason(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    response = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/encerramentos",
        {},
        format="json",
        **actor_headers("gestor", GESTOR, if_match=edital.revision),
    )
    assert response.status_code == 400
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.PUBLICADO


@pytest.mark.django_db
@pytest.mark.contract
def test_finalization_is_idempotent_for_the_same_key(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    url = f"/api/v1/admin/editais/{edital.id}/encerramentos"
    primeira = act(api_client, url, revision=edital.revision, key="encerrar-key-000001")
    repetida = act(api_client, url, revision=edital.revision, key="encerrar-key-000001")
    assert primeira.status_code == repetida.status_code == 200
    assert primeira.json()["revision"] == repetida.json()["revision"]
    assert (
        AtoAdministrativo.objects.filter(aggregate_id=edital.id, operation="ENCERRAR").count() == 1
    )


@pytest.mark.django_db
@pytest.mark.contract
def test_cancelling_a_process_with_open_editais_conflicts(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    response = act(
        api_client,
        f"/api/v1/admin/processos/{edital.processo_id}/cancelamentos",
        revision=ProcessoSeletivo.objects.get(pk=edital.processo_id).revision,
    )
    assert response.status_code == 409
    corpo = response.json()
    assert corpo["code"] == "editais_pendentes"
    assert f"{edital.number}/{edital.year}" in corpo["detail"]
