from pydantic import ValidationError
import pytest

from auteur.beginner.contracts import (
    AcceptedMilestoneReference,
    CreateWorkspaceCommand,
    DecisionStage,
    LifecycleStatus,
    MutationCommand,
    RevisionRef,
    SessionEnvelope,
    StageAvailability,
    StageStatus,
    WorkingDecision,
)


def test_new_session_starts_discovery_working_and_later_stages_locked() -> None:
    session = SessionEnvelope.new(
        project_id="project-1",
        guidance_genre="mystery",
        premise="A missing heir returns home.",
    )

    assert session.schema_version == 1
    assert session.session_version == 0
    assert session.stages[DecisionStage.DISCOVER].lifecycle == LifecycleStatus.WORKING
    assert session.stages[DecisionStage.DISCOVER].availability == StageAvailability.AVAILABLE
    assert session.stages[DecisionStage.STORY_IDENTITY].availability == StageAvailability.LOCKED
    assert session.stages[DecisionStage.STORY_STRUCTURE].availability == StageAvailability.LOCKED
    assert session.stages[DecisionStage.STORY_IDENTITY].lifecycle == LifecycleStatus.NOT_STARTED
    assert session.stages[DecisionStage.STORY_STRUCTURE].lifecycle == LifecycleStatus.NOT_STARTED


def test_session_uses_accepted_milestones_and_no_canonical_field() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A premise.")

    assert session.accepted_milestones == []
    assert "canonical" not in SessionEnvelope.model_fields


def test_mutation_commands_have_distinct_existing_and_create_shapes() -> None:
    existing = MutationCommand(
        workspace_id="workspace-1",
        expected_session_version=3,
        command_id="command-1",
        payload={"stage": "discover"},
    )
    create = CreateWorkspaceCommand(
        command_id="command-2",
        payload={"project_id": "project-1"},
    )

    assert existing.expected_session_version == 3
    assert create.model_dump() == {
        "command_id": "command-2",
        "payload": {"project_id": "project-1"},
    }
    with pytest.raises(ValidationError):
        CreateWorkspaceCommand(
            command_id="command-3",
            payload={},
            workspace_id="not-allowed",
        )


def test_supporting_contracts_are_typed_pydantic_models() -> None:
    decision = WorkingDecision(
        stage=DecisionStage.DISCOVER,
        question="What is the story about?",
    )
    status = StageStatus(
        stage=DecisionStage.DISCOVER,
        lifecycle=LifecycleStatus.WORKING,
        availability=StageAvailability.AVAILABLE,
    )
    milestone = AcceptedMilestoneReference(
        milestone_id="milestone-1",
        revision=RevisionRef(artifact_id="artifact-1", revision=2),
    )

    assert decision.stage is DecisionStage.DISCOVER
    assert status.lifecycle is LifecycleStatus.WORKING
    assert milestone.revision.revision == 2
