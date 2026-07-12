"""Tests for OutlineInspector class.

Tests cover:
- Simple outline display (1 book, 3 sequences, 9 chapters)
- Complex outline (2 books, multiple sequences, many arcs)
- Missing elements detection
- Validation status reporting
- Edge cases (empty sequences, minimal content)
- Completeness calculation
"""

import pytest
from datetime import datetime
from typing import List, Dict, Optional

from auteur.narrative_orchestration.orchestrator import OutlineInspector, ValidationStatus
from auteur.narrative_blueprint.schema.series_outline import SeriesOutline
from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.sequence_outline import SequenceOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint
from auteur.narrative_blueprint.schema.story_arc import StoryArc, ArcCheckpoint
from auteur.narrative_blueprint.schema.outline_types import PhaseRange


class TestOutlineInspectorBasics:
    """Test basic OutlineInspector functionality."""

    def test_inspector_initialization(self):
        """Test OutlineInspector initializes with empty data."""
        inspector = OutlineInspector()
        assert inspector.genre is None
        assert inspector.story_id is None
        assert len(inspector.books) == 0
        assert len(inspector.chapters) == 0
        assert len(inspector.character_arcs) == 0
        assert len(inspector.story_arcs) == 0

    def test_show_structure_empty(self):
        """Test show_structure returns empty message when no artifacts."""
        inspector = OutlineInspector()
        output = inspector.show_structure()
        assert "(empty outline)" in output

    def test_add_artifact_book(self):
        """Test adding a book artifact."""
        inspector = OutlineInspector()
        book = BookOutline(
            genre="mystery",
            story_id="book_001",
            name="The Case",
            description="A mystery",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id=None,
            title="The Case of the Missing Clue",
            chapter_estimate=10,
            structure="3-act",
            phases_summary={
                1: "Setup",
                2: "Investigation begins",
                3: "Clues emerge",
                4: "Red herring",
                5: "Deeper investigation",
                6: "Breakthrough",
                7: "Confrontation",
                8: "Resolution",
                9: "Aftermath"
            }
        )
        inspector.add_artifact(book)
        assert inspector.genre == "mystery"
        assert inspector.story_id == "book_001"
        assert len(inspector.books) == 1
        assert "book_001" in inspector.books

    def test_add_artifact_character_arc(self):
        """Test adding a character arc artifact."""
        inspector = OutlineInspector()
        arc = CharacterArc(
            genre="netorare",
            story_id="character_arc_protag",
            name="Protagonist Arc",
            description="Main character arc",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            span_chapters=[1, 2, 3, 5, 7, 10],
            character_name="Marcus",
            initial_belief="I am secure in my relationship",
            final_belief="I have accepted my wife's infidelity",
            turning_points=[
                TurningPoint(chapter=1, moment="First hint", belief_shift="Confusion"),
                TurningPoint(chapter=5, moment="Undeniable evidence", belief_shift="Denial breaks"),
            ],
            genre_themes=["cuckoldry", "humiliation"]
        )
        inspector.add_artifact(arc)
        assert len(inspector.character_arcs) == 1
        assert "character_arc_protag" in inspector.character_arcs

    def test_add_artifact_unknown_type(self):
        """Test that adding unknown artifact type raises ValueError."""
        inspector = OutlineInspector()
        # Create a mock artifact with unknown type
        class UnknownArtifact:
            def artifact_type(self):
                return "unknown_type"
            genre = "mystery"
            story_id = "unknown_001"

        with pytest.raises(ValueError, match="Unknown artifact type"):
            inspector.add_artifact(UnknownArtifact())


class TestSimpleOutlineDisplay:
    """Test display of simple outline (1 book, 3 sequences, 9 chapters)."""

    @pytest.fixture
    def simple_outline(self) -> OutlineInspector:
        """Create a simple outline for testing."""
        inspector = OutlineInspector()

        # Add book
        book = BookOutline(
            genre="mystery",
            story_id="book_001",
            name="The Investigation",
            description="A mystery investigation",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id=None,
            title="The Case Unfolds",
            chapter_estimate=9,
            structure="3-act",
            phases_summary={i: f"Phase {i}" for i in range(1, 10)}
        )
        inspector.add_artifact(book)

        # Add 3 sequences
        for seq_num in range(1, 4):
            sequence = SequenceOutline(
                genre="mystery",
                story_id=f"sequence_{seq_num:02d}",
                name=f"Sequence {seq_num}",
                description=f"Investigation phase {seq_num}",
                created_at=datetime.now(),
                modified_at=datetime.now(),
                parent_id="book_001",
                sequence_number=seq_num,
                objective=f"Investigate clue set {seq_num}",
                chapter_range=((seq_num - 1) * 3 + 1, seq_num * 3),
                key_scenes=[f"Scene {seq_num}.{j}" for j in range(1, 4)]
            )
            inspector.add_artifact(sequence)

        # Add 9 chapters
        for ch_num in range(1, 10):
            seq_id = f"sequence_{((ch_num - 1) // 3) + 1:02d}"
            chapter = ChapterOutline(
                genre="mystery",
                story_id=f"chapter_{ch_num:02d}",
                name=f"Chapter {ch_num}",
                description=f"Chapter {ch_num} of investigation",
                created_at=datetime.now(),
                modified_at=datetime.now(),
                parent_id=seq_id,
                chapter_number=ch_num,
                phase=ch_num,
                title=f"The Discovery in Chapter {ch_num}",
                goal="Find a new clue",
                conflict="Obstacles block investigation",
                turning_point="Breakthrough moment",
                emotional_beat="Tension rises"
            )
            inspector.add_artifact(chapter)

        return inspector

    def test_simple_structure_display(self, simple_outline):
        """Test display of simple outline structure."""
        output = simple_outline.show_structure()
        assert "Book: The Case Unfolds" in output
        assert "Sequence: Sequence 1" in output
        assert "Sequence: Sequence 3" in output
        assert "Chapter 1: The Discovery in Chapter 1" in output
        assert "Chapter 9: The Discovery in Chapter 9" in output

    def test_simple_missing_elements(self, simple_outline):
        """Test missing elements for simple outline."""
        output = simple_outline.show_missing_elements()
        assert "Series Outline: MISSING" in output
        assert "Books: IMPLEMENTED (1 book(s))" in output
        assert "Chapters: IMPLEMENTED (9 chapter(s))" in output

    def test_simple_completeness(self, simple_outline):
        """Test completeness calculation for simple outline."""
        output = simple_outline.show_completeness()
        assert "Overall Completeness:" in output
        assert "Structural Elements:" in output
        assert "Chapter Details:" in output


class TestComplexOutlineDisplay:
    """Test display of complex outline (2 books, multiple sequences, many arcs)."""

    @pytest.fixture
    def complex_outline(self) -> OutlineInspector:
        """Create a complex outline for testing."""
        inspector = OutlineInspector()

        # Add series
        series = SeriesOutline(
            genre="netorare",
            story_id="series_001",
            name="The Progression",
            description="A multi-book series",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id=None,
            series_name="Cuckoldry Chronicles",
            book_ids=["book_001", "book_002"],
            long_term_character_evolution={
                "Marcus": "From confident to accepting",
                "Claire": "From innocent to knowing"
            },
            thematic_progression=["Suspicion", "Acceptance", "Normalization"]
        )
        inspector.add_artifact(series)

        # Add 2 books with chapters
        for book_num in range(1, 3):
            book = BookOutline(
                genre="netorare",
                story_id=f"book_{book_num:03d}",
                name=f"Book {book_num}",
                description=f"Book {book_num} of series",
                created_at=datetime.now(),
                modified_at=datetime.now(),
                parent_id="series_001",
                title=f"Book {book_num}: The Escalation" if book_num == 1 else "Book 2: The Normalization",
                chapter_estimate=10,
                structure="3-act",
                phases_summary={i: f"Phase {i}" for i in range(1, 10)}
            )
            inspector.add_artifact(book)

            # Add chapters for each book
            for ch_num in range(1, 11):
                chapter = ChapterOutline(
                    genre="netorare",
                    story_id=f"chapter_b{book_num}_c{ch_num:02d}",
                    name=f"Book {book_num} Chapter {ch_num}",
                    description=f"Chapter in book {book_num}",
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                    parent_id=f"book_{book_num:03d}",
                    chapter_number=ch_num,
                    phase=(ch_num // 2) + 1,
                    title=f"Chapter {ch_num}: The Progression Continues",
                    goal="Advance the cuckoldry",
                    conflict="Emotional resistance",
                    turning_point="Acceptance moment",
                    emotional_beat="Humiliation crescendo",
                    arc_progressions={"cuckoldry": "Acceptance grows", "humiliation": "Peaks"}
                )
                inspector.add_artifact(chapter)

        # Add character arc with multiple turning points
        char_arc = CharacterArc(
            genre="netorare",
            story_id="character_arc_marcus",
            name="Marcus Arc",
            description="Protagonist transformation",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            span_chapters=list(range(1, 11)),
            character_name="Marcus",
            initial_belief="I will protect my wife",
            final_belief="I accept and desire her with others",
            turning_points=[
                TurningPoint(chapter=1, moment="First suspicion", belief_shift="Doubt enters"),
                TurningPoint(chapter=3, moment="Undeniable evidence", belief_shift="Denial breaks"),
                TurningPoint(chapter=5, moment="Impossible desire", belief_shift="Arousal confuses"),
                TurningPoint(chapter=7, moment="First watching", belief_shift="Reality shifts"),
                TurningPoint(chapter=9, moment="Acceptance", belief_shift="Embrace desire"),
            ],
            genre_themes=["cuckoldry", "humiliation", "acceptance"]
        )
        inspector.add_artifact(char_arc)

        # Add story arc
        story_arc = StoryArc(
            genre="netorare",
            story_id="story_arc_cuckoldry",
            name="The Cuckoldry Progression",
            description="Plot arc of increasing acceptance",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            arc_name="Cuckoldry Evolution",
            arc_category="romance",
            phase_range=PhaseRange(start=1, peak=5, end=9),
            checkpoints=[
                ArcCheckpoint(phase=1, moment="Temptation introduced"),
                ArcCheckpoint(phase=3, moment="Opportunity seized"),
                ArcCheckpoint(phase=5, moment="First time"),
                ArcCheckpoint(phase=7, moment="Becoming routine"),
                ArcCheckpoint(phase=9, moment="New normal established"),
            ],
            span_chapters=list(range(1, 11))
        )
        inspector.add_artifact(story_arc)

        return inspector

    def test_complex_structure_display(self, complex_outline):
        """Test display of complex outline structure."""
        output = complex_outline.show_structure()
        assert "Series: Cuckoldry Chronicles" in output
        assert "Book: Book 1: The Escalation" in output
        assert "Book: Book 2: The Normalization" in output
        assert "Chapter 1:" in output
        assert "Chapter 10:" in output

    def test_complex_character_arcs_display(self, complex_outline):
        """Test display of character arcs."""
        output = complex_outline.show_character_arcs()
        assert "Character Arc: Marcus" in output
        assert "Initial Belief:" in output
        assert "Final Belief:" in output
        assert "Genre Themes: cuckoldry, humiliation, acceptance" in output
        assert "Turning Points:" in output
        assert "First suspicion" in output

    def test_complex_story_arcs_display(self, complex_outline):
        """Test display of story arcs."""
        output = complex_outline.show_story_arcs()
        assert "Story Arc: Cuckoldry Evolution" in output
        assert "Category: romance" in output
        assert "Phase Range:" in output
        assert "Checkpoints:" in output
        assert "Temptation introduced" in output

    def test_complex_coverage_display(self, complex_outline):
        """Test display of arc coverage."""
        output = complex_outline.show_coverage()
        assert "Chapter Coverage:" in output
        assert "Character Arc (Marcus)" in output
        assert "Story Arc (Cuckoldry Evolution)" in output

    def test_complex_missing_elements(self, complex_outline):
        """Test missing elements for complex outline."""
        output = complex_outline.show_missing_elements()
        assert "Series Outline: IMPLEMENTED" in output
        assert "Character Arcs: IMPLEMENTED" in output
        assert "Story Arcs: IMPLEMENTED" in output

    def test_complex_completeness(self, complex_outline):
        """Test completeness calculation for complex outline."""
        output = complex_outline.show_completeness()
        assert "Overall Completeness:" in output
        assert "Structural Elements:" in output


class TestMissingElementsDetection:
    """Test missing elements detection functionality."""

    def test_missing_series_outline(self):
        """Test detection of missing series outline."""
        inspector = OutlineInspector()
        book = BookOutline(
            genre="mystery",
            story_id="book_001",
            name="Book",
            description="A book",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id=None,
            title="Single Book",
            chapter_estimate=5,
            structure="3-act",
            phases_summary={i: f"Phase {i}" for i in range(1, 10)}
        )
        inspector.add_artifact(book)

        output = inspector.show_missing_elements()
        assert "Series Outline: MISSING (optional, but recommended for multi-book)" in output

    def test_missing_chapters(self):
        """Test detection of missing chapters."""
        inspector = OutlineInspector()
        book = BookOutline(
            genre="mystery",
            story_id="book_001",
            name="Book",
            description="A book",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id=None,
            title="Book with no chapters",
            chapter_estimate=5,
            structure="3-act",
            phases_summary={i: f"Phase {i}" for i in range(1, 10)}
        )
        inspector.add_artifact(book)

        output = inspector.show_missing_elements()
        assert "Chapters: MISSING (required)" in output

    def test_partial_arc_progressions(self):
        """Test detection of partial arc progressions."""
        inspector = OutlineInspector()

        book = BookOutline(
            genre="mystery",
            story_id="book_001",
            name="Book",
            description="A book",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id=None,
            title="Book",
            chapter_estimate=3,
            structure="3-act",
            phases_summary={i: f"Phase {i}" for i in range(1, 10)}
        )
        inspector.add_artifact(book)

        # Add chapters, only some with progressions
        for i in range(1, 4):
            chapter = ChapterOutline(
                genre="mystery",
                story_id=f"chapter_{i:02d}",
                name=f"Chapter {i}",
                description="",
                created_at=datetime.now(),
                modified_at=datetime.now(),
                parent_id="book_001",
                chapter_number=i,
                phase=i,
                title=f"Chapter {i}",
                goal="Goal",
                conflict="Conflict",
                turning_point="Turning point",
                emotional_beat="Beat",
                arc_progressions={"detective": "Discovers clue"} if i % 2 == 0 else None
            )
            inspector.add_artifact(chapter)

        output = inspector.show_missing_elements()
        assert "Chapter Arc Progressions: PARTIAL" in output


class TestValidationStatusReporting:
    """Test validation status reporting."""

    def test_all_validators_pass(self):
        """Test reporting when all validators pass."""
        inspector = OutlineInspector()
        inspector.add_validation_status("Reference Validator", True)
        inspector.add_validation_status("Chronological Validator", True)
        inspector.add_validation_status("Contradiction Validator", True)

        output = inspector.show_validation_status()
        assert "Reference Validator: PASS" in output
        assert "Chronological Validator: PASS" in output
        assert "Contradiction Validator: PASS" in output

    def test_validator_with_errors(self):
        """Test reporting when validator fails with errors."""
        inspector = OutlineInspector()
        inspector.add_validation_status(
            "Reference Validator",
            False,
            errors=["Missing chapter reference", "Broken arc reference"],
            warnings=[]
        )

        output = inspector.show_validation_status()
        assert "Reference Validator: FAIL" in output
        assert "Missing chapter reference" in output
        assert "Broken arc reference" in output

    def test_validator_with_warnings(self):
        """Test reporting when validator fails with warnings."""
        inspector = OutlineInspector()
        inspector.add_validation_status(
            "Arc Validator",
            False,
            errors=["Some arc beats missing"],
            warnings=["Some arc beats could be stronger"]
        )

        output = inspector.show_validation_status()
        assert "Arc Validator: FAIL" in output
        assert "Some arc beats missing" in output
        assert "Some arc beats could be stronger" in output

    def test_no_validation_status(self):
        """Test reporting when no validation status is recorded."""
        inspector = OutlineInspector()
        output = inspector.show_validation_status()
        assert "(no validation status recorded)" in output


class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_empty_sequence(self):
        """Test display with sequence that has no chapters."""
        inspector = OutlineInspector()

        book = BookOutline(
            genre="mystery",
            story_id="book_001",
            name="Book",
            description="",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id=None,
            title="Book",
            chapter_estimate=1,
            structure="3-act",
            phases_summary={i: f"Phase {i}" for i in range(1, 10)}
        )
        inspector.add_artifact(book)

        sequence = SequenceOutline(
            genre="mystery",
            story_id="sequence_01",
            name="Empty Sequence",
            description="",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id="book_001",
            sequence_number=1,
            objective="",
            chapter_range=(1, 1)
        )
        inspector.add_artifact(sequence)

        output = inspector.show_structure()
        assert "Sequence: Empty Sequence" in output

    def test_minimal_outline(self):
        """Test display with minimal outline (only book, no sequences or arcs)."""
        inspector = OutlineInspector()

        book = BookOutline(
            genre="mystery",
            story_id="book_001",
            name="Book",
            description="",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id=None,
            title="Minimal Book",
            chapter_estimate=1,
            structure="3-act",
            phases_summary={i: f"Phase {i}" for i in range(1, 10)}
        )
        inspector.add_artifact(book)

        chapter = ChapterOutline(
            genre="mystery",
            story_id="chapter_01",
            name="Chapter",
            description="",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id="book_001",
            chapter_number=1,
            phase=1,
            title="Only Chapter",
            goal="",
            conflict="",
            turning_point="",
            emotional_beat=""
        )
        inspector.add_artifact(chapter)

        output = inspector.show_structure()
        assert "Book: Minimal Book" in output
        assert "Chapter 1: Only Chapter" in output

    def test_arcs_without_turning_points(self):
        """Test display of arcs with no turning points or checkpoints."""
        inspector = OutlineInspector()

        char_arc = CharacterArc(
            genre="netorare",
            story_id="character_arc_empty",
            name="Empty Arc",
            description="",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            span_chapters=[1, 2],
            character_name="Empty Character",
            initial_belief="Initial",
            final_belief="Final",
            turning_points=[],
            genre_themes=["theme"]
        )
        inspector.add_artifact(char_arc)

        output = inspector.show_character_arcs()
        assert "Character Arc: Empty Character" in output
        assert "(none)" in output

    def test_completeness_with_no_content(self):
        """Test completeness calculation with no artifacts."""
        inspector = OutlineInspector()
        output = inspector.show_completeness()
        assert "Overall Completeness:" in output


class TestComprehensiveSummary:
    """Test comprehensive summary report generation."""

    def test_generate_summary_structure(self):
        """Test that summary report has all expected sections."""
        inspector = OutlineInspector()

        # Add minimal artifacts
        book = BookOutline(
            genre="mystery",
            story_id="book_001",
            name="Book",
            description="",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id=None,
            title="Test Book",
            chapter_estimate=1,
            structure="3-act",
            phases_summary={i: f"Phase {i}" for i in range(1, 10)}
        )
        inspector.add_artifact(book)

        chapter = ChapterOutline(
            genre="mystery",
            story_id="chapter_01",
            name="Chapter",
            description="",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id="book_001",
            chapter_number=1,
            phase=1,
            title="Chapter 1",
            goal="",
            conflict="",
            turning_point="",
            emotional_beat=""
        )
        inspector.add_artifact(chapter)

        summary = inspector.generate_summary()
        assert "OUTLINE STATUS REPORT" in summary
        assert "STRUCTURE" in summary
        assert "CHARACTER ARCS" in summary
        assert "STORY ARCS" in summary
        assert "ARC COVERAGE" in summary
        assert "MISSING ELEMENTS" in summary
        assert "VALIDATION STATUS" in summary
        assert "COMPLETENESS" in summary

    def test_generate_summary_includes_all_data(self):
        """Test that summary includes all outline data."""
        inspector = OutlineInspector()

        book = BookOutline(
            genre="netorare",
            story_id="book_001",
            name="Book",
            description="",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id=None,
            title="Test Book",
            chapter_estimate=2,
            structure="3-act",
            phases_summary={i: f"Phase {i}" for i in range(1, 10)}
        )
        inspector.add_artifact(book)

        for i in range(1, 3):
            chapter = ChapterOutline(
                genre="netorare",
                story_id=f"chapter_{i:02d}",
                name=f"Chapter {i}",
                description="",
                created_at=datetime.now(),
                modified_at=datetime.now(),
                parent_id="book_001",
                chapter_number=i,
                phase=i,
                title=f"Chapter {i}",
                goal="",
                conflict="",
                turning_point="",
                emotional_beat=""
            )
            inspector.add_artifact(chapter)

        char_arc = CharacterArc(
            genre="netorare",
            story_id="character_arc_test",
            name="Test Arc",
            description="",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            span_chapters=[1, 2],
            character_name="Test Character",
            initial_belief="Start",
            final_belief="End",
            turning_points=[TurningPoint(chapter=1, moment="Event", belief_shift="Change")],
            genre_themes=["theme1"]
        )
        inspector.add_artifact(char_arc)

        inspector.add_validation_status("Test Validator", True)

        summary = inspector.generate_summary()
        assert "Test Book" in summary
        assert "Test Character" in summary
        assert "Test Validator: PASS" in summary
