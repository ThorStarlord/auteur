"""Sample StoryBlueprint: 'The Shattered Crown' (grimdark epic fantasy)."""

from __future__ import annotations

from auteur import (
    ActStructure,
    ArcType,
    AuthorAudienceContract,
    Character,
    CharacterState,
    EmotionalBlueprint,
    EndingTone,
    Genre,
    LengthClass,
    ProjectIdentity,
    StoryBlueprint,
    StructuralConstants,
    TargetAudience,
    TensionTarget,
    TensionWaveform,
    ThematicCore,
)
from auteur.blueprint import (
    ActTone,
    ArcMilestone,
    CharacterRole,
    ContentRating,
    POVType,
    Relationship,
)


def build_shattered_crown() -> StoryBlueprint:
    identity = ProjectIdentity(
        title="The Shattered Crown",
        author_intent="A grimdark epic about a hero who succeeds at his quest by becoming the thing he hunted.",
        length_class=LengthClass.EPIC_NOVEL,
        genre=Genre.GRIMDARK_FANTASY,
        subgenre="grimdark",
        target_audience=TargetAudience.ADULT,
        pov_type=POVType.THIRD_LIMITED_MULTIPLE,
    )

    structure = StructuralConstants(
        estimated_chapters=45,
        act_structure=ActStructure.THREE_ACT,
    )

    contract = AuthorAudienceContract(
        content_rating=ContentRating.R,
        explicit_violence="allowed",
        explicit_sex="fade_to_black",
        profanity="moderate",
        on_page_torture=False,
        child_harm=False,
        mandatory_ending_tone=EndingTone.BITTERSWEET,
        expected_elements=[
            "mentor_death",
            "major_betrayal",
            "at_least_3_battles",
            "protagonist_low_point_at_75_percent",
            "thematic_reverberation_in_all_subplots",
        ],
        forbidden_tropes=[
            "chosen_one_prophecy",
            "resurrected_hero",
            "deus_ex_machina_rescue",
        ],
        custom_rules=[
            "No character can wield magic without paying a visible physical cost.",
            "No fully hopeful resolution; bittersweet only.",
        ],
    )

    emotional_design = EmotionalBlueprint(
        overall_emotional_arc="descent into dread, then a defiant spike of hard-won meaning",
        per_act_tones=[
            ActTone(act_index=1, label="Setup", tone="mystery and intrigue, subtle unease"),
            ActTone(act_index=2, label="Confrontation", tone="rising dread with moments of camaraderie"),
            ActTone(act_index=3, label="Resolution", tone="despair sharpening into catharsis"),
        ],
    )

    kael = Character(
        name="Kael",
        role=CharacterRole.PROTAGONIST,
        arc_type=ArcType.CORRUPTION,
        arc_start_percentage=0,
        arc_end_percentage=100,
        current_arc_percentage=39,
        key_milestones=[
            ArcMilestone(at_percentage=25, description="First minor deception without guilt."),
            ArcMilestone(at_percentage=50, description="Justifies a cruel act to himself."),
            ArcMilestone(at_percentage=75, description="Betrays Lira to gain the cursed ring's power."),
            ArcMilestone(at_percentage=100, description="Embraces the dark power as his own."),
        ],
        current_state=CharacterState(
            location="taverntown",
            physical="broken_arm",
            emotional="vengeful",
            inventory=["cursed_ring", "fathers_dagger"],
            relationships=[
                Relationship(other="Lira", kind="trust", intensity=0.8),
                Relationship(other="Malachai", kind="fear", intensity=0.4),
            ],
            secrets_known=["the ring whispers in his sleep"],
        ),
    )

    lira = Character(
        name="Lira",
        role=CharacterRole.DEUTERAGONIST,
        arc_type=ArcType.HEALING,
        arc_start_percentage=10,
        arc_end_percentage=90,
        current_arc_percentage=42,
        key_milestones=[
            ArcMilestone(at_percentage=30, description="Names her trauma aloud for the first time."),
            ArcMilestone(at_percentage=60, description="Refuses to take vengeance when offered it."),
            ArcMilestone(at_percentage=90, description="Forgives the surviving cousin who betrayed her family."),
        ],
        current_state=CharacterState(
            location="taverntown",
            physical="exhausted",
            emotional="quietly hopeful",
            inventory=["mothers_pendant"],
            relationships=[Relationship(other="Kael", kind="trust", intensity=0.7)],
        ),
    )

    waveform = TensionWaveform(
        target_curve=[
            TensionTarget(chapter_index=1, score=4, label="cold_open_unease"),
            TensionTarget(chapter_index=11, score=7, label="first_act_break"),
            TensionTarget(chapter_index=22, score=9, label="midpoint_battle"),
            TensionTarget(chapter_index=23, score=3, label="recovery_valley"),
            TensionTarget(chapter_index=27, score=3, label="quiet_bonding"),
            TensionTarget(chapter_index=33, score=8, label="all_is_lost_ramp"),
            TensionTarget(chapter_index=42, score=10, label="climax"),
            TensionTarget(chapter_index=45, score=5, label="bittersweet_coda"),
        ],
        realized_scores=[4, 5, 5, 6, 6, 7, 6, 6, 7, 7, 7, 6, 6, 7, 7, 8, 8, 7, 8, 8, 9, 9, 3, 4, 5, 4],
    )

    theme = ThematicCore(
        central_question="What does redemption cost when the cost is paid by someone else?",
        thesis="Some debts cannot be honored without becoming the thing you hunted.",
        motifs=["broken crowns", "wounded hands", "rings that whisper"],
    )

    return StoryBlueprint(
        identity=identity,
        structure=structure,
        contract=contract,
        emotional_design=emotional_design,
        characters=[kael, lira],
        tension_waveform=waveform,
        theme=theme,
    )
