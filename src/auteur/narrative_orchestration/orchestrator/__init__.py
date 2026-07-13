"""Orchestration components for Structure composition.

This module contains tools for composing, validating, and visualizing
complete outline structures.

Public API:
    OutlineInspector: Display and analyze complete outline structures
    OutlineGrapher: Visualize outline relationships as ASCII art
"""

from auteur.narrative_orchestration.orchestrator.outline_inspector import (
    OutlineInspector,
    ValidationStatus,
)

try:
    from auteur.narrative_orchestration.orchestrator.outline_grapher import (
        OutlineGrapher,
        OutlineNode,
        ArcReference,
        SetupPayoffFlow,
        TreeFormatter,
    )
    HAS_GRAPHER = True
except ImportError:
    HAS_GRAPHER = False

__all__ = [
    "OutlineInspector",
    "ValidationStatus",
]

if HAS_GRAPHER:
    __all__.extend([
        "OutlineGrapher",
        "OutlineNode",
        "ArcReference",
        "SetupPayoffFlow",
        "TreeFormatter",
    ])
