import yaml
import pytest
from pydantic import ValidationError

from auteur.structure import (
    DiagnosticLayer,
    DiagnosticSeverity,
    RepairOptions,
    StructureDiagnostic,
)
from auteur.structure.proposals import (
    ProposalType,
    StructureProposal,
    propose_repairs_from_diagnostic_report,
    propose_repairs_from_diagnostics,
)

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


def test_creates_repair_proposal_from_error_diagnostic():
    diagnostic = StructureDiagnostic(
        severity=DiagnosticSeverity.ERROR,
        layer=DiagnosticLayer.SCOPE,
        rule="threads.exceeds_subplot_budget",
        message="Declared 6 subordinate threads but subplot_budget is 3.",
        evidence=[
            "structure.subplot_budget = 3",
            "story_engine.threads count = 6",
        ],
        repair_options=RepairOptions(
            preserve_intent=["Merge related threads."],
            challenge_intent=["Reduce story scope."],
        ),
    )

    proposals = propose_repairs_from_diagnostics([diagnostic])

    assert len(proposals) == 1
    proposal = proposals[0]
    assert proposal.type == ProposalType.REPAIR
    assert proposal.source_rule == "threads.exceeds_subplot_budget"
    assert "error" in proposal.summary
    assert "structure.subplot_budget = 3" in proposal.summary
    assert [option.id for option in proposal.options] == [
        "preserve_intent_1",
        "challenge_intent_1",
    ]


def test_creates_repair_proposal_from_warning_diagnostic_with_separate_repair_strategies():
    diagnostic = StructureDiagnostic(
        severity=DiagnosticSeverity.WARNING,
        layer=DiagnosticLayer.SCOPE,
        rule="structure.subplot_budget.missing",
        message="Subordinate threads exist, but structure.subplot_budget is not declared.",
        evidence=[
            "story_engine.threads count = 2",
            "structure.subplot_budget is absent",
        ],
        repair_options=RepairOptions(
            preserve_intent=["Declare a subplot_budget that matches the intended story scale."],
            challenge_intent=["Remove subordinate threads if the story should remain tightly focused."],
        ),
    )

    proposal = propose_repairs_from_diagnostics([diagnostic])[0]

    assert "warning" in proposal.summary
    assert proposal.source_rule == "structure.subplot_budget.missing"
    assert proposal.options[0].id == "preserve_intent_1"
    assert "Preserve-intent repair" in proposal.options[0].tradeoffs
    assert proposal.options[0].data == {}
    assert proposal.options[1].id == "challenge_intent_1"
    assert "Challenge-intent repair" in proposal.options[1].tradeoffs
    assert proposal.options[1].data == {}


def test_converts_diagnostic_report_to_repair_proposal_yaml_artifact():
    diagnostic = StructureDiagnostic(
        severity=DiagnosticSeverity.ERROR,
        layer=DiagnosticLayer.STRUCTURAL_FORCES,
        rule="main_thread.change_duplicates_want",
        message="The main thread change repeats the want.",
        evidence=[
            "main_thread.want.author_text = escape the city",
            "main_thread.change.author_text = escape the city",
        ],
        repair_options=RepairOptions(
            preserve_intent=["Rewrite change as the protagonist's end-state transformation."],
            challenge_intent=["Use a flat arc intentionally and describe world change instead."],
        ),
    )
    report = {"diagnostics": [diagnostic.model_dump(mode="json")]}

    proposal = propose_repairs_from_diagnostic_report(report)[0]
    yaml_text = yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False)
    recovered = StructureProposal.model_validate(yaml.safe_load(yaml_text))

    assert recovered.proposal_id == "repair_1_main_thread_change_duplicates_want"
    assert recovered.type == ProposalType.REPAIR
    assert recovered.source_rule == "main_thread.change_duplicates_want"
    assert recovered.selection.selected_option_id == ""
