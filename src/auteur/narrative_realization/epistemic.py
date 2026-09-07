"""Explicit author, reader, character, and faction knowledge facts."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeFact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observer_id: str
    proposition_id: str
    value: Literal["known", "unknown", "believed_false"]
    event_index: int = Field(ge=0)
    source_event_id: str
    evidence_ref: str = ""


def knowledge_at(
    facts: list[KnowledgeFact], *, observer_id: str, event_index: int
) -> dict[str, KnowledgeFact]:
    """Project the latest explicit knowledge state for one observer."""
    current: dict[str, KnowledgeFact] = {}
    for fact in sorted(facts, key=lambda item: (item.event_index, item.proposition_id)):
        if fact.observer_id == observer_id and fact.event_index <= event_index:
            current[fact.proposition_id] = fact
    return current


def epistemic_findings(facts: list[KnowledgeFact]) -> list[dict[str, str]]:
    """Return narrow findings for impossible knowledge reversals."""
    findings: list[dict[str, str]] = []
    for observer in sorted({fact.observer_id for fact in facts}):
        by_prop = knowledge_at(facts, observer_id=observer, event_index=max((f.event_index for f in facts), default=0))
        for proposition, fact in by_prop.items():
            if fact.value == "known" and not fact.source_event_id:
                findings.append({
                    "rule": "epistemic.known_without_source",
                    "observer_id": observer,
                    "proposition_id": proposition,
                    "message": f"{observer} knows {proposition} without a source event.",
                })
    return findings
