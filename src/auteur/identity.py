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
    StoryThread,
    ThreadType,
    SupportFunction,
)


class StoryType(BaseModel):
    medium: StoryMedium = StoryMedium.NOVEL
    mode: StoryMode = StoryMode.TRAGIC
    genre: Genre = Genre.GRIMDARK_FANTASY
    subgenres: list[str] = Field(default_factory=list)
    target_audience: TargetAudience = TargetAudience.ADULT
    length_class: LengthClass | None = None


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

    def validate_identity(self) -> list[StructureDiagnostic]:
        """Perform deterministic, LLM-free structural validations on this StoryIdentity."""
        from auteur.structure.diagnostics import (
            DiagnosticLayer,
            DiagnosticSeverity,
            RepairOptions,
            StructureDiagnostic,
        )
        diagnostics: list[StructureDiagnostic] = []

        # 1. Want-Change Coherence
        def _normalize(text: str) -> str:
            return " ".join(text.casefold().split())

        if _normalize(self.central_engine.want) == _normalize(self.central_engine.change):
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    layer=DiagnosticLayer.STRUCTURAL_FORCES,
                    rule="identity.central_engine.change_duplicates_want",
                    message="The high-level engine change repeats the want instead of describing transformation.",
                    evidence=[
                        f"want = {self.central_engine.want}",
                        f"change = {self.central_engine.change}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            "Update the change field to describe how the protagonist or world is transformed after the conflict.",
                        ],
                        challenge_intent=[],
                    ),
                )
            )

        # 2. Genre Ending Tone/Mode Mismatch
        if self.genre_contract_snapshot:
            ending_tone_str = "tragic" if self.story_type.mode == StoryMode.TRAGIC else "bittersweet"
            
            is_mismatch = False
            forbidden_type = ""
            if ending_tone_str == "tragic" and "tragic ending" in self.genre_contract_snapshot.forbidden_mismatches:
                is_mismatch = True
                forbidden_type = "tragic ending"
            
            if is_mismatch:
                if "ending_tone" not in self.author_overrides:
                    diagnostics.append(
                        StructureDiagnostic(
                            severity=DiagnosticSeverity.ERROR,
                            layer=DiagnosticLayer.CONSTRAINTS,
                            rule="identity.genre.forbidden_mismatch.ending_tone",
                            message=f"Story mode implies ending tone '{ending_tone_str}' which is forbidden by the '{self.genre_contract_snapshot.display_name}' contract.",
                            evidence=[
                                f"mode = {self.story_type.mode.value}",
                                f"forbidden_mismatch = {forbidden_type}",
                            ],
                            repair_options=RepairOptions(
                                preserve_intent=["Change mode to comic, adventure, or bittersweet/other."],
                                challenge_intent=[
                                    "Add 'ending_tone' to author_overrides to bypass this constraint.",
                                    "Select a different genre that supports tragic endings."
                                ],
                            ),
                        )
                    )
                else:
                    diagnostics.append(
                        StructureDiagnostic(
                            severity=DiagnosticSeverity.WARNING,
                            layer=DiagnosticLayer.CONSTRAINTS,
                            rule="identity.genre.forbidden_mismatch.ending_tone.override",
                            message=f"Story mode implies ending tone '{ending_tone_str}' which is forbidden by the '{self.genre_contract_snapshot.display_name}' contract. Overridden by author.",
                            evidence=[
                                f"mode = {self.story_type.mode.value}",
                                f"forbidden_mismatch = {forbidden_type}",
                                "author_overrides = ending_tone"
                            ],
                            repair_options=RepairOptions(
                                preserve_intent=[],
                                challenge_intent=[]
                            )
                        )
                    )

        # 3. Target Experience Avoidance Clash
        avoided = {a.casefold().strip() for a in self.target_experience.avoid}
        primary = self.target_experience.primary.casefold().strip()
        
        if primary in avoided:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    layer=DiagnosticLayer.TARGET_EXPERIENCE,
                    rule="identity.target_experience.avoid_clashes_with_primary",
                    message=f"Avoided experience list clashes with primary emotional promise '{self.target_experience.primary}'.",
                    evidence=[
                        f"primary = {self.target_experience.primary}",
                        f"avoid = {self.target_experience.avoid}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            "Remove the primary experience from the avoided experience list.",
                            "Change the primary experience to something that is not avoided."
                        ],
                        challenge_intent=[]
                    )
                )
            )
        
        progression_steps = [
            s.casefold().strip()
            for s in self.target_experience.progression.split("->")
            if s.strip()
        ]
        for step in progression_steps:
            if step in avoided:
                diagnostics.append(
                    StructureDiagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        layer=DiagnosticLayer.TARGET_EXPERIENCE,
                        rule="identity.target_experience.avoid_clashes_with_progression",
                        message=f"Avoided experience list clashes with progression step '{step}'.",
                        evidence=[
                            f"progression = {self.target_experience.progression}",
                            f"avoid = {self.target_experience.avoid}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                "Remove the progression step from the avoided experience list.",
                                "Change the progression trajectory."
                            ],
                            challenge_intent=[]
                        )
                    )
                )

        return diagnostics


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


def resolve_length_class(medium: StoryMedium) -> LengthClass:
    """Resolve StoryMedium to LengthClass."""
    if medium == StoryMedium.SHORT_STORY:
        return LengthClass.SHORT_STORY
    elif medium == StoryMedium.NOVELLA:
        return LengthClass.NOVELLA
    elif medium == StoryMedium.SERIES:
        return LengthClass.SERIES
    elif medium == StoryMedium.FILM:
        return LengthClass.NOVEL
    else:
        return LengthClass.NOVEL


def _get_recommended_subplots(genre: Genre) -> list[StoryThread]:
    """Get standard recommended subplots for a given genre."""
    if genre == Genre.MYSTERY:
        return [
            StoryThread(
                name="Investigation & Suspect Pool",
                type=ThreadType.MYSTERY,
                want=StructuralClaim(
                    author_text="Eliminate innocent suspects and expose the true culprit.",
                    checkable_claims=[],
                ),
                resistance=StructuralClaim(
                    author_text="The culprit plants red herrings and misdirects key clues.",
                    checkable_claims=[],
                ),
                conflict=StructuralClaim(
                    author_text="Misinterpreting a fabricated clue vs trusting the logical deduction chain.",
                    checkable_claims=[],
                ),
                stakes=StructuralClaim(
                    author_text="An innocent person is accused while the killer remains free.",
                    checkable_claims=[],
                ),
                change=StructuralClaim(
                    author_text="The detective pieces together the final contradiction to locate the true killer.",
                    checkable_claims=[],
                ),
                supports_main_by=[SupportFunction.COMPLICATES],
                thematic_function="Challenges the detective's logic and proves that truth is costly.",
            ),
            StoryThread(
                name="Foil/Partner Friction",
                type=ThreadType.RELATIONSHIP_ARC,
                want=StructuralClaim(
                    author_text="Gain cooperation and support from a partner, witness, or local authority.",
                    checkable_claims=[],
                ),
                resistance=StructuralClaim(
                    author_text="Different operational values and personal history breed deep skepticism.",
                    checkable_claims=[],
                ),
                conflict=StructuralClaim(
                    author_text="Competing theories of the case strain collaboration during a high-stakes lead.",
                    checkable_claims=[],
                ),
                stakes=StructuralClaim(
                    author_text="The partnership dissolves, leaving the detective isolated and exposed.",
                    checkable_claims=[],
                ),
                change=StructuralClaim(
                    author_text="Mutual vulnerability allows a breakthrough, turning distrust into shared trust.",
                    checkable_claims=[],
                ),
                supports_main_by=[SupportFunction.PRESSURES_CHANGE],
                thematic_function="Forces the detective to articulate internal fears and adjust their moral lens.",
            ),
            StoryThread(
                name="The False Lead",
                type=ThreadType.MYSTERY,
                want=StructuralClaim(
                    author_text="Expose the secrets of a highly suspicious suspect.",
                    checkable_claims=[],
                ),
                resistance=StructuralClaim(
                    author_text="The suspect protects a deeply embarrassing but non-criminal secret.",
                    checkable_claims=[],
                ),
                conflict=StructuralClaim(
                    author_text="Wasting precious investigative runway chasing a secret that is not the murder.",
                    checkable_claims=[],
                ),
                stakes=StructuralClaim(
                    author_text="The real culprit escapes because the investigation is distracted.",
                    checkable_claims=[],
                ),
                change=StructuralClaim(
                    author_text="The false lead is cleared, revealing a crucial piece of positive clue logic.",
                    checkable_claims=[],
                ),
                supports_main_by=[SupportFunction.COMPLICATES],
                thematic_function="Echoes the main thesis by showing how fear drives defensive lies.",
            ),
        ]
    elif genre == Genre.ROMANCE:
        return [
            StoryThread(
                name="Rivalry & Foil Obstacles",
                type=ThreadType.RELATIONSHIP_ARC,
                want=StructuralClaim(
                    author_text="Bridge the operational distance and establish an initial emotional bond.",
                    checkable_claims=[],
                ),
                resistance=StructuralClaim(
                    author_text="Opposite social roles, external obligations, or past wounds create a wall.",
                    checkable_claims=[],
                ),
                conflict=StructuralClaim(
                    author_text="Public professional friction colliding with private growing intimacy.",
                    checkable_claims=[],
                ),
                stakes=StructuralClaim(
                    author_text="A permanent estrangement that leaves both parties emotionally compromised.",
                    checkable_claims=[],
                ),
                change=StructuralClaim(
                    author_text="Sacrificing a safe professional boundary to embrace mutual trust and commitment.",
                    checkable_claims=[],
                ),
                supports_main_by=[SupportFunction.PRESSURES_CHANGE],
                thematic_function="Highlights the difference between transactional safety and authentic vulnerability.",
            ),
            StoryThread(
                name="Self-Worth & Career Pressure",
                type=ThreadType.THEMATIC_ECHO,
                want=StructuralClaim(
                    author_text="Achieve external validation and secure professional independence.",
                    checkable_claims=[],
                ),
                resistance=StructuralClaim(
                    author_text="Systemic demands require compromising personal authenticity and relationships.",
                    checkable_claims=[],
                ),
                conflict=StructuralClaim(
                    author_text="Devoting time to career survival vs investing in relationship growth.",
                    checkable_claims=[],
                ),
                stakes=StructuralClaim(
                    author_text="Securing the career but ending up lonely, or losing the job and the lover.",
                    checkable_claims=[],
                ),
                change=StructuralClaim(
                    author_text="Redefining success based on connection rather than raw external praise.",
                    checkable_claims=[],
                ),
                supports_main_by=[SupportFunction.COMPLICATES],
                thematic_function="Echoes the central thesis by demonstrating the limits of professional shield walls.",
            ),
        ]
    elif genre == Genre.GRIMDARK_FANTASY:
        return [
            StoryThread(
                name="Corruption Echo",
                type=ThreadType.THEMATIC_ECHO,
                want=StructuralClaim(
                    author_text="Protect an innocent ally from the war's psychological rot.",
                    checkable_claims=[],
                ),
                resistance=StructuralClaim(
                    author_text="The ally's desire for vengeance matches the protagonist's starting dark drive.",
                    checkable_claims=[],
                ),
                conflict=StructuralClaim(
                    author_text="Using dark power to keep them safe vs letting them see the cost of the corruption.",
                    checkable_claims=[],
                ),
                stakes=StructuralClaim(
                    author_text="Watching the ally turn into the same monstrous thing the protagonist is becoming.",
                    checkable_claims=[],
                ),
                change=StructuralClaim(
                    author_text="The ally succumbs fully, providing a tragic mirror of the protagonist's destination.",
                    checkable_claims=[],
                ),
                supports_main_by=[SupportFunction.PRESSURES_CHANGE],
                thematic_function="Proves the bleakgrim core truth that corruption spreads to everyone it touches.",
            ),
            StoryThread(
                name="Factional Betrayal",
                type=ThreadType.THEMATIC_ECHO,
                want=StructuralClaim(
                    author_text="Secure a military alliance with a crucial secondary faction.",
                    checkable_claims=[],
                ),
                resistance=StructuralClaim(
                    author_text="The faction's leadership is split between survival and corrupt opportunism.",
                    checkable_claims=[],
                ),
                conflict=StructuralClaim(
                    author_text="Compromising ethical boundaries to buy loyalty vs maintaining honor and getting crushed.",
                    checkable_claims=[],
                ),
                stakes=StructuralClaim(
                    author_text="The alliance betrays the protagonist at the final gate, escalating the tragedy.",
                    checkable_claims=[],
                ),
                change=StructuralClaim(
                    author_text="Accepting the betrayal as the inevitable outcome of a broken world.",
                    checkable_claims=[],
                ),
                supports_main_by=[SupportFunction.COMPLICATES],
                thematic_function="Undercuts standard heroic assumptions of military loyalty.",
            ),
        ]
    else:
        return [
            StoryThread(
                name="Secondary Struggle",
                type=ThreadType.THEMATIC_ECHO,
                want=StructuralClaim(author_text="Establish a secondary goal.", checkable_claims=[]),
                resistance=StructuralClaim(author_text="Opposition from a secondary force.", checkable_claims=[]),
                conflict=StructuralClaim(author_text="Friction between secondary and main goals.", checkable_claims=[]),
                stakes=StructuralClaim(author_text="Secondary loss compounding main stakes.", checkable_claims=[]),
                change=StructuralClaim(author_text="A secondary transformation or cost paid.", checkable_claims=[]),
                supports_main_by=[SupportFunction.COMPLICATES],
                thematic_function="Echoes the main thematic argument.",
            ),
            StoryThread(
                name="Relationship Echo",
                type=ThreadType.RELATIONSHIP_ARC,
                want=StructuralClaim(author_text="Build connection with a support character.", checkable_claims=[]),
                resistance=StructuralClaim(author_text="Misunderstanding or divergent goals.", checkable_claims=[]),
                conflict=StructuralClaim(author_text="Competing values during a crucial choice.", checkable_claims=[]),
                stakes=StructuralClaim(author_text="Emotional isolation or betrayal.", checkable_claims=[]),
                change=StructuralClaim(author_text="A compromise that allows deeper connection.", checkable_claims=[]),
                supports_main_by=[SupportFunction.PRESSURES_CHANGE],
                thematic_function="Forces protagonist to reconsider their approach.",
            ),
        ]


def compile_to_blueprint(identity: StoryIdentity) -> StoryBlueprint:
    """Compile a StoryIdentity into a valid minimal StoryBlueprint skeleton."""
    # 1. Project Identity
    subgenres = identity.story_type.subgenres
    subgenre = subgenres[0] if subgenres else None

    # Resolve length class
    length_class = identity.story_type.length_class
    if length_class is None:
        length_class = resolve_length_class(identity.story_type.medium)

    project_identity = ProjectIdentity(
        title=identity.title,
        author_intent=identity.core_answer,
        target_experience=identity.target_experience,
        length_class=length_class,
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
    from auteur.blueprint import _LENGTH_DEFAULTS
    chapters, words, max_pov, max_total = _LENGTH_DEFAULTS[length_class]
    subplot_budgets = {
        LengthClass.SHORT_STORY: 0,
        LengthClass.NOVELLA: 1,
        LengthClass.NOVEL: 3,
        LengthClass.EPIC_NOVEL: 4,
        LengthClass.SERIES: 6,
    }
    subplot_budget = subplot_budgets.get(length_class, 3)

    constants = StructuralConstants(
        estimated_chapters=chapters,
        estimated_word_count=words,
        act_structure=ActStructure.THREE_ACT,
        max_pov_characters=max_pov,
        max_characters_total=max_total,
        subplot_budget=subplot_budget,
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
    progression_steps = []
    if identity.target_experience.progression:
        progression_steps = [
            s.strip() for s in identity.target_experience.progression.split("->") if s.strip()
        ]

    if not progression_steps:
        primary = identity.target_experience.primary or "emotion"
        progression_steps = [f"establishing {primary}", f"deepening {primary}", f"resolving {primary}"]

    act_1_emotion = progression_steps[0]
    if len(progression_steps) >= 3:
        act_2_emotion = progression_steps[1]
        act_3_emotion = progression_steps[-1]
    elif len(progression_steps) == 2:
        act_2_emotion = f"{progression_steps[0]} and {progression_steps[1]}"
        act_3_emotion = progression_steps[1]
    else:
        act_2_emotion = act_1_emotion
        act_3_emotion = act_1_emotion

    emotional_design = EmotionalBlueprint(
        overall_emotional_arc=f"A {identity.story_type.mode.value} arc focusing on {identity.target_experience.primary}.",
        per_act_tones=[
            ActTone(
                act_index=1,
                label="Setup",
                tone=f"{act_1_emotion.capitalize()}: Establishing the initial situation and the core desire: {identity.central_engine.want[:60]}.",
            ),
            ActTone(
                act_index=2,
                label="Confrontation",
                tone=f"{act_2_emotion.capitalize()}: Rising conflict driven by the core resistance: {identity.central_engine.resistance[:60]}.",
            ),
            ActTone(
                act_index=3,
                label="Resolution",
                tone=f"{act_3_emotion.capitalize()}: The final confrontation, high stakes, and the ultimate transformation: {identity.central_engine.change[:60]}.",
            ),
        ],
    )

    # 5. Theme
    genre_motifs = {
        Genre.MYSTERY: ["clues", "secrets", "shadows"],
        Genre.ROMANCE: ["intimacy", "vulnerability", "distance"],
        Genre.GRIMDARK_FANTASY: ["shadows", "contracts", "sacrifices"],
        Genre.HORROR: ["dread", "decay", "isolation"],
        Genre.THRILLER: ["clocks", "chases", "betrayals"],
        Genre.NETORARE: ["exclusion", "secrets", "compulsion"],
        Genre.NETORI: ["assertion", "rivalry", "domination"],
    }
    motifs = genre_motifs.get(identity.story_type.genre, ["shadows", "contracts", "sacrifices"])

    theme_question = (
        identity.open_questions[0]
        if identity.open_questions
        else f"What is the true cost of pursuing {identity.central_engine.want[:30]}?"
    )
    theme = ThematicCore(
        central_question=theme_question,
        thesis=f"The pursuit of {identity.central_engine.want[:30]} leads to {identity.central_engine.conflict[:30]}, resulting in {identity.central_engine.change[:30]}.",
        motifs=motifs,
    )

    # 6. Story Engine
    # Load subplots based on budget
    recommended = _get_recommended_subplots(identity.story_type.genre)
    seeded_threads = []
    for i in range(subplot_budget):
        if i < len(recommended):
            seeded_threads.append(recommended[i])
        else:
            seeded_threads.append(
                StoryThread(
                    name=f"Secondary Subplot {i+1}",
                    type=ThreadType.THEMATIC_ECHO,
                    want=StructuralClaim(author_text="Secondary want.", checkable_claims=[]),
                    resistance=StructuralClaim(author_text="Secondary resistance.", checkable_claims=[]),
                    conflict=StructuralClaim(author_text="Secondary conflict.", checkable_claims=[]),
                    stakes=StructuralClaim(author_text="Secondary stakes.", checkable_claims=[]),
                    change=StructuralClaim(author_text="Secondary change.", checkable_claims=[]),
                    supports_main_by=[SupportFunction.COMPLICATES],
                    thematic_function="Supports the main thread.",
                )
            )

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
        threads=seeded_threads,
    )

    # 7. Characters
    if identity.story_type.mode == StoryMode.TRAGIC:
        protagonist_arc = ArcType.CORRUPTION
    elif identity.story_type.genre == Genre.MYSTERY:
        protagonist_arc = ArcType.FLAT
    else:
        protagonist_arc = ArcType.GROWTH

    if identity.story_type.genre == Genre.MYSTERY:
        prot_name = "Detective"
        ant_name = "Culprit"
    elif identity.story_type.genre == Genre.ROMANCE:
        prot_name = "Lover A"
        ant_name = "Lover B"
    else:
        prot_name = "Protagonist"
        ant_name = "Antagonist"

    characters = [
        Character(
            name=prot_name,
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
            name=ant_name,
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
    tension_targets = []
    if constants.estimated_chapters <= 1:
        tension_targets = [
            TensionTarget(chapter_index=1, score=9, label="opening_climax")
        ]
    else:
        opening_idx = 1
        midpoint_idx = max(2, round(constants.estimated_chapters * 0.5))
        climax_idx = max(3, round(constants.estimated_chapters * 0.9))
        coda_idx = constants.estimated_chapters

        if midpoint_idx <= opening_idx:
            midpoint_idx = opening_idx + 1
        if climax_idx <= midpoint_idx:
            climax_idx = midpoint_idx + 1
        if coda_idx <= climax_idx:
            coda_idx = climax_idx + 1

        if coda_idx > constants.estimated_chapters:
            constants.estimated_chapters = coda_idx

        tension_targets = [
            TensionTarget(chapter_index=opening_idx, score=3, label="opening"),
            TensionTarget(chapter_index=midpoint_idx, score=7, label="midpoint"),
            TensionTarget(chapter_index=climax_idx, score=9, label="climax"),
            TensionTarget(chapter_index=coda_idx, score=5, label="coda"),
        ]

    tension_waveform = TensionWaveform(
        target_curve=tension_targets,
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
