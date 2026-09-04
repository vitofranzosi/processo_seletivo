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

# `avaliacoes` e `resultados` entram na revisão de 012–013: até aqui nenhuma migration deles era
# exercida por teste de upgrade, e são justamente os dois que a revisão mais mexe — três backfills
# sobre tabelas com histórico, duas delas protegidas contra `UPDATE` por trigger.
APPS = ("processos", "editais", "publicacoes", "auditoria", "avaliacoes", "resultados")
# Agrupadas pelo app que as cria, porque o teste de upgrade incremental exercita **um** app por vez:
# voltar `publicacoes` uma migration desaplica também o que depende dela, e exigir ali o conjunto
# inteiro cobraria triggers de apps que o próprio teste acabou de desmontar.
TRIGGERS_POR_APP = {
    "auditoria": ("auditoria_append_only",),
    "processos": ("ato_administrativo_append_only",),
    "publicacoes": (
        "publicacao_append_only",
        "documento_publicado_append_only",
        "versao_consolidada_append_only",
        # FR-023 da 003: as duas primeiras são condicionais ao estado final, porque Retificação e
        # Alteração mudam legitimamente enquanto o ato está em curso; as duas últimas são absolutas.
        "retificacao_final_imutavel",
        "alteracao_normativa_final_imutavel",
        "revisao_edital_append_only",
    ),
    # A conclusão preservada da 012 e o Resultado da 013. A última não é append-only: é a
    # conferência que impede o Resultado de afirmar o que a Avaliação fonte não afirmou.
    "avaliacoes": ("conclusao_avaliacao_append_only",),
    "resultados": ("resultado_etapa_append_only", "resultado_etapa_coerente"),
}
TRIGGERS = tuple(nome for grupo in TRIGGERS_POR_APP.values() for nome in grupo)

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
    # As de `publicacoes`, e não o conjunto inteiro: voltar este app desaplicou o que depende dele.
    assert set(TRIGGERS_POR_APP["publicacoes"]) <= _installed_triggers()

    executor.loader.build_graph()
    assert ("publicacoes", ultima) in executor.loader.applied_migrations


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_o_salto_para_a_forma_da_conclusao_preenche_o_historico(
    gestor, api_client, manager_headers
):
    """O upgrade com dados, e não só o esquema novo (revisão 012–013, TR-014).

    A suíte roda sobre banco já migrado, e por isso demonstra que o esquema funciona — não que a
    migração até ele funciona. Aqui a instalação é levada ao estado **anterior** à revisão, ganha
    avaliação concluída, rascunho, conclusão preservada e Resultado pontuados, e só então avança:
    é a única forma de provar os três preenchimentos e a recriação das triggers.

    O rascunho está no cenário de propósito. Ele é o caso que a constraint **não** pode exigir: a
    forma é lida no ato de concluir, e carimbá-la no nascimento faria um rascunho aberto antes de
    uma Retificação concluir sob a forma que já não vige.
    """
    # Os testes acima desmontam e remontam o esquema por app, e o que eles remontam é `APPS` — este
    # precisa do banco **inteiro**, porque semeia pelo caminho normal, com inscrição e comissão.
    inicial = MigrationExecutor(connection)
    inicial.loader.build_graph()
    inicial.migrate(inicial.loader.graph.leaf_nodes())

    dados = _semear_historico_pontuado(gestor, api_client, manager_headers)

    # O histórico volta a ser o que era antes da revisão: as colunas somem, as linhas ficam. É o
    # estado de uma instalação em produção no instante em que a migration nova chega.
    executor = MigrationExecutor(connection)
    executor.migrate([("resultados", "0001_initial"), ("avaliacoes", "0001_initial")])
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = 'avaliacoes_avaliacao' AND column_name = 'forma'"
        )
        assert cursor.fetchone() is None, "o cenário precisa começar sem a coluna"

    executor.loader.build_graph()
    alvos = [node for node in executor.loader.graph.leaf_nodes() if node[0] in APPS]
    executor.migrate(alvos)

    with connection.cursor() as cursor:
        cursor.execute("SELECT forma FROM avaliacoes_avaliacao WHERE id = %s", [dados["concluida"]])
        assert cursor.fetchone()[0] == "PONTUADA"
        cursor.execute("SELECT forma FROM avaliacoes_avaliacao WHERE id = %s", [dados["rascunho"]])
        assert cursor.fetchone()[0] == "", "rascunho não recebe forma: ela é lida ao concluir"
        cursor.execute(
            "SELECT forma FROM avaliacoes_conclusaoavaliacao WHERE id = %s", [dados["conclusao"]]
        )
        assert cursor.fetchone()[0] == "PONTUADA"
        cursor.execute(
            "SELECT forma FROM resultados_resultadoetapa WHERE id = %s", [dados["resultado"]]
        )
        assert cursor.fetchone()[0] == "PONTUADA"

    esperadas = set(TRIGGERS_POR_APP["avaliacoes"]) | set(TRIGGERS_POR_APP["resultados"])
    assert esperadas <= _installed_triggers(), "o salto não recriou as triggers que derrubou"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_a_reversao_recusa_quando_ja_existe_conclusao_decisoria(
    gestor, api_client, manager_headers
):
    """Reverter é possível **enquanto ninguém tiver concluído por decisão** — e a recusa diz isso.

    Desfazer o passo é afirmar de novo que concluída significa "tem nota", e uma conclusão decisória
    não tem nota para oferecer. Sem a guarda, o `migrate` para trás falharia adiante com um erro de
    coluna nula que não explica o que aconteceu; com ela, a recusa nomeia o ato administrativo que
    precisa vir antes.

    O teste anterior verificava apenas que existe caminho de volta declarado. Este verifica o que
    esse caminho faz quando há dado — que é quando ele importa.
    """
    from django.db.migrations.exceptions import IrreversibleError

    from tests.fixtures.comissao import inscrever
    from tests.fixtures.mesa import concluir_como, distribuir_para
    from tests.fixtures.resultado import montar_etapa_de_leitura_unica

    inicial = MigrationExecutor(connection)
    inicial.loader.build_graph()
    inicial.migrate(inicial.loader.graph.leaf_nodes())

    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1950, codigo="1950", decisoria=True
    )
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1950")
    concluir_como(cenario, "joao", inscricao, sentido="DESFAVORAVEL", parecer="Sem diploma.")

    executor = MigrationExecutor(connection)
    with pytest.raises(IrreversibleError, match="Desfazê-las é ato administrativo"):
        executor.migrate([("avaliacoes", "0001_initial")])


def _semear_historico_pontuado(gestor, api_client, manager_headers):
    """Uma avaliação concluída, um rascunho, uma conclusão preservada e um Resultado — pontuados.

    Construído pelo caminho normal, e não por `INSERT` cru: o que interessa é o histórico que uma
    instalação real teria, com as chaves estrangeiras que ele de fato carrega.
    """
    from processo_seletivo.avaliacoes.application.avaliacao import gravar
    from processo_seletivo.avaliacoes.models import Avaliacao, ConclusaoAvaliacao
    from processo_seletivo.resultados.application.consolidacao import consolidar
    from processo_seletivo.resultados.models import ResultadoEtapa
    from tests.conftest import ator_institucional
    from tests.fixtures.comissao import inscrever
    from tests.fixtures.mesa import concluir_como, distribuir_para
    from tests.fixtures.resultado import montar_etapa_de_leitura_unica

    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1900, codigo="1900"
    )
    inscricoes = inscrever(cenario["edital"], 2, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1900")
    # A primeira conclui; a segunda fica em **rascunho**, e é ela que prova a regra do
    # preenchimento — a forma é lida no ato de concluir, e o rascunho não a recebe.
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")
    gravar(
        ator=ator_institucional("joao"),
        edital=cenario["edital"],
        etapa_id=cenario["primeira"],
        inscricao_id=inscricoes[1].id,
        pontuacao="60",
        parecer="Em análise.",
        expected_revision=1,
        correlation_id="teste",
    )
    consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[inscricoes[0].id],
        idempotency_key="k-1900",
        correlation_id="teste",
    )

    concluida = Avaliacao.objects.filter(estado=Avaliacao.Estado.CONCLUIDA).first()
    rascunho = Avaliacao.objects.filter(estado=Avaliacao.Estado.RASCUNHO).first()
    assert concluida and rascunho, "o cenário precisa das duas, e é o rascunho que prova a regra"
    conclusao = ConclusaoAvaliacao.objects.filter(avaliacao=concluida).first()
    resultado = ResultadoEtapa.objects.filter(avaliacao=concluida).first()
    assert conclusao and resultado, "o cenário precisa da conclusão preservada e do Resultado"
    return {
        "concluida": concluida.pk,
        "rascunho": rascunho.pk,
        "conclusao": conclusao.pk,
        "resultado": resultado.pk,
    }


DOMINIO_OU_APLICACAO = ("domain", "application")


def _modulos_de_migration():
    from importlib import import_module
    from pathlib import Path

    for app in APPS:
        pacote = import_module(f"processo_seletivo.{app}.migrations")
        pasta = Path(pacote.__file__).parent
        for arquivo in sorted(pasta.glob("[0-9]*.py")):
            yield (
                f"processo_seletivo/{app}/migrations/{arquivo.name}",
                arquivo.read_text(encoding="utf-8"),
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
