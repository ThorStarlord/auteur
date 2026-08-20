"""G1a Story Discovery routing layered over the generic workflow rules."""

from __future__ import annotations

from pathlib import Path

import yaml

from auteur.story_discovery_guidance import (
    BriefLifecycleState,
    inspect_working_brief,
    intent_aware_run_matches_brief,
)
from auteur.workflow.models import AuthorityLevel, WorkflowAction


def _usable_recommendation(root: Path, current_brief: object | None) -> str | None:
    discovery_dir = root / "story_discovery"
    try:
        payload = yaml.safe_load(
            (discovery_dir / "discovery_set.yaml").read_text(encoding="utf-8")
        ) or {}
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(payload, dict):
        return None

    if current_brief is not None and not intent_aware_run_matches_brief(root, current_brief):
        return None

    raw_winner = payload.get("recommended_candidate_id")
    if not isinstance(raw_winner, str) or not raw_winner.strip():
        return None
    winner = raw_winner.strip()
    if Path(winner).name != winner:
        return None
    if not (discovery_dir / f"{winner}.yaml").is_file():
        return None
    return winner


def _front_door_action(root: Path) -> WorkflowAction:
    status = inspect_working_brief(root)
    current_brief = status.brief
    winner = _usable_recommendation(root, current_brief)

    if status.state is BriefLifecycleState.INVALID:
        return WorkflowAction(
            label="Repair your Story Discovery brief",
            command="auteur story-discovery start --project .",
            authority=AuthorityLevel.AUTHORITY_BEARING,
            description=(
                "The working brief cannot be parsed safely. Auteur will not overwrite "
                "or guess author intent."
            ),
        )
    if status.state is BriefLifecycleState.INCOMPLETE:
        return WorkflowAction(
            label="Continue clarifying what you want",
            command="auteur story-discovery start --project .",
            authority=AuthorityLevel.AUTHORITY_BEARING,
            description=(
                "Resume the non-canonical Discovery Brief and answer only the missing "
                "questions required for intent-aware recommendation."
            ),
        )
    if status.state is BriefLifecycleState.ADEQUATE and winner is None:
        return WorkflowAction(
            label="Discover story directions against your intent",
            command=(
                "auteur story-discovery run --brief story_discovery/brief.yaml "
                "--recommend --output story_discovery --project ."
            ),
            authority=AuthorityLevel.CANDIDATE_GENERATION,
            description=(
                "Run intent-aware Story Discovery against the current working brief. "
                "Canonical state remains unchanged."
            ),
        )
    if winner is not None:
        return WorkflowAction(
            label="Choose recommended story direction",
            command=(
                "auteur story-discovery accept "
                f"story_discovery/{winner}.yaml --output story_identity.yaml"
            ),
            authority=AuthorityLevel.AUTHORITY_BEARING,
            description=(
                "Review the Story Discovery recommendation and explicitly accept it "
                "to make the selected StoryIdentity canonical."
            ),
        )
    return WorkflowAction(
        label="Tell Auteur about your story",
        command="auteur story-discovery start --project .",
        authority=AuthorityLevel.AUTHORITY_BEARING,
        description=(
            "Create a resumable, non-canonical Discovery Brief in writer-facing language "
            "before asking Auteur to recommend a direction."
        ),
    )


def apply_story_discovery_workflow_routing(
    project_root: str | Path,
    actions: list[WorkflowAction],
) -> list[WorkflowAction]:
    """Replace the generic Identity Story Discovery action with the G1a front door."""

    replacement = _front_door_action(Path(project_root))
    routed: list[WorkflowAction] = []
    replaced = False
    for action in actions:
        if not replaced and action.command.startswith("auteur story-discovery "):
            routed.append(replacement)
            replaced = True
        else:
            routed.append(action)
    if not replaced:
        routed.append(replacement)
    return routed
