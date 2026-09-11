"""Derived routing from a resolved Tutor choice to existing authority workflows."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from auteur.workflow.models import AuthorityLevel

from .models import AuthorAction
from .session import TutorSession


HandoffStatus = Literal["route_identified", "unresolved", "stale"]
RouteKind = Literal["inspect", "prepare", "validate", "authority"]


class DecisionHandoffStep(BaseModel):
    """One existing workflow step surfaced by a derived handoff."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: RouteKind
    label: str = Field(min_length=1)
    command: str = Field(min_length=1)
    authority: AuthorityLevel
    description: str = Field(min_length=1)
    executable_by_handoff: Literal[False] = False


class DecisionAuthorityHandoff(BaseModel):
    """A noncanonical route toward an existing story-authority workflow."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: int = Field(default=1, ge=1)
    session_id: str
    card_id: str
    response_action: AuthorAction | None = None
    response_value: str | None = None
    status: HandoffStatus
    target_layer: Literal["structure"] | None = None
    affected_artifacts: tuple[str, ...] = ()
    workflow: str | None = None
    steps: tuple[DecisionHandoffStep, ...] = ()
    prerequisites: tuple[str, ...] = ()
    rationale: str = Field(min_length=1)
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"
    mutates_story: Literal[False] = False


def _source_path(key: str) -> str | None:
    """Return the normalized relative path from a persisted NAME=PATH key."""
    if "=" not in key:
        return None
    _name, path = key.split("=", 1)
    return path or None


def _blueprint_source(session: TutorSession) -> str | None:
    for key in sorted(session.source_fingerprints):
        path = _source_path(key)
        if path is not None and path.replace("\\", "/").endswith("blueprint.yaml"):
            return path.replace("\\", "/")
    return None


def _has_structure_evidence(session: TutorSession) -> bool:
    if session.card.source_rule:
        return True
    hints = {
        "beat",
        "causal structure",
        "conflict",
        "institutions",
        "relationships",
        "resolution",
        "setup/payoff",
        "stakes",
        "structure",
    }
    return any(item.casefold() in hints for item in session.card.evidence)


def _base(session: TutorSession, *, status: HandoffStatus, rationale: str) -> dict[str, object]:
    return {
        "session_id": session.session_id,
        "card_id": session.card_id,
        "response_action": session.response_action,
        "response_value": session.response_value,
        "status": status,
        "rationale": rationale,
    }


def derive_decision_handoff(session: TutorSession) -> DecisionAuthorityHandoff:
    """Derive a route without writing files or executing story-authority commands."""
    if session.status == "stale":
        return DecisionAuthorityHandoff(
            **_base(
                session,
                status="stale",
                rationale=(
                    "The Tutor session is stale because its source snapshot changed. "
                    "Re-establish a current decision before routing toward story authority."
                ),
            )
        )

    if session.status != "resolved" or session.response_action != AuthorAction.CHOOSE:
        return DecisionAuthorityHandoff(
            **_base(
                session,
                status="unresolved",
                rationale=(
                    "An authority route is only identified after a current Tutor session "
                    "is resolved with an explicit choose response."
                ),
            )
        )

    blueprint = _blueprint_source(session)
    if blueprint is None or not _has_structure_evidence(session):
        return DecisionAuthorityHandoff(
            **_base(
                session,
                status="unresolved",
                rationale=(
                    "The current evidence does not identify a supported existing authority "
                    "workflow confidently enough to route this choice without guessing."
                ),
            )
        )

    quoted_blueprint = f'"{blueprint}"' if " " in blueprint else blueprint
    steps = (
        DecisionHandoffStep(
            kind="inspect",
            label="Recheck current Structure diagnostics",
            command=f"auteur structure diagnose {quoted_blueprint}",
            authority=AuthorityLevel.READ_ONLY,
            description="Inspect the current blueprint before preparing any authoritative revision.",
        ),
        DecisionHandoffStep(
            kind="prepare",
            label="Prepare a scoped Structure revision plan",
            command="auteur structure revision plan --proposal <proposal.yaml> --project .",
            authority=AuthorityLevel.DERIVED_ARTIFACT,
            description="Create a revision plan from a proposal that explicitly represents the chosen change.",
        ),
        DecisionHandoffStep(
            kind="validate",
            label="Validate the Structure revision plan",
            command="auteur structure revision validate <plan_id> --project .",
            authority=AuthorityLevel.READ_ONLY,
            description="Revalidate the proposed route against current project state before authority is exercised.",
        ),
        DecisionHandoffStep(
            kind="authority",
            label="Apply the confirmed Structure revision",
            command="auteur structure revision apply <plan_id> --confirm --project .",
            authority=AuthorityLevel.CANONICAL_MUTATION,
            description="This existing command is the explicit authority boundary; the handoff never executes it.",
        ),
    )
    return DecisionAuthorityHandoff(
        **_base(
            session,
            status="route_identified",
            rationale=(
                "The resolved choice is bound to the current blueprint and carries Structure-level "
                "evidence, so the existing scoped Structure revision workflow owns any canonical change."
            ),
        ),
        target_layer="structure",
        affected_artifacts=(blueprint,),
        workflow="structure_revision",
        steps=steps,
        prerequisites=(
            "Review the selected Tutor value against the current blueprint.",
            "Provide or select a Structure proposal that explicitly encodes the chosen change; the handoff does not generate one.",
        ),
    )
