"""Convenience registration for all built-in critics."""

from __future__ import annotations

from .runtime import CriticRegistry, register_structure_critic
from .book_manuscript import register_book_manuscript_critic
from .blueprint_coherence import register_blueprint_coherence_critic
from .scene import register_scene_critic
from .setup_payoff import register_setup_payoff_critic


def register_all_builtins(registry: CriticRegistry) -> None:
    """Register every built-in deterministic critic."""
    register_structure_critic(registry)
    register_setup_payoff_critic(registry)
    register_blueprint_coherence_critic(registry)
    register_book_manuscript_critic(registry)
    register_scene_critic(registry)
