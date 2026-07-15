import json

from auteur.reasoning import synthesize_reports


def _reports():
    return [
        {"report_id": "r1", "critic_id": "structure.blueprint", "critic_version": "1",
         "source_snapshot": {"blueprint": 1},
         "claims": [{"claim_id": "c1", "statement": "shared concern"}],
         "evidence": [{"evidence_id": "e1"}],
         "confidence": {"method": "deterministic_analyzer"}},
        {"report_id": "r2", "critic_id": "structure.setup_payoff", "critic_version": "1",
         "source_snapshot": {"blueprint": 1},
         "claims": [{"claim_id": "c2", "statement": "different concern"}],
         "evidence": [{"evidence_id": "e2"}],
         "confidence": {"method": "deterministic_analyzer"}},
    ]


def test_synthesis_preserves_sources_and_conflicting_claims(tmp_path):
    reports = _reports()
    review = synthesize_reports(reports, report_dir=tmp_path / "reviews",
                                current_inputs={"blueprint": {"revision": 1}})
    assert review["status"] == "derived"
    assert len(review["source_reports"]) == 2
    assert review["confidence"]["method"] == "not_combined"
    assert json.loads((tmp_path / "reviews" / f"{review['review_id']}.json").read_text()) == review
    assert reports[0]["claims"][0]["statement"] == "shared concern"


def test_synthesis_marks_stale_source_report_and_is_deterministic():
    reports = _reports()
    first = synthesize_reports(reports, current_inputs={"blueprint": {"revision": 2}})
    second = synthesize_reports(reports, current_inputs={"blueprint": {"revision": 2}})
    assert first == second
    assert first["freshness"]["status"] == "stale"
    assert first["freshness"]["stale_reports"] == ["r1", "r2"]
