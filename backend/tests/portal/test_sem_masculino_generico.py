"""O portal não presume o gênero de quem lê a própria convocação (revisão de 2026-11-13).

O título da chamada dizia *"Você foi convocado!"*, a página da seleção *"Se for convocado"*, o
Requerimento *"quando você for convocado"*. O sistema não sabe o gênero da pessoa, e nenhuma dessas
frases precisa dele: *"Você tem uma convocação!"*, *"A convocação, se houver, pedirá também"*.

**Lista literal, como a varredura de vocabulário**: as telas do portal e os módulos cujo texto chega
ao portal. Uma tela nova entra sozinha, pela pasta; um módulo novo, não — a revisão o acrescenta.

**Só o singular, que fala com quem lê.** "Publicação de convocados" é o nome do ato público da
`149`, como "relação de habilitados" é o de outro ato, e o nome dos atos oficiais fica registrado
na auditoria dos e-mails (achado 9), e não decidido aqui.
"""

import ast
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo"
TELAS = sorted((RAIZ / "portal/templates/portal").glob("*.html"))
MODULOS = (
    "portal/obrigacoes.py",
    "requerimentos/application/preencher.py",
    "requerimentos/application/selectors.py",
    "duvidas/domain/respostas.py",
)
MASCULINO = re.compile(r"\bconvocado\b", re.I)
_COMENTARIO = re.compile(r"\{% comment %\}.*?\{% endcomment %\}|\{#.*?#\}", re.S)
_MARCACAO = re.compile(r"\{\{.*?\}\}|\{%.*?%\}|<[^>]*>", re.S)


def _visivel(caminho):
    return _MARCACAO.sub(" ", _COMENTARIO.sub(" ", caminho.read_text(encoding="utf-8")))


def _textos_que_saem(caminho):
    """As constantes de texto do módulo que não são docstring: o que pode chegar à tela."""
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    docstrings = {
        id(no.body[0].value)
        for no in ast.walk(arvore)
        if isinstance(no, ast.Module | ast.FunctionDef | ast.ClassDef)
        and no.body
        and isinstance(no.body[0], ast.Expr)
        and isinstance(no.body[0].value, ast.Constant)
    }
    return [
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant) and isinstance(no.value, str) and id(no) not in docstrings
    ]


@pytest.mark.parametrize("tela", TELAS, ids=lambda caminho: caminho.name)
def test_nenhuma_tela_do_portal_diz_convocado(tela):
    assert MASCULINO.findall(_visivel(tela)) == []


@pytest.mark.parametrize("modulo", MODULOS)
def test_nenhum_texto_que_chega_ao_portal_diz_convocado(modulo):
    assert [texto for texto in _textos_que_saem(RAIZ / modulo) if MASCULINO.search(texto)] == []


def test_a_varredura_encontra_as_telas():
    assert len(TELAS) > 20
