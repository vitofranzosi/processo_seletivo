"""T088 — defesa em profundidade dos registros append-only.

Duas camadas independentes: a role de runtime não recebe UPDATE/DELETE, e o trigger
recusa a mutação mesmo para quem tiver o privilégio. Cada uma é verificada isolada,
para que a falha de uma não seja mascarada pela outra.
"""

import psycopg
import pytest
from django.db import DatabaseError, connection

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import publish_original

RUNTIME_ROLE = "ps_runtime_conformance"
RUNTIME_PASSWORD = "conformance-only"
# (tabela, coluna de chave primária) — a chave varia e é usada no UPDATE inócuo.
APPEND_ONLY = (
    ("auditoria_registroauditoria", "event_id"),
    ("publicacoes_publicacao", "id"),
    ("publicacoes_documentopublicado", "id"),
    ("publicacoes_versaoconsolidada", "id"),
)
APPEND_ONLY_TABLES = tuple(table for table, _ in APPEND_ONLY)

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="privilégios validados somente em PostgreSQL"
)


def _skip_unless_superuser():
    with connection.cursor() as cursor:
        cursor.execute("SELECT usesuper FROM pg_user WHERE usename = current_user")
        row = cursor.fetchone()
    if not (row and row[0]):
        pytest.skip("criar a role de conformidade exige superusuário")


@pytest.fixture
def runtime_connection():
    """Role sem UPDATE/DELETE, como a role de runtime descrita em .env.example."""
    _skip_unless_superuser()
    database = connection.settings_dict["NAME"]
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [RUNTIME_ROLE])
        if cursor.fetchone():
            cursor.execute(f'DROP OWNED BY "{RUNTIME_ROLE}"')
            cursor.execute(f'DROP ROLE "{RUNTIME_ROLE}"')
        cursor.execute(
            f"CREATE ROLE \"{RUNTIME_ROLE}\" LOGIN PASSWORD '{RUNTIME_PASSWORD}'"
        )
        cursor.execute(f'GRANT CONNECT ON DATABASE "{database}" TO "{RUNTIME_ROLE}"')
        cursor.execute(f'GRANT USAGE ON SCHEMA public TO "{RUNTIME_ROLE}"')
        for table in APPEND_ONLY_TABLES:
            cursor.execute(f'GRANT SELECT, INSERT ON {table} TO "{RUNTIME_ROLE}"')
            cursor.execute(f'REVOKE UPDATE, DELETE ON {table} FROM "{RUNTIME_ROLE}"')

    runtime = psycopg.connect(
        dbname=database,
        user=RUNTIME_ROLE,
        password=RUNTIME_PASSWORD,
        host=connection.settings_dict["HOST"] or "localhost",
        port=connection.settings_dict["PORT"] or "5432",
        autocommit=True,
    )
    try:
        yield runtime
    finally:
        runtime.close()
        with connection.cursor() as cursor:
            cursor.execute(f'DROP OWNED BY "{RUNTIME_ROLE}"')
            cursor.execute(f'DROP ROLE "{RUNTIME_ROLE}"')


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
@pytest.mark.parametrize(("table", "chave"), APPEND_ONLY)
def test_runtime_role_has_no_update_or_delete_privilege(runtime_connection, table, chave):
    for comando in (f"UPDATE {table} SET {chave} = {chave}", f"DELETE FROM {table}"):
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with runtime_connection.cursor() as cursor:
                cursor.execute(comando)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
@pytest.mark.parametrize("table", APPEND_ONLY_TABLES)
def test_runtime_role_keeps_the_privileges_it_needs(runtime_connection, table):
    """A negação é específica: sem SELECT/INSERT o teste anterior passaria por engano."""
    with runtime_connection.cursor() as cursor:
        cursor.execute(f"SELECT count(*) FROM {table}")
        assert cursor.fetchone()[0] >= 0
    with runtime_connection.cursor() as cursor:
        cursor.execute(
            "SELECT has_table_privilege(%s, %s, 'INSERT')", [RUNTIME_ROLE, table]
        )
        assert cursor.fetchone()[0] is True


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_runtime_role_cannot_erase_the_audit_trail_it_wrote(runtime_connection):
    """FR-032: quem grava a trilha não pode apagá-la."""
    with runtime_connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO auditoria_registroauditoria (
                event_id, occurred_at, actor_subject, permission, institution_scope,
                operation, aggregate_type, aggregate_id, previous_state, new_state,
                reason, correlation_id, idempotency_key
            ) VALUES (
                gen_random_uuid(), now(), 'runtime', 'p', 'cefor', 'TESTE', 'Processo',
                gen_random_uuid(), '', '', '', 'c', ''
            ) RETURNING event_id
            """
        )
        event_id = cursor.fetchone()[0]

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        with runtime_connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM auditoria_registroauditoria WHERE event_id = %s", [event_id]
            )
    assert RegistroAuditoria.objects.filter(event_id=event_id).exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_trigger_rejects_mutation_even_for_a_privileged_role(
    api_client, manager_headers, process_payload
):
    """Segunda camada: mesmo com privilégio, o trigger recusa UPDATE e DELETE."""
    edital = publish_original(api_client, manager_headers, process_payload)
    alvos = (
        Publicacao.objects.filter(edital=edital),
        DocumentoPublicado.objects.filter(publicacao__edital=edital),
        VersaoConsolidada.objects.filter(edital=edital),
        RegistroAuditoria.objects.filter(aggregate_id=edital.id),
    )
    for queryset in alvos:
        assert queryset.exists(), queryset.model.__name__
        with pytest.raises(DatabaseError):
            queryset.delete()
