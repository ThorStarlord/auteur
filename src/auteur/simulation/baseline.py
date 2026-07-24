"""Immutable capture of current project state for counterfactual scenarios."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from auteur.simulation.models import (
    CounterfactualBaseline,
    compute_baseline_id,
)

logger = logging.getLogger(__name__)


class BaselineCapture:
    """Capture immutable baselines from current project state.

    Baseline creation is read-only and does not mutate any subsystem.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def capture(self, plan_id: str = "") -> CounterfactualBaseline:
        """Capture current project state as an immutable baseline.

        Gathers references to decisions, accepted pointers, canonical pointers,
        provenance hashes, and review sessions without mutating any state.
        """
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).isoformat()
        baseline_id = compute_baseline_id(str(self.project_root), ts)

        accepted = self._capture_accepted_pointers()
        canonical = self._capture_canonical_pointers()
        provenance = self._capture_provenance_hashes()
        decision_ids = self._capture_decision_ids()
        review_ids = self._capture_review_session_ids()

        return CounterfactualBaseline(
            baseline_id=baseline_id,
            project=str(self.project_root),
            plan_id=plan_id,
            decision_ids=decision_ids,
            accepted_pointers=accepted,
            canonical_pointers=canonical,
            provenance_hashes=provenance,
            review_session_ids=review_ids,
            created_at=ts,
        )

    def _capture_decision_ids(self) -> list[str]:
        """Capture IDs of open decisions."""
        try:
            from auteur.decision.service import DecisionWorkspaceService
            svc = DecisionWorkspaceService(self.project_root)
            decisions = svc.list_decisions()
            return [d.decision_id if hasattr(d, "decision_id") else str(d) for d in decisions]
        except Exception as e:
            logger.debug(f"Could not capture decisions: {e}")
            return []

    def _capture_accepted_pointers(self) -> dict[str, str]:
        """Capture accepted artifact pointers."""
        pointers = {}
        # Check common accepted pointer locations
        for pattern, key in [
            ("story_identity.yaml", "story_identity"),
            ("blueprint.yaml", "blueprint"),
        ]:
            p = self.project_root / pattern
            if p.exists():
                pointers[key] = str(p)
        return pointers

    def _capture_canonical_pointers(self) -> dict[str, str]:
        """Capture canonical artifact pointers."""
        pointers = {}
        canon_dir = self.project_root / ".auteur" / "canonical"
        if canon_dir.exists():
            for f in canon_dir.iterdir():
                if f.is_file():
                    pointers[f.stem] = str(f)
        return pointers

    def _capture_provenance_hashes(self) -> dict[str, str]:
        """Capture provenance content hashes for staleness detection."""
        hashes = {}
        try:
            from auteur.provenance.store import ArtifactStore
            store = ArtifactStore(self.project_root)
            for meta in store.list_metadata():
                if hasattr(meta, "artifact_id") and hasattr(meta, "current_hash"):
                    hashes[meta.artifact_id] = meta.current_hash
        except Exception as e:
            logger.debug(f"Could not capture provenance: {e}")
        return hashes

    def _capture_review_session_ids(self) -> list[str]:
        """Capture active review session IDs."""
        try:
            from auteur.review.service import ReviewService
            svc = ReviewService(self.project_root)
            sessions = svc.list_sessions()
            ids = []
            for s in sessions:
                sid = getattr(s, "session_id", None)
                if sid:
                    ids.append(sid)
                elif isinstance(s, dict):
                    ids.append(s.get("session_id", ""))
            return ids
        except Exception as e:
            logger.debug(f"Could not capture review sessions: {e}")
            return []
