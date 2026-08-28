import pytest
from django.core.management import call_command
from django.db import DatabaseError, connection
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import ProcessoSeletivo
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.concurrency import compare_and_swap


@pytest.mark.django_db
@pytest.mark.integration
def test_compare_and_swap_rejects_stale_revision():
    processo = ProcessoSeletivo.objects.create(
        institution_scope="cefor",
        institutional_code="CAS-1",
        title="CAS",
        created_at=timezone.now(),
        created_by="actor",
        last_changed_at=timezone.now(),
    )
    assert (
        compare_and_swap(
            ProcessoSeletivo.objects, pk=processo.pk, expected_revision=1, title="novo"
        )
        == 2
    )
    with pytest.raises(DomainError) as error:
        compare_and_swap(
            ProcessoSeletivo.objects, pk=processo.pk, expected_revision=1, title="obsoleto"
        )
    assert error.value.status == 412


@pytest.mark.django_db
@pytest.mark.integration
def test_model_rejects_audit_update_and_delete():
    event = RegistroAuditoria.objects.create(
        occurred_at=timezone.now(),
        actor_subject="actor",
        permission="p",
        institution_scope="cefor",
        operation="TEST",
        aggregate_type="Processo",
        aggregate_id="00000000-0000-0000-0000-000000000001",
        correlation_id="c",
    )
    event.operation = "MUTATED"
    with pytest.raises(TypeError):
        event.save()
    with pytest.raises(TypeError):
        event.delete()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_postgresql_trigger_rejects_bulk_mutation():
    if connection.vendor != "postgresql":
        pytest.skip("garantia do banco validada somente em PostgreSQL")
    event = RegistroAuditoria.objects.create(
        occurred_at=timezone.now(),
        actor_subject="actor",
        permission="p",
        institution_scope="cefor",
        operation="TEST",
        aggregate_type="Processo",
        aggregate_id="00000000-0000-0000-0000-000000000001",
        correlation_id="c",
    )
    with pytest.raises(DatabaseError):
        RegistroAuditoria.objects.filter(pk=event.pk).update(operation="MUTATED")


@pytest.mark.django_db
@pytest.mark.integration
def test_models_have_no_pending_migrations():
    call_command("makemigrations", check=True, dry_run=True, verbosity=0)
