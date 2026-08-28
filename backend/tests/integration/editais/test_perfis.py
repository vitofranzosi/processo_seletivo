from uuid import uuid4

import pytest
from django.db import IntegrityError, transaction

from processo_seletivo.editais.models.perfis import PerfilVaga
from processo_seletivo.processos.models import Edital


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_profile_code_is_unique_only_inside_its_edital(
    api_client, manager_headers, process_payload
):
    created = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    processo_id = created.json()["id"]
    second_headers = {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "profile-second-edital"}
    api_client.post(
        f"/api/v1/admin/processos/{processo_id}/editais",
        {"number": "02", "year": 2026, "title": "Segundo"},
        format="json",
        **second_headers,
    )
    first, second = Edital.objects.order_by("number")
    PerfilVaga.objects.create(
        id=uuid4(), edital=first, code="P1", name="Perfil", immediate_vacancies=1
    )
    PerfilVaga.objects.create(
        id=uuid4(), edital=second, code="P1", name="Perfil", immediate_vacancies=1
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        PerfilVaga.objects.create(
            id=uuid4(), edital=first, code="P1", name="Duplicado", immediate_vacancies=1
        )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_database_rejects_incompatible_reserve_limit(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    with pytest.raises(IntegrityError), transaction.atomic():
        PerfilVaga.objects.create(
            edital=edital,
            code="P1",
            name="Inválido",
            immediate_vacancies=0,
            reserve_type="NONE",
            reserve_limit=1,
        )
