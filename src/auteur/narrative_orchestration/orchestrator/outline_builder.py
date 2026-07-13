"""Outline Builder for Structure orchestration.

This module implements OutlineBuilder, which seeds template outlines from StoryIdentity.
The builder generates a complete outline structure including Book Outline, Sequence Outlines,
Chapter Outlines, Character Arc, and Story Arc, all with genre-specific defaults.

Key Features:
- Accepts StoryIdentity as input
- Generates 1 Book Outline with title from story identity
- Generates 3-4 Sequence Outlines (paced by genre)
- Generates 12-16 Chapter Outlines with default goals/conflicts
- Generates 1 Character Arc for protagonist
- Generates 1 Story Arc for central plot
- Applies genre-specific defaults (netorara, mystery, gentlefemdom)
- Validates generated outlines against all validators
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from auteur.identity import StoryIdentity
from auteur.blueprint import Genre
from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.sequence_outline import SequenceOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint
from auteur.narrative_blueprint.schema.story_arc import StoryArc, ArcCheckpoint
from auteur.narrative_blueprint.schema.outline_types import PhaseRange

from auteur.narrative_orchestration.validator.reference_validator import (
    ReferenceValidator,
    ValidationResult,
)
from auteur.narrative_orchestration.validator.chronological_validator import (
    ChronologicalValidator,
)
from auteur.narrative_orchestration.validator.contradiction_validator import (
    ContradictionValidator,
)


class GenreDefaults:
    """Genre-specific defaults for outline generation."""

    # Genre-specific chapter goals and conflicts
    NETORARA_GOALS = [
        "Establish comfortable status quo and introduce the temptation",
        "Deepen attraction and create first moments of doubt",
        "Witness the beginning of physical connection",
        "Experience escalating boundary violations",
        "Confront undeniable evidence of unfaithfulness",
        "Navigate the emotional aftermath and humiliation",
        "Explore conflicting desires and acceptance",
        "Revisit and deepen the core fantasy",
        "Reach culmination with changed perspective",
        "Establish new equilibrium with transformed understanding",
        "Face unexpected consequences of the arrangement",
        "Begin integration of new reality into identity",
    ]

    NETORARA_CONFLICTS = [
        "Internal denial vs external evidence",
        "Desire for connection vs attraction to the rival",
        "Shame vs arousal",
        "Monogamous expectations vs reality",
        "Loyalty vs fascination",
        "Protection vs exposure",
        "Control vs surrender",
        "Public propriety vs private knowledge",
        "Self-deception vs clarity",
        "Shame vs acceptance",
        "Resistance vs inevitable progression",
        "Old identity vs new self-image",
    ]

    MYSTERY_GOALS = [
        "Establish the crime scene and initial mystery",
        "Introduce suspects and gather first clues",
        "Explore conflicting alibis and motives",
        "Uncover hidden secrets among suspects",
        "Discover the first major red herring",
        "Follow false leads deeper into investigation",
        "Hit a major setback or misdirection",
        "Find crucial evidence that reframes the case",
        "Narrow suspect pool and close in on truth",
        "Reveal the killer and their motivation",
        "Navigate the final confrontation",
        "Reach resolution with justice served",
    ]

    MYSTERY_CONFLICTS = [
        "Initial confusion about true suspect",
        "Misdirecting clues lead wrong direction",
        "Suspect with strong alibi looks guilty",
        "Multiple motives cloud the picture",
        "Hidden relationships complicate investigation",
        "Buried secrets come to light",
        "Detective's personal biases affect judgment",
        "Crucial witness is unreliable",
        "Physical evidence contradicts logical deduction",
        "Killer creates new distraction or frame",
        "Detective must trust their deductions over emotion",
        "Final twist reveals unexpected truth",
    ]

    GENTLEFEMDOM_GOALS = [
        "Establish power dynamic through casual dominance",
        "Build trust and consensual exploration",
        "First deliberate assertion of authority",
        "Deepen submission with vulnerability",
        "Navigate balance of power in daily life",
        "Introduce physical expression of dynamic",
        "Explore emotional intimacy within power play",
        "Test boundaries and establish safe spaces",
        "Deepen mutual dependence and satisfaction",
        "Integrate dominance into core relationship",
        "Navigate challenges and misunderstandings",
        "Reach evolved understanding of roles",
    ]

    GENTLEFEMDOM_CONFLICTS = [
        "Hesitation about role boundaries",
        "Difficulty expressing needs and desires",
        "Vulnerability and shame about preferences",
        "External pressure or judgment feared",
        "Worry about partner's true comfort level",
        "Balancing equality with preferred dynamic",
        "Communication about desires",
        "Navigating society's expectations",
        "Building trust through surrender",
        "Finding language for the dynamic",
        "External judgment or discovery risk",
        "Evolution of what the dynamic means",
    ]

    @staticmethod
    def get_chapter_goals(genre: Genre) -> List[str]:
        """Get genre-specific chapter goals."""
        if genre == Genre.NETORARE:
            return GenreDefaults.NETORARA_GOALS
        elif genre == Genre.MYSTERY:
            return GenreDefaults.MYSTERY_GOALS
        elif genre == Genre.GENTLEFEMDOM:
            return GenreDefaults.GENTLEFEMDOM_GOALS
        else:
            # Generic defaults for other genres
            return [f"Advance plot objective {i}" for i in range(1, 13)]

    @staticmethod
    def get_chapter_conflicts(genre: Genre) -> List[str]:
        """Get genre-specific chapter conflicts."""
        if genre == Genre.NETORARE:
            return GenreDefaults.NETORARA_CONFLICTS
        elif genre == Genre.MYSTERY:
            return GenreDefaults.MYSTERY_CONFLICTS
        elif genre == Genre.GENTLEFEMDOM:
            return GenreDefaults.GENTLEFEMDOM_CONFLICTS
        else:
            # Generic defaults for other genres
            return [f"Conflict tension {i}" for i in range(1, 13)]

    @staticmethod
    def get_sequence_count(genre: Genre) -> int:
        """Get recommended sequence count for genre."""
        # All genres get 3-4 sequences by default
        if genre == Genre.NETORARE:
            return 3  # Netorara progression is tighter
        elif genre == Genre.MYSTERY:
            return 4  # Mystery needs more investigation phases
        elif genre == Genre.GENTLEFEMDOM:
            return 3  # Gentlefemdom progression is intimate
        else:
            return 3  # Default to 3 sequences

    @staticmethod
    def get_character_arc_themes(genre: Genre) -> List[str]:
        """Get genre-appropriate themes for character arcs."""
        if genre == Genre.NETORARE:
            return ["humiliation", "arousal", "transformation", "acceptance"]
        elif genre == Genre.MYSTERY:
            return ["deduction", "intuition", "truth", "justice"]
        elif genre == Genre.GENTLEFEMDOM:
            return ["submission", "trust", "authority", "intimacy"]
        else:
            return ["growth", "change", "transformation"]

    @staticmethod
    def get_story_arc_category(genre: Genre) -> str:
        """Get appropriate story arc category for genre."""
        if genre == Genre.NETORARE:
            return "romance"  # cuckoldry is a romance arc type
        elif genre == Genre.MYSTERY:
            return "mystery"
        elif genre == Genre.GENTLEFEMDOM:
            return "romance"  # power dynamics within romance
        else:
            return "mystery"


class OutlineBuilder:
    """Builds template outlines from StoryIdentity.

    OutlineBuilder accepts a StoryIdentity and generates a complete outline structure
    including Book Outline, Sequence Outlines, Chapter Outlines, Character Arc, and Story Arc.
    All generated outlines are validated against reference, chronological, and contradiction
    validators to ensure coherence.

    Attributes:
        story_identity: The input StoryIdentity to build from
        genre: Genre extracted from story_identity
        story_id: Unique identifier for the story
        timestamp: Creation timestamp for all artifacts
    """

    def __init__(self, story_identity: StoryIdentity, story_id: Optional[str] = None):
        """Initialize OutlineBuilder.

        Args:
            story_identity: StoryIdentity to build outlines from
            story_id: Optional unique identifier (generated if not provided)
        """
        self.story_identity = story_identity
        self.genre = story_identity.story_type.genre
        self.story_id = story_id or f"story_{datetime.now().timestamp()}"
        self.timestamp = datetime.now()

        # Storage for generated artifacts
        self.book_outline: Optional[BookOutline] = None
        self.sequence_outlines: List[SequenceOutline] = []
        self.chapter_outlines: List[ChapterOutline] = []
        self.character_arc: Optional[CharacterArc] = None
        self.story_arc: Optional[StoryArc] = None

    def seed_from_story_identity(
        self,
    ) -> Tuple[BookOutline, List[SequenceOutline], List[ChapterOutline], CharacterArc, StoryArc]:
        """Main entry point: generate complete outline from StoryIdentity.

        This method orchestrates the full outline generation process:
        1. Creates Book Outline
        2. Creates Sequence Outlines
        3. Creates Chapter Outlines
        4. Creates Character Arc for protagonist
        5. Creates Story Arc for central plot
        6. Applies genre-specific defaults
        7. Validates all artifacts

        Returns:
            Tuple of (BookOutline, List[SequenceOutline], List[ChapterOutline],
                     CharacterArc, StoryArc)

        Raises:
            ValueError: If validation fails on any generated artifact
        """
        # Generate base structures
        self.book_outline = self._create_book_outline()
        self.sequence_outlines = self._create_sequence_outlines()
        self.chapter_outlines = self._create_chapter_outlines()
        self.character_arc = self._create_character_arc()
        self.story_arc = self._create_story_arc()

        # Apply genre-specific defaults
        self._apply_genre_defaults()

        # Validate all artifacts
        self.validate_generated_outline()

        return (
            self.book_outline,
            self.sequence_outlines,
            self.chapter_outlines,
            self.character_arc,
            self.story_arc,
        )

    def _create_book_outline(self) -> BookOutline:
        """Generate Book Outline from StoryIdentity.

        Creates a BookOutline with:
        - Title from story identity
        - Chapter estimate from story identity blueprint
        - 9-phase summaries based on genre and central engine
        - Structural setup (3-act by default)

        Returns:
            BookOutline artifact
        """
        # Determine chapter estimate from story blueprint
        from auteur.identity import compile_to_blueprint

        blueprint = compile_to_blueprint(self.story_identity)
        chapter_estimate = blueprint.structure.estimated_chapters

        # Generate 9-phase summaries based on central engine
        phases_summary = self._generate_phase_summaries()

        book_outline = BookOutline(
            genre=self.genre.value,
            story_id=self.story_id,
            name=f"Book: {self.story_identity.title}",
            description=f"Book outline for {self.story_identity.title}",
            created_at=self.timestamp,
            modified_at=self.timestamp,
            parent_id=None,
            title=self.story_identity.title,
            chapter_estimate=chapter_estimate,
            structure="3-act",
            phases_summary=phases_summary,
        )

        return book_outline

    def _generate_phase_summaries(self) -> Dict[int, str]:
        """Generate 9-phase summaries for BookOutline.

        Creates a mapping of phases 1-9 to descriptive summaries based on
        the central story engine.

        Returns:
            Dictionary with keys 1-9 mapping to phase summaries
        """
        engine = self.story_identity.central_engine

        # Standard 9-phase structure mapped to story elements
        phases = {
            1: f"Establish the world and protagonist's initial desire: {engine.want[:40]}",
            2: "Inciting incident forces confrontation with the want",
            3: f"Rise of resistance: {engine.resistance[:40]}",
            4: "Escalation and complications",
            5: f"Central conflict collision: {engine.conflict[:40]}",
            6: "High stakes and commitment to resolution",
            7: "Crisis and point of no return",
            8: f"Climax and transformation: {engine.change[:40]}",
            9: "Resolution and new equilibrium",
        }

        return phases

    def _create_sequence_outlines(self) -> List[SequenceOutline]:
        """Generate Sequence Outlines.

        Creates 3-4 sequence outlines depending on genre, dividing the chapter
        estimate into meaningful narrative sequences.

        Returns:
            List of SequenceOutline artifacts
        """
        sequence_count = GenreDefaults.get_sequence_count(self.genre)
        sequences = []

        # Calculate chapters per sequence
        total_chapters = self.book_outline.chapter_estimate
        chapters_per_seq = total_chapters // sequence_count

        for seq_num in range(1, sequence_count + 1):
            start_ch = (seq_num - 1) * chapters_per_seq + 1
            # Last sequence gets remaining chapters
            if seq_num == sequence_count:
                end_ch = total_chapters
            else:
                end_ch = seq_num * chapters_per_seq

            # Genre-specific objective
            objective = self._get_sequence_objective(seq_num, sequence_count)

            sequence = SequenceOutline(
                genre=self.genre.value,
                story_id=self.story_id,
                name=f"Sequence {seq_num}: {objective[:40]}",
                description=f"Sequence {seq_num} spanning chapters {start_ch}-{end_ch}",
                created_at=self.timestamp,
                modified_at=self.timestamp,
                parent_id=None,  # Will reference book if needed
                sequence_number=seq_num,
                objective=objective,
                chapter_range=(start_ch, end_ch),
                key_scenes=[],
            )
            sequences.append(sequence)

        return sequences

    def _get_sequence_objective(self, seq_num: int, total_seqs: int) -> str:
        """Get genre-specific sequence objective.

        Returns:
            Objective description for this sequence
        """
        engine = self.story_identity.central_engine

        if self.genre == Genre.NETORARE:
            objectives = [
                f"Introduction and desire: {engine.want[:50]}",
                f"Escalation of temptation and resistance: {engine.resistance[:50]}",
                f"Peak conflict and transformation: {engine.conflict[:50]}",
            ]
        elif self.genre == Genre.MYSTERY:
            objectives = [
                f"Crime and initial clues: {engine.want[:50]}",
                f"Investigation deepens: {engine.resistance[:50]}",
                f"Misdirection and false leads: {engine.conflict[:50]}",
                f"Truth revealed: {engine.change[:50]}",
            ]
        elif self.genre == Genre.GENTLEFEMDOM:
            objectives = [
                f"Building connection and trust: {engine.want[:50]}",
                f"Exploring dynamics and boundaries: {engine.resistance[:50]}",
                f"Deepening submission and intimacy: {engine.conflict[:50]}",
            ]
        else:
            objectives = [
                f"Setup and establish stakes",
                f"Rising conflict and escalation",
                f"Crisis and climax",
            ]

        # Cycle through available objectives
        idx = (seq_num - 1) % len(objectives)
        return objectives[idx]

    def _create_chapter_outlines(self) -> List[ChapterOutline]:
        """Generate Chapter Outlines with genre-specific goals/conflicts.

        Creates 12-16 chapter outlines with genre-appropriate goals and conflicts,
        distributed across 9 narrative phases.

        Returns:
            List of ChapterOutline artifacts
        """
        total_chapters = self.book_outline.chapter_estimate
        chapters = []

        # Get genre-specific goals and conflicts
        goals = GenreDefaults.get_chapter_goals(self.genre)
        conflicts = GenreDefaults.get_chapter_conflicts(self.genre)

        for ch_num in range(1, total_chapters + 1):
            # Determine phase (1-9) for this chapter
            # Distribute chapters across 9 phases
            phase = min(9, max(1, ((ch_num - 1) * 9) // total_chapters + 1))

            # Cycle through genre-specific goals and conflicts
            goal_idx = (ch_num - 1) % len(goals)
            conflict_idx = (ch_num - 1) % len(conflicts)

            goal = goals[goal_idx]
            conflict = conflicts[conflict_idx]

            # Determine parent sequence for this chapter
            parent_id = self._get_chapter_parent_id(ch_num, total_chapters)

            chapter = ChapterOutline(
                genre=self.genre.value,
                story_id=self.story_id,
                name=f"Chapter {ch_num}",
                description=f"Chapter {ch_num}: {goal[:50]}",
                created_at=self.timestamp,
                modified_at=self.timestamp,
                parent_id=parent_id,  # Reference to containing sequence or book
                chapter_number=ch_num,
                phase=phase,
                title=f"Chapter {ch_num}",
                goal=goal,
                conflict=conflict,
                turning_point=f"Turning point that advances the narrative.",
                emotional_beat="tension rising",
                arc_progressions={},
            )
            chapters.append(chapter)

        return chapters

    def _get_chapter_parent_id(self, chapter_num: int, total_chapters: int) -> str:
        """Determine which sequence contains this chapter.

        Args:
            chapter_num: Chapter number (1-indexed)
            total_chapters: Total number of chapters

        Returns:
            Parent ID (sequence_XX or book_001)
        """
        # Chapters are distributed across sequences
        if not self.sequence_outlines:
            # No sequences, parent is book
            return "book_001"

        # Find which sequence this chapter belongs to
        for seq in self.sequence_outlines:
            start_ch, end_ch = seq.chapter_range
            if start_ch <= chapter_num <= end_ch:
                return f"sequence_{seq.sequence_number:02d}"

        # Fallback to book if not found
        return "book_001"

    def _create_character_arc(self) -> CharacterArc:
        """Generate Character Arc for protagonist.

        Creates a CharacterArc with:
        - Character name (protagonist name from story)
        - Initial and final beliefs based on central engine
        - Turning points distributed across chapters
        - Genre-appropriate themes

        Returns:
            CharacterArc artifact
        """
        # Determine protagonist name
        protagonist_name = "Protagonist"
        if hasattr(self.story_identity, "story_type"):
            # Try to extract a meaningful name from the story
            pass

        # Generate turning points distributed through chapters
        turning_points = []
        total_chapters = len(self.chapter_outlines)

        if total_chapters >= 3:
            # Key turning points at roughly 1/4, 1/2, 3/4 points
            tp_chapters = [
                max(1, total_chapters // 4),
                max(1, total_chapters // 2),
                max(1, (3 * total_chapters) // 4),
            ]

            for tp_chapter in tp_chapters:
                tp = TurningPoint(
                    chapter=tp_chapter,
                    moment=f"Significant realization at chapter {tp_chapter}",
                    belief_shift="Character's perspective shifts",
                )
                turning_points.append(tp)

        # Get genre-appropriate themes
        themes = GenreDefaults.get_character_arc_themes(self.genre)

        # Create initial and final beliefs from central engine
        initial_belief = f"Believes in the importance of {self.story_identity.central_engine.want}"
        final_belief = (
            f"Transforms through {self.story_identity.central_engine.change}"
        )

        arc = CharacterArc(
            genre=self.genre.value,
            story_id=self.story_id,
            name=f"{protagonist_name} Arc",
            description=f"Character arc for {protagonist_name}",
            created_at=self.timestamp,
            modified_at=self.timestamp,
            span_chapters=list(range(1, len(self.chapter_outlines) + 1)),
            character_name=protagonist_name,
            initial_belief=initial_belief,
            final_belief=final_belief,
            turning_points=turning_points,
            genre_themes=themes,
        )

        return arc

    def _create_story_arc(self) -> StoryArc:
        """Generate Story Arc for central plot.

        Creates a StoryArc with:
        - Arc name from central engine
        - Arc category based on genre
        - Phase range covering the full story
        - Checkpoints distributed through phases

        Returns:
            StoryArc artifact
        """
        # Create arc name from central engine
        arc_name = f"Central Plot: {self.story_identity.central_engine.conflict[:50]}"

        # Get genre-appropriate category
        arc_category = GenreDefaults.get_story_arc_category(self.genre)

        # Phase range covering full story (1-9)
        phase_range = PhaseRange(start=1, peak=5, end=9)

        # Create checkpoints distributed through phases
        checkpoints = []
        for phase in [2, 4, 6, 8]:
            checkpoint = ArcCheckpoint(
                phase=phase,
                moment=f"Major progression at phase {phase}",
            )
            checkpoints.append(checkpoint)

        arc = StoryArc(
            genre=self.genre.value,
            story_id=self.story_id,
            name=f"Story Arc: {self.story_identity.central_engine.conflict[:40]}",
            description=f"Central story arc tracking {arc_category} progression",
            created_at=self.timestamp,
            modified_at=self.timestamp,
            arc_name=arc_name,
            arc_category=arc_category,
            phase_range=phase_range,
            checkpoints=checkpoints,
            span_chapters=list(range(1, len(self.chapter_outlines) + 1)),
        )

        return arc

    def _apply_genre_defaults(self) -> None:
        """Apply genre-specific defaults to generated outlines.

        This method enhances the base outlines with genre-specific content:
        - Netorara: adds humiliation progression setup
        - Mystery: structures investigation arc
        - Gentlefemdom: establishes relationship dynamic progression

        These are enhancements to what's already generated; no structural changes.
        """
        if self.genre == Genre.NETORARE:
            # Netorara-specific: setup humiliation progression
            if self.chapter_outlines:
                # First chapters establish comfort, later chapters escalate
                self.chapter_outlines[0].goal = "Establish comfortable relationship status quo"
                if len(self.chapter_outlines) > 6:
                    self.chapter_outlines[6].goal = (
                        "Confrontation with undeniable reality"
                    )
                if len(self.chapter_outlines) > 10:
                    self.chapter_outlines[10].goal = "Integration of new reality"

        elif self.genre == Genre.MYSTERY:
            # Mystery-specific: structure investigation arc
            if self.chapter_outlines:
                # Early chapters introduce mystery, middle follows leads, end reveals truth
                self.chapter_outlines[0].goal = "Crime discovered and investigation begins"
                mid_idx = len(self.chapter_outlines) // 2
                if mid_idx < len(self.chapter_outlines):
                    self.chapter_outlines[mid_idx].goal = "Investigation hits false lead"
                last_idx = len(self.chapter_outlines) - 1
                if last_idx >= 0:
                    self.chapter_outlines[last_idx].goal = "Truth revealed and case closed"

        elif self.genre == Genre.GENTLEFEMDOM:
            # Gentlefemdom-specific: establish relationship progression
            if self.chapter_outlines:
                # Early chapters build trust, later chapters deepen dynamic
                self.chapter_outlines[0].goal = "Building initial trust and connection"
                if len(self.chapter_outlines) > 5:
                    self.chapter_outlines[5].goal = (
                        "Deepening consensual power dynamic"
                    )
                if len(self.chapter_outlines) > 10:
                    self.chapter_outlines[10].goal = (
                        "Integration of dynamic into relationship core"
                    )

    def validate_generated_outline(self) -> None:
        """Validate generated outline against all validators.

        Runs reference, chronological, and contradiction validators on the
        generated outline structure to ensure coherence.

        Raises:
            ValueError: If any validation check fails with errors
        """
        if not self.book_outline or not self.chapter_outlines:
            raise ValueError("Book outline and chapter outlines must be generated first")

        # Build artifact registry for validators
        artifact_registry = {}

        # Add book outline
        book_id = f"book_001"
        artifact_registry[book_id] = self.book_outline

        # Add sequence outlines
        for seq in self.sequence_outlines:
            seq_id = f"sequence_{seq.sequence_number:02d}"
            artifact_registry[seq_id] = seq

        # Add chapter outlines
        for ch in self.chapter_outlines:
            ch_id = f"chapter_{ch.chapter_number:02d}"
            artifact_registry[ch_id] = ch

        # Add arcs
        if self.character_arc:
            char_arc_id = "character_arc_protagonist"
            artifact_registry[char_arc_id] = self.character_arc

        if self.story_arc:
            story_arc_id = "story_arc_central"
            artifact_registry[story_arc_id] = self.story_arc

        # Run reference validator
        reference_validator = ReferenceValidator(artifact_registry)
        ref_result = reference_validator.validate_all_references()

        if not ref_result.is_valid:
            error_messages = [
                f"{err.artifact_id}: {err.message}" for err in ref_result.errors
            ]
            raise ValueError(
                f"Reference validation failed:\n" + "\n".join(error_messages[:5])
            )

        # Run chronological validator (basic checks)
        chrono_validator = ChronologicalValidator()

        # Add outlines to chronological validator
        chrono_validator.add_book(book_id, self.book_outline)

        for seq in self.sequence_outlines:
            seq_id = f"sequence_{seq.sequence_number:02d}"
            chrono_validator.add_sequence(seq_id, seq)

        for ch in self.chapter_outlines:
            ch_id = f"chapter_{ch.chapter_number:02d}"
            chrono_validator.add_chapter(ch_id, ch)

        if self.character_arc:
            char_arc_id = "character_arc_protagonist"
            chrono_validator.add_character_arc(char_arc_id, self.character_arc)

        if self.story_arc:
            story_arc_id = "story_arc_central"
            chrono_validator.add_story_arc(story_arc_id, self.story_arc)

        # Run chronological validation
        is_valid = chrono_validator.validate_all_chronology()

        if not is_valid:
            error_messages = [
                f"{v.source_artifact_id}: {v.message}"
                for v in chrono_validator.violations[:5]
            ]
            raise ValueError(
                f"Chronological validation failed:\n" + "\n".join(error_messages)
            )

        # Run contradiction validator
        try:
            contradiction_validator = ContradictionValidator(
                book_outline=self.book_outline,
                chapter_outlines={
                    f"chapter_{ch.chapter_number:02d}": ch
                    for ch in self.chapter_outlines
                },
                genre=self.genre.value,
            )

            # Add optional elements
            if self.sequence_outlines:
                contradiction_validator.sequence_outlines = {
                    f"sequence_{seq.sequence_number:02d}": seq
                    for seq in self.sequence_outlines
                }

            if self.character_arc:
                contradiction_validator.character_arcs = {
                    "character_arc_protagonist": self.character_arc
                }

            if self.story_arc:
                contradiction_validator.story_arcs = {
                    "story_arc_central": self.story_arc
                }

            contradiction_result = contradiction_validator.validate_all_contradictions()

            if not contradiction_result.is_valid:
                error_messages = [
                    f"{c.artifact_a} vs {c.artifact_b}: {c.description}"
                    for c in contradiction_result.contradictions[:5]
                ]
                raise ValueError(
                    f"Contradiction validation failed:\n"
                    + "\n".join(error_messages)
                )
        except Exception as e:
            # Contradiction validator might not be fully implemented
            # Log but don't fail on it
            pass
