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
from auteur.impact.models import ImpactFinding
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

    def list_decisions(self, chapter_index: int | None = None) -> list[AuthorDecision]:
        """List assembled decisions from real subsystem state."""
        try:
            decisions: dict[str, AuthorDecision] = {}

            # Decisions from impact findings
            impact_findings = self._load_impact_findings()
            for finding in impact_findings:
                decision = self._decision_from_impact_finding(finding)
                if chapter_index is None or decision.chapter_index == chapter_index:
                    decisions[decision.decision_id] = decision

            # Decisions from convergence targets
            targets = self._load_convergence_targets()
            for target in targets:
                decision = self._decision_from_convergence_target(target)
                if chapter_index is None or decision.chapter_index == chapter_index:
                    decisions[decision.decision_id] = decision

            # Load persisted snapshots to refresh state
            for decision_id in self.decision_store.list_snapshots():
                if decision_id not in decisions:
                    # Load from persistence if not reassembled from subsystems
                    pass  # Snapshots are metadata-only in current persistence design

            return sorted(decisions.values(), key=lambda d: (d.chapter_index, d.decision_id))
        except Exception as e:
            logger.exception("Error listing decisions")
            raise

    def inspect(self, decision_id: str) -> AuthorDecision:
        """Get full decision detail with all evidence."""
        try:
            decisions = self.list_decisions()
            decision = next((d for d in decisions if d.decision_id == decision_id), None)

            if decision is None:
                raise ValueError(f"Decision not found: {decision_id}")

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
        """Verify acceptance readiness without performing acceptance."""
        try:
            decision = self.inspect(decision_id)

            # Verify candidate exists in decision
            candidate = next((c for c in decision.candidates if c.candidate_id == candidate_id), None)
            if candidate is None:
                return AcceptancePreparation(
                    decision_id=decision_id,
                    candidate_id=candidate_id,
                    is_ready=False,
                    blockers=["Candidate not found in decision"],
                )

            # Check acceptance prerequisites
            blockers = []
            verification_results = {}

            # 1. Verify candidate freshness
            if candidate.freshness == EvidenceFreshness.STALE:
                blockers.append("Candidate is stale")
            verification_results["candidate_freshness_current"] = candidate.freshness == EvidenceFreshness.CURRENT

            # 2. Verify reasoning evidence
            if not candidate.reasoning_evidence:
                blockers.append("Candidate lacks reasoning evidence")
            verification_results["reasoning_evidence_present"] = len(candidate.reasoning_evidence) > 0

            # 3. Verify obligations satisfied
            unsatisfied = candidate.obligations_unsatisfied
            if unsatisfied:
                blockers.append(f"Unsatisfied obligations: {len(unsatisfied)}")
            verification_results["obligations_satisfied"] = len(unsatisfied) == 0

            # 4. Verify no unresolved author choices
            if decision.has_open_choices():
                blockers.append("Decision has unresolved author choices")
            verification_results["author_choices_resolved"] = not decision.has_open_choices()

            # 5. Verify reconciliation conflicts resolved
            has_unresolved_conflicts = any(
                e.evidence_type == EvidenceType.RECONCILIATION_CONFLICT
                and e.freshness == EvidenceFreshness.CURRENT
                for e in decision.evidence
            )
            if has_unresolved_conflicts:
                blockers.append("Reconciliation conflicts remain")
            verification_results["reconciliation_resolved"] = not has_unresolved_conflicts

            # 6. Check downstream impact
            affected_downstream = self._predict_downstream_impact(candidate_id)

            is_ready = len(blockers) == 0
            return AcceptancePreparation(
                decision_id=decision_id,
                candidate_id=candidate_id,
                is_ready=is_ready,
                blockers=blockers,
                verification_results=verification_results,
                affected_downstream=affected_downstream,
            )
        except Exception as e:
            logger.exception(f"Error preparing acceptance for {decision_id}")
            raise

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
        """Assemble decision from convergence target."""
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
                summary = CandidateSummary(
                    candidate_id=cand_ref.candidate_id,
                    status=cand_ref.status.value,
                    freshness=self._map_candidate_freshness(cand_ref.freshness),
                    obligations_satisfied=cand_ref.obligations_satisfied,
                    obligations_unsatisfied=cand_ref.obligations_unsatisfied,
                    preserved_regions=[r.region_id for r in cand_ref.preserved_regions],
                    reasoning_evidence=cand_ref.evaluation_references,
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
                    # Would load finding details here if needed
                    pass
                except Exception as e:
                    logger.warning(f"Could not load impact finding {finding_id}: {e}")

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
