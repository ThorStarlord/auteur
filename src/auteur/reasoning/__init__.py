"""Read-only reasoning registry and in-process runtime."""

from .runtime import (
    ArtifactRevision,
    ArtifactRevisionAdapter,
    CriticRegistry,
    CriticSpec,
    ExecutionPlan,
    ExecutionResult,
    ReasoningRuntime,
    RuntimeRequest,
    RuntimeStatus,
    register_structure_critic,
)
from .book_manuscript import register_book_manuscript_critic, run_book_analysis
from .setup_payoff import register_setup_payoff_critic, run_setup_payoff
from .scene import register_scene_critic, run_scene_analysis
from .blueprint_coherence import register_blueprint_coherence_critic, run_blueprint_analysis
from .synthesis import synthesize_reports
__all__ = [
    "ArtifactRevision", "ArtifactRevisionAdapter", "CriticRegistry", "CriticSpec", "ExecutionPlan", "ExecutionResult",
    "ReasoningRuntime", "RuntimeRequest", "RuntimeStatus", "register_structure_critic",
    "register_book_manuscript_critic", "run_book_analysis",
    "register_setup_payoff_critic", "run_setup_payoff",
    "register_blueprint_coherence_critic", "run_blueprint_analysis",
    "register_scene_critic", "run_scene_analysis",
]
