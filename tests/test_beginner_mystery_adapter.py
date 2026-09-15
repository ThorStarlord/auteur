from __future__ import annotations

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
from auteur.beginner.guidance import BeginnerGuidance, guidance_for
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
    for reference in (ref for card in inventory.cards for ref in card.evidence_references):
        if reference.startswith("auteur.mystery.core_templates:HowdunitTemplate.phases["):
            phase = int(
                reference.removeprefix("auteur.mystery.core_templates:HowdunitTemplate.phases[").rstrip("]")
            )
            assert phase in template.phases
        elif reference.startswith("auteur.mystery.core_templates:HowdunitTemplate.options["):
            phase = int(
                reference.removeprefix("auteur.mystery.core_templates:HowdunitTemplate.options[").rstrip("]")
            )
            assert phase in template.options
        elif reference.startswith("auteur.mystery.validation:RuleSet:"):
            assert reference.removeprefix("auteur.mystery.validation:RuleSet:") in rule_ids
        else:
            pytest.fail(f"invented evidence reference: {reference}")


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
