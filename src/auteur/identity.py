"""Layered StoryIdentity model and blueprint seeder.

StoryIdentity is the creative brief that precedes the full blueprint. It captures
high-level decisions (the core answer, experience goals, central story engine,
boundaries, and open questions) before generating a valid blueprint structure.
"""

from __future__ import annotations
from enum import Enum
from pathlib import Path
from typing import Self, TYPE_CHECKING
import yaml
from pydantic import BaseModel, Field, model_validator

if TYPE_CHECKING:
    from auteur.genres.models import GenreContract

from auteur.blueprint import (
    Genre,
    StoryMode,
    StoryMedium,
    TargetAudience,
    TargetExperience,
    StoryBlueprint,
    ProjectIdentity,
    LengthClass,
    POVType,
    StructuralConstants,
    ActStructure,
    AuthorAudienceContract,
    ContentRating,
    EndingTone,
    EmotionalBlueprint,
    ActTone,
    ThematicCore,
    StoryEngine,
    MainThread,
    StructuralClaim,
    Character,
    CharacterRole,
    ArcType,
    ArcMilestone,
    CharacterState,
    TensionWaveform,
    TensionTarget,
)


class StoryType(BaseModel):
    medium: StoryMedium = StoryMedium.NOVEL
    mode: StoryMode = StoryMode.TRAGIC
    genre: Genre = Genre.GRIMDARK_FANTASY
    subgenres: list[str] = Field(default_factory=list)
    target_audience: TargetAudience = TargetAudience.ADULT


class HighLevelCentralEngine(BaseModel):
    want: str = Field(min_length=1)
    resistance: str = Field(min_length=1)
    conflict: str = Field(min_length=1)
    stakes: str = Field(min_length=1)
    change: str = Field(min_length=1)


class RecommendationMode(str, Enum):
    OPINIONATED = "opinionated"
    OPEN_ENDED = "open_ended"


class BestBasis(str, Enum):
    GENRE_ALIGNED = "genre_aligned"
    STRUCTURALLY_COHERENT = "structurally_coherent"
    EMOTIONALLY_POWERFUL = "emotionally_powerful"
    FAITHFUL_TO_INPUT = "faithful_to_input"


class StoryIdentity(BaseModel):
    title: str = Field(min_length=1)
    core_answer: str = Field(min_length=1)
    target_experience: TargetExperience = Field(
        default_factory=lambda: TargetExperience(primary="dread", progression="rising", avoid=[])
    )
    story_type: StoryType = Field(default_factory=StoryType)
    central_engine: HighLevelCentralEngine
    not_this: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    alternatives: list[str] = Field(default_factory=list)
    recommendation_mode: RecommendationMode = RecommendationMode.OPINIONATED
    best_basis: BestBasis = BestBasis.GENRE_ALIGNED
    why_this_is_best: str | None = Field(default=None, min_length=1)
    rejected_directions: list[str] = Field(default_factory=list)
    author_overrides: list[str] = Field(default_factory=list)
    genre_contract_snapshot: GenreContract | None = None

    @model_validator(mode="after")
    def _hydrate_genre_contract(self) -> Self:
        if self.genre_contract_snapshot is None:
            from auteur.genres.registry import load_genre_contract
            self.genre_contract_snapshot = load_genre_contract(self.story_type.genre)
        return self

    @classmethod
    def from_yaml(cls, path: str | Path) -> Self:
        """Load a StoryIdentity from a YAML file."""
        text = Path(path).read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        return cls.model_validate(data)

    def to_yaml(self, path: str | Path) -> None:
        """Save this StoryIdentity as a YAML file."""
        Path(path).write_text(
            yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )


def compile_to_blueprint(identity: StoryIdentity) -> StoryBlueprint:
    """Compile a StoryIdentity into a valid minimal StoryBlueprint skeleton."""
    # 1. Project Identity
    subgenres = identity.story_type.subgenres
    subgenre = subgenres[0] if subgenres else None

    project_identity = ProjectIdentity(
        title=identity.title,
        author_intent=identity.core_answer,
        target_experience=identity.target_experience,
        length_class=LengthClass.NOVEL,
        genre=identity.story_type.genre,
        subgenre=subgenre,
        subgenres=subgenres,
        mode=identity.story_type.mode,
        medium=identity.story_type.medium,
        target_audience=identity.story_type.target_audience,
        pov_type=POVType.THIRD_LIMITED_SINGLE,
        genre_contract_snapshot=identity.genre_contract_snapshot,
    )

    # 2. Structural Constants
    constants = StructuralConstants(
        estimated_chapters=25,
        estimated_word_count=90000,
        act_structure=ActStructure.THREE_ACT,
        max_pov_characters=3,
        max_characters_total=25,
        subplot_budget=3,
    )

    # 3. Contract
    content_rating = (
        ContentRating.R
        if identity.story_type.target_audience == TargetAudience.ADULT
        else ContentRating.PG_13
    )
    ending_tone = (
        EndingTone.TRAGIC
        if identity.story_type.mode == StoryMode.TRAGIC
        else EndingTone.BITTERSWEET
    )
    explicit_sex = (
        "fade_to_black"
        if identity.story_type.target_audience == TargetAudience.ADULT
        else "forbidden"
    )

    contract = AuthorAudienceContract(
        content_rating=content_rating,
        explicit_violence="implied_only",
        explicit_sex=explicit_sex,
        profanity="moderate",
        on_page_torture=False,
        child_harm=False,
        mandatory_ending_tone=ending_tone,
        expected_elements=[],
        forbidden_tropes=[],
        custom_rules=[],
    )

    # 4. Emotional Blueprint
    emotional_design = EmotionalBlueprint(
        overall_emotional_arc=f"A {identity.story_type.mode.value} arc focusing on {identity.target_experience.primary}.",
        per_act_tones=[
            ActTone(
                act_index=1,
                label="Setup",
                tone=f"Establishing the initial situation and the core desire: {identity.central_engine.want[:60]}.",
            ),
            ActTone(
                act_index=2,
                label="Confrontation",
                tone=f"Rising conflict driven by the core resistance: {identity.central_engine.resistance[:60]}.",
            ),
            ActTone(
                act_index=3,
                label="Resolution",
                tone=f"The final confrontation, high stakes, and the ultimate transformation: {identity.central_engine.change[:60]}.",
            ),
        ],
    )

    # 5. Theme
    theme_question = (
        identity.open_questions[0]
        if identity.open_questions
        else f"What is the true cost of pursuing {identity.central_engine.want[:30]}?"
    )
    theme = ThematicCore(
        central_question=theme_question,
        thesis=f"Ambition leads to conflict: {identity.central_engine.conflict[:60]}.",
        motifs=["shadows", "contracts", "sacrifices"],
    )

    # 6. Story Engine (Main Thread only initially)
    engine = StoryEngine(
        main_thread=MainThread(
            want=StructuralClaim(author_text=identity.central_engine.want, checkable_claims=[]),
            resistance=StructuralClaim(
                author_text=identity.central_engine.resistance, checkable_claims=[]
            ),
            conflict=StructuralClaim(
                author_text=identity.central_engine.conflict, checkable_claims=[]
            ),
            stakes=StructuralClaim(
                author_text=identity.central_engine.stakes, checkable_claims=[]
            ),
            change=StructuralClaim(
                author_text=identity.central_engine.change, checkable_claims=[]
            ),
            thematic_function=f"Explores the central question: {theme_question}",
        ),
        threads=[],
    )

    # 7. Characters (Seed Protagonist & Antagonist)
    protagonist_arc = (
        ArcType.CORRUPTION
        if identity.story_type.mode == StoryMode.TRAGIC
        else ArcType.GROWTH
    )
    characters = [
        Character(
            name="Protagonist",
            role=CharacterRole.PROTAGONIST,
            arc_type=protagonist_arc,
            arc_start_percentage=0,
            arc_end_percentage=100,
            current_arc_percentage=0,
            key_milestones=[
                ArcMilestone(at_percentage=25, description="Commitment to search."),
                ArcMilestone(at_percentage=50, description="The point of no return."),
                ArcMilestone(at_percentage=75, description="The lowest ebb."),
                ArcMilestone(at_percentage=100, description="The final choice."),
            ],
            current_state=CharacterState(
                location="start_location", physical="healthy", emotional="determined"
            ),
        ),
        Character(
            name="Antagonist",
            role=CharacterRole.ANTAGONIST,
            arc_type=ArcType.FLAT,
            arc_start_percentage=0,
            arc_end_percentage=0,
            current_arc_percentage=0,
            key_milestones=[],
            current_state=CharacterState(
                location="start_location", physical="intact", emotional="unyielding"
            ),
        ),
    ]

    # 8. Tension Waveform
    tension_waveform = TensionWaveform(
        target_curve=[
            TensionTarget(chapter_index=1, score=3, label="opening"),
            TensionTarget(chapter_index=12, score=7, label="midpoint"),
            TensionTarget(chapter_index=22, score=9, label="climax"),
            TensionTarget(chapter_index=25, score=5, label="coda"),
        ],
        realized_scores=[],
    )

    # 9. Assemble and Validate the Root StoryBlueprint
    blueprint = StoryBlueprint(
        identity=project_identity,
        structure=constants,
        story_engine=engine,
        contract=contract,
        emotional_design=emotional_design,
        characters=characters,
        tension_waveform=tension_waveform,
        theme=theme,
    )

    return blueprint


from auteur.genres.models import GenreContract
StoryIdentity.model_rebuild()
