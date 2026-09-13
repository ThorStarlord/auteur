from __future__ import annotations

import json
from pathlib import Path

import yaml

from auteur.cli import main
from auteur.structure.proposal_models import ProposalOption, StructureProposal
from auteur.structure.revision_service import RevisionService

SAMPLE = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _project(tmp_path: Path) -> tuple[Path, Path]:
    (tmp_path / ".auteur" / "structure" / "proposals").mkdir(parents=True)
    blueprint = tmp_path / "blueprint.yaml"
    blueprint.write_bytes(SAMPLE.read_bytes())
    (tmp_path / "story_identity.yaml").write_text("accepted identity sentinel\n", encoding="utf-8")

    raw_blueprint = yaml.safe_load(blueprint.read_text(encoding="utf-8"))
    replacement = dict(raw_blueprint["structure"])
    replacement.update(
        estimated_chapters=48,
        act_structure="three_act",
        subplot_budget=4,
    )
    proposal = StructureProposal(
        proposal_id="tutor_revision_001",
        type="repair",
        source_rule="bounded_test_source",
        source_domain="tutor_card:card_revision_001",
        summary="Give the selected direction more structural runway.",
        options=[
            ProposalOption(
                id="option_revision",
                summary="Expand the chapter runway and subplot budget.",
                tradeoffs="More escalation space, less compression.",
                data={"structure": replacement},
            )
        ],
    )
    proposal_path = tmp_path / ".auteur" / "structure" / "proposals" / "tutor_revision_001.yaml"
    proposal_path.write_text(
        yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    return tmp_path, proposal_path


def _select(project: Path, proposal_path: Path, capsys) -> None:
    assert main([
        "structure", "proposal", "select", str(proposal_path.relative_to(project)),
        "--option", "option_revision", "--project", str(project), "--json",
    ]) == 0
    capsys.readouterr()


def test_selected_tutor_proposal_becomes_one_atomic_blueprint_operation(
    tmp_path: Path, capsys
):
    project, proposal_path = _project(tmp_path)
    _select(project, proposal_path, capsys)

    plan = RevisionService(project).plan(proposal_path=proposal_path)

    assert len(plan.operations) == 1
    operation = plan.operations[0]
    assert operation.target_id == "blueprint"
    assert operation.target_type == "blueprint"
    assert operation.operation_type.value == "replace"
    assert operation.requested_change["data"]["structure"] == {
        "estimated_chapters": 48,
        "act_structure": "three_act",
        "subplot_budget": 4,
    }
    assert plan.preconditions[0].expected_hash.startswith("sha256:")


def test_cli_selected_proposal_plan_then_validate_is_ready_without_story_mutation(
    tmp_path: Path, capsys
):
    project, proposal_path = _project(tmp_path)
    _select(project, proposal_path, capsys)
    identity_before = (project / "story_identity.yaml").read_bytes()
    blueprint_before = (project / "blueprint.yaml").read_bytes()

    assert main([
        "structure", "revision", "plan", "--proposal", str(proposal_path.relative_to(project)),
        "--project", str(project), "--json",
    ]) == 0
    planned = json.loads(capsys.readouterr().out)
    assert planned["authority_status"] == "REVISION PLAN / NOT APPLIED"
    assert planned["mutates_story"] is False
    assert planned["operation_count"] == 1

    assert main([
        "structure", "revision", "validate", planned["plan_id"],
        "--project", str(project), "--json",
    ]) == 0
    validated = json.loads(capsys.readouterr().out)
    assert validated["state"] == "ready"
    assert validated["ready_for_application"] is True
    assert validated["preconditions"][0]["met"] is True
    assert validated["preconditions"][0]["expected_hash"] == validated["preconditions"][0]["actual_hash"]
    assert (project / "story_identity.yaml").read_bytes() == identity_before
    assert (project / "blueprint.yaml").read_bytes() == blueprint_before


def test_revision_validation_blocks_if_blueprint_changes_after_plan(tmp_path: Path, capsys):
    project, proposal_path = _project(tmp_path)
    _select(project, proposal_path, capsys)
    plan = RevisionService(project).plan(proposal_path=proposal_path)
    raw = yaml.safe_load((project / "blueprint.yaml").read_text(encoding="utf-8"))
    raw["structure"]["estimated_chapters"] = 46
    (project / "blueprint.yaml").write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    changed = (project / "blueprint.yaml").read_bytes()

    assert main([
        "structure", "revision", "validate", plan.plan_id,
        "--project", str(project), "--json",
    ]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["state"] == "blocked"
    assert payload["preconditions"][0]["met"] is False
    assert (project / "blueprint.yaml").read_bytes() == changed
