"""As leituras das telas de acesso cabem nos privilégios da role de runtime (107).

A suíte roda como superusuário, e uma leitura que dependesse de privilégio que a runtime não tem
passaria aqui e falharia em produção — foi o que a `106` descobriu na trava da revogação. Cada
consulta nova é executada, com o SQL que o ORM gera, pela conexão da role de runtime.
"""

import pytest
from django.db import connection

from processo_seletivo.seguranca import acessos as catalogo
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.models import Vinculo
from processo_seletivo.unidades.models import Unidade
from tests.integration.test_database_permissions import (  # noqa: F401  (fixture)
    RUNTIME_ROLE,
    runtime_connection,
)
from tests.seguranca.apoio import pessoa, vincular

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.integration,
    pytest.mark.skipif(
        connection.vendor != "postgresql", reason="privilégios validados somente em PostgreSQL"
    ),
]


def _consultas():
    bea = pessoa("bea", nome="Beatriz")
    vincular(bea, "cefor", "elaborador")
    return {
        "busca": acessos.pessoas_institucionais().filter(first_name__icontains="bea"),
        "vinculos da pessoa": acessos.vigentes()
        .filter(pessoa_id=bea.pk)
        .values_list("escopo", "papel"),
        "historico": Vinculo.objects.filter(escopo__in=["cefor"]).select_related(
            "pessoa", "revogacao"
        ),
        "administradores": acessos.vigentes()
        .filter(papel=catalogo.ADMINISTRADOR_DE_ACESSOS)
        .select_related("pessoa"),
        "unidades": Unidade.objects.order_by("codigo"),
    }


def test_a_runtime_le_tudo_o_que_as_telas_leem(runtime_connection):  # noqa: F811
    for nome, consulta in _consultas().items():
        sql, parametros = consulta.query.sql_with_params()
        with runtime_connection.cursor() as cursor:
            cursor.execute(sql, parametros)
            assert cursor.fetchall() is not None, nome


def test_a_runtime_renova_a_sessao(runtime_connection):  # noqa: F811
    """A renovação da atividade grava a sessão a cada requisição (`D-009`)."""
    with runtime_connection.cursor() as cursor:
        for privilegio in ("SELECT", "INSERT", "UPDATE"):
            cursor.execute(
                "SELECT has_table_privilege(%s, 'django_session', %s)", [RUNTIME_ROLE, privilegio]
            )
            assert cursor.fetchone()[0] is True, privilegio
