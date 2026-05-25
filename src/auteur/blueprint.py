"""Layered StoryBlueprint and PlanningCall slicer.

The blueprint is a tree: high-level choices (length, genre, audience) cascade
into structural defaults, contract rules, emotional design, characters, and
the tension waveform. The PlanningCall is a narrow, scope-aware projection
of the blueprint that gets fed to the Cartographer agent.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal, Self, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    from auteur.genres.models import GenreContract


# ---------------------------------------------------------------------------
# Enums (Layer 1 vocabulary that cascades downward)
# ---------------------------------------------------------------------------


class LengthClass(str, Enum):
    SHORT_STORY = "short_story"
    NOVELLA = "novella"
    NOVEL = "novel"
    EPIC_NOVEL = "epic_novel"
    SERIES = "series"


class NarrativeRunway(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    VERY_LONG = "very_long"


class ScopeComplexity(str, Enum):
    MICRO = "micro"
    FOCUSED = "focused"
    STANDARD = "standard"
    EXPANDED = "expanded"
    SERIES = "series"


class MechanicalLoad(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SettingFootprint(str, Enum):
    SINGLE_LOCATION = "single_location"
    LOCAL = "local"
    REGIONAL = "regional"
    WIDE = "wide"
    MULTI_WORLD = "multi_world"


class StoryTimeframe(str, Enum):
    IMMEDIATE = "immediate"
    COMPRESSED = "compressed"
    EXTENDED = "extended"
    GENERATIONAL = "generational"


class TropeLoad(str, Enum):
    MINIMAL = "minimal"
    SELECTIVE = "selective"
    FULL = "full"


class ConsequenceScale(str, Enum):
    PERSONAL = "personal"
    RELATIONAL = "relational"
    COMMUNAL = "communal"
    CITY = "city"
    NATIONAL = "national"
    CIVILIZATIONAL = "civilizational"
    COSMIC = "cosmic"


class Genre(str, Enum):
    EPIC_FANTASY = "epic_fantasy"
    GRIMDARK_FANTASY = "grimdark_fantasy"
    URBAN_FANTASY = "urban_fantasy"
    SCI_FI = "sci_fi"
    SPACE_OPERA = "space_opera"
    LITERARY = "literary"
    MYSTERY = "mystery"
    COZY_MYSTERY = "cozy_mystery"
    HORROR = "horror"
    THRILLER = "thriller"
    ROMANCE = "romance"
    YA_FANTASY = "ya_fantasy"
    NETORARE = "netorare"
    NETORI = "netori"
    OTHER = "other"


class StoryMode(str, Enum):
    TRAGIC = "tragic"
    COMIC = "comic"
    SATIRICAL = "satirical"
    MYTHIC = "mythic"
    PROCEDURAL = "procedural"
    ADVENTURE = "adventure"
    NOIR = "noir"
    INTIMATE = "intimate"
    EPIC = "epic"
    ABSURDIST = "absurdist"
    OTHER = "other"


class StoryMedium(str, Enum):
    NOVEL = "novel"
    SHORT_STORY = "short_story"
    NOVELLA = "novella"
    SERIES = "series"
    FILM = "film"
    TV = "tv"
    VISUAL_NOVEL = "visual_novel"
    GAME = "game"
    INTERACTIVE_FICTION = "interactive_fiction"
    OTHER = "other"


class MediumFormat(str, Enum):
    STANDALONE_BOOK = "standalone_book"
    SHORT_FORM = "short_form"
    NOVELLA = "novella"
    BOOK_SERIES = "book_series"
    WEBNOVEL = "webnovel"
    FEATURE_FILM = "feature_film"
    EPISODIC_TV = "episodic_tv"
    ROUTE_BASED = "route_based"
    ACTION_GAME = "action_game"
    BRANCHING_TEXT = "branching_text"
    OTHER = "other"


class ReleaseModel(str, Enum):
    COMPLETE_RELEASE = "complete_release"
    EPISODIC_SERIAL = "episodic_serial"
    SEASONAL_DROPS = "seasonal_drops"
    COMPLETE_OR_LIVE_SERVICE = "complete_or_live_service"
    OTHER = "other"


class InteractionModel(str, Enum):
    PASSIVE_READER = "passive_reader"
    SERIAL_READER = "serial_reader"
    PASSIVE_VIEWER = "passive_viewer"
    CHOICE_BASED_READER = "choice_based_reader"
    PLAYER_AGENCY = "player_agency"
    OTHER = "other"


class UnitOfDelivery(str, Enum):
    CHAPTER = "chapter"
    STORY = "story"
    BOOK = "book"
    EPISODE = "episode"
    SCENE = "scene"
    SCENE_NODE = "scene_node"
    MISSION = "mission"
    LEVEL = "level"
    CHOICE_NODE = "choice_node"
    OTHER = "other"


class TargetAudience(str, Enum):
    MIDDLE_GRADE = "middle_grade"
    YOUNG_ADULT = "young_adult"
    NEW_ADULT = "new_adult"
    ADULT = "adult"


class POVType(str, Enum):
    FIRST_PERSON = "first_person"
    THIRD_LIMITED_SINGLE = "third_person_limited_single"
    THIRD_LIMITED_MULTIPLE = "third_person_limited_multiple"
    THIRD_OMNISCIENT = "third_person_omniscient"


class ActStructure(str, Enum):
    THREE_ACT = "three_act"
    FIVE_ACT = "five_act"
    SEVEN_POINT = "seven_point"
    HEROS_JOURNEY = "heros_journey"
    KISHOTENKETSU = "kishotenketsu"


class ContentRating(str, Enum):
    G = "G"
    PG = "PG"
    PG_13 = "PG-13"
    R = "R"
    NC_17 = "NC-17"


class EndingTone(str, Enum):
    HOPEFUL = "hopeful"
    BITTERSWEET = "bittersweet"
    TRAGIC = "tragic"
    OPEN = "open"
    AMBIGUOUS = "ambiguous"


class ArcType(str, Enum):
    GROWTH = "growth"
    CORRUPTION = "corruption"
    REDEMPTION = "redemption"
    HEALING = "healing"
    FALL = "fall"
    FLAT = "flat"
    DISILLUSIONMENT = "disillusionment"


class CharacterRole(str, Enum):
    PROTAGONIST = "protagonist"
    DEUTERAGONIST = "deuteragonist"
    ANTAGONIST = "antagonist"
    MENTOR = "mentor"
    ALLY = "ally"
    FOIL = "foil"
    SUPPORTING = "supporting"


class ThreadType(str, Enum):
    MAIN_PLOT = "main_plot"
    CHARACTER_ARC = "character_arc"
    RELATIONSHIP_ARC = "relationship_arc"
    MYSTERY = "mystery"
    POLITICAL = "political"
    SURVIVAL = "survival"
    THEMATIC_ECHO = "thematic_echo"


class SupportFunction(str, Enum):
    COMPLICATES = "complicates"
    MIRRORS = "mirrors"
    CONTRASTS = "contrasts"
    ESCALATES = "escalates"
    REVEALS = "reveals"
    PRESSURES_CHANGE = "pressures_change"
    PAYS_OFF = "pays_off"


class OverrideType(str, Enum):
    SAFE_VARIATION = "safe_variation"
    COMPRESSION = "compression"
    SUBVERSION = "subversion"
    RECLASSIFICATION = "reclassification"



# ---------------------------------------------------------------------------
# Layer 1 — Project Identity
# ---------------------------------------------------------------------------


class EmotionalTrajectory(BaseModel):
    pattern: str = Field(min_length=1)
    start: str = Field(min_length=1)
    midpoint: str = Field(min_length=1)
    ending: str = Field(min_length=1)


class GenreEmotionRole(BaseModel):
    genre: str = Field(min_length=1)
    emotion: str = Field(min_length=1)
    role: str = Field(min_length=1)


class POVExperienceContract(BaseModel):
    dominant_feeling: str = Field(min_length=1)
    function: str = Field(min_length=1)


class TargetExperience(BaseModel):
    # Simplified / legacy fields
    primary: str = Field(default="")
    progression: str = Field(default="")
    secondary: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)

    # Rich model fields
    primary_emotional_promise: str | None = None
    secondary_palette: list[str] = Field(default_factory=list)
    avoided_experiences: list[str] = Field(default_factory=list)
    emotional_trajectory: EmotionalTrajectory | None = None
    genre_emotion_stack: dict[str, GenreEmotionRole] | None = None
    pov_experience_contracts: dict[str, POVExperienceContract] | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_and_backfill(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data

        # Map rich keys to simplified keys if simplified are not provided, and vice versa
        if "primary_emotional_promise" in data and data["primary_emotional_promise"]:
            data.setdefault("primary", data["primary_emotional_promise"])
        elif "primary" in data and data["primary"]:
            data.setdefault("primary_emotional_promise", data["primary"])

        if "avoided_experiences" in data and data["avoided_experiences"]:
            data.setdefault("avoid", data["avoided_experiences"])
        elif "avoid" in data and data["avoid"]:
            data.setdefault("avoided_experiences", data["avoid"])

        if "secondary_palette" in data and data["secondary_palette"]:
            data.setdefault("secondary", data["secondary_palette"])
        elif "secondary" in data and data["secondary"]:
            data.setdefault("secondary_palette", data["secondary"])

        # Extract progression from emotional_trajectory.pattern if progression is not set
        et = data.get("emotional_trajectory")
        if isinstance(et, dict) and "pattern" in et:
            data.setdefault("progression", et["pattern"])

        return data

    @model_validator(mode="after")
    def _validate_non_empty(self) -> Self:
        # Check that we have a primary emotional promise
        if not self.primary and not self.primary_emotional_promise:
            raise ValueError("Either 'primary' or 'primary_emotional_promise' must be specified.")
        
        # Populate defaults and cross-populate
        if not self.primary:
            self.primary = self.primary_emotional_promise
        if not self.primary_emotional_promise:
            self.primary_emotional_promise = self.primary

        if not self.progression and self.emotional_trajectory:
            self.progression = self.emotional_trajectory.pattern
        if not self.progression:
            self.progression = "static"

        # Sync avoided lists
        if self.avoid and not self.avoided_experiences:
            self.avoided_experiences = self.avoid
        elif self.avoided_experiences and not self.avoid:
            self.avoid = self.avoided_experiences

        # Sync secondary lists
        if self.secondary and not self.secondary_palette:
            self.secondary_palette = self.secondary
        elif self.secondary_palette and not self.secondary:
            self.secondary = self.secondary_palette

        return self


class MediumContract(BaseModel):
    medium: StoryMedium
    format: MediumFormat
    release_model: ReleaseModel
    interaction_model: InteractionModel
    unit_of_delivery: UnitOfDelivery
    representation_units: list[str] = Field(default_factory=list)
    modulation_biases: list[str] = Field(default_factory=list)
    medium_failure_modes: list[str] = Field(default_factory=list)





class GenreOverride(BaseModel):
    load_bearing_expectation: str = Field(..., description="The key expectation or trope being bypassed")
    user_override: str = Field(..., description="Description of the alternative mechanism")
    override_type: OverrideType = Field(..., description="Classification of the consequence")
    rationale: str | None = Field(None, description="Optional explanation from the author")


class ProjectIdentity(BaseModel):
    title: str
    author_intent: str = Field(
        description="Free-text description of what the author wants this project to be."
    )
    target_experience: TargetExperience | None = None
    length_class: LengthClass
    genre: Genre
    subgenre: str | None = None
    subgenres: list[str] = Field(default_factory=list)
    mode: StoryMode | None = None
    medium: StoryMedium | None = None
    medium_contract: MediumContract | None = None
    target_audience: TargetAudience
    pov_type: POVType
    genre_contract_snapshot: GenreContract | None = None
    genre_overrides: dict[str, GenreOverride] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _populate_medium_contract_from_shortcut(self) -> Self:
        if self.medium_contract is None and self.medium is not None:
            from auteur.mediums.registry import load_medium_contract

            self.medium_contract = load_medium_contract(self.medium)
        return self


# ---------------------------------------------------------------------------
# Layer 3 — Scope / Container (defaults derived from Layer 1)
# ---------------------------------------------------------------------------


# Length-driven defaults. Author can override, but unset fields are populated
# from this table. Tuples are (chapters, word_count, max_pov, max_total_chars).
_LENGTH_DEFAULTS: dict[LengthClass, tuple[int, int, int, int]] = {
    LengthClass.SHORT_STORY: (1, 5_000, 1, 5),
    LengthClass.NOVELLA: (8, 35_000, 2, 12),
    LengthClass.NOVEL: (25, 90_000, 3, 25),
    LengthClass.EPIC_NOVEL: (45, 150_000, 6, 50),
    LengthClass.SERIES: (60, 300_000, 8, 80),
}


class StructuralConstants(BaseModel):
    estimated_chapters: int | None = Field(default=None, ge=1)
    estimated_word_count: int | None = Field(default=None, ge=500)
    act_structure: ActStructure = ActStructure.THREE_ACT
    max_pov_characters: int | None = Field(default=None, ge=1)
    max_characters_total: int | None = Field(default=None, ge=1)
    subplot_budget: int | None = Field(default=None, ge=0)
    scope_contract: ScopeContract | None = None

    def fill_defaults_from(self, length_class: LengthClass) -> Self:
        chapters, words, max_pov, max_total = _LENGTH_DEFAULTS[length_class]
        if self.estimated_chapters is None:
            self.estimated_chapters = chapters
        if self.estimated_word_count is None:
            self.estimated_word_count = words
        if self.max_pov_characters is None:
            self.max_pov_characters = max_pov
        if self.max_characters_total is None:
            self.max_characters_total = max_total
        return self


class ScopeContract(BaseModel):
    recommended_complexity: ScopeComplexity
    narrative_runway: NarrativeRunway
    mechanical_load: MechanicalLoad
    setting_footprint: SettingFootprint | None = None
    timeframe: StoryTimeframe | None = None
    worldbuilding_load: MechanicalLoad | None = None
    cast_load: MechanicalLoad | None = None
    trope_load: TropeLoad | None = None
    scope_notes: list[str] = Field(default_factory=list)
    scope_warnings: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Layer 2 — Promise / Constraints (the compile-time rule file)
# ---------------------------------------------------------------------------


class AuthorAudienceContract(BaseModel):
    content_rating: ContentRating
    explicit_violence: Literal["forbidden", "implied_only", "fade_to_black", "allowed"] = "implied_only"
    explicit_sex: Literal["forbidden", "fade_to_black", "tasteful", "explicit"] = "forbidden"
    profanity: Literal["none", "mild", "moderate", "uncensored"] = "mild"
    on_page_torture: bool = False
    child_harm: bool = False
    mandatory_ending_tone: EndingTone

    expected_elements: list[str] = Field(
        default_factory=list,
        description=(
            "Hard structural beats the Critic will enforce, e.g. "
            "'mentor_death', 'major_betrayal', 'protagonist_low_point_at_75_percent'."
        ),
    )
    forbidden_tropes: list[str] = Field(
        default_factory=list,
        description="Tropes that auto-fail validation, e.g. 'chosen_one_prophecy'.",
    )
    custom_rules: list[str] = Field(
        default_factory=list,
        description="Free-text rules the Critic checks line-by-line.",
    )


# ---------------------------------------------------------------------------
# Layer 4 — Emotional & Tonal Blueprint
# ---------------------------------------------------------------------------


class ActTone(BaseModel):
    act_index: int = Field(ge=1)
    label: str
    tone: str = Field(description="Short emotional descriptor, e.g. 'rising dread with camaraderie'.")


class EmotionalBlueprint(BaseModel):
    overall_emotional_arc: str
    per_act_tones: list[ActTone] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Layer 5 — Characters & Arcs
# ---------------------------------------------------------------------------


class ArcMilestone(BaseModel):
    at_percentage: int = Field(ge=0, le=100)
    description: str


class Relationship(BaseModel):
    other: str
    kind: str = Field(description="e.g. 'trust', 'fear', 'rivalry', 'love'.")
    intensity: float = Field(ge=0.0, le=1.0)


class CharacterState(BaseModel):
    """Live snapshot — mutated by the Story Bible Updater after each chapter."""

    location: str | None = None
    physical: str | None = Field(default=None, description="e.g. 'broken_arm', 'exhausted'.")
    emotional: str | None = None
    inventory: list[str] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    secrets_known: list[str] = Field(default_factory=list)


class Character(BaseModel):
    name: str
    role: CharacterRole
    arc_type: ArcType
    arc_start_percentage: int = Field(ge=0, le=100)
    arc_end_percentage: int = Field(ge=0, le=100)
    current_arc_percentage: int = Field(default=0, ge=0, le=100)
    key_milestones: list[ArcMilestone] = Field(default_factory=list)
    current_state: CharacterState = Field(default_factory=CharacterState)
    identity: object | None = Field(
        default=None,
        description="Optional CharacterIdentity dict (lazy-imported from auteur.character.models).",
    )
    categorization: object | None = Field(
        default=None,
        description="Optional CharacterCategorization dict (lazy-imported from auteur.character.models).",
    )

    @model_validator(mode="after")
    def _arc_bounds_consistent(self) -> Self:
        if self.arc_type != ArcType.FLAT and self.arc_start_percentage == self.arc_end_percentage:
            raise ValueError(
                f"Character {self.name!r} has a non-flat arc but identical start/end percentages."
            )
        if not min(self.arc_start_percentage, self.arc_end_percentage) <= self.current_arc_percentage <= max(
            self.arc_start_percentage, self.arc_end_percentage
        ):
            raise ValueError(
                f"Character {self.name!r}: current_arc_percentage "
                f"{self.current_arc_percentage} is outside [{self.arc_start_percentage}, "
                f"{self.arc_end_percentage}]."
            )
        return self

    def next_milestone(self) -> ArcMilestone | None:
        upcoming = [m for m in self.key_milestones if m.at_percentage >= self.current_arc_percentage]
        return min(upcoming, key=lambda m: m.at_percentage) if upcoming else None


# ---------------------------------------------------------------------------
# Layer 6 — Tension Waveform
# ---------------------------------------------------------------------------


class TensionTarget(BaseModel):
    chapter_index: int = Field(ge=1)
    score: int = Field(ge=1, le=10)
    label: str = Field(description="Beat label, e.g. 'midpoint_battle', 'recovery_valley'.")


class TensionWaveform(BaseModel):
    target_curve: list[TensionTarget] = Field(default_factory=list)
    realized_scores: list[int] = Field(
        default_factory=list,
        description="Actual tension scores (1-10) of chapters as they are accepted.",
    )

    @field_validator("realized_scores")
    @classmethod
    def _scores_in_range(cls, scores: list[int]) -> list[int]:
        for s in scores:
            if not 1 <= s <= 10:
                raise ValueError(f"Realized tension score {s} outside 1-10.")
        return scores

    def target_for(self, chapter_index: int) -> TensionTarget | None:
        for t in self.target_curve:
            if t.chapter_index == chapter_index:
                return t
        return None

    def recent(self, n: int = 3) -> list[int]:
        return self.realized_scores[-n:]


# ---------------------------------------------------------------------------
# Thematic Core
# ---------------------------------------------------------------------------


class ThematicCore(BaseModel):
    central_question: str = Field(
        description="The philosophical question the story interrogates, e.g. 'What does redemption cost?'"
    )
    thesis: str = Field(description="The story's tentative answer or stance.")
    motifs: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Whole-story engine
# ---------------------------------------------------------------------------


class StructuralClaim(BaseModel):
    author_text: str = Field(min_length=1)
    checkable_claims: list[str] = Field(default_factory=list)
    consequence_scale: ConsequenceScale | None = None
    escalation_ceiling: ConsequenceScale | None = None


class MainThread(BaseModel):
    type: ThreadType = ThreadType.MAIN_PLOT
    want: StructuralClaim
    resistance: StructuralClaim
    conflict: StructuralClaim
    stakes: StructuralClaim
    change: StructuralClaim
    thematic_function: str = Field(min_length=1)

    @field_validator("type")
    @classmethod
    def _type_must_be_main_plot(cls, value: ThreadType) -> ThreadType:
        if value != ThreadType.MAIN_PLOT:
            raise ValueError("main_thread.type must be main_plot.")
        return value


class StoryThread(BaseModel):
    name: str = Field(min_length=1)
    type: ThreadType
    want: StructuralClaim
    resistance: StructuralClaim
    conflict: StructuralClaim
    stakes: StructuralClaim
    change: StructuralClaim
    supports_main_by: list[SupportFunction] = Field(min_length=1)
    thematic_function: str = Field(min_length=1)

    @field_validator("type")
    @classmethod
    def _type_must_not_be_main_plot(cls, value: ThreadType) -> ThreadType:
        if value == ThreadType.MAIN_PLOT:
            raise ValueError("subordinate threads cannot use main_plot type.")
        return value


class StoryEngine(BaseModel):
    main_thread: MainThread
    threads: list[StoryThread] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Root: StoryBlueprint
# ---------------------------------------------------------------------------


class StoryBlueprint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity: ProjectIdentity
    structure: StructuralConstants = Field(default_factory=StructuralConstants)
    story_engine: StoryEngine | None = None
    contract: AuthorAudienceContract
    emotional_design: EmotionalBlueprint
    characters: list[Character] = Field(default_factory=list)
    tension_waveform: TensionWaveform = Field(default_factory=TensionWaveform)
    theme: ThematicCore

    # -- Per-agent LLM model routing -------------------------------------
    cartographer_model: str | None = Field(
        default=None,
        description="Optional model override for Cartographer. Falls back to CLI/global model."
    )
    bard_model: str | None = Field(
        default=None,
        description="Optional model override for Bard (drafting). Falls back to CLI/global model."
    )
    critic_model: str | None = Field(
        default=None,
        description="Optional model override for all Critics. Falls back to CLI/global model."
    )

    @model_validator(mode="after")
    def _apply_and_validate(self) -> Self:
        self.structure.fill_defaults_from(self.identity.length_class)
        if self.identity.genre_contract_snapshot is None:
            from auteur.genres.registry import load_genre_contract
            self.identity.genre_contract_snapshot = load_genre_contract(self.identity.genre)
        self._check_pov_count()
        self._check_genre_ending_consistency()
        self._check_audience_contract_consistency()
        return self

    def _check_pov_count(self) -> None:
        povs = [c for c in self.characters if c.role in {CharacterRole.PROTAGONIST, CharacterRole.DEUTERAGONIST}]
        if self.structure.max_pov_characters is not None and len(povs) > self.structure.max_pov_characters:
            raise ValueError(
                f"Declared {len(povs)} POV-eligible characters but max_pov_characters="
                f"{self.structure.max_pov_characters}."
            )

    def _check_genre_ending_consistency(self) -> None:
        grimdark_genres = {Genre.GRIMDARK_FANTASY, Genre.HORROR}
        if (
            self.identity.genre in grimdark_genres
            and self.contract.mandatory_ending_tone == EndingTone.HOPEFUL
        ):
            raise ValueError(
                f"Genre {self.identity.genre.value} typically excludes a fully hopeful ending. "
                "Override the genre or relax the ending tone (e.g. bittersweet)."
            )

    def _check_audience_contract_consistency(self) -> None:
        if self.identity.target_audience in {TargetAudience.MIDDLE_GRADE, TargetAudience.YOUNG_ADULT}:
            if self.contract.explicit_sex == "explicit":
                raise ValueError("Explicit sex content forbidden for middle_grade/young_adult audiences.")
            if self.contract.on_page_torture:
                raise ValueError("on_page_torture is forbidden for middle_grade/young_adult audiences.")

    @classmethod
    def from_yaml(cls, path: str | Path) -> Self:
        """Load a blueprint from a YAML file. Enum fields accept their string values."""
        import yaml

        text = Path(path).read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        return cls.model_validate(data)

    def character(self, name: str) -> Character:
        for c in self.characters:
            if c.name == name:
                return c
        raise KeyError(f"No character named {name!r} in blueprint.")

    def current_act(self, chapter_index: int) -> int:
        chapters = self.structure.estimated_chapters or 1
        if self.structure.act_structure == ActStructure.THREE_ACT:
            if chapter_index <= chapters * 0.25:
                return 1
            if chapter_index <= chapters * 0.75:
                return 2
            return 3
        # Coarse fallback: divide evenly across declared acts in per_act_tones.
        n_acts = max(1, len(self.emotional_design.per_act_tones) or 3)
        return min(n_acts, max(1, ((chapter_index - 1) * n_acts) // chapters + 1))


from auteur.genres.models import GenreContract
ProjectIdentity.model_rebuild()
StoryBlueprint.model_rebuild()
