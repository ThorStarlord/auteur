from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.expression import ExpressionStore
from auteur.expression.boundary_service import ExpressionBoundaryService
from auteur.provenance import ArtifactStore, ReviewState


def _scene(tmp_path: Path) -> tuple[Path, Path]:
    project = tmp_path / "project"
    scene = project / "chapters" / "01" / "scenes" / "scene_01_01.yaml"
    scene.parent.mkdir(parents=True)
    scene.write_text(
        yaml.safe_dump(
            {
                "id": "scene_01_01",
                "chapter_id": "chapter_01",
                "participants": ["mara"],
                "pov_character_id": "mara",
                "location": "archive",
                "goal": "find the ledger",
                "opposition": "the archive is locked",
                "turn": "mara finds the ledger",
                "decision": "hide the ledger",
                "outcome": "mara hides the ledger",
                "knowledge": ["the ledger exists"],
                "emotional_changes": ["fear to resolve"],
                "arc_realizations": ["mara accepts responsibility"],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    ArtifactStore(project).accept(scene, "scene_realization")
    return project, scene


def test_structured_expression_contradiction_blocks_acceptance_without_upstream_mutation(tmp_path: Path):
    project, scene = _scene(tmp_path)
    source_before = scene.read_bytes()
    store = ExpressionStore(project)
    candidate = store.generate(scene, "Mara leaves the ledger visible on the desk.")

    assessed = ExpressionBoundaryService(project).evaluate_candidate(
        candidate.candidate_id,
        {"outcome": {"status": "contradicted"}},
    )

    assert assessed.review_state is ReviewState.REVIEW_REQUIRED
    assert any(
        finding["code"] == "outcome_contradiction" and finding["severity"] == "error"
        for finding in assessed.validation_findings
    )
    assert store.status(candidate.candidate_id)["health"] == "invalid"
    with pytest.raises(ValueError, match="invalid prose candidate"):
        store.accept(candidate.candidate_id)
    assert scene.read_bytes() == source_before


def test_expression_boundary_can_propose_upstream_change_but_never_apply_it(tmp_path: Path):
    project, scene = _scene(tmp_path)
    source_before = scene.read_bytes()
    store = ExpressionStore(project)
    candidate = store.generate(scene, "Mara leaves the ledger visible on the desk.")
    ExpressionBoundaryService(project).evaluate_candidate(
        candidate.candidate_id,
        {"outcome": {"status": "contradicted"}},
    )
    proposal = store.create_upstream_proposal(
        scene,
        problem="The prose contradicts the accepted Scene outcome.",
        suggested_change="Either restore the hiding action in prose or explicitly revise the Scene outcome.",
        evidence="Structured outcome evidence is contradicted.",
        source_candidate_id=candidate.candidate_id,
    )
    assert proposal["target_layer"] == "Realization"
    assert proposal["status"] == "proposed"
    assert scene.read_bytes() == source_before
