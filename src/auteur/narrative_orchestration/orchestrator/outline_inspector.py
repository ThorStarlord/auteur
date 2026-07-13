"""Outline Inspector for Structure orchestration.

This module provides the OutlineInspector class for displaying and analyzing
complete outline structures in readable format. It shows hierarchy, arc coverage,
missing elements, and validation status.

The OutlineInspector accepts complete outline artifacts (Series, Books, Sequences,
Chapters, Character Arcs, Story Arcs) and provides methods to inspect them in
various ways:
- show_structure(): Display full hierarchy tree
- show_character_arcs(): Display character arc beats with chapter references
- show_story_arcs(): Display story arc progression
- show_coverage(): Show which chapters/sequences have arc beats
- show_missing_elements(): Identify unimplemented optional sections
- show_validation_status(): Show which validators pass/fail
- show_completeness(): Report completion percentage
- generate_summary(): Comprehensive status report
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

from auteur.narrative_blueprint.schema.outline_types import OutlineArtifact
from auteur.narrative_blueprint.schema.series_outline import SeriesOutline
from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.sequence_outline import SequenceOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint
from auteur.narrative_blueprint.schema.story_arc import StoryArc, ArcCheckpoint


@dataclass
class ValidationStatus:
    """Represents the status of a single validator.

    Attributes:
        validator_name: Name of the validator
        passed: Whether the validator passed
        errors: List of error messages if validator failed
        warnings: List of warning messages
    """
    validator_name: str
    passed: bool
    errors: List[str]
    warnings: List[str]


class OutlineInspector:
    """Inspector for analyzing complete narrative outlines.

    The OutlineInspector provides methods to display and analyze outline structures
    in readable format. It works identically across all 3 genres.

    Attributes:
        series_outline: SeriesOutline artifact (optional)
        books: Dictionary mapping book_id to BookOutline
        sequences: Dictionary mapping sequence_id to SequenceOutline
        chapters: Dictionary mapping chapter_id to ChapterOutline
        character_arcs: Dictionary mapping arc_id to CharacterArc
        story_arcs: Dictionary mapping arc_id to StoryArc
        genre: Genre identifier (inferred from first artifact)
        story_id: Story identifier (inferred from first artifact)
    """

    def __init__(self):
        """Initialize an empty OutlineInspector."""
        self.series_outline: Optional[SeriesOutline] = None
        self.books: Dict[str, BookOutline] = {}
        self.sequences: Dict[str, SequenceOutline] = {}
        self.chapters: Dict[str, ChapterOutline] = {}
        self.character_arcs: Dict[str, CharacterArc] = {}
        self.story_arcs: Dict[str, StoryArc] = {}
        self.genre: Optional[str] = None
        self.story_id: Optional[str] = None
        self.validation_status: List[ValidationStatus] = []

    def add_artifact(self, artifact: OutlineArtifact) -> None:
        """Add a narrative artifact to the inspector.

        Args:
            artifact: OutlineArtifact to add (Series, Book, Sequence, Chapter, Arc)

        Raises:
            ValueError: If artifact type is unknown
        """
        # Track genre and story_id from first artifact
        if self.genre is None:
            self.genre = artifact.genre
            self.story_id = artifact.story_id

        artifact_type = artifact.artifact_type()

        if artifact_type == "series_outline":
            self.series_outline = artifact
        elif artifact_type == "book_outline":
            self.books[artifact.story_id] = artifact
        elif artifact_type == "sequence_outline":
            self.sequences[artifact.story_id] = artifact
        elif artifact_type == "chapter_outline":
            self.chapters[artifact.story_id] = artifact
        elif artifact_type == "character_arc":
            self.character_arcs[artifact.story_id] = artifact
        elif artifact_type == "story_arc":
            self.story_arcs[artifact.story_id] = artifact
        else:
            raise ValueError(f"Unknown artifact type: {artifact_type}")

    def add_validation_status(
        self,
        validator_name: str,
        passed: bool,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
    ) -> None:
        """Add validation status information.

        Args:
            validator_name: Name of the validator
            passed: Whether the validator passed
            errors: List of error messages (optional)
            warnings: List of warning messages (optional)
        """
        status = ValidationStatus(
            validator_name=validator_name,
            passed=passed,
            errors=errors or [],
            warnings=warnings or [],
        )
        self.validation_status.append(status)

    def show_structure(self) -> str:
        """Display the complete outline hierarchy as a tree.

        Format:
        Series: <series_name>
        ├── Book: <title>
        │   ├── Sequence: <name>
        │   │   ├── Chapter 1: <title>
        │   │   ├── Chapter 2: <title>
        │   │   └── Chapter 3: <title>
        │   └── Sequence: <name>
        │       └── Chapter 4: <title>
        └── Book: <title>
            └── Chapter 5: <title>

        Returns:
            Formatted string representation of the outline hierarchy
        """
        lines = []

        if not self.books:
            return "(empty outline)"

        # Series level
        if self.series_outline:
            lines.append(f"Series: {self.series_outline.series_name}")
        else:
            lines.append("Series: (no series outline)")

        # Books level
        book_ids = list(self.books.keys())
        for book_idx, book_id in enumerate(book_ids):
            book = self.books[book_id]
            is_last_book = book_idx == len(book_ids) - 1
            book_prefix = "└── " if is_last_book else "├── "
            lines.append(f"{book_prefix}Book: {book.title}")

            # Get sequences and chapters for this book
            book_sequences = [
                seq for seq in self.sequences.values()
                if seq.parent_id == book_id
            ]
            book_chapters = [
                ch for ch in self.chapters.values()
                if ch.parent_id == book_id
            ]

            # Sort sequences by sequence_number
            book_sequences.sort(key=lambda s: s.sequence_number)

            if book_sequences:
                # Display sequences with their chapters
                for seq_idx, sequence in enumerate(book_sequences):
                    is_last_seq = seq_idx == len(book_sequences) - 1 and not book_chapters
                    seq_prefix = "│   " if not is_last_book else "    "
                    seq_branch = "└── " if is_last_seq else "├── "
                    lines.append(f"{seq_prefix}{seq_branch}Sequence: {sequence.name}")

                    # Get chapters in this sequence
                    seq_chapters = [
                        ch for ch in self.chapters.values()
                        if ch.parent_id == sequence.story_id
                    ]
                    seq_chapters.sort(key=lambda c: c.chapter_number)

                    for ch_idx, chapter in enumerate(seq_chapters):
                        is_last_ch = ch_idx == len(seq_chapters) - 1
                        ch_prefix = "│   │   " if not is_last_book else "        "
                        ch_branch = "└── " if is_last_ch else "├── "
                        lines.append(
                            f"{ch_prefix}{ch_branch}Chapter {chapter.chapter_number}: {chapter.title}"
                        )
            elif book_chapters:
                # No sequences, just chapters under book
                book_chapters.sort(key=lambda c: c.chapter_number)
                for ch_idx, chapter in enumerate(book_chapters):
                    is_last_ch = ch_idx == len(book_chapters) - 1
                    ch_prefix = "│   " if not is_last_book else "    "
                    ch_branch = "└── " if is_last_ch else "├── "
                    lines.append(
                        f"{ch_prefix}{ch_branch}Chapter {chapter.chapter_number}: {chapter.title}"
                    )

        return "\n".join(lines)

    def show_character_arcs(self) -> str:
        """Display character arcs and their turning points with chapter references.

        Format:
        Character Arc: Clara's Distrust
        ├── Initial Belief: "I can trust him"
        ├── Final Belief: "I cannot trust anyone"
        └── Turning Points:
            ├── Chapter 3: First betrayal → Doubt grows
            ├── Chapter 7: Deeper deception → Trust shatters
            └── Chapter 12: Final betrayal → Complete distrust

        Returns:
            Formatted string representation of all character arcs
        """
        if not self.character_arcs:
            return "(no character arcs)"

        lines = []

        for arc_idx, (arc_id, arc) in enumerate(self.character_arcs.items()):
            if arc_idx > 0:
                lines.append("")  # Blank line between arcs

            lines.append(f"Character Arc: {arc.character_name}")
            lines.append(f"├── Initial Belief: \"{arc.initial_belief}\"")
            lines.append(f"├── Final Belief: \"{arc.final_belief}\"")
            lines.append(f"├── Genre Themes: {', '.join(arc.genre_themes)}")

            if arc.turning_points:
                lines.append(f"└── Turning Points:")
                for tp_idx, tp in enumerate(arc.turning_points):
                    is_last = tp_idx == len(arc.turning_points) - 1
                    prefix = "    └── " if is_last else "    ├── "
                    chapter_ref = f"Chapter {tp.chapter}" if tp.chapter in range(1, 100) else "Unknown"
                    lines.append(f"{prefix}{chapter_ref}: {tp.moment}")
                    lines.append(f"        → {tp.belief_shift}")
            else:
                lines.append("└── Turning Points: (none)")

        return "\n".join(lines)

    def show_story_arcs(self) -> str:
        """Display story arcs and their checkpoints with phase coverage.

        Format:
        Story Arc: The Cuckoldry Progression
        ├── Category: romance
        ├── Phase Range: 1-9 (peak at 6)
        └── Checkpoints:
            ├── Phase 2: Temptation appears
            ├── Phase 5: Desire becomes overwhelming
            └── Phase 8: Final surrender

        Returns:
            Formatted string representation of all story arcs
        """
        if not self.story_arcs:
            return "(no story arcs)"

        lines = []

        for arc_idx, (arc_id, arc) in enumerate(self.story_arcs.items()):
            if arc_idx > 0:
                lines.append("")  # Blank line between arcs

            lines.append(f"Story Arc: {arc.arc_name}")
            lines.append(f"├── Category: {arc.arc_category}")

            phase_range = arc.phase_range
            lines.append(
                f"├── Phase Range: {phase_range.start}-{phase_range.end} "
                f"(peak at {phase_range.peak})"
            )

            if arc.span_chapters:
                chapters_str = ", ".join(str(c) for c in sorted(arc.span_chapters))
                lines.append(f"├── Spans Chapters: {chapters_str}")

            if arc.checkpoints:
                lines.append(f"└── Checkpoints:")
                for cp_idx, cp in enumerate(arc.checkpoints):
                    is_last = cp_idx == len(arc.checkpoints) - 1
                    prefix = "    └── " if is_last else "    ├── "
                    lines.append(f"{prefix}Phase {cp.phase}: {cp.moment}")
            else:
                lines.append("└── Checkpoints: (none)")

        return "\n".join(lines)

    def show_coverage(self) -> str:
        """Show which chapters and sequences have arc beats.

        Format:
        Chapter Coverage:
        ├── Chapter 1: Character Arc (Clara's Trust), Story Arc (Cuckoldry)
        ├── Chapter 3: Character Arc (Clara's Trust)
        ├── Chapter 5: Story Arc (Cuckoldry), Story Arc (Jealousy)
        └── Chapter 7: (no arcs)

        Returns:
            Formatted string showing arc coverage by chapter and sequence
        """
        lines = []

        # Collect which arcs reference each chapter
        chapter_arcs: Dict[int, List[str]] = {}

        for char_arc in self.character_arcs.values():
            for tp in char_arc.turning_points:
                if tp.chapter not in chapter_arcs:
                    chapter_arcs[tp.chapter] = []
                chapter_arcs[tp.chapter].append(f"Character Arc ({char_arc.character_name})")

        for story_arc in self.story_arcs.values():
            for cp in story_arc.checkpoints:
                # Map phase to potential chapters (approximate)
                if cp.phase not in chapter_arcs:
                    chapter_arcs[cp.phase] = []
                chapter_arcs[cp.phase].append(f"Story Arc ({story_arc.arc_name})")

        if not chapter_arcs:
            return "Chapter Coverage: (no arcs referencing chapters)"

        lines.append("Chapter Coverage:")

        sorted_chapters = sorted(chapter_arcs.keys())
        for ch_idx, ch_num in enumerate(sorted_chapters):
            is_last = ch_idx == len(sorted_chapters) - 1
            prefix = "└── " if is_last else "├── "
            arcs_str = ", ".join(chapter_arcs[ch_num])
            lines.append(f"{prefix}Chapter {ch_num}: {arcs_str}")

        return "\n".join(lines)

    def show_missing_elements(self) -> str:
        """Identify missing elements and unimplemented optional sections.

        Format:
        Missing Elements:
        ├── Series Outline: MISSING (optional, but recommended for multi-book)
        ├── Character Arcs: IMPLEMENTED (2 of 3 planned)
        ├── Story Arcs: MISSING (optional)
        ├── Sequences: IMPLEMENTED (3 sequences covering all chapters)
        └── Chapter Arcs Progressions: PARTIAL (5 of 9 chapters have arc_progressions)

        Returns:
            Formatted string showing missing elements
        """
        lines = []
        lines.append("Missing Elements:")

        # Check series outline
        if self.series_outline:
            lines.append("├── Series Outline: IMPLEMENTED")
        elif self.books:
            lines.append("├── Series Outline: MISSING (optional, but recommended for multi-book)")
        else:
            lines.append("├── Series Outline: MISSING (required for structure)")

        # Check books
        if self.books:
            lines.append(f"├── Books: IMPLEMENTED ({len(self.books)} book(s))")
        else:
            lines.append("├── Books: MISSING (required)")

        # Check sequences
        if self.sequences:
            lines.append(f"├── Sequences: IMPLEMENTED ({len(self.sequences)} sequence(s))")
        else:
            lines.append("├── Sequences: OPTIONAL (not used in this structure)")

        # Check chapters
        if self.chapters:
            lines.append(f"├── Chapters: IMPLEMENTED ({len(self.chapters)} chapter(s))")
        else:
            lines.append("├── Chapters: MISSING (required)")

        # Check character arcs
        if self.character_arcs:
            lines.append(f"├── Character Arcs: IMPLEMENTED ({len(self.character_arcs)} arc(s))")
        else:
            lines.append("├── Character Arcs: OPTIONAL (recommended)")

        # Check story arcs
        if self.story_arcs:
            lines.append(f"├── Story Arcs: IMPLEMENTED ({len(self.story_arcs)} arc(s))")
        else:
            lines.append("├── Story Arcs: OPTIONAL")

        # Check arc progressions in chapters
        chapters_with_progressions = sum(
            1 for ch in self.chapters.values() if ch.arc_progressions
        )
        total_chapters = len(self.chapters)
        if total_chapters > 0:
            if chapters_with_progressions == total_chapters:
                lines.append(
                    f"└── Chapter Arc Progressions: COMPLETE "
                    f"({chapters_with_progressions}/{total_chapters})"
                )
            elif chapters_with_progressions > 0:
                lines.append(
                    f"└── Chapter Arc Progressions: PARTIAL "
                    f"({chapters_with_progressions}/{total_chapters})"
                )
            else:
                lines.append(
                    f"└── Chapter Arc Progressions: OPTIONAL "
                    f"(0/{total_chapters})"
                )

        return "\n".join(lines)

    def show_validation_status(self) -> str:
        """Show which validators pass or fail on this outline.

        Format:
        Validation Status:
        ├── Reference Validator: PASS
        ├── Chronological Validator: PASS
        ├── Contradiction Validator: FAIL
        │   └── Error: Chapter 5 says trust increases, but Character Arc says distrust deepens
        └── Composition Validator: FAIL
            └── Error: Missing required arc coverage in book 2

        Returns:
            Formatted string showing validation status
        """
        if not self.validation_status:
            return "Validation Status: (no validation status recorded)"

        lines = []
        lines.append("Validation Status:")

        for status_idx, status in enumerate(self.validation_status):
            is_last = status_idx == len(self.validation_status) - 1
            prefix = "└── " if is_last else "├── "
            status_str = "PASS" if status.passed else "FAIL"
            lines.append(f"{prefix}{status.validator_name}: {status_str}")

            # Show errors for failed validators
            if not status.passed:
                all_messages = status.errors + status.warnings
                if all_messages:
                    msg_prefix = "    " if is_last else "│   "
                    for msg_idx, msg in enumerate(all_messages):
                        is_last_msg = msg_idx == len(all_messages) - 1
                        msg_branch = "└── " if is_last_msg else "├── "
                        lines.append(f"{msg_prefix}{msg_branch}{msg}")

        return "\n".join(lines)

    def show_completeness(self) -> str:
        """Report overall completeness percentage.

        Calculates a simple completeness metric based on:
        - Artifact presence (books, chapters, arcs)
        - Arc turning point/checkpoint coverage
        - Chapter arc progression filling

        Format:
        Completeness: 72%
        ├── Structural Elements: 4/5 (80%)
        │   ├── Series Outline: YES
        │   ├── Books: YES (2)
        │   ├── Sequences: NO
        │   ├── Chapters: YES (12)
        │   └── Arcs: YES (3)
        ├── Arc Development: 18/30 (60%)
        │   └── Turning Points/Checkpoints: 18 of 30 phases covered
        └── Chapter Details: 7/12 (58%)
            └── Chapters with arc progressions: 7 of 12

        Returns:
            Formatted string showing completeness metrics
        """
        lines = []
        lines.append("Completeness Assessment:")

        # Structural elements scoring
        structural_score = 0
        structural_max = 5

        if self.series_outline:
            structural_score += 1
        if self.books:
            structural_score += 1
        if self.sequences:
            structural_score += 1
        if self.chapters:
            structural_score += 1
        if self.character_arcs or self.story_arcs:
            structural_score += 1

        structural_pct = int((structural_score / structural_max) * 100)
        lines.append(f"├── Structural Elements: {structural_score}/{structural_max} ({structural_pct}%)")

        if self.series_outline:
            lines.append("│   ├── Series Outline: YES")
        else:
            lines.append("│   ├── Series Outline: NO")

        if self.books:
            lines.append(f"│   ├── Books: YES ({len(self.books)})")
        else:
            lines.append("│   ├── Books: NO")

        if self.sequences:
            lines.append(f"│   ├── Sequences: YES ({len(self.sequences)})")
        else:
            lines.append("│   ├── Sequences: NO")

        if self.chapters:
            lines.append(f"│   ├── Chapters: YES ({len(self.chapters)})")
        else:
            lines.append("│   └── Chapters: NO")

        arc_count = len(self.character_arcs) + len(self.story_arcs)
        if arc_count > 0:
            lines.append(f"│   └── Arcs: YES ({arc_count})")
        else:
            lines.append("│   └── Arcs: NO")

        # Arc development scoring
        total_turning_points = sum(len(arc.turning_points) for arc in self.character_arcs.values())
        total_checkpoints = sum(len(arc.checkpoints) for arc in self.story_arcs.values())
        arc_content_score = total_turning_points + total_checkpoints
        arc_content_max = 30  # Reasonable target
        arc_content_pct = min(100, int((arc_content_score / arc_content_max) * 100))

        lines.append(f"├── Arc Development: {arc_content_score}/{arc_content_max} ({arc_content_pct}%)")
        lines.append(
            f"│   └── Turning Points/Checkpoints: {arc_content_score} defined"
        )

        # Chapter details scoring
        chapters_with_progressions = sum(
            1 for ch in self.chapters.values() if ch.arc_progressions
        )
        total_chapters = len(self.chapters) or 1
        chapter_details_pct = int((chapters_with_progressions / total_chapters) * 100)

        lines.append(f"└── Chapter Details: {chapters_with_progressions}/{total_chapters} ({chapter_details_pct}%)")
        lines.append(
            f"    └── Chapters with arc progressions: {chapters_with_progressions} of {total_chapters}"
        )

        # Overall completeness
        overall_score = (structural_score + arc_content_score + chapters_with_progressions)
        overall_max = structural_max + arc_content_max + total_chapters
        overall_pct = int((overall_score / overall_max) * 100) if overall_max > 0 else 0

        lines.insert(0, f"Overall Completeness: {overall_pct}%")

        return "\n".join(lines)

    def generate_summary(self) -> str:
        """Generate a comprehensive status report of the entire outline.

        Returns a multi-section report including:
        1. Structure overview
        2. Character arcs
        3. Story arcs
        4. Arc coverage
        5. Missing elements
        6. Validation status
        7. Completeness metrics

        Returns:
            Complete formatted status report
        """
        sections = [
            ("=" * 60),
            (f"OUTLINE STATUS REPORT"),
            (f"Genre: {self.genre or '(unknown)'} | Story ID: {self.story_id or '(unknown)'}"),
            ("=" * 60),
            (""),
            ("STRUCTURE"),
            ("-" * 60),
            (self.show_structure()),
            (""),
            ("CHARACTER ARCS"),
            ("-" * 60),
            (self.show_character_arcs()),
            (""),
            ("STORY ARCS"),
            ("-" * 60),
            (self.show_story_arcs()),
            (""),
            ("ARC COVERAGE"),
            ("-" * 60),
            (self.show_coverage()),
            (""),
            ("MISSING ELEMENTS"),
            ("-" * 60),
            (self.show_missing_elements()),
            (""),
            ("VALIDATION STATUS"),
            ("-" * 60),
            (self.show_validation_status()),
            (""),
            ("COMPLETENESS"),
            ("-" * 60),
            (self.show_completeness()),
            (""),
            ("=" * 60),
        ]

        return "\n".join(sections)
