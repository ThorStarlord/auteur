"""Minimal deterministic reasoning runtime.

The runtime owns no narrative authority. It reads caller-supplied inputs and
writes only derived reports beneath the caller-supplied report directory.

Execution: independent critics run concurrently in dependency layers.
Synthesis depends on completion of all critic outcomes.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable as CallableType, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_MAX_WORKERS = 5


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class RuntimeStatus(StrEnum):
    SUCCESS = "success"
    STALE = "stale"
    INCOMPATIBLE = "incompatible"
    FAILED = "failed"
    BLOCKED = "blocked"


CriticRunner = Callable[..., list[dict[str, Any]]]


class ArtifactRevision(BaseModel):
    """Provenance snapshot carried beside a raw critic input."""

    artifact_id: str
    artifact_type: str
    revision: int | str
    content_hash: str


class ArtifactRevisionAdapter:
    """Build deterministic source snapshots without changing critic inputs."""

    @staticmethod
    def snapshot(revisions: Mapping[str, ArtifactRevision]) -> dict[str, dict[str, Any]]:
        return {key: value.model_dump(mode="json") for key, value in sorted(revisions.items())}

    @staticmethod
    def hash_content(content: Any) -> str:
        encoded = json.dumps(content, sort_keys=True, default=str, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class CriticSpec(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    critic_id: str
    version: str
    requires: tuple[str, ...] = ()
    input_keys: tuple[str, ...] = ()
    run: CriticRunner


class CriticRegistry:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], CriticSpec] = {}

    def register(self, spec: CriticSpec) -> None:
        key = (spec.critic_id, spec.version)
        if key in self._entries:
            raise ValueError(f"critic {spec.critic_id}@{spec.version} already registered")
        self._entries[key] = spec

    def discover(self, *, critic_id: str) -> CriticSpec:
        matches = [s for (identity, _), s in self._entries.items() if identity == critic_id]
        if not matches:
            raise KeyError(f"unknown critic: {critic_id}")
        return sorted(matches, key=lambda s: s.version)[-1]


def register_structure_critic(registry: CriticRegistry) -> None:
    """Register the first built-in deterministic Structure analyzer adapter."""
    from auteur.structure.analyzer import analyze_structure

    def run(*, blueprint: Any, **_: Any) -> list[dict[str, Any]]:
        diagnostics = analyze_structure(blueprint)
        return [diagnostic.model_dump(mode="json") for diagnostic in diagnostics]

    registry.register(CriticSpec(
        critic_id="structure.blueprint",
        version="1.0.0",
        input_keys=("blueprint",),
        run=run,
    ))


class RuntimeRequest(BaseModel):
    request_id: str = "request"
    critic_ids: list[str] = Field(default_factory=list)
    inputs: dict[str, Any] = Field(default_factory=dict)
    source_revisions: dict[str, ArtifactRevision] = Field(default_factory=dict)


class ExecutionPlan(BaseModel):
    plan_id: str
    request_id: str
    selected_critics: tuple[str, ...] = ()
    dependency_order: tuple[str, ...] = ()
    source_snapshot: dict[str, Any]


class ExecutionOutcome(BaseModel):
    critic_id: str
    version: str
    status: RuntimeStatus
    report_id: str | None = None
    reason: str | None = None
    error: str | None = None
    duration_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


class ExecutionResult(BaseModel):
    plan: ExecutionPlan
    outcomes: list[ExecutionOutcome]


def _stable_id(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()[:16]


def _reasoning_sections(findings: list[dict[str, Any]]) -> dict[str, Any]:
    observations = []
    evidence = []
    hypotheses = []
    evaluation = []
    claims = []
    recommendations = []
    for index, finding in enumerate(findings, 1):
        rule = finding.get("rule", "critic.finding")
        statement = finding.get("message") or finding.get("evidence") or str(finding)
        finding_id = f"finding-{index}"
        observations.append({"observation_id": finding_id, "statement": statement})
        evidence.append({"evidence_id": f"evidence-{index}", "source": rule,
                         "extraction": finding.get("evidence", statement)})
        raw_hypotheses = finding.get("hypotheses") or [statement]
        for hypothesis_index, hypothesis in enumerate(raw_hypotheses, 1):
            hypotheses.append({"hypothesis_id": f"hypothesis-{index}-{hypothesis_index}",
                               "statement": hypothesis,
                               "supporting_evidence": [f"evidence-{index}"],
                               "contradicting_evidence": []})
            evaluation.append({"hypothesis_id": f"hypothesis-{index}-{hypothesis_index}",
                               "result": "supported" if hypothesis_index == 1 else "plausible",
                               "rationale": "deterministic analyzer finding"})
        claims.append({"claim_id": f"claim-{index}", "statement": statement,
                       "hypothesis_id": f"hypothesis-{index}-1"})
        raw_recommendations = finding.get("recommendations") or [finding.get("requested_change", "Review this finding.")]
        for recommendation_index, recommendation in enumerate(raw_recommendations, 1):
            recommendations.append({"recommendation_id": f"recommendation-{index}-{recommendation_index}",
                                "statement": recommendation,
                                "claim_ids": [f"claim-{index}"],
                                "possible_transformations": []})
    return {
        "observations": observations,
        "evidence": evidence,
        "hypotheses": hypotheses,
        "evaluation": evaluation,
        "claims": claims,
        "recommendations": recommendations,
        "confidence": {"overall": "confirmed" if not findings else "disputed" if any(
            f.get("severity") in ("error", "high") for f in findings
        ) else "plausible"},
    }

def _dependency_layers(
    selected_critics: dict[str, CriticSpec],
) -> list[list[str]]:
    """Group critics into layers by dependency depth.

    Layer 0: critics with no unresolved dependencies.
    Layer N: critics whose dependencies all completed in layers < N.

    Returns a list of lists, where each inner list is a layer of critic IDs
    that may execute concurrently.
    """
    remaining = set(selected_critics)
    resolved: set[str] = set()
    layers: list[list[str]] = []

    while remaining:
        layer = [
            cid for cid in remaining
            if all(dep in resolved for dep in selected_critics[cid].requires)
        ]
        if not layer:
            unresolved = remaining.copy()
            raise ValueError(
                f"cannot resolve dependencies for: {sorted(unresolved)}"
            )
        layer.sort()  # deterministic ordering within the layer
        layers.append(layer)
        remaining -= set(layer)
        resolved.update(layer)

    return layers


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------

class ReasoningRuntime:
    def __init__(self, registry: CriticRegistry, report_dir: Path, *,
                 max_workers: int = _DEFAULT_MAX_WORKERS):
        self.registry = registry
        self.report_dir = Path(report_dir)
        self.max_workers = max_workers

    def plan(self, request: RuntimeRequest) -> ExecutionPlan:
        selected: dict[str, CriticSpec] = {}

        def visit(critic_id: str, path: tuple[str, ...] = ()) -> None:
            if critic_id in path:
                cycle = " -> ".join((*path, critic_id))
                raise ValueError(f"dependency cycle: {cycle}")
            if critic_id in selected:
                return
            spec = self.registry.discover(critic_id=critic_id)
            for dependency in spec.requires:
                visit(dependency, (*path, critic_id))
            selected[critic_id] = spec

        for critic_id in request.critic_ids:
            visit(critic_id)
        snapshot = (ArtifactRevisionAdapter.snapshot(request.source_revisions)
                    if request.source_revisions else {
                        key: value.get("revision") if isinstance(value, Mapping) else None
                        for key, value in sorted(request.inputs.items())
                    })
        plan_id = _stable_id({"request": request.model_dump(exclude={"inputs"}), "inputs": request.inputs})
        layers = _dependency_layers(selected)
        return ExecutionPlan(
            plan_id=plan_id,
            request_id=request.request_id,
            selected_critics=tuple(selected),
            dependency_order=tuple(cid for layer in layers for cid in layer),
            source_snapshot=snapshot,
        )

    def run(self, request: RuntimeRequest, *, expected_revisions: Mapping[str, int] | None = None) -> ExecutionResult:
        plan = self.plan(request)
        expected_revisions = expected_revisions or {}
        layers = _dependency_layers({
            cid: self.registry.discover(critic_id=cid)
            for cid in plan.dependency_order
        })
        all_outcomes: list[ExecutionOutcome] = []

        for layer in layers:
            layer_outcomes: list[ExecutionOutcome] = {}
            lock: Any = None  # currently sequential; parallel handled per-critic

            def execute_critic(critic_id: str) -> ExecutionOutcome:
                spec = self.registry.discover(critic_id=critic_id)
                t0 = time.monotonic()

                stale = [key for key, revision in expected_revisions.items()
                         if isinstance(request.inputs.get(key), Mapping)
                         and request.inputs[key].get("revision") != revision]
                if stale:
                    return ExecutionOutcome(critic_id=critic_id, version=spec.version,
                        status=RuntimeStatus.STALE, reason=f"stale inputs: {', '.join(stale)}",
                        duration_ms=int((time.monotonic() - t0) * 1000))

                blocked_by = [o.critic_id for o in all_outcomes
                              if o.critic_id in spec.requires and o.status is not RuntimeStatus.SUCCESS]
                if blocked_by:
                    return ExecutionOutcome(critic_id=critic_id, version=spec.version,
                        status=RuntimeStatus.BLOCKED, reason=f"dependency failed: {', '.join(blocked_by)}",
                        duration_ms=int((time.monotonic() - t0) * 1000))

                try:
                    findings = spec.run(**request.inputs)
                    if not isinstance(findings, list):
                        raise TypeError("critic must return a list of findings")
                    report_id = _stable_id({"plan": plan.plan_id, "critic": critic_id})
                    # Capture token usage from the LLM client if available
                    llm = request.inputs.get("llm")
                    inp_tokens = getattr(llm, "input_tokens", None) or getattr(llm, "prompt_tokens", None)
                    out_tokens = getattr(llm, "output_tokens", None) or getattr(llm, "completion_tokens", None)
                    report = {"report_id": report_id, "status": "derived", "artifact_type": "reasoning_report",
                              "critic_id": critic_id, "critic_version": spec.version,
                              "plan_id": plan.plan_id, "source_snapshot": plan.source_snapshot,
                              "findings": findings, "usage": {"input_tokens": inp_tokens, "output_tokens": out_tokens},
                              **_reasoning_sections(findings)}
                    self.report_dir.mkdir(parents=True, exist_ok=True)
                    (self.report_dir / f"{report_id}.json").write_text(
                        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                    return ExecutionOutcome(critic_id=critic_id, version=spec.version,
                        status=RuntimeStatus.SUCCESS, report_id=report_id,
                        duration_ms=int((time.monotonic() - t0) * 1000),
                        input_tokens=inp_tokens, output_tokens=out_tokens)
                except Exception as exc:
                    return ExecutionOutcome(critic_id=critic_id, version=spec.version,
                        status=RuntimeStatus.FAILED, reason="critic execution failed",
                        error=str(exc), duration_ms=int((time.monotonic() - t0) * 1000))

            if len(layer) == 1:
                all_outcomes.append(execute_critic(layer[0]))
            else:
                with ThreadPoolExecutor(max_workers=min(self.max_workers, len(layer))) as pool:
                    fut_map = {pool.submit(execute_critic, cid): cid for cid in layer}
                    for fut in as_completed(fut_map):
                        all_outcomes.append(fut.result())
                # Sort outcomes by the deterministic layer order
                order = {cid: i for i, cid in enumerate(layer)}
                all_outcomes.sort(key=lambda o: order.get(o.critic_id, 999))

        return ExecutionResult(plan=plan, outcomes=all_outcomes)

    def report_is_fresh(self, report_id: str, inputs: Mapping[str, Any] | None = None,
                        source_revisions: Mapping[str, ArtifactRevision] | None = None) -> bool:
        path = self.report_dir / f"{report_id}.json"
        if not path.exists():
            return False
        report = json.loads(path.read_text(encoding="utf-8"))
        expected = report.get("source_snapshot", {})
        current = (ArtifactRevisionAdapter.snapshot(source_revisions)
                   if source_revisions is not None else {
                       key: value.get("revision") if isinstance(value, Mapping) else None
                       for key, value in sorted((inputs or {}).items())
                   })
        return expected == current
