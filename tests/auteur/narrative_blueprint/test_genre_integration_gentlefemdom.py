"""Integration test for gentle femdom genre with complete outline workflow.

This test validates that the gentle femdom genre works seamlessly with the complete
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


def test_gentlefemdom_full_outline_workflow():
    """Test complete gentle femdom story workflow with all outline layers.

    Validates:
    - BookOutline creation with proper 9-phase structure
    - ChapterOutlines across multiple phases (2, 4, 7, 9)
    - CharacterArc with gentle femdom themes (authority, surrender, dominance, trust)
    - StoryArc spanning romantic authority discovery phases
    - All validations pass using same infrastructure as other genres
    """
    now = datetime.now()
    story_id = "gf_romance_001"
    genre = "gentlefemdom"

    # Layer 1: BookOutline - "Sarah & Alice"
    phases_summary = {
        1: "Setup - Two women meet",
        2: "Inciting Incident - Attraction grows",
        3: "Rising Action 1 - First emotional vulnerability",
        4: "Rising Action 2 - Power dynamics become apparent",
        5: "Midpoint - Alice discovers her desire for authority",
        6: "Rising Action 3 - Sarah responds with surrender",
        7: "Climax Setup - Intimacy deepens",
        8: "Climax - Mutual exploration and acceptance",
        9: "Resolution - Committed relationship established",
    }

    book = BookOutline(
        genre=genre,
        story_id=story_id,
        name="Sarah & Alice",
        description="A tender romance exploring authority and surrender",
        created_at=now,
        modified_at=now,
        parent_id=None,
        title="Sarah & Alice",
        chapter_estimate=10,
        structure="3-act",
        phases_summary=phases_summary,
    )

    # Layer 2: ChapterOutlines spanning phases 2-9
    chapter_specs = [
        {
            "number": 2,
            "phase": 2,
            "title": "First Coffee",
            "goal": "Establish chemistry between Alice and Sarah",
            "conflict": "Mutual attraction complicated by uncertainty",
            "turning": "Sarah suggests a second meeting",
            "beat": "Hopeful excitement mixed with vulnerability",
        },
        {
            "number": 4,
            "phase": 4,
            "title": "The Question",
            "goal": "Power dynamics surface",
            "conflict": "Alice wants to lead but doubts herself",
            "turning": "Sarah asks if Alice wants to take charge",
            "beat": "Alice realizes her desire for authority",
        },
        {
            "number": 7,
            "phase": 7,
            "title": "Tender Authority",
            "goal": "Explore authority in intimate context",
            "conflict": "Fear of hurting or misunderstanding each other",
            "turning": "First intimate moment with role exchange",
            "beat": "Joy in expressing and receiving authority",
        },
        {
            "number": 9,
            "phase": 9,
            "title": "Forever",
            "goal": "Establish permanent commitment",
            "conflict": "Integration of authority into daily life",
            "turning": "Alice and Sarah plan a shared future",
            "beat": "Peace and belonging",
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

    # Layer 3: CharacterArc - Alice's authority discovery
    # Initial belief: "I must be submissive to be loved"
    # Final belief: "My authority excites and comforts my partner"
    alice_arc = CharacterArc(
        genre=genre,
        story_id=story_id,
        name="Alice's Authority Discovery Arc",
        description="Alice's journey from self-doubt to confident authority",
        created_at=now,
        modified_at=now,
        span_chapters=[2, 4, 7, 9],
        character_name="Alice",
        initial_belief="I must be submissive to be loved",
        final_belief="My authority excites and comforts my partner",
        turning_points=[
            TurningPoint(
                chapter=2,
                moment="Sarah's interest in her",
                belief_shift="Someone could genuinely want me",
            ),
            TurningPoint(
                chapter=4,
                moment="Sarah asks if Alice wants to lead",
                belief_shift="Maybe I don't have to be submissive",
            ),
            TurningPoint(
                chapter=7,
                moment="First intimate moment taking charge",
                belief_shift="Authority can be loving and sexy",
            ),
            TurningPoint(
                chapter=9,
                moment="Sarah fully accepts Alice's authority",
                belief_shift="My authority excites and comforts my partner",
            ),
        ],
        genre_themes=["authority", "surrender", "dominance", "trust"],
    )

    # Layer 4: StoryArc - Alice's Romance Arc
    alice_romance_arc = StoryArc(
        genre=genre,
        story_id=story_id,
        name="Alice's Romance Arc",
        description="The romance and intimacy arc centered on Alice and Sarah",
        created_at=now,
        modified_at=now,
        arc_name="Alice's Romance Arc",
        arc_category="romance",
        phase_range=PhaseRange(start=2, peak=8, end=9),
        span_chapters=[2, 4, 7, 9],
        checkpoints=[
            ArcCheckpoint(phase=2, moment="Alice and Sarah meet and feel attraction"),
            ArcCheckpoint(
                phase=4, moment="Power dynamics become clear, Alice's desire emerges"
            ),
            ArcCheckpoint(
                phase=7, moment="First intimate expression of authority and surrender"
            ),
            ArcCheckpoint(
                phase=8, moment="Climactic moment of mutual vulnerability and acceptance"
            ),
            ArcCheckpoint(phase=9, moment="Committed relationship with integrated authority"),
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
    is_valid, errors = arc_validator.validate_arc_themes(alice_arc, genre)
    assert is_valid is True, f"Character arc theme validation failed: {errors}"
    assert errors == [], f"Expected no errors for character arc, got: {errors}"

    # Validate: ArcValidator for StoryArc phases
    is_valid, errors = arc_validator.validate_story_arc_phases(
        alice_romance_arc, num_chapters=len(chapters)
    )
    assert is_valid is True, f"Story arc phase validation failed: {errors}"
    assert errors == [], f"Expected no errors for story arc, got: {errors}"

    # Verify artifact properties
    assert book.genre == genre
    assert book.artifact_type() == "book_outline"
    assert len(chapters) == 4
    assert all(ch.artifact_type() == "chapter_outline" for ch in chapters)
    assert alice_arc.artifact_type() == "character_arc"
    assert alice_romance_arc.artifact_type() == "story_arc"

    # Verify narrative consistency across layers
    assert alice_arc.character_name == "Alice"
    assert alice_arc.initial_belief == "I must be submissive to be loved"
    assert (
        alice_arc.final_belief == "My authority excites and comforts my partner"
    )
    assert len(alice_arc.turning_points) == 4
    assert len(alice_romance_arc.checkpoints) == 5
    assert alice_romance_arc.arc_category == "romance"
    assert alice_romance_arc.phase_range.start == 2
    assert alice_romance_arc.phase_range.peak == 8
    assert alice_romance_arc.phase_range.end == 9
