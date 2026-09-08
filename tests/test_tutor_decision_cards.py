import pytest
from pydantic import TypeAdapter

from auteur.story_design_packs import AuthorAction, SourceFingerprint, source_fingerprint
from auteur.story_design_packs.models import DecisionCard, TutorDepth, stable_card_id


def _card(**overrides):
    values = {
        "decision": "Choose the protagonist's boundary",
        "orientation": "A moral choice shapes the story's pressure.",
        "why_it_matters": "It determines what the audience expects next.",
        "craft_concept": "Moral boundary",
        "recommendation": "Make the boundary costly to cross.",
        "alternatives": ["Keep it implicit"],
        "tradeoffs": ["Less immediate clarity"],
        "beginner_trap": "Treating the boundary as decoration.",
        "downstream_consequences": ["Later choices inherit the cost."],
        "evidence": ["setup:boundary"],
        "pack_sources": [{"pack_id": "superhero", "version": "1", "content_hash": "abc"}],
        "source_rule": "boundary.rule",
    }
    values.update(overrides)
    return DecisionCard(**values)


def test_decision_card_contract_fields_and_typed_actions():
    card = _card()
    assert card.authority_status == "DERIVED / NOT CANON"
    assert card.author_actions == tuple(AuthorAction)
    assert {depth.value for depth in TutorDepth} == {
        "recommend", "explain", "teach", "challenge", "quiz"
    }
    assert set(TutorDepth) == set(TutorDepth(card.value) for card in TutorDepth)


def test_semantic_identity_is_order_independent_and_excludes_presentation_fields():
    first = _card(pack_sources=[{"pack_id": "a", "version": "1", "content_hash": "x"}, {"pack_id": "b", "version": "1", "content_hash": "y"}])
    second = _card(pack_sources=[{"pack_id": "a", "version": "1", "content_hash": "x"}, {"pack_id": "b", "version": "1", "content_hash": "y"}], depth=TutorDepth.TEACH, author_actions=[AuthorAction.REJECT_FINDING])
    assert first.card_id == second.card_id
    assert first.card_id == stable_card_id(first.semantic_identity_payload())
    assert "depth" not in first.semantic_identity_payload()
    assert "author_actions" not in first.semantic_identity_payload()


@pytest.mark.parametrize("field", ["decision", "recommendation", "evidence", "pack_sources", "source_rule"])
def test_each_semantic_representative_changes_id(field):
    original = _card()
    changed = {"evidence": ["different"]}.get(field, "different")
    if field == "pack_sources":
        changed = [{"pack_id": "other", "version": "1", "content_hash": "x"}]
    assert _card(**{field: changed}).card_id != original.card_id


def test_wrong_id_and_mutation_are_rejected_and_depth_copy_preserves_identity():
    with pytest.raises(ValueError):
        _card(card_id="0" * 16)
    card = _card()
    with pytest.raises((TypeError, ValueError)):
        card.recommendation = "changed"
    with pytest.raises((TypeError, AttributeError)):
        card.alternatives.append("changed")
    with pytest.raises((TypeError, ValueError)):
        card.pack_sources[0].pack_id = "changed"
    copy = card.with_depth(TutorDepth.TEACH)
    assert copy is not card
    assert copy.card_id == card.card_id
    assert copy.depth == TutorDepth.TEACH


def test_source_fingerprint_is_typed_stable_and_key_order_independent():
    text_hash = source_fingerprint("hello")
    assert isinstance(text_hash, str)
    assert len(text_hash) == 64
    assert TypeAdapter(SourceFingerprint).validate_python(text_hash) == text_hash
    assert source_fingerprint(b"hello") == text_hash
    assert source_fingerprint({"b": 2, "a": 1}) == source_fingerprint({"a": 1, "b": 2})
    assert source_fingerprint("hello") != source_fingerprint("goodbye")


def test_json_round_trip_exports_typed_contract():
    card = _card()
    restored = DecisionCard.model_validate_json(card.model_dump_json())
    assert restored == card
    assert restored.card_id == card.card_id
    dumped = card.model_dump(mode="json")
    assert isinstance(dumped["alternatives"], list)
    assert dumped["author_actions"] == ["choose", "keep_unresolved", "request_alternatives", "reject_finding"]


def test_card_construction_is_side_effect_free(tmp_path):
    card = _card()
    card.model_dump_json()
    assert not (tmp_path / "story_identity.yaml").exists()
    assert not (tmp_path / "blueprint.yaml").exists()
    assert not (tmp_path / "structure-proposal.yaml").exists()
