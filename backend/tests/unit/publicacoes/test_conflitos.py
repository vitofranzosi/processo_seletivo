from processo_seletivo.publicacoes.domain.conflicts import (
    HASH_MISMATCH,
    TARGET_PRESENT,
    content_conflicts,
    previous_hash,
    requires_content_check,
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
    assert previous_hash(BASE, "/profiles/0/code") == ""


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


def test_content_check_is_required_only_when_some_precondition_exists():
    assert requires_content_check([replace("/title")]) is False
    assert requires_content_check([{"targetPath": "/title", "operation": "REMOVE"}]) is False
    assert requires_content_check([replace("/title", canonical_sha256("Original"))]) is True
    assert requires_content_check([add("/novo")]) is True
    assert requires_content_check([replace("/title"), add("/novo")]) is True
