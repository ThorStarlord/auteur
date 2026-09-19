from __future__ import annotations

from auteur.beginner.decision_inventory import structure_inventory_for
from auteur.beginner.guidance import QualificationInventory, QualificationStage
from auteur.beginner.mystery_adapter import MysteryGuidanceAdapter
from tests.fixtures.beginner_hybrid_mystery import (
    HYBRID_SELECTED_IDENTITY,
    app_after_direction_acceptance,
)


def test_rich_flow_does_not_require_legacy_discovery_or_identity_cards(tmp_path) -> None:
    app = app_after_direction_acceptance(tmp_path)
    session = app.session_store.load()
    inventory = structure_inventory_for(
        session=session,
        analysis=session.architecture_analysis,
        accepted_identity=HYBRID_SELECTED_IDENTITY,
    )
    assert all(card.stage is QualificationStage.STRUCTURE for card in inventory.cards)
    assert "discover.story-experience" not in {card.card_id for card in inventory.cards}
    assert not any(card.card_id.startswith("story_identity.") for card in inventory.cards)


def test_mystery_adapter_no_longer_requires_exact_3_4_3_counts() -> None:
    inventory = QualificationInventory(
        cards=tuple(
            card
            for card in MysteryGuidanceAdapter.inventory().cards
            if card.stage is QualificationStage.STRUCTURE
        )
    )
    MysteryGuidanceAdapter.validate_inventory(inventory)


def test_rich_identity_readiness_is_semantic_not_zero_card_quota(tmp_path) -> None:
    app = app_after_direction_acceptance(tmp_path)
    projection = app.projection()
    identity_nav = next(
        row for row in projection.navigator if row.stage.value == "story_identity"
    )
    assert identity_nav.total_cards == 0
    assert identity_nav.review_available is True
    assert identity_nav.ready_to_accept is True
    assert "0 of 0 decisions" not in projection.reviews[identity_nav.stage].synthesis
