from __future__ import annotations

from pathlib import Path

import yaml

from auteur.story_design_packs import AuthorAction, source_fingerprint
from auteur.story_design_packs.models import DecisionCard
from auteur.story_design_packs.session import TutorSessionStore, create_session
from auteur.structure.proposal_models import ProposalOption, StructureProposal
from auteur.structure.revision_service import RevisionService
from auteur.ui.author_attention import build_author_attention
from auteur.ui.dashboard import build_dashboard, format_dashboard

SAMPLE = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _card() -> DecisionCard:
    return DecisionCard(
        decision="Choose the next structural direction",
        orientation="We are deciding what structural change to pursue.",
        why_it_matters="The choice changes the shape of later planning.",
        craft_concept="Structural pressure",
        recommendation="Increase the runway",
        alternatives=["Keep the current runway"],
        tradeoffs=["More room, less compression."],
        beginner_trap="Treating advice as canon.",
        downstream_consequences=["Later plans may need review."],
        evidence=["blueprint:structure"],
        author_actions=[AuthorAction.CHOOSE, AuthorAction.KEEP_UNRESOLVED],
    )


def _write_proposal(path: Path, *, proposal_id: str, selected: bool) -> None:
    proposal = StructureProposal(
        proposal_id=proposal_id,
        type="repair",
        source_rule="orientation_fixture",
        source_domain="structure",
        summary="Adjust the planned runway.",
        options=[
            ProposalOption(
                id="adjust",
                summary="Adjust chapter count.",
                tradeoffs="Changes pacing budget.",
                data={"structure": {"estimated_chapters": 42}},
            )
        ],
    )
    if selected:
        proposal.accept("adjust", author="Author")
    path.write_text(
        yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )


def _project(tmp_path: Path) -> Path:
    (tmp_path / ".auteur" / "structure" / "proposals").mkdir(parents=True)
    (tmp_path / "blueprint.yaml").write_bytes(SAMPLE.read_bytes())
    (tmp_path / "story_identity.yaml").write_text("accepted identity sentinel\n", encoding="utf-8")

    source = tmp_path / "decision-source.txt"
    source.write_text("v1", encoding="utf-8")
    session = create_session(
        _card(),
        {"source=decision-source.txt": source_fingerprint(source.read_bytes())},
    )
    TutorSessionStore(tmp_path).save(session)
    source.write_text("v2", encoding="utf-8")

    unselected = tmp_path / ".auteur" / "structure" / "proposals" / "unselected.yaml"
    _write_proposal(unselected, proposal_id="unselected", selected=False)
    selected = tmp_path / ".auteur" / "structure" / "proposals" / "selected.yaml"
    _write_proposal(selected, proposal_id="selected", selected=True)
    RevisionService(tmp_path).plan(proposal_path=selected)
    return tmp_path


def _snapshot(project: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(project)): path.read_bytes()
        for path in sorted(project.rglob("*"))
        if path.is_file()
    }


def test_author_attention_prioritizes_existing_artifact_states_without_writes(tmp_path: Path):
    project = _project(tmp_path)
    before = _snapshot(project)

    attention = build_author_attention(project)

    assert [item["priority"] for item in attention] == sorted(item["priority"] for item in attention)
    assert attention[0]["kind"] == "tutor_session"
    assert attention[0]["state"] == "stale"
    assert attention[0]["authority_status"] == "LOCAL / NONCANONICAL"
    assert any(
        item["kind"] == "structure_proposal"
        and item["artifact_id"] == "unselected"
        and item["state"] == "unselected"
        and "structure proposal inspect" in item["next_command"]
        for item in attention
    )
    assert any(
        item["kind"] == "structure_revision_plan"
        and item["state"] == "draft"
        and "structure revision validate" in item["next_command"]
        for item in attention
    )
    assert _snapshot(project) == before


def test_dashboard_adds_author_attention_without_changing_project_files(tmp_path: Path):
    project = _project(tmp_path)
    before = _snapshot(project)

    data = build_dashboard(project)
    rendered = format_dashboard(data)

    assert data["author_attention"]
    assert "## Author Attention" in rendered
    assert rendered.index("## Author Attention") < rendered.index("## Recommended Actions")
    assert "LOCAL / NONCANONICAL" in rendered
    assert _snapshot(project) == before


def test_empty_attention_is_backward_compatible_in_formatter(tmp_path: Path):
    rendered = format_dashboard(
        {
            "project": str(tmp_path),
            "status": {},
            "lifecycle": {},
            "alerts": [],
            "commitment": {},
            "author_attention": [],
        }
    )

    assert "No pending Tutor/proposal/revision item requires attention." in rendered
