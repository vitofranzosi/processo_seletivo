from processo_seletivo.publicacoes.domain.conflicts import conflicting_paths, previous_hash
from processo_seletivo.shared.canonical import canonical_sha256

BASE = {"title": "Original", "rules": {"a": 1}, "profiles": [{"code": "P1"}]}


def test_previous_hash_uses_the_canonical_value_at_the_path():
    assert previous_hash(BASE, "/title") == canonical_sha256("Original")
    assert previous_hash(BASE, "/rules") == canonical_sha256({"a": 1})
    assert previous_hash(BASE, "/rules/a") == canonical_sha256(1)


def test_previous_hash_of_absent_path_is_empty():
    assert previous_hash(BASE, "/inexistente") == ""
    assert previous_hash(BASE, "/rules/b") == ""
    assert previous_hash(BASE, "/profiles/0/code") == ""


def test_matching_expected_hash_does_not_conflict():
    changes = [
        {
            "targetPath": "/title",
            "operation": "REPLACE",
            "newValue": "Novo",
            "expectedPreviousHash": canonical_sha256("Original"),
        }
    ]
    assert conflicting_paths(BASE, changes) == []


def test_stale_expected_hash_conflicts():
    changes = [
        {
            "targetPath": "/title",
            "operation": "REPLACE",
            "newValue": "Novo",
            "expectedPreviousHash": canonical_sha256("Outro conteúdo"),
        },
        {
            "targetPath": "/rules/a",
            "operation": "REPLACE",
            "newValue": 2,
            "expectedPreviousHash": canonical_sha256(1),
        },
    ]
    assert conflicting_paths(BASE, changes) == ["/title"]


def test_declared_previous_content_of_a_removed_path_conflicts():
    changes = [
        {
            "targetPath": "/rules/a",
            "operation": "REPLACE",
            "newValue": 2,
            "expectedPreviousHash": canonical_sha256(1),
        }
    ]
    assert conflicting_paths({"rules": {}}, changes) == ["/rules/a"]


def test_change_without_expected_hash_is_not_verified():
    changes = [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Novo"}]
    assert conflicting_paths(BASE, changes) == []
    assert conflicting_paths(BASE, [{**changes[0], "expectedPreviousHash": ""}]) == []
