"""Tests for auteur.cli_formatters — the I/O-free formatting layer."""

from __future__ import annotations

from pathlib import Path

from auteur.cli_formatters import (
    format_accept,
    format_audit,
    format_cartographer_compile,
    format_cartographer_compile_success,
    format_cartographer_validate,
    format_cartographer_validate_success,
    format_diagnostics,
    format_draft,
    format_draft_not_accepted,
    format_error,
    format_identity_compile,
    format_identity_compile_success,
    format_identity_validate,
    format_identity_validate_success,
    format_init,
    format_plan,
    format_retry,
    format_structure_apply,
    format_structure_diagnose,
    format_structure_generate,
    format_structure_propose_repairs,
)
from auteur.cli_handlers import (
    AcceptResultData,
    AuditResultData,
    CompileBlueprintData,
    DraftResultData,
    HandlerResult,
    IdentityValidateData,
    PlanData,
)
from auteur.structure.diagnostics import DiagnosticLayer, StructureDiagnostic


# ---------------------------------------------------------------------------
# format_error
# ---------------------------------------------------------------------------


def test_format_error_default():
    msg = format_error("something broke")
    assert msg == "Error: something broke"


def test_format_error_with_custom_exit_code():
    msg = format_error("file not found", exit_code=2)
    assert msg == "Error: file not found"


# ---------------------------------------------------------------------------
# format_init
# ---------------------------------------------------------------------------


def test_format_init_success():
    result = HandlerResult.success()
    assert format_init(result) is None


def test_format_init_failure():
    result = HandlerResult.failure("blueprint not found")
    msg = format_init(result)
    assert msg == "Error: blueprint not found"


# ---------------------------------------------------------------------------
# format_plan
# ---------------------------------------------------------------------------


def test_format_plan_success():
    data = PlanData(system_prompt="You are an author.", user_message="Write chapter 1.")
    result = HandlerResult.success(data=data)
    msg = format_plan(result)
    assert msg is not None
    assert "SYSTEM PROMPT" in msg
    assert "You are an author." in msg
    assert "USER MESSAGE" in msg
    assert "Write chapter 1." in msg


def test_format_plan_failure():
    result = HandlerResult.failure("plan failed")
    assert format_plan(result) == "Error: plan failed"


# ---------------------------------------------------------------------------
# format_structure_diagnose
# ---------------------------------------------------------------------------


def test_format_structure_diagnose_success():
    diag1 = {"severity": "error", "rule": "story_engine.missing", "message": "No story engine found", "evidence": []}
    diag2 = {"severity": "warning", "rule": "theme.motifs_unrepresented", "message": "Motifs not tied to engine", "evidence": ["motif: phoenix"]}
    data = {
        "diagnostics": [diag1, diag2],
        "errors": [diag1],
        "warnings": [diag2],
        "infos": [],
    }
    result = HandlerResult.success(data=data)
    msg = format_structure_diagnose(result)
    assert msg is not None
    assert "[ERROR] story_engine.missing: No story engine found" in msg
    assert "[WARNING] theme.motifs_unrepresented: Motifs not tied to engine" in msg
    assert "       motif: phoenix" in msg
    assert "2 total: 1 error(s), 1 warning(s), 0 info" in msg
    assert "---" in msg


def test_format_structure_diagnose_failure():
    result = HandlerResult.failure("blueprint invalid")
    assert format_structure_diagnose(result) == "Error: blueprint invalid"


# ---------------------------------------------------------------------------
# format_structure_propose_repairs
# ---------------------------------------------------------------------------


def test_format_structure_propose_repairs_success():
    data = {
        "diagnostic_count": 3,
        "proposal_count": 2,
        "proposal_paths": [Path("/tmp/p1.yaml"), Path("/tmp/p2.yaml")],
    }
    result = HandlerResult.success(data=data)
    msg = format_structure_propose_repairs(result)
    import json
    parsed = json.loads(msg)
    assert parsed["diagnostic_count"] == 3
    assert parsed["proposal_count"] == 2
    assert parsed["proposal_paths"] == [str(Path("/tmp/p1.yaml")), str(Path("/tmp/p2.yaml"))]
def test_format_structure_propose_repairs_failure():
    result = HandlerResult.failure("invalid blueprint")
    assert format_structure_propose_repairs(result) == "Error: invalid blueprint"


# ---------------------------------------------------------------------------
# format_structure_apply
# ---------------------------------------------------------------------------


def test_format_structure_apply_success():
    data = {
        "target_path": "/tmp/output/blueprint.yaml",
        "in_place": False,
        "selected_option_id": "opt_1",
    }
    result = HandlerResult.success(data=data)
    msg = format_structure_apply(result)
    import json
    parsed = json.loads(msg)
    assert parsed["target_path"] == "/tmp/output/blueprint.yaml"
    assert parsed["in_place"] is False
    assert parsed["selected_option_id"] == "opt_1"


def test_format_structure_apply_failure():
    result = HandlerResult.failure("no option selected")
    assert format_structure_apply(result) == "Error: no option selected"


# ---------------------------------------------------------------------------
# format_structure_generate
# ---------------------------------------------------------------------------


def test_format_structure_generate_symptom_diagnosis():
    data = {
        "symptom": "midpoint feels flat",
        "blueprint": "/tmp/blueprint.yaml",
        "diagnoses": [{"rule": "structure.midpoint_weak", "confidence": 0.8}],
        "is_diagnostics": True,
    }
    result = HandlerResult.success(data=data)
    msg = format_structure_generate(result)
    import json
    parsed = json.loads(msg)
    assert parsed["symptom"] == "midpoint feels flat"
    assert len(parsed["diagnoses"]) == 1


def test_format_structure_generate_diagnostics():
    data = {
        "is_diagnostics": True,
        "diagnostics": [{"severity": "error", "message": "engine missing", "evidence": []}],
    }
    result = HandlerResult.success(data=data)
    msg = format_structure_generate(result)
    assert "ERROR: engine missing" in msg


def test_format_structure_generate_proposal():
    data = {
        "is_diagnostics": False,
        "proposal_dict": {"main_thread": {"want": "story"}},
    }
    result = HandlerResult.success(data=data)
    msg = format_structure_generate(result)
    import json
    parsed = json.loads(msg)
    assert parsed["main_thread"]["want"] == "story"


def test_format_structure_generate_failure():
    result = HandlerResult.failure("generation failed")
    assert format_structure_generate(result) == "Error: generation failed"

# format_draft
# ---------------------------------------------------------------------------


def test_format_draft_accepted():
    data = DraftResultData(
        chapter_index=1,
        accepted=True,
        iterations=2,
        final_path=Path("/proj/chapters/01/final.md"),
        total_input_tokens=100,
        total_output_tokens=50,
    )
    result = HandlerResult.success(data=data)
    msg = format_draft(result)
    assert msg is not None
    assert "ACCEPTED on iteration 2" in msg
    assert "final.md:" in msg and "final.md" in msg
    assert "tokens: 100 in / 50 out" in msg


def test_format_draft_not_accepted():
    data = DraftResultData(
        chapter_index=1,
        accepted=False,
        iterations=3,
        final_path=None,
        total_input_tokens=200,
        total_output_tokens=100,
    )
    result = HandlerResult(exit_code=2, data=data)
    msg = format_draft(result)
    assert msg is None  # callback to caller for extras

    not_accepted_msg = format_draft_not_accepted(result, "/my_project", 1)
    assert not_accepted_msg is not None
    assert "NOT ACCEPTED after 3 iterations" in not_accepted_msg
    assert "auteur accept /my_project 1" in not_accepted_msg
    assert "auteur retry /my_project 1" in not_accepted_msg


def test_format_draft_conflict():
    data = DraftResultData(
        chapter_index=1,
        accepted=False,
        iterations=1,
        conflict_report="incompatible inputs",
    )
    result = HandlerResult(exit_code=3, data=data)
    msg = format_draft(result)
    assert msg is not None
    assert "CONFLICT: incompatible inputs" in msg


def test_format_draft_handler_error():
    result = HandlerResult.failure("project not found")
    msg = format_draft(result)
    assert msg == "Error: project not found"


# ---------------------------------------------------------------------------
# format_accept
# ---------------------------------------------------------------------------


def test_format_accept_success():
    data = AcceptResultData(chapter_index=1, latest_draft_name="draft_v3.md")
    result = HandlerResult.success(data=data)
    msg = format_accept(result)
    assert msg == "Accepted draft_v3.md as final.md for chapter 1."


def test_format_accept_failure():
    result = HandlerResult.failure("no draft found")
    assert format_accept(result) == "Error: no draft found"


# ---------------------------------------------------------------------------
# format_retry
# ---------------------------------------------------------------------------


def test_format_retry_success():
    data = DraftResultData(
        chapter_index=1,
        accepted=True,
        iterations=1,
        final_path=Path("/proj/chapters/01/final.md"),
        total_input_tokens=50,
        total_output_tokens=25,
    )
    result = HandlerResult.success(data=data)
    msg = format_retry(result)
    assert msg is not None
    assert "ACCEPTED on iteration 1" in msg


# ---------------------------------------------------------------------------
# format_audit
# ---------------------------------------------------------------------------


def _make_diag(
    rule: str,
    message: str,
    severity: str = "error",
    layer: DiagnosticLayer = DiagnosticLayer.CARRIERS,
) -> StructureDiagnostic:
    from auteur.structure.diagnostics import DiagnosticSeverity, RepairOptions
    return StructureDiagnostic(
        rule=rule,
        message=message,
        severity=DiagnosticSeverity(severity),
        layer=layer,
        evidence=["location: Throne Room", "location: Dungeon"],
        repair_options=RepairOptions(
            preserve_intent=["Add a transition scene"],
            challenge_intent=["Remove the teleportation"],
        ),
    )


def test_format_audit_with_diagnostics():
    diag = _make_diag("carriers.location_teleportation", "Aldric teleported")
    data = AuditResultData(
        diagnostics=[diag],
        error_count=1,
        warning_count=0,
        artifact_path=Path("/proj/structure/diagnostics/audit_report.json"),
    )
    result = HandlerResult(exit_code=1, data=data)
    msg = format_audit(result)
    assert msg is not None
    assert "Layer 6" in msg
    assert "[ERROR] carriers.location_teleportation: Aldric teleported" in msg
    assert "Found 1 unresolved error(s), 0 unresolved warning(s)." in msg
    assert "Audit report written to" in msg


def test_format_audit_no_issues():
    data = AuditResultData(diagnostics=[], error_count=0, warning_count=0)
    result = HandlerResult.success(data=data)
    msg = format_audit(result)
    assert msg == "No structural or lore issues detected."


def test_format_audit_all_resolved():
    data = AuditResultData(diagnostics=[], error_count=1, warning_count=0)
    result = HandlerResult(exit_code=0, data=data)
    msg = format_audit(result)
    assert msg == "All previously detected issues have been resolved."


def test_format_audit_with_resolved_proposals():
    diag = _make_diag("carriers.location_teleportation", "Aldric teleported")
    data = AuditResultData(
        diagnostics=[diag],
        error_count=1,
        warning_count=0,
        resolved_proposal_count=2,
    )
    result = HandlerResult(exit_code=1, data=data)
    msg = format_audit(result)
    assert msg is not None
    assert "2 previously resolved proposals were skipped" in msg


def test_format_audit_failure():
    result = HandlerResult.failure("blueprint not found")
    assert format_audit(result) == "Error: blueprint not found"


# ---------------------------------------------------------------------------
# format_identity_validate
def _make_identity_diag(
    rule: str,
    message: str,
    severity: str = "error",
) -> StructureDiagnostic:
    from auteur.structure.diagnostics import DiagnosticSeverity, DiagnosticLayer, RepairOptions
    return StructureDiagnostic(
        rule=rule,
        message=message,
        severity=DiagnosticSeverity(severity),
        layer=DiagnosticLayer.THEME,
        evidence=[],
        repair_options=RepairOptions(preserve_intent=[], challenge_intent=[]),
    )


def test_format_identity_validate_with_errors():
    diag = _make_identity_diag("identity.missing_title", "Title is required")
    data = IdentityValidateData(
        diagnostics=[diag],
        has_error=True,
        report={"diagnostics": [diag.model_dump(mode="json")]},
    )
    result = HandlerResult.success(data=data)
    msg = format_identity_validate(result)
    assert msg is not None
    assert "Rule: identity.missing_title" in msg
    assert "Message: Title is required" in msg


def test_format_identity_validate_success():
    identity_path = "/tmp/story_identity.yaml"
    data = IdentityValidateData(diagnostics=[], has_error=False, report={"diagnostics": []})
    result = HandlerResult.success(data=data)
    assert format_identity_validate(result) is None
    msg = format_identity_validate_success(result, identity_path)
    assert msg == "Success: StoryIdentity /tmp/story_identity.yaml is valid."


def test_format_identity_validate_with_warnings():
    diag = _make_identity_diag("identity.minimal_motifs", "Only 1 motif", severity="warning")
    data = IdentityValidateData(
        diagnostics=[diag],
        has_error=False,
        report={"diagnostics": [diag.model_dump(mode="json")]},
    )
    result = HandlerResult.success(data=data)
    assert format_identity_validate(result) is not None
    msg = format_identity_validate_success(result, "/tmp/identity.yaml")
    assert "with warnings" in msg


def test_format_identity_validate_failure():
    result = HandlerResult.failure("parse error")
    assert format_identity_validate(result) == "Error: parse error"


# ---------------------------------------------------------------------------
# format_identity_compile
# ---------------------------------------------------------------------------


def test_format_identity_compile_success():
    result = HandlerResult.success(data=None)
    assert format_identity_compile(result) is None
    msg = format_identity_compile_success("/src/identity.yaml", "/dst/blueprint.yaml")
    assert msg == "Success: compiled identity /src/identity.yaml to blueprint /dst/blueprint.yaml"


def test_format_identity_compile_failure():
    result = HandlerResult.failure("validation errors")
    assert format_identity_compile(result) == "Error: validation errors"


# ---------------------------------------------------------------------------
# format_cartographer_compile
# ---------------------------------------------------------------------------


def test_format_cartographer_compile_success():
    result = HandlerResult.success()
    assert format_cartographer_compile(result) is None
    msg = format_cartographer_compile_success("/tmp/outline.yaml")
    assert msg == "Success: compiled outline into /tmp/outline.yaml"


def test_format_cartographer_compile_failure():
    result = HandlerResult.failure("llm failed")
    assert format_cartographer_compile(result) == "Error: llm failed"


# ---------------------------------------------------------------------------
# format_cartographer_validate
# ---------------------------------------------------------------------------


def test_format_cartographer_validate_success():
    result = HandlerResult.success()
    assert format_cartographer_validate(result) is None
    msg = format_cartographer_validate_success("/tmp/outline.yaml")
    assert msg == "Success: outline /tmp/outline.yaml is valid."


def test_format_cartographer_validate_failure():
    result = HandlerResult.failure("validation failed")
    assert format_cartographer_validate(result) == "Error: validation failed"


# ---------------------------------------------------------------------------
# format_diagnostics (shared helper)
# ---------------------------------------------------------------------------


def test_format_diagnostics_with_evidence():
    diagnostics = [
        {"severity": "error", "rule": "engine.missing", "message": "No engine", "evidence": ["need engine"]},
        {"severity": "warning", "rule": "theme.weak", "message": "Theme weak", "evidence": []},
    ]
    msg = format_diagnostics(diagnostics, artifact_path="/tmp/report.json")
    assert "[ERROR] engine.missing: No engine" in msg
    assert "       need engine" in msg
    assert "[WARNING] theme.weak: Theme weak" in msg
    assert "Diagnostics written to /tmp/report.json" in msg


def test_format_diagnostics_no_evidence():
    diagnostics = [{"severity": "info", "rule": "structure.ok", "message": "All good", "evidence": []}]
    msg = format_diagnostics(diagnostics)
    assert "[INFO] structure.ok: All good" in msg
    assert "Diagnostics written" not in msg


# ---------------------------------------------------------------------------
# Formatting of error HandlerResult always returns error string
# ---------------------------------------------------------------------------


def test_error_on_result_returns_error_string():
    """format_* functions on a result with error should return a format_error string."""
    result = HandlerResult.failure("generic failure")
    for fmt_func in [
        format_init,
        format_plan,
        format_structure_diagnose,
        format_structure_propose_repairs,
        format_structure_apply,
        format_structure_generate,
        format_accept,
        format_identity_validate,
        format_identity_compile,
        format_cartographer_compile,
        format_cartographer_validate,
    ]:
        msg = fmt_func(result)
        assert msg is not None
        assert msg.startswith("Error: generic failure"), f"{fmt_func.__name__} returned {msg!r}"


def test_format_draft_on_error_result():
    """format_draft/format_retry on an error result with no data returns error string."""
    result = HandlerResult.failure("draft failed")
    msg = format_draft(result)
    assert msg is not None
    assert msg.startswith("Error: draft failed")
    msg2 = format_retry(result)
    assert msg2 is not None
    assert msg2.startswith("Error: draft failed")
