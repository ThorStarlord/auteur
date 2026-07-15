from auteur.reasoning import (
    CriticRegistry,
    ReasoningRuntime,
    RuntimeRequest,
    RuntimeStatus,
    register_setup_payoff_critic,
)


def _series():
    return {
        "book_plans": [{"book_number": 1}, {"book_number": 2}],
        "narrative_setups": [{
            "id": "hidden_key", "book_introduced": 1,
            "expected_payoff_by_book": 1, "status": "unresolved",
        }],
    }


def test_setup_payoff_produces_competing_hypotheses_and_alternatives(tmp_path):
    registry = CriticRegistry()
    register_setup_payoff_critic(registry)
    runtime = ReasoningRuntime(registry, tmp_path / "reports")
    result = runtime.run(RuntimeRequest(
        critic_ids=("structure.setup_payoff",),
        inputs={"series": _series(), "scope": "standalone"},
    ))
    assert result.outcomes[0].status is RuntimeStatus.SUCCESS
    import json
    report = json.loads((tmp_path / "reports" / f"{result.outcomes[0].report_id}.json").read_text())
    assert len(report["hypotheses"]) == 4
    assert len(report["recommendations"]) == 4


def test_setup_payoff_skips_future_series_carryover(tmp_path):
    registry = CriticRegistry()
    register_setup_payoff_critic(registry)
    runtime = ReasoningRuntime(registry, tmp_path / "reports")
    result = runtime.run(RuntimeRequest(
        critic_ids=("structure.setup_payoff",),
        inputs={"series": {"book_plans": [{"book_number": 1}], "narrative_setups": [{
            "id": "future", "book_introduced": 1, "expected_payoff_by_book": 2,
            "status": "unresolved",
        }]}, "scope": "series"},
    ))
    assert result.outcomes[0].status is RuntimeStatus.SUCCESS
    import json
    report = json.loads((tmp_path / "reports" / f"{result.outcomes[0].report_id}.json").read_text())
    assert report["observations"] == []
