from __future__ import annotations

import json
from pathlib import Path

import yaml

from auteur.cli import main
from auteur.structure.proposal_models import ProposalOption, StructureProposal

SAMPLE = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _project(tmp_path: Path) -> tuple[Path, Path]:
    (tmp_path / ".auteur" / "structure" / "proposals").mkdir(parents=True)
    (tmp_path / "blueprint.yaml").write_bytes(SAMPLE.read_bytes())
    (tmp_path / "story_identity.yaml").write_text("accepted identity sentinel\n", encoding="utf-8")
    raw = yaml.safe_load((tmp_path / "blueprint.yaml").read_text(encoding="utf-8"))
    structure = dict(raw["structure"])
    structure["estimated_chapters"] = 48
    proposal = StructureProposal(
        proposal_id="preview_proposal",
        type="repair",
        source_rule="preview_fixture",
        source_domain="tutor_card:preview_card",
        summary="Expand the planned runway.",
        options=[
            ProposalOption(
                id="expand",
                summary="Expand the structural runway.",
                tradeoffs="More room, less compression.",
                data={"structure": structure},
            )
        ],
    )
    proposal_path = tmp_path / ".auteur" / "structure" / "proposals" / "preview_proposal.yaml"
    proposal_path.write_text(
        yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    return tmp_path, proposal_path


def _plan_and_validate(project: Path, proposal_path: Path, capsys) -> str:
    rel = str(proposal_path.relative_to(project))
    assert main([
        "structure", "proposal", "select", rel,
        "--option", "expand", "--project", str(project), "--json",
    ]) == 0
    capsys.readouterr()
    assert main([
        "structure", "revision", "plan", "--proposal", rel,
        "--project", str(project), "--json",
    ]) == 0
    plan_id = json.loads(capsys.readouterr().out)["plan_id"]
    assert main([
        "structure", "revision", "validate", plan_id,
        "--project", str(project), "--json",
    ]) == 0
    capsys.readouterr()
    return plan_id


def _snapshot(project: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(project)): path.read_bytes()
        for path in sorted(project.rglob("*"))
        if path.is_file()
    }


def test_revision_preview_reports_bounded_dependency_impact_without_writes(
    tmp_path: Path, capsys
):
    project, proposal_path = _project(tmp_path)
    plan_id = _plan_and_validate(project, proposal_path, capsys)
    before = _snapshot(project)

    assert main([
        "structure", "revision", "preview", plan_id,
        "--project", str(project), "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["authority_status"] == "DERIVED PREVIEW / NOT APPLIED"
    assert payload["mutates_story"] is False
    assert payload["currentness"] == "current"
    assert payload["direct_targets"] == ["blueprint"]
    assert payload["changed_fields"] == ["structure"]
    assert payload["ready_for_authority_action"] is True
    impacted = {item["artifact_id"] for item in payload["definite_downstream_impacts"]}
    assert {
        "chapter_outline",
        "scene_realization",
        "scene_expression",
        "chapter_expression",
        "book_expression",
        "published_output",
    } <= impacted
    assert {"book_plan", "chapter_plan"}.isdisjoint(impacted)
    assert payload["inferred_downstream_impacts"] == []
    assert "structure revision apply" in payload["next_command"]
    assert _snapshot(project) == before


def test_stale_revision_plan_remains_previewable_but_not_actionable(tmp_path: Path, capsys):
    project, proposal_path = _project(tmp_path)
    plan_id = _plan_and_validate(project, proposal_path, capsys)
    raw = yaml.safe_load((project / "blueprint.yaml").read_text(encoding="utf-8"))
    raw["structure"]["estimated_chapters"] = 43
    (project / "blueprint.yaml").write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    before = _snapshot(project)

    assert main([
        "structure", "revision", "preview", plan_id,
        "--project", str(project), "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["currentness"] == "stale"
    assert payload["ready_for_authority_action"] is False
    assert payload["next_command"] is None
    assert any(check["met"] is False for check in payload["preconditions"])
    assert _snapshot(project) == before


def test_missing_revision_plan_preview_fails_cleanly(tmp_path: Path, capsys):
    (tmp_path / ".auteur").mkdir()

    assert main([
        "structure", "revision", "preview", "missing-plan",
        "--project", str(tmp_path), "--json",
    ]) == 1

    assert "Revision plan not found" in capsys.readouterr().err
