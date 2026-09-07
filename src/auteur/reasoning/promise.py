"""Deterministic promise/setup/payoff records for derived reasoning."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PromiseRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    promise_id: str
    kind: Literal["plot", "emotional", "thematic", "relationship"]
    introduced_at: int = Field(ge=0)
    expected_by: int | None = Field(default=None, ge=0)
    status: Literal["open", "escalated", "resolved", "intentionally_deferred"] = "open"
    payoff_ref: str | None = None
    meaning: str = ""


def review_promises(promises: list[PromiseRecord], *, current_index: int) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for promise in promises:
        if promise.status in {"resolved", "intentionally_deferred"} or promise.payoff_ref:
            continue
        if promise.expected_by is not None and current_index >= promise.expected_by:
            findings.append({
                "rule": "promise_payoff.overdue",
                "promise_id": promise.promise_id,
                "kind": promise.kind,
                "message": f"Promise {promise.promise_id} is overdue for a payoff.",
            })
    return findings
