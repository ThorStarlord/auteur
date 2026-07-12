"""Orchestration components for Layer 2.5 narrative structure.

This module contains tools for composing, validating, and visualizing
complete outline structures.

Public API:
    OutlineGrapher: Visualize outline relationships as ASCII art
"""

from auteur.narrative_orchestration.orchestrator.outline_grapher import (
    OutlineGrapher,
    OutlineNode,
    ArcReference,
    SetupPayoffFlow,
    TreeFormatter,
)

__all__ = [
    "OutlineGrapher",
    "OutlineNode",
    "ArcReference",
    "SetupPayoffFlow",
    "TreeFormatter",
]
