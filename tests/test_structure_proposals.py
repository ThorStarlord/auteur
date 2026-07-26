import json
from pathlib import Path
import pytest
import yaml
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
from auteur.blueprint import StoryBlueprint

SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"

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


class TestImpactProposalBridge:
    """Tests for propose_repairs_from_impact_findings."""

    def test_returns_proposals_for_severe_findings(self):
        from auteur.structure.proposal_generation import propose_repairs_from_impact_findings
        findings = [
            {"rule": "impact.continuity", "severity": "blocked", "message": "Chapter 3 contradicts chapter 1", "recommended_action": "Reconcile chapter 3"},
        ]
        proposals = propose_repairs_from_impact_findings(findings)
        assert len(proposals) == 1
        assert proposals[0].source_domain == "impact"
        assert proposals[0].source_rule == "impact.continuity"

    def test_skips_info_severity(self):
        from auteur.structure.proposal_generation import propose_repairs_from_impact_findings
        findings = [
            {"rule": "impact.info", "severity": "info", "message": "Nothing to see here"},
        ]
        proposals = propose_repairs_from_impact_findings(findings)
        assert len(proposals) == 0

    def test_sets_source_domain(self):
        from auteur.structure.proposal_generation import propose_repairs_from_impact_findings
        findings = [
            {"rule": "impact.test", "severity": "reconcile", "message": "Test finding"},
        ]
        proposals = propose_repairs_from_impact_findings(findings)
        assert all(p.source_domain == "impact" for p in proposals)

    def test_empty_findings(self):
        from auteur.structure.proposal_generation import propose_repairs_from_impact_findings
        proposals = propose_repairs_from_impact_findings([])
        assert proposals == []


class TestApplyImpactProposal:
    """Tests for apply_impact_proposal — author decision boundary for impact proposals."""

    def _make_impact_proposal(self, *, accepted: bool = True) -> StructureProposal:
        """Build a typical impact proposal for testing."""
        from auteur.structure.proposal_generation import propose_repairs_from_impact_findings
        proposals = propose_repairs_from_impact_findings([
            {"rule": "impact.continuity", "severity": "blocked",
             "message": "Chapter 3 contradicts chapter 1",
             "recommended_action": "Reconcile chapter 3"},
        ])
        prop = proposals[0]
        if accepted:
            prop.accept("recommended", author="test_author")
        return prop

    def test_rejects_proposal_without_decision(self, tmp_path):
        """apply_impact_proposal fails when no decision has been recorded."""
        from auteur.cli_handlers import apply_impact_proposal
        blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
        prop = self._make_impact_proposal(accepted=False)
        # selection is empty since accept() was never called
        result = apply_impact_proposal(prop, blueprint, output_dir=str(tmp_path))
        assert not result.is_success
        assert "decision" in result.error

    def test_rejects_non_accepted_decision(self, tmp_path):
        """apply_impact_proposal fails when decision status is not 'accepted'."""
        from auteur.cli_handlers import apply_impact_proposal
        from auteur.structure.proposal_models import ProposalDecision
        blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
        prop = self._make_impact_proposal(accepted=False)
        # Set a rejected decision directly
        prop.decision = ProposalDecision(
            selected_option_id="author_override",
            status="rejected",
            author="test_author",
        )
        result = apply_impact_proposal(prop, blueprint, output_dir=str(tmp_path))
        assert not result.is_success
        assert "not 'accepted'" in result.error

    def test_applies_accepted_impact_proposal(self, tmp_path):
        """Full flow: generate impact proposal, accept, apply."""
        from auteur.cli_handlers import apply_impact_proposal
        blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
        prop = self._make_impact_proposal(accepted=True)
        result = apply_impact_proposal(prop, blueprint, output_dir=str(tmp_path))
        assert result.is_success
        assert result.data["target_path"] is not None
        assert result.data["selected_option_id"] == "recommended"
        assert result.data["decision_author"] == "test_author"
        assert result.data["decision_status"] == "accepted"
        # Verify the output file was created
        assert Path(result.data["target_path"]).exists()
        # Verify sidecar was created
        assert Path(result.data["target_path"] + ".meta.yaml").exists()

    def test_applies_impact_proposal_with_override_option(self, tmp_path):
        """Applying an impact proposal with author_override works."""
        from auteur.cli_handlers import apply_impact_proposal
        blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
        prop = self._make_impact_proposal(accepted=True)
        prop.accept("author_override", author="test_author")
        result = apply_impact_proposal(prop, blueprint, output_dir=str(tmp_path))
        assert result.is_success
        assert result.data["selected_option_id"] == "author_override"

    def test_in_place_apply(self, tmp_path):
        """in_place=True writes the blueprint back to the original path."""
        from auteur.cli_handlers import apply_impact_proposal
        import shutil
        bp_path = tmp_path / "blueprint.yaml"
        shutil.copy2(str(SAMPLE_YAML), str(bp_path))
        blueprint = StoryBlueprint.from_yaml(bp_path)
        prop = self._make_impact_proposal(accepted=True)
        result = apply_impact_proposal(prop, blueprint, in_place=True, original_path=str(bp_path))
        assert result.is_success
        assert result.data["target_path"] == str(bp_path)
        # The file should have been overwritten with the same content (no-op merge)
        assert bp_path.exists()

    def test_format_apply_impact_proposal(self, tmp_path):
        """format_apply_impact_proposal produces valid JSON with decision metadata."""
        from auteur.cli_handlers import apply_impact_proposal, HandlerResult
        from auteur.cli_formatters import format_apply_impact_proposal
        import json
        blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
        prop = self._make_impact_proposal(accepted=True)
        result = apply_impact_proposal(prop, blueprint, output_dir=str(tmp_path))
        output = format_apply_impact_proposal(result)
        assert output is not None
        parsed = json.loads(output)
        assert parsed["selected_option_id"] == "recommended"
        assert parsed["decision_author"] == "test_author"
        assert parsed["decision_status"] == "accepted"
        assert "target_path" in parsed

    def test_format_apply_impact_proposal_error(self):
        """format_apply_impact_proposal formats an error result."""
        from auteur.cli_handlers import HandlerResult
        from auteur.cli_formatters import format_apply_impact_proposal
        result = HandlerResult.failure("no decision")
        output = format_apply_impact_proposal(result)
        assert output is not None
        assert "no decision" in output.lower()
