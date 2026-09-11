from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.structure.revision_application import _apply_blueprint_change, apply_revision
from auteur.structure.revision_models import (
    RevisionOperation,
    RevisionOperationType,
    RevisionPrecondition,
    RevisionScope,
)
from auteur.structure.revision_service import RevisionService, StructuralRevisionPlan
from auteur.provenance.store import canonical_content_hash

SAMPLE = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _project(tmp_path: Path) -> Path:
    (tmp_path / ".auteur").mkdir()
    (tmp_path / "blueprint.yaml").write_bytes(SAMPLE.read_bytes())
    return tmp_path


def _plan(project: Path, data: dict) -> StructuralRevisionPlan:
    expected = canonical_content_hash(project / "blueprint.yaml")
    operation = RevisionOperation(
        operation_id="replace_blueprint",
        target_id="blueprint",
        target_type="blueprint",
        operation_type=RevisionOperationType.REPLACE,
        requested_change={"data": data},
    )
    return StructuralRevisionPlan(
        plan_id="plan_fail_closed",
        project=project.name,
        source_ids=["test"],
        target_ids=["blueprint"],
        target_hashes={"blueprint": expected},
        operations=[operation],
        scope=RevisionScope(target_artifact_ids=["blueprint"]),
        preconditions=[
            RevisionPrecondition(
                target_id="blueprint",
                expected_hash=expected,
                actual_hash=expected,
                met=True,
            )
        ],
    )


def test_blueprint_helper_rejects_invalid_replacement_without_write(tmp_path: Path):
    project = _project(tmp_path)
    blueprint = project / "blueprint.yaml"
    before = blueprint.read_bytes()

    with pytest.raises(ValueError, match="Blueprint revision failed validation"):
        _apply_blueprint_change(
            blueprint,
            {"structure": {"estimated_chapters": "not-an-integer"}},
        )

    assert blueprint.read_bytes() == before


def test_apply_revision_records_invalid_blueprint_replacement_as_failure(tmp_path: Path):
    project = _project(tmp_path)
    before = (project / "blueprint.yaml").read_bytes()

    result = apply_revision(
        _plan(project, {"structure": {"estimated_chapters": "invalid"}}),
        project,
        confirmed=True,
    )

    assert result.state != "applied"
    assert len(result.target_results) == 1
    assert result.target_results[0].success is False
    assert "Blueprint revision failed validation" in (result.target_results[0].error or "")
    assert (project / "blueprint.yaml").read_bytes() == before


def test_revision_service_preserves_blueprint_when_replacement_validation_fails(tmp_path: Path):
    project = _project(tmp_path)
    service = RevisionService(project)
    plan = _plan(project, {"structure": {"estimated_chapters": "invalid"}})
    from auteur.structure.revision_service import _save_yaml, _serialise

    _save_yaml(_serialise(plan), service._plan_path(plan.plan_id))
    before = (project / "blueprint.yaml").read_bytes()

    result = service.apply(plan.plan_id, confirmed=True)

    assert result.target_results[0].success is False
    assert service.status(plan.plan_id)["state"] == "partially_applied"
    assert (project / "blueprint.yaml").read_bytes() == before


def test_valid_complete_structure_replacement_still_applies_atomically(tmp_path: Path):
    project = _project(tmp_path)
    blueprint = project / "blueprint.yaml"
    raw = yaml.safe_load(blueprint.read_text(encoding="utf-8"))
    replacement = dict(raw["structure"])
    replacement["estimated_chapters"] = 48
    replacement["subplot_budget"] = 4

    result = apply_revision(
        _plan(project, {"structure": replacement}),
        project,
        confirmed=True,
    )
    saved = yaml.safe_load(blueprint.read_text(encoding="utf-8"))

    assert result.state == "applied"
    assert result.target_results[0].success is True
    assert saved["structure"]["estimated_chapters"] == 48
    assert saved["structure"]["subplot_budget"] == 4


def test_confirmation_gate_still_prevents_any_replacement(tmp_path: Path):
    project = _project(tmp_path)
    before = (project / "blueprint.yaml").read_bytes()

    result = apply_revision(
        _plan(project, {"structure": {"estimated_chapters": "invalid"}}),
        project,
        confirmed=False,
    )

    assert result.state == "failed"
    assert result.target_results == []
    assert (project / "blueprint.yaml").read_bytes() == before
