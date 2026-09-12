from auteur.state_validity import ArtifactValidity, StateValidity
from auteur.decision.adapters.reasoning_adapter import ReasoningAdapter


def test_malformed_validity_is_blocking_and_has_explicit_evidence_freshness() -> None:
    result = StateValidity.malformed("proposal.yaml", "invalid YAML")

    assert result.status is ArtifactValidity.MALFORMED
    assert result.blocking is True
    assert result.evidence_freshness.value == "unknown"
    assert "invalid YAML" in result.reason


def test_reasoning_probe_reports_missing_run_as_missing(tmp_path) -> None:
    result = ReasoningAdapter(tmp_path).probe_validity(1)

    assert result.status is ArtifactValidity.MISSING
    assert result.blocking is True
