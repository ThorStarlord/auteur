import yaml
from pathlib import Path

from auteur.structure.proposals import StructureProposal, apply_proposal_to_blueprint
from auteur.blueprint import StoryBlueprint


def test_accept_records_selection_and_metadata():
    proposal_data = {
        "proposal_id": "001",
        "type": "repair",
        "source_rule": "threads.exceeds_subplot_budget",
        "summary": "Reduce subordinate threads to match subplot budget.",
        "options": [
            {
                "id": "merge_threads",
                "summary": "Merge related threads",
                "tradeoffs": "Reduces complexity but might lose specific character focus.",
                "data": {"story_engine": {"threads": []}},
            },
            {
                "id": "increase_budget",
                "summary": "Increase subplot budget",
                "tradeoffs": "Allows more complexity but increases risk of a bloated story.",
                "data": {"structure": {"subplot_budget": 5}},
            },
        ],
    }

    proposal = StructureProposal.model_validate(proposal_data)
    proposal.accept(
        "increase_budget",
        {"reason": "designer prefers more threads"},
        author="tester",
        references=["threads.exceeds_subplot_budget"],
    )

    assert proposal.selection.selected_option_id == "increase_budget"
    assert proposal.decision is not None
    assert proposal.decision.author == "tester"
    assert "threads.exceeds_subplot_budget" in proposal.decision.references


def test_apply_creates_new_blueprint_file_by_default(tmp_path):
    sample_path = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"
    blueprint = StoryBlueprint.from_yaml(str(sample_path))

    proposal_data = {
        "proposal_id": "002",
        "type": "repair",
        "summary": "Increase subplot budget",
        "options": [
            {
                "id": "increase_budget",
                "summary": "Increase subplot budget",
                "tradeoffs": "Allows more complexity",
                "data": {"structure": {"subplot_budget": 5}},
            }
        ],
        "selection": {"selected_option_id": "increase_budget", "custom_data": {}},
    }

    proposal = StructureProposal.model_validate(proposal_data)

    new_bp, path = apply_proposal_to_blueprint(proposal, blueprint, output_dir=str(tmp_path))

    assert new_bp.structure.subplot_budget == 5
    assert Path(path).exists()
    assert Path(path + ".meta.yaml").exists()
    meta = yaml.safe_load(Path(path + ".meta.yaml").read_text(encoding="utf-8"))
    assert meta["applied_from_proposal"] == "002"
