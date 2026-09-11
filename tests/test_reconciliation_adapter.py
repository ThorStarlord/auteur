from pathlib import Path

import pytest
import yaml

from auteur.decision.adapters.reconciliation_adapter import ReconciliationAdapter
from auteur.decision.models import AuthorDecision, DecisionReadiness, EvidenceClassification, EvidenceType
from auteur.decision.service import DecisionWorkspaceService


def _write_proposal(project: Path, *, target: str = "scene-1", body: str | None = None) -> Path:
    proposal_dir = project / "chapters" / "01" / "expression" / "reconciliation" / "proposals"
    proposal_dir.mkdir(parents=True, exist_ok=True)
    path = proposal_dir / "proposal-1.yaml"
    if body is not None:
        path.write_text(body, encoding="utf-8")
        return path
    proposal = {
        "proposal_id": "proposal-1",
        "target_artifact_id": target,
        "conflicts": [
            {
                "id": "c1",
                "classification": "creative",
                "description": "Choose one",
                "blocking": True,
                "options": ["a", "b"],
            }
        ],
    }
    path.write_text(yaml.safe_dump(proposal), encoding="utf-8")
    return path


def test_load_proposals_reads_expression_reconciliation_store(tmp_path: Path) -> None:
    (tmp_path / ".auteur").mkdir()
    _write_proposal(tmp_path)

    loaded = ReconciliationAdapter(tmp_path).load_proposals("scene-1")

    assert [item["proposal_id"] for item in loaded] == ["proposal-1"]


def test_load_proposals_fails_closed_on_malformed_evidence(tmp_path: Path) -> None:
    (tmp_path / ".auteur").mkdir()
    _write_proposal(tmp_path, body="[")

    with pytest.raises(ValueError, match="reconciliation proposal"):
        ReconciliationAdapter(tmp_path).load_proposals("scene-1")


def test_decision_enrichment_uses_expression_reconciliation_evidence(tmp_path: Path) -> None:
    (tmp_path / ".auteur").mkdir()
    _write_proposal(tmp_path)
    service = DecisionWorkspaceService(tmp_path)
    decision = AuthorDecision(
        decision_id="decision-1",
        project=str(tmp_path),
        chapter_index=1,
        target_artifact_id="scene-1",
        readiness=DecisionReadiness.NEEDS_CANDIDATE,
    )

    enriched = service._enrich_decision(decision)

    conflicts = [item for item in enriched.evidence if item.evidence_type == EvidenceType.RECONCILIATION_CONFLICT]
    assert len(conflicts) == 1
    assert conflicts[0].claim == "Choose one"
    assert conflicts[0].classification == EvidenceClassification.AUTHOR_CHOICE
