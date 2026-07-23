"""Fixture projects for qualification scenarios."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
import pytest


def build_minimal_project(root: Path, **overrides: Any) -> Path:
    """Create a minimal Auteur project with deterministic state.

    Creates project skeleton with .auteur marker, story identity,
    blueprint, chapter outline, and convergence state.
    """
    (root / ".auteur").mkdir(parents=True, exist_ok=True)

    # Story identity
    identity = {
        "story_type": {"genre": overrides.get("genre", "mystery"), "mode": "dramatic", "medium": "novel"},
        "title": overrides.get("title", "Test Story"),
    }
    (root / "story_identity.yaml").write_text(yaml.safe_dump(identity))

    # Blueprint
    blueprint = {
        "chapters": {
            "chapter_01": {"purpose": "Establish mystery"},
            "chapter_03": {"purpose": "Climax and reveal"},
        },
    }
    (root / "blueprint.yaml").write_text(yaml.safe_dump(blueprint))

    # Chapter 1 outline
    ch1 = root / "chapters" / "1"
    ch1.mkdir(parents=True)
    outline = {"scenes": [{"id": "scene_01_01", "purpose": "Detective arrives"}, {"id": "scene_01_02", "purpose": "First clue"}]}
    (ch1 / "outline.yaml").write_text(yaml.safe_dump(outline))

    # Chapter 1 scene
    (ch1 / "scenes").mkdir()
    scene = {"id": "scene_01_01", "purpose": "Detective arrives at the mansion", "location": "mansion", "beats": [{"id": "B01", "description": "Enter"}]}
    (ch1 / "scenes" / "scene_01_01.yaml").write_text(yaml.safe_dump(scene))

    # Reasoning review (used by staleness scenarios)
    reasoning_dir = root / "chapters" / "01" / "reasoning"
    reasoning_dir.mkdir(parents=True, exist_ok=True)

    if overrides.get("with_reasoning"):
        run_id = "run_qualification_test"
        review = {
            "review_id": f"reasoning_review_{run_id}",
            "run_id": run_id,
            "candidate_id": overrides.get("candidate_id", "cand-001"),
            "chapter_index": 1,
            "critic_summaries": [
                {"critic_id": "structure", "status": "success", "version": 1},
                {"critic_id": "dialogue", "status": "success", "version": 1},
            ],
            "blocking_findings": [],
            "warnings": [],
            "synthesis": "All critics passed. Candidate is structurally sound.",
            "freshness": "fresh",
            "source_snapshot": {"draft_hash": overrides.get("draft_hash", "abc123"), "outline_hash": overrides.get("outline_hash", "def456")},
        }
        (reasoning_dir / "reviews").mkdir(parents=True, exist_ok=True)
        (reasoning_dir / "reviews" / f"reasoning_review_{run_id}.yaml").write_text(yaml.safe_dump(review))
        (reasoning_dir / "latest.yaml").write_text(yaml.safe_dump({"run_id": run_id, "review_ref": f"reasoning_review_{run_id}", "chapter_index": 1, "iteration": 1}))

    # Convergence state directories
    conv_dir = root / ".auteur" / "convergence"
    conv_dir.mkdir(parents=True, exist_ok=True)
    (conv_dir / "targets").mkdir(exist_ok=True)
    (conv_dir / "candidates").mkdir(exist_ok=True)

    if overrides.get("with_target"):
        target = {
            "target_id": overrides.get("target_id", "target-001"),
            "project": str(root),
            "scope": "scene",
            "chapter_index": 1,
            "scene_id": "scene_01_01",
            "affected_artifact": overrides.get("affected_artifact", "artifact-001"),
            "target_version": 1,
        }
        (conv_dir / "targets" / f"{target['target_id']}.yaml").write_text(yaml.safe_dump(target))

    if overrides.get("with_candidate"):
        cand = {
            "candidate_id": overrides.get("candidate_id", "cand-001"),
            "target_id": overrides.get("target_id", "target-001"),
            "status": overrides.get("candidate_status", "draft"),
            "freshness": overrides.get("candidate_freshness", "fresh"),
            "obligations_satisfied": overrides.get("ob_satisfied", ["ob-001"]),
            "obligations_unsatisfied": overrides.get("ob_unsatisfied", []),
            "evaluation_references": overrides.get("eval_refs", []),
            "preserved_regions": [],
        }
        (root / ".auteur" / "convergence" / "candidates").mkdir(parents=True, exist_ok=True)
        (root / ".auteur" / "convergence" / "candidates" / f"{cand['candidate_id']}.yaml").write_text(yaml.safe_dump(cand))

    if overrides.get("with_multiple_candidates"):
        for i in range(2, 5):
            cand_b = {
                "candidate_id": f"cand-00{i}",
                "target_id": overrides.get("target_id", "target-001"),
                "status": "evaluated",
                "freshness": "fresh",
                "obligations_satisfied": ["ob-001", "ob-002"],
                "obligations_unsatisfied": [],
                "evaluation_references": [f"ev-00{i}"],
                "preserved_regions": [],
            }
            (root / ".auteur" / "convergence" / "candidates" / f"{cand_b['candidate_id']}.yaml").write_text(yaml.safe_dump(cand_b))

    return root


@pytest.fixture
def empty_project(tmp_path: Path) -> Path:
    """A project with no decisions or convergence state."""
    return build_minimal_project(tmp_path)


@pytest.fixture
def project_with_impact(tmp_path: Path) -> Path:
    """A project with impact-driven decisions."""
    return build_minimal_project(tmp_path, with_target=True)


@pytest.fixture
def project_with_candidate(tmp_path: Path) -> Path:
    """A project with a candidate but no evaluation."""
    return build_minimal_project(tmp_path, with_target=True, with_candidate=True, candidate_status="draft", eval_refs=[])


@pytest.fixture
def project_with_evaluated_candidate(tmp_path: Path) -> Path:
    """A project with evaluated candidate and reasoning."""
    return build_minimal_project(
        tmp_path,
        with_target=True,
        with_candidate=True,
        candidate_status="evaluated",
        eval_refs=["ev-001"],
        with_reasoning=True,
    )


@pytest.fixture
def project_multiple_candidates(tmp_path: Path) -> Path:
    """A project with multiple candidates needing comparison."""
    return build_minimal_project(
        tmp_path,
        with_target=True,
        with_candidate=True,
        with_multiple_candidates=True,
        candidate_status="evaluated",
        eval_refs=["ev-001"],
        with_reasoning=True,
    )


@pytest.fixture
def project_stale_reasoning(tmp_path: Path) -> Path:
    """A project where reasoning is stale (source hashes mismatch)."""
    return build_minimal_project(
        tmp_path,
        with_target=True,
        with_candidate=True,
        candidate_status="stale",
        candidate_freshness="stale",
        eval_refs=["ev-001"],
        with_reasoning=True,
        draft_hash="old_hash",
    )


@pytest.fixture
def project_acceptance_ready(tmp_path: Path) -> Path:
    """A project where a candidate is ready for acceptance."""
    return build_minimal_project(
        tmp_path,
        with_target=True,
        with_candidate=True,
        candidate_status="evaluated",
        eval_refs=["ev-001"],
        with_reasoning=True,
        ob_unsatisfied=[],
    )
