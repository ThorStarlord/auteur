from __future__ import annotations

from pydantic import BaseModel

from auteur.universe.models import UniverseIdentity


class CompiledUniverseConstraints(BaseModel):
    """Compiled universe constraints ready for downstream validation."""
    forbidden_elements_flat: list[str]
    required_elements_flat: list[str]
    constraint_rules: list[str]


def compile_universe_constraints(universe: UniverseIdentity) -> CompiledUniverseConstraints:
    """Compile UniverseIdentity into a form optimized for validator use.

    This creates a flat list of constraints that Series/Book validators can
    quickly check against without needing the full UniverseIdentity structure.
    """
    constraint_rules = [
        f"{c.rule} (severity: {c.severity})"
        for c in universe.cross_story_constraints
    ]

    return CompiledUniverseConstraints(
        forbidden_elements_flat=universe.forbidden_elements,
        required_elements_flat=universe.required_elements,
        constraint_rules=constraint_rules,
    )
