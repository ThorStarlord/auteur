"""Tests for the refactored proposal generation: propose_repairs_from_audit_diagnostics.

RED: These tests will fail until propose_repairs_from_audit_diagnostics is added
to proposal_generation.py and proposal_resolution.py no longer contains generation
logic.
"""
from __future__ import annotations

from auteur.structure import (
    DiagnosticLayer,
    DiagnosticSeverity,
    RepairOptions,
    StructureDiagnostic,
)
from auteur.structure.proposals import (
    StructureProposal,
    propose_repairs_from_audit_diagnostics,
)


def _audit_diag(rule: str = "carriers.location_teleportation") -> StructureDiagnostic:
    return StructureDiagnostic(
        severity=DiagnosticSeverity.ERROR,
        layer=DiagnosticLayer.CARRIERS,
        rule=rule,
        message="Aldric teleports without a transition.",
        evidence=["event 3 → event 5"],
        repair_options=RepairOptions(
            preserve_intent=["Add a transition scene."],
            challenge_intent=["Restructure events 3-5."],
        ),
    )


def test_propose_repairs_from_audit_diagnostics_returns_proposals():
    """propose_repairs_from_audit_diagnostics is callable and returns proposals."""
    diag = _audit_diag()
    proposals = propose_repairs_from_audit_diagnostics([diag])
    assert len(proposals) == 1
    assert isinstance(proposals[0], StructureProposal)


def test_propose_repairs_from_audit_diagnostics_sets_source_domain():
    """All proposals have source_domain='bible_audit'."""
    diags = [_audit_diag(f"rule_{i}") for i in range(3)]
    proposals = propose_repairs_from_audit_diagnostics(diags)
    assert all(p.source_domain == "bible_audit" for p in proposals)


def test_propose_repairs_from_audit_diagnostics_preserves_source_rule():
    """source_rule is set from the diagnostic rule."""
    diag = _audit_diag("carriers.location_teleportation")
    proposals = propose_repairs_from_audit_diagnostics([diag])
    assert proposals[0].source_rule == "carriers.location_teleportation"


def test_propose_repairs_from_audit_diagnostics_options_match_repair_options():
    """preserve_intent and challenge_intent options are represented."""
    diag = _audit_diag()
    proposals = propose_repairs_from_audit_diagnostics([diag])
    option_ids = [o.id for o in proposals[0].options]
    assert any("preserve" in oid for oid in option_ids)
    assert any("challenge" in oid for oid in option_ids)


def test_write_audit_repair_proposals_uses_new_generation_function(tmp_path):
    """write_audit_repair_proposals still works correctly after refactor (regression)."""
    import yaml
    from auteur.structure.proposal_resolution import write_audit_repair_proposals

    diag = _audit_diag("carriers.location_teleportation")
    write_audit_repair_proposals(tmp_path, [diag])

    proposal_files = list((tmp_path / "structure" / "proposals").glob("repair_*.yaml"))
    assert len(proposal_files) == 1
    data = yaml.safe_load(proposal_files[0].read_text(encoding="utf-8"))
    assert data["source_domain"] == "bible_audit"
    assert data["source_rule"] == "carriers.location_teleportation"


def test_proposal_resolution_module_has_no_proposal_option_import():
    """After refactor, proposal_resolution should not define proposal-building logic.
    It should import the generation function rather than re-implement it.
    This is a structural guard — if this test breaks, generation crept back in."""
    import inspect
    import auteur.structure.proposal_resolution as resolution_module

    source = inspect.getsource(resolution_module)
    # The generation function should be imported, not defined here
    assert "def propose_repairs_from_audit_diagnostics" not in source, (
        "Generation function should live in proposal_generation.py, not resolution"
    )
