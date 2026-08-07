"""Bounded deterministic identity-to-structure propagation.

Implements the approved design
(``docs/design/identity-structure-bounded-propagation.md``):

- A1/A3 contract propagation: ``StoryIdentity.not_this`` and
  ``StoryIdentity.rejected_directions`` are appended verbatim to
  ``AuthorAudienceContract.custom_rules`` (never ``forbidden_tropes``), with
  exact-match deduplication, deterministic ordering, a conflict refusal, and
  lightweight provenance.
- A4 safe explicit naming (slice 2).
- B1 role consistency (slice 3).

Hard invariants: no text extraction, no invented names/roles/arcs, no
wall-clock timestamps, no mutation of the identity, and
``StoryIdentity.author_overrides`` is never propagated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from auteur.blueprint import (
    AuthorAudienceContract,
    CharacterRole,
    IdentityPropagationDerivation,
    PropagationOutcome,
    StoryBlueprint,
)

if TYPE_CHECKING:
    from auteur.identity import IdentityCharacter, StoryIdentity

# Outcome classifications (frozen vocabulary from the approved design).
DIRECT_DETERMINISTIC = "DIRECT_DETERMINISTIC"
BLOCKED_INSUFFICIENT_EXPLICIT_INPUT = "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT"

# Frozen compiler placeholder names (case-insensitive) produced by the
# character seeder in compile_to_blueprint. The approved design's frozen
# placeholder set {protagonist, antagonist, lover a, lover b} enumerates the
# placeholder KINDS; "Detective"/"Culprit" are the mystery genre's concrete
# seeded instances of the protagonist/antagonist kinds, and "Lover A"/"Lover B"
# the romance genre's. Propagation runs only on freshly compiled blueprints,
# so these names can only refer to seeded slots, never authored content.
PLACEHOLDER_NAMES = frozenset(
    {"protagonist", "antagonist", "detective", "culprit", "lover a", "lover b"}
)


def _is_placeholder_name(name: str) -> bool:
    return name.casefold() in PLACEHOLDER_NAMES


def _normalize_conflict(value: str) -> str:
    """Normalized form used only for the expected/custom conflict check."""
    return value.casefold().strip()


def _append_verbatim(
    contract: AuthorAudienceContract,
    items: list[str],
    *,
    source_field: str,
    outcomes: list[PropagationOutcome],
) -> None:
    """Append free-text items verbatim into ``contract.custom_rules``.

    - Exact-match (case-sensitive) deduplication against existing destination
      values and against items already appended in this pass.
    - Whitespace-only items are skipped (they carry no rule semantics).
    - A conflict with ``expected_elements`` (same casefolded/stripped value in
      both lists) is refused with a BLOCKED outcome; the item remains — the
      author resolves it, nothing is removed.
    """
    seen = set(contract.custom_rules)
    for index, item in enumerate(items):
        if not item.strip():
            continue
        if item in seen:
            continue
        seen.add(item)
        contract.custom_rules.append(item)
        destination_index = len(contract.custom_rules) - 1
        outcomes.append(
            PropagationOutcome(
                rule=f"identity.{source_field}.custom_rules",
                classification=DIRECT_DETERMINISTIC,
                destination=f"contract.custom_rules[{destination_index}]",
                value=item,
                source=f"{source_field}[{index}]",
            )
        )
        if any(
            _normalize_conflict(item) == _normalize_conflict(expected)
            for expected in contract.expected_elements
        ):
            outcomes.append(
                PropagationOutcome(
                    rule="identity.propagation.contract.conflict",
                    classification=BLOCKED_INSUFFICIENT_EXPLICIT_INPUT,
                    destination=f"contract.custom_rules[{destination_index}]",
                    value=item,
                    source=f"{source_field}[{index}]",
                    reason=(
                        "The same normalized value appears in both expected_elements "
                        "and custom_rules; the author must resolve the conflict "
                        "(AUTHOR_DECISION_REQUIRED)."
                    ),
                )
            )


def apply_contract_propagation(
    identity: StoryIdentity,
    contract: AuthorAudienceContract,
    outcomes: list[PropagationOutcome],
) -> None:
    """Propagate ``not_this`` then ``rejected_directions`` into ``custom_rules``.

    Source field order is preserved; identity items are appended after any
    existing (profile-derived) items in input list order. ``author_overrides``
    is deliberately not read here — it is a workflow/compiler control field.
    """
    _append_verbatim(
        contract,
        identity.not_this,
        source_field="not_this",
        outcomes=outcomes,
    )
    _append_verbatim(
        contract,
        identity.rejected_directions,
        source_field="rejected_directions",
        outcomes=outcomes,
    )


def apply_character_naming(
    identity: StoryIdentity,
    blueprint: StoryBlueprint,
    outcomes: list[PropagationOutcome],
) -> None:
    """A4: name placeholder slots from explicit ``structural_role`` declarations.

    - An entry with an explicit ``structural_role`` names the unique blueprint
      slot with that role whose current name is a compiler placeholder.
    - Two declared entries claiming the same role -> BLOCKED, no naming for
      that role.
    - An entry without ``structural_role`` -> no naming. Unnamed entities are
      never invented.
    - Naming never depends on ``arc_type``.
    """
    role_counts: dict[CharacterRole, int] = {}
    for declared in identity.characters:
        if declared.structural_role is not None:
            role_counts[declared.structural_role] = role_counts.get(declared.structural_role, 0) + 1

    for index, declared in enumerate(identity.characters):
        if declared.structural_role is None:
            continue
        if role_counts[declared.structural_role] > 1:
            outcomes.append(
                PropagationOutcome(
                    rule="identity.propagation.naming.ambiguous",
                    classification=BLOCKED_INSUFFICIENT_EXPLICIT_INPUT,
                    source=f"characters[{index}].structural_role",
                    value=declared.name,
                    reason=(
                        f"Multiple declared entries claim structural_role="
                        f"{declared.structural_role.value}; no naming applied "
                        "(AUTHOR_DECISION_REQUIRED)."
                    ),
                )
            )
            continue

        matching_slots = [
            (slot_index, slot)
            for slot_index, slot in enumerate(blueprint.characters)
            if slot.role == declared.structural_role and _is_placeholder_name(slot.name)
        ]
        if not matching_slots:
            # No compiler placeholder slot with that role: restraint, no trace.
            continue
        if len(matching_slots) > 1:
            outcomes.append(
                PropagationOutcome(
                    rule="identity.propagation.naming.ambiguous",
                    classification=BLOCKED_INSUFFICIENT_EXPLICIT_INPUT,
                    source=f"characters[{index}].structural_role",
                    value=declared.name,
                    reason=(
                        f"More than one blueprint slot with role "
                        f"{declared.structural_role.value} is a compiler placeholder; "
                        "no naming applied."
                    ),
                )
            )
            continue

        slot_index, slot = matching_slots[0]
        if slot.name == declared.name:
            # Already represented: restraint, no trace (the case-1 guard).
            continue
        slot.name = declared.name
        outcomes.append(
            PropagationOutcome(
                rule=f"identity.naming.{declared.structural_role.value}",
                classification=DIRECT_DETERMINISTIC,
                destination=f"characters[{slot_index}].name",
                value=declared.name,
                source=f"characters[{index}].name",
            )
        )


def apply_role_rule(
    identity: StoryIdentity,
    blueprint: StoryBlueprint,
    outcomes: list[PropagationOutcome],
) -> None:
    """B1: role consistency for declared transformation subjects.

    The five decision stages from the approved design (structured form):

    - Stage 0: no entry with ``undergoes_central_change=True`` -> NOT_APPLICABLE
      (no action, no trace).
    - Stage 1: a subject explicitly framed as opposition
      (``structural_role == ANTAGONIST``) is never recast (NOT_APPLICABLE).
    - Stage 2: a subject already represented by a blueprint slot (name match on
      a non-antagonist slot, or a slot matching the declared role) is restraint.
    - Stage 3: ambiguity (multiple remaining subjects, or no eligible
      placeholder target) -> BLOCKED_INSUFFICIENT_EXPLICIT_INPUT, no mutation.
    - Stage 4: exactly one unambiguous subject, a contradictory compiler
      placeholder slot, and an EXPLICITLY declared ``arc_type`` ->
      deterministic correction (name/role/arc, 0-100). No arc is ever invented.
    - Stage 4a: correction without a declared arc -> BLOCKED, no mutation.
    - Stage 5: the contradictory slot is authored (non-placeholder) -> BLOCKED
      (AUTHOR_DECISION_REQUIRED), never silently overwritten.
    """
    subjects = [c for c in identity.characters if c.undergoes_central_change is True]
    if not subjects:
        return  # Stage 0: no explicit transformation commitment.

    # Stage 1: opposition precedence — a changing explicit opponent is not recast.
    candidates = [
        (index, subject)
        for index, subject in enumerate(identity.characters)
        if subject.undergoes_central_change is True
        and subject.structural_role != CharacterRole.ANTAGONIST
    ]

    # Stage 2: already represented — restraint, no action.
    remaining: list[tuple[int, IdentityCharacter]] = []
    for index, subject in candidates:
        represented = any(
            slot.name == subject.name
            and (slot.role != CharacterRole.ANTAGONIST or slot.role == subject.structural_role)
            for slot in blueprint.characters
        )
        if not represented:
            remaining.append((index, subject))

    if not remaining:
        return  # all candidates already represented: NOT_APPLICABLE, no trace.

    # Stage 3: ambiguity — more than one transformation subject claims correction.
    if len(remaining) > 1:
        for index, subject in remaining:
            outcomes.append(
                PropagationOutcome(
                    rule="identity.propagation.role_rule.ambiguous_subject",
                    classification=BLOCKED_INSUFFICIENT_EXPLICIT_INPUT,
                    source=f"characters[{index}].undergoes_central_change",
                    value=subject.name,
                    reason=(
                        "Multiple declared transformation subjects; no single "
                        "unambiguous correspondence exists (BLOCKED, no mutation)."
                    ),
                )
            )
        return

    index, subject = remaining[0]
    eligible = [
        (slot_index, slot)
        for slot_index, slot in enumerate(blueprint.characters)
        if slot.role == CharacterRole.ANTAGONIST and _is_placeholder_name(slot.name)
    ]

    if not eligible:
        authored_contradiction = any(
            slot.role == CharacterRole.ANTAGONIST and not _is_placeholder_name(slot.name)
            for slot in blueprint.characters
        )
        if authored_contradiction:
            # Stage 5: the contradictory slot is authored — author decision path.
            outcomes.append(
                PropagationOutcome(
                    rule="identity.propagation.role_contradiction.unresolved",
                    classification=BLOCKED_INSUFFICIENT_EXPLICIT_INPUT,
                    source=f"characters[{index}]",
                    value=subject.name,
                    reason=(
                        "The contradictory blueprint slot is authored, not a compiler "
                        "placeholder; no automatic recast (AUTHOR_DECISION_REQUIRED)."
                    ),
                )
            )
            return
        # Stage 3: no eligible placeholder slot exists.
        outcomes.append(
            PropagationOutcome(
                rule="identity.propagation.role_rule.ambiguous_subject",
                classification=BLOCKED_INSUFFICIENT_EXPLICIT_INPUT,
                source=f"characters[{index}].undergoes_central_change",
                value=subject.name,
                reason=(
                    "No eligible compiler placeholder slot exists for the declared "
                    "transformation subject (BLOCKED, no mutation)."
                ),
            )
        )
        return

    if len(eligible) > 1:
        outcomes.append(
            PropagationOutcome(
                rule="identity.propagation.role_rule.ambiguous_subject",
                classification=BLOCKED_INSUFFICIENT_EXPLICIT_INPUT,
                source=f"characters[{index}].undergoes_central_change",
                value=subject.name,
                reason=(
                    "More than one eligible placeholder slot exists; correspondence "
                    "is ambiguous (BLOCKED, no mutation)."
                ),
            )
        )
        return

    if subject.arc_type is None:
        # Stage 4a: atomicity — no name/role mutation without a defensible arc.
        outcomes.append(
            PropagationOutcome(
                rule="identity.propagation.role_rule.arc_undeclared",
                classification=BLOCKED_INSUFFICIENT_EXPLICIT_INPUT,
                source=f"characters[{index}].arc_type",
                value=subject.name,
                reason=(
                    "Correction requires an explicitly declared arc_type; none was "
                    "provided, so no name/role mutation was applied "
                    "(AUTHOR_DECISION_REQUIRED)."
                ),
            )
        )
        return

    # Stage 4: bounded deterministic correction of the placeholder slot.
    slot_index, slot = eligible[0]
    slot.name = subject.name
    slot.role = subject.structural_role or CharacterRole.DEUTERAGONIST
    slot.arc_type = subject.arc_type
    slot.arc_start_percentage = 0
    slot.arc_end_percentage = 100
    outcomes.append(
        PropagationOutcome(
            rule="identity.role_rule.correction",
            classification=DIRECT_DETERMINISTIC,
            destination=f"characters[{slot_index}]",
            value=subject.name,
            source=f"characters[{index}]",
        )
    )


def propagate_identity(
    identity: StoryIdentity,
    blueprint: StoryBlueprint,
) -> IdentityPropagationDerivation | None:
    """Run all identity-to-structure propagation rules on a fresh blueprint.

    Returns ``None`` when no outcome (applied or blocked) occurred — inert
    identities leave no trace, keeping their blueprints unchanged. Restraint
    (NOT_APPLICABLE) outcomes are never recorded.
    """
    outcomes: list[PropagationOutcome] = []
    apply_contract_propagation(identity, blueprint.contract, outcomes)
    apply_character_naming(identity, blueprint, outcomes)
    apply_role_rule(identity, blueprint, outcomes)
    if not outcomes:
        return None
    return IdentityPropagationDerivation(outcomes=outcomes)
