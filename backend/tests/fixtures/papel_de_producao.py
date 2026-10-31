"""Os privilégios da role de produção na **própria conexão** da suíte, por `SET ROLE` (A-02).

**Por que existe.** A suíte conecta como superusuário, e o superusuário passa por cima de toda
negação de privilégio. O que só o privilégio recusa — `SELECT ... FOR UPDATE` numa tabela
append-only, que o PostgreSQL trata como escrita e a política nega — passava aqui e falhava em
produção. Foi assim duas vezes: a revogação da `106` e o julgamento com efeito (A-01, auditoria de
prontidão de 31/10/2026).

**Por que `SET ROLE`, e não uma conexão à parte.** A fixture `runtime_connection` já conecta como a
role de conformidade, mas é um `psycopg` cru: serve a SQL escrito à mão e não alcança um comando do
domínio, que fala com `django.db.connection`. Com `SET ROLE` na conexão do Django, o comando roda
inteiro — ORM, gatilhos, idempotência, trilha — e cada instrução é checada como seria em produção:
o PostgreSQL confere privilégio contra `current_user`, e o atributo de superusuário não acompanha o
`SET ROLE`.

**O papel é o da política real**, provisionado por `comandos()` exatamente como na fixture irmã —
e com os mesmos nomes, por worker e por banco. Montá-lo à mão faria o teste verificar a si mesmo.

**O preparo continua como superusuário, e só o ato examinado roda como produção.** As fixtures de
cenário usam atalhos que a role não tem (desligar gatilho, gravar estado direto), e o que se quer
provar é que *o comando* cabe nos privilégios — não a fixture.
"""

import contextlib

import pytest
from django.db import DatabaseError, connection

from tests.integration.test_database_permissions import (
    MIGRATION_PASSWORD,
    MIGRATION_ROLE,
    RUNTIME_PASSWORD,
    RUNTIME_ROLE,
    _remover_papeis,
    _skip_unless_superuser,
)


def assumir(conexao):
    """Passa `conexao` para a role de produção. Serve também à conexão de outra *thread*."""
    conexao.ensure_connection()
    with conexao.cursor() as cursor:
        cursor.execute(f'SET ROLE "{RUNTIME_ROLE}"')


def devolver(conexao):
    """Volta ao superusuário — e falha se a conexão deixou de ser a role no meio do caminho.

    **A conferência é a garantia de que o teste provou alguma coisa.** Se a conexão fosse fechada e
    reaberta durante o ato (um `close_old_connections`, uma reconexão), o resto dele rodaria como
    superusuário e passaria em silêncio. Ler `current_user` na saída é o que distingue "cabe nos
    privilégios" de "não chegou a ser checado".
    """
    if conexao.connection is None:
        raise AssertionError("a conexão foi fechada sob a role de produção: o ato não foi checado")
    if conexao.in_atomic_block and conexao.needs_rollback:
        # A transação do caso morreu; o `ROLLBACK` que o encerra desfaz o `SET` também.
        return
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT current_user")
            atual = cursor.fetchone()[0]
            cursor.execute("RESET ROLE")
    except DatabaseError:
        if conexao.in_atomic_block:
            return
        raise
    assert atual == RUNTIME_ROLE, f"o ato terminou como {atual!r}, e não como a role de produção"


@pytest.fixture
def como_producao(db):
    """Um gerenciador de contexto: o que roda dentro dele roda com os privilégios de produção.

    ```python
    with como_producao():
        julgar(...)
    ```

    Vale para casos transacionais e não transacionais. Nos segundos, papéis, propriedade e `SET`
    nascem dentro da transação do caso e morrem com o `ROLLBACK` dela — `CREATE ROLE` também é
    transacional —, e desfazê-los à mão só repetiria o problema das FKs pendentes; nos primeiros, a
    saída do contexto devolve a role e o fim da fixture desfaz a política.
    """
    _skip_unless_superuser()
    from processo_seletivo.seguranca.papeis import comandos

    no_caso = connection.in_atomic_block
    _remover_papeis()
    with connection.cursor() as cursor:
        if no_caso:
            # A política transfere a propriedade das tabelas, e o PostgreSQL recusa `ALTER TABLE`
            # sobre tabela com verificação de chave estrangeira pendente — que é o que as fixtures
            # deixam, porque o Django cria toda FK como `DEFERRABLE INITIALLY DEFERRED`. Verificar
            # agora esvazia a fila; voltar a adiar devolve o estado inicial, porque não há, neste
            # esquema, restrição adiável que nasça imediata.
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
        for instrucao in comandos(
            database=connection.settings_dict["NAME"],
            migration_role=MIGRATION_ROLE,
            migration_password=MIGRATION_PASSWORD,
            runtime_role=RUNTIME_ROLE,
            runtime_password=RUNTIME_PASSWORD,
        ):
            cursor.execute(instrucao)
        if no_caso:
            cursor.execute("SET CONSTRAINTS ALL DEFERRED")

    @contextlib.contextmanager
    def contexto(conexao=connection):
        assumir(conexao)
        try:
            yield
        finally:
            devolver(conexao)

    yield contexto
    if not no_caso:
        _remover_papeis()
