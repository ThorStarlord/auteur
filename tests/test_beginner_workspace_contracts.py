from pydantic import ValidationError
import pytest

from auteur.beginner import contracts
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
from auteur.story_design_packs.models import PackProvenance


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
        CreateWorkspaceCommand.model_validate(
            {
                "command_id": "command-3",
                "payload": {},
                "workspace_id": "not-allowed",
            }
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
        accepted_content="accepted content",
        fingerprint="fingerprint-2",
    )

    assert decision.stage is DecisionStage.DISCOVER
    assert status.lifecycle is LifecycleStatus.WORKING
    assert milestone.revision.revision == 2
    restored = AcceptedMilestoneReference.model_validate_json(milestone.model_dump_json())
    assert restored == milestone


@pytest.mark.parametrize(
    "stages",
    [
        {},
        {"discover": SessionEnvelope.new("p", "mystery", "premise").stages[DecisionStage.DISCOVER].model_dump()},
        {
            **SessionEnvelope.new("p", "mystery", "premise").model_dump(mode="json")["stages"],
            "extra": {
                "stage": "extra",
                "lifecycle": "not_started",
                "availability": "locked",
            },
        },
    ],
)
def test_session_rejects_empty_missing_or_extra_stage_mappings(stages: dict) -> None:
    payload = SessionEnvelope.new("p", "mystery", "premise").model_dump(mode="json")
    payload["stages"] = stages

    with pytest.raises(ValidationError):
        SessionEnvelope.model_validate(payload)


def test_session_rejects_nested_stage_mismatches() -> None:
    payload = SessionEnvelope.new("p", "mystery", "premise").model_dump(mode="json")
    payload["stages"]["discover"]["stage"] = "story_identity"

    with pytest.raises(ValidationError, match="must match its stage mapping key"):
        SessionEnvelope.model_validate(payload)


def test_stage_status_rejects_working_decision_for_another_stage() -> None:
    status = {
        "stage": "discover",
        "lifecycle": "working",
        "availability": "available",
        "working_decision": {
            "stage": "story_identity",
            "question": "Who is the protagonist?",
        },
    }

    with pytest.raises(ValidationError, match="working_decision.stage must match stage"):
        StageStatus.model_validate(status)


def test_session_json_round_trip_preserves_stage_contract() -> None:
    session = SessionEnvelope.new("p", "mystery", "premise")

    restored = SessionEnvelope.model_validate_json(session.model_dump_json())

    assert restored == session


def test_working_composition_separates_dimension_axes_and_preserves_review_records() -> None:
    provenance = PackProvenance(pack_id="superhero", version="0.1.0", content_hash="sha256:fixture")
    dimension = contracts.WorkingDimension(
        dimension_id="hero-public-identity",
        category=contracts.DimensionCategory.SETTING_WORLD,
        origin=contracts.DimensionOrigin.DETECTED_FROM_PACK,
        status=contracts.DimensionStatus.CONFIRMED,
        label="Superhero public identity",
        detection_evidence=("premise:hero",),
        source_provenance=(provenance,),
        confirmed_by_author=True,
    )
    override = contracts.AuthorOverride(
        original_value="analytical investigation",
        replacement_value="subjective uncertainty",
        rationale="Keep the reader inside the protagonist's doubt.",
        affected_dimension_ids=(dimension.dimension_id,),
        validation=contracts.OverrideValidationResult(
            preflight_result="accepted",
            final_result=None,
            valid=True,
            accepted_value="subjective uncertainty",
        ),
    )
    mapping = contracts.MappingRecord(
        mapping_id="map-1",
        source_dimension_id=dimension.dimension_id,
        source_category=dimension.category,
        source_origin=dimension.origin,
        source_provenance=(provenance,),
        destination_field="story_type.subgenres",
        proposed_value="superhero",
        mapping_strength=contracts.MappingStrength.SUPPORTED_CONTRIBUTION,
        evidence_class=contracts.EvidenceClass.CURATED_COMPOSITION_RULE,
        disposition=contracts.MappingDisposition.CONTRIBUTES_TO_CANON,
        rationale="The public identity creates a setting/world contribution.",
        author_override=override,
        review_status=contracts.MappingReviewStatus.OVERRIDDEN,
    )
    composition = contracts.WorkingComposition(
        workspace_id="w1",
        composition_id="c1",
        schema_version=1,
        dimensions=(dimension,),
        tensions=(
            contracts.CompositionTension(
                tension_id="tension-1",
                dimension_ids=(dimension.dimension_id,),
                explanation="Public identity pressure competes with intimate trust.",
                affected_decision_or_contract="story_identity.relationship-pressure",
            ),
        ),
        mapping_records=(mapping,),
        unmapped_remainders=(
            contracts.UnmappedRemainder(
                remainder_id="remainder-1",
                dimension_id=dimension.dimension_id,
                text="The emotional aesthetic remains contextual.",
            ),
        ),
    )

    assert composition.dimensions[0].origin is contracts.DimensionOrigin.DETECTED_FROM_PACK
    assert composition.dimensions[0].status is contracts.DimensionStatus.CONFIRMED
    assert composition.mapping_records[0].review_status is contracts.MappingReviewStatus.OVERRIDDEN
    assert composition.mapping_records[0].author_override.validation.preflight_result == "accepted"
    assert composition.unmapped_remainders[0].remainder_id == "remainder-1"


def test_rejected_mapping_does_not_reject_source_dimension() -> None:
    dimension = contracts.WorkingDimension(
        dimension_id="relationship-lens",
        category=contracts.DimensionCategory.RELATIONSHIP_THEMATIC,
        origin=contracts.DimensionOrigin.AUTHOR_DEFINED,
        status=contracts.DimensionStatus.CONFIRMED,
        label="Relationship betrayal",
        confirmed_by_author=True,
    )
    mapping = contracts.MappingRecord(
        mapping_id="map-rejected",
        source_dimension_id=dimension.dimension_id,
        source_category=dimension.category,
        source_origin=dimension.origin,
        mapping_strength=contracts.MappingStrength.CONTEXTUAL_INFLUENCE,
        evidence_class=contracts.EvidenceClass.AUTHOR_CONFIRMED_DECISION,
        disposition=contracts.MappingDisposition.MAPS_TO_CANON,
        review_status=contracts.MappingReviewStatus.REJECTED,
        rationale="The author rejected this destination mapping only.",
    )
    composition = contracts.WorkingComposition(
        workspace_id="w1",
        composition_id="c1",
        schema_version=1,
        dimensions=(dimension,),
        mapping_records=(mapping,),
    )

    assert composition.dimensions[0].status is contracts.DimensionStatus.CONFIRMED


def test_contract_rejects_unknown_dimension_category() -> None:
    with pytest.raises(ValidationError):
        contracts.WorkingDimension.model_validate(
            {
                "dimension_id": "bad",
                "category": "NOT_A_CATEGORY",
                "origin": "AUTHOR_DEFINED",
                "status": "CONFIRMED",
                "label": "Bad category",
            }
        )
