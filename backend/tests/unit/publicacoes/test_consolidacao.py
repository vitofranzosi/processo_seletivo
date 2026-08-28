from processo_seletivo.publicacoes.domain.changes import apply_changes
from processo_seletivo.publicacoes.domain.consolidation import consolidate


def test_changes_add_replace_and_remove_without_mutating_base():
    base = {"title": "Original", "rules": {"a": 1, "b": 2}}
    result, provenance = apply_changes(
        base,
        [
            {"targetPath": "/title", "operation": "REPLACE", "newValue": "Novo"},
            {"targetPath": "/rules/c", "operation": "ADD", "newValue": 3},
            {"targetPath": "/rules/a", "operation": "REMOVE"},
        ],
        publication_id="p1",
    )
    assert base["title"] == "Original"
    assert result == {"title": "Novo", "rules": {"b": 2, "c": 3}}
    assert provenance["/title"] == "p1"


def test_same_effective_time_accumulates_and_later_publication_wins_conflict():
    acts = [
        {
            "effectiveAt": "2026-09-10T12:00:00+00:00",
            "publicationOrder": 2,
            "publicationId": "p2",
            "changes": [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Segundo"}],
        },
        {
            "effectiveAt": "2026-09-10T12:00:00+00:00",
            "publicationOrder": 1,
            "publicationId": "p1",
            "changes": [
                {"targetPath": "/title", "operation": "REPLACE", "newValue": "Primeiro"},
                {"targetPath": "/extra", "operation": "ADD", "newValue": True},
            ],
        },
    ]
    content, provenance = consolidate({"title": "Original"}, acts)
    assert content == {"title": "Segundo", "extra": True}
    assert provenance["/title"] == "p2"
    assert provenance["/extra"] == "p1"
