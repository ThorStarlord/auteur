"""Typed, reusable story-design knowledge and derived guidance models."""
from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


class PackKind(str, Enum):
    GENRE = "genre"
    CHARACTER = "character"
    THEME = "theme"
    SETTING = "setting"


class TutorDepth(str, Enum):
    """Presentation depth for derived Tutor guidance."""

    RECOMMEND = "recommend"
    EXPLAIN = "explain"
    TEACH = "teach"
    CHALLENGE = "challenge"
    QUIZ = "quiz"


class AuthorAction(str, Enum):
    CHOOSE = "choose"
    KEEP_UNRESOLVED = "keep_unresolved"
    REQUEST_ALTERNATIVES = "request_alternatives"
    REJECT_FINDING = "reject_finding"


SourceFingerprint = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


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


class TutorDiagnosticGuidance(BaseModel):
    diagnostic_rule: str
    what_seems_wrong: str
    craft_principle: str
    why_it_matters_in_this_story: str
    repair_options: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)
    next_author_decision: str
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"


class DecisionCard(BaseModel):
    """One author-decidable, derived creative decision."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: int = Field(default=1, ge=1)
    card_id: str = ""
    decision: str = Field(min_length=1)
    orientation: str = Field(min_length=1)
    why_it_matters: str = Field(min_length=1)
    craft_concept: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)
    alternatives: tuple[str, ...] = Field(default_factory=tuple)
    tradeoffs: tuple[str, ...] = Field(default_factory=tuple)
    beginner_trap: str = Field(min_length=1)
    downstream_consequences: tuple[str, ...] = Field(default_factory=tuple)
    evidence: tuple[str, ...] = Field(default_factory=tuple)
    pack_sources: tuple[PackProvenance, ...] = Field(default_factory=tuple)
    depth: TutorDepth = TutorDepth.RECOMMEND
    source_rule: str | None = None
    author_actions: tuple[AuthorAction, ...] = Field(
        default_factory=lambda: (
            AuthorAction.CHOOSE,
            AuthorAction.KEEP_UNRESOLVED,
            AuthorAction.REQUEST_ALTERNATIVES,
        )
    )
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"

    @model_validator(mode="after")
    def ensure_card_id(self) -> "DecisionCard":
        expected = stable_card_id(self.semantic_identity_payload())
        if self.card_id and self.card_id != expected:
            raise ValueError("card_id does not match semantic identity")
        if not self.card_id:
            object.__setattr__(self, "card_id", expected)
        return self

    def semantic_identity_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "decision": self.decision,
            "orientation": self.orientation,
            "why_it_matters": self.why_it_matters,
            "craft_concept": self.craft_concept,
            "recommendation": self.recommendation,
            "alternatives": self.alternatives,
            "tradeoffs": self.tradeoffs,
            "beginner_trap": self.beginner_trap,
            "downstream_consequences": self.downstream_consequences,
            "evidence": self.evidence,
            "pack_sources": self.pack_sources,
            "source_rule": self.source_rule,
        }

    def with_depth(self, depth: TutorDepth) -> "DecisionCard":
        values = self.model_dump()
        values["depth"] = depth
        return type(self).model_validate(values)

    @classmethod
    def from_diagnostic(
        cls,
        *,
        rule: str,
        message: str,
        story_context: str,
        repair_options: list[str],
        evidence: list[str] | None = None,
    ) -> "DecisionCard":
        return cls(
            decision="Resolve or intentionally preserve the finding",
            orientation=f"A finding needs an author decision in {story_context}.",
            why_it_matters=message,
            craft_concept="Narrative consequence",
            recommendation=repair_options[0] if repair_options else "Inspect the finding before changing the story.",
            alternatives=tuple(repair_options),
            tradeoffs=[
                "Repairing the finding may require changing a later commitment.",
                "Keeping it preserves ambiguity but should be intentional.",
            ],
            beginner_trap="Treating a diagnostic as an automatic rewrite instruction.",
            downstream_consequences=["Any selected repair remains a proposal until explicitly accepted."],
            evidence=tuple(evidence or [rule, message]),
            source_rule=rule,
            author_actions=(
                AuthorAction.CHOOSE,
                AuthorAction.KEEP_UNRESOLVED,
                AuthorAction.REJECT_FINDING,
                AuthorAction.REQUEST_ALTERNATIVES,
            ),
        )


def stable_card_id(payload: object) -> str:
    """Return a stable identifier for a derived Decision Card."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=_json_default).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def _json_default(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def source_fingerprint(source: object) -> SourceFingerprint:
    if isinstance(source, bytes):
        encoded = source
    elif isinstance(source, str):
        encoded = source.encode("utf-8")
    else:
        encoded = json.dumps(source, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


PackPayload = Union[DesignPackPayload]

# Public vocabulary aliases keep the implementation name concrete while
# matching the product contract's envelope/context terminology.
DesignPackEnvelope = StoryDesignPack
StoryDesignContext = PackComposition
