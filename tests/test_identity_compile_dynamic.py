from auteur.identity import StoryIdentity, StoryType, HighLevelCentralEngine, compile_to_blueprint
from auteur.blueprint import (
    Genre,
    StoryMedium,
    StoryMode,
    TargetAudience,
    TargetExperience,
    LengthClass,
    ArcType,
)

def test_compile_short_story_mystery():
    identity = StoryIdentity(
        title="The Whispering Clue",
        core_answer="A brilliant detective solves a murder only to find their spouse was the prime instigator.",
        target_experience=TargetExperience(
            primary="curiosity",
            progression="curiosity -> unease -> shock",
            avoid=[],
        ),
        story_type=StoryType(
            medium=StoryMedium.SHORT_STORY,
            mode=StoryMode.PROCEDURAL,
            genre=Genre.MYSTERY,
            subgenres=["cozy_mystery"],
            target_audience=TargetAudience.ADULT,
        ),
        central_engine=HighLevelCentralEngine(
            want="Find the killer of the estate's owner.",
            resistance="A lack of physical evidence and highly secretive suspects.",
            conflict="Protecting a close friend from suspicion vs following the logical clues.",
            stakes="The killer strikes again if not exposed.",
            change="The detective accepts a bitter truth to prevent more harm.",
        ),
    )

    blueprint = compile_to_blueprint(identity)

    # 1. Scope and Length constraints
    assert blueprint.identity.length_class == LengthClass.SHORT_STORY
    assert blueprint.structure.estimated_chapters == 1
    assert blueprint.structure.subplot_budget == 0

    # 2. Emotional Design
    assert len(blueprint.emotional_design.per_act_tones) == 3
    assert "Curiosity:" in blueprint.emotional_design.per_act_tones[0].tone
    assert "Unease:" in blueprint.emotional_design.per_act_tones[1].tone
    assert "Shock:" in blueprint.emotional_design.per_act_tones[2].tone

    # 3. Theme Motifs & Thesis
    assert "clues" in blueprint.theme.motifs
    assert "secrets" in blueprint.theme.motifs
    assert "The pursuit of" in blueprint.theme.thesis

    # 4. Engine & Subplots (0 budget)
    assert len(blueprint.story_engine.threads) == 0

    # 5. Genre-aligned Characters
    assert blueprint.characters[0].name == "Detective"
    assert blueprint.characters[0].arc_type == ArcType.FLAT  # Mystery gets flat arc
    assert blueprint.characters[1].name == "Culprit"

    # 6. Tension targets (1 chapter scale)
    assert len(blueprint.tension_waveform.target_curve) == 1
    assert blueprint.tension_waveform.target_curve[0].chapter_index == 1
    assert blueprint.tension_waveform.target_curve[0].label == "opening_climax"


def test_compile_novel_romance():
    identity = StoryIdentity(
        title="Friction in the Stars",
        core_answer="Two rival planetary explorers must collaborate to survive a desert storm, discovering mutual devotion.",
        target_experience=TargetExperience(
            primary="attraction",
            progression="attraction -> friction -> devotion",
            avoid=[],
        ),
        story_type=StoryType(
            medium=StoryMedium.NOVEL,
            mode=StoryMode.INTIMATE,
            genre=Genre.ROMANCE,
            subgenres=["sci_fi_romance"],
            target_audience=TargetAudience.ADULT,
        ),
        central_engine=HighLevelCentralEngine(
            want="Establish planetary contact and win the survey prize.",
            resistance="Harsh weather and a competing explorer.",
            conflict="Sharing survival resources vs securing personal career win.",
            stakes="Survival on a barren rock and long-term isolation.",
            change="Both explorers choose mutual commitment over raw competition.",
        ),
    )

    blueprint = compile_to_blueprint(identity)

    # 1. Scope constraints
    assert blueprint.identity.length_class == LengthClass.NOVEL
    assert blueprint.structure.estimated_chapters == 25
    assert blueprint.structure.subplot_budget == 3

    # 2. Emotional design
    assert len(blueprint.emotional_design.per_act_tones) == 3
    assert "Attraction:" in blueprint.emotional_design.per_act_tones[0].tone
    assert "Friction:" in blueprint.emotional_design.per_act_tones[1].tone
    assert "Devotion:" in blueprint.emotional_design.per_act_tones[2].tone

    # 3. Subplots (Budget = 3)
    assert len(blueprint.story_engine.threads) == 3
    assert blueprint.story_engine.threads[0].name == "Rivalry & Foil Obstacles"
    assert blueprint.story_engine.threads[1].name == "Self-Worth & Career Pressure"
    assert blueprint.story_engine.threads[2].name.startswith("Secondary Subplot")

    # 4. Genre-aligned Characters
    assert blueprint.characters[0].name == "Lover A"
    assert blueprint.characters[0].arc_type == ArcType.GROWTH
    assert blueprint.characters[1].name == "Lover B"

    # 5. Tension targets
    assert len(blueprint.tension_waveform.target_curve) == 4
    assert blueprint.tension_waveform.target_curve[0].chapter_index == 1
    assert blueprint.tension_waveform.target_curve[1].chapter_index == 12  # max(2, round(25 * 0.5))
    assert blueprint.tension_waveform.target_curve[2].chapter_index == 22  # max(3, round(25 * 0.9))
    assert blueprint.tension_waveform.target_curve[3].chapter_index == 25


def test_compile_explicit_length_override():
    identity = StoryIdentity(
        title="Short Epic",
        core_answer="A standard quest but scaled as a standalone novel.",
        target_experience=TargetExperience(
            primary="wonder",
            progression="wonder -> danger -> triumph",
            avoid=[],
        ),
        story_type=StoryType(
            medium=StoryMedium.SHORT_STORY,
            mode=StoryMode.ADVENTURE,
            genre=Genre.EPIC_FANTASY,
            subgenres=[],
            target_audience=TargetAudience.ADULT,
            length_class=LengthClass.NOVEL,  # Explicit override
        ),
        central_engine=HighLevelCentralEngine(
            want="Find the artifact.",
            resistance="The guardian dragon.",
            conflict="Bypassing the guardian vs risking the party's lives.",
            stakes="The kingdom's eternal curse.",
            change="The seeker gains the crown and takes the dragon's watch.",
        ),
    )

    blueprint = compile_to_blueprint(identity)

    # Verifies the override took precedence over the medium default
    assert blueprint.identity.length_class == LengthClass.NOVEL
    assert blueprint.structure.estimated_chapters == 25
    assert blueprint.structure.subplot_budget == 3
