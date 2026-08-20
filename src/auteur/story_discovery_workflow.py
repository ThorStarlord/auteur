"""Story Discovery routing layered over the generic workflow rules."""

from __future__ import annotations

from pathlib import Path

from auteur.story_discovery_state import StoryDiscoveryStateKind, classify_story_discovery_project
from auteur.workflow.models import AuthorityLevel, WorkflowAction


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
    if (
        state.brief_state.value == "adequate"
        and state.kind in {
            StoryDiscoveryStateKind.READY_TO_DISCOVER,
            StoryDiscoveryStateKind.NON_ADJUDICABLE,
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
    if state.has_recommendation:
        assert state.recommended_candidate_id is not None
        return WorkflowAction(
            label="Choose recommended story direction",
            command=(
                "auteur story-discovery accept "
                f"story_discovery/{state.recommended_candidate_id}.yaml "
                "--output story_identity.yaml"
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
