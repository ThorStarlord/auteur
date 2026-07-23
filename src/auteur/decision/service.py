"""Decision workspace service — compose real project state from subsystems."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from auteur.convergence.models import CandidateRef, RevisionTarget
from auteur.convergence.persistence import ConvergenceStore
from auteur.decision.assembler import DecisionAssembler
from auteur.decision.models import (
    AuthorDecision,
    CandidateSummary,
    DecisionEvidence,
    DecisionReadiness,
    DecisionTrigger,
    EvidenceClassification,
    EvidenceFreshness,
    EvidenceSource,
    EvidenceType,
    LifecycleState,
    AcceptancePreparation,
)
from auteur.decision.persistence import DecisionStore
from auteur.impact.models import ImpactFinding, ImpactPreview
from auteur.impact.persistence import ImpactStore
from auteur.provenance.store import ArtifactStore
from auteur.workflow.models import AuthorityLevel

logger = logging.getLogger(__name__)

class DecisionWorkspaceService:
    """Orchestrate decision workspace from real Auteur subsystems."""

    def __init__(self, project_root: Path):
        """Initialize service for a project."""
        self.project_root = Path(project_root).resolve()
        self._validate_project()

        # Initialize subsystem stores
        self.artifact_store = ArtifactStore(self.project_root)
        self.impact_store = ImpactStore(self.project_root)
        self.convergence_store = ConvergenceStore(self.project_root)
        self.decision_store = DecisionStore(self.project_root)
        self.assembler = DecisionAssembler(self.project_root)

        # Initialize adapters for direct subsystem integration
        from auteur.decision.adapters.reasoning_adapter import ReasoningAdapter
        self.reasoning_adapter = ReasoningAdapter(self.project_root)
        from auteur.decision.adapters.reconciliation_adapter import ReconciliationAdapter
        self.reconciliation_adapter = ReconciliationAdapter(self.project_root)

    def _validate_project(self) -> None:
        """Verify this is a valid Auteur project."""
        auteur_marker = self.project_root / ".auteur"
        if not auteur_marker.exists():
            raise ValueError(f"Not an Auteur project (no .auteur directory): {self.project_root}")

    def status(self) -> dict[str, Any]:
        """Get workspace status summary."""
        try:
            decisions = self.list_decisions()
            decisions_by_readiness = {}
            for decision in decisions:
                key = decision.readiness.value
                decisions_by_readiness[key] = decisions_by_readiness.get(key, 0) + 1

            impact_findings = self._load_impact_findings()
            open_findings = [f for f in impact_findings if not self._finding_has_decision(f)]

            return {
                "project": str(self.project_root),
                "total_decisions": len(decisions),
                "decisions_by_readiness": decisions_by_readiness,
                "open_impact_findings": len(open_findings),
                "ready_for_acceptance": decisions_by_readiness.get(DecisionReadiness.READY_FOR_ACCEPTANCE.value, 0),
                "blocked_decisions": decisions_by_readiness.get(DecisionReadiness.BLOCKED.value, 0),
                "highest_priority_readiness": self._get_highest_priority_readiness(decisions),
            }
        except Exception as e:
            logger.exception("Error getting workspace status")
            raise

    def list_decisions(
        self,
        chapter_index: int | None = None,
        readiness: str | None = None,
        stale: bool | None = None,
        requires_author: bool | None = None,
        bypass_low_priority: bool | None = None,
    ) -> list[AuthorDecision]:
        """List assembled decisions with optional filters.

        Filters are composable and deterministic (sorted by chapter then ID).
        """
        try:
            decisions: dict[str, AuthorDecision] = {}

            # Decisions from impact findings
            impact_findings = self._load_impact_findings()
            for finding in impact_findings:
                decision = self._decision_from_impact_finding(finding)
                if self._passes_filters(decision, chapter_index, readiness, stale, requires_author, bypass_low_priority):
                    decisions[decision.decision_id] = decision

            # Decisions from convergence targets
            targets = self._load_convergence_targets()
            for target in targets:
                decision = self._decision_from_convergence_target(target)
                if self._passes_filters(decision, chapter_index, readiness, stale, requires_author, bypass_low_priority):
                    decisions[decision.decision_id] = decision

            return sorted(decisions.values(), key=lambda d: (d.chapter_index, d.decision_id))
        except Exception as e:
            logger.exception("Error listing decisions")
            raise

    def _passes_filters(
        self,
        decision: AuthorDecision,
        chapter_index: int | None,
        readiness: str | None,
        stale: bool | None,
        requires_author: bool | None,
        bypass_low_priority: bool | None,
    ) -> bool:
        """Check if a decision passes all active filters."""
        if chapter_index is not None and decision.chapter_index != chapter_index:
            return False
        if readiness is not None and decision.readiness.value != readiness:
            return False
        if stale is not None:
            is_stale = decision.freshness == EvidenceFreshness.STALE or decision.lifecycle_state == LifecycleState.STALE
            if stale and not is_stale:
                return False
            if not stale and is_stale:
                return False
        if requires_author is not None:
            has_open = decision.has_open_choices() if hasattr(decision, 'has_open_choices') else bool(decision.unresolved_choices)
            if requires_author and not has_open:
                return False
            if not requires_author and has_open:
                return False
        if bypass_low_priority:
            from auteur.decision.models import DecisionReadiness
            low_priority = {
                DecisionReadiness.NEEDS_CANDIDATE,
                DecisionReadiness.STALE,
            }
            if decision.readiness in low_priority:
                return False
        return True

    def inspect(self, decision_id: str) -> AuthorDecision:
        """Get full decision detail with all evidence.

        First tries live-assembled state (impact findings + convergence targets),
        then falls back to the snapshot store for persisted-only decisions.
        """
        try:
            decisions = self.list_decisions()
            decision = next((d for d in decisions if d.decision_id == decision_id), None)

            if decision is None:
                # Fallback: try snapshot store
                decision = self.decision_store.load_snapshot(decision_id)
                if decision is None:
                    raise ValueError(f"Decision not found: {decision_id}")
                return decision

            # Enrich with full evidence details
            decision = self._enrich_decision(decision)
            return decision
        except Exception as e:
            logger.exception(f"Error inspecting decision {decision_id}")
            raise

    def evidence_for_decision(self, decision_id: str) -> list[DecisionEvidence]:
        """Get all evidence grouped by classification for a decision."""
        decision = self.inspect(decision_id)
        return sorted(
            decision.evidence,
            key=lambda e: (e.classification.value, e.source_subsystem.value, e.freshness.value),
        )

    def compare_candidates(self, decision_id: str) -> dict[str, Any]:
        """Get candidate comparison data for a decision."""
        decision = self.inspect(decision_id)

        if len(decision.candidates) < 2:
            return {
                "decision_id": decision_id,
                "comparison_available": False,
                "reason": "Fewer than 2 candidates",
                "candidates": [c.candidate_id for c in decision.candidates],
            }

        # Check for stored comparison
        comparisons = self.convergence_store.list_comparisons(decision.target_artifact_id)
        if not comparisons:
            return {
                "decision_id": decision_id,
                "comparison_available": False,
                "reason": "No comparison evidence",
                "candidates": [c.candidate_id for c in decision.candidates],
            }

        # Return comparison details
        latest_comparison = comparisons[-1]
        return {
            "decision_id": decision_id,
            "comparison_id": latest_comparison.get("comparison_id"),
            "comparison_available": True,
            "candidates": latest_comparison.get("candidate_ids", []),
            "dimensions": latest_comparison.get("dimensions", []),
            "conflicts": latest_comparison.get("conflicts", []),
            "recommended_candidate": latest_comparison.get("recommended_candidate_id"),
        }

    def next_action(self, decision_id: str) -> dict[str, Any]:
        """Recommend next action for a decision."""
        decision = self.inspect(decision_id)
        action = self.assembler.compute_next_action(decision)

        if action is None:
            return {
                "decision_id": decision_id,
                "action": None,
                "readiness": decision.readiness.value,
                "reason": "No further action recommended",
            }

        return {
            "decision_id": decision_id,
            "action_id": action.action_id,
            "title": action.title,
            "reason": action.reason,
            "command": action.command,
            "safe_to_execute": action.safe_to_execute,
            "authority_level": action.authority_level.value,
            "expected_result_state": action.expected_result_state,
        }

    def prepare_acceptance(self, decision_id: str, candidate_id: str) -> AcceptancePreparation:
        """Enriched acceptance readiness review with prerequisites, tradeoffs, and impact."""
        try:
            decision = self.inspect(decision_id)

            candidate = next((c for c in decision.candidates if c.candidate_id == candidate_id), None)
            if candidate is None:
                return AcceptancePreparation(
                    decision_id=decision_id,
                    candidate_id=candidate_id,
                    is_ready=False,
                    blockers=["Candidate not found in decision"],
                )

            # Collect satisfied and unsatisfied prerequisites
            satisfied: list[str] = []
            unsatisfied: list[str] = []
            blockers: list[str] = []
            verification_results: dict[str, bool] = {}

            # 1. Candidate freshness
            is_fresh = candidate.freshness == EvidenceFreshness.CURRENT
            verification_results["candidate_freshness_current"] = is_fresh
            if is_fresh:
                satisfied.append("Candidate is fresh")
            else:
                unsatisfied.append("Candidate freshness")
                blockers.append("Candidate is stale")

            # 2. Reasoning evidence via adapter
            reasoning_reports = []
            try:
                reasoning_reports = self.reasoning_adapter.get_candidate_reports(
                    candidate_id, decision.chapter_index,
                )
            except Exception:
                pass
            has_reasoning = len(reasoning_reports) > 0 or len(candidate.reasoning_evidence) > 0
            verification_results["reasoning_evidence_present"] = has_reasoning
            if has_reasoning:
                satisfied.append("Reasoning evidence present")
            else:
                unsatisfied.append("Reasoning evidence")
                blockers.append("Candidate lacks reasoning evidence")

            # 3. Obligations satisfied
            ob_satisfied = len(candidate.obligations_unsatisfied) == 0
            verification_results["obligations_satisfied"] = ob_satisfied
            if ob_satisfied:
                satisfied.append("All obligations satisfied")
            else:
                ob_count = len(candidate.obligations_unsatisfied)
                unsatisfied.append(f"Obligations satisfied: {len(candidate.obligations_satisfied)}, unsatisfied: {ob_count}")
                blockers.append(f"Unsatisfied obligations: {ob_count}")

            # 4. Author choices resolved
            choices_resolved = not decision.has_open_choices()
            verification_results["author_choices_resolved"] = choices_resolved
            if choices_resolved:
                satisfied.append("No unresolved author choices")
            else:
                unsatisfied.append("Author choices")
                blockers.append("Decision has unresolved author choices")

            # 5. Reconciliation conflicts resolved
            has_conflicts = any(
                e.evidence_type == EvidenceType.RECONCILIATION_CONFLICT
                and e.freshness == EvidenceFreshness.CURRENT
                for e in decision.evidence
            )
            verification_results["reconciliation_resolved"] = not has_conflicts
            if not has_conflicts:
                satisfied.append("Reconciliation conflicts resolved")
            else:
                unsatisfied.append("Reconciliation conflicts")
                blockers.append("Reconciliation conflicts remain")

            # 6. Downstream impact simulation
            impact_preview = None
            stale_after: list[str] = []
            try:
                impact_preview = self.impact_preview(decision_id, candidate_id)
                stale_after = [imp.artifact_id for imp in impact_preview.definite_impacts]
            except Exception:
                pass

            # Build candidate tradeoffs summary
            tradeoffs: list[str] = []
            if decision.candidates:
                total = len(decision.candidates)
                idx = next((i for i, c in enumerate(decision.candidates) if c.candidate_id == candidate_id), -1)
                tradeoffs.append(f"Candidate {idx + 1} of {total}")
            tradeoffs.append(f"Obligations: {len(candidate.obligations_satisfied)} satisfied, {len(candidate.obligations_unsatisfied)} unsatisfied")
            if candidate.reasoning_evidence:
                tradeoffs.append(f"Reasoning reviews: {len(candidate.reasoning_evidence)} reference(s)")
            if candidate.continuity_conflicts:
                tradeoffs.append(f"Continuity conflicts: {len(candidate.continuity_conflicts)}")

            # Build reasoning evidence summary
            reasoning_summary: dict[str, Any] = {
                "report_count": len(reasoning_reports),
                "report_ids": [r.get("review_id", r.get("run_id", "")) for r in reasoning_reports[:5]],
            }

            # Build reconciliation evidence summary
            reconciliation_summary: dict[str, Any] = {
                "has_conflicts": has_conflicts,
                "conflict_count": len([e for e in decision.evidence if e.evidence_type == EvidenceType.RECONCILIATION_CONFLICT]),
            }

            # Build acceptance request (populated only when ready)
            acceptance_request = None
            if len(blockers) == 0:
                acceptance_request = {
                    "decision_id": decision_id,
                    "candidate_id": candidate_id,
                    "snapshot_id": decision.snapshot_id,
                    "source_snapshot": decision.source_snapshot,
                    "accepted_by": "author",
                    "type": "acceptance_request_v1",
                }

            is_ready = len(blockers) == 0
            return AcceptancePreparation(
                decision_id=decision_id,
                candidate_id=candidate_id,
                is_ready=is_ready,
                blockers=blockers,
                satisfied_prerequisites=satisfied,
                unsatisfied_prerequisites=unsatisfied,
                candidate_tradeoffs=tradeoffs,
                reasoning_evidence_summary=reasoning_summary,
                reconciliation_evidence_summary=reconciliation_summary,
                downstream_impact=impact_preview,
                stale_after_acceptance=stale_after,
                acceptance_request=acceptance_request,
                verification_results=verification_results,
            )
        except Exception as e:
            logger.exception(f"Error preparing acceptance for {decision_id}")
            raise

    # =========================================================================
    # Lineage and lifecycle queries
    # =========================================================================

    def lineage(self, decision_id: str) -> list[AuthorDecision]:
        """Return all snapshots in a decision's lineage, oldest first."""
        lineage_entries = self.decision_store.load_lineage(decision_id)
        decisions: list[AuthorDecision] = []
        for entry in lineage_entries:
            sid = entry.get("snapshot_id")
            if sid:
                # Reconstruct from snapshot store
                decision = self.decision_store.load_snapshot(decision_id)
                if decision and decision.snapshot_id == sid:
                    decisions.append(decision)
        # Fallback: if no snapshots returned, try loading directly
        if not decisions:
            snapshot = self.decision_store.load_snapshot(decision_id)
            if snapshot:
                decisions.append(snapshot)
        return decisions

    def history(self, decision_id: str) -> list[dict[str, Any]]:
        """Return summary history of a decision's snapshots for CLI display."""
        entries = self.decision_store.load_lineage(decision_id)
        if not entries:
            # Try loading snapshot directly for non-lineage-tracked decisions
            snapshot = self.decision_store.load_snapshot(decision_id)
            if snapshot:
                return [{
                    "snapshot_id": snapshot.snapshot_id or "unknown",
                    "preceding_snapshot_id": None,
                    "readiness": snapshot.readiness.value,
                    "lifecycle_state": snapshot.lifecycle_state.value,
                    "freshness": snapshot.freshness.value,
                    "recorded_at": snapshot.last_updated_at.isoformat(),
                }]
            # Check raw dict for v0.7.0 compat
            raw = self.decision_store.load_snapshot_raw(decision_id)
            if raw:
                return [{
                    "snapshot_id": raw.get("snapshot_id", "(v0 compat)"),
                    "preceding_snapshot_id": None,
                    "readiness": raw.get("readiness", "unknown"),
                    "lifecycle_state": raw.get("lifecycle_state", "unknown"),
                    "freshness": raw.get("freshness", "unknown"),
                    "recorded_at": raw.get("last_updated_at", "unknown"),
                }]
            return []

        result: list[dict[str, Any]] = []
        for entry in entries:
            sid = entry.get("snapshot_id")
            if sid:
                decision = self.decision_store.load_snapshot(decision_id)
                if decision and decision.snapshot_id == sid:
                    result.append({
                        "snapshot_id": sid,
                        "preceding_snapshot_id": entry.get("preceding_snapshot_id"),
                        "readiness": decision.readiness.value,
                        "lifecycle_state": decision.lifecycle_state.value,
                        "freshness": decision.freshness.value,
                        "recorded_at": entry.get("recorded_at", decision.last_updated_at.isoformat()),
                    })
                else:
                    result.append({
                        "snapshot_id": sid,
                        "preceding_snapshot_id": entry.get("preceding_snapshot_id"),
                        "readiness": "(snapshot not loaded)",
                        "lifecycle_state": "",
                        "freshness": "",
                        "recorded_at": entry.get("recorded_at", ""),
                    })
        return result

    def diff(self, snapshot_id_a: str, snapshot_id_b: str) -> dict[str, Any]:
        """Compute field-level diff between two decision snapshots."""
        # Find decisions containing these snapshot IDs
        all_ids = self.decision_store.list_snapshots()
        decision_a: AuthorDecision | None = None
        decision_b: AuthorDecision | None = None

        for did in all_ids:
            snap = self.decision_store.load_snapshot(did)
            if snap and snap.snapshot_id == snapshot_id_a:
                decision_a = snap
            if snap and snap.snapshot_id == snapshot_id_b:
                decision_b = snap
            if decision_a and decision_b:
                break

        if not decision_a or not decision_b:
            missing = []
            if not decision_a:
                missing.append(snapshot_id_a)
            if not decision_b:
                missing.append(snapshot_id_b)
            return {"error": f"Snapshot(s) not found: {', '.join(missing)}"}

        # Compute diff
        changes: dict[str, dict[str, Any]] = {}
        comparable_fields = [
            "readiness", "lifecycle_state", "freshness",
            "authority_required", "blockers",
        ]

        for field in comparable_fields:
            val_a = getattr(decision_a, field)
            val_b = getattr(decision_b, field)
            serialized_a = val_a.value if isinstance(val_a, (DecisionReadiness, LifecycleState, EvidenceFreshness)) else val_a
            serialized_b = val_b.value if isinstance(val_b, (DecisionReadiness, LifecycleState, EvidenceFreshness)) else val_b
            if serialized_a != serialized_b:
                changes[field] = {"from": serialized_a, "to": serialized_b}

        # Compare evidence count
        if len(decision_a.evidence) != len(decision_b.evidence):
            changes["evidence_count"] = {
                "from": len(decision_a.evidence),
                "to": len(decision_b.evidence),
            }

        # Compare candidate count
        if len(decision_a.candidates) != len(decision_b.candidates):
            changes["candidate_count"] = {
                "from": len(decision_a.candidates),
                "to": len(decision_b.candidates),
            }

        # Compare conflict count
        if len(decision_a.conflicts) != len(decision_b.conflicts):
            changes["conflict_count"] = {
                "from": len(decision_a.conflicts),
                "to": len(decision_b.conflicts),
            }

        return {
            "snapshot_a": snapshot_id_a,
            "snapshot_b": snapshot_id_b,
            "decision_id": decision_a.decision_id,
            "changes": changes,
            "has_changes": len(changes) > 0,
        }

    def _compute_preceding_snapshot_id(self, decision_id: str) -> str | None:
        """Get the most recent snapshot_id for a decision, if any."""
        entries = self.decision_store.load_lineage(decision_id)
        if entries:
            return entries[-1].get("snapshot_id")
        return None

    def conflicts(self, decision_id: str) -> list[DecisionConflict]:
        """Get active conflicts for a decision, classified by type."""
        decision = self.inspect(decision_id)
        from auteur.decision.conflict_detector import ConflictDetector
        detector = ConflictDetector()
        return detector.detect_conflicts(decision_id, decision.evidence)

    def impact_preview(self, decision_id: str, candidate_id: str) -> ImpactPreview:
        """Simulate the downstream impact of accepting a candidate.

        Completely read-only: no canonical or accepted state is modified.
        Returns an ``ImpactPreview`` with definite and inferred impacts.
        """
        from auteur.impact.models import ImpactPreview, ImpactedArtifact
        from auteur.impact.graph import DependencyGraph

        decision = self.inspect(decision_id)
        candidate = next((c for c in decision.candidates if c.candidate_id == candidate_id), None)
        if candidate is None:
            return ImpactPreview(
                candidate_id=candidate_id,
                target_artifact_id=decision.target_artifact_id,
                downstream_work_summary="Candidate not found in decision",
            )

        # Walk dependency graph from the target artifact
        graph = DependencyGraph(self.project_root)
        target_id = decision.target_artifact_id

        definite: list[ImpactedArtifact] = []
        inferred: list[ImpactedArtifact] = []
        unchanged: list[str] = []

        try:
            downstream = graph.get_downstream(target_id)

            for dep_id, dep_info in downstream.items():
                artifact_type = dep_info.get("type", "unknown")
                chapter = dep_info.get("chapter_index")
                edge_kind = dep_info.get("kind", "structural")

                if edge_kind in ("structural", "composition"):
                    definite.append(ImpactedArtifact(
                        artifact_id=dep_id,
                        artifact_type=artifact_type,
                        chapter_index=chapter,
                        impact_kind="definite",
                        impact_reason=f"Structural dependency on {target_id}",
                        downstream_cost=2,
                    ))
                elif edge_kind in ("reference", "review"):
                    inferred.append(ImpactedArtifact(
                        artifact_id=dep_id,
                        artifact_type=artifact_type,
                        chapter_index=chapter,
                        impact_kind="inferred",
                        impact_reason=f"Referential dependency on {target_id}",
                        downstream_cost=1,
                    ))
                else:
                    unchanged.append(dep_id)
        except Exception:
            pass

        downstream_work = (
            f"{len(definite)} definite, {len(inferred)} inferred impact(s)"
            if definite or inferred else
            "No downstream impact detected"
        )

        if definite:
            downstream_work += f" — requires regeneration of {len(definite)} artifact(s)"

        return ImpactPreview(
            candidate_id=candidate_id,
            target_artifact_id=target_id,
            definite_impacts=definite,
            inferred_impacts=inferred,
            unchanged_artifacts=unchanged,
            downstream_work_summary=downstream_work,
        )

    def refresh(self) -> None:
        """Refresh workspace state from subsystems."""
        try:
            # Reload impact findings
            findings = self._load_impact_findings(force=True)
            logger.info(f"Refreshed {len(findings)} impact findings")

            # Reload convergence targets and candidates
            targets = self._load_convergence_targets(force=True)
            logger.info(f"Refreshed {len(targets)} convergence targets")
        except Exception as e:
            logger.exception("Error refreshing workspace")
            raise

    # =========================================================================
    # Safe executable actions (idempotent, no canonical mutation)
    # =========================================================================

    SAFE_ACTION_IDS: frozenset[str] = frozenset({
        "refresh-impact-analysis",
        "refresh-decision-snapshots",
        "run-candidate-comparison",
        "run-deterministic-validation",
        "generate-reconciliation-proposals",
        "inspect-reasoning-evidence",
        "prepare-acceptance-evidence",
    })

    def refresh_snapshots(self, decision_id: str | None = None) -> dict[str, Any]:
        """Re-assemble and persist updated snapshots.

        Idempotent: skips writes when content is unchanged.
        """
        try:
            if decision_id:
                decision = self.inspect(decision_id)
                preceding = self._compute_preceding_snapshot_id(decision_id)
                sid = self.decision_store.save_snapshot(decision, preceding_snapshot_id=preceding)
                self.decision_store.save_latest_pointer(decision)
                return {"status": "ok", "snapshot_id": sid, "decision_id": decision_id}

            decisions = self.list_decisions()
            saved = 0
            for d in decisions:
                try:
                    preceding = self._compute_preceding_snapshot_id(d.decision_id)
                    self.decision_store.save_snapshot(d, preceding_snapshot_id=preceding)
                    self.decision_store.save_latest_pointer(d)
                    saved += 1
                except Exception as e:
                    logger.warning(f"Failed to save snapshot for {d.decision_id}: {e}")
            return {"status": "ok", "saved": saved, "total": len(decisions)}
        except Exception as e:
            logger.exception("Error refreshing snapshots")
            return {"status": "failed", "error": str(e)}

    def run_comparison(self, decision_id: str) -> dict[str, Any]:
        """Run deterministic candidate comparison for a decision."""
        try:
            decision = self.inspect(decision_id)
            if len(decision.candidates) < 2:
                return {"status": "skipped", "reason": "Fewer than 2 candidates"}

            from auteur.convergence.comparison import compare_candidates
            target_id = decision.target_artifact_id
            candidates_data = self.convergence_store.list_candidates(target_id)
            if not candidates_data:
                return {"status": "skipped", "reason": "No candidate data in store"}

            from auteur.convergence.models import CandidateRef
            candidates = [CandidateRef(**cd) for cd in candidates_data]
            if len(candidates) >= 2:
                result = compare_candidates(candidates[0], candidates[1])
                self.convergence_store.save_comparison(result)
                return {"status": "ok", "comparison_id": result.comparison_id}
            return {"status": "skipped", "reason": "Need at least 2 CandidateRef objects"}
        except Exception as e:
            logger.exception(f"Error running comparison for {decision_id}")
            return {"status": "failed", "error": str(e)}

    def run_validation(self, decision_id: str) -> dict[str, Any]:
        """Run deterministic validation on a decision."""
        try:
            decision = self.inspect(decision_id)
            issues: list[str] = []
            if not decision.candidates:
                issues.append("No candidates")
            if not decision.evidence:
                issues.append("No evidence")
            if decision.readiness.value == "blocked":
                issues.extend(decision.blockers)
            return {"status": "ok", "decision_id": decision_id, "issues": issues, "issue_count": len(issues)}
        except Exception as e:
            logger.exception(f"Error validating {decision_id}")
            return {"status": "failed", "error": str(e)}

    def inspect_evidence(self, decision_id: str, source: str | None = None) -> dict[str, Any]:
        """Inspect evidence for a decision, optionally filtered by source."""
        try:
            decision = self.inspect(decision_id)
            evidence = decision.evidence
            if source:
                from auteur.decision.models import EvidenceSource
                try:
                    source_enum = EvidenceSource(source)
                    evidence = [e for e in evidence if e.source_subsystem == source_enum]
                except ValueError:
                    return {"status": "failed", "error": f"Unknown evidence source: {source}"}

            return {
                "status": "ok",
                "decision_id": decision_id,
                "evidence_count": len(evidence),
                "evidence": [
                    {"id": e.evidence_id, "source": e.source_subsystem.value,
                     "type": e.evidence_type.value, "claim": e.claim[:200],
                     "freshness": e.freshness.value}
                    for e in evidence
                ],
            }
        except Exception as e:
            logger.exception(f"Error inspecting evidence for {decision_id}")
            return {"status": "failed", "error": str(e)}

    def refresh_snapshots(self, decision_id: str | None = None) -> dict[str, Any]:
        """Re-assemble and persist updated snapshots.

        Idempotent: skips writes when content is unchanged.
        If a decision exists only in the snapshot store (not live state),
        it is preserved as-is.
        """
        try:
            if decision_id:
                try:
                    decision = self.inspect(decision_id)
                except ValueError:
                    # Decision not in live state — try snapshot store
                    decision = self.decision_store.load_snapshot(decision_id)
                    if decision is None:
                        return {"status": "failed", "error": f"Decision not found: {decision_id}"}
                preceding = self._compute_preceding_snapshot_id(decision_id)
                sid = self.decision_store.save_snapshot(decision, preceding_snapshot_id=preceding)
                self.decision_store.save_latest_pointer(decision)
                return {"status": "ok", "snapshot_id": sid, "decision_id": decision_id}

            decisions = self.list_decisions()
            saved = 0
            for d in decisions:
                try:
                    preceding = self._compute_preceding_snapshot_id(d.decision_id)
                    self.decision_store.save_snapshot(d, preceding_snapshot_id=preceding)
                    self.decision_store.save_latest_pointer(d)
                    saved += 1
                except Exception as e:
                    logger.warning(f"Failed to save snapshot for {d.decision_id}: {e}")
            return {"status": "ok", "saved": saved, "total": len(decisions)}
        except Exception as e:
            logger.exception("Error refreshing snapshots")
            return {"status": "failed", "error": str(e)}

    # =========================================================================
    # Private: Subsystem integration
    # =========================================================================

    def _load_impact_findings(self, force: bool = False) -> list[ImpactFinding]:
        """Load impact findings from impact subsystem."""
        try:
            # Check for persisted analyses
            if not force and self.impact_store.has_any():
                reports = self.impact_store.list_reports()
                if reports:
                    # Load latest report
                    latest_report = self.impact_store.get_latest()
                    if latest_report and latest_report.findings:
                        return latest_report.findings

            # Run analyzer for fresh findings
            from auteur.impact.analyzer import ImpactAnalyzer

            analyzer = ImpactAnalyzer(self.project_root)
            findings = analyzer.analyze()
            return findings
        except Exception as e:
            logger.warning(f"Could not load impact findings: {e}")
            return []

    def _load_convergence_targets(self, force: bool = False) -> list[RevisionTarget]:
        """Load convergence targets from convergence subsystem."""
        try:
            targets_data = self.convergence_store.list_targets()
            return [RevisionTarget(**t) for t in targets_data]
        except Exception as e:
            logger.warning(f"Could not load convergence targets: {e}")
            return []

    def _decision_from_impact_finding(self, finding: ImpactFinding) -> AuthorDecision:
        """Assemble decision from impact finding."""
        if not finding.affected_artifact:
            logger.warning(f"Impact finding {finding.finding_id} missing affected_artifact")
            return AuthorDecision(
                decision_id="unknown",
                project=str(self.project_root),
                chapter_index=0,
                target_artifact_id="unknown",
                blockers=["Missing affected artifact"],
                readiness=DecisionReadiness.BLOCKED,
            )

        decision = self.assembler.assemble_from_impact(
            project=str(self.project_root),
            chapter_index=finding.affected_artifact.chapter_index or 0,
            scene_id=None,
            impact_finding_id=finding.finding_id,
            target_artifact_id=finding.affected_artifact.artifact_id,
        )

        # Add evidence from impact finding
        evidence = DecisionEvidence.create(
            source_subsystem=EvidenceSource.IMPACT,
            source_artifact_id=finding.finding_id,
            claim=finding.reason,
            evidence_type=EvidenceType.IMPACT_FINDING,
            classification=EvidenceClassification.FACT,
            freshness=self._map_impact_severity_to_freshness(finding.severity),
            supporting_reference=finding.affected_artifact.artifact_id,
        )
        decision = self._update_decision_evidence(decision, [evidence])

        # Update readiness based on finding severity
        decision = self._update_decision_readiness(decision)
        return decision

    def _decision_from_convergence_target(self, target: RevisionTarget) -> AuthorDecision:
        """Assemble decision from convergence target with real reasoning evidence."""
        decision = self.assembler.assemble_from_convergence(
            project=target.project,
            chapter_index=target.chapter_index,
            scene_id=target.scene_id,
            target_id=target.target_id,
            target_artifact_id=target.affected_artifact,
        )

        # Load candidates for this target
        candidates_data = self.convergence_store.list_candidates(target.target_id)
        candidates = []

        for cand_data in candidates_data:
            try:
                cand_ref = CandidateRef(**cand_data)

                # Load reasoning evidence via adapter instead of evaluation_references
                reasoning_evidence = list(cand_ref.evaluation_references)  # legacy compat
                try:
                    reports = self.reasoning_adapter.get_candidate_reports(
                        cand_ref.candidate_id, target.chapter_index,
                    )
                    if reports:
                        # Convert reports to evidence references
                        reasoning_evidence = [r.get("review_id", r.get("run_id", "unknown")) for r in reports]
                except Exception:
                    # Fall back to legacy evaluation_references
                    pass

                summary = CandidateSummary(
                    candidate_id=cand_ref.candidate_id,
                    status=cand_ref.status.value,
                    freshness=self._map_candidate_freshness(cand_ref.freshness),
                    obligations_satisfied=cand_ref.obligations_satisfied,
                    obligations_unsatisfied=cand_ref.obligations_unsatisfied,
                    preserved_regions=[r.region_id for r in cand_ref.preserved_regions],
                    reasoning_evidence=reasoning_evidence,
                    reconciliation_status=None,
                )
                candidates.append(summary)
            except Exception as e:
                logger.warning(f"Failed to load candidate {cand_data.get('candidate_id')}: {e}")

        decision = AuthorDecision(
            decision_id=decision.decision_id,
            project=decision.project,
            chapter_index=decision.chapter_index,
            scene_id=decision.scene_id,
            beat_ids=decision.beat_ids,
            target_artifact_id=decision.target_artifact_id,
            trigger_type=decision.trigger_type,
            trigger_ids=decision.trigger_ids,
            candidates=candidates,
            readiness=decision.readiness,
        )

        # Update readiness
        decision = self._update_decision_readiness(decision)
        return decision

    def _enrich_decision(self, decision: AuthorDecision) -> AuthorDecision:
        """Enrich decision with full details from subsystems."""
        # Load full evidence details
        evidence: list[DecisionEvidence] = list(decision.evidence)

        # Add evidence from impact findings if this is impact-triggered
        if decision.trigger_type == DecisionTrigger.IMPACT_FINDING:
            for finding_id in decision.trigger_ids:
                try:
                    pass
                except Exception as e:
                    logger.warning(f"Could not load impact finding {finding_id}: {e}")

        # Add reasoning evidence for each candidate
        for candidate in decision.candidates:
            try:
                reports = self.reasoning_adapter.get_candidate_reports(
                    candidate.candidate_id, decision.chapter_index,
                )
                for report in reports:
                    evidence.extend(
                        self.reasoning_adapter.reasoning_to_evidence(
                            report, candidate_id=candidate.candidate_id,
                        )
                    )
            except Exception as e:
                logger.debug(f"Could not load reasoning evidence for {candidate.candidate_id}: {e}")

        # Add evidence from reconciliation proposals if available
        try:
            proposals = self.convergence_store.list_proposals(decision.target_artifact_id)
            for proposal in proposals:
                if proposal.get("conflicts"):
                    for conflict in proposal["conflicts"]:
                        evidence.append(
                            DecisionEvidence.create(
                                source_subsystem=EvidenceSource.RECONCILIATION,
                                source_artifact_id=proposal.get("proposal_id", "unknown"),
                                claim=conflict.get("description", ""),
                                evidence_type=EvidenceType.RECONCILIATION_CONFLICT,
                                classification=EvidenceClassification.DERIVED_INFERENCE,
                                freshness=EvidenceFreshness.CURRENT,
                            )
                        )
        except Exception as e:
            logger.warning(f"Could not load reconciliation proposals: {e}")

        # Return enriched decision
        return AuthorDecision(
            decision_id=decision.decision_id,
            project=decision.project,
            chapter_index=decision.chapter_index,
            scene_id=decision.scene_id,
            beat_ids=decision.beat_ids,
            target_artifact_id=decision.target_artifact_id,
            trigger_type=decision.trigger_type,
            trigger_ids=decision.trigger_ids,
            candidates=decision.candidates,
            evidence=evidence,
            readiness=decision.readiness,
            lifecycle_state=decision.lifecycle_state,
            freshness=decision.freshness,
            blockers=decision.blockers,
        )

    def _update_decision_evidence(
        self,
        decision: AuthorDecision,
        new_evidence: list[DecisionEvidence],
    ) -> AuthorDecision:
        """Add evidence to a decision."""
        combined = list(decision.evidence) + new_evidence
        return AuthorDecision(
            decision_id=decision.decision_id,
            project=decision.project,
            chapter_index=decision.chapter_index,
            scene_id=decision.scene_id,
            beat_ids=decision.beat_ids,
            target_artifact_id=decision.target_artifact_id,
            trigger_type=decision.trigger_type,
            trigger_ids=decision.trigger_ids,
            candidates=decision.candidates,
            evidence=combined,
            readiness=decision.readiness,
            lifecycle_state=decision.lifecycle_state,
            freshness=decision.freshness,
            blockers=decision.blockers,
        )

    def _update_decision_readiness(self, decision: AuthorDecision) -> AuthorDecision:
        """Recompute readiness from current evidence."""
        readiness = self.assembler.compute_readiness(decision)
        freshness = self.assembler.detect_freshness(decision)
        lifecycle_state = self.assembler.derive_lifecycle_state(decision)

        return AuthorDecision(
            decision_id=decision.decision_id,
            project=decision.project,
            chapter_index=decision.chapter_index,
            scene_id=decision.scene_id,
            beat_ids=decision.beat_ids,
            target_artifact_id=decision.target_artifact_id,
            trigger_type=decision.trigger_type,
            trigger_ids=decision.trigger_ids,
            candidates=decision.candidates,
            evidence=decision.evidence,
            readiness=readiness,
            lifecycle_state=lifecycle_state,
            freshness=freshness,
            blockers=decision.blockers,
        )

    def _finding_has_decision(self, finding: ImpactFinding) -> bool:
        """Check if an impact finding already has an open decision."""
        # Would check persisted decisions for this finding
        return False

    def _map_impact_severity_to_freshness(self, severity: Any) -> EvidenceFreshness:
        """Map impact severity to evidence freshness."""
        severity_str = severity.value if hasattr(severity, "value") else str(severity)
        if severity_str in ("blocked", "reconcile"):
            return EvidenceFreshness.CURRENT
        return EvidenceFreshness.CURRENT

    def _map_candidate_freshness(self, freshness_str: str) -> EvidenceFreshness:
        """Map candidate freshness string to enum."""
        if freshness_str == "stale":
            return EvidenceFreshness.STALE
        return EvidenceFreshness.CURRENT

    def _predict_downstream_impact(self, candidate_id: str) -> list[str]:
        """Predict downstream artifacts affected by candidate acceptance."""
        # Would use impact analyzer to predict downstream changes
        return []

    def _get_highest_priority_readiness(self, decisions: list[AuthorDecision]) -> str:
        """Determine highest priority readiness across decisions."""
        if not decisions:
            return "none"

        priority = [
            DecisionReadiness.BLOCKED,
            DecisionReadiness.NEEDS_AUTHOR_DECISION,
            DecisionReadiness.NEEDS_RECONCILIATION,
            DecisionReadiness.NEEDS_COMPARISON,
            DecisionReadiness.NEEDS_EVALUATION,
            DecisionReadiness.NEEDS_CANDIDATE,
            DecisionReadiness.READY_FOR_ACCEPTANCE,
            DecisionReadiness.RESOLVED,
            DecisionReadiness.STALE,
        ]

        for readiness in priority:
            if any(d.readiness == readiness for d in decisions):
                return readiness.value

        return "none"
