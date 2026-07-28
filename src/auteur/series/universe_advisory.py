"""Advisory Universe-field diagnostics for Series (auteur#38 Decision A, Phase 2).

This module is deliberately separate from :class:`UniverseToSeriesValidator` in
``universe_integration.py``. That validator dispatches on
``StructuredConstraint.type``; ``UniverseIdentity.forbidden_elements`` is a plain
``list[str]`` advisory field with search-and-match semantics, not
constraint-type dispatch, so forcing it through that dispatch would be a
category error.

Scope: ``forbidden_elements`` only. ``required_elements`` (Phase 3) and
``cross_story_constraints`` (Phase 4) are intentionally not implemented here.
"""

from __future__ import annotations

import re
import unicodedata
from typing import TYPE_CHECKING, Sequence

from auteur.series.continuity_validators import ValidationDiagnostic

if TYPE_CHECKING:
    from auteur.series.models import SeriesIdentity

FORBIDDEN_ELEMENT_PRESENT = "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT"
FORBIDDEN_ELEMENT_UNEVALUABLE = "UNIVERSE_FORBIDDEN_ELEMENT_UNEVALUABLE"
ADVISORY_RULE_UNSUPPORTED = "UNIVERSE_ADVISORY_RULE_UNSUPPORTED"

# Repository-wide `conflict_source` convention: every ValidationDiagnostic in
# continuity_validators.py and universe_integration.py prefixes the artifact
# filename, either bare ("series_identity.yaml") or as
# "series_identity.yaml:<field path>". This module follows that convention;
# the exact matched field path required by auteur#43 is preserved verbatim
# after the ":" separator, and also appears in `conflict`/`explanation`.
SERIES_ARTIFACT = "series_identity.yaml"
UNIVERSE_ARTIFACT = "universe_identity.yaml"

_WHITESPACE_RUN = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    """Normalize a forbidden element or a Series field value for matching.

    Applies, in order: Unicode NFKC normalization, casefolding, collapsing every
    internal whitespace run to a single ASCII space, and trimming.
    """
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.casefold()
    normalized = _WHITESPACE_RUN.sub(" ", normalized)
    return normalized.strip()


def extract_searchable_fields(series: SeriesIdentity) -> list[tuple[str, str]]:
    """Return the ratified searchable ``(field_path, raw_value)`` pairs.

    Ordering is deterministic: top-level fields, global arc fields, book plans,
    thematic arcs, lore entries, recurring symbols -- each list in list order.

    ``character_arcs``, ``relationships`` and ``character_states`` are
    deliberately excluded (auteur#38 Decision A).
    """
    pairs: list[tuple[str, str]] = [
        ("title", series.title),
        ("core_question", series.core_question),
        ("global_arc.beginning", series.global_arc.beginning),
        ("global_arc.midpoint", series.global_arc.midpoint),
        ("global_arc.ending", series.global_arc.ending or ""),
    ]

    for index, book in enumerate(series.book_plans):
        pairs.append((f"book_plans[{index}].title", book.title))
        pairs.append((f"book_plans[{index}].core_answer", book.core_answer))

    for index, arc in enumerate(series.thematic_arcs):
        pairs.append((f"thematic_arcs[{index}].theme", arc.theme))

    for index, entry in enumerate(series.lore_entries):
        pairs.append((f"lore_entries[{index}].content", entry.content))

    for index, symbol in enumerate(series.recurring_symbols):
        pairs.append((f"recurring_symbols[{index}]", symbol))

    return [(path, value if value is not None else "") for path, value in pairs]


def phrase_matches(normalized_phrase: str, normalized_text: str) -> bool:
    """Whole-word/phrase contiguous match of an already-normalized phrase."""
    if not normalized_phrase:
        return False
    pattern = rf"(?<!\w){re.escape(normalized_phrase)}(?!\w)"
    return re.search(pattern, normalized_text) is not None


def validate_forbidden_elements(
    series: SeriesIdentity,
    forbidden_elements: Sequence[str],
) -> list[ValidationDiagnostic]:
    """Produce deterministic ``forbidden_elements`` diagnostics for a Series.

    Cardinality: one diagnostic per (forbidden element, matched field path).
    Repeated occurrences inside one field yield a single diagnostic.

    When every searchable field is empty or whitespace-only, one
    ``UNIVERSE_FORBIDDEN_ELEMENT_UNEVALUABLE`` diagnostic is emitted per
    (well-formed) forbidden element instead, and no PRESENT diagnostics are
    emitted.

    A forbidden element that is empty or whitespace-only after normalization is
    malformed advisory input: exactly one
    ``UNIVERSE_ADVISORY_RULE_UNSUPPORTED`` (INFO) diagnostic is emitted for it
    and it is never silently discarded, per auteur#38 Decision D. Remaining
    entries are still evaluated deterministically.
    """
    if not forbidden_elements:
        return []

    searchable = extract_searchable_fields(series)
    normalized_fields = [(path, normalize_text(value)) for path, value in searchable]
    has_searchable_text = any(text for _, text in normalized_fields)

    diagnostics: list[ValidationDiagnostic] = []

    for index, element in enumerate(forbidden_elements):
        source = f"universe:forbidden_elements[{index}]"
        normalized_element = normalize_text(element)

        # Malformed advisory input (empty or whitespace-only rule) is reported,
        # never silently discarded, per auteur#38 Decision D
        # (UNIVERSE_ADVISORY_RULE_UNSUPPORTED, INFO, non-blocking). Exactly one
        # diagnostic per malformed entry; neither PRESENT nor UNEVALUABLE is
        # emitted for it, and evaluation of the remaining entries continues.
        if not normalized_element:
            diagnostics.append(
                ValidationDiagnostic(
                    id=ADVISORY_RULE_UNSUPPORTED,
                    severity="INFO",
                    constraint=element,
                    source=source,
                    conflict="Forbidden element is empty or whitespace-only",
                    conflict_source=f"{UNIVERSE_ARTIFACT}:forbidden_elements[{index}]",
                    explanation=(
                        f"Universe forbidden_elements[{index}] is empty or whitespace-only "
                        "and cannot be processed as a forbidden-element rule. Remove the "
                        "entry or replace it with the phrase that should be forbidden."
                    ),
                    lsm_context={},
                )
            )
            continue

        if not has_searchable_text:
            diagnostics.append(
                ValidationDiagnostic(
                    id=FORBIDDEN_ELEMENT_UNEVALUABLE,
                    severity="INFO",
                    constraint=element,
                    source=source,
                    conflict="No searchable Series text is present",
                    conflict_source=SERIES_ARTIFACT,
                    explanation=(
                        f'Forbidden element "{element}" could not be evaluated: '
                        "no searchable Series text is present"
                    ),
                    lsm_context={},
                )
            )
            continue

        for path, text in normalized_fields:
            if not phrase_matches(normalized_element, text):
                continue
            diagnostics.append(
                ValidationDiagnostic(
                    id=FORBIDDEN_ELEMENT_PRESENT,
                    severity="WARNING",
                    constraint=element,
                    source=source,
                    conflict=f"Forbidden element found in {path}",
                    conflict_source=f"{SERIES_ARTIFACT}:{path}",
                    explanation=(
                        f'Universe forbids "{element}", but it appears in Series field '
                        f"{path}. Options: (1) Remove or rename the element in {path}, "
                        "(2) Relax the Universe forbidden_elements entry if the usage is intentional."
                    ),
                    lsm_context={},
                )
            )

    return diagnostics
