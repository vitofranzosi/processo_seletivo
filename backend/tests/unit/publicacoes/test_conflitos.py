"""Precondições de conteúdo, agora que o caminho nomeia a entidade.

A `003` guardava aqui, além do hash, uma âncora de identidade por índice atravessado, e boa
parte destes testes era sobre ela: dois Perfis de denominação idêntica tornavam o hash
indistinguível depois de a lista mudar de forma. Com `id=<uuid>` a lista pode mudar de forma à
vontade — o caminho continua achando o mesmo Perfil —, e o que a âncora respondia deixou de ser
pergunta (FR-015). O hash ficou, respondendo a sua (FR-014).
"""

import pytest

from processo_seletivo.publicacoes.domain.changes import EnderecamentoPosicional
from processo_seletivo.publicacoes.domain.conflicts import (
    DUPLICATE_KEY,
    HASH_MISMATCH,
    KEY_NOT_FOUND,
    TARGET_PRESENT,
    content_conflicts,
    derive_preconditions,
    duplicate_keys,
    previous_hash,
)
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.snapshot import PERFIL

P1, P2, P3 = PERFIL["A"], PERFIL["B"], PERFIL["C"]

BASE = {
    "title": "Original",
    "rules": {"a": 1},
    "profiles": [{"id": P1, "code": "P1"}],
}


def replace(path, expected=None):
    change = {"targetPath": path, "operation": "REPLACE", "newValue": "Novo"}
    if expected is not None:
        change["expectedPreviousHash"] = expected
    return change


def add(path, expected=None):
    return {**replace(path, expected), "operation": "ADD"}


def test_previous_hash_uses_the_canonical_value_at_the_path():
    assert previous_hash(BASE, "/title") == canonical_sha256("Original")
    assert previous_hash(BASE, "/rules") == canonical_sha256({"a": 1})
    assert previous_hash(BASE, "/rules/a") == canonical_sha256(1)


def test_previous_hash_of_absent_path_is_empty():
    assert previous_hash(BASE, "/inexistente") == ""
    assert previous_hash(BASE, "/rules/b") == ""
    # Chave que não está na coleção e posição de acréscimo não existem: nada há para sobrescrever.
    assert previous_hash(BASE, f"/profiles/id={P2}") == ""
    assert previous_hash(BASE, "/profiles/-") == ""
    assert previous_hash(BASE, f"/profiles/id={P1}/inexistente") == ""


def test_previous_hash_reaches_content_inside_lists():
    """A precondição vale dentro de listas; sem isso, Perfil e Evento ficariam sem proteção."""
    assert previous_hash(BASE, f"/profiles/id={P1}/code") == canonical_sha256("P1")
    assert previous_hash(BASE, f"/profiles/id={P1}") == canonical_sha256({"id": P1, "code": "P1"})


def test_previous_hash_refuses_a_positional_path_instead_of_answering_it():
    """Ler por posição uma coleção com chave é a pergunta errada, não uma resposta vazia."""
    with pytest.raises(EnderecamentoPosicional):
        previous_hash(BASE, "/profiles/0/code")


def test_add_into_a_list_is_appending_and_never_a_silent_overwrite():
    assert content_conflicts(BASE, [add("/profiles/-")]) == {}
    assert content_conflicts(BASE, [add("/title")]) == {TARGET_PRESENT: ["/title"]}


def test_matching_expected_hash_does_not_conflict():
    assert content_conflicts(BASE, [replace("/title", canonical_sha256("Original"))]) == {}


def test_stale_expected_hash_conflicts():
    changes = [
        replace("/title", canonical_sha256("Outro conteúdo")),
        replace("/rules/a", canonical_sha256(1)),
    ]
    assert content_conflicts(BASE, changes) == {HASH_MISMATCH: ["/title"]}


def test_declared_previous_content_of_a_removed_path_conflicts():
    changes = [replace("/rules/a", canonical_sha256(1))]
    assert content_conflicts({"rules": {}}, changes) == {HASH_MISMATCH: ["/rules/a"]}


def test_replace_without_expected_hash_is_not_verified():
    assert content_conflicts(BASE, [replace("/title")]) == {}
    assert content_conflicts(BASE, [replace("/title", "")]) == {}


def test_add_over_an_occupied_path_conflicts_even_without_expected_hash():
    assert content_conflicts(BASE, [add("/novo")]) == {}
    assert content_conflicts(BASE, [add("/title"), add("/rules/a")]) == {
        TARGET_PRESENT: ["/title", "/rules/a"]
    }


def test_declared_hash_authorizes_an_add_over_an_occupied_path():
    assert content_conflicts(BASE, [add("/title", canonical_sha256("Original"))]) == {}
    assert content_conflicts(BASE, [add("/title", canonical_sha256("Outro"))]) == {
        HASH_MISMATCH: ["/title"]
    }


def test_preconditions_follow_the_content_the_act_itself_produces():
    remove_then_add = [
        {"targetPath": "/rules", "operation": "REMOVE"},
        add("/rules"),
    ]
    assert content_conflicts(BASE, remove_then_add) == {}
    chained = [
        replace("/title", canonical_sha256("Original")),
        replace("/title", canonical_sha256("Novo")),
    ]
    assert content_conflicts(BASE, chained) == {}


def test_precondition_of_a_path_created_by_an_earlier_change_is_verified():
    changes = [add("/anexo"), add("/anexo")]
    assert content_conflicts(BASE, changes) == {TARGET_PRESENT: ["/anexo"]}


PERFIS = {
    "profiles": [
        {"id": P1, "code": "P1", "name": "A"},
        {"id": P2, "code": "P2", "name": "MESMO"},
        {"id": P3, "code": "P3", "name": "MESMO"},
    ]
}


def sem_o_primeiro(conteudo):
    return {"profiles": conteudo["profiles"][1:]}


def com_precondicoes(conteudo, changes):
    """As alterações como ficam persistidas: o hash derivado da base declarada."""
    return [
        {**change, "expectedPreviousHash": hash_}
        for change, hash_ in zip(changes, derive_preconditions(conteudo, changes), strict=True)
    ]


def test_a_shifted_list_no_longer_disturbs_an_untouched_profile():
    """O caso que a `003` só conseguia recusar, e que esta feature deixa publicar.

    P2 e P3 têm a mesma denominação de propósito: era esse par que tornava o hash incapaz de
    distinguir as entidades depois do deslocamento. Com a chave no caminho, remover P1 não move
    o alvo, e o ato sobre P2 continua sendo sobre P2.
    """
    ato = com_precondicoes(
        PERFIS,
        [{"targetPath": f"/profiles/id={P2}/name", "operation": "REPLACE", "newValue": "Novo"}],
    )
    assert content_conflicts(sem_o_primeiro(PERFIS), ato) == {}


def test_a_removed_profile_is_key_not_found_and_not_a_silent_miss():
    ato = com_precondicoes(
        PERFIS,
        [{"targetPath": f"/profiles/id={P1}/name", "operation": "REPLACE", "newValue": "Novo"}],
    )
    assert content_conflicts(sem_o_primeiro(PERFIS), ato) == {
        KEY_NOT_FOUND: [f"/profiles/id={P1}/name"]
    }


def test_two_acts_on_the_same_field_of_the_same_profile_still_collide():
    """A chave diz de quem o ato fala; o hash, se o conteúdo ainda é o que estava à vista."""
    ato = com_precondicoes(
        PERFIS,
        [{"targetPath": f"/profiles/id={P2}/name", "operation": "REPLACE", "newValue": "Novo"}],
    )
    ja_alterado = {
        "profiles": [
            perfil if perfil["id"] != P2 else {**perfil, "name": "Alterado por outra"}
            for perfil in PERFIS["profiles"]
        ]
    }
    assert content_conflicts(ja_alterado, ato) == {HASH_MISMATCH: [f"/profiles/id={P2}/name"]}


def test_appending_at_the_end_is_stable():
    novo = {"id": "00000000-0000-0000-0000-0000000005ff", "code": "PX", "name": "X"}
    ato = com_precondicoes(
        PERFIS, [{"targetPath": "/profiles/-", "operation": "ADD", "newValue": novo}]
    )
    assert ato[0]["expectedPreviousHash"] == ""
    assert content_conflicts(sem_o_primeiro(PERFIS), ato) == {}


def test_duplicate_keys_are_reported_per_collection():
    repetido = {"profiles": [*PERFIS["profiles"], {"id": P2, "code": "P9", "name": "Clone"}]}
    assert duplicate_keys(repetido) == [f"/profiles/id={P2}"]
    assert duplicate_keys(PERFIS) == []


def test_the_same_identifier_in_two_different_collections_is_not_a_duplicate():
    """A resolução é escopada à coleção que o caminho nomeia; unicidade global não é suposta."""
    conteudo = {
        "profiles": [{"id": P1, "code": "P1"}],
        "schedule": [{"id": P1, "type": "INSCRICAO"}],
    }
    assert duplicate_keys(conteudo) == []


def test_an_act_that_would_duplicate_a_key_conflicts():
    clone = {"id": P2, "code": "P9", "name": "Clone"}
    ato = [{"targetPath": "/profiles/-", "operation": "ADD", "newValue": clone}]
    assert content_conflicts(PERFIS, ato) == {DUPLICATE_KEY: [f"/profiles/id={P2}"]}


def test_derivation_stops_at_the_first_inapplicable_change():
    """As seguintes partiriam de um estado que não existe: derivar delas seria inventar."""
    changes = [
        {"targetPath": "/rules/inexistente/x", "operation": "REPLACE", "newValue": 1},
        replace("/title"),
    ]
    assert derive_preconditions(BASE, changes) == ["", ""]


def test_replacing_an_entity_under_the_same_key_is_refused():
    """FR-009: acrescentar com a chave de outro e remover o original é substituição disfarçada.

    A coleção termina íntegra — uma entidade por identificador —, mas no instante do acréscimo a
    chave já existia, e o que foi publicado é a troca de uma entidade por outra sob o mesmo
    identificador. Verificar só o estado final deixava isso passar.
    """
    disfarce = [
        {"targetPath": "/profiles/-", "operation": "ADD", "newValue": {"id": P1, "name": "Outro"}},
        {"targetPath": f"/profiles/id={P1}", "operation": "REMOVE"},
    ]
    assert content_conflicts(PERFIS, disfarce) == {DUPLICATE_KEY: [f"/profiles/id={P1}"]}


def test_removing_and_recreating_under_the_same_key_is_legitimate():
    """A recíproca precisa continuar passando: apagar e recriar é ato declarado, não disfarçado."""
    recriacao = [
        {"targetPath": f"/profiles/id={P1}", "operation": "REMOVE"},
        {"targetPath": "/profiles/-", "operation": "ADD", "newValue": {"id": P1, "name": "Novo"}},
    ]
    assert content_conflicts(PERFIS, recriacao) == {}


def test_a_duplication_already_in_the_base_is_not_charged_to_the_act():
    """O ato encontrou a repetição; não a criou.

    Imputá-la travaria qualquer Retificação sobre a base defeituosa — inclusive a que a corrige.
    """
    ja_repetido = {"profiles": [*PERFIS["profiles"], {"id": P2, "code": "P9", "name": "Clone"}]}
    alheio = [{"targetPath": f"/profiles/id={P3}/name", "operation": "REPLACE", "newValue": "X"}]
    assert content_conflicts(ja_repetido, alheio) == {}
    corrigir = [{"targetPath": f"/profiles/id={P2}", "operation": "REMOVE"}]
    assert content_conflicts(ja_repetido, corrigir) == {}


def test_a_key_that_is_not_text_never_breaks_the_uniqueness_check():
    """`id` de lista ou objeto quebrava o conjunto com TypeError — 500 onde cabia recusa."""
    assert duplicate_keys({"profiles": [{"id": ["x"]}, {"id": ["x"]}, {"id": {"a": 1}}]}) == []
    assert duplicate_keys({"profiles": [{"id": P1}, {"id": P1}, {"id": ["x"]}]}) == [
        f"/profiles/id={P1}"
    ]
