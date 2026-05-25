from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from auteur.character.enums import (
    Archetype,
    AuthorshipVector,
    DefenseMechanism,
    DependencySymmetry,
    DramaticFunction,
    EssenceTraitSource,
    IntimacyAccess,
    MoralAlignment,
    MotifType,
    PersonalityTrait,
    PhilosophyTag,
    RelationshipArcStage,
    RelationshipType,
    TrustProgressionType,
    ValidationSource,
    VulnerabilityFamily,
)


# ---------------------------------------------------------------------------
# Layer 1 — Narrative Role
# ---------------------------------------------------------------------------


class StructuralRole(BaseModel):
    secondary: list[DramaticFunction] = Field(
        default_factory=list,
        description="Secondary dramatic functions (primary role lives on Character.role).",
    )


# ---------------------------------------------------------------------------
# Layer 2 — Archetypal
# ---------------------------------------------------------------------------


class ArchetypalLayer(BaseModel):
    core: Archetype | None = None
    shadow: Archetype | None = None


# ---------------------------------------------------------------------------
# Layer 3 — Psychology
# ---------------------------------------------------------------------------


class CaregivingAccess(BaseModel):
    openness: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Willingness to provide care, support, and nurture others.",
    )
    reciprocity_tolerance: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="How comfortable the character is with receiving care in return.",
    )
    safety_prerequisites: list[str] = Field(default_factory=list)
    trust_triggers: list[str] = Field(default_factory=list)
    trust_blocks: list[str] = Field(default_factory=list)


class RomanticAccess(BaseModel):
    openness: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Willingness to receive care, depend on another, and be vulnerable in intimate contexts.",
    )
    dependency_willingness: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Comfort with needing others emotionally.",
    )
    safety_prerequisites: list[str] = Field(default_factory=list)
    trust_triggers: list[str] = Field(default_factory=list)
    trust_blocks: list[str] = Field(default_factory=list)


class IntimacyRequirements(BaseModel):
    """How the character grants emotional access and what they need to feel safe."""

    access_pattern: IntimacyAccess = Field(
        default=IntimacyAccess.GUARDED_PROGRESSIVE,
        description="The character's default pattern for granting emotional intimacy.",
    )
    caregiving: CaregivingAccess = Field(
        default_factory=CaregivingAccess,
        description="Willingness and conditions for providing nurture.",
    )
    romantic: RomanticAccess = Field(
        default_factory=RomanticAccess,
        description="Willingness and conditions for receiving care and depending on another.",
    )


class PsychologicalLayer(BaseModel):
    wound: str | None = Field(default=None, description="Core emotional wound, e.g. 'abandonment'.")
    fear: str | None = Field(default=None, description="Deepest fear, e.g. 'irrelevance'.")
    desire: str | None = Field(default=None, description="What the character secretly craves, e.g. 'recognition'.")
    contradictions: list[str] = Field(
        default_factory=list,
        description="Internal contradictions that create believable tension.",
    )
    vulnerability_family: VulnerabilityFamily | None = Field(
        default=None,
        description="The family of emotional vulnerability driving the character's behavior, e.g. 'status_control'.",
    )
    defense_mechanisms: list[DefenseMechanism] = Field(
        default_factory=list,
        description="Stress-response behaviors from controlled vocabulary.",
    )
    validation_dependency: list[ValidationSource] = Field(
        default_factory=list,
        description="Where the character derives their sense of worth, e.g. 'service', 'external_needed', 'achievement'.",
    )
    intimacy: IntimacyRequirements | None = Field(
        default=None,
        description="Character's intimacy access pattern, safety prerequisites, and trust triggers/blocks.",
    )


# ---------------------------------------------------------------------------
# Layer 4 — Texture (behavioral fingerprints)
# ---------------------------------------------------------------------------


class TextureVoice(BaseModel):
    cadence: str | None = Field(default=None, description="Speech cadence, e.g. 'clipped', 'lilting'.")
    vocabulary: str | None = Field(default=None, description="Vocabulary register, e.g. 'technical', 'archaic'.")


class TextureLayer(BaseModel):
    voice: TextureVoice | None = None
    habits: list[str] = Field(default_factory=list, description="Idiosyncratic behaviors.")
    aesthetic: list[str] = Field(default_factory=list, description="Visual/stylistic signatures, e.g. 'silver jewelry'.")
    gestures: list[str] = Field(
        default_factory=list,
        description="Recurring physical gestures, e.g. 'silently fixes his collar during stress', 'walks ahead in crowds'.",
    )
    rituals: list[str] = Field(
        default_factory=list,
        description="Ritualized behavior patterns, e.g. 'checks evacuation exits repeatedly', 'edits announcement boards at night'.",
    )
    social_habits: list[str] = Field(
        default_factory=list,
        description="Social interaction patterns, e.g. 'deliberately breaks rules in front of others', 'avoids eye contact when lying'.",
    )
    behavioral_tells: list[str] = Field(
        default_factory=list,
        description="Subconscious tells that reveal emotional state, e.g. 'folds receipts when anxious'.",
    )
    social_aura: list[str] = Field(
        default_factory=list,
        description="Social atmosphere the character projects, e.g. 'executive_pressure', 'emotional_distance', 'warm_authority'.",
    )


# ---------------------------------------------------------------------------
# Layer 5 — Ideological Profile (character as philosophy)
# ---------------------------------------------------------------------------


class IdeologicalProfile(BaseModel):
    worldview: str | None = Field(
        default=None,
        description="Core philosophical stance, e.g. 'protection through hierarchy'.",
    )
    solution: str | None = Field(
        default=None,
        description="What they believe is the answer to existential insecurity.",
    )
    philosophy_tags: list[PhilosophyTag] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Layer 6 — Essence Profile (identity construction)
# ---------------------------------------------------------------------------


class EssenceTrait(BaseModel):
    name: str
    source: EssenceTraitSource = EssenceTraitSource.PERSONAL
    description: str = ""


class EssenceProfile(BaseModel):
    personal_traits: list[EssenceTrait] = Field(
        default_factory=list,
        description="Traits inherent to the character's original identity.",
    )
    bond_traits: list[EssenceTrait] = Field(
        default_factory=list,
        description="Traits acquired through Essence Bonds — may become authentic over time.",
    )


# ---------------------------------------------------------------------------
# Layer 7 — Motif Profile (recurring symbolic behaviors)
# ---------------------------------------------------------------------------


class Motif(BaseModel):
    behavior: str = Field(description="The recurring action, e.g. 'silently replaces his damaged items before he notices'.")
    type: MotifType = MotifType.GESTURE
    significance: str = Field(
        default="",
        description="What this motif communicates emotionally or thematically.",
    )


class MotifProfile(BaseModel):
    motifs: list[Motif] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Arc / Transformation
# ---------------------------------------------------------------------------


class ArcChange(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: str = Field(default="", alias="from", description="Starting trait, e.g. 'control'.")
    to: str = Field(default="", description="Ending trait, e.g. 'vulnerability'.")


class ArcEngine(BaseModel):
    positive_change: ArcChange | None = Field(
        default=None,
        description="Direction of positive transformation. Empty for flat/corruption arcs.",
    )


# ---------------------------------------------------------------------------
# Relationship
# ---------------------------------------------------------------------------


class RelationshipSignature(BaseModel):
    other: str
    type: RelationshipType
    intensity: float = Field(ge=0.0, le=1.0, default=0.5)
    bidirectional: bool = Field(default=True)
    ideological_alignment: str | None = Field(
        default=None,
        description="How their worldviews relate: 'aligned', 'opposed', 'complementary', 'asymmetric'.",
    )
    authorship_vector: AuthorshipVector | None = Field(
        default=None,
        description="Who shapes whom in the relationship.",
    )
    dependency_symmetry: DependencySymmetry | None = Field(
        default=None,
        description="How dependency is distributed.",
    )


class RelationshipArc(BaseModel):
    other: str
    stages: list[str] = Field(
        default_factory=list,
        description="Progression stages of the relationship, e.g. 'fascination', 'vulnerability_discovery', 'trust_formation'.",
    )
    current_stage: str | None = Field(default=None, description="Where the relationship currently sits in its arc.")
    trust_level: float = Field(ge=0.0, le=1.0, default=0.5)
    trust_evolution: str | None = Field(
        default=None,
        description="Narrative of how trust changed over time, e.g. 'rose steadily, dipped at crisis, recovered stronger'.",
    )
    turning_points: list[str] = Field(
        default_factory=list,
        description="Key events that changed the relationship trajectory.",
    )
    progression_type: str | None = Field(
        default=None,
        description="How the relationship evolves: 'trust_based', 'coercive', 'adversarial', 'ritualistic'.",
    )
    asymmetry_state: str | None = Field(
        default=None,
        description="Current asymmetry dynamic: 'savior', 'rescued', 'mutual', 'pursuer_distance', 'nurturer_dependent', etc.",
    )
    asymmetry_trajectory: str | None = Field(
        default=None,
        description="How asymmetry is evolving over time: 'balancing', 'deepening', 'dissolving', 'stuck'.",
    )
    asymmetry_history: list[str] = Field(
        default_factory=list,
        description="Notable shifts in the relationship asymmetry over the story arc.",
    )


class RelationshipMesh(BaseModel):
    relationships: list[RelationshipSignature] = Field(default_factory=list)
    ideological_tensions: list[str] = Field(
        default_factory=list,
        description="Philosophical conflicts active in the relationship network.",
    )
    arcs: list[RelationshipArc] = Field(
        default_factory=list,
        description="Relationship arcs tracking progression stages and trust evolution.",
    )


# ---------------------------------------------------------------------------
# Analysis / Inference
# ---------------------------------------------------------------------------


class ThematicAlignment(BaseModel):
    theme: str
    stance: str = Field(
        description="How the character embodies or challenges the theme.",
    )


class RoleInference(BaseModel):
    inferred_role: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    reasoning: str = ""


class SceneEnergySignature(BaseModel):
    """Inferred profile of the atmospheric impact a character has in a scene."""

    default_atmosphere: list[str] = Field(
        default_factory=list,
        description="The ambient feeling the character carries, e.g. 'formal_pressure', 'warm_reassurance', 'unsettling_calm'.",
    )
    pressure_style: list[str] = Field(
        default_factory=list,
        description="How the character applies social weight, e.g. 'direct_command', 'silent_expectation', 'emotional_withholding'.",
    )
    silence_quality: list[str] = Field(
        default_factory=list,
        description="What silence feels like around them, e.g. 'tense', 'comfortable', 'expectant', 'heavy'.",
    )
    spatial_behavior: list[str] = Field(
        default_factory=list,
        description="How they occupy physical space, e.g. 'occupies_center', 'hovers_periphery', 'controls_thresholds'.",
    )
    interruption_pattern: str | None = Field(
        default=None,
        description="How they handle conversational turn-taking, e.g. 'frequent', 'never', 'strategic', 'deferential'.",
    )
    gaze_control: str | None = Field(
        default=None,
        description="How they use eye contact, e.g. 'holding', 'avoidant', 'measuring', 'intimate'.",
    )


# ---------------------------------------------------------------------------
# Root: CharacterIdentity (authored)
# ---------------------------------------------------------------------------


class CharacterIdentity(BaseModel):
    narrative_role: StructuralRole | None = None
    archetype: ArchetypalLayer | None = None
    psychology: PsychologicalLayer | None = None
    texture: TextureLayer | None = None
    ideology: IdeologicalProfile | None = None
    essence: EssenceProfile | None = None
    motifs: MotifProfile | None = None
    arc: ArcEngine | None = None
    relationship_mesh: RelationshipMesh | None = None

    moral_alignment: MoralAlignment | None = None
    personality_traits: list[PersonalityTrait] = Field(default_factory=list)
    trope_tags: list[TropeTag] = Field(default_factory=list)
    custom_tags: list[str] = Field(
        default_factory=list,
        description="Free-form semantic tags beyond the controlled vocabulary.",
    )


# ---------------------------------------------------------------------------
# CharacterCategorization (inferred)
# ---------------------------------------------------------------------------


class CharacterCategorization(BaseModel):
    identity: CharacterIdentity = Field(default_factory=CharacterIdentity)
    relationship_signatures: list[RelationshipSignature] = Field(default_factory=list)
    thematic_alignments: list[ThematicAlignment] = Field(default_factory=list)
    role_inferences: list[RoleInference] = Field(default_factory=list)
    scene_energy: SceneEnergySignature | None = Field(
        default=None,
        description="Inferred atmospheric signature — how the character shapes scene energy through presence, pressure, and spatial behavior.",
    )
