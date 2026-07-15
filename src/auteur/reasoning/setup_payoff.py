"""Deterministic setup/payoff reasoning adapter for accepted series structure."""

from __future__ import annotations

from typing import Any

from .runtime import CriticRegistry, CriticSpec


def register_setup_payoff_critic(registry: CriticRegistry) -> None:
    registry.register(CriticSpec(
        critic_id="structure.setup_payoff",
        version="1.0.0",
        input_keys=("series", "scope"),
        run=run_setup_payoff,
    ))


def run_setup_payoff(*, series: Any, scope: str = "series", **_: Any) -> list[dict[str, Any]]:
    """Return explainable findings without changing the supplied series."""
    setups = getattr(series, "narrative_setups", None)
    if setups is None and isinstance(series, dict):
        setups = series.get("narrative_setups", [])
    total_books = len(getattr(series, "book_plans", []) or series.get("book_plans", [])) if isinstance(series, dict) else len(series.book_plans)
    findings: list[dict[str, Any]] = []
    for setup in setups or []:
        get = setup.get if isinstance(setup, dict) else lambda key, default=None: getattr(setup, key, default)
        if get("status", "unresolved") != "unresolved":
            continue
        setup_id = get("id")
        payoff_id = get("payoff_id")
        if payoff_id:
            continue
        deadline = get("expected_payoff_by_book")
        within_scope = deadline <= total_books
        if not within_scope and scope == "series":
            continue
        findings.append({
            "rule": "setup_payoff.unresolved",
            "message": f"Setup '{setup_id}' has no linked payoff within the {scope} scope.",
            "evidence": {
                "setup_id": setup_id,
                "introduced_book": get("book_introduced"),
                "expected_payoff_by_book": deadline,
                "available_books": total_books,
                "scope": scope,
            },
            "hypotheses": [
                "the payoff is missing",
                "the setup is intentionally unresolved for a later scope",
                "the payoff exists but is not linked",
                "the setup should be removed or weakened",
            ],
            "recommendations": [
                "link an existing payoff",
                "record a future-scope carryover",
                "add a payoff beat",
                "remove or weaken the setup",
            ],
            "requested_change": "Review the setup and choose an author-approved resolution.",
        })
    return findings
