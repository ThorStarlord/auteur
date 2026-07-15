"""Minimal deterministic reasoning runtime.

The runtime owns no narrative authority. It reads caller-supplied inputs and
writes only derived reports beneath the caller-supplied report directory.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RuntimeStatus(StrEnum):
    SUCCESS = "success"
    STALE = "stale"
    INCOMPATIBLE = "incompatible"
    FAILED = "failed"
    BLOCKED = "blocked"


CriticRunner = Callable[..., list[dict[str, Any]]]


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
    critic_ids: tuple[str, ...]
    inputs: dict[str, Any] = Field(default_factory=dict)


class ExecutionPlan(BaseModel):
    plan_id: str
    request_id: str
    selected_critics: tuple[str, ...]
    dependency_order: tuple[str, ...]
    source_snapshot: dict[str, Any]


class ExecutionOutcome(BaseModel):
    critic_id: str
    version: str
    status: RuntimeStatus
    reason: str = ""
    report_id: str | None = None
    error: str | None = None


class ExecutionResult(BaseModel):
    plan: ExecutionPlan
    outcomes: list[ExecutionOutcome]


def _stable_id(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()[:16]


class ReasoningRuntime:
    def __init__(self, registry: CriticRegistry, report_dir: Path) -> None:
        self.registry = registry
        self.report_dir = Path(report_dir)

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
        snapshot = {
            key: value.get("revision") if isinstance(value, Mapping) else None
            for key, value in sorted(request.inputs.items())
        }
        plan_id = _stable_id({"request": request.model_dump(exclude={"inputs"}), "inputs": request.inputs})
        return ExecutionPlan(
            plan_id=plan_id,
            request_id=request.request_id,
            selected_critics=tuple(selected),
            dependency_order=tuple(selected),
            source_snapshot=snapshot,
        )

    def run(self, request: RuntimeRequest, *, expected_revisions: Mapping[str, int] | None = None) -> ExecutionResult:
        plan = self.plan(request)
        expected_revisions = expected_revisions or {}
        outcomes: list[ExecutionOutcome] = []
        reports: dict[str, str] = {}
        for critic_id in plan.dependency_order:
            spec = self.registry.discover(critic_id=critic_id)
            stale = [key for key, revision in expected_revisions.items()
                      if isinstance(request.inputs.get(key), Mapping)
                      and request.inputs[key].get("revision") != revision]
            if stale:
                outcomes.append(ExecutionOutcome(critic_id=critic_id, version=spec.version,
                    status=RuntimeStatus.STALE, reason=f"stale inputs: {', '.join(stale)}"))
                continue
            if any(o.critic_id in spec.requires and o.status is not RuntimeStatus.SUCCESS for o in outcomes):
                outcomes.append(ExecutionOutcome(critic_id=critic_id, version=spec.version,
                    status=RuntimeStatus.BLOCKED, reason="dependency did not succeed"))
                continue
            try:
                findings = spec.run(**request.inputs)
                if not isinstance(findings, list):
                    raise TypeError("critic must return a list of findings")
                report_id = _stable_id({"plan": plan.plan_id, "critic": critic_id})
                report = {"report_id": report_id, "status": "derived", "artifact_type": "reasoning_report",
                          "critic_id": critic_id, "critic_version": spec.version,
                          "plan_id": plan.plan_id, "source_snapshot": plan.source_snapshot,
                          "findings": findings}
                self.report_dir.mkdir(parents=True, exist_ok=True)
                (self.report_dir / f"{report_id}.json").write_text(
                    json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                reports[critic_id] = report_id
                outcomes.append(ExecutionOutcome(critic_id=critic_id, version=spec.version,
                    status=RuntimeStatus.SUCCESS, report_id=report_id))
            except Exception as exc:  # noqa: BLE001 - outcome must be explicit
                outcomes.append(ExecutionOutcome(critic_id=critic_id, version=spec.version,
                    status=RuntimeStatus.FAILED, reason="critic execution failed", error=str(exc)))
        return ExecutionResult(plan=plan, outcomes=outcomes)
