from pathlib import Path

from auteur.learning.models import LearningEvent
from auteur.learning.service import LearningService
from auteur.reasoning.reports import build_reasoning_report
from auteur.story_design_packs.tutor import decision_card_from_reasoning_report
from auteur.series.context_reconstruction import reconstruct_series_context
from auteur.simulation.narrative_counterfactual import project_counterfactual


def test_reasoning_report_has_evidence_and_noncanonical_status():
    report = build_reasoning_report(
        subject="promise-1",
        rule="setup_payoff.overdue",
        message="A promise is overdue.",
        evidence={"setup-1": "expected_by=3"},
        recommendations=["link a payoff"],
        hypotheses=["the payoff is missing", "the promise is intentionally deferred"],
    )
    assert report.evidence[0].source_artifact == "setup-1"
    assert report.status == "derived"
    assert report.confidence_method == "deterministic_rule"
    assert decision_card_from_reasoning_report(report).authority_status == "DERIVED / NOT CANON"


def test_counterfactual_keeps_preserved_and_unknown_separate():
    result = project_counterfactual(
        baseline_hash="base",
        changed_fact="book-1-villain-survives",
        direct_dependents={"book-2-alliance": ["edge-1"]},
        preserved=["corporate-conspiracy"],
    )
    assert result.consequences[0].classification == "DERIVED"
    assert result.preserved == ("corporate-conspiracy",)
    assert result.unknowns
    assert not result.promoted


def test_context_reconstruction_is_bounded_and_learning_reduces_scaffolding(tmp_path: Path):
    snapshot = reconstruct_series_context([
        {"item_id": "promise-1", "kind": "promise", "summary": "The debt must be paid.", "book_number": 1, "status": "open", "dependent_books": [3]},
        {"item_id": "unrelated", "kind": "theme", "summary": "Unrelated", "book_number": 1, "status": "resolved"},
    ], target_book=3)
    assert [item.item_id for item in snapshot.items] == ["promise-1"]
    assert snapshot.unresolved_promises == ["promise-1"]
    service = LearningService(tmp_path)
    assert service.scaffolding("causality") == "teach"
    service.record(LearningEvent(concept="causality", event="practiced", source_ref="card-1"))
    assert service.scaffolding("causality") == "explain"
    service.record(LearningEvent(concept="causality", event="demonstrated_independently", source_ref="transfer-1"))
    assert service.scaffolding("causality") == "recommend"
