from __future__ import annotations

import pytest

from auteur.beginner.contracts import LifecycleStatus, SessionEnvelope
from auteur.beginner.mystery_adapter import (
    QualificationStage,
    mystery_qualification_inventory,
)
from auteur.beginner.guidance import guidance_for


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

    assert all(card.source_subject for card in inventory.cards)
    assert any("clue" in card.source_subject.casefold() for card in inventory.cards)
    assert any("solution" in card.source_subject.casefold() for card in inventory.cards)
    assert all(card.options for card in inventory.cards)


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


def test_guidance_rejects_unknown_card_id() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")

    with pytest.raises(KeyError, match="unknown-card"):
        guidance_for("unknown-card", session)
