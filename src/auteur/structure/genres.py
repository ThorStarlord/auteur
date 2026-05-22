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
# The "override_bypassed" constants are glossary categories representing a family
# of analyzer rules, rather than the exact emitted string. The actual rule IDs
# produced by analyze_structure() append specific constraint types and override
# types as suffixes.
#
# Glossary Rule Category mapping to Emitted Analyzer Rules:
#
# | Glossary Rule Category                       | Emitted Analyzer Rules Examples                                      |
# |----------------------------------------------|----------------------------------------------------------------------|
# | genre.forbidden_mismatch.override_bypassed | Maps to ending-tone and required-trope override warnings, e.g.:      |
# |                                              | - genre.forbidden_mismatch.ending_tone.subversion                    |
# |                                              | - genre.forbidden_mismatch.required_trope_forbidden.reclassification |
# | genre.runway.override_bypassed               | Maps to runway override warnings, e.g.:                              |
# |                                              | - genre.setup_contract.insufficient_runway.compressed                |
# |                                              | - genre.setup_contract.insufficient_runway.subverted                 |
# |                                              | - genre.setup_contract.insufficient_runway.reclassified              |

FORBIDDEN_MISMATCH_OVERRIDE_BYPASSED = "genre.forbidden_mismatch.override_bypassed"
RUNWAY_OVERRIDE_BYPASSED = "genre.runway.override_bypassed"
