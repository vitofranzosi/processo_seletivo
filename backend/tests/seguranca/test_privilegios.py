"""A concessão e a revogação cabem nos privilégios da role de runtime (106).

**A suíte roda como superusuário, e por isso não via o defeito.** A primeira versão da revogação
trancava o vínculo com `SELECT ... FOR UPDATE`, que exige o privilégio de `UPDATE` — e a role de
runtime não o tem sobre as tabelas append-only. Em produção, toda revogação seria recusada com
`permission denied`. A trava passou para a pessoa, e estes casos prendem as duas metades: o que a
role pode trancar, e que o código só tranca isso.
"""

import ast
import pathlib

import psycopg
import pytest
from django.db import connection

from tests.integration.test_database_permissions import (  # noqa: F401  (fixture)
    RUNTIME_ROLE,
    runtime_connection,
)

RAIZ = pathlib.Path(__file__).resolve().parents[2] / "processo_seletivo" / "seguranca"

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="privilégios validados somente em PostgreSQL"
)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_a_runtime_tranca_a_pessoa_e_nao_os_registros_append_only(runtime_connection):  # noqa: F811
    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT id FROM auth_user FOR UPDATE")
        for privilegio in ("SELECT", "INSERT", "UPDATE"):
            cursor.execute(
                "SELECT has_table_privilege(%s, 'auth_user', %s)", [RUNTIME_ROLE, privilegio]
            )
            assert cursor.fetchone()[0] is True, f"a entrada precisa de {privilegio} na pessoa"
    for tabela in ("seguranca_vinculo", "seguranca_revogacaodevinculo"):
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with runtime_connection.cursor() as cursor:
                cursor.execute(f"SELECT id FROM {tabela} FOR UPDATE")


def test_o_codigo_da_106_so_tranca_a_pessoa():
    """Todo `select_for_update` do app parte de `get_user_model().objects`."""
    travas = []
    for arquivo in RAIZ.rglob("*.py"):
        if "migrations" in arquivo.parts:
            continue
        for no in ast.walk(ast.parse(arquivo.read_text())):
            if isinstance(no, ast.Attribute) and no.attr == "select_for_update":
                travas.append((arquivo.name, ast.unparse(no.value)))
    assert travas
    assert {origem for _, origem in travas} == {"get_user_model().objects"}, travas
