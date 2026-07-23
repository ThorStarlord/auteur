"""Assemble decisions from existing subsystem state."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from auteur.decision.models import (
    AuthorDecision,
    DecisionAction,
    DecisionConflict,
    DecisionEvidence,
    DecisionReadiness,
    DecisionTrigger,
    EvidenceClassification,
    EvidenceFreshness,
    EvidenceSource,
    EvidenceType,
    LifecycleState,
    UnresolvedChoice,
)
from auteur.workflow.models import AuthorityLevel


class DecisionAssembler:
    """Compose decisions from impact, convergence, reasoning, reconciliation state."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def compute_decision_id(
        self,
        project: str,
        trigger_type: DecisionTrigger,
        chapter_index: int,
        scene_id: str | None,
        beat_ids: list[str],
        target_artifact_id: str,
        trigger_ids: list[str],
    ) -> str:
        """Compute stable deterministic decision ID."""
        key_parts = [
            project,
            trigger_type.value,
            str(chapter_index),
            scene_id or "",
            ",".join(sorted(beat_ids)),
            target_artifact_id,
            ",".join(sorted(trigger_ids)),
        ]
        key = "|".join(key_parts)
        digest = hashlib.sha256(key.encode()).hexdigest()
        return digest[:16]

    def assemble_from_impact(
        self,
        project: str,
        chapter_index: int,
        scene_id: str | None,
        impact_finding_id: str,
        target_artifact_id: str,
    ) -> AuthorDecision:
        """Assemble a decision triggered by an impact finding."""
        decision_id = self.compute_decision_id(
            project=project,
            trigger_type=DecisionTrigger.IMPACT_FINDING,
            chapter_index=chapter_index,
            scene_id=scene_id,
            beat_ids=[],
            target_artifact_id=target_artifact_id,
            trigger_ids=[impact_finding_id],
        )

        # Basic decision structure
        decision = AuthorDecision(
            decision_id=decision_id,
            project=project,
            chapter_index=chapter_index,
            scene_id=scene_id,
            target_artifact_id=target_artifact_id,
            trigger_type=DecisionTrigger.IMPACT_FINDING,
            trigger_ids=[impact_finding_id],
            readiness=DecisionReadiness.NEEDS_CANDIDATE,
            lifecycle_state=LifecycleState.OPEN,
        )

        return decision

    def assemble_from_convergence(
        self,
        project: str,
        chapter_index: int,
        scene_id: str | None,
        target_id: str,
        target_artifact_id: str,
    ) -> AuthorDecision:
        """Assemble a decision from a convergence target."""
        decision_id = self.compute_decision_id(
            project=project,
            trigger_type=DecisionTrigger.CONVERGENCE_TARGET,
            chapter_index=chapter_index,
            scene_id=scene_id,
            beat_ids=[],
            target_artifact_id=target_artifact_id,
            trigger_ids=[target_id],
        )

        decision = AuthorDecision(
            decision_id=decision_id,
            project=project,
            chapter_index=chapter_index,
            scene_id=scene_id,
            target_artifact_id=target_artifact_id,
            trigger_type=DecisionTrigger.CONVERGENCE_TARGET,
            trigger_ids=[target_id],
            readiness=DecisionReadiness.NEEDS_CANDIDATE,
            lifecycle_state=LifecycleState.OPEN,
        )

        return decision

    def compute_readiness(
        self,
        decision: AuthorDecision,
    ) -> DecisionReadiness:
        """Determine readiness from decision state."""
        # Check for blockers first
        if decision.blockers:
            return DecisionReadiness.BLOCKED

        # Check for stale evidence
        if decision.freshness == EvidenceFreshness.STALE:
            return DecisionReadiness.STALE

        # Check for stale candidates
        stale_candidates = [c for c in decision.candidates if c.freshness == EvidenceFreshness.STALE]
        if decision.candidates and stale_candidates and len(stale_candidates) == len(decision.candidates):
            return DecisionReadiness.NEEDS_CANDIDATE

        # No candidates
        if not decision.candidates:
            return DecisionReadiness.NEEDS_CANDIDATE

        # Has candidates but some lack evaluation
        unevaluated = [c for c in decision.candidates if not c.reasoning_evidence]
        if unevaluated:
            return DecisionReadiness.NEEDS_EVALUATION

        # Multiple candidates, no comparison
        if len(decision.candidates) > 1 and not any(e.evidence_type == EvidenceType.COMPARISON_RESULT for e in decision.evidence):
            return DecisionReadiness.NEEDS_COMPARISON

        # Check for unresolved reconciliation conflicts
        has_reconciliation_conflict = any(
            e.evidence_type == EvidenceType.RECONCILIATION_CONFLICT for e in decision.evidence
        )
        if has_reconciliation_conflict:
            return DecisionReadiness.NEEDS_RECONCILIATION

        # Check for unresolved author choices
        if decision.has_open_choices():
            return DecisionReadiness.NEEDS_AUTHOR_DECISION

        # All prerequisites met
        return DecisionReadiness.READY_FOR_ACCEPTANCE

    def detect_freshness(self, decision: AuthorDecision) -> EvidenceFreshness:
        """Detect if decision is stale."""
        stale_evidence = [e for e in decision.evidence if e.freshness == EvidenceFreshness.STALE]
        if stale_evidence:
            return EvidenceFreshness.STALE

        unknown_evidence = [e for e in decision.evidence if e.freshness == EvidenceFreshness.UNKNOWN]
        if unknown_evidence:
            return EvidenceFreshness.UNKNOWN

        return EvidenceFreshness.CURRENT

    def derive_lifecycle_state(self, decision: AuthorDecision) -> LifecycleState:
        """Derive lifecycle state from readiness and freshness."""
        if decision.freshness == EvidenceFreshness.STALE:
            return LifecycleState.STALE

        if decision.readiness == DecisionReadiness.BLOCKED:
            return LifecycleState.BLOCKED

        if decision.readiness == DecisionReadiness.READY_FOR_ACCEPTANCE:
            return LifecycleState.READY_FOR_ACCEPTANCE

        if decision.readiness == DecisionReadiness.NEEDS_AUTHOR_DECISION:
            return LifecycleState.AUTHOR_DECISION_REQUIRED

        return LifecycleState.EVIDENCE_INCOMPLETE

    def compute_next_action(self, decision: AuthorDecision) -> DecisionAction | None:
        """Recommend primary next action."""
        if decision.blockers:
            return DecisionAction(
                action_id="fix-blockers",
                title="Fix data issues",
                reason="Decision has malformed or missing data",
                safe_to_execute=False,
                authority_level=AuthorityLevel.AUTHORITY_BEARING,
            )

        if decision.readiness == DecisionReadiness.NEEDS_CANDIDATE:
            return DecisionAction(
                action_id="generate-candidate",
                title=f"Generate candidate for {decision.target_artifact_id}",
                reason="No viable candidate exists",
                command=f"auteur realization generate-candidate --chapter {decision.chapter_index}" +
                        (f" --scene {decision.scene_id}" if decision.scene_id else ""),
                safe_to_execute=True,
                authority_level=AuthorityLevel.CANDIDATE_GENERATION,
                expected_result_state="NEEDS_EVALUATION",
            )

        if decision.readiness == DecisionReadiness.NEEDS_EVALUATION:
            candidate = decision.candidates[0] if decision.candidates else None
            if candidate:
                return DecisionAction(
                    action_id="evaluate-candidate",
                    title=f"Evaluate {candidate.candidate_id}",
                    reason="Candidate exists but lacks reasoning review",
                    command=f"auteur reasoning evaluate --candidate {candidate.candidate_id}",
                    safe_to_execute=True,
                    authority_level=AuthorityLevel.CANDIDATE_GENERATION,
                    expected_result_state="NEEDS_COMPARISON",
                )

        if decision.readiness == DecisionReadiness.NEEDS_COMPARISON:
            return DecisionAction(
                action_id="compare-candidates",
                title=f"Compare candidates for {decision.target_artifact_id}",
                reason="Multiple candidates exist, no comparison",
                command=f"auteur decision compare {decision.decision_id}",
                safe_to_execute=True,
                authority_level=AuthorityLevel.DERIVED_ARTIFACT,
                expected_result_state="NEEDS_RECONCILIATION",
            )

        if decision.readiness == DecisionReadiness.NEEDS_RECONCILIATION:
            return DecisionAction(
                action_id="resolve-conflicts",
                title="Review and resolve reconciliation conflicts",
                reason="Conflicts detected between candidates",
                command=f"auteur decision inspect {decision.decision_id}",
                safe_to_execute=False,
                authority_level=AuthorityLevel.AUTHORITY_BEARING,
                expected_result_state="NEEDS_AUTHOR_DECISION",
            )

        if decision.readiness == DecisionReadiness.NEEDS_AUTHOR_DECISION:
            choice = next((c for c in decision.unresolved_choices if c.blocking_status), None)
            if choice:
                return DecisionAction(
                    action_id="author-decision",
                    title=f"Make decision: {choice.question}",
                    reason="Creative choice required",
                    command=f"auteur decision inspect {decision.decision_id}",
                    safe_to_execute=False,
                    authority_level=AuthorityLevel.AUTHORITY_BEARING,
                    expected_result_state="READY_FOR_ACCEPTANCE",
                )

        if decision.readiness == DecisionReadiness.READY_FOR_ACCEPTANCE:
            candidate = decision.candidates[0] if decision.candidates else None
            if candidate:
                return DecisionAction(
                    action_id="prepare-acceptance",
                    title=f"Prepare acceptance of {candidate.candidate_id}",
                    reason="Candidate ready for author decision",
                    command=f"auteur decision prepare-acceptance {decision.decision_id} --candidate {candidate.candidate_id}",
                    safe_to_execute=True,
                    authority_level=AuthorityLevel.DERIVED_ARTIFACT,
                    expected_result_state="RESOLVED",
                )

        return None

    def to_dict(self, decision: AuthorDecision) -> dict[str, Any]:
        """Serialize decision to dict including schema and lineage metadata."""
        return {
            "schema_version": decision.schema_version,
            "snapshot_id": decision.snapshot_id,
            "preceding_snapshot_id": decision.preceding_snapshot_id,
            "decision_id": decision.decision_id,
            "project": decision.project,
            "chapter_index": decision.chapter_index,
            "scene_id": decision.scene_id,
            "beat_ids": decision.beat_ids,
            "target_artifact_id": decision.target_artifact_id,
            "trigger_type": decision.trigger_type.value,
            "trigger_ids": decision.trigger_ids,
            "readiness": decision.readiness.value,
            "lifecycle_state": decision.lifecycle_state.value,
            "freshness": decision.freshness.value,
            "authority_required": decision.authority_required.value,
            "blockers": decision.blockers,
            "created_at": decision.created_at.isoformat(),
            "last_updated_at": decision.last_updated_at.isoformat(),
        }
