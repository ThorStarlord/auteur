"""Advisory Universe-field diagnostics for Series (auteur#38 Decisions A/B/C, Phases 2-4).

This module is deliberately separate from :class:`UniverseToSeriesValidator` in
``universe_integration.py``. That validator dispatches on
``StructuredConstraint.type``; ``UniverseIdentity.forbidden_elements`` is a plain
``list[str]`` advisory field with search-and-match semantics, not
constraint-type dispatch, so forcing it through that dispatch would be a
category error.

Scope: ``forbidden_elements`` (Phase 2, auteur#43), ``required_elements``
(Phase 3, auteur#45) and ``cross_story_constraints`` (Phase 4, auteur#47,
#38 Decision C).

The two *text-matching* advisory validators share the same text machinery
(:func:`normalize_text`, :func:`extract_searchable_fields`,
:func:`phrase_matches`) and invert only the reporting rule:
``forbidden_elements`` reports when a phrase IS found (per matched field),
``required_elements`` reports when a phrase is NOT found in any searchable
field (union presence, one diagnostic per absent entry).

``cross_story_constraints`` is deliberately different in kind and shares none
of that machinery: :func:`surface_cross_story_constraints` performs no search,
reads no Series text, and makes no compliance judgement. It emits one
non-blocking ``INFO`` human-review notice per configured entry stating that the
rule was *not* automatically evaluated. A single ``SeriesIdentity`` cannot
prove or disprove a cross-story invariant, so no pass/fail outcome is ever
claimed.
"""

from __future__ import annotations

import re
import unicodedata
from typing import TYPE_CHECKING, Sequence

from auteur.series.continuity_validators import ValidationDiagnostic

if TYPE_CHECKING:
    from auteur.series.models import SeriesIdentity
    from auteur.universe.models import CrossStoryConstraint

FORBIDDEN_ELEMENT_PRESENT = "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT"
FORBIDDEN_ELEMENT_UNEVALUABLE = "UNIVERSE_FORBIDDEN_ELEMENT_UNEVALUABLE"
REQUIRED_ELEMENT_MISSING = "UNIVERSE_REQUIRED_ELEMENT_MISSING"
REQUIRED_ELEMENT_UNEVALUABLE = "UNIVERSE_REQUIRED_ELEMENT_UNEVALUABLE"
ADVISORY_RULE_UNSUPPORTED = "UNIVERSE_ADVISORY_RULE_UNSUPPORTED"
CROSS_STORY_CONSTRAINT_NOT_EVALUATED = "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED"

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


def _unsupported_rule_diagnostic(
    *,
    field_name: str,
    index: int,
    element: str,
    label: str,
    rule_kind: str,
    remedy: str,
) -> ValidationDiagnostic:
    """Build the shared ``UNIVERSE_ADVISORY_RULE_UNSUPPORTED`` diagnostic.

    Malformed advisory input (an empty or whitespace-only rule) is reported,
    never silently discarded, per auteur#38 Decision D. Both
    :func:`validate_forbidden_elements` and :func:`validate_required_elements`
    use this single construction so the two phases cannot drift into
    incompatible unsupported-rule policies.
    """
    return ValidationDiagnostic(
        id=ADVISORY_RULE_UNSUPPORTED,
        severity="INFO",
        constraint=element,
        source=f"universe:{field_name}[{index}]",
        conflict=f"{label} is empty or whitespace-only",
        conflict_source=f"{UNIVERSE_ARTIFACT}:{field_name}[{index}]",
        explanation=(
            f"Universe {field_name}[{index}] is empty or whitespace-only "
            f"and cannot be processed as a {rule_kind} rule. {remedy}"
        ),
        lsm_context={},
    )


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
                _unsupported_rule_diagnostic(
                    field_name="forbidden_elements",
                    index=index,
                    element=element,
                    label="Forbidden element",
                    rule_kind="forbidden-element",
                    remedy=(
                        "Remove the entry or replace it with the phrase that should be forbidden."
                    ),
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


def validate_required_elements(
    series: SeriesIdentity,
    required_elements: Sequence[str],
) -> list[ValidationDiagnostic]:
    """Produce deterministic ``required_elements`` diagnostics for a Series.

    Presence is a union across the ratified searchable fields: a required
    element is satisfied when it matches in *any one* field, so a satisfied
    element produces no diagnostic at all (there is no positive "present"
    diagnostic, unlike ``forbidden_elements``).

    Cardinality, per auteur#38 Decision B/D:

    * exactly one ``UNIVERSE_REQUIRED_ELEMENT_MISSING`` (WARNING) per
      well-formed element that is absent from every searchable field, when
      searchable Series text exists somewhere -- not one per searched field;
    * exactly one ``UNIVERSE_REQUIRED_ELEMENT_UNEVALUABLE`` (INFO) per
      well-formed element when every searchable field is empty or
      whitespace-only, and never a MISSING in that state;
    * exactly one ``UNIVERSE_ADVISORY_RULE_UNSUPPORTED`` (INFO) per malformed
      (empty/whitespace-only) entry, which is never silently skipped.

    Entries are evaluated in original list order and keep their original list
    indices; duplicate identical entries are not deduplicated. The Series is
    never mutated.
    """
    if not required_elements:
        return []

    searchable = extract_searchable_fields(series)
    normalized_fields = [(path, normalize_text(value)) for path, value in searchable]
    has_searchable_text = any(text for _, text in normalized_fields)

    diagnostics: list[ValidationDiagnostic] = []

    for index, element in enumerate(required_elements):
        source = f"universe:required_elements[{index}]"
        normalized_element = normalize_text(element)

        if not normalized_element:
            diagnostics.append(
                _unsupported_rule_diagnostic(
                    field_name="required_elements",
                    index=index,
                    element=element,
                    label="Required element",
                    rule_kind="required-element",
                    remedy=(
                        "Remove the entry or replace it with the phrase that should be required."
                    ),
                )
            )
            continue

        if not has_searchable_text:
            diagnostics.append(
                ValidationDiagnostic(
                    id=REQUIRED_ELEMENT_UNEVALUABLE,
                    severity="INFO",
                    constraint=element,
                    source=source,
                    conflict="No searchable Series text is present",
                    conflict_source=SERIES_ARTIFACT,
                    explanation=(
                        f'Required element "{element}" could not be evaluated: '
                        "no searchable Series text is present"
                    ),
                    lsm_context={},
                )
            )
            continue

        if any(phrase_matches(normalized_element, text) for _, text in normalized_fields):
            continue

        diagnostics.append(
            ValidationDiagnostic(
                id=REQUIRED_ELEMENT_MISSING,
                severity="WARNING",
                constraint=element,
                source=source,
                conflict="Required element not found in any searchable Series field",
                conflict_source=SERIES_ARTIFACT,
                explanation=(
                    f'Required element "{element}" was not found in any searchable '
                    "Series field. Options: (1) Introduce the element in the Series "
                    "title, core question, global arc, book plans, thematic arcs, lore "
                    "entries or recurring symbols, (2) Relax the Universe "
                    "required_elements entry if it no longer applies."
                ),
                lsm_context={},
            )
        )

    return diagnostics


def _severity_label(severity: object) -> str:
    """Render a configured ``ConstraintSeverity`` deterministically as text.

    ``CrossStoryConstraint`` sets ``model_config = ConfigDict(use_enum_values=True)``,
    so at runtime ``severity`` is normally the plain ``str`` value ("required",
    "warning", "info"). An enum member is still accepted defensively so the
    rendered label never leaks a ``ConstraintSeverity.REQUIRED`` repr into
    operator-facing text.
    """
    return str(getattr(severity, "value", severity))


def surface_cross_story_constraints(
    cross_story_constraints: Sequence[CrossStoryConstraint],
) -> list[ValidationDiagnostic]:
    """Surface each configured ``cross_story_constraints`` entry for human review.

    auteur#38 Decision C / Phase 4 (auteur#47). This function performs **no
    evaluation whatsoever**: it does not receive a :class:`SeriesIdentity`, does
    not read Series text, and deliberately shares none of the text machinery
    used by :func:`validate_forbidden_elements` /
    :func:`validate_required_elements` (:func:`extract_searchable_fields`,
    :func:`normalize_text`, :func:`phrase_matches`). A cross-story invariant
    cannot be proven or disproven from a single Series artifact, so the system
    must never claim it was checked.

    Cardinality and ordering:

    * exactly one ``UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED`` (INFO,
      non-blocking) notice per configured entry;
    * an empty list produces no notices;
    * source-list order and original list indices are preserved;
    * duplicate rule strings at different indices stay distinct -- no
      deduplication, no suppression based on rule text;
    * no success diagnostic and no violation diagnostic is ever emitted;
    * repeated calls on identical input produce identical output.

    The notice's own severity is always ``INFO`` because it reports
    non-evaluation, not a rule outcome. The configured ``severity``
    (``required`` / ``warning`` / ``info``) and ``applies_to_all_stories`` are
    carried as explanatory metadata only and never upgrade the notice to
    WARNING or ERROR.

    Malformed input is out of scope by design: ``CrossStoryConstraint.rule`` is
    declared ``Field(min_length=1)``, so a blank rule fails Universe model
    loading and surfaces through the existing ``UNIVERSE_CONTRACT_INVALID``
    path. Phase 4 neither relaxes that schema nor disguises that failure as a
    cross-story notice.

    Neither the constraints nor any Universe/Series data are mutated.
    """
    if not cross_story_constraints:
        return []

    diagnostics: list[ValidationDiagnostic] = []

    for index, constraint in enumerate(cross_story_constraints):
        rule = constraint.rule
        severity_label = _severity_label(constraint.severity)
        diagnostics.append(
            ValidationDiagnostic(
                id=CROSS_STORY_CONSTRAINT_NOT_EVALUATED,
                severity="INFO",
                constraint=rule,
                source=f"universe:cross_story_constraints[{index}]",
                conflict="Cross-story constraint requires human review",
                conflict_source=f"{UNIVERSE_ARTIFACT}:cross_story_constraints[{index}]",
                explanation=(
                    f'Cross-story constraint "{rule}" was not automatically evaluated '
                    "and requires human review. "
                    f"applies_to_all_stories={constraint.applies_to_all_stories}; "
                    f"configured_severity={severity_label}."
                ),
                lsm_context={},
            )
        )

    return diagnostics
