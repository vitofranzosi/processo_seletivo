"""T088 e FR-019 da 003 — defesa em profundidade dos registros append-only.

Duas camadas independentes: a role de runtime não recebe UPDATE/DELETE, e o trigger
recusa a mutação mesmo para quem tiver o privilégio. Cada uma é verificada isolada,
para que a falha de uma não seja mascarada pela outra.

A role de conformidade é provisionada **pela mesma política** que o comando `provisionar_papeis`
aplica em produção. Montá-la aqui à mão faria o teste verificar a si mesmo: passaria mesmo que o
provisionamento real concedesse privilégio demais.
"""

import psycopg
import pytest
from django.db import DatabaseError, connection

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.seguranca.papeis import (
    TABELAS_APPEND_ONLY,
    comandos,
    comandos_de_privilegios,
)
from tests.fixtures.publicacao import publish_original

RUNTIME_ROLE = "ps_runtime_conformance"
MIGRATION_ROLE = "ps_migration_conformance"
RUNTIME_PASSWORD = "conformance-only"
MIGRATION_PASSWORD = "conformance-migration"
# Chave primária de cada tabela append-only, usada no UPDATE inócuo que testa o privilégio.
CHAVES = {"auditoria_registroauditoria": "event_id"}
APPEND_ONLY = tuple((tabela, CHAVES.get(tabela, "id")) for tabela in TABELAS_APPEND_ONLY)
APPEND_ONLY_TABLES = TABELAS_APPEND_ONLY

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="privilégios validados somente em PostgreSQL"
)


def _skip_unless_superuser():
    with connection.cursor() as cursor:
        cursor.execute("SELECT usesuper FROM pg_user WHERE usename = current_user")
        row = cursor.fetchone()
    if not (row and row[0]):
        pytest.skip("criar a role de conformidade exige superusuário")


def _remover_papeis():
    with connection.cursor() as cursor:
        for papel in (RUNTIME_ROLE, MIGRATION_ROLE):
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [papel])
            if cursor.fetchone():
                # A política transfere a propriedade das tabelas e do schema para o papel de
                # migração; sem devolvê-la antes, `DROP OWNED BY` levaria o banco de teste junto.
                cursor.execute(f'REASSIGN OWNED BY "{papel}" TO CURRENT_USER')
                cursor.execute(f'DROP OWNED BY "{papel}"')
                cursor.execute(f'DROP ROLE "{papel}"')


@pytest.fixture
def runtime_connection():
    """Role sem UPDATE/DELETE, como a role de runtime descrita em .env.example."""
    _skip_unless_superuser()
    database = connection.settings_dict["NAME"]
    _remover_papeis()
    with connection.cursor() as cursor:
        for instrucao in comandos(
            database=database,
            migration_role=MIGRATION_ROLE,
            migration_password=MIGRATION_PASSWORD,
            runtime_role=RUNTIME_ROLE,
            runtime_password=RUNTIME_PASSWORD,
        ):
            cursor.execute(instrucao)

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
        _remover_papeis()


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


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
@pytest.mark.parametrize(
    "table", ("publicacoes_retificacao", "publicacoes_alteracaonormativa", "processos_edital")
)
def test_runtime_role_keeps_update_where_the_flow_needs_it(runtime_connection, table):
    """A política não pode ser generosa demais nem restritiva demais.

    Retificação transita de estado e Alteração é substituída a cada edição de rascunho: negar
    `UPDATE` nelas quebraria o fluxo. A imutabilidade delas é condicional ao estado final, o que
    só a trigger consegue expressar — privilégio não distingue linha de linha.
    """
    with runtime_connection.cursor() as cursor:
        for privilegio in ("UPDATE", "DELETE"):
            cursor.execute(
                "SELECT has_table_privilege(%s, %s, %s)", [RUNTIME_ROLE, table, privilegio]
            )
            assert cursor.fetchone()[0] is True, f"{table} precisa de {privilegio}"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_provisionamento_e_idempotente(runtime_connection):
    """Rodar de novo sobre banco já provisionado não pode falhar nem afrouxar a política."""
    with connection.cursor() as cursor:
        for instrucao in comandos(
            database=connection.settings_dict["NAME"],
            migration_role=MIGRATION_ROLE,
            migration_password=MIGRATION_PASSWORD,
            runtime_role=RUNTIME_ROLE,
            runtime_password=RUNTIME_PASSWORD,
        ):
            cursor.execute(instrucao)
        for tabela in APPEND_ONLY_TABLES:
            cursor.execute(
                "SELECT has_table_privilege(%s, %s, 'UPDATE')", [RUNTIME_ROLE, tabela]
            )
            assert cursor.fetchone()[0] is False, tabela


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_o_comando_imprime_a_politica_sem_executar():
    """`--dry-run` é o que permite revisar o que será aplicado antes de aplicá-lo."""
    from io import StringIO

    from django.core.management import call_command

    saida = StringIO()
    call_command(
        "provisionar_papeis",
        "--dry-run",
        "--migration-role=ps_migration_dry",
        "--migration-password=segredo-de-migracao",
        "--runtime-role=ps_runtime_dry",
        "--runtime-password=segredo-de-runtime",
        stdout=saida,
    )

    texto = saida.getvalue()
    assert "CREATE ROLE" in texto
    assert "REVOKE UPDATE, DELETE" in texto
    # `--dry-run` existe para ser lido, colado em revisão e anexado a chamado.
    assert "segredo-de-migracao" not in texto
    assert "segredo-de-runtime" not in texto
    assert "PASSWORD '********'" in texto
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'ps_runtime_dry'")
        assert cursor.fetchone() is None


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_comando_exige_os_papeis_e_a_senha():
    """Sem eles o provisionamento aplicaria a política a um papel que ninguém declarou."""
    from django.core.management import CommandError, call_command

    with pytest.raises(CommandError) as recusa:
        call_command(
            "provisionar_papeis",
            "--migration-role=",
            "--migration-password=",
            "--runtime-role=",
            "--runtime-password=",
        )

    for esperado in (
        "--migration-role",
        "--migration-password",
        "--runtime-role",
        "--runtime-password",
    ):
        assert esperado in str(recusa.value)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@pytest.mark.skipif(
    connection.vendor == "postgresql", reason="a recusa por vendor só aparece fora do PostgreSQL"
)
def test_o_comando_recusa_banco_que_nao_seja_postgresql():
    from django.core.management import CommandError, call_command

    with pytest.raises(CommandError, match="PostgreSQL"):
        call_command(
            "provisionar_papeis",
            "--migration-role=m",
            "--migration-password=s",
            "--runtime-role=r",
            "--runtime-password=s",
        )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_a_revogacao_ignora_tabela_que_ainda_nao_existe(runtime_connection):
    """FR-019: a primeira passada roda em banco vazio, antes de qualquer migration.

    O `REVOKE` nominal falhava com `relation ... does not exist` e derrubava o provisionamento
    inteiro — o que tornava a ordem impossível de fechar: não havia como conceder privilégio de
    tabela antes das migrations, nem como migrar antes de existir papel para migrar.
    """
    with connection.cursor() as cursor:
        for instrucao in comandos_de_privilegios(
            migration_role=MIGRATION_ROLE,
            runtime_role=RUNTIME_ROLE,
            tabelas=("tabela_que_ainda_nao_existe", "auditoria_registroauditoria"),
        ):
            cursor.execute(instrucao)
        cursor.execute(
            "SELECT has_table_privilege(%s, %s, 'UPDATE')",
            [RUNTIME_ROLE, "auditoria_registroauditoria"],
        )
        assert cursor.fetchone()[0] is False, "a tabela que existe precisa ter sido trancada"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_o_papel_de_migracao_e_dono_das_tabelas(runtime_connection):
    """`GRANT ALL` deixa usar a tabela; `ALTER TABLE` exige ser dono.

    Sem a transferência de propriedade, um esquema criado pelo superusuário faz a próxima
    migration falhar em produção, no meio do deploy.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT tableowner FROM pg_tables "
            "WHERE schemaname = 'public' AND tablename = 'publicacoes_publicacao'"
        )
        assert cursor.fetchone()[0] == MIGRATION_ROLE


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_o_papel_de_migracao_tem_senha(runtime_connection):
    """`.env.example` sempre declarou `DB_MIGRATION_PASSWORD`; o papel nascia sem senha alguma."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT rolpassword IS NOT NULL FROM pg_authid WHERE rolname = %s", [MIGRATION_ROLE]
        )
        linha = cursor.fetchone()
    if linha is None:
        pytest.skip("ler pg_authid exige superusuário")
    assert linha[0] is True
