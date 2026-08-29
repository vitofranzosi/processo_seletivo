import pytest

from processo_seletivo.publicacoes.domain.changes import (
    CaminhoInexistente,
    EnderecamentoPosicional,
    apply_changes,
)
from processo_seletivo.publicacoes.domain.consolidation import consolidate
from tests.fixtures.snapshot import EVENTO, MODALIDADE, PERFIL

P1, P2 = PERFIL["A"], PERFIL["B"]
E1 = EVENTO["A"]
M1 = MODALIDADE["A"]


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


def snapshot_with_lists():
    return {
        "title": "Edital 01/2026",
        "profiles": [
            {
                "id": P1,
                "code": "P1",
                "immediateVacancies": 1,
                "competitionModalities": [{"id": M1, "code": "AC", "name": "Ampla"}],
            },
            {"id": P2, "code": "P2", "immediateVacancies": 2, "competitionModalities": []},
        ],
        "schedule": [
            {"id": E1, "type": "INSCRICAO", "order": 1},
            {"id": EVENTO["B"], "type": "PROVA", "order": 2},
        ],
    }


def test_retification_replaces_vacancies_inside_profile_list():
    base = snapshot_with_lists()
    caminho = f"/profiles/id={P1}/immediateVacancies"
    result, provenance = apply_changes(
        base,
        [{"targetPath": caminho, "operation": "REPLACE", "newValue": 5}],
        publication_id="p1",
    )
    assert result["profiles"][0]["immediateVacancies"] == 5
    assert result["profiles"][1]["immediateVacancies"] == 2
    assert base["profiles"][0]["immediateVacancies"] == 1
    assert provenance[caminho] == "p1"


def test_retification_reaches_list_nested_inside_list():
    result, _ = apply_changes(
        snapshot_with_lists(),
        [
            {
                "targetPath": f"/profiles/id={P1}/competitionModalities/id={M1}/name",
                "operation": "REPLACE",
                "newValue": "Ampla Concorrência",
            }
        ],
        publication_id="p1",
    )
    assert result["profiles"][0]["competitionModalities"][0]["name"] == "Ampla Concorrência"


def test_retification_only_appends_at_the_end():
    """Inserção em posição saiu da gramática: `-` é a única forma de ADD em lista (FR-006)."""
    novo = {"id": PERFIL["C"], "code": "P9", "immediateVacancies": 0, "competitionModalities": []}
    result, _ = apply_changes(
        snapshot_with_lists(),
        [{"targetPath": "/profiles/-", "operation": "ADD", "newValue": novo}],
        publication_id="p1",
    )
    assert [item["code"] for item in result["profiles"]] == ["P1", "P2", "P9"]


def test_retification_removes_schedule_event_from_list():
    result, _ = apply_changes(
        snapshot_with_lists(),
        [{"targetPath": f"/schedule/id={E1}", "operation": "REMOVE"}],
        publication_id="p1",
    )
    assert [item["type"] for item in result["schedule"]] == ["PROVA"]


def test_changes_apply_sequentially_so_a_later_path_sees_what_an_earlier_one_created():
    novo = {"id": PERFIL["C"], "code": "P0", "immediateVacancies": 9, "competitionModalities": []}
    result, _ = apply_changes(
        snapshot_with_lists(),
        [
            {"targetPath": "/profiles/-", "operation": "ADD", "newValue": novo},
            {
                "targetPath": f"/profiles/id={PERFIL['C']}/immediateVacancies",
                "operation": "REPLACE",
                "newValue": 7,
            },
        ],
        publication_id="p1",
    )
    assert result["profiles"][-1]["immediateVacancies"] == 7


@pytest.mark.parametrize(
    "path",
    [
        "/schedule/01",  # grafia ambígua: não é índice nem seletor
        "/schedule/x",
        "/schedule/-",  # posição de acréscimo não é alvo de REPLACE
        "/schedule/-1",
        "/title/0",  # o contêiner não é lista
    ],
)
def test_invalid_list_paths_are_rejected(path):
    with pytest.raises(CaminhoInexistente, match="Caminho inexistente"):
        apply_changes(
            snapshot_with_lists(),
            [{"targetPath": path, "operation": "REPLACE", "newValue": 1}],
            publication_id="p1",
        )


@pytest.mark.parametrize("path", ["/profiles/2/immediateVacancies", "/profiles/9", "/schedule/0"])
def test_positional_paths_over_keyed_collections_are_refused_and_not_merely_missing(path):
    """Índice fora da lista e índice dentro dela têm a mesma resposta: a forma é que está errada."""
    with pytest.raises(EnderecamentoPosicional):
        apply_changes(
            snapshot_with_lists(),
            [{"targetPath": path, "operation": "REPLACE", "newValue": 1}],
            publication_id="p1",
        )


def test_append_token_is_rejected_for_remove():
    with pytest.raises(ValueError, match="Caminho inexistente"):
        apply_changes(
            snapshot_with_lists(),
            [{"targetPath": "/profiles/-", "operation": "REMOVE"}],
            publication_id="p1",
        )


def test_add_by_the_index_after_the_last_element_is_refused_like_any_other_index():
    """`/schedule/2` já foi acréscimo ao fim; agora só `-` o é, e a ambiguidade some."""
    with pytest.raises(EnderecamentoPosicional):
        apply_changes(
            snapshot_with_lists(),
            [{"targetPath": "/schedule/2", "operation": "ADD", "newValue": {"type": "RESULTADO"}}],
            publication_id="p1",
        )


def test_unknown_operation_is_rejected_before_touching_the_content():
    with pytest.raises(ValueError, match="Operação desconhecida"):
        apply_changes(
            snapshot_with_lists(),
            [
                {
                    "targetPath": f"/profiles/id={P1}/immediateVacancies",
                    "operation": "MOVE",
                    "newValue": 1,
                }
            ],
            publication_id="p1",
        )


def test_future_effective_dates_compose_by_vigencia_not_by_publication_order():
    """FR-039: A publicada antes, com vigência posterior a B, só compõe após a vigência de B."""
    acts = [
        {
            "effectiveAt": "2026-10-20T12:00:00+00:00",
            "publicationOrder": 1,
            "publicationId": "retificacao-A",
            "changes": [
                {
                    "targetPath": f"/profiles/id={P1}/immediateVacancies",
                    "operation": "REPLACE",
                    "newValue": 30,
                }
            ],
        },
        {
            "effectiveAt": "2026-10-10T12:00:00+00:00",
            "publicationOrder": 2,
            "publicationId": "retificacao-B",
            "changes": [
                {
                    "targetPath": f"/profiles/id={P1}/immediateVacancies",
                    "operation": "REPLACE",
                    "newValue": 20,
                },
                {"targetPath": "/title", "operation": "REPLACE", "newValue": "Retificado por B"},
            ],
        },
    ]
    apenas_b = [act for act in acts if act["publicationId"] == "retificacao-B"]
    content, _ = consolidate(snapshot_with_lists(), apenas_b)
    assert content["profiles"][0]["immediateVacancies"] == 20

    content, provenance = consolidate(snapshot_with_lists(), acts)
    assert content["profiles"][0]["immediateVacancies"] == 30
    assert content["title"] == "Retificado por B"
    assert provenance[f"/profiles/id={P1}/immediateVacancies"] == "retificacao-A"
    assert provenance["/title"] == "retificacao-B"
