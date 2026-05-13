"""Tests for source_domain field on StructureProposal.

RED tests (will fail until source_domain is added to the model and generation
functions populate it).
"""
from __future__ import annotations

import yaml

from auteur.structure.proposals import (
    ProposalType,
    StructureProposal,
    propose_repairs_from_diagnostics,
)
from auteur.structure import (
    DiagnosticLayer,
    DiagnosticSeverity,
    RepairOptions,
    StructureDiagnostic,
)


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


def test_source_domain_defaults_to_none():
    """Existing-style YAMLs without source_domain parse with source_domain=None."""
    data = {
        "proposal_id": "test_001",
        "type": "repair",
        "summary": "Test proposal",
        "options": [
            {
                "id": "opt_a",
                "summary": "Option A",
                "tradeoffs": "Some tradeoff",
                "data": {},
            }
        ],
    }
    proposal = StructureProposal.model_validate(data)
    assert proposal.source_domain is None


def test_source_domain_structure_accepted():
    """source_domain='structure' is a valid value."""
    data = {
        "proposal_id": "test_002",
        "type": "repair",
        "source_domain": "structure",
        "summary": "Test proposal",
        "options": [
            {
                "id": "opt_a",
                "summary": "Option A",
                "tradeoffs": "Some tradeoff",
                "data": {},
            }
        ],
    }
    proposal = StructureProposal.model_validate(data)
    assert proposal.source_domain == "structure"


def test_source_domain_bible_audit_accepted():
    """source_domain='bible_audit' is a valid value."""
    data = {
        "proposal_id": "test_003",
        "type": "repair",
        "source_domain": "bible_audit",
        "summary": "Test proposal",
        "options": [
            {
                "id": "opt_a",
                "summary": "Option A",
                "tradeoffs": "Some tradeoff",
                "data": {},
            }
        ],
    }
    proposal = StructureProposal.model_validate(data)
    assert proposal.source_domain == "bible_audit"


def test_source_domain_round_trips_yaml():
    """source_domain survives a YAML serialise/parse round-trip."""
    data = {
        "proposal_id": "test_004",
        "type": "repair",
        "source_domain": "structure",
        "summary": "Test proposal",
        "options": [
            {
                "id": "opt_a",
                "summary": "Option A",
                "tradeoffs": "Some tradeoff",
                "data": {},
            }
        ],
    }
    proposal = StructureProposal.model_validate(data)
    dumped = yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False)
    reloaded = StructureProposal.model_validate(yaml.safe_load(dumped))
    assert reloaded.source_domain == "structure"


# ---------------------------------------------------------------------------
# Generation tests: structure path sets source_domain="structure"
# ---------------------------------------------------------------------------


def _make_diagnostic(rule: str = "story_engine.missing") -> StructureDiagnostic:
    return StructureDiagnostic(
        severity=DiagnosticSeverity.ERROR,
        layer=DiagnosticLayer.STRUCTURAL_FORCES,
        rule=rule,
        message="Missing story engine.",
        evidence=[],
        repair_options=RepairOptions(
            preserve_intent=["Add a main thread."],
            challenge_intent=["Restructure the premise."],
        ),
    )


def test_propose_repairs_sets_source_domain_structure():
    """propose_repairs_from_diagnostics sets source_domain='structure' on each proposal."""
    diag = _make_diagnostic()
    proposals = propose_repairs_from_diagnostics([diag])
    assert len(proposals) == 1
    assert proposals[0].source_domain == "structure"


def test_propose_repairs_multiple_diagnostics_all_have_source_domain():
    """All proposals from propose_repairs_from_diagnostics have source_domain='structure'."""
    diagnostics = [_make_diagnostic(f"rule_{i}") for i in range(3)]
    proposals = propose_repairs_from_diagnostics(diagnostics)
    assert all(p.source_domain == "structure" for p in proposals)


# ---------------------------------------------------------------------------
# Generation tests: Bible audit path sets source_domain="bible_audit"
# ---------------------------------------------------------------------------


def test_write_audit_repair_proposals_sets_source_domain_bible_audit(tmp_path):
    """write_audit_repair_proposals writes proposals with source_domain='bible_audit'."""
    from auteur.structure.proposal_resolution import write_audit_repair_proposals

    diag = _make_diagnostic("carriers.location_teleportation")
    write_audit_repair_proposals(tmp_path, [diag])

    proposal_files = list((tmp_path / "structure" / "proposals").glob("repair_*.yaml"))
    assert len(proposal_files) == 1

    proposal_data = yaml.safe_load(proposal_files[0].read_text(encoding="utf-8"))
    assert proposal_data.get("source_domain") == "bible_audit"
