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
APPS = (
    "processos",
    "editais",
    "publicacoes",
    "auditoria",
    "avaliacoes",
    "resultados",
    "classificacao",
    # A divulgação da 017: três tabelas append-only e a coerência da publicação contra o ato.
    "divulgacao",
    # A contestação da 018: três tabelas append-only e **duas** de coerência — uma por tabela que
    # precisa dela, porque o gatilho é por tabela e uma trigger não valida linha de outra.
    "recursos",
)
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
    # conferência que impede o Resultado de afirmar o que a Avaliação fonte não afirmou — e, desde
    # D-1, também que o Resultado por Ocorrência afirme fonte nenhuma e cite norma de outro Edital.
    # O nome não mudou com o terceiro ramo: a função foi recriada, e a trigger é a mesma.
    "avaliacoes": ("conclusao_avaliacao_append_only",),
    "resultados": ("resultado_etapa_append_only", "resultado_etapa_coerente"),
    "classificacao": (
        "ato_de_ordenacao_append_only",
        # A proveniência do ato, conferida uma vez por ato e não uma vez por posição (T125).
        "ato_de_ordenacao_coerente",
        "posicao_coerente",
        # A citação da decisão (018): imutável como toda proveniência, e coerente porque uma
        # gravação direta que ligasse decisão de um marco a ato de outro liberaria indevidamente a
        # publicação definitiva daquele outro (T-015, FR-112).
        "citacao_append_only",
        "citacao_coerente",
    ),
    # A divulgação da 017: as três de imutabilidade são **absolutas** — publicar não tem ato em
    # curso que legitime mutação, e toda sucessão é linha nova. A quarta é de coerência, no molde
    # de `resultado_etapa_coerente`: ela confere os eixos declarados contra o ato citado e contra
    # a linha predecessora, e é o que impede a publicação de nascer errada (FR-038, FR-040).
    "divulgacao": (
        "publicacao_resultado_append_only",
        "situacao_divulgada_append_only",
        "documento_do_resultado_append_only",
        "publicacao_resultado_coerente",
    ),
    # A contestação da 018. As três de imutabilidade são **absolutas** — interpor, admitir e julgar
    # acontecem uma vez cada, e não há ato em curso que legitime mutação. As duas de coerência são
    # **duas** porque o gatilho é por tabela: `recurso_coerente` roda no `INSERT` do `Recurso`, e
    # nenhuma linha de `DecisaoRecurso` passa por ela.
    "recursos": (
        "recurso_append_only",
        "recurso_coerente",
        "juizo_de_admissibilidade_append_only",
        "decisao_recurso_append_only",
        "decisao_recurso_coerente",
    ),
}
TRIGGERS = tuple(nome for grupo in TRIGGERS_POR_APP.values() for nome in grupo)

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="migrations validadas em PostgreSQL"
)


@pytest.fixture(autouse=True)
def _esquema_restaurado(request):
    """Cada teste deste arquivo devolve o banco ao grafo completo antes de sair.

    **Por que isto precisa existir.** Os testes daqui desaplicam migrations de propósito — é o que
    eles verificam. Mas desaplicar `publicacoes` desaplica junto **tudo o que depende dela**, e
    reaplicar só `publicacoes` deixa os dependentes de fora: `classificacao`, `resultados` e, desde
    a 017, `divulgacao` ficam sem tabela para o resto da sessão. Como a ordem dos testes é
    sorteada, o efeito aparecia como erro `relation ... does not exist` em arquivos que não têm
    relação nenhuma com migrations — e num arquivo diferente a cada execução.

    O teste que desaplica continua desaplicando; o que muda é que ele não deixa a conta para o
    próximo.
    """
    yield
    # Os testes que só leem arquivo não pedem banco, e tocar a conexão neles seria o erro de
    # acesso a banco que o pytest-django existe para impedir.
    if connection.vendor != "postgresql" or "django_db_setup" not in request.fixturenames:
        return
    executor = MigrationExecutor(connection)
    executor.loader.build_graph()
    executor.migrate(executor.loader.graph.leaf_nodes())


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


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_o_salto_para_a_origem_declarada_preenche_o_historico(gestor, api_client, manager_headers):
    """O upgrade de D-1 com dados: `origem` e `versao` nas linhas que já existiam.

    `origem` nasce com `DEFAULT 'AVALIACAO'`, que é DDL e não toca linha nenhuma. `versao` não tem
    valor constante a oferecer — cada Resultado herda a da sua Avaliação —, e por isso o
    preenchimento é um `UPDATE` linha a linha **numa tabela append-only**. É o único passo destas
    migrations que precisa desligar a própria proteção pelo tempo em que corre, e é por isso que
    ele merece prova com dado real em vez de só esquema.
    """
    inicial = MigrationExecutor(connection)
    inicial.loader.build_graph()
    inicial.migrate(inicial.loader.graph.leaf_nodes())

    dados = _semear_historico_pontuado(gestor, api_client, manager_headers)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT versao_id FROM resultados_resultadoetapa WHERE id = %s", [dados["resultado"]]
        )
        versao_esperada = cursor.fetchone()[0]

    # A instalação volta ao estado anterior a D-1: as colunas somem, as linhas ficam.
    executor = MigrationExecutor(connection)
    executor.migrate([("resultados", "0003_sentido_restrito_aos_dois_valores")])
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = 'resultados_resultadoetapa' AND column_name = 'origem'"
        )
        assert cursor.fetchone() is None, "o cenário precisa começar sem a coluna"

    executor.loader.build_graph()
    alvos = [node for node in executor.loader.graph.leaf_nodes() if node[0] in APPS]
    executor.migrate(alvos)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT origem, versao_id, avaliacao_id FROM resultados_resultadoetapa WHERE id = %s",
            [dados["resultado"]],
        )
        origem, versao, avaliacao = cursor.fetchone()
    assert origem == "AVALIACAO", "o histórico inteiro nasceu de Avaliação"
    assert versao == versao_esperada, "a versão preenchida é a que a junção devolvia"
    assert avaliacao is not None

    esperadas = set(TRIGGERS_POR_APP["resultados"])
    assert esperadas <= _installed_triggers(), "o salto não recriou as triggers que derrubou"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_a_reversao_de_d1_recusa_quando_ja_existe_ocorrencia(gestor, api_client, manager_headers):
    """Reverter é possível **enquanto ninguém tiver registrado ocorrência** — e a recusa diz isso.

    Desfazer o passo é afirmar de novo que todo Resultado tem Avaliação, e o Resultado por
    Ocorrência não tem nenhuma a oferecer. Sem a guarda, o `migrate` para trás falharia adiante com
    um erro de coluna nula que não explica o que aconteceu.
    """
    from django.db.migrations.exceptions import IrreversibleError

    from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
    from tests.conftest import ator_institucional
    from tests.fixtures.comissao import inscrever
    from tests.fixtures.resultado import montar_etapa_de_leitura_unica

    inicial = MigrationExecutor(connection)
    inicial.loader.build_graph()
    inicial.migrate(inicial.loader.graph.leaf_nodes())

    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1960, codigo="1960"
    )
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    registrar_ocorrencia(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[inscricao.id],
        motivo="não compareceu à Entrevista (item 6.3 do Edital)",
        idempotency_key="k-1960",
        correlation_id="teste",
    )

    executor = MigrationExecutor(connection)
    with pytest.raises(IrreversibleError, match="Desfazê-los é ato administrativo"):
        executor.migrate([("resultados", "0003_sentido_restrito_aos_dois_valores")])


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


# Os apps que a 017 **lê** e não toca. `divulgacao` depende dos quatro, e a direção da dependência
# é única: nenhum deles passa a conhecê-la (017, T-001).
APPS_QUE_A_017_NAO_TOCA = ("classificacao", "resultados", "editais", "publicacoes")


def test_a_017_nao_acrescenta_migration_aos_apps_que_ela_apenas_le():
    """FR-070: a divulgação lê os agregados existentes e não altera nenhum deles.

    A tentação concreta que isto bloqueia tem nome: acrescentar uma coluna de "publicado" ao
    `AtoDeOrdenacao`, ou um campo de vigência ao lado dele. Qualquer uma das duas faria a 015
    passar a conhecer a 017 — e a sucessão do ato e a da divulgação, que são cadeias diferentes
    sobre objetos diferentes, começariam a se confundir numa coluna só.

    A guarda é por **contagem**: a 017 nasce depois destas migrations, e qualquer uma nova nesses
    quatro apps que ela precisasse teria de vir com justificativa própria — que é exatamente a
    conversa que este teste força.
    """
    import pathlib as _pathlib

    raiz = _pathlib.Path(__file__).resolve().parents[2] / "processo_seletivo"
    esperadas = {
        # **Sobe para 4 com a 018**, e a justificativa é própria: a `classificacao/0004` cria a
        # `CitacaoDeDecisao` — a proveniência que liga o ato de ordenação à decisão de recurso que
        # ele executa. Sem ela, o cumprimento da providência a jusante só poderia ser presumido
        # ("publicou-se ato novo"), e um ato emitido por razão alheia encerraria a pendência sem
        # que ninguém tivesse corrigido o vício reconhecido (018, T-015, FR-112).
        "classificacao": 4,
        # **Sobe para 5 com a 018**, e a justificativa é a que este teste existe para exigir: a
        # `resultados/0005` dá sucessão ao `ResultadoEtapa` — o único elo da cadeia que não a
        # tinha —, para que um recurso deferido possa superar um Resultado sem alterá-lo. Não é
        # a 017 acrescentando migration a um app que ela lê: é outra feature, com decisão própria
        # (018, decisão C §1.1).
        "resultados": 5,
        # **Sobe para 11 com a 018**: a `editais/0011` acrescenta `janela_recursal` ao marco
        # classificatório — o degrau 8. É elaboração, e não divulgação: quem declara o prazo é o
        # Edital, e é por isso que o campo mora aqui e não na 017 (FR-020, FR-030).
        # **Sobe para 13 com a 020**: a `editais/0012` cria o Anexo e o seu artefato e liga o
        # Documento Exigido ao modelo; a `0013` põe no banco a imutabilidade do artefato já
        # publicado. São duas porque protegem coisas diferentes — criar tabela e trancar o que ela
        # guarda —, e a segunda é condicional ao estado, como a `publicacoes/0007` (020, FR-010).
        "editais": 13,
        "publicacoes": 8,
        # **Sobe para 2 com a 018**: a `divulgacao/0002` acrescenta os três campos da declaração
        # expressa de encerramento do prazo e a constraint que os mantém inteiros (FR-085).
        "divulgacao": 2,
    }
    for app, quantas in esperadas.items():
        migrations = sorted((raiz / app / "migrations").glob("[0-9]*.py"))
        assert len(migrations) == quantas, (
            f"{app} tem {len(migrations)} migrations, e a 017 não acrescenta nenhuma a ele "
            f"(FR-070). Se a mudança é legítima, ela é de outra feature — e este número sobe "
            f"junto com a justificativa."
        )


# As migrations que a **017** escreveu. A guarda de alteração vale para elas, e não para o app
# inteiro: a 018 acrescenta a `0002`, e ela **altera de propósito** a tabela da própria divulgação —
# os três campos da declaração expressa. Manter a proibição sobre o app inteiro faria a guarda dizer
# "a 017 não altera esquema" e verificar "ninguém altera esta tabela nunca", que é outra coisa e
# congelaria a divulgação para sempre.
MIGRATIONS_DA_017 = ("0001_initial.py",)


def test_a_017_nao_toca_o_esquema_de_outros_apps():
    """O espelho da guarda da 011: a migration da divulgação não nomeia app alheio.

    Ela **depende** de `classificacao`, `inscricoes` e `processos` — é preciso, para as chaves
    estrangeiras —, e o que ela não pode é alterar tabela deles.

    A proibição de nomear app alheio vale para **todas** as migrations da divulgação, inclusive as
    que outras features acrescentarem: nenhuma delas tem por que alterar tabela de terceiro por
    aqui. A proibição de alterar campo vale só para as da 017 — ver `MIGRATIONS_DA_017`.
    """
    import pathlib as _pathlib

    raiz = _pathlib.Path(__file__).resolve().parents[2] / "processo_seletivo"
    migrations = sorted((raiz / "divulgacao" / "migrations").glob("[0-9]*.py"))
    assert migrations, "a 017 precisa ter ao menos uma migration"

    alteracoes = ("AlterField", "AddField", "RemoveField", "RenameField", "DeleteModel")
    for arquivo in migrations:
        corpo = arquivo.read_text()
        if arquivo.name in MIGRATIONS_DA_017:
            for operacao in alteracoes:
                assert operacao not in corpo, (
                    f"{arquivo.name} usa {operacao}: a 017 cria as tabelas dela e não altera as "
                    "existentes (FR-070)"
                )
        for app_alheio in APPS_QUE_A_017_NAO_TOCA:
            assert f'model_name="{app_alheio}' not in corpo


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


# Os apps que a **022** lê, e nada além de ler. São todos os que compõem o Pulso e os cinco
# sinais: a supervisão observa a fronteira entre eles, e por isso conhece muitos — mas não é dona
# de fato nenhum (022, T-001).
APPS_QUE_A_022_NAO_TOCA = (
    "avaliacoes",
    "classificacao",
    "comissoes",
    "divulgacao",
    "editais",
    "inscricoes",
    "processos",
    "publicacoes",
    "recursos",
    "resultados",
)


def test_a_022_nao_acrescenta_migration_aos_apps_que_ela_apenas_le():
    """FR-007 e SC-014: a supervisão não introduz estrutura de dados persistente nenhuma.

    A tentação concreta que isto bloqueia tem nome, e ela é a mais sedutora da feature: gravar o
    sinal. Uma tabela de "condições de atenção" tornaria a região barata de renderizar e cara de
    manter — passaria a existir estado a sincronizar com sete agregados, e a primeira divergência
    entre o gravado e o real seria invisível, porque a página leria o gravado.

    `D-007` faz da necessidade de persistir estado um motivo para **revisar a spec**, e não para
    escrever migration. A guarda é por contagem, no formato que a 017 e a 011 já usam: qualquer
    migration nova nesses apps vem de outra feature, com justificativa própria — que é exatamente
    a conversa que este teste força.
    """
    import pathlib as _pathlib

    raiz = _pathlib.Path(__file__).resolve().parents[2] / "processo_seletivo"
    esperadas = {
        "avaliacoes": 3,
        "classificacao": 4,
        "comissoes": 1,
        "divulgacao": 2,
        "editais": 13,
        "inscricoes": 4,
        "processos": 2,
        "publicacoes": 8,
        "recursos": 1,
        "resultados": 5,
    }
    assert set(esperadas) == set(APPS_QUE_A_022_NAO_TOCA)
    for app, quantas in esperadas.items():
        migrations = sorted((raiz / app / "migrations").glob("[0-9]*.py"))
        assert len(migrations) == quantas, (
            f"{app} tem {len(migrations)} migrations, e a 022 não acrescenta nenhuma a ele "
            f"(FR-007). Se a mudança é legítima, ela é de outra feature — e este número sobe "
            f"junto com a justificativa."
        )


def test_a_022_nao_cria_app_com_migrations_proprias():
    """T-001: app sem modelo criaria a expectativa de que um dia terá.

    A `011` abriu app novo porque trouxe agregado; a `022` não traz nenhum. Este teste é a metade
    que a contagem acima não cobre: ela vigia os apps que existem, e este vigia o que não existe.
    """
    import pathlib as _pathlib

    raiz = _pathlib.Path(__file__).resolve().parents[2] / "processo_seletivo"

    assert not (raiz / "supervisao").exists(), (
        "a supervisão é módulo de leitura em `interface/`, e não app: ela não é dona de fato "
        "persistido algum (FR-007, T-001)."
    )
