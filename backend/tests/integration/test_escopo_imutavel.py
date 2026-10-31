"""O escopo de Processo Seletivo e de Edital não muda depois de criado (110, FR-3333, FR-3334).

O escopo é a unidade do certame. Até a `110`, um `QuerySet.update()` ou um SQL direto moveria um
Edital para outra unidade sem que nada recusasse; os gatilhos de `processos/0005` recusam a mudança,
e só ela: o `save()` completo regrava o mesmo valor e passa, e as outras colunas continuam mudando.

Os casos rodam com a conexão da suíte, que é superusuária. É a prova mais forte: o gatilho não
depende de privilégio, e o que recusa o superusuário recusa a role de runtime. Fora do PostgreSQL o
gatilho não existe, e os casos são pulados — fingi-lo afirmaria uma garantia que não existe ali.
"""

import pytest
from django.db import DatabaseError, connection, transaction

from processo_seletivo.processos.models import Edital, ProcessoSeletivo

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

so_postgresql = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho validado somente no PostgreSQL"
)

TABELAS = {ProcessoSeletivo: "processos_processoseletivo", Edital: "processos_edital"}


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    """Um Processo e o primeiro Edital, do Cefor, pelo canal administrativo."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.select_related("processo").get(processo_id=criado.json()["id"])


def _objetos(edital):
    return [edital.processo, edital]


@so_postgresql
def test_as_tabelas_sao_as_que_os_gatilhos_nomeiam():
    """A migration escreve os nomes à mão; se o modelo mudar de tabela, o gatilho fica órfão."""
    assert {modelo: modelo._meta.db_table for modelo in TABELAS} == TABELAS


@so_postgresql
def test_update_do_escopo_e_recusado(edital):
    for objeto in _objetos(edital):
        with pytest.raises(DatabaseError, match="institution scope"), transaction.atomic():
            type(objeto).objects.filter(pk=objeto.pk).update(institution_scope="serra")
        objeto.refresh_from_db()
        assert objeto.institution_scope == "cefor"


@so_postgresql
def test_save_que_muda_o_escopo_e_recusado(edital):
    for objeto in _objetos(edital):
        objeto.institution_scope = "serra"
        with pytest.raises(DatabaseError, match="institution scope"), transaction.atomic():
            objeto.save()
        objeto.refresh_from_db()
        assert objeto.institution_scope == "cefor"


@so_postgresql
def test_sql_direto_e_recusado(edital):
    for modelo, tabela in TABELAS.items():
        objeto = edital.processo if modelo is ProcessoSeletivo else edital
        with pytest.raises(DatabaseError, match="institution scope"), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    f"UPDATE {tabela} SET institution_scope = %s WHERE id = %s",  # noqa: S608
                    ["serra", objeto.pk],
                )
        objeto.refresh_from_db()
        assert objeto.institution_scope == "cefor"


@so_postgresql
def test_save_sem_mudanca_e_aceito(edital):
    """`IS DISTINCT FROM`: o `save()` completo regrava o mesmo escopo, e isso não é mudança."""
    for objeto in _objetos(edital):
        objeto.title = f"{objeto.title} (revisto)"
        objeto.save()
        type(objeto).objects.filter(pk=objeto.pk).update(institution_scope="cefor")
        objeto.refresh_from_db()
        assert objeto.title.endswith("(revisto)")
        assert objeto.institution_scope == "cefor"


@so_postgresql
def test_os_gatilhos_da_060_continuam():
    """FR-3334: a `0005` acrescenta dois gatilhos, e não toca nos do registro de unidades."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT tgname FROM pg_trigger WHERE NOT tgisinternal")
        instalados = {linha[0] for linha in cursor.fetchall()}
    assert {
        "processo_escopo_imutavel",
        "edital_escopo_imutavel",
        "unidade_codigo_imutavel",
        "unidade_nao_se_exclui",
    } <= instalados
