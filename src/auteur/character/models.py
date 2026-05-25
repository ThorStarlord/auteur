from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from auteur.character.enums import (
    Archetype,
    DramaticFunction,
    MoralAlignment,
    PersonalityTrait,
    RelationshipType,
    TropeTag,
)


class StructuralRole(BaseModel):
    secondary: list[DramaticFunction] = Field(
        default_factory=list,
        description="Secondary dramatic functions (primary role lives on Character.role).",
    )


class ArchetypalLayer(BaseModel):
    core: Archetype | None = None
    shadow: Archetype | None = None


class PsychologicalLayer(BaseModel):
    wound: str | None = Field(default=None, description="Core emotional wound, e.g. 'abandonment'.")
    fear: str | None = Field(default=None, description="Deepest fear, e.g. 'irrelevance'.")
    desire: str | None = Field(default=None, description="What the character secretly craves, e.g. 'recognition'.")
    contradictions: list[str] = Field(
        default_factory=list,
        description="Internal contradictions that create believable tension, e.g. 'compassionate_to_strangers', 'cruel_to_family'.",
    )


class TextureVoice(BaseModel):
    cadence: str | None = Field(default=None, description="Speech cadence, e.g. 'clipped', 'lilting'.")
    vocabulary: str | None = Field(default=None, description="Vocabulary register, e.g. 'technical', 'archaic'.")


class TextureLayer(BaseModel):
    voice: TextureVoice | None = None
    habits: list[str] = Field(default_factory=list, description="Idiosyncratic behaviors.")
    aesthetic: list[str] = Field(default_factory=list, description="Visual/stylistic signatures, e.g. 'silver jewelry'.")


class ArcChange(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: str = Field(default="", alias="from", description="Starting trait, e.g. 'control'.")
    to: str = Field(default="", description="Ending trait, e.g. 'vulnerability'.")


class ArcEngine(BaseModel):
    positive_change: ArcChange | None = Field(
        default=None,
        description="Direction of positive transformation. Empty for flat/corruption arcs.",
    )


class RelationshipSignature(BaseModel):
    other: str
    type: RelationshipType
    intensity: float = Field(ge=0.0, le=1.0, default=0.5)
    bidirectional: bool = Field(
        default=True,
        description="Whether the relationship is likely mutual.",
    )


class RelationshipMesh(BaseModel):
    relationships: list[RelationshipSignature] = Field(default_factory=list)


class ThematicAlignment(BaseModel):
    theme: str
    stance: str = Field(
        description="How the character embodies or challenges the theme, e.g. 'embodies', 'questions', 'rejects'.",
    )


class RoleInference(BaseModel):
    inferred_role: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    reasoning: str = ""


class CharacterIdentity(BaseModel):
    narrative_role: StructuralRole | None = None
    archetype: ArchetypalLayer | None = None
    psychology: PsychologicalLayer | None = None
    texture: TextureLayer | None = None
    arc: ArcEngine | None = None
    relationship_mesh: RelationshipMesh | None = None

    moral_alignment: MoralAlignment | None = None
    personality_traits: list[PersonalityTrait] = Field(default_factory=list)
    trope_tags: list[TropeTag] = Field(default_factory=list)
    custom_tags: list[str] = Field(
        default_factory=list,
        description="Free-form semantic tags beyond the controlled vocabulary.",
    )


class CharacterCategorization(BaseModel):
    identity: CharacterIdentity = Field(default_factory=CharacterIdentity)
    relationship_signatures: list[RelationshipSignature] = Field(default_factory=list)
    thematic_alignments: list[ThematicAlignment] = Field(default_factory=list)
    role_inferences: list[RoleInference] = Field(default_factory=list)
