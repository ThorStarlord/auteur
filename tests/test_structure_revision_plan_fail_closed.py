from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.structure.proposal_models import ProposalOption, StructureProposal
from auteur.structure.revision_service import RevisionService


def _project(tmp_path: Path) -> Path:
    (tmp_path / ".auteur").mkdir()
    (tmp_path / "blueprint.yaml").write_text("accepted blueprint sentinel\n", encoding="utf-8")
    return tmp_path


def _write(project: Path, proposal: StructureProposal, name: str = "proposal.yaml") -> Path:
    path = project / name
    path.write_text(
        yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    return path


def _proposal(data: dict, *, selected: bool) -> StructureProposal:
    proposal = StructureProposal(
        proposal_id="proposal_fail_closed",
        type="repair",
        summary="A bounded structural change.",
        options=[
            ProposalOption(
                id="option_a",
                summary="Apply the bounded change.",
                tradeoffs="Controlled fixture.",
                data=data,
            )
        ],
    )
    if selected:
        proposal.accept("option_a")
    return proposal


def _assert_no_revision_artifacts(project: Path) -> None:
    base = project / ".auteur" / "structure"
    for name in ("revision-plans", "revision-events"):
        path = base / name
        assert not path.exists() or not list(path.glob("*.yaml"))


def test_revision_plan_rejects_unselected_proposal_before_persistence(tmp_path: Path):
    project = _project(tmp_path)
    before = (project / "blueprint.yaml").read_bytes()
    path = _write(project, _proposal({"structure": {"estimated_chapters": 48}}, selected=False))
    service = RevisionService(project)

    with pytest.raises(ValueError, match="selected"):
        service.plan(proposal_path=path)

    _assert_no_revision_artifacts(project)
    assert (project / "blueprint.yaml").read_bytes() == before


def test_revision_plan_rejects_selected_proposal_with_zero_operations(tmp_path: Path):
    project = _project(tmp_path)
    path = _write(project, _proposal({}, selected=True))
    service = RevisionService(project)

    with pytest.raises(ValueError, match="operations"):
        service.plan(proposal_path=path)

    _assert_no_revision_artifacts(project)


def test_revision_plan_still_accepts_selected_proposal_with_concrete_operation(tmp_path: Path):
    project = _project(tmp_path)
    path = _write(
        project,
        _proposal(
            {
                "structure": {
                    "estimated_chapters": 48,
                    "act_structure": "three_act",
                    "subplot_budget": 3,
                }
            },
            selected=True,
        ),
    )
    plan = RevisionService(project).plan(proposal_path=path)

    assert plan.operations
    assert plan.operations[0].target_id == "blueprint"
    assert plan.operations[0].requested_change["value"]["estimated_chapters"] == 48
    assert (project / ".auteur" / "structure" / "revision-plans" / f"{plan.plan_id}.yaml").is_file()
