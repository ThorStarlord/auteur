import json

import pytest

from auteur.reasoning.runtime import (
    ArtifactRevision,
    ArtifactRevisionAdapter,
    CriticRegistry,
    CriticSpec,
    ReasoningRuntime,
    RuntimeRequest,
    RuntimeStatus,
    register_structure_critic,
)


def _critic(critic_id="structure.blueprint", *, requires=(), run=None):
    return CriticSpec(
        critic_id=critic_id,
        version="1.0.0",
        requires=tuple(requires),
        run=run or (lambda blueprint: []),
    )


def test_registry_discovers_critic_and_rejects_duplicate():
    registry = CriticRegistry()
    registry.register(_critic())
    assert registry.discover(critic_id="structure.blueprint").critic_id == "structure.blueprint"
    with pytest.raises(ValueError, match="already registered"):
        registry.register(_critic())


def test_runtime_executes_and_persists_derived_report(tmp_path):
    registry = CriticRegistry()
    registry.register(_critic(run=lambda blueprint: [{"rule": "ok", "message": "clean"}]))
    runtime = ReasoningRuntime(registry, tmp_path / "reports")

    result = runtime.run(RuntimeRequest(critic_ids=("structure.blueprint",), inputs={"blueprint": {"id": "b1", "revision": 1}}))

    assert result.outcomes[0].status is RuntimeStatus.SUCCESS
    assert result.outcomes[0].report_id
    report = json.loads((tmp_path / "reports" / f"{result.outcomes[0].report_id}.json").read_text())
    assert report["status"] == "derived"
    assert report["critic_id"] == "structure.blueprint"
    assert report["findings"][0]["rule"] == "ok"
    assert {"observations", "evidence", "claims", "confidence", "recommendations"} <= report.keys()


def test_revision_adapter_preserves_raw_inputs_and_records_hashes(tmp_path):
    revision = ArtifactRevision(artifact_id="blueprint-1", artifact_type="blueprint",
                                revision=3, content_hash=ArtifactRevisionAdapter.hash_content({"x": 1}))
    registry = CriticRegistry()
    seen = []
    registry.register(_critic(run=lambda blueprint: seen.append(blueprint) or []))
    runtime = ReasoningRuntime(registry, tmp_path / "reports")
    request = RuntimeRequest(critic_ids=("structure.blueprint",), inputs={"blueprint": {"x": 1}},
                             source_revisions={"blueprint": revision})
    result = runtime.run(request)
    assert result.outcomes[0].status is RuntimeStatus.SUCCESS
    assert seen == [{"x": 1}]
    report = json.loads((tmp_path / "reports" / f"{result.outcomes[0].report_id}.json").read_text())
    assert report["source_snapshot"]["blueprint"]["revision"] == 3
    assert runtime.report_is_fresh(result.outcomes[0].report_id, source_revisions={"blueprint": revision})


def test_runtime_rejects_stale_input_before_execution(tmp_path):
    calls = []
    registry = CriticRegistry()
    registry.register(_critic(run=lambda blueprint: calls.append(blueprint) or []))
    runtime = ReasoningRuntime(registry, tmp_path / "reports")
    request = RuntimeRequest(critic_ids=("structure.blueprint",), inputs={"blueprint": {"id": "b1", "revision": 1}})
    request.inputs["blueprint"]["revision"] = 2

    result = runtime.run(request, expected_revisions={"blueprint": 1})

    assert result.outcomes[0].status is RuntimeStatus.STALE
    assert calls == []


def test_persisted_report_becomes_stale_after_source_revision_changes(tmp_path):
    registry = CriticRegistry()
    registry.register(_critic(run=lambda blueprint: []))
    runtime = ReasoningRuntime(registry, tmp_path / "reports")
    result = runtime.run(RuntimeRequest(critic_ids=("structure.blueprint",),
        inputs={"blueprint": {"revision": 1}}))
    report_id = result.outcomes[0].report_id
    assert runtime.report_is_fresh(report_id, {"blueprint": {"revision": 1}})
    assert not runtime.report_is_fresh(report_id, {"blueprint": {"revision": 2}})


def test_missing_and_malformed_inputs_are_explicit_failures(tmp_path):
    registry = CriticRegistry()
    registry.register(_critic(run=lambda blueprint: blueprint["required"]))
    runtime = ReasoningRuntime(registry, tmp_path / "reports")
    result = runtime.run(RuntimeRequest(critic_ids=("structure.blueprint",), inputs={}))
    assert result.outcomes[0].status is RuntimeStatus.FAILED
    assert list((tmp_path / "reports").glob("*.json")) == []


def test_deterministic_rerun_has_same_plan_and_report(tmp_path):
    registry = CriticRegistry()
    registry.register(_critic(run=lambda blueprint: [{"rule": "same"}]))
    runtime = ReasoningRuntime(registry, tmp_path / "reports")
    request = RuntimeRequest(critic_ids=("structure.blueprint",), inputs={"blueprint": {"revision": 1}})
    first = runtime.run(request)
    second = runtime.run(request)
    assert first.plan == second.plan
    assert first.outcomes[0].report_id == second.outcomes[0].report_id


def test_both_built_in_critics_run_together_without_mutating_inputs(tmp_path):
    from copy import deepcopy
    from pathlib import Path
    from auteur.blueprint import StoryBlueprint
    from auteur.reasoning import register_setup_payoff_critic, register_structure_critic

    blueprint = StoryBlueprint.from_yaml(Path("examples/sample_blueprint.yaml"))
    series = {"book_plans": [{"book_number": 1}], "narrative_setups": []}
    original_blueprint = blueprint.model_dump(mode="json")
    original_series = deepcopy(series)
    registry = CriticRegistry()
    register_structure_critic(registry)
    register_setup_payoff_critic(registry)
    runtime = ReasoningRuntime(registry, tmp_path / "reports")

    result = runtime.run(RuntimeRequest(
        critic_ids=("structure.blueprint", "structure.setup_payoff"),
        inputs={"blueprint": blueprint, "series": series, "scope": "standalone"},
    ))

    assert [outcome.status for outcome in result.outcomes] == [RuntimeStatus.SUCCESS, RuntimeStatus.SUCCESS]
    assert blueprint.model_dump(mode="json") == original_blueprint
    assert series == original_series


def test_runtime_rejects_dependency_cycle(tmp_path):
    registry = CriticRegistry()
    registry.register(_critic("a", requires=("b",)))
    registry.register(_critic("b", requires=("a",)))
    runtime = ReasoningRuntime(registry, tmp_path / "reports")

    with pytest.raises(ValueError, match="cycle"):
        runtime.plan(RuntimeRequest(critic_ids=("a",), inputs={}))


def test_builtin_structure_adapter_emits_reasoning_findings(tmp_path):
    from pathlib import Path
    from auteur.blueprint import StoryBlueprint

    blueprint = StoryBlueprint.from_yaml(Path("examples/sample_blueprint.yaml"))
    registry = CriticRegistry()
    register_structure_critic(registry)
    runtime = ReasoningRuntime(registry, tmp_path / "reports")

    result = runtime.run(RuntimeRequest(
        critic_ids=("structure.blueprint",),
        inputs={"blueprint": blueprint},
    ))

    assert result.outcomes[0].status is RuntimeStatus.SUCCESS
    report = json.loads((tmp_path / "reports" / f"{result.outcomes[0].report_id}.json").read_text())
    assert report["artifact_type"] == "reasoning_report"
