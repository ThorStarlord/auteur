"""Bible audit — deterministic lore drift detection across chapter events.

Slice 2 (data model) + Slice 3 (location teleportation detector).

NOTE (ADR 003): This module is a *temporary resident* of ``auteur.structure``.
It operates on the StoryBible event log (Layer 6 carrier state), not on the
StoryBlueprint, and therefore does not logically belong here.  It will move
once ``DiagnosticLayer``, ``DiagnosticSeverity``, and ``RepairOptions`` are
extracted from ``auteur.structure.diagnostics`` to a shared location reachable
from both the structure engine and a future ``auteur.audit`` (or equivalent)
package.  See ``docs/adr/003-bible-audit-placement.md`` for the preconditions.
``BibleAuditDiagnostic`` is intentionally excluded from ``auteur.structure``
public exports.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from auteur.bible import StoryBible
from auteur.structure.diagnostics import (
    DiagnosticLayer,
    DiagnosticSeverity,
    RepairOptions,
)


class BibleAuditDiagnostic(BaseModel):
    """A single finding from a Bible audit pass.

    Follows the same shape as StructureDiagnostic but targets carrier-level
    (Layer 6) state inconsistencies across chapter events rather than
    within-blueprint coherence.
    """

    severity: DiagnosticSeverity
    layer: DiagnosticLayer
    rule: str
    message: str
    evidence: list[str] = Field(default_factory=list)
    repair_options: RepairOptions = Field(default_factory=RepairOptions)
    genre_recommendation_flow: dict[str, object] | None = None


def audit_bible_locations(bible: StoryBible) -> list[BibleAuditDiagnostic]:
    """Detect location teleportation across consecutive Bible events.

    A teleportation occurs when the "before" location in event N's delta
    does not match the character's last known "after" location from a prior
    event.  When they match, the delta itself records the transition — the
    move is explained and no diagnostic is emitted.

    Returns one BibleAuditDiagnostic per character per teleportation.
    """
    diagnostics: list[BibleAuditDiagnostic] = []
    events: list[dict] = bible.data.get("events", [])

    # Track the last known "after" location per character across events.
    last_location: dict[str, tuple[str, int]] = {}  # char -> (location, event_index)

    for i, event in enumerate(events):
        deltas: dict = event.get("deltas", {})
        changes: list[dict] = deltas.get("character_state_changes", [])

        for change in changes:
            if change.get("field") != "location":
                continue

            character: str = change["character"]
            before: str | None = change.get("before")
            after: str | None = change.get("after")

            if after is None:
                continue

            if character not in last_location:
                # First appearance — record and continue.
                last_location[character] = (after, i)
                continue

            prev_location, prev_event_idx = last_location[character]

            # A teleportation occurs when the "before" in this event does not
            # match the character's last known "after" from a prior event.
            # If they match, the event's delta itself records the transition —
            # the move is explained and no diagnostic is emitted.
            if before != prev_location:
                diagnostics.append(
                    BibleAuditDiagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        layer=DiagnosticLayer.CARRIERS,
                        rule="carriers.location_teleportation",
                        message=(
                            f"Character '{character}' was last at "
                            f"'{prev_location}' (event {prev_event_idx + 1}) "
                            f"but appears at '{after}' in event {i + 1} "
                            f"with no intermediate transition explaining the move."
                        ),
                        evidence=[
                            f"event[{prev_event_idx}].character_state_changes: "
                            f"{character} after = {prev_location}",
                            f"event[{i}].character_state_changes: "
                            f"{character} before = {before}, after = {after}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                f"Add a transition scene between chapter "
                                f"{prev_event_idx + 1} and {i + 1} explaining "
                                f"the move from {prev_location} to {after}."
                            ],
                            challenge_intent=[
                                f"Revise chapter {i + 1} to place {character} "
                                f"at {prev_location} instead of {after}, "
                                f"or add an intermediate chapter."
                            ],
                        ),
                    )
                )

            # Update to the latest known location.
            last_location[character] = (after, i)

    return diagnostics


from auteur.structure.diagnostics import StructureDiagnostic


def as_structure_diagnostic(bible_diag: BibleAuditDiagnostic) -> StructureDiagnostic:
    """Adapt a BibleAuditDiagnostic to the StructureDiagnostic shape."""
    return StructureDiagnostic(
        severity=bible_diag.severity,
        layer=bible_diag.layer,
        rule=bible_diag.rule,
        message=bible_diag.message,
        evidence=bible_diag.evidence,
        repair_options=bible_diag.repair_options or RepairOptions(),
        genre_recommendation_flow=bible_diag.genre_recommendation_flow,
    )

