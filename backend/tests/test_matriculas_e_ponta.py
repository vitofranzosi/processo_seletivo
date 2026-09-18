"""A exportação é a **ponta da leitura**, e isto é prova de import — não de texto (031).

**O app `matriculas` lê todo mundo e ninguém o lê de volta.** A `029` custou uma sessão a um ciclo
de importação — `inscricoes → requerimentos → convocacao → inscricoes` —, resolvido com um módulo
que não podia importar `convocacao.application`. Um app que ninguém importa não entra em ciclo
nenhum, e a regra fica verificável sozinha: se algum dia outro app importar `matriculas`, é sinal de
que a feature deixou de ser ponta.

**`interface` é a exceção, e ela é nomeada.** A Fase 7 desta feature existe porque o Princípio VI
não considera entregue uma capacidade que nenhuma interface alcança — de modo que o canal do ator
**precisa** chamar a exportação. `interface` é canal, e nenhum app de domínio a importa de volta: o
ciclo continua impossível, e a exceção não afrouxa a regra.

**E a exportação não chama o sistema acadêmico** (`FR-450`). O arquivo é entregue a uma pessoa; não
há cliente HTTP, não há integração programática, e não há como haver sem que esta varredura acuse.
"""

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"

# O único app que pode conhecer `matriculas`: o canal do ator. Ver a razão na docstring.
CANAL = "interface"

APPS = sorted(
    caminho.name
    for caminho in RAIZ.iterdir()
    if caminho.is_dir() and (caminho / "__init__.py").exists() and caminho.name != "matriculas"
)

# O que um app que **não** chama serviço externo não importa. `requests` e `httpx` não são
# dependências deste projeto; `urllib`, `http.client` e `socket` são da biblioteca padrão e
# entrariam sem que nada acusasse.
DA_REDE = ("requests", "httpx", "urllib", "http.client", "socket", "aiohttp")


def modulos(app):
    return [
        caminho
        for caminho in (RAIZ / app).rglob("*.py")
        if "migrations" not in caminho.parts and "__pycache__" not in caminho.parts
    ]


def importados(caminho):
    """Os módulos que este arquivo importa — **inclusive os importados dentro de função**.

    O import tardio é o recurso que este repositório usa para quebrar ciclo, e por isso a varredura
    desce a árvore inteira: um import escondido dentro de um `def` criaria a aresta do mesmo jeito.
    """
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
    return nomes


@pytest.mark.parametrize("app", [app for app in APPS if app != CANAL])
def test_nenhum_app_de_dominio_importa_matriculas(app):
    """`T034`: a feature continua sendo ponta de leitura."""
    achados = {
        str(caminho.relative_to(RAIZ)): sorted(
            nome for nome in importados(caminho) if "matriculas" in nome
        )
        for caminho in modulos(app)
    }
    culpados = {arquivo: nomes for arquivo, nomes in achados.items() if nomes}
    assert culpados == {}, (
        f"{app} passou a importar `matriculas`: a exportação deixou de ser ponta de leitura, e um "
        f"ciclo de importação voltou a ser possível — {culpados}"
    )


def test_so_a_view_do_canal_conhece_a_exportacao():
    """A exceção é **uma**, e ela é a porta da Fase 7.

    Se um segundo módulo da interface passar a importar a exportação, é sinal de que a capacidade
    ganhou uma segunda porta — e duas portas divergem na primeira mudança.
    """
    portas = sorted(
        str(caminho.relative_to(RAIZ))
        for caminho in modulos(CANAL)
        if any("matriculas" in nome for nome in importados(caminho))
    )
    assert portas == ["interface/views.py"], portas


def test_matriculas_nao_chama_o_sistema_academico():
    """`FR-450`, `T035d`: o arquivo é entregue a uma pessoa, e não a uma interface programática."""
    achados = {
        str(caminho.relative_to(RAIZ)): sorted(
            nome
            for nome in importados(caminho)
            if any(nome == alvo or nome.startswith(f"{alvo}.") for alvo in DA_REDE)
        )
        for caminho in modulos("matriculas")
    }
    culpados = {arquivo: nomes for arquivo, nomes in achados.items() if nomes}
    assert culpados == {}, (
        f"`matriculas` passou a alcançar a rede: a `FR-450` proíbe chamar o sistema acadêmico por "
        f"interface programática — {culpados}"
    )
