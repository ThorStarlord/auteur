"""Thin context projection (M2) for author decisions.

Resolves ONLY explicitly referenced material: constraint refs against the accepted
Identity, blocked-provenance refs and default references against the current
Blueprint. The builder is deliberately NOT "helpful": it never searches for
semantically related information, and it fails closed on any unresolvable or
mismatched reference. Nothing is copied unless a golden-rubric item requires it.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

from auteur.author_decisions.models import (
    AuthorDecision,
    DecisionValidationError,
)
from auteur.blueprint import StoryBlueprint
from auteur.identity import StoryIdentity

_REF_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_.]*)\[(\d+)\]")


class ResolvedConstraint:
    """One resolved hard constraint: ref plus verbatim text from the Identity."""

    __slots__ = ("ref", "text")

    def __init__(self, ref: str, text: str) -> None:
        self.ref = ref
        self.text = text


class ResolvedBinding:
    """One resolved M1 alternative->entity binding: exact field-path reference
    plus the resolved entity object. Resolution is exact and fail-closed; the
    consumer derives consequences FROM these, never creates them."""

    __slots__ = ("alternative_id", "entity_ref", "relationship", "entity")

    def __init__(self, alternative_id: str, entity_ref: str, relationship, entity: Any) -> None:
        self.alternative_id = alternative_id
        self.entity_ref = entity_ref
        self.relationship = relationship
        self.entity = entity


class DecisionContext:
    """The thin resolved context; carries only what the decision references."""

    def __init__(
        self,
        decision: AuthorDecision,
        constraints: list[ResolvedConstraint],
        blocked_count: int,
        blocked_provenance_verified: bool,
        resolved_defaults: dict[str, Any],
        identity: Any = None,
        blueprint: Any = None,
        resolved_bindings: list[ResolvedBinding] | None = None,
    ) -> None:
        self.decision = decision
        self.constraints = constraints
        self.blocked_count = blocked_count
        self.blocked_provenance_verified = blocked_provenance_verified
        self.resolved_defaults = resolved_defaults
        # Objects the resolution ran against; carried so the deterministic
        # consequence consumer can probe concrete structure with exact refs.
        self.identity = identity
        self.blueprint = blueprint
        self.resolved_bindings = resolved_bindings or []

    @property
    def alternative_labels(self) -> list[str]:
        # Alternatives are the authored options, verbatim — never extracted from prose.
        return list(self.decision.unresolved_choice.options or [])

    @property
    def alternative_source(self) -> str:
        return "authored"

    def build_report(self) -> dict[str, Any]:
        from auteur.author_decisions.report import build_report

        return build_report(self)


def _resolve_identity_ref(identity: StoryIdentity, ref: str) -> str:
    """Resolve 'not_this[0]', 'rejected_directions[1]', 'target_experience.avoid[0]'."""
    m = _REF_RE.fullmatch(ref)
    if not m:
        raise DecisionValidationError(f"unsupported constraint ref syntax: {ref!r}")
    path, idx = m.group(1), int(m.group(2))
    obj: Any = identity
    for part in path.split("."):
        obj = getattr(obj, part, None)
        if obj is None:
            raise DecisionValidationError(f"unresolvable constraint ref: {ref}")
    if not isinstance(obj, (list, tuple)) or idx >= len(obj):
        raise DecisionValidationError(f"constraint ref index out of range: {ref}")
    return str(obj[idx])


def _resolve_default(blueprint: StoryBlueprint, default_id: str) -> Any:
    """Resolve a product-owned default reference (e.g. contract.mandatory_ending_tone)."""
    if default_id == "characters":
        return [c.name for c in blueprint.characters]
    obj: Any = blueprint
    for part in default_id.split("."):
        obj = getattr(obj, part, None)
        if obj is None:
            raise DecisionValidationError(f"unresolvable default reference: {default_id}")
    if hasattr(obj, "value"):  # enum -> its serialized value
        return obj.value
    return obj


def _resolve_entity_ref(identity: StoryIdentity, blueprint: StoryBlueprint, entity_ref: str) -> Any:
    """Exact field-path resolution for M1 bindings (design Q4).

    Allowed roots: identity (Layer 1) and blueprint (Layer 2) ONLY. Grammar is
    the shipped field-path form (e.g. identity.characters[0],
    identity.characters[3].undergoes_central_change). Fail closed on any
    unknown path, non-list index, malformed index, or out-of-range index.
    """
    if entity_ref in ("identity", "blueprint") or entity_ref.startswith(("identity.", "blueprint.")) is False:
        raise DecisionValidationError(
            f"entity_ref must be a field path rooted at identity or blueprint: {entity_ref!r}"
        )
    root_name, _, rest = entity_ref.partition(".")
    root = identity if root_name == "identity" else blueprint
    obj: Any = root
    for part in rest.split("."):
        idx = None
        if "[" in part:
            if not part.endswith("]"):
                raise DecisionValidationError(f"malformed entity_ref: {entity_ref!r}")
            name, _, span = part.partition("[")
            try:
                idx = int(span[:-1])
            except ValueError:
                raise DecisionValidationError(f"malformed entity_ref index: {entity_ref!r}")
            part = name
        obj = getattr(obj, part, None)
        if obj is None:
            raise DecisionValidationError(f"unresolvable entity_ref: {entity_ref!r}")
        if idx is not None:
            if not isinstance(obj, (list, tuple)) or idx >= len(obj):
                raise DecisionValidationError(
                    f"entity_ref index out of range: {entity_ref!r}"
                )
            obj = obj[idx]
    return obj


def _verify_blocked_provenance(blueprint: StoryBlueprint, refs) -> bool:
    outcomes = []
    if blueprint.identity_propagation is not None:
        outcomes = list(blueprint.identity_propagation.outcomes or [])
    blocked = [o for o in outcomes if o.classification == "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"]
    # F2: multiset equality — duplicate refs must be satisfied by equally many
    # indistinguishable outcomes (set semantics could over-verify). Ordering is
    # irrelevant; multiplicity is exact. No stable outcome IDs are invented.
    ref_counts = Counter((r.rule, r.classification, r.source) for r in refs)
    out_counts = Counter((o.rule, o.classification, o.source) for o in blocked)
    return ref_counts == out_counts


def build_decision_context(
    decision: AuthorDecision,
    identity: StoryIdentity,
    blueprint: StoryBlueprint,
) -> DecisionContext:
    """Resolve the decision's explicit references; fail closed on any mismatch."""
    constraints: list[ResolvedConstraint] = []
    for constraint_ref in decision.hard_constraints:
        text = _resolve_identity_ref(identity, constraint_ref.ref)
        if constraint_ref.snapshot is not None and constraint_ref.snapshot != text:
            raise DecisionValidationError(
                f"constraint snapshot mismatch for {constraint_ref.ref}: "
                f"artifact says {constraint_ref.snapshot!r}, accepted Identity has {text!r}"
            )
        constraints.append(ResolvedConstraint(constraint_ref.ref, text))

    refs = list(decision.blocked_provenance.outcome_refs)
    verified = _verify_blocked_provenance(blueprint, refs)
    if not verified:
        raise DecisionValidationError(
            f"blocked provenance mismatch: artifact references {len(refs)} blocked "
            f"outcome(s); the current Blueprint must contain exactly those blocked outcomes"
        )

    resolved_defaults: dict[str, Any] = {}
    for dref in decision.default_references:
        resolved_defaults[dref.default_id] = _resolve_default(blueprint, dref.default_id)

    resolved_bindings: list[ResolvedBinding] = []
    for b in decision.alternative_bindings:
        for r in b.references:
            entity = _resolve_entity_ref(identity, blueprint, r.entity_ref)
            resolved_bindings.append(ResolvedBinding(b.alternative_id, r.entity_ref, r.relationship, entity))

    return DecisionContext(
        decision=decision,
        constraints=constraints,
        blocked_count=len(refs),
        blocked_provenance_verified=verified,
        resolved_defaults=resolved_defaults,
        identity=identity,
        blueprint=blueprint,
        resolved_bindings=resolved_bindings,
    )
