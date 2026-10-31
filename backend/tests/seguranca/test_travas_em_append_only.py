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

# (arquivo relativo a `processo_seletivo/`, função que contém a trava, receptor de
# `select_for_update` como o `ast` o escreve) → os modelos que a trava alcança. Só o que a varredura
# não lê sozinha: relação reversa e função que devolve *queryset*. Variável local ela segue até a
# atribuição. Mantenha a razão em uma linha: é ela que se confere na revisão.
DECLARADAS = {
    ("processos/application/finalizacao.py", "_editais_pendentes_travados", "processo.editais"): (
        "Edital",
    ),
    (
        "identidade/application/credenciais.py",
        "tornar_principal",
        "identidade.credenciais",
    ): ("CandidateEmail",),
    (
        "identidade/application/credenciais.py",
        "remover",
        "identidade.credenciais",
    ): ("CandidateEmail",),
    # `vigentes()` filtra e exclui por subconsulta — subconsulta não é travada.
    (
        "requerimentos/application/preencher.py",
        "_rascunho_para_escrita",
        "vigentes(inscricao)",
    ): ("RequerimentoDeMatricula",),
}

TRAVA_EM_SQL = re.compile(r"\bFOR\s+(?:NO\s+KEY\s+UPDATE|UPDATE|KEY\s+SHARE|SHARE)\b", re.I)
TABELA_EM_SQL = re.compile(r"\b(?:FROM|JOIN)\s+\"?(\w+)\"?(?:\s+(?:AS\s+)?\"?(\w+)\"?)?", re.I)
OF_EM_SQL = re.compile(
    r"\bFOR\s+(?:NO\s+KEY\s+UPDATE|UPDATE|KEY\s+SHARE|SHARE)\s+OF\s+([\w\s,\"]+)", re.I
)
TABELA_INTERPOLADA = re.compile(r"\b(?:FROM|JOIN)\s+\{\}", re.I)
# O que pode seguir o nome da tabela sem ser apelido dela.
PALAVRAS_DO_SQL = {
    "where", "join", "inner", "left", "right", "full", "cross", "on", "using", "for", "order",
    "group", "limit", "offset", "having", "union", "window", "natural", "lateral",
}  # fmt: skip
# Os métodos cujos argumentos nomeados viram junção quando atravessam relação.
COM_LOOKUP = {"filter", "exclude", "get"}
# O que `select_related()` sem argumentos segue: as FKs não nulas, até esta profundidade.
PROFUNDIDADE_DO_SELECT_RELATED = 5


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


def _fks_nao_nulas(modelo, profundidade=PROFUNDIDADE_DO_SELECT_RELATED):
    """O que `select_related()` **sem argumentos** junta: toda FK não nula, recursivamente."""
    if profundidade == 0:
        return []
    alcancados = []
    for campo in modelo._meta.fields:
        if (campo.many_to_one or campo.one_to_one) and not campo.null:
            alcancados.append(campo.related_model)
            alcancados += _fks_nao_nulas(campo.related_model, profundidade - 1)
    return alcancados


def _para_dentro(expressao):
    """`X.objects.a().b()` → (`X.objects`, [b(), a()])."""
    chamadas = []
    while isinstance(expressao, ast.Call) and isinstance(expressao.func, ast.Attribute):
        chamadas.append(expressao)
        expressao = expressao.func.value
    return expressao, chamadas


def _para_fora(no, pais):
    """As chamadas encadeadas depois de `no`: `no.filter(...).first()`."""
    chamadas = []
    while isinstance(pais.get(no), ast.Attribute) and isinstance(pais.get(pais[no]), ast.Call):
        if pais[pais[no]].func is not pais[no]:
            break
        no = pais[pais[no]]
        chamadas.append(no)
    return chamadas


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


def _funcao_de(no, pais):
    while no is not None and not isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
        no = pais.get(no)
    return no


def _origens(expressao, funcao, nomes, vistas=frozenset()):
    """Cada `(modelo, chamadas)` de onde a expressão pode vir, seguindo atribuições locais.

    `consulta = X.objects.filter(...)` e, adiante, `consulta = consulta.select_for_update()`: a
    segunda é a própria trava, e a primeira é de onde vem o modelo e as junções. Toda atribuição
    à variável na função conta — a varredura não sabe qual ramo roda, e erra para o lado de
    examinar demais. `None` quando alguma origem não chega a um modelo nomeado.
    """
    raiz, chamadas = _para_dentro(expressao)
    modelo = _modelo_da_raiz(raiz, nomes)
    if modelo is not None:
        return [(modelo, chamadas)]
    if not (isinstance(raiz, ast.Name) and funcao is not None) or raiz.id in vistas:
        return None
    origens = []
    for no in ast.walk(funcao):
        alvos = no.targets if isinstance(no, ast.Assign) else [getattr(no, "target", None)]
        if not isinstance(no, (ast.Assign, ast.AnnAssign)) or no.value is None:
            continue
        if not any(isinstance(alvo, ast.Name) and alvo.id == raiz.id for alvo in alvos):
            continue
        valor_raiz, _ = _para_dentro(no.value)
        if isinstance(valor_raiz, ast.Name) and valor_raiz.id == raiz.id:
            continue  # a reatribuição que só encadeia sobre ela mesma
        de_la = _origens(no.value, funcao, nomes, vistas | {raiz.id})
        if de_la is None:
            return None
        origens += [(modelo, chamadas + anteriores) for modelo, anteriores in de_la]
    return origens or None


def _alcance(modelo, chamadas, of):
    if of is not None:
        caminhos = [e.value for e in getattr(of, "elts", []) if isinstance(e, ast.Constant)]
        return [modelo] + [m for c in caminhos if c != "self" for m in _caminho(modelo, c)[-1:]]
    travados = [modelo]
    for chamada in chamadas:
        metodo = chamada.func.attr
        if metodo == "select_related":
            if not chamada.args:
                travados += _fks_nao_nulas(modelo)
            for argumento in chamada.args:
                if isinstance(argumento, ast.Constant):
                    travados += _caminho(modelo, argumento.value)
        elif metodo in COM_LOOKUP:
            for chave in chamada.keywords:
                if chave.arg:
                    travados += _caminho(modelo, chave.arg)
    return travados


def _travados_pelo_orm(no, pais, arquivo, nomes):
    """Os modelos que um `select_for_update` alcança, ou `None` se a origem não é legível."""
    funcao = _funcao_de(no, pais)
    chave = (arquivo, getattr(funcao, "name", ""), ast.unparse(no.func.value))
    if chave in DECLARADAS:
        return [nomes[nome] for nome in DECLARADAS[chave]]
    origens = _origens(no.func.value, funcao, nomes)
    if origens is None:
        return None
    of = next((k.value for k in no.keywords if k.arg == "of"), None)
    depois = _para_fora(no, pais)
    return [
        travado for modelo, antes in origens for travado in _alcance(modelo, antes + depois, of)
    ]


def _fora_dos_parenteses(sql):
    """Só o nível externo da instrução: subconsulta e `EXTRACT(... FROM ...)` não são travados."""
    nivel, fora = 0, []
    for caractere in sql:
        if caractere == "(":
            nivel += 1
        elif caractere == ")":
            nivel = max(nivel - 1, 0)
        elif nivel == 0:
            fora.append(caractere)
    return "".join(fora)


def _travadas_pelo_sql(sql):
    """As tabelas que a instrução trava: as do `OF`, se houver, ou as de FROM/JOIN externos."""
    externo = _fora_dos_parenteses(sql)
    tabelas = {}
    for tabela, apelido in TABELA_EM_SQL.findall(externo):
        tabelas[tabela] = tabela
        if apelido and apelido.lower() not in PALAVRAS_DO_SQL:
            tabelas[apelido] = tabela
    of = OF_EM_SQL.search(externo)
    if of is None:
        return set(tabelas.values())
    nomes = [nome.strip().strip('"') for nome in of.group(1).split(",")]
    return {tabelas.get(nome.split()[0], nome.split()[0]) for nome in nomes if nome.split()}


def _docstrings(arvore):
    for no in ast.walk(arvore):
        corpo = getattr(no, "body", None)
        if isinstance(corpo, list) and corpo and isinstance(corpo[0], ast.Expr):
            if isinstance(corpo[0].value, ast.Constant):
                yield corpo[0].value


def _texto(no):
    """O SQL de uma string, com `{}` onde uma f-string interpola."""
    if isinstance(no, ast.Constant):
        return no.value
    return "".join(parte.value if isinstance(parte, ast.Constant) else "{}" for parte in no.values)


def travas_em_append_only(fonte, arquivo):
    """`(violações, não declaradas, travas examinadas)` de um arquivo; separado para o autoteste."""
    nomes = _modelos_por_nome()
    append_only = set(TABELAS_APPEND_ONLY)
    arvore = ast.parse(fonte)
    pais = {filho: pai for pai in ast.walk(arvore) for filho in ast.iter_child_nodes(pai)}
    docstrings = set(map(id, _docstrings(arvore)))
    violacoes, nao_declaradas, examinadas = [], [], 0
    for no in ast.walk(arvore):
        if (
            isinstance(no, ast.Call)
            and isinstance(no.func, ast.Attribute)
            and no.func.attr == "select_for_update"
        ):
            examinadas += 1
            travados = _travados_pelo_orm(no, pais, arquivo, nomes)
            if travados is None:
                nao_declaradas.append((arquivo, ast.unparse(no.func.value), no.lineno))
                continue
            for modelo in travados:
                if modelo._meta.db_table in append_only:
                    violacoes.append((arquivo, no.lineno, modelo._meta.db_table))
            continue
        e_texto = isinstance(no, ast.JoinedStr) or (
            isinstance(no, ast.Constant)
            and isinstance(no.value, str)
            and not isinstance(pais.get(no), ast.JoinedStr)
            and id(no) not in docstrings
        )
        if not e_texto:
            continue
        sql = _texto(no)
        if not TRAVA_EM_SQL.search(sql):
            continue
        examinadas += 1
        if TABELA_INTERPOLADA.search(_fora_dos_parenteses(sql)):
            nao_declaradas.append((arquivo, sql.strip()[:60], no.lineno))
        for tabela in _travadas_pelo_sql(sql):
            if tabela in append_only:
                violacoes.append((arquivo, no.lineno, tabela))
    return violacoes, nao_declaradas, examinadas


def _producao():
    for caminho in sorted(RAIZ.rglob("*.py")):
        if "migrations" in caminho.parts:
            continue
        yield caminho.relative_to(RAIZ).as_posix(), caminho.read_text()


def test_nenhuma_trava_alcanca_tabela_append_only():
    violacoes, nao_declaradas, examinadas = [], [], 0
    for arquivo, fonte in _producao():
        achadas, sem_alvo, vistas = travas_em_append_only(fonte, arquivo)
        violacoes += achadas
        nao_declaradas += sem_alvo
        examinadas += vistas

    # Uma varredura que não encontrasse trava nenhuma passaria por não ter olhado. A contagem é a
    # das travas que a análise de fato visitou, pelo ORM e em SQL — eram 47 em 31/10/2026 —, e o
    # piso só precisa estar longe do zero.
    assert examinadas >= 30, examinadas

    assert not violacoes, (
        "trava de linha em tabela append-only: a role de produção não tem UPDATE nela, e o "
        f"PostgreSQL o exige para FOR UPDATE/FOR SHARE. Trave o agregado acima: {violacoes}"
    )
    assert not nao_declaradas, (
        "trava sem alvo legível (relação reversa, função que devolve queryset, tabela interpolada "
        f"no SQL): declare em DECLARADAS os modelos que ela alcança — {nao_declaradas}"
    )


def test_toda_declaracao_ainda_existe():
    """Declaração órfã é a porta por onde a lista deixaria de ser conferida."""
    presentes = set()
    for arquivo, fonte in _producao():
        arvore = ast.parse(fonte)
        pais = {filho: pai for pai in ast.walk(arvore) for filho in ast.iter_child_nodes(pai)}
        for no in ast.walk(arvore):
            if isinstance(no, ast.Attribute) and no.attr == "select_for_update":
                funcao = _funcao_de(no, pais)
                presentes.add((arquivo, getattr(funcao, "name", ""), ast.unparse(no.value)))
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

PELA_VARIAVEL = """
def _registrada(codigo):
    consulta = Unidade.objects.filter(codigo=codigo)
    consulta = consulta.select_for_update()
    return consulta.first()


def _candidata(inscricao_id, travar=False):
    consulta = Inscricao.objects.filter(pk=inscricao_id).filter(resultados__isnull=False)
    if travar:
        consulta = consulta.select_for_update()
    return consulta.first()
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
            "DecisaoRecurso.objects.none().select_for_update()",
            "recursos_decisaorecurso",
            id="o próprio modelo append-only",
        ),
        pytest.param(
            "PosicaoNaOrdem.objects.none()",
            None,
            id="sem trava nada se acusa",
        ),
        pytest.param(
            "Recurso.objects.select_related().select_for_update().get(pk=1)",
            "recursos_recurso",
            id="select_related sem argumentos",
        ),
        pytest.param(
            "JuizoDeAdmissibilidade.objects.select_related().select_for_update(of=())",
            "recursos_juizodeadmissibilidade",
            id="of vazio ainda trava o próprio",
        ),
        pytest.param(
            PELA_VARIAVEL,
            "resultados_resultadoetapa",
            id="junção vinda pela atribuição da variável",
        ),
        pytest.param(
            'cursor.execute("SELECT id FROM recursos_recurso WHERE id = %s FOR SHARE", [x])',
            "recursos_recurso",
            id="SQL escrito à mão",
        ),
        pytest.param(
            'cursor.execute("SELECT r.id FROM recursos_recurso r JOIN processos_edital e '
            'ON true FOR UPDATE OF r")',
            "recursos_recurso",
            id="OF pelo apelido",
        ),
    ],
)
def test_o_guardiao_reprova_a_reintroducao(fonte, tabela):
    violacoes, _, _ = travas_em_append_only(fonte, "recursos/application/julgar.py")
    encontradas = {encontrada for _, _, encontrada in violacoes}
    assert (tabela in encontradas) if tabela else not encontradas


def test_o_select_related_sem_argumentos_segue_as_fks_nao_nulas():
    """O `Juízo` tem FK não nula para o `Recurso`: a trava sem `of=` alcança os dois."""
    violacoes, _, _ = travas_em_append_only(
        "JuizoDeAdmissibilidade.objects.select_related().select_for_update()", "x.py"
    )
    assert {"recursos_juizodeadmissibilidade", "recursos_recurso"} <= {
        tabela for _, _, tabela in violacoes
    }


def test_a_variavel_de_outra_funcao_nao_empresta_a_origem():
    """Cada `consulta` é seguida na própria função — a da Unidade não absolve a da Inscrição."""
    violacoes, nao_declaradas, examinadas = travas_em_append_only(PELA_VARIAVEL, "x.py")
    assert examinadas == 2 and not nao_declaradas
    assert {linha for _, linha, _ in violacoes} == {11}


def test_tabela_interpolada_no_sql_pede_declaracao():
    fonte = 'cursor.execute(f"SELECT id FROM {tabela} WHERE id = %s FOR SHARE", [x])'
    violacoes, nao_declaradas, examinadas = travas_em_append_only(fonte, "x.py")
    assert (violacoes, examinadas) == ([], 1)
    assert len(nao_declaradas) == 1


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
        pytest.param(
            'cursor.execute("SELECT id FROM processos_processoseletivo WHERE id IN '
            '(SELECT processo_id FROM recursos_recurso) FOR UPDATE")',
            id="subconsulta não é travada",
        ),
        pytest.param(
            'cursor.execute("SELECT p.id FROM processos_processoseletivo p JOIN recursos_recurso r '
            'ON true FOR UPDATE OF p")',
            id="OF deixa a junção destravada",
        ),
        pytest.param(
            'cursor.execute("SELECT EXTRACT(YEAR FROM recursos_recurso.x) FROM processos_edital '
            'FOR SHARE")',
            id="EXTRACT não é tabela",
        ),
    ],
)
def test_o_guardiao_aceita_o_que_a_producao_aceita(fonte):
    violacoes, nao_declaradas, _ = travas_em_append_only(fonte, "x.py")
    assert (violacoes, nao_declaradas) == ([], [])
