"""Pydantic models for Author Decision Objects.

Composes the existing frozen dataclass ``UnresolvedChoice`` (question + explicit
options) rather than introducing a parallel representation. AuthorDecision narrows
it: options are required and must be an explicit list of at least two strings
(open-ended ``options=None`` is rejected). Unknown fields are rejected at every
level (anti-creep rule from the approved design).
"""
from __future__ import annotations

import enum
import re
from pathlib import Path
from typing import Any, Literal

import yaml as _yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from auteur.decision.models import UnresolvedChoice


class DecisionValidationError(ValueError):
    """Raised when an author decision artifact is invalid or its references cannot be resolved."""


# Lowest shared boundary for path safety: no filesystem path may ever be derived
# from a decision_id that fails this pattern (review finding F1).
_DECISION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def validate_decision_id(decision_id: str) -> None:
    """Raise DecisionValidationError unless decision_id is a safe, stable artifact id."""
    if not isinstance(decision_id, str) or _DECISION_ID_RE.fullmatch(decision_id) is None:
        raise DecisionValidationError(
            f"invalid decision_id {decision_id!r}: must match {_DECISION_ID_RE.pattern}"
        )


class CombinationRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule: Literal["one_of", "choose_k_of_n"] = "one_of"
    k: int | None = None


class Criterion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    evaluator: str = "author_or_consumer"


class ConstraintRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ref: str
    snapshot: str | None = None


class RequiredCharacter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    standing: str | None = None


class BlockedOutcomeRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule: str
    classification: Literal[
        "DIRECT_DETERMINISTIC", "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"
    ]
    source: str | None = None


class BlockedProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # No stable outcome IDs exist in the current model (PropagationOutcome,
    # blueprint.py:713); (rule, classification, source) tuples are the strongest
    # stable reference available. expected_count is DERIVED from these refs.
    outcome_refs: list[BlockedOutcomeRef] = Field(default_factory=list)


class DefaultReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Author declares the RELATIONSHIP; the product-owned VALUE is resolved from
    # the current Blueprint by the context builder (never authored by restating).
    default_id: str
    relates_to: str
    relationship: str = "conflicts_with"


class EntityReferenceKind(str, enum.Enum):
    """Accepted relationship vocabulary (design rev 2, binding): EXACTLY two
    values, both with defined shipped consumer semantics. requires/preserves
    are deferred candidates, NOT schema values: Auteur must not accept authored
    semantic declarations that are silently inert."""

    concerns = "concerns"
    conflicts_with = "conflicts_with"


class EntityReference(BaseModel):
    """One explicit authored alternative->entity link (M1)."""

    model_config = ConfigDict(extra="forbid")

    entity_ref: str  # exact field-path ref, roots identity|blueprint (Q4)
    relationship: EntityReferenceKind = EntityReferenceKind.concerns


class AlternativeBinding(BaseModel):
    """Bindings authored directly on one alternative (M1)."""

    model_config = ConfigDict(extra="forbid")

    alternative_id: str
    references: list[EntityReference] = Field(min_length=1)


class StructuralAnchorKind(str, enum.Enum):
    """Minimal structural-kind vocabulary (B4 design Q1): ONLY the kind
    justified by the Case E reasoning requirement."""

    subplot = "subplot"


class AnchorRelationshipKind(str, enum.Enum):
    """Minimal anchor relationship vocabulary: ONLY bears_on in this slice."""

    bears_on = "bears_on"


class AnchorRelationshipNature(str, enum.Enum):
    """N1 closed relationship-nature vocabulary (design 2026-08-relationship-
    nature-n1.md): EXACTLY {sustains, pressures} in this slice. Every value has
    pinned author meaning, consumer meaning, and composed kept/cut semantics.
    complicates/resolves are deferred candidates, NOT schema values: if Auteur
    accepts a semantic relationship, the shipped consumer knows what it means."""

    sustains = "sustains"
    pressures = "pressures"


class AnchorBearsOn(BaseModel):
    """One explicit anchor->canonical relationship (e.g. a subplot bears on the
    ending constraint). ``nature`` describes HOW the anchor relates to THAT
    target (per-relationship, never anchor-global); None = "relationship nature
    not explicitly supplied" (the bears_on relevance remains valid)."""

    model_config = ConfigDict(extra="forbid")

    ref: str  # explicit-root ref (identity. / blueprint. / decision.)
    relationship: AnchorRelationshipKind = AnchorRelationshipKind.bears_on
    nature: AnchorRelationshipNature | None = None


class StructuralAnchor(BaseModel):
    """Decision-scoped author context (B4): an explicit structural entity or
    relationship the canonical story representation does not carry. NEVER
    promoted into canonical Blueprint/Identity state."""

    model_config = ConfigDict(extra="forbid")

    anchor_id: str
    kind: StructuralAnchorKind = StructuralAnchorKind.subplot
    participants: list[str] = Field(default_factory=list)  # explicit entity_refs
    carrier_refs: list[str] = Field(default_factory=list)  # empty = not declared
    bears_on: list[AnchorBearsOn] = Field(default_factory=list)


class AuthorDecision(BaseModel):
    """Authored, validated author decision artifact (YAML)."""

    model_config = ConfigDict(extra="forbid")

    decision_id: str | None = None
    unresolved_choice: UnresolvedChoice
    alternative_ids: list[str] = Field(default_factory=list)
    combination: CombinationRule = Field(default_factory=CombinationRule)
    criterion: Criterion
    hard_constraints: list[ConstraintRef] = Field(default_factory=list)
    required_characters: list[RequiredCharacter] = Field(default_factory=list)
    blocked_provenance: BlockedProvenance = Field(default_factory=BlockedProvenance)
    default_references: list[DefaultReference] = Field(default_factory=list)
    alternative_bindings: list[AlternativeBinding] = Field(default_factory=list)
    structural_anchors: list[StructuralAnchor] = Field(default_factory=list)
    combination_direction: Literal["kept", "cut"] | None = None

    @model_validator(mode="after")
    def _validate_semantics(self) -> "AuthorDecision":
        opts = self.unresolved_choice.options
        if opts is None or len(opts) < 2:
            raise DecisionValidationError(
                "alternatives (unresolved_choice.options) must be an explicit authored "
                "list of at least 2 — open-ended choices are not author decisions"
            )
        n = len(opts)
        if len(self.alternative_ids) != n:
            raise DecisionValidationError(
                "alternative_ids must have the same length as unresolved_choice.options"
            )
        if len(set(self.alternative_ids)) != n:
            raise DecisionValidationError("alternative_ids must be unique")
        if self.combination.rule == "choose_k_of_n":
            k = self.combination.k
            if k is None or k < 1 or k > n:
                raise DecisionValidationError(
                    f"choose_k_of_n requires 1 <= k <= {n}, got k={k!r}"
                )
        if self.decision_id is None:
            self.decision_id = self.unresolved_choice.choice_id or "unnamed"
        validate_decision_id(self.decision_id)  # F1: path safety at the model boundary
        if self.combination.rule == "one_of" and self.combination.k is not None:
            raise DecisionValidationError("one_of must not carry k")
        self._validate_bindings()
        self._validate_anchors()
        return self

    def _validate_anchors(self) -> None:
        """B4 schema integrity (design Q8): duplicate anchor ids, duplicate
        refs within lists, and one_of+direction all fail closed."""
        if self.combination_direction is not None and self.combination.rule != "choose_k_of_n":
            raise DecisionValidationError(
                "combination_direction requires combination rule choose_k_of_n"
            )
        seen: set[str] = set()
        for a in self.structural_anchors:
            if not _DECISION_ID_RE.fullmatch(a.anchor_id):
                raise DecisionValidationError(
                    f"invalid anchor_id {a.anchor_id!r}: must match {_DECISION_ID_RE.pattern}"
                )
            if a.anchor_id in seen:
                raise DecisionValidationError(
                    f"duplicate anchor_id: {a.anchor_id!r}"
                )
            seen.add(a.anchor_id)
            if len(set(a.participants)) != len(a.participants):
                raise DecisionValidationError(
                    f"duplicate participant ref in anchor {a.anchor_id!r}"
                )
            if len(set(a.carrier_refs)) != len(a.carrier_refs):
                raise DecisionValidationError(
                    f"duplicate carrier ref in anchor {a.anchor_id!r}"
                )
            refs = [b.ref for b in a.bears_on]
            if len(set(refs)) != len(refs):
                raise DecisionValidationError(
                    f"duplicate bears_on ref in anchor {a.anchor_id!r}"
                )

    def _validate_bindings(self) -> None:
        """M1 schema integrity (design Q8): unknown alternative_id, duplicate
        blocks, duplicate identical references, and conflicting relationship
        declarations all fail closed; no merge is performed."""
        alt_ids = set(self.alternative_ids)
        seen_blocks: set[str] = set()
        for b in self.alternative_bindings:
            if b.alternative_id not in alt_ids:
                raise DecisionValidationError(
                    f"binding references unknown alternative_id: {b.alternative_id!r}"
                )
            if b.alternative_id in seen_blocks:
                raise DecisionValidationError(
                    f"duplicate binding block for alternative: {b.alternative_id!r}"
                )
            seen_blocks.add(b.alternative_id)
            declared: dict[str, EntityReferenceKind] = {}
            for r in b.references:
                if r.entity_ref in declared:
                    if declared[r.entity_ref] == r.relationship:
                        raise DecisionValidationError(
                            f"duplicate identical reference in binding for "
                            f"{b.alternative_id!r}: {r.entity_ref}"
                        )
                    raise DecisionValidationError(
                        f"conflicting relationship declarations for "
                        f"{b.alternative_id!r} / {r.entity_ref}"
                    )
                declared[r.entity_ref] = r.relationship

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuthorDecision":
        import copy

        payload = copy.deepcopy(data)
        choice = payload.get("unresolved_choice")
        # The reused frozen dataclass requires choice_id (workspace identity
        # metadata). AuthorDecision derives a stable one when the author omitted
        # it; this is layer-level normalization, not a parallel model.
        if isinstance(choice, dict) and "choice_id" not in choice:
            choice["choice_id"] = payload.get("decision_id") or "unnamed"
        try:
            return cls.model_validate(payload)
        except DecisionValidationError:
            raise
        except ValidationError as exc:
            raise DecisionValidationError(
                f"invalid author decision artifact: {exc}"
            ) from exc

    @classmethod
    def from_yaml(cls, path: Path | str) -> "AuthorDecision":
        path = Path(path)
        data = _yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise DecisionValidationError(
                f"author decision artifact must be a YAML mapping: {path}"
            )
        return cls.from_dict(data)
