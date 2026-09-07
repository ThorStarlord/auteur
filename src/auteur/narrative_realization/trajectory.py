"""Explicit, small state projections for character and relationship trajectories."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CharacterStateSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    character_id: str
    event_index: int = Field(ge=0)
    wants: list[str] = Field(default_factory=list)
    beliefs: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    commitments: list[str] = Field(default_factory=list)
    knowledge: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    status: str = ""
    identity: str = ""
    moral_boundaries: list[str] = Field(default_factory=list)
    source_ref: str = ""


class RelationshipStateSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relationship_id: str
    subject_a: str
    subject_b: str
    event_index: int = Field(ge=0)
    state: str
    cause_ref: str | None = None
    source_ref: str = ""


def current_character_states(states: list[CharacterStateSnapshot]) -> dict[str, CharacterStateSnapshot]:
    """Return the latest explicit state for each character."""
    current: dict[str, CharacterStateSnapshot] = {}
    for state in sorted(states, key=lambda item: (item.event_index, item.character_id)):
        current[state.character_id] = state
    return current


def relationship_transition_findings(
    states: list[RelationshipStateSnapshot],
) -> list[dict[str, str]]:
    """Find state changes without an explicit causal reference."""
    findings: list[dict[str, str]] = []
    previous: dict[str, RelationshipStateSnapshot] = {}
    for state in sorted(states, key=lambda item: (item.event_index, item.relationship_id)):
        prior = previous.get(state.relationship_id)
        if prior and prior.state != state.state and not state.cause_ref:
            findings.append({
                "rule": "relationship.transition_without_cause",
                "relationship_id": state.relationship_id,
                "before": prior.state,
                "after": state.state,
                "message": f"Relationship {state.relationship_id} changes from {prior.state} to {state.state} without a declared cause.",
            })
        previous[state.relationship_id] = state
    return findings
