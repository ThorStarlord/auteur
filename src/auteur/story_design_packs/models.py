"""Typed, reusable story-design knowledge and derived guidance models."""
from __future__ import annotations

from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, Field


class PackKind(str, Enum):
    GENRE = "genre"
    CHARACTER = "character"
    THEME = "theme"
    SETTING = "setting"


class RuleStrength(str, Enum):
    HARD_CONSTRAINT = "HARD_CONSTRAINT"
    STRONG_DEFAULT = "STRONG_DEFAULT"
    COMMON_PATTERN = "COMMON_PATTERN"
    OPTIONAL_TECHNIQUE = "OPTIONAL_TECHNIQUE"
    BOUNDARY_WARNING = "BOUNDARY_WARNING"
    INTENTIONAL_SUBVERSION_POINT = "INTENTIONAL_SUBVERSION_POINT"


class DesignOption(BaseModel):
    option_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    what_it_is: str = Field(min_length=1)
    craft_function: str = Field(min_length=1)
    works_well_when: str = Field(min_length=1)
    tradeoffs: list[str] = Field(default_factory=list)
    common_beginner_failure: str = ""
    compatible_patterns: list[str] = Field(default_factory=list)
    tensions: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    architecture_targets: list[str] = Field(default_factory=list)
    strength: RuleStrength = RuleStrength.COMMON_PATTERN


class CraftPrinciple(BaseModel):
    principle_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    explanation: str = Field(min_length=1)


class CommonFailure(BaseModel):
    failure_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    symptom: str = Field(min_length=1)
    correction: str = Field(min_length=1)


class TeachingNote(BaseModel):
    note_id: str = Field(min_length=1)
    concept: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    question: str = Field(min_length=1)


class CompatibilityRule(BaseModel):
    rule_id: str = Field(min_length=1)
    other_pack_id: str = Field(min_length=1)
    relation: Literal["reinforces", "tension", "incompatible"]
    statement: str = Field(min_length=1)
    strength: RuleStrength = RuleStrength.COMMON_PATTERN
    suggested_question: str = ""


class DecisionHook(BaseModel):
    hook_id: str = Field(min_length=1)
    decision: str = Field(min_length=1)
    question: str = Field(min_length=1)
    recommended_option_id: str | None = None


class Applicability(BaseModel):
    signals: list[str] = Field(default_factory=list)
    description: str = Field(min_length=1)


class DesignPackPayload(BaseModel):
    options: list[DesignOption] = Field(default_factory=list)
    principles: list[CraftPrinciple] = Field(default_factory=list)
    common_failures: list[CommonFailure] = Field(default_factory=list)


class StoryDesignPack(BaseModel):
    pack_id: str = Field(min_length=1)
    pack_kind: PackKind
    version: str = Field(min_length=1)
    schema_version: int = Field(default=1, ge=1)
    display_name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    applicability: Applicability
    design_options: list[DesignOption] = Field(default_factory=list)
    teaching_notes: list[TeachingNote] = Field(default_factory=list)
    common_failures: list[CommonFailure] = Field(default_factory=list)
    compatibility_rules: list[CompatibilityRule] = Field(default_factory=list)
    decision_hooks: list[DecisionHook] = Field(default_factory=list)


class PackProvenance(BaseModel):
    pack_id: str
    version: str
    content_hash: str


class PackComposition(BaseModel):
    selected_packs: list[PackProvenance]
    applicable_design_priors: list[DesignOption] = Field(default_factory=list)
    reinforcing_patterns: list[str] = Field(default_factory=list)
    productive_tensions: list[str] = Field(default_factory=list)
    actual_conflicts: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    decision_suggestions: list[DecisionHook] = Field(default_factory=list)
    pack_provenance: list[PackProvenance] = Field(default_factory=list)


class TutorGuidance(BaseModel):
    decision: str
    orientation: str
    craft_concept: str
    plain_language_explanation: str
    story_application: str
    recommendation: str
    why_recommended: str
    alternatives: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)
    when_alternative_is_stronger: list[str] = Field(default_factory=list)
    common_beginner_mistake: str
    pack_sources: list[PackProvenance]
    architecture_evidence: list[str] = Field(default_factory=list)
    consequence: str
    question_for_author: str
    comprehension_check: str | None = None
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"


PackPayload = Union[DesignPackPayload]

# Public vocabulary aliases keep the implementation name concrete while
# matching the product contract's envelope/context terminology.
DesignPackEnvelope = StoryDesignPack
StoryDesignContext = PackComposition
