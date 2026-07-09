from __future__ import annotations

from auteur.relations.diagnostics import diagnose_relation_changes, diagnose_relation_map
from auteur.relations.graph import build_relation_graph
from auteur.relations.models import RelationChange, RelationChangeSet, RelationMap, RelationState


def _map() -> RelationMap:
    return RelationMap(
        relations=[
            RelationState(
                id="elena_marcus",
                from_character="Elena",
                to_character="Marcus",
                trust=20,
                resentment=70,
                dependency=40,
                attraction=10,
                fear=30,
                obligation=50,
            )
        ]
    )


def test_large_unexplained_metric_jump_is_diagnostic() -> None:
    changes = RelationChangeSet(
        chapter=3,
        relation_changes=[RelationChange(relation="elena_marcus", trust=45, reason="")],
    )

    diagnostics = diagnose_relation_changes(_map(), changes)

    assert [d.rule for d in diagnostics] == ["relations.metric_jump_unexplained"]
    assert diagnostics[0].severity == "warning"


def test_explained_metric_jump_does_not_emit_jump_warning() -> None:
    changes = RelationChangeSet(
        chapter=3,
        relation_changes=[
            RelationChange(
                relation="elena_marcus",
                trust=45,
                reason="Marcus risks public punishment to protect Elena.",
            )
        ],
    )

    assert diagnose_relation_changes(_map(), changes) == []


def test_unknown_relation_change_target_is_error() -> None:
    changes = RelationChangeSet(
        chapter=3,
        relation_changes=[RelationChange(relation="unknown_pair", trust=5, reason="A scene.")],
    )

    diagnostics = diagnose_relation_changes(_map(), changes)

    assert diagnostics[0].rule == "relations.unknown_relation"
    assert diagnostics[0].severity == "error"


def test_empty_private_truth_for_high_intensity_relation_is_hint() -> None:
    relation_map = RelationMap(
        relations=[
            RelationState(
                id="elena_marcus",
                from_character="Elena",
                to_character="Marcus",
                trust=90,
                obligation=90,
            )
        ]
    )

    diagnostics = diagnose_relation_map(relation_map)

    assert [d.rule for d in diagnostics] == ["relations.private_truth_missing"]


def test_relation_graph_is_deterministic() -> None:
    changes = [
        RelationChangeSet(
            chapter=3,
            relation_changes=[RelationChange(relation="elena_marcus", trust=8, reason="A scene.")],
        )
    ]

    graph = build_relation_graph(_map(), changes)

    assert graph["nodes"][0] == {"id": "character:Elena", "type": "character", "label": "Elena"}
    assert graph["edges"][0]["source"] == "character:Elena"
    assert graph["edges"][0]["target"] == "relation:elena_marcus"
    assert graph["changed_by_chapter"] == {"chapter_03": ["elena_marcus"]}

