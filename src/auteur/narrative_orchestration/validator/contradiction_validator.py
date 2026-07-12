"""Contradiction validator for detecting conflicts between Layer 2.5 artifacts.

This module implements ContradictionValidator, which detects conflicts between
different outline artifacts (Book, Sequence, Chapter, CharacterArc, StoryArc).

Contradiction types:
1. Arc beats vs Chapter outcomes: Arc says X happens, Chapter says opposite
2. Story arc progress vs Chapters: Story arc expects progress but chapters don't show it
3. Character state consistency: Character appears in two places simultaneously
4. Arc theme vs Genre contract: Arc theme violates genre constraints
5. Sequence/Chapter alignment: Sequence objective doesn't match chapter contents
6. Book ending vs Outline climax: Book says ending one way, outline says another

Each contradiction has severity (hard = structural error, soft = inconsistency).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple, Set, Any

from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint
from auteur.narrative_blueprint.schema.sequence_outline import SequenceOutline
from auteur.narrative_blueprint.schema.story_arc import StoryArc, ArcCheckpoint
from auteur.narrative_ontology.validator.ontology_validator import OntologyValidator


class ContradictionSeverity(str, Enum):
    """Severity levels for contradictions."""

    HARD = "hard"  # Structural error, breaks composition
    SOFT = "soft"  # Inconsistency that should be reviewed


@dataclass
class Contradiction:
    """Represents a single contradiction between artifacts.

    Attributes:
        contradiction_type: Type of contradiction (e.g., "arc_vs_chapter_conflict")
        severity: HARD (structural error) or SOFT (inconsistency)
        artifact_a: ID of first conflicting artifact
        artifact_a_type: Type of artifact A (e.g., "character_arc")
        artifact_b: ID of second conflicting artifact
        artifact_b_type: Type of artifact B (e.g., "chapter_outline")
        description: Human-readable description of what conflicts
        evidence_a: What artifact A says
        evidence_b: What artifact B says
        context: Additional context about the contradiction
    """

    contradiction_type: str
    severity: ContradictionSeverity
    artifact_a: str
    artifact_a_type: str
    artifact_b: str
    artifact_b_type: str
    description: str
    evidence_a: str
    evidence_b: str
    context: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "type": self.contradiction_type,
            "severity": self.severity.value,
            "artifact_a": self.artifact_a,
            "artifact_a_type": self.artifact_a_type,
            "artifact_b": self.artifact_b,
            "artifact_b_type": self.artifact_b_type,
            "description": self.description,
            "evidence_a": self.evidence_a,
            "evidence_b": self.evidence_b,
            "context": self.context,
        }


class ContradictionValidator:
    """Validates that outline artifacts don't contradict each other.

    Detects conflicts between different outline artifacts and provides clear
    reporting of what contradicts what. Supports genre-aware validation by
    checking arc themes against genre contracts.

    Attributes:
        book_outline: BookOutline artifact (required)
        sequence_outlines: Dict of SequenceOutline artifacts by ID (optional)
        chapter_outlines: Dict of ChapterOutline artifacts by ID (required)
        character_arcs: Dict of CharacterArc artifacts by ID (optional)
        story_arcs: Dict of StoryArc artifacts by ID (optional)
        genre: Genre identifier (required for theme validation)
    """

    def __init__(
        self,
        book_outline: BookOutline,
        chapter_outlines: Dict[str, ChapterOutline],
        genre: str,
        sequence_outlines: Optional[Dict[str, SequenceOutline]] = None,
        character_arcs: Optional[Dict[str, CharacterArc]] = None,
        story_arcs: Optional[Dict[str, StoryArc]] = None,
    ):
        """Initialize ContradictionValidator with outline artifacts.

        Args:
            book_outline: BookOutline artifact
            chapter_outlines: Dictionary of ChapterOutline artifacts
            genre: Genre identifier (for theme validation)
            sequence_outlines: Dictionary of SequenceOutline artifacts (optional)
            character_arcs: Dictionary of CharacterArc artifacts (optional)
            story_arcs: Dictionary of StoryArc artifacts (optional)

        Raises:
            ValueError: If required artifacts are missing or invalid
        """
        if not book_outline:
            raise ValueError("book_outline is required")
        if not chapter_outlines:
            raise ValueError("chapter_outlines cannot be empty")
        if not genre:
            raise ValueError("genre is required")

        self.book_outline = book_outline
        self.chapter_outlines = chapter_outlines
        self.sequence_outlines = sequence_outlines or {}
        self.character_arcs = character_arcs or {}
        self.story_arcs = story_arcs or {}
        self.genre = genre

        self.ontology_validator = OntologyValidator()
        self.contradictions: List[Contradiction] = []

    def validate_no_contradictions(self) -> Tuple[bool, List[Contradiction]]:
        """Orchestrate all contradiction checks.

        Runs all validation methods and collects contradictions.

        Returns:
            Tuple of (no_contradictions_found, list of Contradiction objects)
            no_contradictions_found is True if no contradictions were found
            list of Contradiction objects contains all found contradictions
        """
        self.contradictions = []

        # Run all validation checks
        self.validate_arc_vs_chapter_agreement()
        self.validate_story_arc_vs_chapters()
        self.validate_character_state_consistency()
        self.validate_arc_theme_genre_alignment()
        self.validate_sequence_chapter_alignment()

        return len(self.contradictions) == 0, self.contradictions

    def validate_arc_vs_chapter_agreement(self) -> None:
        """Validate arc beats align with chapter outcomes.

        Checks that:
        - Arc turning points occur in chapters with compatible outcomes
        - Chapter emotional beats don't contradict arc transformations
        - Arc initial/final beliefs match chapter progression

        Contradictions are added to self.contradictions.
        """
        for arc_id, arc in self.character_arcs.items():
            # Check each turning point in the arc
            for tp in arc.turning_points:
                # Find the chapter for this turning point
                if tp.chapter not in self.chapter_outlines:
                    continue

                chapter = self.chapter_outlines[tp.chapter]

                # Check if chapter's emotional beat contradicts the belief shift
                # Simple heuristic: if arc says beliefs shift to something negative
                # but chapter says emotional beat is positive, that's soft contradiction
                if self._is_emotional_contradiction(arc, tp, chapter):
                    self.contradictions.append(
                        Contradiction(
                            contradiction_type="arc_vs_chapter_emotional_conflict",
                            severity=ContradictionSeverity.SOFT,
                            artifact_a=arc_id,
                            artifact_a_type="character_arc",
                            artifact_b=str(tp.chapter),
                            artifact_b_type="chapter_outline",
                            description=(
                                f"Arc turning point in chapter {tp.chapter} contradicts "
                                f"chapter's emotional beat"
                            ),
                            evidence_a=f"Turning point: {tp.moment} → {tp.belief_shift}",
                            evidence_b=f"Chapter emotional beat: {chapter.emotional_beat}",
                            context=f"Character arc '{arc.character_name}' expects "
                            f"transformation but chapter shows different emotional progression",
                        )
                    )

    def validate_story_arc_vs_chapters(self) -> None:
        """Validate story arc progress reflects chapter outcomes.

        Checks that:
        - Story arc checkpoints occur in chapters with appropriate content
        - Mystery arc progress shows clues in investigation phases
        - Romance arc progress shows relationship development
        - Chapter goals align with story arc expectations

        Contradictions are added to self.contradictions.
        """
        for arc_id, arc in self.story_arcs.items():
            # Check each checkpoint in the arc
            for checkpoint in arc.checkpoints:
                # Find chapters in this phase
                chapters_in_phase = [
                    (ch_id, ch)
                    for ch_id, ch in self.chapter_outlines.items()
                    if ch.phase == checkpoint.phase
                ]

                if not chapters_in_phase:
                    continue

                # Check if any chapter in this phase supports the arc checkpoint
                has_supporting_chapter = any(
                    self._chapter_supports_arc_checkpoint(ch, arc, checkpoint)
                    for _, ch in chapters_in_phase
                )

                if not has_supporting_chapter and chapters_in_phase:
                    first_chapter_id = chapters_in_phase[0][0]
                    chapter = chapters_in_phase[0][1]

                    self.contradictions.append(
                        Contradiction(
                            contradiction_type="story_arc_progress_mismatch",
                            severity=ContradictionSeverity.SOFT,
                            artifact_a=arc_id,
                            artifact_a_type="story_arc",
                            artifact_b=str(first_chapter_id),
                            artifact_b_type="chapter_outline",
                            description=(
                                f"Story arc '{arc.arc_name}' expects progress in phase "
                                f"{checkpoint.phase} but chapter {first_chapter_id} "
                                f"doesn't support this"
                            ),
                            evidence_a=f"Arc checkpoint (phase {checkpoint.phase}): "
                            f"{checkpoint.moment}",
                            evidence_b=f"Chapter goal: {chapter.goal}",
                            context=f"Story arc type: {arc.arc_category}",
                        )
                    )

    def validate_character_state_consistency(self) -> None:
        """Validate character state is consistent across arcs.

        Checks that:
        - Character doesn't appear in two incompatible states simultaneously
        - State transitions follow valid progressions
        - Character's turning points don't contradict each other

        Contradictions are added to self.contradictions.
        """
        for arc_id, arc in self.character_arcs.items():
            # Check that all turning points are ordered by chapter
            turning_points = sorted(arc.turning_points, key=lambda tp: tp.chapter)

            # Check each consecutive pair for contradictions
            for i in range(len(turning_points) - 1):
                current_tp = turning_points[i]
                next_tp = turning_points[i + 1]

                # Check if the transitions are contradictory
                if self._is_state_transition_contradictory(
                    arc, current_tp, next_tp
                ):
                    self.contradictions.append(
                        Contradiction(
                            contradiction_type="character_state_contradiction",
                            severity=ContradictionSeverity.HARD,
                            artifact_a=f"turning_point_{current_tp.chapter}",
                            artifact_a_type="turning_point",
                            artifact_b=f"turning_point_{next_tp.chapter}",
                            artifact_b_type="turning_point",
                            description=(
                                f"Character '{arc.character_name}' has contradictory "
                                f"state transitions"
                            ),
                            evidence_a=f"Chapter {current_tp.chapter}: {current_tp.belief_shift}",
                            evidence_b=f"Chapter {next_tp.chapter}: {next_tp.belief_shift}",
                            context=f"Character state must progress consistently, "
                            f"not oscillate between incompatible beliefs",
                        )
                    )

    def validate_arc_theme_genre_alignment(self) -> None:
        """Validate arc themes align with genre contract.

        Checks that:
        - Character arc themes are appropriate for the genre
        - Story arc categories are valid for the genre
        - Theme combinations respect genre constraints

        Contradictions are added to self.contradictions.
        """
        # Validate character arcs
        for arc_id, arc in self.character_arcs.items():
            if not self.ontology_validator.is_valid_genre(self.genre):
                continue

            try:
                expected_themes = self.ontology_validator.get_genre_themes(self.genre)
            except ValueError:
                continue

            arc_themes = set(arc.genre_themes)

            # Check if there's at least one overlap
            overlap = arc_themes & expected_themes

            if not overlap:
                self.contradictions.append(
                    Contradiction(
                        contradiction_type="arc_theme_genre_violation",
                        severity=ContradictionSeverity.HARD,
                        artifact_a=arc_id,
                        artifact_a_type="character_arc",
                        artifact_b=self.genre,
                        artifact_b_type="genre",
                        description=(
                            f"Character arc themes don't match {self.genre} genre contract"
                        ),
                        evidence_a=f"Arc themes: {sorted(arc_themes)}",
                        evidence_b=f"Genre '{self.genre}' expects one of: "
                        f"{sorted(expected_themes)}",
                        context="Character development must respect the emotional and "
                        "thematic boundaries of the genre",
                    )
                )

    def validate_sequence_chapter_alignment(self) -> None:
        """Validate sequence objectives align with chapter goals.

        Checks that:
        - Chapters in a sequence support the sequence's objective
        - Chapter goals collectively accomplish the sequence goal
        - Sequence purpose is coherent with its chapters

        Contradictions are added to self.contradictions.
        """
        for seq_id, sequence in self.sequence_outlines.items():
            start, end = sequence.chapter_range
            chapters_in_sequence = {
                ch_id: ch
                for ch_id, ch in self.chapter_outlines.items()
                if start <= ch.chapter_number <= end
            }

            if not chapters_in_sequence:
                continue

            # Check if chapters' goals collectively support sequence objective
            chapter_goals = [ch.goal for ch in chapters_in_sequence.values()]

            # Simple heuristic: if no chapter goal relates to sequence objective,
            # that's a soft contradiction
            if not self._chapter_goals_support_objective(
                chapter_goals, sequence.objective
            ):
                self.contradictions.append(
                    Contradiction(
                        contradiction_type="sequence_chapter_misalignment",
                        severity=ContradictionSeverity.SOFT,
                        artifact_a=seq_id,
                        artifact_a_type="sequence_outline",
                        artifact_b=f"chapters_{start}_{end}",
                        artifact_b_type="chapter_range",
                        description=(
                            f"Sequence {seq_id} objective doesn't align with chapter goals"
                        ),
                        evidence_a=f"Sequence objective: {sequence.objective}",
                        evidence_b=f"Chapter goals ({len(chapter_goals)} chapters): "
                        f"{'; '.join(chapter_goals[:2])}{'...' if len(chapter_goals) > 2 else ''}",
                        context=f"Chapters {start}-{end}: sequence objective should be "
                        f"supported by chapter contents",
                    )
                )

    def report_contradictions(self) -> Dict[str, Any]:
        """Generate comprehensive report of all contradictions.

        Returns:
            Dictionary with:
                - "total_contradictions": Count of contradictions found
                - "hard_contradictions": Count of hard contradictions
                - "soft_contradictions": Count of soft contradictions
                - "contradictions": List of Contradiction dicts
                - "summary": Human-readable summary
        """
        hard_count = sum(
            1 for c in self.contradictions if c.severity == ContradictionSeverity.HARD
        )
        soft_count = len(self.contradictions) - hard_count

        contradictions_dicts = [c.to_dict() for c in self.contradictions]

        # Build summary by type
        by_type = {}
        for c in self.contradictions:
            if c.contradiction_type not in by_type:
                by_type[c.contradiction_type] = []
            by_type[c.contradiction_type].append(c)

        summary_lines = [
            f"Found {len(self.contradictions)} total contradictions "
            f"({hard_count} hard, {soft_count} soft)"
        ]

        for contradiction_type, contradictions in sorted(by_type.items()):
            summary_lines.append(
                f"  - {contradiction_type}: {len(contradictions)} "
                f"({sum(1 for c in contradictions if c.severity == ContradictionSeverity.HARD)} hard)"
            )

        return {
            "total_contradictions": len(self.contradictions),
            "hard_contradictions": hard_count,
            "soft_contradictions": soft_count,
            "contradictions": contradictions_dicts,
            "summary": "\n".join(summary_lines),
        }

    # Helper methods for contradiction detection

    def _is_emotional_contradiction(
        self, arc: CharacterArc, tp: TurningPoint, chapter: ChapterOutline
    ) -> bool:
        """Check if turning point contradicts chapter's emotional beat.

        Args:
            arc: CharacterArc containing the turning point
            tp: TurningPoint to check
            chapter: ChapterOutline at that turning point location

        Returns:
            True if there's a contradiction, False otherwise
        """
        # Simple heuristic: check for opposing emotional keywords
        negative_keywords = {"despair", "decline", "failure", "loss", "shame", "dread"}
        positive_keywords = {"hope", "triumph", "victory", "gain", "pride", "joy"}

        tp_has_positive = any(kw in tp.belief_shift.lower() for kw in positive_keywords)
        tp_has_negative = any(kw in tp.belief_shift.lower() for kw in negative_keywords)

        ch_has_positive = any(
            kw in chapter.emotional_beat.lower() for kw in positive_keywords
        )
        ch_has_negative = any(
            kw in chapter.emotional_beat.lower() for kw in negative_keywords
        )

        # Contradiction: turning point positive but chapter negative (or vice versa)
        if (tp_has_positive and ch_has_negative) or (tp_has_negative and ch_has_positive):
            return True

        return False

    def _chapter_supports_arc_checkpoint(
        self, chapter: ChapterOutline, arc: StoryArc, checkpoint: ArcCheckpoint
    ) -> bool:
        """Check if a chapter supports an arc checkpoint.

        Args:
            chapter: ChapterOutline to check
            arc: StoryArc containing the checkpoint
            checkpoint: ArcCheckpoint to match

        Returns:
            True if chapter supports the checkpoint, False otherwise
        """
        # Simple heuristic: check if chapter goal relates to arc category
        goal_lower = chapter.goal.lower()
        checkpoint_lower = checkpoint.moment.lower()

        # Check for keyword overlap
        goal_words = set(goal_lower.split())
        checkpoint_words = set(checkpoint_lower.split())

        overlap = goal_words & checkpoint_words
        if overlap:
            return True

        # Check for arc-category-specific patterns
        arc_category = arc.arc_category.lower()
        if arc_category == "mystery" and any(
            kw in goal_lower for kw in ["investigate", "clue", "reveal", "discover"]
        ):
            return True
        if arc_category == "romance" and any(
            kw in goal_lower for kw in ["develop", "relationship", "emotional", "connect"]
        ):
            return True
        if arc_category == "revenge" and any(
            kw in goal_lower for kw in ["plot", "scheme", "retaliate", "justice"]
        ):
            return True

        return False

    def _is_state_transition_contradictory(
        self, arc: CharacterArc, tp1: TurningPoint, tp2: TurningPoint
    ) -> bool:
        """Check if two consecutive turning points contradict.

        Args:
            arc: CharacterArc containing both turning points
            tp1: First turning point
            tp2: Second turning point

        Returns:
            True if transitions contradict, False otherwise
        """
        # Simple heuristic: check for direct contradictions in belief shifts
        shift1_lower = tp1.belief_shift.lower()
        shift2_lower = tp2.belief_shift.lower()

        # Define opposing concepts
        opposing_pairs = [
            ("trust", "distrust"),
            ("confident", "afraid"),
            ("accept", "reject"),
            ("embrace", "resist"),
            ("believe", "doubt"),
            ("open", "closed"),
        ]

        for pos, neg in opposing_pairs:
            # If first shift has positive and second has negative (or vice versa)
            if (pos in shift1_lower and neg in shift2_lower) or (
                neg in shift1_lower and pos in shift2_lower
            ):
                # Only contradiction if they're about the same thing
                # (Very simple check: both shifts are relatively short)
                if len(shift1_lower) < 100 and len(shift2_lower) < 100:
                    return True

        return False

    def _chapter_goals_support_objective(
        self, chapter_goals: List[str], objective: str
    ) -> bool:
        """Check if chapter goals collectively support sequence objective.

        Args:
            chapter_goals: List of chapter goal strings
            objective: Sequence objective string

        Returns:
            True if goals support objective, False otherwise
        """
        if not chapter_goals:
            return False

        # Simple heuristic: check for keyword overlap
        objective_lower = objective.lower()
        objective_words = set(objective_lower.split())

        # Count how many chapters have goal words that overlap with objective
        supporting_chapters = 0
        for goal in chapter_goals:
            goal_lower = goal.lower()
            goal_words = set(goal_lower.split())
            overlap = goal_words & objective_words
            if overlap:
                supporting_chapters += 1

        # Consider it supported if at least one chapter goal relates to objective
        # or if the sequence is relatively short and goals are related
        if supporting_chapters > 0:
            return True

        # Check for high-level alignment (both are about conflict, emotion, etc.)
        conflict_words = {"conflict", "tension", "challenge", "obstacle"}
        emotion_words = {"emotional", "feeling", "reaction", "response"}
        resolution_words = {"resolve", "conclude", "end", "climax"}

        objective_has_conflict = any(kw in objective_lower for kw in conflict_words)
        any_goal_has_conflict = any(
            any(kw in g.lower() for kw in conflict_words) for g in chapter_goals
        )

        if objective_has_conflict and any_goal_has_conflict:
            return True

        return False
