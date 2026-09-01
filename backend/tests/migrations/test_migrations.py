"""T089 — as migrations aplicam do zero e a partir da versão anterior, sem reescrita.

A Constituição proíbe reescrever migration já aplicada: correções entram como migration
nova. Estes testes protegem as duas rotas que a produção percorre — instalação limpa e
upgrade incremental — e verificam que os objetos de banco criados fora do ORM (triggers)
sobrevivem às duas.
"""

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader

APPS = ("processos", "editais", "publicacoes", "auditoria")
TRIGGERS = (
    "auditoria_append_only",
    "publicacao_append_only",
    "documento_publicado_append_only",
    "versao_consolidada_append_only",
    # FR-023 da 003: as duas primeiras são condicionais ao estado final, porque Retificação e
    # Alteração mudam legitimamente enquanto o ato está em curso; as duas últimas são absolutas.
    "retificacao_final_imutavel",
    "alteracao_normativa_final_imutavel",
    "ato_administrativo_append_only",
    "revisao_edital_append_only",
)

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="migrations validadas em PostgreSQL"
)


def _installed_triggers():
    with connection.cursor() as cursor:
        cursor.execute("SELECT tgname FROM pg_trigger WHERE NOT tgisinternal")
        return {row[0] for row in cursor.fetchall()}


def _plan_to(executor, targets):
    return executor.migration_plan(targets)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_migration_graph_has_a_single_leaf_per_app():
    """Dois leaf nodes no mesmo app quebram qualquer migrate; falhou uma vez neste repo."""
    loader = MigrationLoader(connection)
    for app in APPS:
        leaves = [node for node in loader.graph.leaf_nodes() if node[0] == app]
        assert len(leaves) == 1, f"{app} tem múltiplos leaf nodes: {leaves}"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_every_migration_declares_a_reverse_path():
    """Sem reversão não há rollback de deploy; RunPython precisa de função inversa."""
    loader = MigrationLoader(connection)
    irreversiveis = []
    for (app, name), migration in loader.disk_migrations.items():
        if app not in APPS:
            continue
        for operation in migration.operations:
            if not operation.reversible:
                irreversiveis.append(f"{app}.{name}: {operation.__class__.__name__}")
    assert not irreversiveis, f"operações irreversíveis: {irreversiveis}"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_migrations_apply_from_scratch_and_recreate_the_triggers():
    executor = MigrationExecutor(connection)
    alvos = [(app, None) for app in APPS]

    executor.migrate(alvos)  # desfaz tudo
    assert not _installed_triggers() & set(TRIGGERS)

    executor.loader.build_graph()
    completos = [node for node in executor.loader.graph.leaf_nodes() if node[0] in APPS]
    executor.migrate(completos)

    assert set(TRIGGERS) <= _installed_triggers()
    executor.loader.build_graph()
    assert not _plan_to(executor, completos), "migrate do zero deixou plano pendente"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_upgrade_from_the_previous_version_applies_only_the_new_migrations():
    """Instalação já existente na penúltima migration de publicacoes avança sem reescrever."""
    executor = MigrationExecutor(connection)
    executor.loader.build_graph()
    publicacoes = sorted(
        name for app, name in executor.loader.disk_migrations if app == "publicacoes"
    )
    assert len(publicacoes) >= 2, "o teste pressupõe histórico incremental em publicacoes"
    anterior, ultima = publicacoes[-2], publicacoes[-1]

    executor.migrate([("publicacoes", anterior)])
    executor.loader.build_graph()
    aplicadas = executor.loader.applied_migrations
    assert ("publicacoes", anterior) in aplicadas
    assert ("publicacoes", ultima) not in aplicadas

    plano = _plan_to(executor, [("publicacoes", ultima)])
    assert [str(migration) for migration, _ in plano] == [f"publicacoes.{ultima}"]

    executor.migrate([("publicacoes", ultima)])
    assert set(TRIGGERS) <= _installed_triggers()

    executor.loader.build_graph()
    assert ("publicacoes", ultima) in executor.loader.applied_migrations


DOMINIO_OU_APLICACAO = ("domain", "application")


def _modulos_de_migration():
    from importlib import import_module
    from pathlib import Path

    for app in APPS:
        pacote = import_module(f"processo_seletivo.{app}.migrations")
        pasta = Path(pacote.__file__).parent
        for arquivo in sorted(pasta.glob("[0-9]*.py")):
            yield f"processo_seletivo/{app}/migrations/{arquivo.name}", arquivo.read_text(
                encoding="utf-8"
            )


def test_migrations_do_not_import_domain_or_application_code():
    """Migration aplicada tem de continuar significando o que significava no dia em que rodou.

    Importar uma função do domínio faz uma alteração futura nela mudar retroativamente o efeito
    de uma migration já executada em produção. A lógica de que a migration precisa é copiada e
    congelada dentro dela; a duplicação é o preço de a história ser fixa.
    """
    infratores = [
        (caminho, linha.strip())
        for caminho, fonte in _modulos_de_migration()
        for linha in fonte.splitlines()
        if linha.startswith(("import processo_seletivo", "from processo_seletivo"))
        and any(f".{camada}" in linha for camada in DOMINIO_OU_APLICACAO)
    ]
    assert not infratores, f"migrations acopladas ao código vivo: {infratores}"


def test_a_011_nao_altera_o_esquema_de_outros_apps():
    """FR-083 e SC-018: a comissão é operacional, e não toca o normativo.

    A tentação concreta que isto bloqueia tem nome — acrescentar `avaliadores_exigidos` à Etapa —
    e ela mudaria conteúdo normativo publicável por necessidade operacional (011, D-005).
    """
    import pathlib as _pathlib

    raiz = _pathlib.Path(__file__).resolve().parents[2] / "processo_seletivo"
    migrations = sorted((raiz / "comissoes" / "migrations").glob("[0-9]*.py"))
    assert migrations, "a 011 precisa ter ao menos uma migration"

    for arquivo in migrations:
        corpo = arquivo.read_text()
        for app_alheio in ("editais", "publicacoes", "auditoria", "inscricoes"):
            assert f'"{app_alheio}' not in corpo.lower(), f"{arquivo.name} toca {app_alheio}"
