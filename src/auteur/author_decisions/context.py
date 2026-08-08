"""Thin context projection (M2) for author decisions.

Resolves ONLY explicitly referenced material: constraint refs against the accepted
Identity, blocked-provenance refs and default references against the current
Blueprint. The builder is deliberately NOT "helpful": it never searches for
semantically related information, and it fails closed on any unresolvable or
mismatched reference. Nothing is copied unless a golden-rubric item requires it.
"""
from __future__ import annotations

import re
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


class DecisionContext:
    """The thin resolved context; carries only what the decision references."""

    def __init__(
        self,
        decision: AuthorDecision,
        constraints: list[ResolvedConstraint],
        blocked_count: int,
        blocked_provenance_verified: bool,
        resolved_defaults: dict[str, Any],
    ) -> None:
        self.decision = decision
        self.constraints = constraints
        self.blocked_count = blocked_count
        self.blocked_provenance_verified = blocked_provenance_verified
        self.resolved_defaults = resolved_defaults

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


def _verify_blocked_provenance(blueprint: StoryBlueprint, refs) -> bool:
    outcomes = []
    if blueprint.identity_propagation is not None:
        outcomes = list(blueprint.identity_propagation.outcomes or [])
    blocked = [o for o in outcomes if o.classification == "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"]
    if len(blocked) != len(refs):
        return False
    for ref in refs:
        if not any(
            o.rule == ref.rule and o.classification == ref.classification and o.source == ref.source
            for o in blocked
        ):
            return False
    return True


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

    return DecisionContext(
        decision=decision,
        constraints=constraints,
        blocked_count=len(refs),
        blocked_provenance_verified=verified,
        resolved_defaults=resolved_defaults,
    )