from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from processo_seletivo.editais.models.cronograma import Cronograma, EventoCronograma
from processo_seletivo.processos.models import Edital


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_database_rejects_event_with_end_before_start(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    cronograma = Cronograma.objects.create(edital=Edital.objects.get())
    start = timezone.now()
    with pytest.raises(IntegrityError), transaction.atomic():
        EventoCronograma.objects.create(
            cronograma=cronograma,
            type="INSCRICAO",
            description="Inválido",
            start_at=start,
            end_at=start - timedelta(days=1),
            order=1,
        )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_each_edital_has_an_independent_schedule(api_client, manager_headers, process_payload):
    created = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    api_client.post(
        f"/api/v1/admin/processos/{created.json()['id']}/editais",
        {"number": "02", "year": 2026, "title": "Segundo"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "schedule-second-edital"},
    )
    first, second = Edital.objects.order_by("number")
    first_schedule = Cronograma.objects.create(edital=first)
    second_schedule = Cronograma.objects.create(edital=second)
    assert first_schedule.id != second_schedule.id
    assert first_schedule.edital_id != second_schedule.edital_id
