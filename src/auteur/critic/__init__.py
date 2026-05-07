"""Critic system — validation findings and aggregation.

The five built-in critics live in their own modules (contract, arc, tension,
slop, theme). Each emits a list[CriticFinding]. run_critics fans them out
in parallel and aggregates into one ValidationReport.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class CriticFinding(BaseModel):
    critic: Literal["contract", "arc", "tension", "slop", "theme"]
    severity: Literal["error", "warning"]
    rule: str
    evidence: str
    requested_change: str


class ValidationReport(BaseModel):
    chapter_index: int
    iteration: int
    findings: list[CriticFinding]
    passed: bool


__all__ = ["CriticFinding", "ValidationReport"]
