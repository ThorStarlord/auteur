from __future__ import annotations

import json
from pathlib import Path

import yaml

from auteur.cli import main
from auteur.structure import revision_reassessment
from auteur.structure.diagnostics import (
    DiagnosticLayer,
    DiagnosticSeverity,
    StructureDiagnostic,
)
from auteur.structure.proposal_models import ProposalOption, StructureProposal
from auteur.structure.revision_models import RevisionApplication, RevisionPlanState
from auteur.structure.revision_service import StructuralRevisionPlan

SAMPLE = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"
RULE = "scope.test.rule"


def _write_yaml(path: Path, model) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(model.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )


def _project(
    tmp_path: Path,
    *,
    source_domain: str = "structure",
    source_rule: str = RULE,
    application_state: str = "applied",
) -> tuple[Path, str]:
    (tmp_path / ".auteur").mkdir()
    (tmp_path / "blueprint.yaml").write_bytes(SAMPLE.read_bytes())
    (tmp_path / "story_identity.yaml").write_text("identity sentinel\n", encoding="utf-8")

    proposal = StructureProposal(
        proposal_id="reassessment_proposal",
        type="repair",
        source_rule=source_rule,
        source_domain=source_domain,
        summary="Deterministic reassessment fixture.",
        options=[
            ProposalOption(
                id="option_a",
                summary="A bounded change.",
                tradeoffs="Fixture tradeoff.",
                data={"structure": {"estimated_chapters": 48}},
            )
        ],
    )
    proposal_path = tmp_path / ".auteur" / "structure" / "proposals" / "reassessment_proposal.yaml"
    _write_yaml(proposal_path, proposal)

    plan = StructuralRevisionPlan(
        plan_id="plan_reassessment",
        project=tmp_path.name,
        proposal_path=str(proposal_path),
        state=RevisionPlanState.APPLIED,
    )
    _write_yaml(
        tmp_path / ".auteur" / "structure" / "revision-plans" / "plan_reassessment.yaml",
        plan,
    )
    application = RevisionApplication(
        application_id="app_reassessment",
        plan_id=plan.plan_id,
        state=application_state,
        confirmed=True,
    )
    _write_yaml(
        tmp_path / ".auteur" / "structure" / "revision-applications" / "app_reassessment.yaml",
        application,
    )
    return tmp_path, application.application_id


def _snapshot(project: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(project)): path.read_bytes()
        for path in sorted(project.rglob("*"))
        if path.is_file()
    }


def test_reassessment_reports_resolved_when_exact_rule_is_no_longer_emitted(
    tmp_path: Path, monkeypatch, capsys
):
    project, application_id = _project(tmp_path)
    before = _snapshot(project)
    monkeypatch.setattr(revision_reassessment, "analyze_structure", lambda _blueprint: [])

    assert main([
        "structure", "revision", "reassess", application_id,
        "--project", str(project), "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["assessment_status"] == "resolved"
    assert payload["source_rule"] == RULE
    assert payload["matching_diagnostics"] == []
    assert payload["authority_status"] == "DERIVED REASSESSMENT / READ ONLY"
    assert payload["mutates_story"] is False
    assert payload["quality_score"] is None
    assert "does not prove" in payload["claim_scope"]
    assert _snapshot(project) == before


def test_reassessment_reports_remaining_with_exact_current_diagnostic(
    tmp_path: Path, monkeypatch, capsys
):
    project, application_id = _project(tmp_path)
    diagnostic = StructureDiagnostic(
        severity=DiagnosticSeverity.WARNING,
        layer=DiagnosticLayer.SCOPE,
        rule=RULE,
        message="The exact diagnostic remains.",
        evidence=["fixture evidence"],
    )
    monkeypatch.setattr(
        revision_reassessment,
        "analyze_structure",
        lambda _blueprint: [diagnostic],
    )

    assert main([
        "structure", "revision", "reassess", application_id,
        "--project", str(project), "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["assessment_status"] == "remaining"
    assert payload["matching_diagnostics"][0]["rule"] == RULE
    assert payload["matching_diagnostics"][0]["message"] == "The exact diagnostic remains."


def test_tutor_craft_revision_is_explicitly_not_assessable(
    tmp_path: Path, monkeypatch, capsys
):
    project, application_id = _project(
        tmp_path,
        source_domain="tutor_card:card_001",
        source_rule="tutor_session:session_001:snapshot",
    )

    def should_not_run(_blueprint):
        raise AssertionError("Tutor craft reassessment must not invent diagnostic evidence")

    monkeypatch.setattr(revision_reassessment, "analyze_structure", should_not_run)
    assert main([
        "structure", "revision", "reassess", application_id,
        "--project", str(project), "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["assessment_status"] == "not_assessable"
    assert payload["matching_diagnostics"] == []
    assert "will not infer" in payload["reason"]
    assert payload["claim_scope"] == "No deterministic resolution claim is made."


def test_reassessment_rejects_non_applied_revision(tmp_path: Path, capsys):
    project, application_id = _project(tmp_path, application_state="failed")

    assert main([
        "structure", "revision", "reassess", application_id,
        "--project", str(project), "--json",
    ]) == 1

    assert "is not fully applied" in capsys.readouterr().err
