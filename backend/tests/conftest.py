import pytest
from django.db import connections
from rest_framework.test import APIClient


def encerrar_conexoes_da_thread():
    """Fecha as conexões desta thread, inclusive a subjacente do SQLite em memória.

    `connections.close_all()` não basta: para banco em memória o backend do SQLite trata
    `close()` como no-op, porque fechar destruiria o banco. Como o Django monta o banco de teste
    com `cache=shared` quando há threads, ele sobrevive enquanto qualquer conexão continuar
    aberta — e a da thread principal continua. Sem isto cada thread deixa uma `sqlite3.Connection`
    para o coletor de lixo, e o ResourceWarning aparece atribuído ao teste seguinte, que não tem
    relação nenhuma com ele.
    """
    for conexao in connections.all(initialized_only=True):
        subjacente = conexao.connection
        em_memoria = getattr(conexao, "is_in_memory_db", lambda: False)()
        conexao.close()
        if em_memoria and subjacente is not None:
            subjacente.close()
            conexao.connection = None


_FIXTURES_DE_BANCO = frozenset(
    {"db", "transactional_db", "django_db_reset_sequences", "django_db_serialized_rollback"}
)


@pytest.fixture(autouse=True)
def unidade_e_autoridades_da_suite(request):
    """O Cefor e as autoridades de teste, em todo caso que toca o banco (060, R-012).

    Ativa só com banco — marcador `django_db` ou uma das fixtures dele, inclusive indireta —, para
    que os testes puros não paguem conexão. O helper do pytest-django é pedido antes de gravar: é
    ele que decide se o caso é transacional, e gravar antes dele seria gravar fora do caso. Os
    valores e a razão de não serem data migration estão em `tests/fixtures/autoridades.py`.
    """
    usa_banco = request.node.get_closest_marker("django_db") or (
        _FIXTURES_DE_BANCO & set(request.fixturenames)
    )
    # A semente da 110 só se aplica a registro vazio, e o caso que a prova não pode receber o Cefor
    # daqui. Num caso transacional o registro começa vazio: a limpeza do caso anterior o truncou.
    if not usa_banco or request.node.get_closest_marker("sem_unidade_da_suite"):
        return
    request.getfixturevalue("_django_db_helper")
    from tests.fixtures.autoridades import garantir_o_cefor

    garantir_o_cefor()


@pytest.fixture(autouse=True)
def sem_trava_em_append_only(request):
    """Nenhum caso que toca o banco trava linha append-only (A-01 da auditoria de 31/10/2026).

    A suíte roda como superusuário, que trava o que quiser; produção recusa. O vigia lê o SQL que o
    caso de fato executa e o recusa antes do banco — as razões e o que ele não vê estão em
    `tests/guardiao_de_travas.py`. Vale para a conexão do caso e para as que outras *threads*
    abrirem durante ele; a do `live_server`, aberta antes, fica de fora. `trava_deliberada`
    dispensa o caso que trava de propósito.
    """
    usa_banco = request.node.get_closest_marker("django_db") or (
        _FIXTURES_DE_BANCO & set(request.fixturenames)
    )
    if not usa_banco or request.node.get_closest_marker("trava_deliberada"):
        yield
        return
    from django.db import connection

    from tests.guardiao_de_travas import vigiando

    with vigiando(connection) as acusadas:
        yield
    if acusadas:
        pytest.fail(
            f"trava em tabela append-only, ainda que a exceção tenha sido engolida: {acusadas}"
        )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def manager_headers():
    return {
        "HTTP_AUTHORIZATION": "Bearer gestor-a|cefor|processo:criar,processo:ativar,edital:criar",
        "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0001",
        "HTTP_X_CORRELATION_ID": "test-correlation-id",
    }


@pytest.fixture
def process_payload():
    return {
        "institutionalCode": "PS-2026-001",
        "title": "Processo Seletivo 2026",
        "firstEdital": {"number": "01", "year": 2026, "title": "Primeiro Edital"},
    }


# ---------------------------------------------------------------------------
# A jornada do candidato (009). Ficam aqui, e não num conftest de diretório, porque integração e
# autorização exercitam as mesmas precondições — e fixture só é vista do conftest da raiz ou do
# próprio diretório.
# ---------------------------------------------------------------------------


@pytest.fixture
def raiz_de_arquivos(settings, tmp_path):
    """Cada teste com a sua raiz de arquivos.

    O armazenamento resolve a configuração a cada operação justamente para isto: sem resolver por
    propriedade, `override_settings` não teria efeito e os testes escreveriam todos no mesmo lugar.
    """
    settings.ARQUIVOS_CANDIDATOS_RAIZ = str(tmp_path)
    return tmp_path


@pytest.fixture
def selecao(raiz_de_arquivos, api_client, manager_headers, process_payload):
    """Seleção publicada, período aberto, três documentos exigidos com alcances distintos."""
    from datetime import timedelta

    from django.utils import timezone

    from tests.fixtures.selecao import publicar_selecao, rascunho_aberto_com_documentos

    return publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
    )


@pytest.fixture
def candidatos_registrados():
    """Maria e João existem como identidades persistidas, e não como declarações (010).

    Não é *autouse*, e a razão é dupla. A abertura de rascunho passou a exigir que a linha da
    identidade exista — sem isso uma inscrição poderia nascer órfã de uma identidade descartada —,
    então os testes da jornada precisam delas. Mas registrá-las em **todo** teste de banco poluiria
    os que contam identidades, e contagem poluída é teste que passa a medir a *fixture*.
    """
    from tests.fixtures.candidato import JOAO, MARIA, registrar

    return [registrar(identidade) for identidade in (MARIA, JOAO)]


@pytest.fixture
def inscricao_de_maria(selecao, candidatos_registrados):
    from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
    from tests.fixtures.candidato import MARIA, PERFIL_DOCENTE

    return abrir_inscricao(identidade=MARIA, edital_id=selecao.id, profile_id=PERFIL_DOCENTE)


@pytest.fixture
def desafio_consumido():
    """Um desafio já validado, portando a decisão pendente da reconciliação (010).

    Fica aqui, e não num conftest de diretório, pelo mesmo motivo das *fixtures* da `009`:
    integração e autorização exercitam as mesmas precondições.
    """
    from processo_seletivo.identidade.application import desafio as servico
    from processo_seletivo.identidade.models import DesafioDeAcesso

    endereco = "maria@exemplo.test"
    _, codigo = servico.solicitar(
        email_canonico=endereco, finalidade=DesafioDeAcesso.Finalidade.ENTRAR
    )
    return servico.validar(
        email_canonico=endereco, finalidade=DesafioDeAcesso.Finalidade.ENTRAR, codigo=codigo
    )


# ---------------------------------------------------------------------------
# A organização do trabalho (011). Ficam aqui pela mesma razão das fixtures da 009: integração,
# autorização, interface e aceitação exercitam as mesmas precondições, e fixture só é vista do
# conftest da raiz ou do próprio diretório.
# ---------------------------------------------------------------------------


def ator_institucional(subject, *permissoes, escopo="cefor"):
    from processo_seletivo.seguranca.domain import Actor

    return Actor(subject, escopo, frozenset(permissoes))


@pytest.fixture
def gestor():
    return ator_institucional("carlos", "comissao:gerir")


@pytest.fixture
def auditor():
    return ator_institucional("auditora", "auditoria:consultar")


@pytest.fixture
def sem_nada():
    return ator_institucional("estranho")


@pytest.fixture
def edital_a(db, api_client, manager_headers, process_payload):
    """Processo A publicado, com duas Etapas — A1 e A2."""
    from tests.fixtures.comissao import publicar_processo_com_etapas

    return publicar_processo_com_etapas(api_client, manager_headers, process_payload)


@pytest.fixture
def edital_com_documentos(db, raiz_de_arquivos, api_client, manager_headers):
    """Um Processo próprio, com Documentos Exigidos — a `012` abre a inscrição por requisito.

    **Processo, código e chave próprios, e não os do Processo A.** Esta fixture se dizia "o mesmo
    Processo A" e criava o Processo com o payload e a chave de idempotência de `edital_a`. Num
    teste que usava as duas — e bastava `processo_a` —, a segunda criação **reencenava** a
    primeira, devolvia o Edital já publicado, e o `PUT` do rascunho dela voltava 409 em silêncio.
    Havia um Edital só, e **qual** dos dois rascunhos ele carregava dependia da ordem dos
    argumentos do teste: com `processo_a` pedido antes, saía sem requisito nenhum (045, `R-9`).

    A semente continua `0`, para que `etapa_a1` e `DOCUMENTO_A` sirvam aos dois — e é por isso que
    esta fixture **não convive** com `edital_a` no mesmo teste: Perfil e Evento têm identificador
    global, e o rascunho da segunda é recusado ("Identificadores já vinculados a outro
    contêiner"). A recusa é alta, que é o que se quer; quem precisa da Comissão sobre este Edital
    usa `comissao_com_documentos`.
    """
    from tests.fixtures.comissao import publicar_processo_com_etapas

    return publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0012"},
        {
            "institutionalCode": "PS-2026-012",
            "title": "Processo com Documentos Exigidos",
            "firstEdital": {"number": "12", "year": 2026, "title": "Edital com Documentos"},
        },
        com_documentos=True,
    )


@pytest.fixture
def processo_com_documentos(edital_com_documentos):
    return edital_com_documentos.processo


@pytest.fixture
def processo_a(edital_a):
    return edital_a.processo


@pytest.fixture
def edital_b(db, api_client, manager_headers):
    """Processo B, para que "Etapa de outro Processo" seja demonstrável."""
    from tests.fixtures.comissao import publicar_processo_com_etapas

    return publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0002"},
        {
            "institutionalCode": "PS-2026-002",
            "title": "Outro Processo",
            "firstEdital": {"number": "02", "year": 2026, "title": "Segundo Edital"},
        },
        seed=1,
    )


@pytest.fixture
def etapa_a1():
    from tests.fixtures.comissao import ETAPA_A1
    from tests.fixtures.edital import identificador

    return identificador(ETAPA_A1, 0)


@pytest.fixture
def etapa_a2():
    from tests.fixtures.comissao import ETAPA_A2
    from tests.fixtures.edital import identificador

    return identificador(ETAPA_A2, 0)


@pytest.fixture
def etapa_b1():
    from tests.fixtures.comissao import ETAPA_A1
    from tests.fixtures.edital import identificador

    return identificador(ETAPA_A1, 1)


@pytest.fixture
def comissao_de_a(gestor, processo_a):
    """Maria presidente, João membro — a composição dos cenários da spec."""
    from tests.fixtures.comissao import constituir

    return constituir(gestor, processo_a, [("maria", "PRESIDENTE"), ("joao", "MEMBRO")])


@pytest.fixture
def comissao_com_documentos(gestor, processo_com_documentos):
    """A mesma composição de `comissao_de_a`, sobre o Processo de `edital_com_documentos`."""
    from tests.fixtures.comissao import constituir

    return constituir(
        gestor, processo_com_documentos, [("maria", "PRESIDENTE"), ("joao", "MEMBRO")]
    )


@pytest.fixture
def seletor_ligado(settings):
    """O seletor de identidade institucional, que só existe fora de produção.

    Estava no conftest da interface; subiu para cá quando os testes de autorização da 011
    passaram a exercitar as mesmas telas — a autorização por objeto só é demonstrável pelo canal
    do ator, e o canal exige identidade.
    """
    settings.INTERFACE_SELETOR_IDENTIDADE = True


# ---------------------------------------------------------------------------
# A supervisão do Processo (022). Ficam aqui pela mesma razão das anteriores: integração,
# interface e aceitação exercitam as mesmas precondições, e fixture só é vista do conftest da raiz
# ou do próprio diretório.
# ---------------------------------------------------------------------------


@pytest.fixture
def edital_c(db, api_client, manager_headers, processo_a):
    """Um segundo Edital **no mesmo Processo**, com período de inscrições em curso.

    É o que torna a soma demonstrável: sem dois Editais sob o mesmo Processo, "o total é a soma dos
    Editais" não tem contraprova.
    """
    from tests.fixtures.supervisao import (
        SEGUNDO_SEED,
        etapa_ligada,
        publicar_no_processo,
        rascunho_com_periodo,
    )

    return publicar_no_processo(
        api_client,
        manager_headers,
        processo_a,
        draft=rascunho_com_periodo(
            SEGUNDO_SEED,
            etapas=[etapa_ligada(SEGUNDO_SEED)],
        ),
    )


# ---------------------------------------------------------------------------
# A limpeza depois de cada caso transacional, medida em
# `doc/estudo-limpeza-dos-casos-transacionais.md`: o teardown desses casos era a maior parcela da
# suíte, e quase todo ele era trabalho que não muda o banco que o caso seguinte recebe.
# ---------------------------------------------------------------------------

# As duas tabelas que o `post_migrate` repovoa. Ninguém no sistema lê tipo de conteúdo nem
# permissão do Django — a autorização é a do domínio —, mas elas ficam povoadas como em produção, e
# não vazias, para que o teste que um dia precisar delas não quebre em silêncio.
_TABELAS_DE_REFERENCIA = frozenset({"django_content_type", "auth_permission"})

# Por banco de teste: as tabelas, quem referencia cada uma, a consulta de sujas e a impressão das
# tabelas de referência. Tudo sai da primeira limpeza, que é a do Django inteira.
_limpeza_por_banco = {}


def _impressao_das_tabelas_de_referencia(cursor):
    cursor.execute(
        "SELECT"
        " (SELECT md5(coalesce(string_agg(t::text, ',' ORDER BY id), ''))"
        " FROM django_content_type t),"
        " (SELECT md5(coalesce(string_agg(t::text, ',' ORDER BY id), '')) FROM auth_permission t)"
    )
    return cursor.fetchone()


def _quem_referencia(cursor, tabelas):
    cursor.execute(
        "SELECT referenciada.relname, referenciadora.relname FROM pg_constraint c"
        " JOIN pg_class referenciada ON referenciada.oid = c.confrelid"
        " JOIN pg_class referenciadora ON referenciadora.oid = c.conrelid"
        " WHERE c.contype = 'f' AND c.confrelid <> c.conrelid"
    )
    mapa = {tabela: set() for tabela in tabelas}
    for referenciada, referenciadora in cursor.fetchall():
        if referenciada in mapa and referenciadora in mapa:
            mapa[referenciada].add(referenciadora)
    return mapa


def _fecho(sujas, quem_referencia):
    fecho, fila = set(sujas), list(sujas)
    while fila:
        for referenciadora in quem_referencia[fila.pop()]:
            if referenciadora not in fecho:
                fecho.add(referenciadora)
                fila.append(referenciadora)
    return fecho


def _preparar_limpeza(conexao):
    from django.db import DatabaseError

    tabelas = conexao.introspection.django_table_names(only_existing=True, include_views=False)
    try:
        with conexao.cursor() as cursor:
            return {
                "tabelas": tabelas,
                "quem_referencia": _quem_referencia(cursor, tabelas),
                "impressao": _impressao_das_tabelas_de_referencia(cursor),
                # Uma ida ao banco, e não uma por tabela.
                "sujas": " UNION ALL ".join(
                    f"SELECT '{tabela}' WHERE EXISTS (SELECT 1 FROM {nome})"
                    for tabela, nome in ((t, conexao.ops.quote_name(t)) for t in tabelas)
                ),
            }
    except DatabaseError:
        # Um caso de `tests/migrations/` que falhou no meio pode deixar o banco sem as tabelas de
        # referência. Sem preparo, a próxima limpeza é a do Django de novo.
        return None


def _limpar_como_o_django(db_name):
    from django.core.management import call_command

    call_command(
        "flush",
        verbosity=0,
        interactive=False,
        database=db_name,
        reset_sequences=False,
        allow_cascade=False,
        inhibit_post_migrate=False,
    )


def _limpar_so_o_que_mudou(conexao, preparo, db_name):
    """Devolve `False` quando o banco não está como o preparo o viu, e a limpeza não foi feita."""
    from django.core.management.color import no_style
    from django.core.management.sql import emit_post_migrate_signal
    from django.db import DatabaseError

    try:
        with conexao.cursor() as cursor:
            cursor.execute(preparo["sujas"])
            sujas = {linha[0] for linha in cursor.fetchall()}
            intactas = _impressao_das_tabelas_de_referencia(cursor) == preparo["impressao"]
    except DatabaseError:
        # Tabela que sumiu: um caso de `tests/migrations/` deixou o esquema noutro estado.
        return False
    if intactas:
        sujas -= _TABELAS_DE_REFERENCIA
    alvo = _fecho(sujas, preparo["quem_referencia"])
    # Nenhuma tabela suja é referenciada pelas de referência hoje, e o fecho não chega a elas. Se
    # um dia chegar, elas são truncadas, e então precisam do sinal que as repovoa.
    repovoar = not intactas or bool(alvo & _TABELAS_DE_REFERENCIA)
    if alvo:
        conexao.ops.execute_sql_flush(
            conexao.ops.sql_flush(no_style(), sorted(alvo), reset_sequences=False)
        )
    if repovoar:
        emit_post_migrate_signal(0, False, db_name)
        # Repovoadas, as linhas voltam com ids novos. Sem a impressão nova, toda limpeza seguinte
        # deste banco as julgaria alteradas e refaria o sinal — foi o que a primeira versão fez,
        # depois do primeiro caso que mexeu nelas.
        with conexao.cursor() as cursor:
            preparo["impressao"] = _impressao_das_tabelas_de_referencia(cursor)
    return True


def _limpeza_enxuta(self):
    """O `TransactionTestCase._fixture_teardown`, sem o trabalho que não muda o banco.

    **Trunca só as tabelas com linha, e as que as referenciam.** O PostgreSQL só aceita truncar
    uma tabela junto de todas as que têm chave estrangeira para ela, vazias ou não — o fecho é
    dessas, e não um excesso de zelo. As que ficam de fora já estavam vazias, e o `TRUNCATE` do
    Django não reinicia sequência: o banco que o caso seguinte recebe é o mesmo.

    **Não emite o `post_migrate` quando as tabelas de referência continuam como estavam.** Ele só
    recria tipos de conteúdo e permissões, e elas ficam fora do `TRUNCATE`. Se um caso mexer
    nelas, a impressão muda, e a limpeza volta a ser a do Django.

    Fica com a limpeza do Django o que ela trata de outro jeito — `available_apps`,
    `serialized_rollback` — e o que não é PostgreSQL. `LIMPEZA_INTEGRAL=1` a devolve inteira, para
    o caso em que se suspeitar desta.
    """
    import os

    from django.db import connections as conexoes

    if (
        self.available_apps is not None
        or self.serialized_rollback
        or os.environ.get("LIMPEZA_INTEGRAL") == "1"
    ):
        return _limpeza_do_django(self)
    for db_name in self._databases_names(include_mirrors=False):
        conexao = conexoes[db_name]
        if conexao.vendor != "postgresql":
            _limpar_como_o_django(db_name)
            continue
        chave = (db_name, conexao.settings_dict["NAME"])
        preparo = _limpeza_por_banco.get(chave)
        if preparo is None or not _limpar_so_o_que_mudou(conexao, preparo, db_name):
            _limpar_como_o_django(db_name)
            _limpeza_por_banco[chave] = _preparar_limpeza(conexao)


def _instalar_limpeza_enxuta():
    from django.test import TransactionTestCase

    global _limpeza_do_django
    # Uma vez só: envolver a si mesma faria a "limpeza do Django" de reserva ser esta outra vez.
    if getattr(TransactionTestCase._fixture_teardown, "__name__", "") == "_limpeza_enxuta":
        return
    _limpeza_do_django = TransactionTestCase._fixture_teardown
    TransactionTestCase._fixture_teardown = _limpeza_enxuta


_instalar_limpeza_enxuta()
