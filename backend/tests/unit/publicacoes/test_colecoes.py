"""O guarda de FR-012: quais coleções têm chave é declarado, e a declaração é verificada.

Detectar por introspecção — "o elemento é dict e tem `id`" — acerta hoje e erra em silêncio no
dia em que uma coleção nova nascer sem identificador. Estes testes existem para que esse dia
seja uma falha de suíte.
"""

from processo_seletivo.publicacoes.domain import colecoes
from tests.fixtures.snapshot import (
    PERFIL,
    colecoes_nao_declaradas,
    conteudo_normativo,
    elementos_sem_chave,
)


def test_every_collection_in_the_snapshot_is_declared():
    """Lista não declarada é coleção que ninguém decidiu se tem chave — e isso precisa doer."""
    assert colecoes_nao_declaradas(conteudo_normativo()) == []


def test_every_element_of_a_keyed_collection_carries_its_key():
    assert elementos_sem_chave(conteudo_normativo()) == []


def test_an_undeclared_collection_is_reported():
    """O guarda serve para alguma coisa: uma coleção nova aparece nele."""
    conteudo = conteudo_normativo()
    conteudo["annexes"] = [{"id": PERFIL["A"], "title": "Anexo I"}]
    assert colecoes_nao_declaradas(conteudo) == ["/annexes"]


def test_a_keyed_collection_missing_an_identifier_is_reported():
    conteudo = conteudo_normativo()
    del conteudo["profiles"][1]["id"]
    assert elementos_sem_chave(conteudo) == ["/profiles"]


def test_requirements_is_the_only_collection_without_a_key():
    assert colecoes.COLECOES_ATOMICAS == frozenset({"/profiles/*/requirements"})


def test_nested_collections_are_declared_by_shape_and_not_by_profile():
    """A regra vale para as Modalidades de qualquer Perfil, e não de um Perfil em particular."""
    assert colecoes.tem_chave("/profiles/*/competitionModalities")
    assert not colecoes.tem_chave(f"/profiles/id={PERFIL['A']}/competitionModalities")


def test_normative_rule_is_an_object_and_not_a_collection():
    """Ter `id` não faz de `normativeRule` item de lista: ela continua sendo nome de chave."""
    formas = {forma for forma, _ in colecoes.colecoes_com_chave(conteudo_normativo())}
    assert "/profiles/*/competitionModalities/*/normativeRule" not in formas


def test_control_lists_are_named_and_not_guessed():
    assert colecoes.e_controle_interno("applied_publications")
    assert not colecoes.e_controle_interno("profiles")


def test_the_shape_escapes_keys_so_a_slash_in_a_name_cannot_forge_a_collection():
    assert colecoes.escapar("a/b") == "a~1b"
    assert colecoes.escapar("a~b") == "a~0b"
