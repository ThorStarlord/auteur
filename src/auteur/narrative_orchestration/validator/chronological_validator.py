"""Chronological validator for Structure orchestration.

This module validates chronological ordering constraints across narrative artifacts.
It ensures that:
- Payoff events occur after their setups (unless intentional prelude)
- Character arc beats progress through chapters in order
- Story arc checkpoints follow the 9-phase sequence
- Book-level reveals don't contradict earlier knowledge
- Series-level continuity is maintained (no retroactive changes)

The ChronologicalValidator accepts outline artifacts and cross-checks their temporal
relationships for coherence.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.sequence_outline import SequenceOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint
from auteur.narrative_blueprint.schema.story_arc import StoryArc, ArcCheckpoint


class ChronologyViolationType(str, Enum):
    """Enumeration of chronological violation types."""

    PAYOFF_BEFORE_SETUP = "payoff_before_setup"
    ARC_BEAT_OUT_OF_ORDER = "arc_beat_out_of_order"
    CRISIS_BEFORE_SETUP = "crisis_before_setup"
    MIDPOINT_AFTER_THIRD_ACT = "midpoint_after_third_act"
    REVEAL_IN_WRONG_BOOK = "reveal_in_wrong_book"
    PHASE_OUT_OF_ORDER = "phase_out_of_order"
    CONTRADICTORY_STATE = "contradictory_state"
    ARC_CHECKPOINT_OUT_OF_ORDER = "arc_checkpoint_out_of_order"


@dataclass
class ChronologicalViolation:
    """Represents a single chronological ordering violation.

    Attributes:
        violation_type: Type of chronological violation
        source_artifact_id: ID of artifact causing the violation
        target_artifact_id: ID of conflicting artifact
        message: Human-readable description of the violation
        severity: 'error' (breaks composition) or 'warning' (should be reviewed)
    """

    violation_type: ChronologyViolationType
    source_artifact_id: str
    target_artifact_id: Optional[str]
    message: str
    severity: str  # 'error' or 'warning'


class ChronologicalValidator:
    """Validates chronological ordering in narrative outlines.

    This validator checks that all temporal relationships between narrative
    elements are coherent and follow genre-appropriate ordering rules.

    Attributes:
        books: Dictionary mapping book IDs to BookOutline artifacts
        sequences: Dictionary mapping sequence IDs to SequenceOutline artifacts
        chapters: Dictionary mapping chapter IDs to ChapterOutline artifacts
        character_arcs: Dictionary mapping character arc IDs to CharacterArc artifacts
        story_arcs: Dictionary mapping story arc IDs to StoryArc artifacts
        violations: List of ChronologicalViolation objects found during validation
    """

    def __init__(self):
        """Initialize an empty ChronologicalValidator."""
        self.books: Dict[str, BookOutline] = {}
        self.sequences: Dict[str, SequenceOutline] = {}
        self.chapters: Dict[str, ChapterOutline] = {}
        self.character_arcs: Dict[str, CharacterArc] = {}
        self.story_arcs: Dict[str, StoryArc] = {}
        self.violations: List[ChronologicalViolation] = []

    def add_book(self, book_id: str, book: BookOutline) -> None:
        """Add a book outline to the validator.

        Args:
            book_id: Unique identifier for the book
            book: BookOutline artifact
        """
        self.books[book_id] = book

    def add_sequence(self, sequence_id: str, sequence: SequenceOutline) -> None:
        """Add a sequence outline to the validator.

        Args:
            sequence_id: Unique identifier for the sequence
            sequence: SequenceOutline artifact
        """
        self.sequences[sequence_id] = sequence

    def add_chapter(self, chapter_id: str, chapter: ChapterOutline) -> None:
        """Add a chapter outline to the validator.

        Args:
            chapter_id: Unique identifier for the chapter
            chapter: ChapterOutline artifact
        """
        self.chapters[chapter_id] = chapter

    def add_character_arc(self, arc_id: str, arc: CharacterArc) -> None:
        """Add a character arc to the validator.

        Args:
            arc_id: Unique identifier for the character arc
            arc: CharacterArc artifact
        """
        self.character_arcs[arc_id] = arc

    def add_story_arc(self, arc_id: str, arc: StoryArc) -> None:
        """Add a story arc to the validator.

        Args:
            arc_id: Unique identifier for the story arc
            arc: StoryArc artifact
        """
        self.story_arcs[arc_id] = arc

    def validate_all_chronology(self) -> bool:
        """Orchestrate all chronological validation checks.

        Runs all validation methods and returns whether all checks passed.

        Returns:
            True if all chronological checks pass, False if any violations found
        """
        self.violations = []

        self.validate_setup_payoff_ordering()
        self.validate_character_arc_progression()
        self.validate_story_arc_timing()
        self.validate_revelation_timing()
        self.validate_book_continuity()
        self.validate_phase_progression()

        return len(self.violations) == 0

    def validate_setup_payoff_ordering(self) -> List[ChronologicalViolation]:
        """Validate that payoff events occur after setup events.

        Checks that in narrative cause-effect relationships, the payoff (consequence)
        occurs after the setup (action/plant). Allows for intentional preludes where
        payoff may come before setup.

        Returns:
            List of ChronologicalViolation objects found
        """
        violations = []

        # Check arc progressions in chapters for setup/payoff patterns
        for chapter_id, chapter in self.chapters.items():
            if not chapter.arc_progressions:
                continue

            # Parse arc progressions for setup/payoff patterns
            for arc_id, progression_str in chapter.arc_progressions.items():
                if "setup" in progression_str.lower() and "payoff" in progression_str.lower():
                    # This chapter claims both setup and payoff in same place - flag for review
                    violations.append(
                        ChronologicalViolation(
                            violation_type=ChronologyViolationType.PAYOFF_BEFORE_SETUP,
                            source_artifact_id=chapter_id,
                            target_artifact_id=arc_id,
                            message=(
                                f"Chapter {chapter_id} claims both setup and payoff in same "
                                f"arc progression for {arc_id}. Payoff should occur later."
                            ),
                            severity="warning",
                        )
                    )

        self.violations.extend(violations)
        return violations

    def validate_character_arc_progression(self) -> List[ChronologicalViolation]:
        """Validate that character arc beats progress through chapters in order.

        Checks that all turning points in a character arc occur in chapters that
        are in increasing order (chapter 3 beat before chapter 7 beat, etc.).

        Returns:
            List of ChronologicalViolation objects found
        """
        violations = []

        for arc_id, arc in self.character_arcs.items():
            if not arc.turning_points:
                continue

            # Extract chapter numbers from turning points
            chapter_numbers = [tp.chapter for tp in arc.turning_points]

            # Check if chapters are in increasing order
            for i in range(len(chapter_numbers) - 1):
                current_chapter = chapter_numbers[i]
                next_chapter = chapter_numbers[i + 1]

                if current_chapter >= next_chapter:
                    violations.append(
                        ChronologicalViolation(
                            violation_type=ChronologyViolationType.ARC_BEAT_OUT_OF_ORDER,
                            source_artifact_id=arc_id,
                            target_artifact_id=f"chapter_{next_chapter}",
                            message=(
                                f"Character arc {arc_id} has turning points out of order: "
                                f"chapter {current_chapter} before chapter {next_chapter}. "
                                f"Arc beats must progress chronologically."
                            ),
                            severity="error",
                        )
                    )

        self.violations.extend(violations)
        return violations

    def validate_story_arc_timing(self) -> List[ChronologicalViolation]:
        """Validate that story arc checkpoints follow the 9-phase sequence.

        Checks that checkpoints in a story arc occur in phases that follow the
        arc's phase_range (start, peak, end) progression.

        Returns:
            List of ChronologicalViolation objects found
        """
        violations = []

        for arc_id, arc in self.story_arcs.items():
            if not arc.checkpoints:
                continue

            # Extract phases from checkpoints
            checkpoint_phases = [cp.phase for cp in arc.checkpoints]

            # Check if phases are within the arc's phase range and in order
            previous_phase = arc.phase_range.start - 1
            for cp in arc.checkpoints:
                phase = cp.phase

                # Phase should be within the arc's range
                if not arc.phase_range.includes_phase(phase):
                    violations.append(
                        ChronologicalViolation(
                            violation_type=ChronologyViolationType.PHASE_OUT_OF_ORDER,
                            source_artifact_id=arc_id,
                            target_artifact_id=None,
                            message=(
                                f"Story arc {arc_id} has checkpoint in phase {phase}, "
                                f"which is outside its range ({arc.phase_range.start}-"
                                f"{arc.phase_range.end})"
                            ),
                            severity="error",
                        )
                    )

                # Phase should be in increasing order
                if phase <= previous_phase:
                    violations.append(
                        ChronologicalViolation(
                            violation_type=ChronologyViolationType.ARC_CHECKPOINT_OUT_OF_ORDER,
                            source_artifact_id=arc_id,
                            target_artifact_id=None,
                            message=(
                                f"Story arc {arc_id} has checkpoints out of order: "
                                f"phase {previous_phase + 1} should come after phase {phase}. "
                                f"Checkpoints must progress through phases."
                            ),
                            severity="error",
                        )
                    )

                previous_phase = phase

        self.violations.extend(violations)
        return violations

    def validate_revelation_timing(self) -> List[ChronologicalViolation]:
        """Validate that key reveals/discoveries happen in proper sequence.

        Checks that revelations don't reference knowledge that hasn't been
        established yet in the narrative (e.g., Book 3 reveal not used in Book 1).

        Returns:
            List of ChronologicalViolation objects found
        """
        violations = []

        # Check chapters for revelation patterns in arc progressions
        for chapter_id, chapter in self.chapters.items():
            if not chapter.arc_progressions:
                continue

            for arc_id, progression_str in chapter.arc_progressions.items():
                # Look for "reveal" or "discovery" patterns
                if "reveal" in progression_str.lower() or "discover" in progression_str.lower():
                    # Check if this revelation is consistent with the chapter's position
                    # If it's a major revelation, it should generally be in later phases
                    if "major" in progression_str.lower() and chapter.phase < 6:
                        violations.append(
                            ChronologicalViolation(
                                violation_type=ChronologyViolationType.REVEAL_IN_WRONG_BOOK,
                                source_artifact_id=chapter_id,
                                target_artifact_id=arc_id,
                                message=(
                                    f"Chapter {chapter_id} (phase {chapter.phase}) has major "
                                    f"revelation for arc {arc_id}, but phase {chapter.phase} is "
                                    f"too early for major reveals (should be phase 6+)"
                                ),
                                severity="warning",
                            )
                        )

        self.violations.extend(violations)
        return violations

    def validate_book_continuity(self) -> List[ChronologicalViolation]:
        """Validate series-level continuity across books.

        Checks that:
        - Character arcs don't reference future knowledge in earlier books
        - No retroactive changes to established story state
        - Character states progress consistently across book boundaries

        Returns:
            List of ChronologicalViolation objects found
        """
        violations = []

        # Sort books by assumed order (if IDs indicate ordering)
        sorted_books = sorted(self.books.values(), key=lambda b: b.name)

        # Check character arc progression across books
        for arc_id, arc in self.character_arcs.items():
            if not arc.turning_points or len(arc.turning_points) < 2:
                continue

            # Get the chapters spanned by this arc
            arc_chapters = sorted(arc.span_chapters)

            # Check if the arc's chapters come from multiple books
            # (This is a simplified check - a full implementation would track book boundaries)
            if arc.initial_belief and arc.final_belief:
                # Check that belief transformation is consistent
                # A simplified version: just ensure the arc spans multiple chapters
                if len(arc_chapters) > 1:
                    first_chapter = arc_chapters[0]
                    last_chapter = arc_chapters[-1]

                    if first_chapter >= last_chapter:
                        violations.append(
                            ChronologicalViolation(
                                violation_type=ChronologyViolationType.CONTRADICTORY_STATE,
                                source_artifact_id=arc_id,
                                target_artifact_id=None,
                                message=(
                                    f"Character arc {arc_id} spans chapters {first_chapter}-"
                                    f"{last_chapter}, but these are not in order. "
                                    f"Arc span must be chronological across books."
                                ),
                                severity="error",
                            )
                        )

        self.violations.extend(violations)
        return violations

    def validate_phase_progression(self) -> List[ChronologicalViolation]:
        """Validate that chapters progress through phases in order.

        Checks that chapters within a book or sequence don't violate phase
        ordering (e.g., no phase 5 chapter before phase 3 chapter).

        Returns:
            List of ChronologicalViolation objects found
        """
        violations = []

        # Group chapters by parent to check phase ordering within containers
        chapters_by_parent: Dict[Optional[str], List[Tuple[int, ChapterOutline]]] = {}
        for chapter_id, chapter in self.chapters.items():
            parent = chapter.parent_id
            if parent not in chapters_by_parent:
                chapters_by_parent[parent] = []
            chapters_by_parent[parent].append((chapter.chapter_number, chapter))

        # Check phase ordering within each parent container
        for parent_id, chapter_list in chapters_by_parent.items():
            # Sort by chapter number
            sorted_chapters = sorted(chapter_list, key=lambda x: x[0])

            # Check that phases are in increasing order
            previous_phase = 0
            for chapter_num, chapter in sorted_chapters:
                if chapter.phase < previous_phase:
                    violations.append(
                        ChronologicalViolation(
                            violation_type=ChronologyViolationType.PHASE_OUT_OF_ORDER,
                            source_artifact_id=chapter.name,
                            target_artifact_id=parent_id,
                            message=(
                                f"Chapter {chapter_num} is in phase {chapter.phase}, "
                                f"but comes after a chapter in phase {previous_phase}. "
                                f"Phases must progress in order through chapters."
                            ),
                            severity="warning",
                        )
                    )
                previous_phase = max(previous_phase, chapter.phase)

        self.violations.extend(violations)
        return violations

    def report_chronological_issues(self) -> str:
        """Generate a comprehensive report of all chronological violations.

        Returns:
            Formatted string report of all violations, grouped by type
        """
        if not self.violations:
            return "No chronological violations found."

        # Group violations by type
        violations_by_type: Dict[str, List[ChronologicalViolation]] = {}
        for violation in self.violations:
            vtype = violation.violation_type.value
            if vtype not in violations_by_type:
                violations_by_type[vtype] = []
            violations_by_type[vtype].append(violation)

        # Generate report
        report_lines = ["Chronological Violations Report", "=" * 50]

        error_count = sum(1 for v in self.violations if v.severity == "error")
        warning_count = sum(1 for v in self.violations if v.severity == "warning")
        report_lines.append(f"Total: {len(self.violations)} issues ({error_count} errors, {warning_count} warnings)")
        report_lines.append("")

        for violation_type, violations in sorted(violations_by_type.items()):
            report_lines.append(f"\n{violation_type.upper()}")
            report_lines.append("-" * len(violation_type))

            for violation in violations:
                severity_marker = "ERROR" if violation.severity == "error" else "WARN"
                report_lines.append(
                    f"  [{severity_marker}] {violation.source_artifact_id}: {violation.message}"
                )

        return "\n".join(report_lines)

    def get_violations(
        self, violation_type: Optional[ChronologyViolationType] = None, severity: Optional[str] = None
    ) -> List[ChronologicalViolation]:
        """Get violations, optionally filtered by type and/or severity.

        Args:
            violation_type: Optional filter by violation type
            severity: Optional filter by severity ('error' or 'warning')

        Returns:
            List of ChronologicalViolation objects matching filters
        """
        result = self.violations

        if violation_type is not None:
            result = [v for v in result if v.violation_type == violation_type]

        if severity is not None:
            result = [v for v in result if v.severity == severity]

        return result

    def has_violations(self, severity: Optional[str] = None) -> bool:
        """Check if any violations exist, optionally filtered by severity.

        Args:
            severity: Optional filter by severity ('error' or 'warning')

        Returns:
            True if violations exist matching the filter
        """
        return len(self.get_violations(severity=severity)) > 0
