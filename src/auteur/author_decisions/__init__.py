"""Author Decision Objects (M4 + thin M2, bounded M3).

Design: docs/design/2026-08-post-propagation-author-decision-objects.md.
An author decision object is an authored, validated artifact carrying an unresolved
question, explicit alternatives, combination/cardinality, hard constraints, required
commitments, blocked provenance, default references, and a comparison criterion.
The context builder resolves ONLY explicitly referenced material (thin boundary);
the deterministic companion enumerates and validates, never renders a creative verdict.
"""
from auteur.author_decisions.models import (
    AuthorDecision,
    DecisionValidationError,
)
from auteur.author_decisions.context import build_decision_context
from auteur.author_decisions.report import enumerate_combinations

__all__ = [
    "AuthorDecision",
    "build_decision_context",
    "enumerate_combinations",
    "DecisionValidationError",
]