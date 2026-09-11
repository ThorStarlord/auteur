from __future__ import annotations

import json
from pathlib import Path

import yaml

from auteur.cli import main
from auteur.structure import proposal_cli
from auteur.structure.proposal_models import ProposalOption, StructureProposal


def _project(tmp_path: Path) -> tuple[Path, Path]:
    (tmp_path / ".auteur" / "structure" / "proposals").mkdir(parents=True)
    (tmp_path / "story_identity.yaml").write_text("identity sentinel\n", encoding="utf-8")
    (tmp_path / "blueprint.yaml").write_text("blueprint sentinel\n", encoding="utf-8")
    proposal = StructureProposal(
        proposal_id="proposal_review_001",
        type="repair",
        summary="Choose a clearer midpoint reversal.",
        options=[
            ProposalOption(
                id="sharpen_midpoint",
                summary="Make the midpoint irreversibly change the goal.",
                tradeoffs="Stronger causality, less room for a soft transition.",
                data={"structure": {"estimated_chapters": 42}},
            )
        ],
    )
    path = tmp_path / ".auteur" / "structure" / "proposals" / "proposal_review_001.yaml"
    path.write_text(yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
    return tmp_path, path


def test_structure_proposal_inspect_is_read_only_and_explicitly_noncanonical(
    tmp_path: Path, capsys
):
    project, path = _project(tmp_path)
    before = path.read_bytes()

    assert main(["structure", "proposal", "inspect", str(path.relative_to(project)), "--project", str(project), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["proposal_id"] == "proposal_review_001"
    assert payload["selected_option_id"] is None
    assert payload["authority_status"] == "NONCANONICAL PROPOSAL / NOT APPLIED"
    assert payload["mutates_story"] is False
    assert payload["ready_for_revision_plan"] is False
    assert "structure proposal select" in payload["select_command"]
    assert path.read_bytes() == before


def test_structure_proposal_select_records_only_proposal_decision(tmp_path: Path, capsys):
    project, path = _project(tmp_path)
    identity_before = (project / "story_identity.yaml").read_bytes()
    blueprint_before = (project / "blueprint.yaml").read_bytes()

    assert main([
        "structure", "proposal", "select", str(path.relative_to(project)),
        "--option", "sharpen_midpoint", "--author", "Author", "--project", str(project), "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)
    saved = StructureProposal.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))

    assert saved.selection.selected_option_id == "sharpen_midpoint"
    assert saved.decision is not None and saved.decision.author == "Author"
    assert payload["ready_for_revision_plan"] is True
    assert "structure revision plan" in payload["next_command"]
    assert (project / "story_identity.yaml").read_bytes() == identity_before
    assert (project / "blueprint.yaml").read_bytes() == blueprint_before


def test_invalid_option_fails_without_rewriting_proposal(tmp_path: Path, capsys):
    project, path = _project(tmp_path)
    before = path.read_bytes()

    assert main([
        "structure", "proposal", "select", str(path.relative_to(project)),
        "--option", "missing", "--project", str(project),
    ]) == 1

    assert "does not match any option" in capsys.readouterr().err
    assert path.read_bytes() == before


def test_selection_does_not_overwrite_a_different_prior_decision(tmp_path: Path, capsys):
    project, path = _project(tmp_path)
    proposal = StructureProposal.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    proposal.options.append(
        ProposalOption(id="other", summary="Other route.", tradeoffs="Different cost.", data={"theme": {"statement": "x"}})
    )
    proposal.accept("sharpen_midpoint", author="First Author")
    path.write_text(yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
    before = path.read_bytes()

    assert main([
        "structure", "proposal", "select", str(path.relative_to(project)),
        "--option", "other", "--project", str(project),
    ]) == 1

    assert "already selected" in capsys.readouterr().err
    assert path.read_bytes() == before


def test_proposal_path_outside_project_is_rejected(tmp_path: Path, capsys):
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside.yaml"
    outside.write_text("proposal_id: outside\n", encoding="utf-8")

    assert main([
        "structure", "proposal", "inspect", str(outside), "--project", str(project),
    ]) == 1
    assert "inside the selected project" in capsys.readouterr().err


def test_atomic_replace_failure_leaves_original_proposal(tmp_path: Path, monkeypatch, capsys):
    project, path = _project(tmp_path)
    before = path.read_bytes()

    def fail_replace(_source, _target):
        raise OSError("replace failed")

    monkeypatch.setattr(proposal_cli.os, "replace", fail_replace)
    assert main([
        "structure", "proposal", "select", str(path.relative_to(project)),
        "--option", "sharpen_midpoint", "--project", str(project),
    ]) == 1

    assert "replace failed" in capsys.readouterr().err
    assert path.read_bytes() == before
    assert not list(path.parent.glob("*.tmp"))
