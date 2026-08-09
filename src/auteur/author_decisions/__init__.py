"""Author Decision Objects (M4 + thin M2, bounded M3).

Approved implementation design: "Author Decision Objects" (post-propagation
solution discovery, 2026-08). The detailed design document lives in a separate
design worktree; this module implements the M4 + thin M2 mechanism with a
bounded deterministic M3 companion.
An author decision object is an authored, validated artifact carrying an
unresolved question, explicit alternatives, combination/cardinality, hard
constraints, required commitments, blocked provenance, default references, and
a comparison criterion. The context builder resolves ONLY explicitly referenced
material (thin boundary); the deterministic companion enumerates and validates,
never renders a creative verdict.
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
