"""Conflict detector — identifies factual, structural, interpretive, and creative conflicts
across evidence from impact, reasoning, convergence, and reconciliation subsystems."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from auteur.decision.models import (
    ConflictType,
    DecisionConflict,
    DecisionEvidence,
    EvidenceClassification,
    EvidenceFreshness,
    EvidenceSource,
    EvidenceType,
    ResolutionBoundary,
)


class ConflictDetector:
    """Detect and classify conflicts across decision evidence.

    Each conflict records all subsystem claims involved — no single
    subsystem is silently authoritative. The detector recommends a
    resolution boundary based on conflict type.
    """

    def detect_conflicts(self, decision_id: str, evidence: list[DecisionEvidence]) -> list[DecisionConflict]:
        """Detect all active conflicts from evidence list.

        Scans evidence pairwise by artifact/candidate to identify
        contradictory claims across subsystems.
        """
        conflicts: list[DecisionConflict] = []
        fresh_evidence = [e for e in evidence if e.freshness == EvidenceFreshness.CURRENT]

        # 1. Factual conflicts: same artifact, different content hashes
        conflicts.extend(self._detect_factual_conflicts(fresh_evidence))

        # 2. Structural conflicts: composition/ordering disagreement
        conflicts.extend(self._detect_structural_conflicts(fresh_evidence))

        # 3. Interpretive conflicts: reasoning critics disagree
        conflicts.extend(self._detect_interpretive_conflicts(fresh_evidence))

        # 4. Creative conflicts: author intention vs realized state
        conflicts.extend(self._detect_creative_conflicts(fresh_evidence))

        # Deduplicate by title similarity within same candidates
        return self._deduplicate(conflicts)

    # ------------------------------------------------------------------
    # Conflict type detectors
    # ------------------------------------------------------------------

    def _detect_factual_conflicts(self, evidence: list[DecisionEvidence]) -> list[DecisionConflict]:
        """Detect factual conflicts: same target, contradictory claims across subsystems.

        Example: impact says content_hash=X, reasoning recorded hash=Y.
        """
        conflicts: list[DecisionConflict] = []
        by_artifact: dict[str, list[DecisionEvidence]] = {}

        for ev in evidence:
            if ev.supporting_reference:
                key = ev.supporting_reference
                by_artifact.setdefault(key, []).append(ev)

        for artifact_id, ev_list in by_artifact.items():
            factual_pairs = self._find_contradictory_pairs(ev_list)

            for ev_a, ev_b in factual_pairs:
                # Same artifact, different subsystems, same classification = factual
                if ev_a.source_subsystem != ev_b.source_subsystem:
                    if ev_a.classification == EvidenceClassification.FACT and ev_b.classification == EvidenceClassification.FACT:
                        conflicts.append(DecisionConflict.create(
                            title=f"Factual conflict: {artifact_id[:16]}...",
                            conflict_type=ConflictType.FACTUAL,
                            resolution_boundary=ResolutionBoundary.RECOMPUTE,
                            source_subsystem=ev_a.source_subsystem,
                            claim_a=ev_a.claim,
                            claim_b=ev_b.claim,
                            claims=[
                                {"subsystem": ev_a.source_subsystem.value, "claim": ev_a.claim, "artifact": ev_a.source_artifact_id},
                                {"subsystem": ev_b.source_subsystem.value, "claim": ev_b.claim, "artifact": ev_b.source_artifact_id},
                            ],
                            affected_candidates=[ev_a.candidate_id] if ev_a.candidate_id else [],
                        ))

        return conflicts

    def _detect_structural_conflicts(self, evidence: list[DecisionEvidence]) -> list[DecisionConflict]:
        """Detect structural conflicts: ordering or composition disagreements.

        Example: structure says scene A→B→C, realization has B→A→C.
        """
        conflicts: list[DecisionConflict] = []
        # Structural conflicts manifest as impact findings touching composition
        structural = [
            e for e in evidence
            if e.evidence_type in (EvidenceType.STRUCTURAL_FACT, EvidenceType.OBLIGATION_STATUS)
        ]

        for i, ev_a in enumerate(structural):
            for ev_b in structural[i + 1:]:
                if ev_a.candidate_id == ev_b.candidate_id and ev_a.claim != ev_b.claim:
                    conflicts.append(DecisionConflict.create(
                        title=f"Structural conflict: {ev_a.source_artifact_id} vs {ev_b.source_artifact_id}",
                        conflict_type=ConflictType.STRUCTURAL,
                        resolution_boundary=ResolutionBoundary.RECONCILE,
                        source_subsystem=ev_a.source_subsystem,
                        claim_a=ev_a.claim,
                        claim_b=ev_b.claim,
                        claims=[
                            {"subsystem": ev_a.source_subsystem.value, "claim": ev_a.claim, "artifact": ev_a.source_artifact_id},
                            {"subsystem": ev_b.source_subsystem.value, "claim": ev_b.claim, "artifact": ev_b.source_artifact_id},
                        ],
                        affected_candidates=[ev_a.candidate_id] if ev_a.candidate_id else [],
                    ))

        return conflicts

    def _detect_interpretive_conflicts(self, evidence: list[DecisionEvidence]) -> list[DecisionConflict]:
        """Detect interpretive conflicts: reasoning critics disagree on evaluation.

        Example: structure critic says "valid arc", dialogue critic says "tone mismatch".
        """
        conflicts: list[DecisionConflict] = []
        reasoning = [e for e in evidence if e.source_subsystem == EvidenceSource.REASONING]

        for i, ev_a in enumerate(reasoning):
            for ev_b in reasoning[i + 1:]:
                if ev_a.candidate_id == ev_b.candidate_id and ev_a.candidate_id is not None:
                    # Different classifications from reasoning = interpretive disagreement
                    if ev_a.classification != ev_b.classification and ev_a.classification in (
                        EvidenceClassification.DERIVED_INFERENCE,
                        EvidenceClassification.RECOMMENDATION,
                    ):
                        conflicts.append(DecisionConflict.create(
                            title=f"Interpretive conflict: {ev_a.source_artifact_id} vs {ev_b.source_artifact_id}",
                            conflict_type=ConflictType.INTERPRETIVE,
                            resolution_boundary=ResolutionBoundary.REQUEST_AUTHOR_CHOICE,
                            source_subsystem=EvidenceSource.REASONING,
                            claim_a=ev_a.claim,
                            claim_b=ev_b.claim,
                            claims=[
                                {"subsystem": "reasoning", "claim": ev_a.claim, "artifact": ev_a.source_artifact_id},
                                {"subsystem": "reasoning", "claim": ev_b.claim, "artifact": ev_b.source_artifact_id},
                            ],
                            affected_candidates=[ev_a.candidate_id],
                        ))

        return conflicts

    def _detect_creative_conflicts(self, evidence: list[DecisionEvidence]) -> list[DecisionConflict]:
        """Detect creative conflicts: author intention vs realized state.

        Example: identity specifies 'tragic mode', realization draft is comedic.
        """
        conflicts: list[DecisionConflict] = []
        # Look for AUTHOR_CHOICE evidence in tension with FACT/STRUCTURAL evidence
        author_choices = [e for e in evidence if e.classification == EvidenceClassification.AUTHOR_CHOICE]
        factuals = [e for e in evidence if e.classification == EvidenceClassification.FACT]

        for ac in author_choices:
            for fact in factuals:
                if ac.candidate_id == fact.candidate_id or (ac.candidate_id is None and fact.candidate_id is not None):
                    conflicts.append(DecisionConflict.create(
                        title=f"Creative conflict: author intention vs realized state",
                        conflict_type=ConflictType.CREATIVE,
                        resolution_boundary=ResolutionBoundary.BLOCK_ACCEPTANCE,
                        source_subsystem=ac.source_subsystem,
                        claim_a=ac.claim,
                        claim_b=fact.claim,
                        claims=[
                            {"subsystem": ac.source_subsystem.value, "claim": ac.claim, "artifact": ac.source_artifact_id, "classification": "author_choice"},
                            {"subsystem": fact.source_subsystem.value, "claim": fact.claim, "artifact": fact.source_artifact_id, "classification": "fact"},
                        ],
                        affected_candidates=[fact.candidate_id] if fact.candidate_id else [],
                    ))

        return conflicts

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_contradictory_pairs(evidence: list[DecisionEvidence]) -> list[tuple[DecisionEvidence, DecisionEvidence]]:
        """Find pairs of evidence that make contradictory claims.

        Heuristic: same supporting_reference + different source subsystem +
        different claim text = potential contradiction.
        """
        pairs: list[tuple[DecisionEvidence, DecisionEvidence]] = []
        for i, ev_a in enumerate(evidence):
            for ev_b in evidence[i + 1:]:
                if ev_a.supporting_reference == ev_b.supporting_reference:
                    if ev_a.source_subsystem != ev_b.source_subsystem:
                        if ev_a.claim != ev_b.claim:
                            pairs.append((ev_a, ev_b))
        return pairs

    @staticmethod
    def _deduplicate(conflicts: list[DecisionConflict]) -> list[DecisionConflict]:
        """Remove conflicts with identical title and claim_a/claim_b."""
        seen: set[tuple[str, str, str]] = set()
        deduped: list[DecisionConflict] = []
        for c in conflicts:
            key = (c.title, c.claim_a[:80], c.claim_b[:80])
            if key not in seen:
                seen.add(key)
                deduped.append(c)
        return deduped

    # ------------------------------------------------------------------
    # Integration helpers
    # ------------------------------------------------------------------

    def update_readiness_from_conflicts(
        self,
        readiness: Any,
        conflicts: list[DecisionConflict],
    ) -> Any:
        """Update a DecisionReadiness value based on active conflicts.

        BLOCK_ACCEPTANCE conflicts → BLOCKED
        RECONCILE conflicts → NEEDS_RECONCILIATION
        REQUEST_AUTHOR_CHOICE → NEEDS_AUTHOR_DECISION
        """
        from auteur.decision.models import DecisionReadiness

        has_blocking = any(c.resolution_boundary == ResolutionBoundary.BLOCK_ACCEPTANCE for c in conflicts)
        has_reconcile = any(c.resolution_boundary == ResolutionBoundary.RECONCILE for c in conflicts)
        has_author = any(c.resolution_boundary == ResolutionBoundary.REQUEST_AUTHOR_CHOICE for c in conflicts)

        if has_blocking:
            return DecisionReadiness.BLOCKED
        if has_reconcile:
            return DecisionReadiness.NEEDS_RECONCILIATION
        if has_author:
            return DecisionReadiness.NEEDS_AUTHOR_DECISION
        return readiness
