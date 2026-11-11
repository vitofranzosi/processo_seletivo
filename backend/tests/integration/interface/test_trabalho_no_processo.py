"""O recorte da faixa da 104 ao Processo (147, FR-5309).

As Etapas da avaliadora em outros Processos custavam a leitura das Etapas vigentes de cada Edital
alocado, e a página do Processo as pagava para depois descartá-las. O recorte vai **na consulta**.
"""

import pytest

from processo_seletivo.comissoes.application import selectors
from processo_seletivo.interface import trabalho
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em, constituir

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_minhas_etapas_recorta_ao_processo_na_consulta(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, edital_b, etapa_b1
):
    processo_b = edital_b.processo
    joao_em_b = constituir(
        gestor, processo_b, [("paula", "PRESIDENTE"), ("joao", "MEMBRO")], prefixo="recorte"
    )["joao"]
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    alocar_em(gestor, processo_b, joao_em_b, edital_b, etapa_b1)
    joao = ator_institucional("joao")

    assert {item["edital"].id for item in selectors.minhas_etapas(joao)} == {
        edital_a.id,
        edital_b.id,
    }
    assert [item["edital"].id for item in selectors.minhas_etapas(joao, processo=processo_a)] == [
        edital_a.id
    ]


def test_a_faixa_passa_o_processo_as_avaliacoes(monkeypatch, processo_a):
    vistos = []
    monkeypatch.setattr(
        trabalho.comissao_selectors,
        "minhas_etapas",
        lambda ator, processo=None: vistos.append(processo) or [],
    )
    ator = ator_institucional("joao")

    trabalho.do_ator(ator, [], em_curso={}, processo=processo_a)
    trabalho.do_ator(ator, [], em_curso={})

    # A página do Processo recorta; a Lista não passa o argumento e continua somando tudo.
    assert vistos == [processo_a, None]
