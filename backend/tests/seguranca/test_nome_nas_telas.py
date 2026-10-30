"""O nome da pessoa nas telas que mostram quem praticou um ato (107, US9, `FR-3150`, `FR-3151`)."""

import pytest
from django.template import Context, Template
from django.test import RequestFactory

from tests.seguranca.apoio import pessoa

pytestmark = pytest.mark.django_db

MODELO = Template(
    "{% load interface_extras %}{% for s in autores %}[{% nome_de_pessoa s %}]{% endfor %}"
)


def _renderizar(autores):
    request = RequestFactory().get("/gestao/")
    return MODELO.render(Context({"autores": autores, "request": request}))


def test_a_demonstracao_volta_como_veio_e_sem_consulta(django_assert_num_queries):
    with django_assert_num_queries(0):
        assert (
            _renderizar(["gustavo.gestor", "implantacao", "", None])
            == "[gustavo.gestor][implantacao][][]"
        )


def test_a_pessoa_institucional_aparece_pelo_nome_numa_consulta_por_pagina(
    django_assert_num_queries,
):
    ana = pessoa("ana", nome="Ana Souza")
    bea = pessoa("bea", email="bea@ifes.edu.br")
    sem_nada = pessoa("cid")

    with django_assert_num_queries(1):
        saida = _renderizar([ana.username, bea.username, ana.username, sem_nada.username])

    assert saida == "[Ana Souza][bea@ifes.edu.br][Ana Souza][pessoa sem nome informado]"


def test_nenhum_template_mostra_o_autor_sem_a_tag():
    """A varredura das telas: autor de ato exibido cru, depois da 107, é regressão.

    Lê os templates sem os comentários, e procura `{{ … }}` cujo último nome seja de autor — os
    campos `*_por`, `created_by`, `homologated_by`, `prepared_by`, `published_by`,
    `identity_subject`, `actor_subject` e `.ator`. As exceções são as que **precisam** do
    identificador: o valor de um filtro, o identificador digitado que a confirmação mostra como será
    gravado, a escolha do seletor de demonstração e as chaves de rascunho do próprio ator.
    """
    import re
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[2] / "processo_seletivo/interface/templates/interface"
    autor = re.compile(
        r"\{\{\s*[\w.]*\.(?:\w+_por|created_by|homologated_by|prepared_by|published_by|"
        r"identity_subject|actor_subject|ator)\s*(?:\|[^}]*)?\}\}"
    )
    excecoes = {"comissao_confirmar.html", "identificar_demonstracao.html", "impedimentos.html"}
    crus = []
    for modelo in sorted(raiz.glob("*.html")):
        if modelo.name in excecoes:
            continue
        texto = re.sub(
            r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", "", modelo.read_text(), flags=re.S
        )
        for achado in autor.finditer(texto):
            antes = texto[max(0, achado.start() - 40) : achado.start()]
            if re.search(r'(?:value|data-[\w-]+|href|name|id)="[^"]*$', antes):
                continue
            crus.append(f"{modelo.name}: {achado.group(0)}")
    assert crus == []
