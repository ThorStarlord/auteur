import json

import pytest

from auteur.reasoning.runtime import (
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
