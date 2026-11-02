"""A manchete da lista fechada (111, FR-3427, EC-14, D-013).

Só quando nenhum título oficial cabe; derivada da ficha; filtrada pelo vocabulário (FR-3414); sem
texto livre. A escolha chega como índice, e índice fora da lista é recusado (a view responde 422).
"""

import pytest

from processo_seletivo.interface import kit_peca
from processo_seletivo.interface.kit_peca import MancheteInvalida
from tests.unit.kit import geometria
from tests.unit.kit.test_peca import _titulo
from tests.unit.kit.test_textos import QUATRO_POLOS, _ficha, _oferta

LONGO = _titulo(400)


def _sem_titulo(**mudar):
    return _ficha(titulo_sem_numero=LONGO, titulo_do_processo=LONGO, **mudar)


def test_com_titulo_oficial_que_cabe_nao_ha_manchete():
    ficha = _ficha()
    assert kit_peca.manchetes(ficha) == ()
    with pytest.raises(MancheteInvalida):
        kit_peca.compor(ficha, manchete=0)


def test_nome_comum_quando_todas_tem_o_mesmo_nome():
    assert kit_peca.manchetes(_sem_titulo()) == ("Especialização em Informática na Educação",)


def test_nome_de_cada_opcao_ate_quatro():
    ofertas = (
        _oferta("1", "Técnico em Administração", "Serra", 30),
        _oferta("2", "Técnico em Informática", "Serra", 30),
    )
    lista = kit_peca.manchetes(_sem_titulo(ofertas=ofertas, nomes_iguais=False))
    assert lista == ("Técnico em Administração", "Técnico em Informática")


def test_nome_e_localidade_da_opcao_unica():
    lista = kit_peca.manchetes(_sem_titulo(ofertas=QUATRO_POLOS[:1], total_de_vagas=40))
    assert lista == (
        "Especialização em Informática na Educação",
        "Especialização em Informática na Educação — Polo Bom Jesus do Norte",
    )


def test_acima_de_quatro_so_o_nome_comum():
    cinco = tuple(_oferta(str(i), "Curso", f"Polo {i}", 10) for i in range(5))
    assert kit_peca.manchetes(_sem_titulo(ofertas=cinco)) == ("Curso",)
    distintas = tuple(_oferta(str(i), f"Curso {i}", "", 10) for i in range(5))
    assert kit_peca.manchetes(_sem_titulo(ofertas=distintas, nomes_iguais=False)) == ()


def test_filtrada_pelo_vocabulario():
    ofertas = (
        _oferta("1", "Vagas garantidas em Administração", "Serra", 30),
        _oferta("2", "Técnico em Informática", "Serra", 30),
    )
    lista = kit_peca.manchetes(_sem_titulo(ofertas=ofertas, nomes_iguais=False))
    assert lista == ("Técnico em Informática",)


def test_so_as_que_cabem():
    ofertas = (_oferta("1", LONGO, "Serra", 30), _oferta("2", "Técnico", "Serra", 30))
    assert kit_peca.manchetes(_sem_titulo(ofertas=ofertas, nomes_iguais=False)) == ("Técnico",)


def test_escolhida_vai_so_para_a_peca():
    ficha = _sem_titulo()
    peca = kit_peca.compor(ficha, manchete=0)
    assert geometria.problemas(peca) == []
    assert peca.titulo == "manchete"
    assert peca.manchete == "Especialização em Informática na Educação"
    assert peca.omissao == ""
    assert "Especialização em Informática na Educação" in peca.alternativo


def test_sem_escolha_a_peca_sai_sem_titulo_e_diz():
    peca = kit_peca.compor(_sem_titulo())
    assert peca.titulo == ""
    assert peca.omissao == kit_peca.ESCOLHA_A_MANCHETE


@pytest.mark.parametrize("indice", [-1, 1, 99])
def test_indice_fora_da_lista(indice):
    with pytest.raises(MancheteInvalida):
        kit_peca.compor(_sem_titulo(), manchete=indice)
