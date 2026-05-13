"""End-to-end CLI fixture test for the structure workflow.

Exercises the full sequence:
  auteur structure propose-repairs  →  author selects  →  auteur structure apply

Also covers the `auteur audit --accept` path (stamps decision, does not mutate
blueprint).

RED: These tests will fail if the full workflow has integration gaps not caught
by unit tests.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from auteur.cli import main


# ---------------------------------------------------------------------------
# Shared test blueprint content — minimal blueprint with a missing story_engine
# so that propose-repairs emits exactly one proposal.
# ---------------------------------------------------------------------------

_MINIMAL_BLUEPRINT_YAML = """\
identity:
  title: "Fixture Story"
  author_intent: "A wandering knight seeks absolution after betraying her order."
  length_class: novel
  genre: literary
  mode: tragic
  target_audience: adult
  pov_type: third_person_limited_single
contract:
  content_rating: R
  mandatory_ending_tone: bittersweet
emotional_design:
  overall_emotional_arc: "guilt -> confrontation -> partial absolution"
theme:
  central_question: "Can a person be forgiven for a cowardly act they cannot undo?"
  thesis: "Redemption is possible only when the self-lie is dismantled."
  motifs: ["silence", "uniforms", "maps"]
"""


# ---------------------------------------------------------------------------
# Fixture: propose-repairs → author selects → apply
# ---------------------------------------------------------------------------


def test_end_to_end_propose_repairs_then_apply(tmp_path: Path, capsys) -> None:
    """Full structure workflow: propose-repairs writes a proposal with a diagnostic,
    author sets selected_option_id, apply merges data into a new blueprint file."""
    # 1. Write blueprint to disk
    blueprint_path = tmp_path / "blueprint.yaml"
    blueprint_path.write_text(_MINIMAL_BLUEPRINT_YAML, encoding="utf-8")

    # 2. Run propose-repairs
    rc = main(["structure", "propose-repairs", str(blueprint_path)])
    assert rc == 0, "propose-repairs should exit 0"
    propose_output = json.loads(capsys.readouterr().out)
    assert propose_output["diagnostic_count"] >= 1
    assert propose_output["proposal_count"] >= 1

    # 3. Read proposal YAML from disk
    proposals_dir = tmp_path / "structure" / "proposals"
    proposal_files = sorted(proposals_dir.glob("*.yaml"))
    assert len(proposal_files) >= 1, "At least one proposal YAML should be written"

    proposal_path = proposal_files[0]
    proposal_data = yaml.safe_load(proposal_path.read_text(encoding="utf-8"))

    # Verify source_domain is set correctly (Issue 4 regression guard)
    assert proposal_data.get("source_domain") == "structure", (
        "propose-repairs should set source_domain='structure'"
    )

    # 4. Simulate author selection — pick the first option and add blueprint data
    first_option_id = proposal_data["options"][0]["id"]
    proposal_data["selection"] = {
        "selected_option_id": first_option_id,
        "custom_data": {},
    }
    # Patch in blueprint data so apply has something concrete to merge.
    # We add a 'structure.subplot_budget' field as the repair payload.
    proposal_data["options"][0]["data"] = {"structure": {"subplot_budget": 2}}
    proposal_path.write_text(
        yaml.safe_dump(proposal_data, sort_keys=False), encoding="utf-8"
    )

    # 5. Run apply
    output_dir = tmp_path / "applied"
    rc = main([
        "structure", "apply",
        str(proposal_path),
        str(blueprint_path),
        "--output", str(output_dir),
    ])
    assert rc == 0, "apply should exit 0"
    apply_output = json.loads(capsys.readouterr().out)

    # 6. Assert output blueprint has the merged field
    target_path = Path(apply_output["target_path"])
    assert target_path.exists(), "Output blueprint file should exist"
    applied_bp = yaml.safe_load(target_path.read_text(encoding="utf-8"))
    assert applied_bp["structure"]["subplot_budget"] == 2, (
        "Applied blueprint should have subplot_budget from proposal data"
    )

    # 7. Assert meta file records the proposal and selected option
    meta_path = Path(str(target_path) + ".meta.yaml")
    assert meta_path.exists(), ".meta.yaml should be written alongside applied blueprint"
    meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
    assert meta["applied_from_proposal"] == proposal_data["proposal_id"]
    assert meta["selected_option_id"] == first_option_id

    # 8. Assert original blueprint was not mutated
    original_content = yaml.safe_load(blueprint_path.read_text(encoding="utf-8"))
    assert "structure" not in original_content, (
        "Original blueprint should not be mutated by apply"
    )


def test_end_to_end_propose_repairs_output_dir_is_same_dir_by_default(
    tmp_path: Path, capsys
) -> None:
    """When --output is omitted, apply writes the new blueprint alongside the source."""
    blueprint_path = tmp_path / "blueprint.yaml"
    blueprint_path.write_text(_MINIMAL_BLUEPRINT_YAML, encoding="utf-8")

    main(["structure", "propose-repairs", str(blueprint_path)])
    capsys.readouterr()

    proposals_dir = tmp_path / "structure" / "proposals"
    proposal_path = sorted(proposals_dir.glob("*.yaml"))[0]
    proposal_data = yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
    first_option_id = proposal_data["options"][0]["id"]
    proposal_data["selection"] = {"selected_option_id": first_option_id, "custom_data": {}}
    proposal_data["options"][0]["data"] = {"structure": {"subplot_budget": 1}}
    proposal_path.write_text(yaml.safe_dump(proposal_data, sort_keys=False), encoding="utf-8")

    rc = main(["structure", "apply", str(proposal_path), str(blueprint_path)])
    assert rc == 0
    apply_output = json.loads(capsys.readouterr().out)

    # Default output dir is the blueprint's parent dir
    target_path = Path(apply_output["target_path"])
    assert target_path.parent == blueprint_path.parent
    assert target_path != blueprint_path


def test_end_to_end_propose_repairs_report_written_to_diagnostics_dir(
    tmp_path: Path, capsys
) -> None:
    """propose-repairs writes structure_report.json to structure/diagnostics/."""
    blueprint_path = tmp_path / "blueprint.yaml"
    blueprint_path.write_text(_MINIMAL_BLUEPRINT_YAML, encoding="utf-8")

    main(["structure", "propose-repairs", str(blueprint_path)])
    capsys.readouterr()

    report_path = tmp_path / "structure" / "diagnostics" / "structure_report.json"
    assert report_path.exists(), "structure_report.json should be written"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert len(report["diagnostics"]) >= 1
    assert report["diagnostics"][0]["rule"] == "story_engine.missing"


def test_structure_apply_rejects_bible_audit_proposal(
    tmp_path: Path, capsys
) -> None:
    """`auteur structure apply` rejects bible_audit proposals and leaves the
    source blueprint unchanged."""
    blueprint_path = tmp_path / "blueprint.yaml"
    blueprint_path.write_text(_MINIMAL_BLUEPRINT_YAML, encoding="utf-8")
    original_blueprint_text = blueprint_path.read_text(encoding="utf-8")

    proposal_path = tmp_path / "repair_from_audit.yaml"
    proposal_data = {
        "proposal_id": "repair_1_carriers_location_teleportation",
        "type": "repair",
        "source_domain": "bible_audit",
        "source_rule": "carriers.location_teleportation",
        "summary": "Aldric teleports from Throne Room to Dungeon.",
        "options": [
            {
                "id": "preserve_1",
                "summary": "Add a transition scene.",
                "tradeoffs": "Adds a scene but preserves intent.",
                "data": {},
            }
        ],
        "selection": {"selected_option_id": "preserve_1", "custom_data": {}},
    }
    proposal_path.write_text(
        yaml.safe_dump(proposal_data, sort_keys=False), encoding="utf-8"
    )

    rc = main(["structure", "apply", str(proposal_path), str(blueprint_path)])
    assert rc == 1

    stderr = capsys.readouterr().err
    assert "bible_audit proposals cannot be applied to blueprints" in stderr
    assert "auteur audit --accept" in stderr

    assert blueprint_path.read_text(encoding="utf-8") == original_blueprint_text, (
        "structure apply must not mutate the blueprint when source_domain is bible_audit"
    )


# ---------------------------------------------------------------------------
# Fixture: audit --accept stamps decision, does not mutate blueprint
# ---------------------------------------------------------------------------


def test_audit_accept_stamps_decision_on_proposal_yaml(tmp_path: Path, capsys) -> None:
    """`auteur audit --accept` stamps selection+decision in the YAML; does not
    mutate the blueprint file."""
    # 1. Init a project
    sample_yaml = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"
    project_path = tmp_path / "novel"
    assert main(["init", str(project_path), "--from", str(sample_yaml)]) == 0
    capsys.readouterr()

    blueprint_path = project_path / "blueprint.yaml"
    original_blueprint_text = blueprint_path.read_text(encoding="utf-8")

    # 2. Write a fake bible-audit proposal manually
    proposals_dir = project_path / "structure" / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)
    proposal_id = "repair_1_carriers_location_teleportation"
    proposal_path = proposals_dir / f"{proposal_id}.yaml"
    proposal_data = {
        "proposal_id": proposal_id,
        "type": "repair",
        "source_domain": "bible_audit",
        "source_rule": "carriers.location_teleportation",
        "summary": "Aldric teleports from Throne Room to Dungeon.",
        "options": [
            {
                "id": "preserve_1",
                "summary": "Add a transition scene.",
                "tradeoffs": "Adds a scene but preserves intent.",
                "data": {},
            }
        ],
        "selection": {"selected_option_id": "", "custom_data": {}},
    }
    proposal_path.write_text(
        yaml.safe_dump(proposal_data, sort_keys=False), encoding="utf-8"
    )

    # 3. Run audit --accept
    rc = main([
        "audit", str(project_path),
        "--accept", proposal_id,
        "--option", "preserve_1",
    ])
    assert rc == 0, "audit --accept should exit 0"
    capsys.readouterr()

    # 4. Proposal YAML has decision stamped
    updated = yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
    assert updated["decision"]["status"] == "accepted"
    assert updated["decision"]["selected_option_id"] == "preserve_1"
    assert updated["selection"]["selected_option_id"] == "preserve_1"

    # 5. Blueprint was NOT mutated
    assert blueprint_path.read_text(encoding="utf-8") == original_blueprint_text, (
        "audit --accept must not mutate the blueprint file"
    )
