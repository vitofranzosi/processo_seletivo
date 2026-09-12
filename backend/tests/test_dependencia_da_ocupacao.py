"""A dependência corre num sentido só, e a `016` não importa o que ordena (016, `R-002`, `FR-257`).

**Por que é varredura de import, e não de texto.** A `FR-257` proíbe a `016` de selecionar
candidato, ordenar, desempatar ou convocar. Uma varredura de vocabulário — como a que o corte usa —
prova que a tela não *diz* essas palavras; não prova que nenhum caminho as *faz*. Prova de import
prova: o que a feature não importa, ela não executa.

**A lista permitida é curta de propósito.** `emissao_do_corte` é a única porta, porque é por ela que
a `016` causa a faixa sem escolher ninguém — quem lê a ordem e seleciona é a `014`, do outro lado da
chamada. `emissao` (que emite ordem), `combinacao` e `desempate` ficam de fora: importá-los seria a
`016` passando a ter meio de ordenar, e a proibição deixaria de ser verificável.

**E o sentido contrário é o que a fronteira de 11/09/2026 protege.** Se `classificacao` lesse a
apuração para descobrir a causa da faixa seguinte, a `014` deixaria de ser compreensível sozinha.
"""

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"
OCUPACAO = RAIZ / "ocupacao"
CLASSIFICACAO = RAIZ / "classificacao"

# O que a `016` pode importar de `classificacao`. Nada além disto.
PERMITIDOS = {
    "processo_seletivo.classificacao.models",
    "processo_seletivo.classificacao.application.selectors",
    "processo_seletivo.classificacao.application.corte",
    "processo_seletivo.classificacao.application.emissao_do_corte",
    "processo_seletivo.classificacao.domain.universo",
}

# O que ela **não** pode importar, e a razão de cada um.
PROIBIDOS = {
    # Emite ordem. Importá-la daria à `016` meio de ordenar, que é o que a `FR-257` proíbe.
    "processo_seletivo.classificacao.application.emissao",
    # Combina pontuação: é o cálculo da ordem.
    "processo_seletivo.classificacao.domain.combinacao",
    # Desempata: é escolha entre pessoas, e escolha é da `014`.
    "processo_seletivo.classificacao.domain.desempate",
}

pytestmark = [pytest.mark.contract]


def _importados(arquivo):
    """Todo módulo que o arquivo importa, incluindo os de dentro de função.

    Importar dentro de função é o caminho normal aqui — vários módulos o fazem para evitar ciclo —,
    e uma varredura que só olhasse o topo do arquivo não veria nada.
    """
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
            nomes.update(f"{no.module}.{alias.name}" for alias in no.names)
    return nomes


def _modulos(pasta):
    return [p for p in pasta.rglob("*.py") if "migrations" not in p.parts]


def test_classificacao_nunca_importa_ocupacao():
    """**A seta é da `016` para a `014`** (`R-002`).

    O import circular seria o menor dos problemas: o grave é que a `014` deixaria de ser
    compreensível sozinha, contra a fronteira que a decisão de 11/09/2026 fixou.
    """
    ofensores = {
        arquivo.relative_to(RAIZ).as_posix(): sorted(
            nome for nome in _importados(arquivo) if "ocupacao" in nome
        )
        for arquivo in _modulos(CLASSIFICACAO)
        if any("ocupacao" in nome for nome in _importados(arquivo))
    }

    assert ofensores == {}, ofensores


def test_a_ocupacao_nao_importa_o_que_ordena_nem_desempata():
    """**`FR-257` como prova de import.** O que a feature não importa, ela não executa."""
    ofensores = {}
    for arquivo in _modulos(OCUPACAO):
        proibidos = sorted(_importados(arquivo) & PROIBIDOS)
        if proibidos:
            ofensores[arquivo.relative_to(RAIZ).as_posix()] = proibidos

    assert ofensores == {}, ofensores


def test_a_ocupacao_le_classificacao_so_pelas_portas_declaradas():
    """A lista permitida é curta de propósito, e crescer nela é conversa, não descuido.

    Acrescentar um módulo aqui exige dizer por que a `016` precisa dele — que é exatamente a
    pergunta que este teste existe para forçar, no molde da varredura de vigência da `018`.
    """
    inesperados = {}
    for arquivo in _modulos(OCUPACAO):
        de_classificacao = {
            nome
            for nome in _importados(arquivo)
            if nome.startswith("processo_seletivo.classificacao")
        }
        fora = sorted(nome for nome in de_classificacao if nome not in PERMITIDOS)
        # `from x.y import z` registra `x.y` e `x.y.z`; o que interessa é o módulo, e os nomes
        # importados de dentro dele caem aqui como sufixo. Descartamos os que são prefixados por um
        # permitido, que é o caso de `from ...selectors import ato_vigente`.
        fora = [nome for nome in fora if not any(nome.startswith(f"{p}.") for p in PERMITIDOS)]
        if fora:
            inesperados[arquivo.relative_to(RAIZ).as_posix()] = fora

    assert inesperados == {}, inesperados
