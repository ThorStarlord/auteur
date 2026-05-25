from __future__ import annotations

from pydantic import BaseModel, Field

from auteur.character.enums import (
    Archetype,
    DramaticFunction,
    MoralAlignment,
    PersonalityTrait,
    ProtagonistSubtype,
    RelationshipType,
    TropeTag,
    Vice,
    Virtue,
)


class CharacterIdentity(BaseModel):
    archetype: Archetype | None = None
    protagonist_subtype: ProtagonistSubtype | None = None
    moral_alignment: MoralAlignment | None = None
    virtues: list[Virtue] = Field(default_factory=list)
    vices: list[Vice] = Field(default_factory=list)
    personality_traits: list[PersonalityTrait] = Field(default_factory=list)
    dramatic_functions: list[DramaticFunction] = Field(default_factory=list)
    trope_tags: list[TropeTag] = Field(default_factory=list)
    custom_tags: list[str] = Field(
        default_factory=list,
        description="Free-form semantic tags beyond the controlled vocabulary.",
    )


class RelationshipSignature(BaseModel):
    other: str
    type: RelationshipType
    intensity: float = Field(ge=0.0, le=1.0, default=0.5)
    bidirectional: bool = Field(
        default=True,
        description="Whether the relationship is likely mutual.",
    )


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


class CharacterCategorization(BaseModel):
    identity: CharacterIdentity = Field(default_factory=CharacterIdentity)
    relationship_signatures: list[RelationshipSignature] = Field(default_factory=list)
    thematic_alignments: list[ThematicAlignment] = Field(default_factory=list)
    role_inferences: list[RoleInference] = Field(default_factory=list)
