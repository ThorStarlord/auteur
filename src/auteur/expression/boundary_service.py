"""V1 service for recording structured Realization evidence against prose candidates."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.expression.pilot import ExpressionStore, ProseCandidate
from auteur.provenance import Lifecycle, ReviewState


class ExpressionBoundaryService:
    """Evaluate an unaccepted prose candidate without changing upstream authority."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.store = ExpressionStore(self.project_root)

    @staticmethod
    def _atomic_write(path: Path, metadata: ProseCandidate) -> None:
        rendered = yaml.safe_dump(metadata.model_dump(mode="json"), sort_keys=False)
        fd, temporary = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(rendered)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def evaluate_candidate(
        self,
        candidate_id: str,
        realization_evidence: dict[str, Any],
        *,
        evaluated_by: str = "deterministic-validator",
    ) -> ProseCandidate:
        """Persist bounded evidence/findings on a draft candidate only.

        Structured contradictions become blocking validation findings and mark
        the candidate review-required. This service never edits the source Scene
        Realization; upstream change remains an explicit separate proposal/action.
        """
        metadata = self.store.inspect(candidate_id)
        if metadata.lifecycle is not Lifecycle.DRAFT:
            raise ValueError(
                "structured Realization evidence may only be attached to an unaccepted draft candidate"
            )
        scene_path = self.store._scene_path(metadata)
        prose = self.store.prose_path(candidate_id).read_text(encoding="utf-8")
        findings = self.store.validate_prose(
            scene_path,
            prose,
            realization_evidence=realization_evidence,
        )
        metadata.realization_evidence = dict(realization_evidence)
        metadata.validation_findings = findings
        metadata.metadata_revision += 1
        blocking = any(item.get("severity", "error") == "error" for item in findings)
        if blocking:
            metadata.review_state = ReviewState.REVIEW_REQUIRED
        metadata.review_history.append(
            {
                "state": "realization_boundary_evaluated",
                "by": evaluated_by,
                "blocking": blocking,
                "at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self._atomic_write(self.store._metadata_path(candidate_id), metadata)
        return metadata
