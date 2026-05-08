import yaml
import pytest
from pydantic import ValidationError

from auteur.structure.proposals import StructureProposal, ProposalType

def test_proposal_parsing_from_yaml():
    yaml_text = """
proposal_id: "001"
type: "repair"
source_rule: "threads.exceeds_subplot_budget"
summary: "Reduce subordinate threads to match subplot budget."

options:
  - id: "merge_threads"
    summary: "Merge related threads"
    tradeoffs: "Reduces complexity but might lose specific character focus."
    data:
      story_engine:
        threads: []

  - id: "increase_budget"
    summary: "Increase subplot budget"
    tradeoffs: "Allows more complexity but increases risk of a bloated story."
    data:
      structure:
        subplot_budget: 5

selection:
  selected_option_id: "increase_budget"
  custom_data: {}
"""
    data = yaml.safe_load(yaml_text)
    proposal = StructureProposal.model_validate(data)

    assert proposal.proposal_id == "001"
    assert proposal.type == ProposalType.REPAIR
    assert proposal.source_rule == "threads.exceeds_subplot_budget"
    assert len(proposal.options) == 2
    assert proposal.options[0].id == "merge_threads"
    assert proposal.options[1].data["structure"]["subplot_budget"] == 5
    assert proposal.selection.selected_option_id == "increase_budget"

def test_proposal_selection_defaults():
    proposal_data = {
        "proposal_id": "gen_001",
        "type": "generation",
        "summary": "Initial generation",
        "options": [
            {
                "id": "opt1",
                "summary": "Option 1",
                "tradeoffs": "T1",
                "data": {}
            }
        ]
    }
    proposal = StructureProposal.model_validate(proposal_data)
    assert proposal.selection.selected_option_id == ""
    assert proposal.selection.custom_data == {}


def test_rejects_unknown_selected_option_id():
    proposal_data = {
        "proposal_id": "gen_001",
        "type": "generation",
        "summary": "Initial generation",
        "options": [
            {
                "id": "opt1",
                "summary": "Option 1",
                "tradeoffs": "T1",
                "data": {},
            }
        ],
        "selection": {"selected_option_id": "missing", "custom_data": {}},
    }

    with pytest.raises(ValidationError):
        StructureProposal.model_validate(proposal_data)


def test_rejects_duplicate_option_ids():
    proposal_data = {
        "proposal_id": "gen_001",
        "type": "generation",
        "summary": "Initial generation",
        "options": [
            {
                "id": "opt1",
                "summary": "Option 1",
                "tradeoffs": "T1",
                "data": {},
            },
            {
                "id": "opt1",
                "summary": "Option  duplicate",
                "tradeoffs": "T2",
                "data": {},
            },
        ],
    }

    with pytest.raises(ValidationError):
        StructureProposal.model_validate(proposal_data)
