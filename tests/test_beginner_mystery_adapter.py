from __future__ import annotations

import subprocess
import sys

import pytest
from pydantic import ValidationError

from auteur.beginner.contracts import (
    AcceptedMilestoneReference,
    DecisionStage,
    LifecycleStatus,
    RevisionRef,
    SessionEnvelope,
    StageAvailability,
    StageStatus,
    WorkingDecision,
)
from auteur.beginner.mystery_adapter import (
    QualificationCard,
    QualificationInventory,
    QualificationStage,
    mystery_qualification_inventory,
)
from auteur.beginner.guidance import (
    BeginnerGuidance,
    guidance_for,
    register_guidance_adapter,
    unregister_guidance_adapter,
)
from auteur.mystery.core_templates import HowdunitTemplate
from auteur.mystery.validation import RuleSet


def test_mystery_inventory_is_small_sealed_and_stable() -> None:
    inventory = mystery_qualification_inventory()

    assert inventory.stage_counts == {
        QualificationStage.DISCOVER: 3,
        QualificationStage.STORY_IDENTITY: 4,
        QualificationStage.STRUCTURE: 3,
    }
    assert [card.card_id for card in inventory.cards] == [
        "discover.mystery-question",
        "discover.investigation-motivation",
        "discover.inquiry-scope",
        "story-identity.protagonist-want",
        "story-identity.resistance",
        "story-identity.stakes",
        "story-identity.change",
        "structure.clue-distribution",
        "structure.solution-density",
        "structure.reveal-consequences",
    ]
    assert isinstance(inventory.cards, tuple)


def test_inventory_cards_reference_existing_mystery_subjects() -> None:
    inventory = mystery_qualification_inventory()
    template = HowdunitTemplate()
    rule_ids = {rule.rule_id for rule in RuleSet("howdunit").rules}

    assert all(card.source_subject for card in inventory.cards)
    assert any("clue" in card.source_subject.casefold() for card in inventory.cards)
    assert any("solution" in card.source_subject.casefold() for card in inventory.cards)
    assert all(card.options for card in inventory.cards)
    expected_phase_names = {
        "discover.mystery-question": {"genre_contract", "structural_forces"},
        "discover.investigation-motivation": {"structural_forces"},
        "discover.inquiry-scope": {"scope"},
        "story-identity.protagonist-want": {"structural_forces"},
        "story-identity.resistance": {"structural_forces"},
        "story-identity.stakes": {"structural_forces"},
        "story-identity.change": {"structural_forces"},
        "structure.clue-distribution": {"clue_distribution"},
        "structure.solution-density": {"solution_density"},
        "structure.reveal-consequences": {"structural_forces"},
    }
    for card in inventory.cards:
        phase_names: set[str] = set()
        supported_labels: set[str] = set()
        for reference in card.evidence_references:
            if reference.startswith("auteur.mystery.core_templates:HowdunitTemplate.phases["):
                phase = int(
                    reference.removeprefix("auteur.mystery.core_templates:HowdunitTemplate.phases[").rstrip("]")
                )
                assert phase in template.phases
                phase_names.add(template.phases[phase])
                supported_labels.update(option.label for option in template.options.get(phase, []))
            elif reference.startswith("auteur.mystery.core_templates:HowdunitTemplate.options["):
                phase = int(
                    reference.removeprefix("auteur.mystery.core_templates:HowdunitTemplate.options[").rstrip("]")
                )
                assert phase in template.options
                phase_names.add(template.phases[phase])
                supported_labels.update(option.label for option in template.options[phase])
            elif reference.startswith("auteur.mystery.validation:RuleSet:"):
                assert reference.removeprefix("auteur.mystery.validation:RuleSet:") in rule_ids
            else:
                pytest.fail(f"invented evidence reference: {reference}")
        assert phase_names == expected_phase_names[card.card_id]
        assert set(card.options) <= supported_labels
        assert card.recommendation in supported_labels


def test_guidance_includes_all_working_decisions_and_accepted_snapshot_details() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    discover = StageStatus(
        stage=DecisionStage.DISCOVER,
        lifecycle=LifecycleStatus.WORKING,
        availability=StageAvailability.AVAILABLE,
        working_decision=WorkingDecision(
            stage=DecisionStage.DISCOVER,
            question="Which truth is being hidden?",
            options=["the inheritance", "the disappearance"],
        ),
    )
    identity = StageStatus(
        stage=DecisionStage.STORY_IDENTITY,
        lifecycle=LifecycleStatus.WORKING,
        availability=StageAvailability.AVAILABLE,
        working_decision=WorkingDecision(
            stage=DecisionStage.STORY_IDENTITY,
            question="What does the investigator risk?",
            options=["reputation", "belonging"],
        ),
    )
    full_state = session.model_copy(
        update={
            "stages": {
                **session.stages,
                DecisionStage.DISCOVER: discover,
                DecisionStage.STORY_IDENTITY: identity,
            },
            "accepted_milestones": [
                AcceptedMilestoneReference(
                    milestone_id="identity-accepted",
                    revision=RevisionRef(artifact_id="identity-42", revision=7),
                    accepted_content="accepted narrative identity",
                    fingerprint="fingerprint-v7",
                )
            ],
        }
    )
    assert discover.working_decision is not None
    changed_upstream = full_state.model_copy(
        update={
            "stages": {
                **full_state.stages,
                DecisionStage.DISCOVER: discover.model_copy(
                    update={
                        "working_decision": discover.working_decision.model_copy(
                            update={"question": "Which promise must be kept?"}
                        )
                    }
                ),
            }
        }
    )
    changed_accepted = full_state.model_copy(
        update={
            "accepted_milestones": [
                full_state.accepted_milestones[0].model_copy(
                    update={"revision": RevisionRef(artifact_id="identity-43", revision=8)}
                )
            ]
        }
    )

    projected = guidance_for("structure.clue-distribution", full_state)

    assert "Which truth is being hidden?" in projected.context_summary
    assert "What does the investigator risk?" in projected.context_summary
    assert "identity-42" in projected.context_summary
    assert '"revision":7' in projected.context_summary
    assert "accepted narrative identity" in projected.context_summary
    assert "fingerprint-v7" in projected.context_summary
    assert guidance_for("structure.clue-distribution", changed_upstream) != projected
    assert guidance_for("structure.clue-distribution", changed_accepted) != projected


def test_guidance_routing_uses_an_extensible_adapter_registry() -> None:
    class StubAdapter:
        genre = "stub"

        @staticmethod
        def inventory() -> QualificationInventory:
            return mystery_qualification_inventory()

    register_guidance_adapter(StubAdapter())
    try:
        session = SessionEnvelope.new("project-1", "stub", "A test premise.")
        guidance = guidance_for("discover.mystery-question", session)
        assert guidance.card_id == "discover.mystery-question"
    finally:
        unregister_guidance_adapter("stub")


def test_guidance_for_mystery_registers_in_a_fresh_process() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from auteur.beginner.contracts import SessionEnvelope; "
            "from auteur.beginner.guidance import guidance_for; "
            "print(guidance_for('discover.mystery-question', "
            "SessionEnvelope.new('p', 'mystery', 'premise')).card_id)",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "discover.mystery-question"


def test_guidance_contains_teaching_decision_and_evidence_contract() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")

    guidance = guidance_for("discover.mystery-question", session)

    assert guidance.card_id == "discover.mystery-question"
    assert guidance.stage is QualificationStage.DISCOVER
    assert guidance.why_this_matters
    assert guidance.narrative_principle
    assert guidance.recommendation
    assert guidance.rationale
    assert guidance.alternatives
    assert guidance.tradeoffs
    assert guidance.downstream_consequences
    assert guidance.warnings_or_tensions
    assert guidance.evidence_references
    assert guidance.authority_status == "DERIVED / NOT CANON"


def test_guidance_is_deterministic_contextual_and_non_mutating() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    before = session.model_dump(mode="json")

    first = guidance_for("structure.clue-distribution", session)
    second = guidance_for("structure.clue-distribution", session)

    assert first == second
    assert "A missing heir returns home." in first.rationale
    assert session.model_dump(mode="json") == before

    progressed = session.model_copy(deep=True)
    progressed.stages[next(iter(progressed.stages))].lifecycle = LifecycleStatus.COMPLETE
    progressed_guidance = guidance_for("structure.clue-distribution", progressed)
    assert progressed_guidance.rationale != first.rationale


def test_guidance_is_independent_of_stage_mapping_insertion_order() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    reversed_stages = dict(reversed(tuple(session.stages.items())))
    reordered = session.model_copy(update={"stages": reversed_stages})

    assert guidance_for("structure.clue-distribution", reordered) == guidance_for(
        "structure.clue-distribution", session
    )


def test_context_contains_complete_canonical_session_projection() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    guidance = guidance_for("discover.mystery-question", session)
    changed = session.model_copy(
        update={
            "session_version": 4,
            "project_id": "project-2",
            "stages": {
                **session.stages,
                DecisionStage.STORY_IDENTITY: session.stages[DecisionStage.STORY_IDENTITY].model_copy(
                    update={
                        "lifecycle": LifecycleStatus.COMPLETE,
                        "availability": StageAvailability.AVAILABLE,
                    }
                ),
            },
        }
    )
    changed_guidance = guidance_for("discover.mystery-question", changed)

    assert '"schema_version":1' in guidance.context_summary
    assert '"session_version":0' in guidance.context_summary
    assert '"project_id":"project-1"' in guidance.context_summary
    for stage in DecisionStage:
        assert f'"stage":"{stage.value}"' in guidance.context_summary
    assert guidance != changed_guidance
    assert '"session_version":4' in changed_guidance.context_summary
    assert '"project_id":"project-2"' in changed_guidance.context_summary
    assert '"lifecycle":"complete"' in changed_guidance.context_summary
    assert '"availability":"available"' in changed_guidance.context_summary


def test_card_questions_options_and_consequences_are_card_specific() -> None:
    inventory = mystery_qualification_inventory()
    question_card = inventory.card("discover.mystery-question")
    want_card = inventory.card("story-identity.protagonist-want")

    assert question_card.question == "Which investigation mode should the story use?"
    assert "Solve the puzzle" not in want_card.options
    assert want_card.question == "Which want drives the protagonist beyond merely solving the case?"
    assert question_card.downstream_consequences != want_card.downstream_consequences
    session = SessionEnvelope.new("project-1", "mystery", "A premise.")
    assert guidance_for(question_card.card_id, session).downstream_consequences == question_card.downstream_consequences


def test_guidance_projects_working_decision_and_accepted_milestone_state() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    working = StageStatus(
        stage=DecisionStage.DISCOVER,
        lifecycle=LifecycleStatus.WORKING,
        availability=StageAvailability.AVAILABLE,
        working_decision=WorkingDecision(
            stage=DecisionStage.DISCOVER,
            question="Which truth is being hidden?",
            options=["the inheritance", "the disappearance"],
        ),
    )
    working_state = session.model_copy(
        update={"stages": {**session.stages, DecisionStage.DISCOVER: working}}
    )
    accepted_state = working_state.model_copy(
        update={
            "accepted_milestones": [
                AcceptedMilestoneReference(
                    milestone_id="identity-accepted",
                    revision=RevisionRef(artifact_id="identity-1", revision=1),
                )
            ]
        }
    )

    base = guidance_for("discover.mystery-question", session)
    working_guidance = guidance_for("discover.mystery-question", working_state)
    accepted_guidance = guidance_for("discover.mystery-question", accepted_state)

    assert working_guidance != base
    assert accepted_guidance != working_guidance
    assert "Which truth is being hidden?" in working_guidance.context_summary
    assert "identity-accepted" in accepted_guidance.context_summary


def test_guidance_routes_by_genre_and_rejects_unsupported_genres() -> None:
    romance = SessionEnvelope.new("project-1", "romance", "Two rivals share a secret.")

    with pytest.raises(ValueError, match="unsupported guidance genre"):
        guidance_for("discover.mystery-question", romance)


def test_guidance_contract_is_strict_and_never_canonical() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    guidance = guidance_for("discover.mystery-question", session)
    payload = guidance.model_dump(mode="python")

    with pytest.raises(ValidationError):
        BeginnerGuidance.model_validate({**payload, "stage": "discover"}, strict=True)
    with pytest.raises(ValidationError):
        BeginnerGuidance.model_validate({**payload, "alternatives": list(guidance.alternatives)}, strict=True)
    with pytest.raises(ValidationError):
        BeginnerGuidance.model_validate({**payload, "authority_status": "CANON"}, strict=True)


def test_inventory_contract_rejects_coercible_enum_and_list_fields() -> None:
    card = mystery_qualification_inventory().cards[0]
    payload = card.model_dump(mode="python")

    with pytest.raises(ValidationError):
        QualificationCard.model_validate({**payload, "stage": "discover"}, strict=True)
    with pytest.raises(ValidationError):
        QualificationCard.model_validate({**payload, "options": list(card.options)}, strict=True)
    with pytest.raises(ValidationError):
        QualificationInventory.model_validate(
            {"cards": list(mystery_qualification_inventory().cards)}, strict=True
        )


def test_guidance_rejects_unknown_card_id() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")

    with pytest.raises(KeyError, match="unknown-card"):
        guidance_for("unknown-card", session)
