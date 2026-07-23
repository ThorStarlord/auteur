"""Read-only reasoning adapter — loads critic and synthesis artifacts for candidates.

This adapter replaces the indirect ``evaluation_references`` string list on
``CandidateRef`` with direct reads from the reasoning subsystem's persisted
reports, reviews, and source hashes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from auteur.decision.models import (
    DecisionEvidence,
    EvidenceClassification,
    EvidenceFreshness,
    EvidenceSource,
    EvidenceType,
)
from auteur.reasoning.draft_review import (
    load_latest_run,
    load_reasoning_run,
    review_source_freshness,
)
from auteur.workflow.models import AuthorityLevel


def _reasoning_root(project_root: Path, chapter_index: int) -> Path:
    return project_root / "chapters" / f"{chapter_index:02d}" / "reasoning"


def _reports_dir(root: Path) -> Path:
    return root / "outcomes"


class ReasoningAdapter:
    """Query interface to the reasoning subsystem for workspace decisions.

    All methods are read-only; no reasoning artifacts are created or modified.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()

    # ------------------------------------------------------------------
    # Candidate report queries
    # ------------------------------------------------------------------

    def get_candidate_reports(self, candidate_id: str, chapter_index: int) -> list[dict[str, Any]]:
        """Load synthesis reports associated with a candidate.

        Searches reasoning reviews that reference this candidate_id.
        Returns empty list if no reports found.
        """
        reports: list[dict[str, Any]] = []
        root = _reasoning_root(self.project_root, chapter_index)
        reviews_dir = root / "reviews"
        if not reviews_dir.exists():
            return reports

        for review_path in sorted(reviews_dir.glob("reasoning_review_*.yaml")):
            try:
                import yaml
                review = yaml.safe_load(review_path.read_text(encoding="utf-8")) or {}
                if review.get("candidate_id") == candidate_id or candidate_id in str(review.get("run_id", "")):
                    reports.append(review)
            except (yaml.YAMLError, OSError):
                continue

        # Fallback: load latest run and check for candidate references
        if not reports:
            latest = load_latest_run(self.project_root, chapter_index)
            if latest:
                run_id = latest.get("run_id")
                if run_id:
                    run = load_reasoning_run(self.project_root, chapter_index, run_id)
                    if run and (candidate_id in str(run.get("run_id", "")) or candidate_id in str(run.get("critic_ids", []))):
                        # Load the review file linked in latest
                        review_ref = latest.get("review_ref")
                        if review_ref:
                            review_path = reviews_dir / f"{review_ref}.yaml"
                            if review_path.exists():
                                import yaml
                                try:
                                    review = yaml.safe_load(review_path.read_text(encoding="utf-8")) or {}
                                    reports.append(review)
                                except (yaml.YAMLError, OSError):
                                    pass
        return reports

    def run_report_exists(self, run_id: str, chapter_index: int) -> bool:
        """Check if a specific reasoning run exists."""
        run = load_reasoning_run(self.project_root, chapter_index, run_id)
        return run is not None

    def list_reasoning_runs(self, chapter_index: int) -> list[str]:
        """List all reasoning run IDs for a chapter."""
        root = _reasoning_root(self.project_root, chapter_index)
        runs_dir = root / "runs"
        if not runs_dir.exists():
            return []
        return sorted([
            p.stem.replace("reasoning_run_", "")
            for p in runs_dir.glob("reasoning_run_*.yaml")
        ])

    # ------------------------------------------------------------------
    # Evidence conversion
    # ------------------------------------------------------------------

    def reasoning_to_evidence(
        self,
        review: dict[str, Any],
        candidate_id: str | None = None,
    ) -> list[DecisionEvidence]:
        """Convert a reasoning review into DecisionEvidence entries.

        Preserves nuanced findings — each critic finding becomes a separate
        evidence entry with its original classification, not collapsed to a
        single "winner score".
        """
        evidence: list[DecisionEvidence] = []
        critic_summaries = review.get("critic_summaries", [])

        for cs in critic_summaries:
            critic_id = cs.get("critic_id", "unknown")
            status = cs.get("status", "unknown")
            version = cs.get("version", 0)

            claim = f"Critic {critic_id} (v{version}): {status}"
            if cs.get("usage", {}).get("total", {}).get("input_tokens"):
                claim += f" — {cs['usage']['total']['input_tokens']}t in"

            evidence_type = self._map_critic_status_to_evidence_type(status)
            classification = self._map_critic_status_to_classification(status)

            evidence.append(
                DecisionEvidence.create(
                    source_subsystem=EvidenceSource.REASONING,
                    source_artifact_id=f"{critic_id}@v{version}",
                    claim=claim,
                    evidence_type=evidence_type,
                    classification=classification,
                    freshness=EvidenceFreshness.CURRENT,
                    supporting_reference=review.get("run_id"),
                    candidate_id=candidate_id,
                    authority=AuthorityLevel.READ_ONLY,
                )
            )

        # Add blocking findings as evidence
        for bf in review.get("blocking_findings", []):
            evidence.append(
                DecisionEvidence.create(
                    source_subsystem=EvidenceSource.REASONING,
                    source_artifact_id=bf.get("critic", bf.get("critic_id", "unknown")),
                    claim=bf.get("evidence", bf.get("message", "")),
                    evidence_type=EvidenceType.REASONING_FINDING,
                    classification=EvidenceClassification.FACT,
                    freshness=EvidenceFreshness.CURRENT,
                    supporting_reference=review.get("run_id"),
                    candidate_id=candidate_id,
                )
            )

        # Add warnings as contextual observations
        for w in review.get("warnings", []):
            evidence.append(
                DecisionEvidence.create(
                    source_subsystem=EvidenceSource.REASONING,
                    source_artifact_id="synthesis",
                    claim=w.get("evidence", w.get("message", "")),
                    evidence_type=EvidenceType.REASONING_FINDING,
                    classification=EvidenceClassification.CONTEXTUAL_OBSERVATION,
                    freshness=EvidenceFreshness.CURRENT,
                    supporting_reference=review.get("run_id"),
                    candidate_id=candidate_id,
                )
            )

        # Add synthesis text as derived inference
        synthesis = review.get("synthesis", "")
        if synthesis:
            evidence.append(
                DecisionEvidence.create(
                    source_subsystem=EvidenceSource.REASONING,
                    source_artifact_id="synthesis",
                    claim=synthesis[:500],  # truncate to reasonable length
                    evidence_type=EvidenceType.REASONING_FINDING,
                    classification=EvidenceClassification.DERIVED_INFERENCE,
                    freshness=EvidenceFreshness.CURRENT,
                    supporting_reference=review.get("run_id"),
                    candidate_id=candidate_id,
                )
            )

        return evidence

    @staticmethod
    def _map_critic_status_to_evidence_type(status: str) -> EvidenceType:
        if status == "success":
            return EvidenceType.REASONING_FINDING
        elif status in ("failed", "stale"):
            return EvidenceType.ACCEPTANCE_REQUIREMENT
        return EvidenceType.REASONING_FINDING

    @staticmethod
    def _map_critic_status_to_classification(status: str) -> EvidenceClassification:
        if status == "success":
            return EvidenceClassification.DERIVED_INFERENCE
        elif status == "failed":
            return EvidenceClassification.FACT  # failure is a fact
        return EvidenceClassification.CONTEXTUAL_OBSERVATION

    # ------------------------------------------------------------------
    # Freshness / staleness
    # ------------------------------------------------------------------

    def detect_staleness(
        self,
        chapter_index: int,
        source_hashes: dict[str, str] | None = None,
    ) -> EvidenceFreshness:
        """Detect whether reasoning results for a chapter are stale.

        Compares current source hashes against the latest run's recorded
        source snapshot. Returns ``STALE`` on mismatch, ``CURRENT`` if fresh,
        or ``UNKNOWN`` if no run exists.
        """
        latest = load_latest_run(self.project_root, chapter_index)
        if latest is None:
            return EvidenceFreshness.UNKNOWN

        run_id = latest.get("run_id")
        if not run_id:
            return EvidenceFreshness.UNKNOWN

        if source_hashes is None:
            source_hashes = {}

        freshness = review_source_freshness(
            self.project_root,
            chapter_index,
            run_id,
            current_draft_hash=source_hashes.get("draft_hash", ""),
            current_outline_hash=source_hashes.get("outline_hash", ""),
        )

        if not freshness.get("fresh", True):
            return EvidenceFreshness.STALE
        return EvidenceFreshness.CURRENT

    def get_missing_evidence(self, chapter_index: int, candidate_id: str) -> list[str]:
        """Identify what reasoning evidence is missing for a candidate.

        Returns list of missing report/review IDs or descriptive strings.
        """
        missing: list[str] = []
        latest = load_latest_run(self.project_root, chapter_index)
        if latest is None:
            missing.append(f"No reasoning run for chapter {chapter_index}")
            return missing

        # Check if there's a review for this candidate
        reviews = self.get_candidate_reports(candidate_id, chapter_index)
        if not reviews:
            missing.append(f"No review found linking candidate {candidate_id} to reasoning output")
        else:
            # Check if the review has actual content
            for review in reviews:
                if not review.get("critic_summaries") and not review.get("synthesis"):
                    missing.append(f"Review {review.get('review_id', 'unknown')} has no critic findings")

        return missing

    # ------------------------------------------------------------------
    # Report content access
    # ------------------------------------------------------------------

    def get_report_content(self, report_id: str, chapter_index: int) -> dict[str, Any] | None:
        """Load raw critic report JSON by report_id.

        Reports are stored by the ReasoningRuntime in the chapter's
        reasoning/outcomes/<run_id>/ directory.
        """
        root = _reasoning_root(self.project_root, chapter_index)
        runs_dir = root / "runs"
        if not runs_dir.exists():
            return None

        # Search across all run outcome directories
        for out_dir in (root / "outcomes").iterdir():
            if out_dir.is_dir():
                report_path = out_dir / f"{report_id}.json"
                if report_path.exists():
                    try:
                        return json.loads(report_path.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, OSError):
                        continue
        return None
