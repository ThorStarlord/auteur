from __future__ import annotations

from pathlib import Path

import yaml

from auteur.cli import main, parse_args
from auteur.provenance.store import canonical_content_hash
from auteur.structure.revision_models import RevisionPlanState
from auteur.structure.revision_recovery import recover_interrupted_revisions
from auteur.structure.revision_service import StructuralRevisionPlan


def _write_plan(project: Path, *, state: str = "applying") -> tuple[Path, Path]:
    (project / ".auteur" / "structure" / "revision-plans").mkdir(parents=True)
    blueprint = project / "blueprint.yaml"
    blueprint.write_text("structure:\n  estimated_chapters: 30\n", encoding="utf-8")
    plan = StructuralRevisionPlan(
        plan_id="recovery_plan",
        project=project.name,
        target_ids=["blueprint"],
        target_hashes={"blueprint": canonical_content_hash(blueprint)},
        state=RevisionPlanState(state),
    )
    path = project / ".auteur" / "structure" / "revision-plans" / "recovery_plan.yaml"
    path.write_text(yaml.safe_dump(plan.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
    return path, blueprint


def test_recovery_returns_unchanged_interrupted_plan_to_ready(tmp_path: Path):
    plan_path, blueprint = _write_plan(tmp_path)
    before = blueprint.read_bytes()
    recovered = recover_interrupted_revisions(tmp_path)
    assert recovered[0]["recovered_state"] == "ready"
    assert recovered[0]["automatic_replay"] is False
    assert blueprint.read_bytes() == before
    raw = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    assert raw["state"] == "ready"


def test_recovery_fails_closed_when_target_changed_without_application_record(tmp_path: Path):
    plan_path, blueprint = _write_plan(tmp_path)
    blueprint.write_text("structure:\n  estimated_chapters: 99\n", encoding="utf-8")
    changed = blueprint.read_bytes()
    recovered = recover_interrupted_revisions(tmp_path)
    assert recovered[0]["recovered_state"] == "failed"
    assert "automatic replay is forbidden" in recovered[0]["reason"]
    assert blueprint.read_bytes() == changed
    raw = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    assert raw["state"] == "failed"


def test_recovery_cli_is_explicit_and_does_not_replay_authority(tmp_path: Path, capsys):
    _write_plan(tmp_path)
    args = parse_args(["structure", "revision", "recover", "--project", str(tmp_path)])
    assert args.revision_command == "recover"
    assert main(["structure", "revision", "recover", "--project", str(tmp_path), "--json"]) == 0
    output = capsys.readouterr().out
    assert '"recovered_state": "ready"' in output
    assert '"automatic_replay": false' in output
