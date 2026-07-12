"""Integration test for mystery genre with complete outline workflow.

This test validates that the mystery genre works seamlessly with the complete
narrative hierarchy: BookOutline, ChapterOutlines, CharacterArc, and StoryArc.

The test proves that all three genres (netorare, mystery, gentlefemdom) use
identical infrastructure with zero special-casing.
"""

from datetime import datetime
from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint
from auteur.narrative_blueprint.schema.story_arc import StoryArc, ArcCheckpoint
from auteur.narrative_blueprint.schema.outline_types import PhaseRange
from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator
from auteur.narrative_blueprint.validator.arc_validator import ArcValidator


def test_mystery_full_outline_workflow():
    """Test complete mystery story workflow with all outline layers.

    Validates:
    - BookOutline creation with proper 9-phase structure
    - ChapterOutlines across multiple phases (1, 3, 6, 9)
    - CharacterArc with mystery-appropriate themes (investigation, deception, revelation)
    - StoryArc spanning key investigation phases
    - All validations pass using same infrastructure as other genres
    """
    now = datetime.now()
    story_id = "mystery_001"
    genre = "mystery"

    # Layer 1: BookOutline - "The Curious Cottage"
    phases_summary = {
        1: "Setup - Detective arrives at cottage",
        2: "Inciting Incident - Victim discovered missing",
        3: "Investigation Opens - Suspects identified",
        4: "Rising Action 1 - Clues emerge",
        5: "Midpoint - False suspect arrested",
        6: "Rising Action 2 - Real conspiracy revealed",
        7: "Climax Setup - Trap for real culprits",
        8: "Climax - Confrontation with masterminds",
        9: "Resolution - Truth exposed",
    }

    book = BookOutline(
        genre=genre,
        story_id=story_id,
        name="The Curious Cottage",
        description="A cozy mystery where nothing is as it seems",
        created_at=now,
        modified_at=now,
        parent_id=None,
        title="The Curious Cottage",
        chapter_estimate=12,
        structure="3-act",
        phases_summary=phases_summary,
    )

    # Layer 2: ChapterOutlines spanning phases 1-9
    chapter_specs = [
        {
            "number": 1,
            "phase": 1,
            "title": "Arrival at the Cottage",
            "goal": "Establish setting and introduce detective",
            "conflict": "Eerie atmosphere suggests danger",
            "turning": "Discovery of missing person",
            "beat": "Curiosity mixed with unease",
        },
        {
            "number": 3,
            "phase": 3,
            "title": "The Servants Speak",
            "goal": "Question household staff",
            "conflict": "Conflicting testimonies",
            "turning": "Butler claims innocence too firmly",
            "beat": "Growing doubt about initial suspect",
        },
        {
            "number": 6,
            "phase": 6,
            "title": "The Conspiracy Unfolds",
            "goal": "Discover the real plot",
            "conflict": "Multiple parties involved",
            "turning": "Victim orchestrated disappearance",
            "beat": "Shock at betrayal and deception",
        },
        {
            "number": 9,
            "phase": 9,
            "title": "Justice Served",
            "goal": "Resolution and revelation",
            "conflict": "Confronting multiple conspirators",
            "turning": "All truth finally exposed",
            "beat": "Satisfaction in uncovering truth",
        },
    ]

    chapters = []
    for spec in chapter_specs:
        chapter = ChapterOutline(
            genre=genre,
            story_id=story_id,
            name=f"Chapter {spec['number']}",
            description=f"Phase {spec['phase']} chapter",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=spec["number"],
            phase=spec["phase"],
            title=spec["title"],
            goal=spec["goal"],
            conflict=spec["conflict"],
            turning_point=spec["turning"],
            emotional_beat=spec["beat"],
        )
        chapters.append(chapter)

    # Layer 3: CharacterArc - Detective's investigation arc
    # Initial belief: "The butler did it"
    # Final belief: "The victim orchestrated the disappearance"
    detective_arc = CharacterArc(
        genre=genre,
        story_id=story_id,
        name="Detective's Investigation Arc",
        description="Detective's journey from assumption to truth",
        created_at=now,
        modified_at=now,
        span_chapters=[1, 3, 6, 9],
        character_name="Detective Sarah",
        initial_belief="The butler did it",
        final_belief="The victim orchestrated the disappearance",
        turning_points=[
            TurningPoint(
                chapter=1,
                moment="First impression of the cottage",
                belief_shift="Something is wrong here",
            ),
            TurningPoint(
                chapter=3,
                moment="Butler's testimony reveals inconsistencies",
                belief_shift="Maybe someone else is responsible",
            ),
            TurningPoint(
                chapter=6,
                moment="Servant admits victim had secret meetings",
                belief_shift="The victim might be complicit",
            ),
            TurningPoint(
                chapter=9,
                moment="Confrontation with conspirators",
                belief_shift="Victim orchestrated everything",
            ),
        ],
        genre_themes=["investigation", "deception", "revelation", "conspiracy"],
    )

    # Layer 4: StoryArc - The Investigation
    investigation_arc = StoryArc(
        genre=genre,
        story_id=story_id,
        name="Main Investigation Arc",
        description="The central mystery plot spanning the investigation",
        created_at=now,
        modified_at=now,
        arc_name="The Investigation",
        arc_category="mystery",
        phase_range=PhaseRange(start=1, peak=6, end=9),
        span_chapters=[1, 3, 6, 9],
        checkpoints=[
            ArcCheckpoint(
                phase=1, moment="Detective arrives and discovers missing person"
            ),
            ArcCheckpoint(
                phase=3, moment="Initial suspects questioned, butler primary suspect"
            ),
            ArcCheckpoint(
                phase=6, moment="Real conspiracy revealed with victim's involvement"
            ),
            ArcCheckpoint(phase=9, moment="All conspirators confronted and truth exposed"),
        ],
    )

    # Validate: ContainerValidator for BookOutline + ChapterOutlines
    container_validator = ContainerValidator()
    all_outlines = [book] + chapters
    is_valid, errors = container_validator.validate_consistency(all_outlines)

    assert is_valid is True, f"Container validation failed: {errors}"
    assert errors == [], f"Expected no errors, got: {errors}"

    # Validate: ArcValidator for CharacterArc
    arc_validator = ArcValidator()
    is_valid, errors = arc_validator.validate_arc_themes(detective_arc, genre)
    assert is_valid is True, f"Character arc theme validation failed: {errors}"
    assert errors == [], f"Expected no errors for character arc, got: {errors}"

    # Validate: ArcValidator for StoryArc phases
    is_valid, errors = arc_validator.validate_story_arc_phases(
        investigation_arc, num_chapters=len(chapters)
    )
    assert is_valid is True, f"Story arc phase validation failed: {errors}"
    assert errors == [], f"Expected no errors for story arc, got: {errors}"

    # Verify artifact properties
    assert book.genre == genre
    assert book.artifact_type() == "book_outline"
    assert len(chapters) == 4
    assert all(ch.artifact_type() == "chapter_outline" for ch in chapters)
    assert detective_arc.artifact_type() == "character_arc"
    assert investigation_arc.artifact_type() == "story_arc"

    # Verify narrative consistency across layers
    assert detective_arc.character_name == "Detective Sarah"
    assert detective_arc.initial_belief == "The butler did it"
    assert detective_arc.final_belief == "The victim orchestrated the disappearance"
    assert len(detective_arc.turning_points) == 4
    assert len(investigation_arc.checkpoints) == 4
    assert investigation_arc.arc_category == "mystery"
    assert investigation_arc.phase_range.start == 1
    assert investigation_arc.phase_range.peak == 6
    assert investigation_arc.phase_range.end == 9
