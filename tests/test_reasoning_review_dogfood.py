from auteur.reasoning import synthesize_reports


def test_review_prioritizes_high_impact_issue_over_many_low_impact_findings():
    review = synthesize_reports([
        {"report_id": "high", "critic_id": "setup", "source_snapshot": {"story": 1},
         "findings": [{"rule": "payoff", "severity": "error", "artifact_id": "setup-1"}],
         "claims": [{"claim_id": "claim-1", "statement": "Payoff is unresolved"}],
         "evidence": [{"evidence_id": "one"}]},
        {"report_id": "low", "critic_id": "structure", "source_snapshot": {"story": 1},
         "findings": [{"rule": f"minor-{i}", "severity": "warning"} for i in range(5)],
         "claims": [{"claim_id": f"claim-{i+1}", "statement": f"Minor issue {i}"} for i in range(5)],
         "evidence": [{"evidence_id": f"e{i}"} for i in range(5)]},
    ], current_inputs={"story": {"revision": 1}})
    top = next(group for group in review["groups"] if group["group_id"] == review["priorities"][0]["group_id"])
    assert top["severity_score"] == 3
    assert top["next_action"]


def test_review_exposes_clean_area_and_stale_report():
    review = synthesize_reports([
        {"report_id": "clean", "critic_id": "structure", "source_snapshot": {"story": 1},
         "findings": [], "claims": [], "evidence": []},
    ], current_inputs={"story": {"revision": 2}})
    assert review["groups"] == []
    assert review["freshness"]["status"] == "stale"
