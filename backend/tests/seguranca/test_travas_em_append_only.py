"""Nenhum código de produção trava linha de tabela append-only (A-01 da auditoria de 31/10/2026).

**Duas metades, e a principal não está aqui.** O vigia do `tests/conftest.py`
(`sem_trava_em_append_only`, com a lógica em `tests/guardiao_de_travas.py`) lê o SQL que cada caso
executa e recusa a trava antes do banco: é exato e alcança tudo o que a suíte roda — inclusive a
junção que um *manager* acrescenta por dentro. Este arquivo cobre o que ele não vê, **o caminho que
nenhum teste executa**, com uma checagem estática deliberadamente pequena:

```text
ORM   Modelo.manager....select_for_update(...)   ← o modelo que abre a cadeia é append-only?
SQL   "... FROM t ... FOR SHARE" no código       ← alguma tabela travada no nível externo é?
```

Ela não segue variável, junção nem `select_related`: reimplementar o Django para isso foi a
primeira versão, e custava ~490 linhas para cobrir menos do que o vigia. E prova as duas metades
contra o A-01 como ele estava.
"""

import ast
import pathlib

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import connection, transaction

from tests.guardiao_de_travas import APPEND_ONLY, TravaEmAppendOnly, tabelas_travadas, vigiando

RAIZ = pathlib.Path(__file__).resolve().parents[2] / "processo_seletivo"

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="o SQL de trava só é gerado pelo PostgreSQL"
)


def _modelo_que_abre(chamada, nomes):
    """`Modelo.manager.a().select_for_update()` → `Modelo`; `None` se a cadeia não começa num."""
    no = chamada.func.value
    while isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute):
        no = no.func.value
    if not isinstance(no, ast.Attribute):
        return None
    if isinstance(no.value, ast.Name):
        return nomes.get(no.value.id)
    if isinstance(no.value, ast.Call) and getattr(no.value.func, "id", "") == "get_user_model":
        return get_user_model()
    return None


def _docstrings(arvore):
    for no in ast.walk(arvore):
        corpo = getattr(no, "body", None)
        if isinstance(corpo, list) and corpo and isinstance(corpo[0], ast.Expr):
            yield corpo[0].value


def travas_estaticas(fonte, arquivo):
    """`(violações, travas examinadas)` de um arquivo-fonte; separado para o autoteste."""
    nomes = {modelo.__name__: modelo for modelo in apps.get_models()}
    arvore = ast.parse(fonte)
    docstrings = set(map(id, _docstrings(arvore)))
    violacoes, examinadas = [], 0
    for no in ast.walk(arvore):
        if (
            isinstance(no, ast.Call)
            and isinstance(no.func, ast.Attribute)
            and no.func.attr == "select_for_update"
        ):
            examinadas += 1
            modelo = _modelo_que_abre(no, nomes)
            if modelo is not None and modelo._meta.db_table in APPEND_ONLY:
                violacoes.append((arquivo, no.lineno, modelo._meta.db_table))
        elif (
            isinstance(no, ast.Constant) and isinstance(no.value, str) and id(no) not in docstrings
        ):
            travadas = tabelas_travadas(no.value)
            examinadas += bool(travadas)
            for tabela in sorted(travadas & APPEND_ONLY):
                violacoes.append((arquivo, no.lineno, tabela))
    return violacoes, examinadas


def test_nenhuma_trava_no_codigo_abre_em_tabela_append_only():
    violacoes, examinadas = [], 0
    for caminho in sorted(RAIZ.rglob("*.py")):
        if "migrations" in caminho.parts:
            continue
        achadas, vistas = travas_estaticas(caminho.read_text(), caminho.relative_to(RAIZ))
        violacoes += achadas
        examinadas += vistas

    # Uma varredura que não encontrasse trava nenhuma passaria por não ter olhado. Eram 47 em
    # 31/10/2026, entre ORM e SQL; o piso só precisa estar longe do zero.
    assert examinadas >= 30, examinadas
    assert not violacoes, (
        "trava de linha em tabela append-only: a role de produção não tem UPDATE nela, e o "
        f"PostgreSQL o exige para FOR UPDATE/FOR SHARE. Trave o agregado acima: {violacoes}"
    )


# ---------------------------------------------------------------------------
# A metade estática diante do A-01
# ---------------------------------------------------------------------------

A_01 = """
def _protegido(peca, etapa_id):
    return (
        ResultadoEtapa.vigentes.select_for_update(of=("self",))
        .filter(inscricao_id=peca.inscricao_id, etapa_id=etapa_id)
        .first()
    )
"""


@pytest.mark.parametrize(
    ("fonte", "tabela"),
    [
        pytest.param(A_01, "resultados_resultadoetapa", id="o A-01 como estava"),
        pytest.param(
            "Vinculo.objects.select_for_update().filter(pk=1).first()",
            "seguranca_vinculo",
            id="a revogação da 106 como estava",
        ),
        pytest.param(
            'cursor.execute("SELECT id FROM recursos_recurso WHERE id = %s FOR SHARE", [x])',
            "recursos_recurso",
            id="SQL escrito à mão",
        ),
    ],
)
def test_a_checagem_estatica_reprova_a_reintroducao(fonte, tabela):
    violacoes, _ = travas_estaticas(fonte, "recursos/application/julgar.py")
    assert tabela in {encontrada for _, _, encontrada in violacoes}


@pytest.mark.parametrize(
    "fonte",
    [
        pytest.param("ProcessoSeletivo.objects.select_for_update().get(pk=1)", id="o Processo"),
        pytest.param(
            '"""Travar o Resultado com FOR UPDATE FROM resultados_resultadoetapa não serve."""',
            id="docstring não é SQL",
        ),
        pytest.param(
            'cursor.execute("SELECT id FROM processos_processoseletivo WHERE id IN '
            '(SELECT processo_id FROM recursos_recurso) FOR UPDATE")',
            id="subconsulta não é travada",
        ),
    ],
)
def test_a_checagem_estatica_aceita_o_que_a_producao_aceita(fonte):
    assert travas_estaticas(fonte, "x.py")[0] == []


# ---------------------------------------------------------------------------
# O vigia diante do SQL que o Django gera
# ---------------------------------------------------------------------------


def _sql(queryset):
    compilado, _ = queryset.query.get_compiler(connection=connection).as_sql()
    return compilado


@pytest.mark.django_db
@postgresql_only
def test_o_vigia_le_as_travas_que_o_django_gera():
    """O que a primeira versão reimplementava, lido do próprio SQL.

    O A-01 trava a tabela de origem mesmo com `of=("self",)`. O `select_related` sem `of=`
    estende a trava ao relacionado, e com `of=("self",)` não. O Processo não alcança nada.
    """
    from processo_seletivo.processos.models import ProcessoSeletivo
    from processo_seletivo.publicacoes.models_retificacao import Retificacao
    from processo_seletivo.resultados.models import ResultadoEtapa

    with transaction.atomic():
        a_01 = ResultadoEtapa.vigentes.select_for_update(of=("self",)).filter(etapa_id=None)
        junta = Retificacao.objects.select_related("base_snapshot").select_for_update()
        restrita = Retificacao.objects.select_related("base_snapshot").select_for_update(
            of=("self",)
        )
        processo = ProcessoSeletivo.objects.select_for_update().filter(pk=None)

        assert tabelas_travadas(_sql(a_01)) & APPEND_ONLY == {"resultados_resultadoetapa"}
        assert "publicacoes_versaoconsolidada" in tabelas_travadas(_sql(junta))
        assert not tabelas_travadas(_sql(restrita)) & APPEND_ONLY
        assert not tabelas_travadas(_sql(processo)) & APPEND_ONLY


@pytest.mark.django_db
@pytest.mark.trava_deliberada
@postgresql_only
def test_o_vigia_recusa_a_trava_antes_do_banco_e_guarda_a_acusacao():
    from processo_seletivo.processos.models import ProcessoSeletivo
    from processo_seletivo.resultados.models import ResultadoEtapa

    with vigiando(connection) as acusadas:
        with pytest.raises(TravaEmAppendOnly, match="resultados_resultadoetapa"):
            with transaction.atomic():
                list(ResultadoEtapa.vigentes.select_for_update(of=("self",)))
        with transaction.atomic():
            list(ProcessoSeletivo.objects.select_for_update())

    # A exceção engolida não apaga o achado: é a lista que o fim do caso cobra no conftest.
    assert [tabelas for tabelas, _ in acusadas] == [["resultados_resultadoetapa"]]


@pytest.mark.django_db(transaction=True)
@pytest.mark.trava_deliberada
@postgresql_only
def test_o_vigia_alcanca_a_conexao_que_outra_thread_abre_durante_o_caso():
    """Os casos de corrida rodam o comando em *threads*, cada uma com a sua conexão."""
    import threading

    from django.db import connection as da_thread

    from processo_seletivo.processos.models import ProcessoSeletivo
    from processo_seletivo.resultados.models import ResultadoEtapa

    desfechos = []

    def travar():
        try:
            with transaction.atomic():
                list(ProcessoSeletivo.objects.select_for_update())
            try:
                with transaction.atomic():
                    list(ResultadoEtapa.vigentes.select_for_update(of=("self",)))
            except TravaEmAppendOnly as recusa:
                desfechos.append(recusa)
        finally:
            da_thread.close()

    with vigiando(connection) as acusadas:
        thread = threading.Thread(target=travar)
        thread.start()
        thread.join(timeout=30)

    assert len(desfechos) == 1, "a trava legítima passou, e a do A-01 foi recusada na thread"
    assert [tabelas for tabelas, _ in acusadas] == [["resultados_resultadoetapa"]]
