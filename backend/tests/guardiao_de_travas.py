"""Quais tabelas uma instrução trava, e o vigia que confere isso em todo SQL da suíte (A-01).

**A regra.** O PostgreSQL exige o privilégio de `UPDATE` para `SELECT ... FOR UPDATE`, `FOR NO KEY
UPDATE`, `FOR SHARE` e `FOR KEY SHARE`, e a política nega `UPDATE` à role de runtime em toda tabela
de `TABELAS_APPEND_ONLY`. Uma trava ali passa na suíte, que roda como superusuário, e é `permission
denied` em produção — foi assim na revogação da `106` e no julgamento com efeito da `018`.

**Por que ler o SQL executado, e não o código.** A primeira versão deste guardião analisava o
código-fonte e reimplementava o Django para descobrir o que cada `select_for_update` alcança — o
`of=`, o `select_related` com e sem argumentos, as junções dos filtros, as atribuições de variável
— em ~490 linhas, e ainda não via a junção que um *manager* acrescenta por dentro. O SQL que o
Django de fato gerou já responde tudo isso, exato. O vigia confere cada instrução de trava que a
suíte executa (eram ~99,6 mil numa rodada completa, em 31/10/2026, sem custo de tempo mensurável).
O que ele não vê é o caminho que nenhum teste executa: por isso `test_travas_em_append_only.py`
guarda a checagem estática mínima, pelo modelo que abre a cadeia e pelo SQL escrito à mão.
"""

import contextlib
import re

from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY

APPEND_ONLY = frozenset(TABELAS_APPEND_ONLY)

TRAVA = re.compile(r"\bFOR\s+(?:NO\s+KEY\s+UPDATE|UPDATE|KEY\s+SHARE|SHARE)\b", re.I)
OF = re.compile(
    r"\bFOR\s+(?:NO\s+KEY\s+UPDATE|UPDATE|KEY\s+SHARE|SHARE)\s+OF\s+(.+?)"
    r"(?:\s+(?:NOWAIT|SKIP\s+LOCKED)|\s+FOR\s|$)",
    re.I | re.S,
)
TABELA = re.compile(r"\b(?:FROM|JOIN)\s+\"?(\w+)\"?(?:\s+(?:AS\s+)?\"?(\w+)\"?)?", re.I)
# O que pode seguir o nome da tabela sem ser apelido dela.
PALAVRAS_DO_SQL = frozenset(
    "where join inner left right full cross on using for order group limit offset having union "
    "window natural lateral".split()
)


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


def tabelas_travadas(sql):
    """As tabelas que a instrução trava: as do `OF`, se houver, ou as de FROM/JOIN externos."""
    externo = _fora_dos_parenteses(sql)
    if not TRAVA.search(externo):
        return set()
    tabelas = {}
    for tabela, apelido in TABELA.findall(externo):
        tabelas[tabela] = tabela
        if apelido and apelido.lower() not in PALAVRAS_DO_SQL:
            tabelas[apelido] = tabela
    of = OF.search(externo)
    if of is None:
        return set(tabelas.values())
    nomes = [nome.strip().strip('"') for nome in of.group(1).split(",")]
    return {tabelas.get(nome, nome) for nome in nomes if nome}


class TravaEmAppendOnly(AssertionError):
    """A instrução que a role de produção recusaria — levantada antes de chegar ao banco."""


@contextlib.contextmanager
def vigiando(conexao):
    """Recusa toda trava que alcance tabela append-only, e devolve as acusadas.

    Vale para `conexao` **e para toda conexão aberta enquanto o contexto durar**, em qualquer
    *thread*: os casos de corrida abrem uma por *thread*, e é nelas que o comando examinado roda.
    Elas são alcançadas pelo sinal `connection_created` e soltas na saída, para que uma conexão que
    sobreviva ao caso (a do `live_server`, que é uma *thread* longa) não leve o vigia adiante.

    Levanta no ponto da instrução, para que o rastro aponte o código que trava, **e** guarda a
    acusação: código que engula a exceção não apaga o achado, que o fim do caso ainda cobra.
    """
    from django.db.backends.signals import connection_created

    acusadas = []

    def vigia(execute, sql, params, many, context):
        if isinstance(sql, str) and "FOR " in sql.upper():
            alcancadas = tabelas_travadas(sql) & APPEND_ONLY
            if alcancadas:
                acusadas.append((sorted(alcancadas), sql))
                raise TravaEmAppendOnly(
                    f"trava de linha em tabela append-only {sorted(alcancadas)}: a role de "
                    "produção não tem UPDATE nela, e o PostgreSQL o exige para FOR UPDATE/FOR "
                    "SHARE. Trave o agregado acima (o ProcessoSeletivo, o Edital).\n" + sql
                )
        return execute(sql, params, many, context)

    vigiadas = []

    def vigiar(conexao_nova):
        if vigia not in conexao_nova.execute_wrappers:
            conexao_nova.execute_wrappers.append(vigia)
            vigiadas.append(conexao_nova)

    def ao_conectar(sender, connection, **kwargs):
        vigiar(connection)

    vigiar(conexao)
    connection_created.connect(ao_conectar, weak=False)
    try:
        yield acusadas
    finally:
        connection_created.disconnect(ao_conectar)
        for vigiada in vigiadas:
            if vigia in vigiada.execute_wrappers:
                vigiada.execute_wrappers.remove(vigia)
