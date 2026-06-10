"""Tests for auteur.cli_serializers — extract file writes from cli.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from auteur.cli_handlers import (
    CompileBlueprintData,
    HandlerResult,
    IdentityValidateData,
    RecommendOpinionatedData,
    RecommendOpenEndedData,
)
from auteur.cli_serializers import (
    serialize_audit,
    serialize_compile_blueprint,
    serialize_identity_openended,
    serialize_identity_opinionated,
    serialize_identity_promote,
    serialize_identity_validate,
    serialize_structure_diagnose,
    serialize_structure_generate_text,
    serialize_structure_propose_repairs,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def diagnose_success() -> HandlerResult:
    return HandlerResult.success(
        data={
            "diagnostics": [
                {"rule": "test.rule", "severity": "error", "message": "test error"}
            ],
            "errors": [{"rule": "test.rule", "severity": "error", "message": "test error"}],
            "warnings": [],
            "infos": [],
        }
    )


@pytest.fixture
def failure_result() -> HandlerResult:
    return HandlerResult.failure("something went wrong")


# ---------------------------------------------------------------------------
# serialize_structure_diagnose
# ---------------------------------------------------------------------------


def test_structure_diagnose_writes_valid_json(diagnose_success: HandlerResult, tmp_path: Path) -> None:
    path = serialize_structure_diagnose(diagnose_success, tmp_path / "report.json")
    assert path is not None
    assert path.exists()
    assert path.read_bytes()[-1:] == b"\n"  # trailing newline
    data = json.loads(path.read_text())
    assert "diagnostics" in data
    assert data["diagnostics"][0]["rule"] == "test.rule"


def test_structure_diagnose_creates_parent_dirs(diagnose_success: HandlerResult, tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b" / "report.json"
    path = serialize_structure_diagnose(diagnose_success, nested)
    assert path == nested
    assert nested.exists()


def test_structure_diagnose_returns_none_on_failure(failure_result: HandlerResult, tmp_path: Path) -> None:
    result = serialize_structure_diagnose(failure_result, tmp_path / "report.json")
    assert result is None


# ---------------------------------------------------------------------------
# serialize_structure_propose_repairs
# ---------------------------------------------------------------------------


class _MockProposal:
    """Minimal mock matching the StructureProposal interface used by the serializer."""
    def __init__(self, proposal_id: str) -> None:
        self.proposal_id = proposal_id

    def model_dump(self, mode: str = "json") -> dict:
        return {"proposal_id": self.proposal_id, "mode": mode}


def test_propose_repairs_writes_report_and_proposals(tmp_path: Path) -> None:
    result = HandlerResult.success(
        data={
            "diagnostics": [{"rule": "r1", "severity": "warning", "message": "warn"}],
            "proposals": [_MockProposal("prop_a"), _MockProposal("prop_b")],
            "diagnostic_count": 1,
            "proposal_count": 2,
        }
    )
    diag_dir = tmp_path / "diagnostics"
    prop_dir = tmp_path / "proposals"

    report_path = serialize_structure_propose_repairs(result, diag_dir, prop_dir)
    assert report_path == diag_dir / "structure_report.json"
    assert report_path.exists()

    # Verify report content
    report = json.loads(report_path.read_text())
    assert report["diagnostics"][0]["rule"] == "r1"

    # Verify proposal files
    prop_a = prop_dir / "prop_a.yaml"
    prop_b = prop_dir / "prop_b.yaml"
    assert prop_a.exists()
    assert prop_b.exists()
    assert yaml.safe_load(prop_a.read_text())["proposal_id"] == "prop_a"

    # Verify paths injected into result.data
    assert result.data["report_path"] == str(report_path)
    assert len(result.data["proposal_paths"]) == 2


def test_propose_repairs_returns_none_on_failure(failure_result: HandlerResult, tmp_path: Path) -> None:
    result = serialize_structure_propose_repairs(failure_result, tmp_path, tmp_path)
    assert result is None


# ---------------------------------------------------------------------------
# serialize_structure_generate_text
# ---------------------------------------------------------------------------


def test_generate_text_writes_content(tmp_path: Path) -> None:
    p = tmp_path / "out.txt"
    result = serialize_structure_generate_text("hello world", p)
    assert result == p
    assert p.read_text() == "hello world\n"


def test_generate_text_creates_parent_dirs(tmp_path: Path) -> None:
    p = tmp_path / "x" / "y" / "out.txt"
    result = serialize_structure_generate_text("content", p)
    assert result == p
    assert p.exists()


# ---------------------------------------------------------------------------
# serialize_identity_validate
# ---------------------------------------------------------------------------


def test_identity_validate_writes_valid_json(tmp_path: Path) -> None:
    report_dict = {"valid": True, "checks": [{"rule": "r1", "passed": True}]}
    result = HandlerResult.success(data=IdentityValidateData(
        diagnostics=[], has_error=False, report=report_dict,
    ))
    path = serialize_identity_validate(result, tmp_path)
    assert path == tmp_path / "validation_report.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["valid"] is True


def test_identity_validate_creates_parent_dirs(tmp_path: Path) -> None:
    result = HandlerResult.success(data=IdentityValidateData(
        diagnostics=[], has_error=False, report={"ok": True},
    ))
    nested = tmp_path / "a" / "b"
    path = serialize_identity_validate(result, nested)
    assert path == nested / "validation_report.json"
    assert path.exists()


def test_identity_validate_returns_none_on_failure(failure_result: HandlerResult, tmp_path: Path) -> None:
    result = serialize_identity_validate(failure_result, tmp_path)
    assert result is None


# ---------------------------------------------------------------------------
# serialize_identity_opinionated
# ---------------------------------------------------------------------------


class _MockIdentity:
    def __init__(self, title: str = "Test Story") -> None:
        self.title = title

    def to_yaml(self, path: str | Path) -> None:
        Path(path).write_text(f"title: {self.title}\n", encoding="utf-8")

    @property
    def confidence(self) -> float:
        return 0.95


class _MockOpinionatedData(RecommendOpinionatedData):
    pass


def test_identity_opinionated_writes_yaml(tmp_path: Path) -> None:
    identity = _MockIdentity("My Story")
    data = _MockOpinionatedData(identity=identity, warnings=[])
    out = tmp_path / "identity.yaml"
    result = serialize_identity_opinionated(data, out)
    assert result == out
    assert out.read_text() == "title: My Story\n"


def test_identity_opinionated_creates_parent_dirs(tmp_path: Path) -> None:
    identity = _MockIdentity("Test")
    data = _MockOpinionatedData(identity=identity, warnings=[])
    nested = tmp_path / "deep" / "sub" / "id.yaml"
    result = serialize_identity_opinionated(data, nested)
    assert result == nested
    assert nested.exists()


# ---------------------------------------------------------------------------
# serialize_identity_openended
# ---------------------------------------------------------------------------


class _MockCandidate:
    def __init__(self, candidate_id: str) -> None:
        self.candidate_id = candidate_id
        self.yaml_content = f"id: {candidate_id}\n"
        self.candidate = _MockCandidateMeta(candidate_id)

    def __repr__(self) -> str:
        return f"MockCandidate({self.candidate_id})"


class _MockCandidateMeta:
    def __init__(self, candidate_id: str) -> None:
        self.path = ""

    def __repr__(self) -> str:
        return f"MockCandidateMeta({self.path})"


class _MockRecSet:
    def __init__(self) -> None:
        self.source_input_path = ""
        self.candidates: list = []

    def model_dump(self, mode: str = "json") -> dict:
        return {
            "source_input_path": self.source_input_path,
            "candidates": [p.path for p in self.candidates],
        }


class _MockOpenEndedData(RecommendOpenEndedData):
    pass


def test_identity_openended_writes_all_artifacts(tmp_path: Path) -> None:
    cand1 = _MockCandidate("candidate_1")
    cand2 = _MockCandidate("candidate_2")
    rec_set = _MockRecSet()
    rec_set.candidates = [cand1.candidate, cand2.candidate]

    data = _MockOpenEndedData(
        candidates=[cand1, cand2],
        rec_set=rec_set,
        comparison_lines=[
            "# Comparison",
            "\nSource line placeholder",
            "| A | B |",
        ],
    )
    out = tmp_path / "output" / "identity.yaml"

    written = serialize_identity_openended(data, out, premise="test premise")
    assert len(written) == 4  # 2 candidates + rec_set + comparison

    # Candidate YAMLs
    cand_dir = tmp_path / "output" / "story_identity_candidates"
    assert (cand_dir / "candidate_1.yaml").exists()
    assert (cand_dir / "candidate_1.yaml").read_text() == "id: candidate_1\n"
    assert (cand_dir / "candidate_2.yaml").exists()

    # recommendation_set.yaml
    rs_path = cand_dir / "recommendation_set.yaml"
    assert rs_path.exists()
    rs_data = yaml.safe_load(rs_path.read_text())
    assert rs_data["source_input_path"] == "test premise"

    # comparison.md
    cmp_path = cand_dir / "comparison.md"
    assert cmp_path.exists()
    cmp_text = cmp_path.read_text()
    assert "test premise" in cmp_text

    # Candidate paths updated
    assert cand1.candidate.path == str(cand_dir / "candidate_1.yaml")


def test_identity_openended_creates_parent_dirs(tmp_path: Path) -> None:
    cand = _MockCandidate("candidate_1")
    rec_set = _MockRecSet()
    rec_set.candidates = [cand.candidate]
    data = _MockOpenEndedData(
        candidates=[cand],
        rec_set=rec_set,
        comparison_lines=["# C", "", "|  |"],
    )
    nested = tmp_path / "a" / "b" / "id.yaml"
    written = serialize_identity_openended(data, nested, premise="p")
    assert len(written) >= 1
    assert all(p.exists() for p in written)


# ---------------------------------------------------------------------------
# serialize_identity_promote
# ---------------------------------------------------------------------------


def test_identity_promote_writes_yaml(tmp_path: Path) -> None:
    identity = _MockIdentity("Promoted")
    out = tmp_path / "promoted.yaml"
    result = serialize_identity_promote(identity, out)
    assert result == out
    assert out.read_text() == "title: Promoted\n"


def test_identity_promote_creates_parent_dirs(tmp_path: Path) -> None:
    identity = _MockIdentity("P")
    nested = tmp_path / "x" / "y" / "id.yaml"
    result = serialize_identity_promote(identity, nested)
    assert result == nested
    assert nested.exists()


# ---------------------------------------------------------------------------
# serialize_compile_blueprint
# ---------------------------------------------------------------------------


class _MockBlueprint:
    def __init__(self, title: str = "Test Blueprint") -> None:
        self.title = title

    def model_dump(self, mode: str = "json") -> dict:
        return {"title": self.title, "mode": mode}


def test_compile_blueprint_writes_yaml(tmp_path: Path) -> None:
    bp = _MockBlueprint("My Blueprint")
    result = HandlerResult.success(data=CompileBlueprintData(blueprint=bp))
    out = tmp_path / "blueprint.yaml"
    written = serialize_compile_blueprint(result, out)
    assert written == out
    assert out.exists()
    data = yaml.safe_load(out.read_text())
    assert data["title"] == "My Blueprint"


def test_compile_blueprint_creates_parent_dirs(tmp_path: Path) -> None:
    bp = _MockBlueprint()
    result = HandlerResult.success(data=CompileBlueprintData(blueprint=bp))
    nested = tmp_path / "a" / "b" / "out.yaml"
    written = serialize_compile_blueprint(result, nested)
    assert written == nested
    assert nested.exists()


def test_compile_blueprint_returns_none_on_failure(failure_result: HandlerResult, tmp_path: Path) -> None:
    result = serialize_compile_blueprint(failure_result, tmp_path / "out.yaml")
    assert result is None


# ---------------------------------------------------------------------------
# serialize_audit
# ---------------------------------------------------------------------------


class _MockDiagnostic:
    def __init__(self, rule: str, severity: str, message: str) -> None:
        self.rule = rule
        self.severity = severity
        self.message = message

    def model_dump(self, mode: str = "json") -> dict:
        return {"rule": self.rule, "severity": self.severity, "message": self.message}


class _MockAuditData:
    def __init__(self, diagnostics: list) -> None:
        self.diagnostics = diagnostics
        self.error_count = sum(1 for d in diagnostics if d.severity == "error")
        self.warning_count = sum(1 for d in diagnostics if d.severity == "warning")


def test_audit_writes_valid_json(tmp_path: Path) -> None:
    diag_list = [
        _MockDiagnostic("audit.1", "error", "broken"),
        _MockDiagnostic("audit.2", "warning", "caution"),
    ]
    result = HandlerResult(exit_code=1, data=_MockAuditData(diagnostics=diag_list))
    path = serialize_audit(result, tmp_path)
    assert path == tmp_path / "audit_report.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert len(data["diagnostics"]) == 2
    assert data["diagnostics"][0]["rule"] == "audit.1"


def test_audit_creates_parent_dirs(tmp_path: Path) -> None:
    result = HandlerResult(exit_code=0, data=_MockAuditData(diagnostics=[]))
    nested = tmp_path / "a" / "b"
    path = serialize_audit(result, nested)
    assert path == nested / "audit_report.json"
    assert path.exists()


def test_audit_returns_none_on_failure(failure_result: HandlerResult, tmp_path: Path) -> None:
    result = serialize_audit(failure_result, tmp_path)
    assert result is None
