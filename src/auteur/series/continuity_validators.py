"""Continuity validators for Series narratives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from auteur.series.models import (
    CharacterState,
    LoreEntry,
    NarrativeSetup,
    Relationship,
    SeriesIdentity,
    ThematicArc,
    TimelineEvent,
)


@dataclass
class ValidationDiagnostic:
    """A single validation finding."""

    id: str
    severity: str  # "ERROR", "WARNING", "INFO"
    constraint: str
    source: str
    conflict: str
    conflict_source: str
    explanation: str
    lsm_context: dict[str, Any] | None = None


class ThematicProgressionValidator:
    """Validates that thematic arcs progress consistently across books."""

    def validate(self, series: SeriesIdentity) -> list[ValidationDiagnostic]:
        """Check thematic progression rules."""
        diagnostics: list[ValidationDiagnostic] = []
        total_books = len(series.book_plans)

        for arc in series.thematic_arcs:
            # Validate that progression develops sequentially
            prev_state = None
            for book in sorted(arc.progression.keys()):
                state = arc.progression[book]
                if book > total_books:
                    diagnostics.append(
                        ValidationDiagnostic(
                            id="THEMATIC_BOOK_OUT_OF_RANGE",
                            severity="ERROR",
                            constraint=f"Thematic arc {arc.id} book range",
                            source=f"thematic_arcs[{arc.id}].progression[{book}]",
                            conflict=f"Book {book} exceeds series total ({total_books})",
                            conflict_source="series_identity.yaml",
                            explanation=f"Thematic arc references book {book} but series only has {total_books} books.",
                        )
                    )

            # Check that arcs introduced must progress
            if arc.books:
                first_book = min(arc.books)
                if first_book in arc.progression:
                    first_state = arc.progression[first_book]
                    if first_state == "introduces":
                        # Must have deepens or resolves in later books
                        has_continuation = any(
                            arc.progression.get(b) in ("deepens", "resolves") for b in arc.books if b > first_book
                        )
                        if not has_continuation:
                            diagnostics.append(
                                ValidationDiagnostic(
                                    id="THEMATIC_ARC_NOT_DEVELOPED",
                                    severity="WARNING",
                                    constraint=f"Thematic arc must progress: {arc.theme}",
                                    source=f"thematic_arcs[{arc.id}]",
                                    conflict=f"Arc introduced in book {first_book} but not developed in later books",
                                    conflict_source="series_identity.yaml",
                                    explanation=f"Theme '{arc.theme}' is introduced in Book {first_book} but is not deepened or resolved in later books. Consider: (1) Add deepens/resolves entries to progression, (2) Remove theme if not central to series.",
                                )
                            )

                        # Check for gaps in progression
                        for book_num in sorted(arc.books)[:-1]:
                            if book_num not in arc.progression:
                                next_book = next((b for b in sorted(arc.books) if b > book_num), None)
                                if next_book:
                                    diagnostics.append(
                                        ValidationDiagnostic(
                                            id="THEMATIC_PROGRESSION_GAP",
                                            severity="WARNING",
                                            constraint=f"Thematic arc continuity: {arc.theme}",
                                            source=f"thematic_arcs[{arc.id}].progression",
                                            conflict=f"No progression entry for book {book_num}, but arc continues in book {next_book}",
                                            conflict_source="series_identity.yaml",
                                            explanation=f"Thematic arc '{arc.theme}' skips Book {book_num} in progression. Add an entry (e.g., 'continues' or 'develops') for continuity.",
                                        )
                                    )

        return diagnostics


class CharacterContinuityValidator:
    """Validates character states across books."""

    def validate(self, series: SeriesIdentity) -> list[ValidationDiagnostic]:
        """Check character continuity rules."""
        diagnostics: list[ValidationDiagnostic] = []
        total_books = len(series.book_plans)

        # Group states by character
        chars_by_id = {}
        for state in series.character_states:
            if state.book > total_books:
                diagnostics.append(
                    ValidationDiagnostic(
                        id="CHARACTER_STATE_BOOK_OUT_OF_RANGE",
                        severity="ERROR",
                        constraint=f"Character {state.character_id} exists in series",
                        source=f"character_states[book={state.book}]",
                        conflict=f"Book {state.book} exceeds series total ({total_books})",
                        conflict_source="series_identity.yaml",
                        explanation=f"Character state references book {state.book} but series only has {total_books} books.",
                    )
                )
                continue

            if state.character_id not in chars_by_id:
                chars_by_id[state.character_id] = []
            chars_by_id[state.character_id].append(state)

        # Validate consistency across books for each character
        for char_id, states in chars_by_id.items():
            sorted_states = sorted(states, key=lambda s: s.book)
            first_state = sorted_states[0].state

            # Check that state fields remain consistent
            for i, state in enumerate(sorted_states[1:], start=1):
                prev_state = sorted_states[i - 1].state
                # Warn if new keys appear unexpectedly
                new_keys = set(state.state.keys()) - set(prev_state.keys())
                if new_keys:
                    diagnostics.append(
                        ValidationDiagnostic(
                            id="CHARACTER_STATE_NEW_FIELDS",
                            severity="WARNING",
                            constraint=f"Character {char_id} state field consistency",
                            source=f"character_states[{char_id}, book={state.book}]",
                            conflict=f"New fields introduced: {new_keys}",
                            conflict_source="series_identity.yaml",
                            explanation=f"Character '{char_id}' gains new state fields in Book {state.book}: {new_keys}. Document why these fields were added (e.g., new knowledge, new relationships).",
                        )
                    )

        return diagnostics


class RelationshipContinuityValidator:
    """Validates relationship states across books."""

    def validate(self, series: SeriesIdentity) -> list[ValidationDiagnostic]:
        """Check relationship continuity rules."""
        diagnostics: list[ValidationDiagnostic] = []
        total_books = len(series.book_plans)

        # Group relationships by (party_a, party_b)
        rels_by_pair = {}
        for rel in series.relationships:
            if rel.book > total_books:
                diagnostics.append(
                    ValidationDiagnostic(
                        id="RELATIONSHIP_BOOK_OUT_OF_RANGE",
                        severity="ERROR",
                        constraint=f"Relationship {rel.id} exists in series",
                        source=f"relationships[{rel.id}, book={rel.book}]",
                        conflict=f"Book {rel.book} exceeds series total ({total_books})",
                        conflict_source="series_identity.yaml",
                        explanation=f"Relationship references book {rel.book} but series only has {total_books} books.",
                    )
                )
                continue

            pair = (min(rel.party_a, rel.party_b), max(rel.party_a, rel.party_b))
            if pair not in rels_by_pair:
                rels_by_pair[pair] = []
            rels_by_pair[pair].append(rel)

        # Check state transitions
        for (party_a, party_b), rels in rels_by_pair.items():
            sorted_rels = sorted(rels, key=lambda r: r.book)
            prev_state = None
            for i, rel in enumerate(sorted_rels):
                if i > 0:
                    prev_state = sorted_rels[i - 1].state
                    if rel.state != prev_state and not rel.notes:
                        diagnostics.append(
                            ValidationDiagnostic(
                                id="RELATIONSHIP_TRANSITION_UNJUSTIFIED",
                                severity="WARNING",
                                constraint=f"Relationship state transition for {rel.id}",
                                source=f"relationships[{rel.id}, book={rel.book}]",
                                conflict=f"State changes from '{prev_state}' to '{rel.state}' without justification",
                                conflict_source="series_identity.yaml",
                                explanation=f"Relationship between {party_a} and {party_b} transitions from '{prev_state}' to '{rel.state}' in Book {rel.book}. Add notes explaining the transition (e.g., 'conflict resolved', 'betrayal discovered').",
                            )
                        )

        return diagnostics


class LoreConsistencyValidator:
    """Validates that lore is consistent across books."""

    def validate(self, series: SeriesIdentity) -> list[ValidationDiagnostic]:
        """Check lore consistency rules."""
        diagnostics: list[ValidationDiagnostic] = []
        total_books = len(series.book_plans)

        # Group lore by id
        lore_by_id = {}
        for entry in series.lore_entries:
            if entry.book > total_books:
                diagnostics.append(
                    ValidationDiagnostic(
                        id="LORE_BOOK_OUT_OF_RANGE",
                        severity="ERROR",
                        constraint=f"Lore entry {entry.id} exists in series",
                        source=f"lore_entries[{entry.id}, book={entry.book}]",
                        conflict=f"Book {entry.book} exceeds series total ({total_books})",
                        conflict_source="series_identity.yaml",
                        explanation=f"Lore entry references book {entry.book} but series only has {total_books} books.",
                    )
                )
                continue

            if entry.id not in lore_by_id:
                lore_by_id[entry.id] = []
            lore_by_id[entry.id].append(entry)

        # Check for contradictions
        for lore_id, entries in lore_by_id.items():
            sorted_entries = sorted(entries, key=lambda e: e.book)
            prev_content = None
            for i, entry in enumerate(sorted_entries):
                if i > 0:
                    prev_content = sorted_entries[i - 1].content
                    if entry.content != prev_content and not entry.consistency_notes:
                        diagnostics.append(
                            ValidationDiagnostic(
                                id="LORE_CONTRADICTION_UNEXPLAINED",
                                severity="WARNING",
                                constraint=f"Lore consistency for {lore_id}",
                                source=f"lore_entries[{lore_id}, book={entry.book}]",
                                conflict=f"Content differs from Book {sorted_entries[i-1].book} without explanation",
                                conflict_source="series_identity.yaml",
                                explanation=f"Lore entry '{lore_id}' has different content in Book {entry.book} than Book {sorted_entries[i-1].book}. Add consistency_notes explaining the change (e.g., 'new world after spell', 'author's realization of error').",
                            )
                        )

        return diagnostics


class ChronologyValidator:
    """Validates timeline consistency."""

    def validate(self, series: SeriesIdentity) -> list[ValidationDiagnostic]:
        """Check chronology rules."""
        diagnostics: list[ValidationDiagnostic] = []
        total_books = len(series.book_plans)

        for event in series.timeline_events:
            if event.relative_book > total_books:
                diagnostics.append(
                    ValidationDiagnostic(
                        id="TIMELINE_BOOK_OUT_OF_RANGE",
                        severity="ERROR",
                        constraint=f"Timeline event {event.id} exists in series",
                        source=f"timeline_events[{event.id}].relative_book",
                        conflict=f"Book {event.relative_book} exceeds series total ({total_books})",
                        conflict_source="series_identity.yaml",
                        explanation=f"Timeline event references book {event.relative_book} but series only has {total_books} books.",
                    )
                )

        return diagnostics


class SetupPayoffValidator:
    """Validates setup and payoff tracking."""

    def validate(self, series: SeriesIdentity) -> list[ValidationDiagnostic]:
        """Check setup/payoff rules."""
        diagnostics: list[ValidationDiagnostic] = []
        total_books = len(series.book_plans)

        for setup in series.narrative_setups:
            if setup.book_introduced > total_books:
                diagnostics.append(
                    ValidationDiagnostic(
                        id="SETUP_BOOK_OUT_OF_RANGE",
                        severity="ERROR",
                        constraint=f"Narrative setup {setup.id} exists in series",
                        source=f"narrative_setups[{setup.id}].book_introduced",
                        conflict=f"Book {setup.book_introduced} exceeds series total ({total_books})",
                        conflict_source="series_identity.yaml",
                        explanation=f"Setup references book {setup.book_introduced} but series only has {total_books} books.",
                    )
                )

            if setup.expected_payoff_by_book > total_books:
                diagnostics.append(
                    ValidationDiagnostic(
                        id="SETUP_PAYOFF_BOOK_OUT_OF_RANGE",
                        severity="ERROR",
                        constraint=f"Narrative setup {setup.id} payoff deadline",
                        source=f"narrative_setups[{setup.id}].expected_payoff_by_book",
                        conflict=f"Book {setup.expected_payoff_by_book} exceeds series total ({total_books})",
                        conflict_source="series_identity.yaml",
                        explanation=f"Setup payoff deadline references book {setup.expected_payoff_by_book} but series only has {total_books} books.",
                    )
                )

            # Check for unresolved setups past deadline
            if setup.status == "unresolved" and setup.expected_payoff_by_book < total_books:
                diagnostics.append(
                    ValidationDiagnostic(
                        id="SETUP_UNRESOLVED_WARNING",
                        severity="WARNING",
                        constraint=f"Setup {setup.id} should be resolved by Book {setup.expected_payoff_by_book}",
                        source=f"narrative_setups[{setup.id}]",
                        conflict=f"Status is 'unresolved' but deadline was Book {setup.expected_payoff_by_book}; series has {total_books} books",
                        conflict_source="series_identity.yaml",
                        explanation=f"Setup '{setup.id}' was supposed to be resolved by Book {setup.expected_payoff_by_book} but is still unresolved in a {total_books}-book series. Consider: (1) Adding a payoff entry, (2) Marking as abandoned with a reason, (3) Extending the deadline.",
                    )
                )

            if setup.status == "resolved" and not setup.payoff_id:
                diagnostics.append(
                    ValidationDiagnostic(
                        id="SETUP_RESOLVED_NO_PAYOFF_ID",
                        severity="ERROR",
                        constraint=f"Resolved setup {setup.id} must reference payoff",
                        source=f"narrative_setups[{setup.id}]",
                        conflict="Status is 'resolved' but payoff_id is empty",
                        conflict_source="series_identity.yaml",
                        explanation=f"Setup '{setup.id}' is marked as resolved but has no payoff_id. Link it to a narrative_payoffs entry or change status to 'unresolved'.",
                    )
                )

            if setup.status == "abandoned" and not setup.reason_abandoned:
                diagnostics.append(
                    ValidationDiagnostic(
                        id="SETUP_ABANDONED_NO_REASON",
                        severity="WARNING",
                        constraint=f"Abandoned setup {setup.id} should document reason",
                        source=f"narrative_setups[{setup.id}]",
                        conflict="Status is 'abandoned' but reason_abandoned is empty",
                        conflict_source="series_identity.yaml",
                        explanation=f"Setup '{setup.id}' is marked as abandoned. Document why (e.g., 'not thematically relevant', 'contradicts later plot').",
                    )
                )

        return diagnostics
