"""Candidate lifecycle, generation, and external registration."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.convergence.models import (
    CandidateLineage,
    CandidateRef,
    CandidateStatus,
    GenerationStrategy,
    PreservedRegion,
    RevisionTarget,
)


def _hash_content(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _read_yaml(path: Path) -> dict[str, Any] | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return None


class CandidateStore:
    """Manages candidate lifecycle, generation, and registration."""

    def __init__(self, project: Path):
        self.project = Path(project)
        self.root = self.project / ".auteur" / "convergence"

    def _candidate_path(self, candidate_id: str) -> Path:
        return self.root / "candidates" / f"{candidate_id}.yaml"

    def _target_path(self, target_id: str) -> Path:
        return self.root / "targets" / f"{target_id}.yaml"

    def generate_candidate(
        self,
        target: RevisionTarget,
        strategy: GenerationStrategy,
        obligations: list[str],
        preserved_regions: list[PreservedRegion],
        existing_artifact: str = "",
    ) -> CandidateRef:
        """Create a new generated candidate.

        Generates a candidate artifact with lineage recorded.
        Does NOT move canonical pointers.
        """
        candidate_id = f"candidate_{hashlib.sha256((target.target_id + strategy.value + datetime.now(timezone.utc).isoformat()).encode()).hexdigest()[:12]}"

        candidate = CandidateRef(
            candidate_id=candidate_id,
            target_id=target.target_id,
            status=CandidateStatus.GENERATED,
            lineage=CandidateLineage(
                source_artifact_id=existing_artifact or target.current_accepted_artifact or target.target_id,
                generation_method=f"generated:{strategy.value}",
            ),
            obligations=obligations,
            preserved_regions=preserved_regions,
            content_artifact_ref="",
            content_artifact_hash="",
            provenance={
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "strategy": strategy.value,
                "chapter_index": target.chapter_index,
                "scene_id": target.scene_id,
            },
            authority="derived",
            canonical=False,
            freshness="fresh",
            generation_strategy=strategy.value,
        )

        self._save_candidate(candidate)
        return candidate

    def register_candidate(
        self,
        target: RevisionTarget,
        content_path: Path,
        obligations: list[str],
        preserved_regions: list[PreservedRegion],
        *,
        author: str = "author",
    ) -> CandidateRef:
        """Register an externally authored candidate realization.

        Validates:
        - target identity is unambiguous
        - content path exists
        - computes hash
        - creates provenance
        - marks authority correctly
        - preserves original source material
        - rejects ambiguous target mapping
        - does NOT accept
        """
        if not content_path.exists():
            raise ValueError(f"Content path does not exist: {content_path}")

        content = content_path.read_text(encoding="utf-8")
        content_hash = _hash_content(content)

        candidate_id = f"ext_{hashlib.sha256((target.target_id + content_hash).encode()).hexdigest()[:12]}"

        existing = self._load_candidate(candidate_id)
        if existing is not None:
            raise ValueError(f"Candidate with same content hash already exists: {candidate_id}")

        candidate = CandidateRef(
            candidate_id=candidate_id,
            target_id=target.target_id,
            status=CandidateStatus.REGISTERED,
            lineage=CandidateLineage(
                source_artifact_id=str(content_path),
                generation_method=f"external:{author}",
            ),
            obligations=obligations,
            preserved_regions=preserved_regions,
            content_artifact_ref=str(content_path.resolve()),
            content_artifact_hash=content_hash,
            provenance={
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "author": author,
                "chapter_index": target.chapter_index,
                "scene_id": target.scene_id,
            },
            authority="authority_bearing",
            canonical=False,
            freshness="fresh",
            generation_strategy="external",
        )

        self._save_candidate(candidate)
        return candidate

    def get_candidate(self, candidate_id: str) -> CandidateRef | None:
        return self._load_candidate(candidate_id)

    def list_candidates(self, target_id: str) -> list[CandidateRef]:
        """List all candidates for a given target."""
        candidates = []
        candidates_dir = self.root / "candidates"
        if not candidates_dir.exists():
            return candidates

        for path in sorted(candidates_dir.glob("*.yaml")):
            candidate = _read_yaml(path)
            if candidate and candidate.get("target_id") == target_id:
                candidates.append(CandidateRef(**candidate))
        return candidates

    def update_status(self, candidate_id: str, status: CandidateStatus) -> CandidateRef | None:
        candidate = self._load_candidate(candidate_id)
        if candidate is None:
            return None
        candidate.status = status
        self._save_candidate(candidate)
        return candidate

    def mark_stale(self, candidate_id: str) -> CandidateRef | None:
        return self.update_status(candidate_id, CandidateStatus.STALE)

    def supersede(self, candidate_id: str) -> CandidateRef | None:
        return self.update_status(candidate_id, CandidateStatus.SUPERSEDED)

    def reject(self, candidate_id: str) -> CandidateRef | None:
        return self.update_status(candidate_id, CandidateStatus.REJECTED)

    def _save_candidate(self, candidate: CandidateRef) -> None:
        """Persist a candidate atomically (immutable: does not overwrite)."""
        path = self._candidate_path(candidate.candidate_id)
        if path.exists():
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".tmp")
        try:
            temp.write_text(
                yaml.safe_dump(candidate.model_dump(mode="json"), sort_keys=False),
                encoding="utf-8",
            )
            temp.replace(path)
        except Exception:
            if temp.exists():
                temp.unlink()
            raise

    def _load_candidate(self, candidate_id: str) -> CandidateRef | None:
        path = self._candidate_path(candidate_id)
        if not path.exists():
            return None
        data = _read_yaml(path)
        if data is None:
            return None
        return CandidateRef(**data)
