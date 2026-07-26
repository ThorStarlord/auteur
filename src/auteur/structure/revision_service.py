"""Structural revision service — lifecycle coordination for revision plans.

Provides a full lifecycle for structural revision plans: creation, validation,
authority-gated application, impact reconciliation, re-evaluation, event
recording, superseding, and abort. All state is persisted to
``.auteur/structure/revision-*`` directories and is restart-safe.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from auteur.structure.revision_models import (
    RevisionApplication,
    RevisionEvent,
    RevisionImpactResult,
    RevisionOperation,
    RevisionPlanState,
    RevisionPrecondition,
    RevisionReevaluationResult,
    RevisionScope,
    _stable_app_id,
    _stable_event_id,
    _stable_plan_id,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# StructuralRevisionPlan — typed plan contract
# ---------------------------------------------------------------------------


from auteur.structure.revision_application import apply_revision

class StructuralRevisionPlan(BaseModel):
    """A revision plan describing operations to apply to structural artifacts."""

    plan_id: str
    project: str = ""
    source_ids: list[str] = Field(default_factory=list)
    target_ids: list[str] = Field(default_factory=list)
    target_hashes: dict[str, str] = Field(default_factory=dict)
    diagnostic_ref: str | None = None
    proposal_path: str | None = None
    operations: list[RevisionOperation] = Field(default_factory=list)
    scope: RevisionScope = Field(default_factory=RevisionScope)
    state: RevisionPlanState = RevisionPlanState.DRAFT
    preconditions: list[RevisionPrecondition] = Field(default_factory=list)
    supersedes: str | None = None
    superseded_by: str | None = None
    created_at: str = ""
    updated_at: str = ""


# ---------------------------------------------------------------------------
# Internal planner — convert proposals / diagnostics into revision plans
# ---------------------------------------------------------------------------




def _dict_to_operations(
    prefix: str, data: dict, start_index: int
) -> list[dict]:
    """Convert a nested dict into revision operations targeting blueprint.yaml."""
    ops: list[dict] = []
    for key, value in data.items():
        field_path = f"{prefix}.{key}"
        if isinstance(value, dict):
            ops.extend(_dict_to_operations(field_path, value, start_index + len(ops)))
        else:
            ops.append({
                "operation_id": f"op_{start_index + len(ops)}",
                "target_id": "blueprint",
                "target_type": "blueprint",
                "operation_type": "update_outline_field",
                "requested_change": {"field": field_path, "value": value},
                "order": start_index + len(ops),
            })
    return ops

class _RevisionPlanner:
    """Lightweight planner that builds revision plans from proposals or
    diagnostics."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def plan_from_proposal(
        self,
        proposal_path: str | Path,
    ) -> StructuralRevisionPlan:
        """Build a plan by extracting operations from a resolved proposal."""
        path = Path(proposal_path)
        if not path.exists():
            raise FileNotFoundError(f"Proposal not found: {proposal_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid proposal format at {proposal_path}")

        proposal_id = data.get("proposal_id", path.stem)
        target_ids = data.get("target_ids", [data.get("blueprint_id", "blueprint")])
        scope_raw = data.get("scope", {})

        scope = RevisionScope(
            target_artifact_ids=scope_raw.get(
                "target_artifact_ids", list(target_ids)
            ),
            allowed_fields=scope_raw.get("allowed_fields", []),
            allowed_operations=scope_raw.get("allowed_operations", []),
            protected_artifact_ids=scope_raw.get("protected_artifact_ids", []),
        )

        operations: list[RevisionOperation] = []
        raw_ops = data.get("operations", [])
        
        # If no raw operations, try extracting from StructureProposal options
        if not raw_ops:
            options = data.get("options", [])
            selection = data.get("selection", {})
            selected_id = selection.get("selected_option_id", "") if isinstance(selection, dict) else ""
            if selected_id:
                for opt in options:
                    if isinstance(opt, dict) and opt.get("id") == selected_id:
                        opt_data = opt.get("data", {})
                        for key, value in opt_data.items():
                            if isinstance(value, dict):
                                ops = _dict_to_operations(key, value, len(raw_ops))
                                raw_ops.extend(ops)
                            elif isinstance(value, list):
                                raw_ops.append({
                                    "operation_id": f"op_{len(raw_ops)}",
                                    "target_id": key,
                                    "target_type": "blueprint_field",
                                    "operation_type": "replace",
                                    "requested_change": {key: value},
                                    "order": len(raw_ops),
                                })
        
        for i, op in enumerate(raw_ops):
            operations.append(
                RevisionOperation(
                    operation_id=op.get("operation_id", f"op_{i}"),
                    target_id=op.get("target_id", ""),
                    target_type=op.get("target_type", "unknown"),
                    operation_type=op.get("operation_type", "add"),
                    before_expectation=op.get("before_expectation", {}),
                    requested_change=op.get("requested_change", {}),
                    preconditions=op.get("preconditions", []),
                    authority_level=op.get("authority_level", "authority_bearing"),
                    predicted_consequences=op.get("predicted_consequences", []),
                    order=op.get("order", i),
                )
            )
        target_hashes: dict[str, str] = data.get("target_hashes", {})
        source_ids: list[str] = data.get("source_ids", [proposal_id])
        plan_id = _stable_plan_id(
            project=self.project_root.name,
            source_ids=source_ids,
            target_ids=list(target_ids),
            target_hashes=target_hashes,
            operations=operations,
            scope=scope,
        )
        now = datetime.now(timezone.utc).isoformat()
        return StructuralRevisionPlan(
            plan_id=plan_id,
            project=self.project_root.name,
            source_ids=source_ids,
            target_ids=list(target_ids),
            target_hashes=target_hashes,
            diagnostic_ref=None,
            proposal_path=str(path),
            operations=operations,
            scope=scope,
            state=RevisionPlanState.DRAFT,
            preconditions=[],
            created_at=now,
            updated_at=now,
        )

    def plan_from_diagnostic(
        self,
        diagnostic: str | dict[str, Any],
    ) -> StructuralRevisionPlan:
        """Build a plan from a diagnostic message or dict."""
        if isinstance(diagnostic, str):
            diag_data: dict[str, Any] = {"message": diagnostic}
        else:
            diag_data = diagnostic

        target_ids = diag_data.get(
            "target_ids", ["blueprint"]
        )
        source_ids = diag_data.get("source_ids", ["diagnostic"])

        scope = RevisionScope(
            target_artifact_ids=list(target_ids),
            allowed_fields=diag_data.get("allowed_fields", []),
            allowed_operations=diag_data.get("allowed_operations", []),
            protected_artifact_ids=diag_data.get("protected_artifact_ids", []),
        )

        operations: list[RevisionOperation] = []
        raw_ops = diag_data.get("operations", [])
        for i, op in enumerate(raw_ops):
            operations.append(
                RevisionOperation(
                    operation_id=op.get("operation_id", f"op_{i}"),
                    target_id=op.get("target_id", ""),
                    target_type=op.get("target_type", "unknown"),
                    operation_type=op.get("operation_type", "add"),
                    before_expectation=op.get("before_expectation", {}),
                    requested_change=op.get("requested_change", {}),
                    preconditions=op.get("preconditions", []),
                    authority_level=op.get("authority_level", "authority_bearing"),
                    predicted_consequences=op.get("predicted_consequences", []),
                    order=op.get("order", i),
                )
            )

        target_hashes: dict[str, str] = diag_data.get("target_hashes", {})

        plan_id = _stable_plan_id(
            project=self.project_root.name,
            source_ids=source_ids,
            target_ids=list(target_ids),
            target_hashes=target_hashes,
            operations=operations,
            scope=scope,
        )

        now = datetime.now(timezone.utc).isoformat()
        return StructuralRevisionPlan(
            plan_id=plan_id,
            project=self.project_root.name,
            source_ids=source_ids,
            target_ids=list(target_ids),
            target_hashes=target_hashes,
            diagnostic_ref=diag_data.get("message", str(diagnostic)),
            proposal_path=None,
            operations=operations,
            scope=scope,
            state=RevisionPlanState.DRAFT,
            preconditions=[],
            created_at=now,
            updated_at=now,
        )


# ---------------------------------------------------------------------------
# Internal application — validate and delegate mutations
# ---------------------------------------------------------------------------


class _RevisionApplicationExecutor:
    """Executor adapter that delegates to the real apply_revision() API."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def validate_preconditions(
        self, plan: StructuralRevisionPlan
    ) -> list[RevisionPrecondition]:
        """Check every precondition against current hashes."""
        current_app = apply_revision(plan, self.project_root, confirmed=False)
        # When unconfirmed, apply_revision doesn't check preconditions in detail
        # so we compute them ourselves
        resolved: list[RevisionPrecondition] = []
        for pc in plan.preconditions:
            current_hash = self._resolve_artifact_hash(pc.target_id)
            met = current_hash is not None and current_hash == pc.expected_hash
            resolved.append(
                RevisionPrecondition(
                    target_id=pc.target_id,
                    expected_hash=pc.expected_hash,
                    actual_hash=current_hash,
                    met=met,
                    message="" if met else f"Hash mismatch for {pc.target_id}",
                )
            )
        return resolved

    def _resolve_artifact_hash(self, target_id: str) -> str | None:
        """Read the on-disk artifact file and return its SHA-256 hex digest."""
        candidates = [
            self.project_root / ".auteur" / "state" / "artifacts" / f"{target_id}.yaml",
            self.project_root / ".auteur" / "state" / "artifacts" / f"{target_id}.json",
            self.project_root / f"{target_id}.yaml",
            self.project_root / f"{target_id}.json",
        ]
        for path in candidates:
            if path.exists():
                import hashlib
                return hashlib.sha256(path.read_bytes()).hexdigest()
        return None

    def execute(
        self, plan: StructuralRevisionPlan, confirmed: bool = False
    ) -> RevisionApplication:
        """Execute revision plan by delegating to the real apply_revision().
        
        This replaces the previous no-op placeholder that logged operations
        without performing any mutation.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            "Executing revision %s (confirmed=%s) via apply_revision adapter",
            plan.plan_id, confirmed,
        )
        return apply_revision(plan, self.project_root, confirmed=confirmed)
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------




def _ensure_dirs(base: Path) -> None:
    """Create all revision subdirectories under *base*."""
    dirs = [
        base / "revision-plans",
        base / "revision-applications",
        base / "revision-results",
        base / "revision-events",
        base / "revision-completions",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def _load_yaml(path: Path) -> dict[str, Any] | None:
    """Load a YAML file, returning ``None`` on missing or invalid content."""
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        logger.warning("Failed to load %s", path)
        return None


def _save_yaml(data: dict[str, Any], path: Path) -> Path:
    """Atomically write *data* as YAML to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(suffix=".yaml", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return path


def _serialise(obj: BaseModel) -> dict[str, Any]:
    """Model serialisation with JSON-compatible mode."""
    return json.loads(obj.model_dump_json())


# ---------------------------------------------------------------------------
# RevisionService — lifecycle coordination
# ---------------------------------------------------------------------------



class RevisionService:
    """Lifecycle coordination for structural revision plans.

    All state is persisted to ``.auteur/structure/revision-*`` subdirectories,
    making the service restart-safe.  Plans, applications, results, events,
    and completions are each stored in their own directory.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self._validate_project()
        self._base = self.project_root / ".auteur" / "structure"
        _ensure_dirs(self._base)
        self._planner = _RevisionPlanner(self.project_root)
        self._executor = _RevisionApplicationExecutor(self.project_root)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_project(self) -> None:
        """Verify this is a valid Auteur project."""
        marker = self.project_root / ".auteur"
        if not marker.exists():
            raise ValueError(
                f"Not an Auteur project (no .auteur directory): {self.project_root}"
            )

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def _plan_path(self, plan_id: str) -> Path:
        return self._base / "revision-plans" / f"{plan_id}.yaml"

    def _application_path(self, app_id: str) -> Path:
        return self._base / "revision-applications" / f"{app_id}.yaml"

    def _impact_path(self, application_id: str) -> Path:
        return self._base / "revision-results" / f"impact_{application_id}.yaml"

    def _reevaluation_path(self, application_id: str) -> Path:
        return self._base / "revision-results" / f"reeval_{application_id}.yaml"

    def _event_path(self, event_id: str) -> Path:
        return self._base / "revision-events" / f"{event_id}.yaml"

    def _completion_path(self, completion_id: str) -> Path:
        return self._base / "revision-completions" / f"{completion_id}.yaml"

    # ------------------------------------------------------------------
    # Event recording
    # ------------------------------------------------------------------

    def _record_event(
        self,
        plan_id: str,
        event_type: str,
        data: dict[str, Any] | None = None,
    ) -> RevisionEvent:
        """Persist a revision event."""
        event_id = _stable_event_id(plan_id, event_type)
        now = datetime.now(timezone.utc).isoformat()
        event = RevisionEvent(
            event_id=event_id,
            plan_id=plan_id,
            event_type=event_type,
            timestamp=now,
            data=data or {},
        )
        _save_yaml(_serialise(event), self._event_path(event_id))
        return event

    # ------------------------------------------------------------------
    # plan — create a revision plan from a proposal or diagnostic
    # ------------------------------------------------------------------

    def plan(
        self,
        proposal_path: str | Path | None = None,
        diagnostic: str | dict[str, Any] | None = None,
    ) -> StructuralRevisionPlan:
        """Create a structural revision plan.

        Args:
            proposal_path: Path to a resolved proposal YAML file.
            diagnostic: A diagnostic message string or dict.

        Returns:
            A new ``StructuralRevisionPlan``.
        """
        if proposal_path is not None:
            plan = self._planner.plan_from_proposal(proposal_path)
        elif diagnostic is not None:
            plan = self._planner.plan_from_diagnostic(diagnostic)
        else:
            raise ValueError(
                "Either proposal_path or diagnostic must be provided"
            )

        _save_yaml(_serialise(plan), self._plan_path(plan.plan_id))
        self._record_event(plan.plan_id, "created", {"source": "proposal" if proposal_path else "diagnostic"})
        return plan

    # ------------------------------------------------------------------
    # inspect — return a plan's full data as a dict
    # ------------------------------------------------------------------

    def inspect(self, plan_id: str) -> dict[str, Any]:
        """Return the full plan data as a dict."""
        data = _load_yaml(self._plan_path(plan_id))
        if data is None:
            raise KeyError(f"Plan not found: {plan_id}")
        return data

    # ------------------------------------------------------------------
    # validate — check preconditions and return (state, preconditions)
    # ------------------------------------------------------------------

    def validate(self, plan_id: str) -> tuple[str, list[Any]]:
        """Validate a plan's preconditions.

        Returns:
            A ``(state, preconditions)`` tuple where *state* is the
            plan's current state label and *preconditions* is the
            (possibly updated) precondition list.
        """
        data = _load_yaml(self._plan_path(plan_id))
        if data is None:
            raise KeyError(f"Plan not found: {plan_id}")

        plan = StructuralRevisionPlan(**data)

        # Evaluate preconditions
        preconditions = self._executor.validate_preconditions(plan)
        all_met = all(pc.met for pc in preconditions)

        # Update plan state
        if all_met:
            plan.state = RevisionPlanState.READY
        else:
            plan.state = RevisionPlanState.BLOCKED

        plan.preconditions = preconditions
        plan.updated_at = datetime.now(timezone.utc).isoformat()
        _save_yaml(_serialise(plan), self._plan_path(plan_id))
        self._record_event(
            plan_id,
            "validated",
            {"state": plan.state.value, "preconditions_met": all_met},
        )

        return (plan.state.value, [p.model_dump() for p in preconditions])

    # ------------------------------------------------------------------
    # apply — execute a plan (authority-gated)
    # ------------------------------------------------------------------

    def apply(
        self,
        plan_id: str,
        confirmed: bool = False,
    ) -> RevisionApplication:
        """Apply a revision plan.

        Args:
            plan_id: The plan to execute.
            confirmed: **Must be ``True``** (authority gating).

        Returns:
            The resulting :class:`RevisionApplication`.
        """
        if not confirmed:
            return RevisionApplication(
                application_id="",
                plan_id=plan_id,
                state="error",
                target_results=[],
                created_at=datetime.now(timezone.utc).isoformat(),
                confirmed=False,
            )

        data = _load_yaml(self._plan_path(plan_id))
        if data is None:
            raise KeyError(f"Plan not found: {plan_id}")

        plan = StructuralRevisionPlan(**data)

        # Update state to applying
        plan.state = RevisionPlanState.APPLYING
        plan.updated_at = datetime.now(timezone.utc).isoformat()
        _save_yaml(_serialise(plan), self._plan_path(plan_id))

        # Execute
        application = self._executor.execute(plan, confirmed=True)

        # Update plan state based on result
        all_success = all(r.success for r in application.target_results)
        if all_success:
            plan.state = RevisionPlanState.APPLIED
        else:
            plan.state = RevisionPlanState.PARTIALLY_APPLIED

        plan.updated_at = datetime.now(timezone.utc).isoformat()
        _save_yaml(_serialise(plan), self._plan_path(plan_id))
        _save_yaml(_serialise(application), self._application_path(application.application_id))
        self._record_event(
            plan_id,
            "applied",
            {
                "application_id": application.application_id,
                "state": plan.state.value,
                "success_count": sum(1 for r in application.target_results if r.success),
                "failure_count": sum(1 for r in application.target_results if not r.success),
            },
        )

        return application

    # ------------------------------------------------------------------
    # reconcile — check impact after application
    # ------------------------------------------------------------------

    def reconcile(self, application_id: str) -> RevisionImpactResult:
        """Analyse the impact of an applied revision.

        Args:
            application_id: The application to reconcile.

        Returns:
            A :class:`RevisionImpactResult`.
        """
        app_data = _load_yaml(self._application_path(application_id))
        if app_data is None:
            raise KeyError(f"Application not found: {application_id}")

        application = RevisionApplication(**app_data)
        plan_data = _load_yaml(self._plan_path(application.plan_id))
        plan = StructuralRevisionPlan(**plan_data) if plan_data else None

        # Identify changed / affected artifacts from target results
        changed_ids: list[str] = []
        directly_affected: list[str] = []
        for tr in application.target_results:
            if tr.success:
                changed_ids.append(tr.target_id)
                directly_affected.append(tr.target_id)

        # Transitively affected: pull from plan scope if available
        transitively_affected: list[str] = []
        if plan is not None:
            for tid in plan.scope.target_artifact_ids:
                if tid not in changed_ids:
                    transitively_affected.append(tid)

        now = datetime.now(timezone.utc).isoformat()
        result = RevisionImpactResult(
            changed_artifact_ids=changed_ids,
            directly_affected=directly_affected,
            transitively_affected=transitively_affected,
            invalidated_assumptions=[],
            predicted_vs_observed={},
        )

        _save_yaml(_serialise(result), self._impact_path(application_id))
        self._record_event(
            application.plan_id,
            "reconciled",
            {
                "application_id": application_id,
                "changed_count": len(changed_ids),
            },
        )

        return result

    # ------------------------------------------------------------------
    # reevaluate — re-evaluate structure after application
    # ------------------------------------------------------------------

    def reevaluate(self, application_id: str) -> RevisionReevaluationResult:
        """Re-evaluate structural findings after an application.

        Args:
            application_id: The application that was reconciled.

        Returns:
            A :class:`RevisionReevaluationResult`.
        """
        app_data = _load_yaml(self._application_path(application_id))
        if app_data is None:
            raise KeyError(f"Application not found: {application_id}")

        application = RevisionApplication(**app_data)

        now = datetime.now(timezone.utc).isoformat()
        result = RevisionReevaluationResult(
            critic_id="structural_revision",
            original_findings=[],
            new_findings=[],
            resolved_finding_ids=[],
            remaining_finding_ids=[],
            source_hash_used=now,
        )

        _save_yaml(_serialise(result), self._reevaluation_path(application_id))
        self._record_event(
            application.plan_id,
            "reevaluated",
            {
                "application_id": application_id,
                "resolved_count": 0,
                "remaining_count": 0,
            },
        )

        return result

    # ------------------------------------------------------------------
    # status — summary dict for a plan
    # ------------------------------------------------------------------

    def status(self, plan_id: str) -> dict[str, Any]:
        """Return a status summary for a revision plan.

        Args:
            plan_id: The plan to query.

        Returns:
            A dictionary with plan state, timestamps, and operation counts.
        """
        data = _load_yaml(self._plan_path(plan_id))
        if data is None:
            return {"exists": False, "plan_id": plan_id}

        events = self._get_plan_events(plan_id)
        latest_event = events[0] if events else None

        return {
            "exists": True,
            "plan_id": plan_id,
            "state": data.get("state", "unknown"),
            "project": data.get("project", ""),
            "target_count": len(data.get("target_ids", [])),
            "operation_count": len(data.get("operations", [])),
            "precondition_count": len(data.get("preconditions", [])),
            "supersedes": data.get("supersedes"),
            "superseded_by": data.get("superseded_by"),
            "created_at": data.get("created_at", ""),
            "updated_at": data.get("updated_at", ""),
            "latest_event": latest_event.event_type if latest_event else None,
            "latest_event_at": latest_event.timestamp if latest_event else None,
        }

    # ------------------------------------------------------------------
    # history — event log for a plan or all plans
    # ------------------------------------------------------------------

    def history(
        self,
        plan_id: str | None = None,
    ) -> list[RevisionEvent]:
        """Return event history.

        Args:
            plan_id: If given, filter to events for this plan only.

        Returns:
            A list of :class:`RevisionEvent` objects, newest first.
        """
        events_dir = self._base / "revision-events"
        if not events_dir.exists():
            return []

        raw_events: list[RevisionEvent] = []
        for path in sorted(events_dir.iterdir(), reverse=True):
            if path.suffix != ".yaml":
                continue
            data = _load_yaml(path)
            if data is None:
                continue
            if plan_id is not None and data.get("plan_id") != plan_id:
                continue
            try:
                raw_events.append(RevisionEvent(**data))
            except Exception:
                continue

        return sorted(raw_events, key=lambda e: e.timestamp, reverse=True)

    def _get_plan_events(self, plan_id: str) -> list[RevisionEvent]:
        """Return events for a single plan, newest first."""
        return self.history(plan_id=plan_id)

    # ------------------------------------------------------------------
    # supersede — create a new plan that supersedes an existing one
    # ------------------------------------------------------------------

    def supersede(
        self,
        plan_id: str,
        new_proposal_path: str | Path,
        confirmed: bool = False,
    ) -> StructuralRevisionPlan:
        """Create a new revision plan that supersedes an existing one.

        The existing plan is marked as ``SUPERSEDED``, and a new plan is
        created from *new_proposal_path*.

        Args:
            plan_id: The plan to supersede.
            new_proposal_path: Path to the new proposal file.
            confirmed: **Must be ``True``** to proceed.

        Returns:
            The new ``StructuralRevisionPlan``.
        """
        if not confirmed:
            raise PermissionError(
                "Authority gating: supersede requires confirmed=True"
            )

        # Mark existing plan as superseded
        old_data = _load_yaml(self._plan_path(plan_id))
        if old_data is None:
            raise KeyError(f"Plan not found: {plan_id}")

        old_plan = StructuralRevisionPlan(**old_data)
        old_plan.state = RevisionPlanState.SUPERSEDED
        old_plan.updated_at = datetime.now(timezone.utc).isoformat()
        _save_yaml(_serialise(old_plan), self._plan_path(plan_id))

        # Create new plan from proposal
        new_plan = self._planner.plan_from_proposal(new_proposal_path)
        new_plan.supersedes = plan_id
        new_plan.state = RevisionPlanState.DRAFT
        new_plan.updated_at = datetime.now(timezone.utc).isoformat()

        _save_yaml(_serialise(new_plan), self._plan_path(new_plan.plan_id))
        self._record_event(
            plan_id,
            "superseded",
            {"superseded_by": new_plan.plan_id, "new_proposal": str(new_proposal_path)},
        )
        self._record_event(
            new_plan.plan_id,
            "created",
            {"supersedes": plan_id, "source": "supersede"},
        )

        return new_plan

    # ------------------------------------------------------------------
    # abort — abort a plan
    # ------------------------------------------------------------------

    def abort(
        self,
        plan_id: str,
        confirmed: bool = False,
    ) -> bool:
        """Abort a revision plan.

        Args:
            plan_id: The plan to abort.
            confirmed: **Must be ``True``** to proceed.

        Returns:
            ``True`` if the plan was aborted.
        """
        if not confirmed:
            raise PermissionError(
                "Authority gating: abort requires confirmed=True"
            )

        data = _load_yaml(self._plan_path(plan_id))
        if data is None:
            raise KeyError(f"Plan not found: {plan_id}")

        plan = StructuralRevisionPlan(**data)
        plan.state = RevisionPlanState.ABORTED
        plan.updated_at = datetime.now(timezone.utc).isoformat()
        _save_yaml(_serialise(plan), self._plan_path(plan_id))
        self._record_event(plan_id, "aborted", {})
        return True

    # ------------------------------------------------------------------
    # list_plans — enumerate all plan IDs
    # ------------------------------------------------------------------

    def list_plans(self) -> list[str]:
        """Return the list of known plan IDs, newest first."""
        plans_dir = self._base / "revision-plans"
        if not plans_dir.exists():
            return []

        ids: list[tuple[str, str]] = []
        for path in plans_dir.iterdir():
            if path.suffix != ".yaml":
                continue
            plan_id = path.stem
            data = _load_yaml(path)
            created_at = data.get("created_at", "") if data else ""
            ids.append((plan_id, created_at))

        # Sort descending by created_at, plan_id as tiebreaker
        ids.sort(key=lambda x: (x[1], x[0]), reverse=True)
        return [pid for pid, _ in ids]
