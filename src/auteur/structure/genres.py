"""Genre override validation rules.

Provides the rule IDs referenced in the CONTEXT.md glossary:
- ``genre.forbidden_mismatch.override_bypassed``
- ``genre.runway.override_bypassed``

These are thin wrappers around the inline override logic in
``auteur.structure.analyzer.analyze_structure``. The actual rule IDs emitted
by the analyzer carry a suffix matching the override type (e.g.,
``genre.forbidden_mismatch.ending_tone.subversion``), and this module maps
them to the generic glossary entries.
"""

from __future__ import annotations

from auteur.blueprint import GenreOverride, OverrideType  # noqa: F401

# Rule ID prefixes referenced in CONTEXT.md glossary.
# The full rule IDs produced by analyze_structure() append the override type
# as a suffix:
#   genre.forbidden_mismatch.ending_tone.{override_type.value}
#   genre.setup_contract.insufficient_runway.{override_type.value}
#
# The "override_bypassed" form is shorthand for any of these suffixes.

FORBIDDEN_MISMATCH_OVERRIDE_BYPASSED = "genre.forbidden_mismatch.override_bypassed"
RUNWAY_OVERRIDE_BYPASSED = "genre.runway.override_bypassed"
