"""Milestone derivation and evaluation for project planning.

Milestones derive from real artifact and authority state using existing
Auteur subsystems. No milestone is marked complete based on artifact
existence alone — accepted/current state is required.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from auteur.planning.models import (
    MilestoneState,
    PlanMilestone,
    PlanningHorizon,
    _stable_id,
)


class MilestoneEngine:
    """Derive and evaluate project milestones from real subsystem state."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def derive_milestones(
        self,
        status_data: dict[str, Any] | None = None,
        chapters: list[int] | None = None,
    ) -> list[PlanMilestone]:
        """Derive all project milestones from current state.

        Args:
            status_data: Pre-fetched status dict from gather_status(), if available.
            chapters: Chapter indices to scope milestones to (None = all).

        Returns:
            List of PlanMilestone with current state evaluated.
        """
        milestones: list[PlanMilestone] = []
        s = status_data or {}

        # Story Identity accepted
        milestones.append(self._eval_story_identity(s))

        # Structure valid
        milestones.append(self._eval_structure(s))

        # Chapter milestones
        chapter_indices = chapters or self._detect_chapters()
        for ci in chapter_indices:
            milestones.append(self._eval_chapter_realization(ci, s))
            milestones.append(self._eval_chapter_expression(ci, s))
            milestones.append(self._eval_chapter_reasoning(ci, s))
            milestones.append(self._eval_chapter_reconciliation(ci, s))

        # Book milestones
        book_indices = self._detect_books()
        for bi in book_indices:
            milestones.append(self._eval_book_assembly(bi, s))
            milestones.append(self._eval_book_acceptance(bi, s))

        # Publication
        milestones.append(self._eval_publication(s))

        return milestones

    def evaluate_milestone(self, milestone: PlanMilestone) -> PlanMilestone:
        """Re-evaluate a single milestone's state."""
        # This is a convenience for refreshing one milestone.
        # In practice, derive_milestones() is the normal path.
        return milestone

    # ------------------------------------------------------------------
    # Individual milestone evaluators
    # ------------------------------------------------------------------

    def _eval_story_identity(self, s: dict[str, Any]) -> PlanMilestone:
        mid = _stable_id("milestone", "story-identity-accepted")
        identity_path = self.project_root / "story_identity.yaml"

        required = ["story_identity.yaml exists", "identity is accepted"]
        completed: list[str] = []
        blocked: list[str] = []
        state: MilestoneState

        if not identity_path.exists():
            state = MilestoneState.NOT_STARTED
            blocked.append("story_identity.yaml not found")
        else:
            completed.append("story_identity.yaml exists")
            # Check acceptance state from status
            identity_status = s.get("identity", {})
            is_accepted = identity_status.get("is_accepted", False)
            if is_accepted:
                completed.append("identity is accepted")
                state = MilestoneState.COMPLETED
            else:
                state = MilestoneState.IN_PROGRESS
                blocked.append("identity not yet accepted")

        return PlanMilestone(
            milestone_id=mid,
            title="Story Identity accepted",
            scope=PlanningHorizon.PROJECT,
            state=state,
            required_conditions=required,
            completed_conditions=completed,
            blocked_conditions=blocked,
            authority_requirement="authority_required",
            evidence=f"identity_path={identity_path}",
            status_reason=_reason(state, blocked, "Identity milestone"),
        )

    def _eval_structure(self, s: dict[str, Any]) -> PlanMilestone:
        mid = _stable_id("milestone", "structure-valid")
        required = ["blueprint validates without errors"]
        completed: list[str] = []
        blocked: list[str] = []
        state: MilestoneState

        blueprint_status = s.get("blueprint", {})
        bp_valid = blueprint_status.get("is_valid", False)

        if bp_valid:
            completed.append("blueprint validates without errors")
            state = MilestoneState.COMPLETED
        else:
            errors = blueprint_status.get("errors", [])
            if errors:
                blocked.append(f"Blueprint errors: {len(errors)}")
                state = MilestoneState.BLOCKED
            else:
                state = MilestoneState.NOT_STARTED
                blocked.append("Blueprint not validated")

        return PlanMilestone(
            milestone_id=mid,
            title="Structure valid",
            scope=PlanningHorizon.PROJECT,
            state=state,
            required_conditions=required,
            completed_conditions=completed,
            blocked_conditions=blocked,
            evidence=f"valid={bp_valid}",
            status_reason=_reason(state, blocked, "Structure milestone"),
        )

    def _eval_chapter_realization(self, chapter: int, s: dict[str, Any]) -> PlanMilestone:
        mid = _stable_id("milestone", f"ch{chapter}-realization-accepted")
        title = f"Chapter {chapter} realization accepted"
        required = [f"Chapter {chapter} has accepted realization"]
        completed: list[str] = []
        blocked: list[str] = []
        state: MilestoneState

        chapter_state = self._get_chapter_state(chapter, s)
        has_realization = chapter_state.get("has_accepted_realization", False)
        real_path = chapter_state.get("realization_path", "")

        if has_realization:
            completed.append(f"Accepted realization: {real_path}")
            state = MilestoneState.COMPLETED
        elif real_path:
            state = MilestoneState.IN_PROGRESS
            blocked.append("Realization exists but not accepted")
        else:
            state = MilestoneState.NOT_STARTED
            blocked.append("No realization found")

        return PlanMilestone(
            milestone_id=mid,
            title=title,
            scope=PlanningHorizon.CHAPTER,
            chapter_index=chapter,
            state=state,
            required_conditions=required,
            completed_conditions=completed,
            blocked_conditions=blocked,
            authority_requirement="authority_required",
            evidence=f"realization_path={real_path}",
            status_reason=_reason(state, blocked, f"Chapter {chapter} realization"),
        )

    def _eval_chapter_expression(self, chapter: int, s: dict[str, Any]) -> PlanMilestone:
        mid = _stable_id("milestone", f"ch{chapter}-expression-accepted")
        title = f"Chapter {chapter} expression accepted"
        required = [f"Chapter {chapter} has accepted expression"]
        completed: list[str] = []
        blocked: list[str] = []
        state: MilestoneState

        chapter_state = self._get_chapter_state(chapter, s)
        has_expression = chapter_state.get("has_accepted_expression", False)
        exp_path = chapter_state.get("expression_path", "")

        if has_expression:
            completed.append(f"Accepted expression: {exp_path}")
            state = MilestoneState.COMPLETED
        elif exp_path:
            state = MilestoneState.IN_PROGRESS
            blocked.append("Expression exists but not accepted")
        else:
            state = MilestoneState.NOT_STARTED
            blocked.append("No expression found")

        return PlanMilestone(
            milestone_id=mid,
            title=title,
            scope=PlanningHorizon.CHAPTER,
            chapter_index=chapter,
            state=state,
            required_conditions=required,
            completed_conditions=completed,
            blocked_conditions=blocked,
            authority_requirement="authority_required",
            evidence=f"expression_path={exp_path}",
            status_reason=_reason(state, blocked, f"Chapter {chapter} expression"),
        )

    def _eval_chapter_reasoning(self, chapter: int, s: dict[str, Any]) -> PlanMilestone:
        mid = _stable_id("milestone", f"ch{chapter}-reasoning-current")
        title = f"Chapter {chapter} reasoning current"
        required = [f"Chapter {chapter} reasoning is non-stale"]
        completed: list[str] = []
        blocked: list[str] = []
        state: MilestoneState

        chapter_state = self._get_chapter_state(chapter, s)
        reasoning_current = chapter_state.get("reasoning_current", False)
        reasoning_available = chapter_state.get("reasoning_available", False)

        if reasoning_current:
            completed.append("Reasoning is current")
            state = MilestoneState.COMPLETED
        elif reasoning_available:
            state = MilestoneState.STALE
            blocked.append("Reasoning exists but is stale")
        else:
            state = MilestoneState.NOT_STARTED
            blocked.append("No reasoning found")

        return PlanMilestone(
            milestone_id=mid,
            title=title,
            scope=PlanningHorizon.CHAPTER,
            chapter_index=chapter,
            state=state,
            required_conditions=required,
            completed_conditions=completed,
            blocked_conditions=blocked,
            evidence=f"current={reasoning_current}, available={reasoning_available}",
            status_reason=_reason(state, blocked, f"Chapter {chapter} reasoning"),
        )

    def _eval_chapter_reconciliation(self, chapter: int, s: dict[str, Any]) -> PlanMilestone:
        mid = _stable_id("milestone", f"ch{chapter}-reconciliation-complete")
        title = f"Chapter {chapter} reconciliation complete"
        required = [f"Chapter {chapter} reconciliation closed"]
        completed: list[str] = []
        blocked: list[str] = []
        state: MilestoneState

        chapter_state = self._get_chapter_state(chapter, s)
        reconciled = chapter_state.get("reconciliation_complete", False)

        if reconciled:
            completed.append("Reconciliation complete")
            state = MilestoneState.COMPLETED
        else:
            state = MilestoneState.NOT_STARTED
            blocked.append("Reconciliation not complete")

        return PlanMilestone(
            milestone_id=mid,
            title=title,
            scope=PlanningHorizon.CHAPTER,
            chapter_index=chapter,
            state=state,
            required_conditions=required,
            completed_conditions=completed,
            blocked_conditions=blocked,
            evidence=f"reconciled={reconciled}",
            status_reason=_reason(state, blocked, f"Chapter {chapter} reconciliation"),
        )

    def _eval_book_assembly(self, book_index: int, s: dict[str, Any]) -> PlanMilestone:
        mid = _stable_id("milestone", f"book{book_index}-assembled")
        title = f"Book {book_index} assembled"
        required = ["All chapters composed into book"]
        completed: list[str] = []
        blocked: list[str] = []
        state: MilestoneState

        book_state = s.get("book", {})
        chapters_assembled = book_state.get("chapters_assembled", 0)
        total_chapters = book_state.get("total_chapters", 0)

        if chapters_assembled >= total_chapters > 0:
            completed.append(f"All {total_chapters} chapters assembled")
            state = MilestoneState.COMPLETED
        elif chapters_assembled > 0:
            completed.append(f"{chapters_assembled}/{total_chapters} chapters assembled")
            state = MilestoneState.IN_PROGRESS
            blocked.append(f"Remaining: {total_chapters - chapters_assembled} chapters")
        else:
            state = MilestoneState.NOT_STARTED
            blocked.append("No chapters assembled")

        return PlanMilestone(
            milestone_id=mid,
            title=title,
            scope=PlanningHorizon.BOOK,
            book_index=book_index,
            state=state,
            required_conditions=required,
            completed_conditions=completed,
            blocked_conditions=blocked,
            authority_requirement="recommendation",
            evidence=f"assembled={chapters_assembled}/{total_chapters}",
            status_reason=_reason(state, blocked, f"Book {book_index} assembly"),
        )

    def _eval_book_acceptance(self, book_index: int, s: dict[str, Any]) -> PlanMilestone:
        mid = _stable_id("milestone", f"book{book_index}-accepted")
        title = f"Book {book_index} accepted"
        required = ["Book expression accepted"]
        completed: list[str] = []
        blocked: list[str] = []
        state: MilestoneState

        book_state = s.get("book", {})
        is_accepted = book_state.get("is_accepted", False)

        if is_accepted:
            completed.append("Book expression accepted")
            state = MilestoneState.COMPLETED
        else:
            assembled = book_state.get("chapters_assembled", 0) > 0
            if assembled:
                state = MilestoneState.READY
                blocked.append("Book assembled but not accepted")
            else:
                state = MilestoneState.NOT_STARTED
                blocked.append("Book not yet assembled")

        return PlanMilestone(
            milestone_id=mid,
            title=title,
            scope=PlanningHorizon.BOOK,
            book_index=book_index,
            state=state,
            required_conditions=required,
            completed_conditions=completed,
            blocked_conditions=blocked,
            authority_requirement="authority_required",
            evidence=f"accepted={is_accepted}",
            status_reason=_reason(state, blocked, f"Book {book_index} acceptance"),
        )

    def _eval_publication(self, s: dict[str, Any]) -> PlanMilestone:
        mid = _stable_id("milestone", "publication-current")
        title = "Publication current"
        required = ["Publication is up to date"]
        completed: list[str] = []
        blocked: list[str] = []
        state: MilestoneState

        pub_state = s.get("publishing", {})
        is_current = pub_state.get("is_current", False)

        if is_current:
            completed.append("Publication is current")
            state = MilestoneState.COMPLETED
        else:
            state = MilestoneState.NOT_STARTED
            blocked.append("Publication not current")

        return PlanMilestone(
            milestone_id=mid,
            title=title,
            scope=PlanningHorizon.PROJECT,
            state=state,
            required_conditions=required,
            completed_conditions=completed,
            blocked_conditions=blocked,
            evidence=f"current={is_current}",
            status_reason=_reason(state, blocked, "Publication milestone"),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_chapter_state(self, chapter: int, s: dict[str, Any]) -> dict[str, Any]:
        """Extract chapter state from status data."""
        chapters = s.get("chapters") or []
        for ch in chapters:
            if isinstance(ch, dict) and ch.get("index") == chapter:
                return ch
        return {}

    def _detect_chapters(self) -> list[int]:
        """Detect chapter indices from project structure."""
        chapters: list[int] = []
        chapters_dir = self.project_root / "chapters"
        if chapters_dir.exists():
            for d in sorted(chapters_dir.iterdir()):
                if d.is_dir() and d.name.isdigit():
                    chapters.append(int(d.name))
        # If no chapters dir, check actual project structure
        if not chapters:
            for d in sorted(self.project_root.iterdir()):
                if d.is_dir() and d.name.isdigit():
                    chapters.append(int(d.name))
        return sorted(chapters) if chapters else [1]

    def _detect_books(self) -> list[int]:
        """Detect book indices."""
        return [1]  # Default to single book


def _reason(state: MilestoneState, blocked: list[str], fallback: str) -> str:
    if state == MilestoneState.COMPLETED:
        return "All conditions satisfied"
    if blocked:
        return f"Blocked: {'; '.join(blocked[:3])}"
    return fallback
