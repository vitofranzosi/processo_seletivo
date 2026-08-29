from processo_seletivo.publicacoes.domain.conflicts import (
    ANCHOR_MISMATCH,
    HASH_MISMATCH,
    TARGET_PRESENT,
    content_conflicts,
    derive_preconditions,
    path_anchors,
    previous_hash,
)
from processo_seletivo.shared.canonical import canonical_sha256

BASE = {"title": "Original", "rules": {"a": 1}, "profiles": [{"code": "P1"}]}


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
    # Índice fora da lista e posição de acréscimo não existem: nada há para sobrescrever.
    assert previous_hash(BASE, "/profiles/9") == ""
    assert previous_hash(BASE, "/profiles/-") == ""
    assert previous_hash(BASE, "/profiles/0/inexistente") == ""


def test_previous_hash_reaches_content_inside_lists():
    """A precondição vale dentro de listas; sem isso, Perfil e Evento ficariam sem proteção."""
    assert previous_hash(BASE, "/profiles/0/code") == canonical_sha256("P1")
    assert previous_hash(BASE, "/profiles/0") == canonical_sha256({"code": "P1"})


def test_add_into_a_list_is_insertion_and_never_a_silent_overwrite():
    """RFC 6902: ADD em lista insere e desloca; só em objeto ele substitui."""
    assert content_conflicts(BASE, [add("/profiles/0")]) == {}
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
        {"id": "id-1", "code": "P1", "name": "A"},
        {"id": "id-2", "code": "P2", "name": "MESMO"},
        {"id": "id-3", "code": "P3", "name": "MESMO"},
    ]
}


def sem_o_primeiro(conteudo):
    return {"profiles": conteudo["profiles"][1:]}


def com_precondicoes(conteudo, changes):
    """As alterações como ficam persistidas: hash e âncoras derivados da base."""
    derivadas = derive_preconditions(conteudo, changes)
    return [
        {
            **change,
            "expectedPreviousHash": precondition["hash"],
            "expectedAnchors": precondition["anchors"],
        }
        for change, precondition in zip(changes, derivadas, strict=True)
    ]


def test_anchors_identify_every_list_index_the_path_crosses():
    assert path_anchors(PERFIS, "/profiles/1/name") == {"/profiles/1": "id:id-2"}
    assert path_anchors(PERFIS, "/profiles/2") == {"/profiles/2": "id:id-3"}
    assert path_anchors(PERFIS, "/profiles/-") == {}
    assert path_anchors(PERFIS, "/profiles/3") == {}


def test_anchor_of_an_element_without_id_falls_back_to_its_content():
    conteudo = {"requisitos": [{"texto": "a"}, {"texto": "b"}]}
    ancoras = path_anchors(conteudo, "/requisitos/1/texto")
    assert ancoras["/requisitos/1"].startswith("hash:")


def test_identical_content_in_a_shifted_list_is_still_caught():
    """O hash da folha não distingue duas entidades de mesmo valor; a âncora distingue."""
    ato = com_precondicoes(
        PERFIS, [{"targetPath": "/profiles/1/name", "operation": "REPLACE", "newValue": "Novo"}]
    )
    # O valor em /profiles/1/name continua "MESMO" depois da remoção — agora é o do P3.
    assert previous_hash(sem_o_primeiro(PERFIS), "/profiles/1/name") == ato[0][
        "expectedPreviousHash"
    ]
    assert content_conflicts(sem_o_primeiro(PERFIS), ato) == {ANCHOR_MISMATCH: ["/profiles/1"]}


def test_positional_add_is_anchored_to_the_element_it_precedes():
    """`ADD` não tem conteúdo anterior, mas tem posição — e posição também desloca."""
    novo = {"id": "id-x", "code": "PX", "name": "X"}
    ato = com_precondicoes(
        PERFIS, [{"targetPath": "/profiles/1", "operation": "ADD", "newValue": novo}]
    )
    assert ato[0]["expectedPreviousHash"] == ""
    assert content_conflicts(PERFIS, ato) == {}
    assert content_conflicts(sem_o_primeiro(PERFIS), ato) == {ANCHOR_MISMATCH: ["/profiles/1"]}


def test_appending_at_the_end_is_stable_and_needs_no_anchor():
    novo = {"id": "id-x", "code": "PX", "name": "X"}
    ato = com_precondicoes(
        PERFIS, [{"targetPath": "/profiles/-", "operation": "ADD", "newValue": novo}]
    )
    assert ato[0]["expectedAnchors"] == {}
    assert content_conflicts(sem_o_primeiro(PERFIS), ato) == {}


def test_an_untouched_path_still_publishes_after_an_unrelated_shift():
    """A âncora não pode transformar o caminho feliz em recusa."""
    ato = com_precondicoes(
        PERFIS, [{"targetPath": "/profiles/2/name", "operation": "REPLACE", "newValue": "Novo"}]
    )
    assert content_conflicts(PERFIS, ato) == {}
