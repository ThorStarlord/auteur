"""Universe-to-Series constraint validation (ADR 013)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from auteur.series.continuity_validators import ValidationDiagnostic
from auteur.universe.constraints import ConstraintEnforcement, ConstraintType

if TYPE_CHECKING:
    from auteur.series.models import SeriesIdentity
    from auteur.universe.constraints import StructuredConstraint
    from auteur.universe.models import UniverseIdentity


class UniverseToSeriesValidator:
    """Validates that Series respects Universe constraints (ADR 013)."""

    def validate(self, series: SeriesIdentity, universe: UniverseIdentity, constraints: list[StructuredConstraint]) -> list[ValidationDiagnostic]:
        """Check that Series does not violate Universe constraints.

        Structured constraints (DETERMINISTIC) produce ERROR diagnostics if violated.
        Natural-language principles (ADVISORY) produce WARNING diagnostics.
        """
        diagnostics: list[ValidationDiagnostic] = []

        for constraint in constraints:
            if constraint.type == ConstraintType.GENRE_RULE:
                diagnostics.extend(self._validate_genre_constraint(series, constraint))
            elif constraint.type == ConstraintType.THEMATIC_INVARIANT:
                diagnostics.extend(self._validate_thematic_constraint(series, constraint))
            elif constraint.type == ConstraintType.CHARACTER_STATE:
                diagnostics.extend(self._validate_character_constraint(series, constraint))
            elif constraint.type == ConstraintType.RELATIONSHIP_RULE:
                diagnostics.extend(self._validate_relationship_constraint(series, constraint))

        return diagnostics

    def _validate_genre_constraint(
        self, series: SeriesIdentity, constraint: StructuredConstraint
    ) -> list[ValidationDiagnostic]:
        """Validate genre rule: allowed_values must include all series book genres."""
        diagnostics: list[ValidationDiagnostic] = []
        allowed_genres = constraint.schema.get("allowed_values", [])

        for book in series.book_plans:
            book_genre = book.story_type.genre.value if hasattr(book.story_type, "genre") else None
            if book_genre and book_genre not in allowed_genres:
                severity = "ERROR" if constraint.enforcement == ConstraintEnforcement.DETERMINISTIC else "WARNING"
                diagnostics.append(
                    ValidationDiagnostic(
                        id=f"UNIVERSE_GENRE_VIOLATION_{constraint.id}",
                        severity=severity,
                        constraint=constraint.description,
                        source=f"universe:{constraint.id}",
                        conflict=f"Book {book.book_number} has genre '{book_genre}', not in allowed: {allowed_genres}",
                        conflict_source=f"series_identity.yaml:book_plans[{book.book_number-1}].story_type",
                        explanation=f"Universe rule '{constraint.description}' restricts genres to {allowed_genres}, but Book {book.book_number} uses '{book_genre}'. Options: (1) Change book genre, (2) Modify universe constraint if series-wide genre shift is intentional.",
                    )
                )

        return diagnostics

    def _validate_thematic_constraint(
        self, series: SeriesIdentity, constraint: StructuredConstraint
    ) -> list[ValidationDiagnostic]:
        """Validate thematic invariant: must_appear_in books should have this theme."""
        diagnostics: list[ValidationDiagnostic] = []
        theme_name = constraint.schema.get("thematic_arc", "")
        must_appear = constraint.schema.get("must_appear_in", [])

        # Check if theme exists in series
        theme_found = False
        for arc in series.thematic_arcs:
            if theme_name.lower() in arc.theme.lower():
                theme_found = True
                # Verify it appears in required books
                for book_num in must_appear:
                    if book_num not in arc.books:
                        severity = "ERROR" if constraint.enforcement == ConstraintEnforcement.DETERMINISTIC else "WARNING"
                        diagnostics.append(
                            ValidationDiagnostic(
                                id=f"UNIVERSE_THEMATIC_VIOLATION_{constraint.id}",
                                severity=severity,
                                constraint=constraint.description,
                                source=f"universe:{constraint.id}",
                                conflict=f"Theme '{theme_name}' required in Book {book_num} but arc {arc.id} excludes it",
                                conflict_source=f"series_identity.yaml:thematic_arcs",
                                explanation=f"Universe rule requires theme '{theme_name}' to appear in Book {book_num}, but it's not included. Add Book {book_num} to the arc's books list.",
                            )
                        )

        if not theme_found and must_appear:
            severity = "ERROR" if constraint.enforcement == ConstraintEnforcement.DETERMINISTIC else "WARNING"
            diagnostics.append(
                ValidationDiagnostic(
                    id=f"UNIVERSE_THEME_MISSING_{constraint.id}",
                    severity=severity,
                    constraint=constraint.description,
                    source=f"universe:{constraint.id}",
                    conflict=f"Required theme '{theme_name}' not found in series thematic_arcs",
                    conflict_source="series_identity.yaml",
                    explanation=f"Universe rule requires theme '{theme_name}', but the series has no matching thematic arc. Add a thematic_arc with this theme and include the required books.",
                )
            )

        return diagnostics

    def _validate_character_constraint(
        self, series: SeriesIdentity, constraint: StructuredConstraint
    ) -> list[ValidationDiagnostic]:
        """Validate character state constraint."""
        # Simplified: check that required character states exist
        diagnostics: list[ValidationDiagnostic] = []
        required_char = constraint.schema.get("character", "")
        required_state = constraint.schema.get("must_be", "")

        if not required_char:
            return diagnostics

        char_found = False
        for state in series.character_states:
            if state.character_id.lower() == required_char.lower():
                char_found = True
                # Check if required state is in any of the character's states
                state_found = any(v == required_state for v in state.state.values())
                if not state_found:
                    severity = "ERROR" if constraint.enforcement == ConstraintEnforcement.DETERMINISTIC else "WARNING"
                    diagnostics.append(
                        ValidationDiagnostic(
                            id=f"UNIVERSE_CHARACTER_VIOLATION_{constraint.id}",
                            severity=severity,
                            constraint=constraint.description,
                            source=f"universe:{constraint.id}",
                            conflict=f"Character '{required_char}' must be '{required_state}' but is not",
                            conflict_source=f"series_identity.yaml:character_states",
                            explanation=f"Universe rule requires '{required_char}' to have state '{required_state}'. Update character state entries.",
                        )
                    )

        if not char_found:
            severity = "ERROR" if constraint.enforcement == ConstraintEnforcement.DETERMINISTIC else "WARNING"
            diagnostics.append(
                ValidationDiagnostic(
                    id=f"UNIVERSE_CHARACTER_MISSING_{constraint.id}",
                    severity=severity,
                    constraint=constraint.description,
                    source=f"universe:{constraint.id}",
                    conflict=f"Required character '{required_char}' not found in series",
                    conflict_source="series_identity.yaml",
                    explanation=f"Universe rule references character '{required_char}', who is not tracked in character_states. Add this character.",
                )
            )

        return diagnostics

    def _validate_relationship_constraint(
        self, series: SeriesIdentity, constraint: StructuredConstraint
    ) -> list[ValidationDiagnostic]:
        """Validate relationship rule."""
        diagnostics: list[ValidationDiagnostic] = []
        party_a = constraint.schema.get("party_a", "")
        party_b = constraint.schema.get("party_b", "")
        required_state = constraint.schema.get("must_be", "")

        if not (party_a and party_b and required_state):
            return diagnostics

        rel_found = False
        for rel in series.relationships:
            if {rel.party_a, rel.party_b} == {party_a, party_b}:
                rel_found = True
                if rel.state != required_state:
                    severity = "ERROR" if constraint.enforcement == ConstraintEnforcement.DETERMINISTIC else "WARNING"
                    diagnostics.append(
                        ValidationDiagnostic(
                            id=f"UNIVERSE_RELATIONSHIP_VIOLATION_{constraint.id}",
                            severity=severity,
                            constraint=constraint.description,
                            source=f"universe:{constraint.id}",
                            conflict=f"Relationship {party_a}-{party_b} must be '{required_state}' but is '{rel.state}'",
                            conflict_source=f"series_identity.yaml:relationships",
                            explanation=f"Universe rule requires {party_a} and {party_b} to be '{required_state}'. Update the relationship state.",
                        )
                    )

        if not rel_found:
            severity = "ERROR" if constraint.enforcement == ConstraintEnforcement.DETERMINISTIC else "WARNING"
            diagnostics.append(
                ValidationDiagnostic(
                    id=f"UNIVERSE_RELATIONSHIP_MISSING_{constraint.id}",
                    severity=severity,
                    constraint=constraint.description,
                    source=f"universe:{constraint.id}",
                    conflict=f"Required relationship {party_a}-{party_b} not found in series",
                    conflict_source="series_identity.yaml",
                    explanation=f"Universe rule requires a relationship between {party_a} and {party_b}. Add this relationship to relationships.",
                )
            )

        return diagnostics


def validate_series_against_universe(
    series: SeriesIdentity, universe: UniverseIdentity, constraints: list[StructuredConstraint] | None = None
) -> list[ValidationDiagnostic]:
    """Validate that a Series respects its Universe constraints (ADR 013).

    Args:
        series: The SeriesIdentity to validate
        universe: The UniverseIdentity (for context)
        constraints: List of StructuredConstraint objects; if None, skips validation

    Returns:
        List of ValidationDiagnostic objects (empty if no constraints or no violations)
    """
    if not constraints:
        return []

    validator = UniverseToSeriesValidator()
    return validator.validate(series, universe, constraints)
