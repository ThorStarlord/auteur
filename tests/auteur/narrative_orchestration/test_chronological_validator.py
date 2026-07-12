"""Tests for chronological validator in Layer 2.5 narrative orchestration."""

import pytest
from datetime import datetime

from auteur.narrative_orchestration.validator.chronological_validator import (
    ChronologicalValidator,
    ChronologyViolationType,
)
from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.sequence_outline import SequenceOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint
from auteur.narrative_blueprint.schema.story_arc import StoryArc, ArcCheckpoint
from auteur.narrative_blueprint.schema.outline_types import PhaseRange


class TestChronologicalValidatorBasics:
    """Test basic ChronologicalValidator functionality."""

    def test_validator_initialization(self):
        """Test that validator initializes with empty collections."""
        validator = ChronologicalValidator()

        assert len(validator.books) == 0
        assert len(validator.sequences) == 0
        assert len(validator.chapters) == 0
        assert len(validator.character_arcs) == 0
        assert len(validator.story_arcs) == 0
        assert len(validator.violations) == 0

    def test_add_book(self):
        """Test adding a book to the validator."""
        validator = ChronologicalValidator()
        now = datetime.now()

        book = BookOutline(
            genre="netorare",
            story_id="story_001",
            name="book_1",
            description="First book",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Book One",
            chapter_estimate=12,
            structure="3-act",
            phases_summary={i: f"Phase {i}" for i in range(1, 10)},
        )

        validator.add_book("book_001", book)
        assert len(validator.books) == 1
        assert "book_001" in validator.books
        assert validator.books["book_001"].title == "Book One"

    def test_add_chapter(self):
        """Test adding a chapter to the validator."""
        validator = ChronologicalValidator()
        now = datetime.now()

        chapter = ChapterOutline(
            genre="netorare",
            story_id="story_001",
            name="chapter_1",
            description="First chapter",
            created_at=now,
            modified_at=now,
            parent_id="book_001",
            chapter_number=1,
            phase=1,
            title="Chapter One",
            goal="Introduce protagonist",
            conflict="Uncertainty about future",
            turning_point="First meeting",
            emotional_beat="Hope → Anticipation",
        )

        validator.add_chapter("chapter_001", chapter)
        assert len(validator.chapters) == 1
        assert validator.chapters["chapter_001"].chapter_number == 1

    def test_add_character_arc(self):
        """Test adding a character arc to the validator."""
        validator = ChronologicalValidator()
        now = datetime.now()

        arc = CharacterArc(
            genre="netorare",
            story_id="story_001",
            name="clara_arc",
            description="Clara's journey",
            created_at=now,
            modified_at=now,
            span_chapters=[1, 2, 3, 4, 5],
            character_name="Clara",
            initial_belief="Love conquers all",
            final_belief="Love is complicated",
            turning_points=[
                TurningPoint(chapter=1, moment="First meeting", belief_shift="Initial attraction"),
                TurningPoint(chapter=3, moment="Betrayal", belief_shift="Doubt emerges"),
                TurningPoint(chapter=5, moment="Acceptance", belief_shift="Understanding"),
            ],
            genre_themes=["humiliation", "cuckoldry"],
        )

        validator.add_character_arc("character_arc_clara", arc)
        assert len(validator.character_arcs) == 1
        assert validator.character_arcs["character_arc_clara"].character_name == "Clara"

    def test_add_story_arc(self):
        """Test adding a story arc to the validator."""
        validator = ChronologicalValidator()
        now = datetime.now()

        arc = StoryArc(
            genre="netorare",
            story_id="story_001",
            name="cuckoldry_arc",
            description="The cuckoldry progression",
            created_at=now,
            modified_at=now,
            arc_name="The Descent",
            arc_category="romance",
            phase_range=PhaseRange(start=1, peak=5, end=9),
            checkpoints=[
                ArcCheckpoint(phase=1, moment="Temptation introduced"),
                ArcCheckpoint(phase=5, moment="Point of no return"),
                ArcCheckpoint(phase=9, moment="New reality accepted"),
            ],
            span_chapters=[1, 5, 9],
        )

        validator.add_story_arc("story_arc_cuckoldry", arc)
        assert len(validator.story_arcs) == 1
        assert validator.story_arcs["story_arc_cuckoldry"].arc_name == "The Descent"


class TestCharacterArcProgression:
    """Test character arc beat ordering validation."""

    def test_valid_character_arc_progression(self):
        """Test that valid arc progression passes validation."""
        validator = ChronologicalValidator()
        now = datetime.now()

        arc = CharacterArc(
            genre="netorare",
            story_id="story_001",
            name="clara_arc",
            description="Clara's journey",
            created_at=now,
            modified_at=now,
            span_chapters=[1, 3, 5],
            character_name="Clara",
            initial_belief="Love conquers all",
            final_belief="Love is complicated",
            turning_points=[
                TurningPoint(chapter=1, moment="First meeting", belief_shift="Attraction"),
                TurningPoint(chapter=3, moment="Betrayal", belief_shift="Doubt"),
                TurningPoint(chapter=5, moment="Acceptance", belief_shift="Understanding"),
            ],
            genre_themes=["humiliation", "cuckoldry"],
        )

        validator.add_character_arc("character_arc_clara", arc)
        violations = validator.validate_character_arc_progression()

        assert len(violations) == 0

    def test_arc_beats_out_of_order(self):
        """Test detection of out-of-order character arc beats."""
        validator = ChronologicalValidator()
        now = datetime.now()

        arc = CharacterArc(
            genre="netorare",
            story_id="story_001",
            name="clara_arc",
            description="Clara's journey",
            created_at=now,
            modified_at=now,
            span_chapters=[5, 3, 1],
            character_name="Clara",
            initial_belief="Love conquers all",
            final_belief="Love is complicated",
            turning_points=[
                TurningPoint(chapter=5, moment="Acceptance", belief_shift="Understanding"),
                TurningPoint(chapter=3, moment="Betrayal", belief_shift="Doubt"),
                TurningPoint(chapter=1, moment="First meeting", belief_shift="Attraction"),
            ],
            genre_themes=["humiliation", "cuckoldry"],
        )

        validator.add_character_arc("character_arc_clara", arc)
        violations = validator.validate_character_arc_progression()

        assert len(violations) >= 2
        assert any(v.violation_type == ChronologyViolationType.ARC_BEAT_OUT_OF_ORDER for v in violations)

    def test_single_turning_point(self):
        """Test that single turning point passes validation (edge case)."""
        validator = ChronologicalValidator()
        now = datetime.now()

        arc = CharacterArc(
            genre="netorare",
            story_id="story_001",
            name="minor_arc",
            description="Minor character arc",
            created_at=now,
            modified_at=now,
            span_chapters=[3],
            character_name="Extra",
            initial_belief="Initial belief",
            final_belief="Final belief",
            turning_points=[
                TurningPoint(chapter=3, moment="Single moment", belief_shift="Shift"),
            ],
            genre_themes=["humiliation"],
        )

        validator.add_character_arc("character_arc_extra", arc)
        violations = validator.validate_character_arc_progression()

        assert len(violations) == 0

    def test_empty_turning_points(self):
        """Test that arc with no turning points passes validation (edge case)."""
        validator = ChronologicalValidator()
        now = datetime.now()

        arc = CharacterArc(
            genre="netorare",
            story_id="story_001",
            name="flat_arc",
            description="No turning points",
            created_at=now,
            modified_at=now,
            span_chapters=[1, 2, 3],
            character_name="Static",
            initial_belief="Initial belief",
            final_belief="Final belief",
            turning_points=[],
            genre_themes=["humiliation"],
        )

        validator.add_character_arc("character_arc_static", arc)
        violations = validator.validate_character_arc_progression()

        assert len(violations) == 0


class TestStoryArcTiming:
    """Test story arc checkpoint phase ordering validation."""

    def test_valid_story_arc_timing(self):
        """Test that valid story arc checkpoint progression passes validation."""
        validator = ChronologicalValidator()
        now = datetime.now()

        arc = StoryArc(
            genre="netorare",
            story_id="story_001",
            name="cuckoldry_arc",
            description="The cuckoldry progression",
            created_at=now,
            modified_at=now,
            arc_name="The Descent",
            arc_category="romance",
            phase_range=PhaseRange(start=1, peak=5, end=9),
            checkpoints=[
                ArcCheckpoint(phase=1, moment="Temptation"),
                ArcCheckpoint(phase=5, moment="Peak"),
                ArcCheckpoint(phase=9, moment="Resolution"),
            ],
            span_chapters=[1, 5, 9],
        )

        validator.add_story_arc("story_arc_cuckoldry", arc)
        violations = validator.validate_story_arc_timing()

        assert len(violations) == 0

    def test_story_arc_checkpoint_out_of_order(self):
        """Test detection of out-of-order story arc checkpoints."""
        validator = ChronologicalValidator()
        now = datetime.now()

        arc = StoryArc(
            genre="netorare",
            story_id="story_001",
            name="cuckoldry_arc",
            description="The cuckoldry progression",
            created_at=now,
            modified_at=now,
            arc_name="The Descent",
            arc_category="romance",
            phase_range=PhaseRange(start=1, peak=5, end=9),
            checkpoints=[
                ArcCheckpoint(phase=9, moment="Resolution"),
                ArcCheckpoint(phase=5, moment="Peak"),
                ArcCheckpoint(phase=1, moment="Temptation"),
            ],
            span_chapters=[9, 5, 1],
        )

        validator.add_story_arc("story_arc_cuckoldry", arc)
        violations = validator.validate_story_arc_timing()

        assert len(violations) >= 2
        assert any(v.violation_type == ChronologyViolationType.ARC_CHECKPOINT_OUT_OF_ORDER for v in violations)

    def test_story_arc_checkpoint_outside_range(self):
        """Test detection of checkpoints outside arc's phase range."""
        validator = ChronologicalValidator()
        now = datetime.now()

        arc = StoryArc(
            genre="netorare",
            story_id="story_001",
            name="cuckoldry_arc",
            description="The cuckoldry progression",
            created_at=now,
            modified_at=now,
            arc_name="The Descent",
            arc_category="romance",
            phase_range=PhaseRange(start=3, peak=5, end=7),
            checkpoints=[
                ArcCheckpoint(phase=1, moment="Too early"),
                ArcCheckpoint(phase=5, moment="Valid"),
                ArcCheckpoint(phase=9, moment="Too late"),
            ],
            span_chapters=[1, 5, 9],
        )

        validator.add_story_arc("story_arc_cuckoldry", arc)
        violations = validator.validate_story_arc_timing()

        assert len(violations) >= 2
        assert any(v.violation_type == ChronologyViolationType.PHASE_OUT_OF_ORDER for v in violations)

    def test_single_checkpoint(self):
        """Test that single checkpoint passes validation (edge case)."""
        validator = ChronologicalValidator()
        now = datetime.now()

        arc = StoryArc(
            genre="mystery",
            story_id="story_001",
            name="single_arc",
            description="Single checkpoint arc",
            created_at=now,
            modified_at=now,
            arc_name="One Point",
            arc_category="mystery",
            phase_range=PhaseRange(start=5, peak=5, end=5),
            checkpoints=[
                ArcCheckpoint(phase=5, moment="Single checkpoint"),
            ],
            span_chapters=[5],
        )

        validator.add_story_arc("story_arc_single", arc)
        violations = validator.validate_story_arc_timing()

        assert len(violations) == 0

    def test_empty_checkpoints(self):
        """Test that arc with no checkpoints passes validation (edge case)."""
        validator = ChronologicalValidator()
        now = datetime.now()

        arc = StoryArc(
            genre="mystery",
            story_id="story_001",
            name="no_checkpoint_arc",
            description="Arc with no checkpoints",
            created_at=now,
            modified_at=now,
            arc_name="Empty Arc",
            arc_category="mystery",
            phase_range=PhaseRange(start=1, peak=5, end=9),
            checkpoints=[],
            span_chapters=[1, 5, 9],
        )

        validator.add_story_arc("story_arc_empty", arc)
        violations = validator.validate_story_arc_timing()

        assert len(violations) == 0


class TestPhaseProgression:
    """Test chapter phase ordering validation."""

    def test_valid_phase_progression(self):
        """Test that chapters with progressive phases pass validation."""
        validator = ChronologicalValidator()
        now = datetime.now()

        for i in range(1, 10):
            chapter = ChapterOutline(
                genre="netorare",
                story_id="story_001",
                name=f"chapter_{i}",
                description=f"Chapter {i}",
                created_at=now,
                modified_at=now,
                parent_id="book_001",
                chapter_number=i,
                phase=i,
                title=f"Chapter {i}",
                goal="Progress story",
                conflict="Some conflict",
                turning_point="A moment",
                emotional_beat="Building tension",
            )
            validator.add_chapter(f"chapter_{i:03d}", chapter)

        violations = validator.validate_phase_progression()

        assert len(violations) == 0

    def test_phases_out_of_order(self):
        """Test detection of out-of-order phases."""
        validator = ChronologicalValidator()
        now = datetime.now()

        # Create chapters with phases out of order
        chapters_data = [
            (1, 1),
            (2, 9),  # Phase 9 too early
            (3, 5),
            (4, 3),  # Phase 3 after phase 5
        ]

        for chapter_num, phase in chapters_data:
            chapter = ChapterOutline(
                genre="netorare",
                story_id="story_001",
                name=f"chapter_{chapter_num}",
                description=f"Chapter {chapter_num}",
                created_at=now,
                modified_at=now,
                parent_id="book_001",
                chapter_number=chapter_num,
                phase=phase,
                title=f"Chapter {chapter_num}",
                goal="Progress story",
                conflict="Some conflict",
                turning_point="A moment",
                emotional_beat="Building tension",
            )
            validator.add_chapter(f"chapter_{chapter_num:03d}", chapter)

        violations = validator.validate_phase_progression()

        # Should detect phase ordering issues
        assert len(violations) >= 1
        assert any(v.violation_type == ChronologyViolationType.PHASE_OUT_OF_ORDER for v in violations)


class TestCompleteValidation:
    """Test orchestrated validation across all checks."""

    def test_validate_all_chronology_passes(self):
        """Test that valid outline passes all chronology checks."""
        validator = ChronologicalValidator()
        now = datetime.now()

        # Add a single valid chapter
        chapter = ChapterOutline(
            genre="netorare",
            story_id="story_001",
            name="chapter_1",
            description="Chapter 1",
            created_at=now,
            modified_at=now,
            parent_id="book_001",
            chapter_number=1,
            phase=1,
            title="Chapter 1",
            goal="Introduce story",
            conflict="Initial conflict",
            turning_point="First meeting",
            emotional_beat="Hope",
        )
        validator.add_chapter("chapter_001", chapter)

        # Add valid character arc
        arc = CharacterArc(
            genre="netorare",
            story_id="story_001",
            name="char_arc",
            description="Character arc",
            created_at=now,
            modified_at=now,
            span_chapters=[1],
            character_name="Protagonist",
            initial_belief="Initial",
            final_belief="Final",
            turning_points=[TurningPoint(chapter=1, moment="Moment", belief_shift="Shift")],
            genre_themes=["humiliation"],
        )
        validator.add_character_arc("character_arc_01", arc)

        result = validator.validate_all_chronology()

        assert result is True
        assert len(validator.violations) == 0

    def test_validate_all_chronology_fails(self):
        """Test that invalid outline fails chronology checks."""
        validator = ChronologicalValidator()
        now = datetime.now()

        # Add character arc with out-of-order beats
        arc = CharacterArc(
            genre="netorare",
            story_id="story_001",
            name="char_arc",
            description="Character arc",
            created_at=now,
            modified_at=now,
            span_chapters=[5, 1],
            character_name="Protagonist",
            initial_belief="Initial",
            final_belief="Final",
            turning_points=[
                TurningPoint(chapter=5, moment="Later", belief_shift="Shift"),
                TurningPoint(chapter=1, moment="Earlier", belief_shift="Shift"),
            ],
            genre_themes=["humiliation"],
        )
        validator.add_character_arc("character_arc_01", arc)

        result = validator.validate_all_chronology()

        assert result is False
        assert len(validator.violations) > 0

    def test_report_chronological_issues_no_violations(self):
        """Test that report indicates no violations when valid."""
        validator = ChronologicalValidator()
        validator.violations = []

        report = validator.report_chronological_issues()

        assert "No chronological violations found" in report

    def test_report_chronological_issues_with_violations(self):
        """Test that report includes all violations."""
        validator = ChronologicalValidator()
        now = datetime.now()

        # Create arc with out-of-order beats to generate violations
        arc = CharacterArc(
            genre="netorare",
            story_id="story_001",
            name="char_arc",
            description="Character arc",
            created_at=now,
            modified_at=now,
            span_chapters=[5, 3],
            character_name="Protagonist",
            initial_belief="Initial",
            final_belief="Final",
            turning_points=[
                TurningPoint(chapter=5, moment="Later", belief_shift="Shift"),
                TurningPoint(chapter=3, moment="Earlier", belief_shift="Shift"),
            ],
            genre_themes=["humiliation"],
        )
        validator.add_character_arc("character_arc_01", arc)

        validator.validate_all_chronology()
        report = validator.report_chronological_issues()

        assert "Chronological Violations Report" in report
        assert "ARC_BEAT_OUT_OF_ORDER" in report

    def test_get_violations_by_type(self):
        """Test filtering violations by type."""
        validator = ChronologicalValidator()
        now = datetime.now()

        # Create multiple violation types
        arc1 = CharacterArc(
            genre="netorare",
            story_id="story_001",
            name="arc1",
            description="Arc 1",
            created_at=now,
            modified_at=now,
            span_chapters=[5, 3],
            character_name="Char1",
            initial_belief="A",
            final_belief="B",
            turning_points=[
                TurningPoint(chapter=5, moment="Later", belief_shift="Shift"),
                TurningPoint(chapter=3, moment="Earlier", belief_shift="Shift"),
            ],
            genre_themes=["humiliation"],
        )
        validator.add_character_arc("char_arc_01", arc1)

        arc2 = StoryArc(
            genre="netorare",
            story_id="story_001",
            name="arc2",
            description="Arc 2",
            created_at=now,
            modified_at=now,
            arc_name="Story Arc",
            arc_category="romance",
            phase_range=PhaseRange(start=1, peak=5, end=9),
            checkpoints=[
                ArcCheckpoint(phase=9, moment="Last"),
                ArcCheckpoint(phase=1, moment="First"),
            ],
        )
        validator.add_story_arc("story_arc_01", arc2)

        validator.validate_all_chronology()

        # Get only arc beat violations
        arc_beat_violations = validator.get_violations(
            violation_type=ChronologyViolationType.ARC_BEAT_OUT_OF_ORDER
        )
        assert len(arc_beat_violations) >= 1

        # Get only error severity violations
        errors = validator.get_violations(severity="error")
        assert len(errors) >= 1

    def test_has_violations(self):
        """Test checking for existence of violations."""
        validator = ChronologicalValidator()
        now = datetime.now()

        # Initially no violations
        assert not validator.has_violations()

        # Add invalid arc
        arc = CharacterArc(
            genre="netorare",
            story_id="story_001",
            name="arc",
            description="Arc",
            created_at=now,
            modified_at=now,
            span_chapters=[5, 1],
            character_name="Char",
            initial_belief="A",
            final_belief="B",
            turning_points=[
                TurningPoint(chapter=5, moment="Later", belief_shift="Shift"),
                TurningPoint(chapter=1, moment="Earlier", belief_shift="Shift"),
            ],
            genre_themes=["humiliation"],
        )
        validator.add_character_arc("char_arc_01", arc)

        validator.validate_all_chronology()

        # Now has violations
        assert validator.has_violations()
        assert validator.has_violations(severity="error")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_validator(self):
        """Test validation on completely empty validator."""
        validator = ChronologicalValidator()

        result = validator.validate_all_chronology()

        assert result is True
        assert len(validator.violations) == 0

    def test_single_chapter_valid(self):
        """Test single chapter in narrative."""
        validator = ChronologicalValidator()
        now = datetime.now()

        chapter = ChapterOutline(
            genre="netorare",
            story_id="story_001",
            name="only_chapter",
            description="Only chapter",
            created_at=now,
            modified_at=now,
            parent_id="book_001",
            chapter_number=1,
            phase=5,
            title="Only Chapter",
            goal="Tell entire story",
            conflict="All conflict here",
            turning_point="The moment",
            emotional_beat="Complete journey",
        )
        validator.add_chapter("chapter_001", chapter)

        result = validator.validate_all_chronology()

        assert result is True

    def test_multiple_genres(self):
        """Test validation across different genres."""
        validator = ChronologicalValidator()
        now = datetime.now()

        # Add netorare arc
        arc1 = CharacterArc(
            genre="netorare",
            story_id="story_001",
            name="arc1",
            description="Netorare arc",
            created_at=now,
            modified_at=now,
            span_chapters=[1, 2, 3],
            character_name="Char1",
            initial_belief="A",
            final_belief="B",
            turning_points=[
                TurningPoint(chapter=1, moment="First", belief_shift="Shift1"),
                TurningPoint(chapter=2, moment="Second", belief_shift="Shift2"),
                TurningPoint(chapter=3, moment="Third", belief_shift="Shift3"),
            ],
            genre_themes=["humiliation"],
        )
        validator.add_character_arc("char_arc_netorare", arc1)

        # Add mystery arc
        arc2 = CharacterArc(
            genre="mystery",
            story_id="story_002",
            name="arc2",
            description="Mystery arc",
            created_at=now,
            modified_at=now,
            span_chapters=[1, 2, 3],
            character_name="Char2",
            initial_belief="X",
            final_belief="Y",
            turning_points=[
                TurningPoint(chapter=1, moment="Clue1", belief_shift="Shift1"),
                TurningPoint(chapter=2, moment="Clue2", belief_shift="Shift2"),
                TurningPoint(chapter=3, moment="Resolution", belief_shift="Shift3"),
            ],
            genre_themes=["deduction"],
        )
        validator.add_character_arc("char_arc_mystery", arc2)

        result = validator.validate_all_chronology()

        assert result is True
        assert len(validator.character_arcs) == 2
