"""Read-only reasoning registry and in-process runtime."""

from .runtime import (
    CriticRegistry,
    CriticSpec,
    ExecutionPlan,
    ExecutionResult,
    ReasoningRuntime,
    RuntimeRequest,
    RuntimeStatus,
    register_structure_critic,
)
from .setup_payoff import register_setup_payoff_critic, run_setup_payoff
from .synthesis import synthesize_reports

__all__ = [
    "CriticRegistry", "CriticSpec", "ExecutionPlan", "ExecutionResult",
    "ReasoningRuntime", "RuntimeRequest", "RuntimeStatus", "register_structure_critic",
    "register_setup_payoff_critic", "run_setup_payoff",
    "synthesize_reports",
]
