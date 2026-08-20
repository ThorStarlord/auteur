"""Story Discovery routing layered over the generic workflow rules."""

from __future__ import annotations

from pathlib import Path

from auteur.story_discovery_state import StoryDiscoveryStateKind, classify_story_discovery_project
from auteur.workflow.models import AuthorityLevel, WorkflowAction


def _review_action(label: str, description: str) -> WorkflowAction:
    return WorkflowAction(
        label=label,
        command="auteur story-discovery review --project .",
        authority=AuthorityLevel.READ_ONLY,
        description=description,
    )


def _front_door_action(root: Path) -> WorkflowAction:
    state = classify_story_discovery_project(root)

    if state.kind is StoryDiscoveryStateKind.INVALID_BRIEF:
        return WorkflowAction(
            label="Repair your Story Discovery brief",
            command="auteur story-discovery start --project .",
            authority=AuthorityLevel.AUTHORITY_BEARING,
            description=(
                "The working brief cannot be parsed safely. Auteur will not overwrite "
                "or guess author intent."
            ),
        )
    if state.kind is StoryDiscoveryStateKind.INCOMPLETE_BRIEF:
        return WorkflowAction(
            label="Continue clarifying what you want",
            command="auteur story-discovery start --project .",
            authority=AuthorityLevel.AUTHORITY_BEARING,
            description=(
                "Resume the non-canonical Discovery Brief and answer only the missing "
                "questions required for intent-aware recommendation."
            ),
        )
    if state.kind is StoryDiscoveryStateKind.NON_ADJUDICABLE:
        return _review_action(
            "Review why Auteur cannot recommend a direction yet",
            (
                "Read the persisted causal evidence and recovery options. Review never "
                "manufactures a winner or changes canonical state."
            ),
        )
    if state.kind is StoryDiscoveryStateKind.COMPOSED_CANDIDATE_AVAILABLE:
        return _review_action(
            "Review composed story direction",
            (
                "Compare the composed candidate with its governing primary and inspect "
                "the persisted hierarchy evidence before deciding."
            ),
        )
    if state.kind is StoryDiscoveryStateKind.RECOMMENDATION_AVAILABLE:
        return _review_action(
            "Review recommended story direction",
            (
                "Reconstruct the advisory recommendation, causal mechanics, and craft "
                "tradeoffs before any explicit acceptance decision."
            ),
        )
    if (
        state.brief_state.value == "adequate"
        and state.kind in {
            StoryDiscoveryStateKind.READY_TO_DISCOVER,
            StoryDiscoveryStateKind.DISCOVERY_INVALID,
        }
    ):
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
    """Replace the generic Identity Story Discovery action with the derived front door."""

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
