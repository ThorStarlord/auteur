"""Evidence-backed reasoning reports for interactive diagnostic teaching."""
from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ReasoningEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    source_artifact: str
    source_revision: str = ""
    extraction: str


class ReasoningReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reasoning_id: str
    subject: str
    observations: list[str] = Field(default_factory=list)
    evidence: list[ReasoningEvidence] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    claim: str
    confidence_method: str
    confidence: Literal["high", "medium", "low", "unknown"]
    recommendations: list[str] = Field(default_factory=list)
    possible_transformations: list[str] = Field(default_factory=list)
    status: Literal["derived"] = "derived"


def build_reasoning_report(
    *, subject: str, rule: str, message: str, evidence: dict[str, object], recommendations: list[str], hypotheses: list[str]
) -> ReasoningReport:
    refs = [ReasoningEvidence(evidence_id=f"e-{key}", source_artifact=key, extraction=str(value)) for key, value in sorted(evidence.items())]
    payload = {"subject": subject, "rule": rule, "message": message, "evidence": [item.model_dump() for item in refs]}
    reasoning_id = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return ReasoningReport(
        reasoning_id=reasoning_id,
        subject=subject,
        observations=[message],
        evidence=refs,
        hypotheses=hypotheses,
        claim=message,
        confidence_method="deterministic_rule",
        confidence="medium",
        recommendations=recommendations,
        possible_transformations=["author.review_decision_card"],
    )
