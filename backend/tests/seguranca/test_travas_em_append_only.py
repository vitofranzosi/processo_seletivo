"""Nenhum código de produção trava linha de tabela append-only (A-01 da auditoria de 31/10/2026).

**A regra.** O PostgreSQL exige o privilégio de `UPDATE` para `SELECT ... FOR UPDATE`, `FOR NO KEY
UPDATE`, `FOR SHARE` e `FOR KEY SHARE`, e a política nega `UPDATE` à role de runtime em toda tabela
de `TABELAS_APPEND_ONLY`. Trava ali passa na suíte, que roda como superusuário, e é `permission
denied` em produção — foi assim na revogação da `106` e no julgamento com efeito da `018`.

**O guardião anterior** (`test_privilegios.py`) varria só `seguranca/`. Este varre todo
`processo_seletivo/`, menos as migrations, e responde por duas formas de travar:

```text
ORM      X.manager[...].select_for_update(...)   ← o modelo X, os de select_related e as junções
                                                    dos filtros da mesma cadeia, salvo `of=`
SQL      "... FROM t ... JOIN u ... FOR SHARE"    ← as tabelas de FROM/JOIN da instrução
```

**Não é um analisador geral, e não tenta ser.** Quando a cadeia não começa num modelo nomeado — uma
variável, uma relação reversa, uma função que devolve *queryset* —, o alvo vem de `DECLARADAS`,
escrito à mão e conferido pelo mesmo critério. A trava nova que ninguém declarou reprova com a
instrução de declarar: é o momento em que alguém olha para ela, que é o que faltou nas duas vezes.
O que escapa: junção que um *manager* acrescenta por dentro (o de vigência faz uma); por isso os
fluxos de fumaça de `tests/integration/test_fluxos_com_privilegios_de_producao.py` existem ao lado.
"""

import ast
import pathlib
import re

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist

from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY

RAIZ = pathlib.Path(__file__).resolve().parents[2] / "processo_seletivo"

# (arquivo relativo a `processo_seletivo/`, receptor de `select_for_update` como o `ast` o escreve)
# → os modelos que a trava alcança. Mantenha a razão em uma linha: é ela que se confere na revisão.
DECLARADAS = {
    # `_unidade`: a consulta é `Unidade.objects.filter(codigo=...)`.
    ("unidades/application/registro.py", "consulta"): ("Unidade",),
    # `_autoridade`: `select_related("unidade")` sem `of=` trava as duas.
    ("unidades/application/autoridades.py", "consulta"): ("AutoridadeHabilitada", "Unidade"),
    ("processos/application/finalizacao.py", "processo.editais"): ("Edital",),
    ("identidade/application/credenciais.py", "identidade.credenciais"): ("CandidateEmail",),
    # `vigentes()` filtra e exclui por subconsulta — subconsulta não é travada.
    ("requerimentos/application/preencher.py", "vigentes(inscricao)"): ("RequerimentoDeMatricula",),
}

TRAVA_EM_SQL = re.compile(r"\bFOR\s+(?:NO\s+KEY\s+UPDATE|UPDATE|KEY\s+SHARE|SHARE)\b", re.I)
TABELA_EM_SQL = re.compile(r"\b(?:FROM|JOIN)\s+\"?(\w+)\"?", re.I)
# Os métodos cujos argumentos nomeados viram junção quando atravessam relação.
COM_LOOKUP = {"filter", "exclude", "get"}


def _modelos_por_nome():
    return {modelo.__name__: modelo for modelo in apps.get_models()}


def _caminho(modelo, lookup):
    """Os modelos que um caminho `a__b__c` atravessa a partir de `modelo`."""
    alcancados = []
    for parte in lookup.split("__"):
        try:
            campo = modelo._meta.get_field(parte)
        except FieldDoesNotExist:
            break
        if not campo.is_relation or campo.related_model is None:
            break
        modelo = campo.related_model
        alcancados.append(modelo)
    return alcancados


def _cadeia(no, pais):
    """As chamadas de método da cadeia em que `no` está, de dentro para fora, e a raiz dela."""
    chamadas = []
    atual = no
    # Para fora: `x.select_for_update().filter(...).first()`.
    while isinstance(pais.get(atual), ast.Attribute) and isinstance(
        pais.get(pais[atual]), ast.Call
    ):
        atual = pais[pais[atual]]
        chamadas.append(atual)
    # Para dentro: `X.objects.select_related(...).select_for_update()`.
    raiz = no.func.value
    while isinstance(raiz, ast.Call) and isinstance(raiz.func, ast.Attribute):
        chamadas.append(raiz)
        raiz = raiz.func.value
    return chamadas, raiz


def _modelo_da_raiz(raiz, nomes):
    if isinstance(raiz, ast.Attribute):
        base = raiz.value
        if isinstance(base, ast.Name) and base.id in nomes:
            return nomes[base.id]
        if (
            isinstance(base, ast.Call)
            and isinstance(base.func, ast.Name)
            and base.func.id == "get_user_model"
        ):
            return get_user_model()
    return None


def _travados_pelo_orm(no, pais, arquivo, nomes):
    """Os modelos que um `select_for_update` alcança, ou `None` se a raiz não é legível."""
    chamadas, raiz = _cadeia(no, pais)
    receptor = ast.unparse(no.func.value)
    declarados = DECLARADAS.get((arquivo, receptor))
    if declarados is not None:
        return [nomes[nome] for nome in declarados]
    modelo = _modelo_da_raiz(raiz, nomes)
    if modelo is None:
        return None
    of = next((k.value for k in no.keywords if k.arg == "of"), None)
    if of is not None:
        caminhos = [e.value for e in getattr(of, "elts", []) if isinstance(e, ast.Constant)]
        return [modelo] + [m for c in caminhos if c != "self" for m in _caminho(modelo, c)]
    travados = [modelo]
    for chamada in chamadas:
        metodo = chamada.func.attr
        if metodo == "select_related":
            for argumento in chamada.args:
                if isinstance(argumento, ast.Constant):
                    travados += _caminho(modelo, argumento.value)
        elif metodo in COM_LOOKUP:
            for chave in chamada.keywords:
                if chave.arg:
                    travados += _caminho(modelo, chave.arg)
    return travados


def _docstrings(arvore):
    for no in ast.walk(arvore):
        corpo = getattr(no, "body", None)
        if isinstance(corpo, list) and corpo and isinstance(corpo[0], ast.Expr):
            if isinstance(corpo[0].value, ast.Constant):
                yield corpo[0].value


def travas_em_append_only(fonte, arquivo):
    """`(violações, não declaradas)` de um arquivo-fonte — separado para o autoteste."""
    nomes = _modelos_por_nome()
    append_only = set(TABELAS_APPEND_ONLY)
    arvore = ast.parse(fonte)
    pais = {filho: pai for pai in ast.walk(arvore) for filho in ast.iter_child_nodes(pai)}
    docstrings = set(map(id, _docstrings(arvore)))
    violacoes, nao_declaradas = [], []
    for no in ast.walk(arvore):
        if (
            isinstance(no, ast.Call)
            and isinstance(no.func, ast.Attribute)
            and no.func.attr == "select_for_update"
        ):
            travados = _travados_pelo_orm(no, pais, arquivo, nomes)
            if travados is None:
                nao_declaradas.append((arquivo, ast.unparse(no.func.value), no.lineno))
                continue
            for modelo in travados:
                if modelo._meta.db_table in append_only:
                    violacoes.append((arquivo, no.lineno, modelo._meta.db_table))
        elif (
            isinstance(no, ast.Constant)
            and isinstance(no.value, str)
            and id(no) not in docstrings
            and TRAVA_EM_SQL.search(no.value)
        ):
            for tabela in TABELA_EM_SQL.findall(no.value):
                if tabela in append_only:
                    violacoes.append((arquivo, no.lineno, tabela))
    return violacoes, nao_declaradas


def _producao():
    for caminho in sorted(RAIZ.rglob("*.py")):
        if "migrations" in caminho.parts:
            continue
        yield caminho.relative_to(RAIZ).as_posix(), caminho.read_text()


def test_nenhuma_trava_alcanca_tabela_append_only():
    violacoes, nao_declaradas, examinadas = [], [], 0
    for arquivo, fonte in _producao():
        achadas, sem_alvo = travas_em_append_only(fonte, arquivo)
        violacoes += achadas
        nao_declaradas += sem_alvo
        examinadas += fonte.count(".select_for_update(")

    # Uma varredura que não encontrasse trava nenhuma passaria por não ter olhado. Eram 45 em
    # 31/10/2026; o piso só precisa estar longe do zero.
    assert examinadas >= 30, examinadas

    assert not violacoes, (
        "trava de linha em tabela append-only: a role de produção não tem UPDATE nela, e o "
        f"PostgreSQL o exige para FOR UPDATE/FOR SHARE. Trave o agregado acima: {violacoes}"
    )
    assert not nao_declaradas, (
        "select_for_update sem modelo legível na própria cadeia: declare em DECLARADAS os modelos "
        f"que a trava alcança — {nao_declaradas}"
    )


def test_toda_declaracao_ainda_existe():
    """Declaração órfã é a porta por onde a lista deixaria de ser conferida."""
    presentes = set()
    for arquivo, fonte in _producao():
        for no in ast.walk(ast.parse(fonte)):
            if isinstance(no, ast.Attribute) and no.attr == "select_for_update":
                presentes.add((arquivo, ast.unparse(no.value)))
    assert set(DECLARADAS) <= presentes, set(DECLARADAS) - presentes


# ---------------------------------------------------------------------------
# O autoteste: o guardião vê a reintrodução do A-01
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
            "Recurso.objects.select_related('inscricao').select_for_update()"
            ".filter(decisoes__especie='X')",
            "recursos_decisaorecurso",
            id="junção por filtro sem of",
        ),
        pytest.param(
            'cursor.execute("SELECT id FROM recursos_recurso WHERE id = %s FOR SHARE", [x])',
            "recursos_recurso",
            id="SQL escrito à mão",
        ),
    ],
)
def test_o_guardiao_reprova_a_reintroducao(fonte, tabela):
    violacoes, _ = travas_em_append_only(fonte, "recursos/application/julgar.py")
    assert tabela in {encontrada for _, _, encontrada in violacoes}


@pytest.mark.parametrize(
    "fonte",
    [
        pytest.param("ProcessoSeletivo.objects.select_for_update().get(pk=1)", id="o Processo"),
        pytest.param(
            "Atribuicao.objects.select_for_update(of=('self',)).filter(avaliacao__id=1)",
            id="of restringe a trava",
        ),
        pytest.param(
            '"""Travar o Resultado com FOR UPDATE FROM resultados_resultadoetapa não serve."""',
            id="docstring não é SQL",
        ),
    ],
)
def test_o_guardiao_aceita_o_que_a_producao_aceita(fonte):
    assert travas_em_append_only(fonte, "x.py") == ([], [])
