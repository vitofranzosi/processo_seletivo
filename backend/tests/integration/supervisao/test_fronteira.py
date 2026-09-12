"""A fronteira da `022`: o que ela **não** faz, e o que o custo dela não acompanha.

Metade desta feature é uma lista de proibições, e proibição sem teste é intenção. Estes são os
testes que transformam a fronteira de `D-007` e `FR-006` em algo que quebra quando alguém a
atravessa.
"""

import re
from pathlib import Path

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.interface import supervisao
from tests.conftest import ator_institucional
from tests.fixtures.supervisao import SEGUNDO_SEED, rascunhar, submeter

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

MODULO = Path(supervisao.__file__)
TEMPLATES = Path(supervisao.__file__).parent / "templates" / "interface"


@pytest.fixture
def presidenta():
    return ator_institucional("maria", "recurso:julgar")


def _sem_comentarios(codigo):
    """O código sem docstring nem comentário: a prosa deste módulo **fala** de gravar.

    Um teste que procurasse `save(` no arquivo inteiro acusaria o comentário que explica por que
    não se grava — e a explicação é justamente o que se quer manter.
    """
    sem_docstrings = re.sub(r'(?s)""".*?"""', "", codigo)
    return re.sub(r"(?m)#.*$", "", sem_docstrings)


def test_o_modulo_de_leitura_nao_contem_nenhuma_escrita():
    """`FR-006`: nenhum `save`, `create`, `update` ou `delete` originado nesta feature."""
    codigo = _sem_comentarios(MODULO.read_text())

    for escrita in (
        ".save(",
        ".create(",
        ".update(",
        ".delete(",
        ".bulk_create(",
        ".get_or_create(",
    ):
        assert escrita not in codigo, f"a supervisão só lê, e {escrita} é escrita"


def test_a_leitura_inteira_nao_emite_uma_consulta_de_escrita(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta
):
    """A mesma proibição, verificada no banco em vez de no texto.

    A varredura acima protege contra o que se escreve; esta protege contra o que se chama: um
    selector alheio que gravasse por dentro passaria pela primeira e cairia aqui.
    """
    submeter(edital_c, 3, seed=SEGUNDO_SEED)
    rascunhar(edital_a, 2)

    with CaptureQueriesContext(connection) as consultas:
        supervisao.pulso(processo_a)
        supervisao.sinais(processo_a, presidenta)

    escritas = [
        registro["sql"]
        for registro in consultas.captured_queries
        if not registro["sql"].lstrip().upper().startswith(("SELECT", "SAVEPOINT", "RELEASE"))
    ]
    assert escritas == [], escritas


def test_nenhuma_forma_de_leitura_carrega_identificacao_de_candidato(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta
):
    """`FR-004a`: a página é agregada por construção — contagens e nomes de Edital e de Etapa.

    É esta proibição que sustenta a permissão de `FR-004a`: o Pulso não é suprimido por alcance
    **porque** ele não tem dado pessoal. Se um dia passar a ter, aquela linha cai junto.
    """
    inscricoes = submeter(edital_c, 2, seed=SEGUNDO_SEED)

    lido = repr(supervisao.pulso(processo_a)) + repr(supervisao.sinais(processo_a, presidenta))

    for inscricao in inscricoes:
        assert inscricao.protocolo not in lido
        assert inscricao.nome not in lido
        assert inscricao.cpf not in lido
        assert inscricao.identity_subject not in lido


def test_a_supervisao_nao_apresenta_carga_nem_desempenho_de_membro(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta
):
    """`FR-034`: a operação é de duas ou três pessoas acumulando papéis, e a presidência avalia.

    Uma tabela de produtividade mediria a presidência contra si mesma. A verificação é dupla: as
    formas de leitura não nomeiam pessoa alguma, e os templates não percorrem coleção de membros —
    porque é ali que a coluna apareceria.

    `UX-005` fala de membros da comissão **como conjunto**, e não de um deles: dizer "todos estão
    impedidos" é nomear a condição, e nomear quem seria a carga que este teste proíbe.
    """
    lido = repr(supervisao.pulso(processo_a)) + repr(supervisao.sinais(processo_a, presidenta))

    for membro in comissao_de_a.values():
        assert membro.identity_subject not in lido

    for arquivo in ("supervisao.html", "_sinal.html", "_serie_de_inscricoes.html"):
        marcacao = (TEMPLATES / arquivo).read_text().lower()
        for proibido in ("membro", "avaliador", "produtividade", "desempenho", "carga"):
            assert proibido not in marcacao, f"{arquivo} apresenta {proibido}"


def test_o_custo_da_pagina_cresce_com_o_que_mudou_e_nao_com_o_tamanho_do_processo(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta, django_assert_num_queries
):
    """`T-002` e `T-003`: dobrar as inscrições não muda o número de consultas.

    É o que separa esta página de um painel que envelhece: as contagens são agregações, a série é
    uma agregação por Edital, e a obsolescência só chama o cálculo exato onde o filtro barato
    acusou. Nada aqui é por linha.
    """
    submeter(edital_c, 5, seed=SEGUNDO_SEED)
    with CaptureQueriesContext(connection) as com_cinco:
        supervisao.pulso(processo_a)
        supervisao.sinais(processo_a, presidenta)
    orcamento = len(com_cinco.captured_queries)

    submeter(edital_c, 5, primeiro=500, seed=SEGUNDO_SEED)

    with django_assert_num_queries(orcamento):
        supervisao.pulso(processo_a)
        supervisao.sinais(processo_a, presidenta)
