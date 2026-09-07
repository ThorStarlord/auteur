import pytest
from pydantic import TypeAdapter

from auteur.story_design_packs import AuthorAction, SourceFingerprint, source_fingerprint
from auteur.story_design_packs.models import DecisionCard, TutorDepth, stable_card_id
from auteur.reasoning.setup_payoff import run_setup_payoff
from auteur.story_design_packs.tutor import decision_card_from_diagnostic, decision_card_from_guidance, tutor_recommend


def test_decision_card_preserves_tutor_authority_and_evidence():
    guidance = tutor_recommend(["superhero", "hard_determinism"], decision="moral boundary")
    card = decision_card_from_guidance(guidance, source_subject="story_identity")

    assert isinstance(card, DecisionCard)
    assert card.card_id
    assert card.depth == TutorDepth.RECOMMEND
    assert card.recommendation == guidance.recommendation
    assert list(card.pack_sources) == guidance.pack_sources
    assert card.authority_status == "DERIVED / NOT CANON"
    assert card.author_actions == (
        AuthorAction.CHOOSE,
        AuthorAction.KEEP_UNRESOLVED,
        AuthorAction.REQUEST_ALTERNATIVES,
    )


def test_diagnostic_card_has_explicit_keep_and_reject_actions():
    card = DecisionCard.from_diagnostic(
        rule="setup_payoff.unresolved",
        message="A setup has no linked payoff.",
        story_context="the novel",
        repair_options=["Link a payoff", "Keep it unresolved intentionally"],
        evidence=["setup:promise-1", "revision:3"],
    )

    assert card.decision == "Resolve or intentionally preserve the finding"
    assert list(card.alternatives) == ["Link a payoff", "Keep it unresolved intentionally"]
    assert list(card.evidence) == ["setup:promise-1", "revision:3"]
    assert AuthorAction.REJECT_FINDING in card.author_actions


def test_setup_payoff_finding_becomes_a_card_without_mutating_the_finding():
    finding = run_setup_payoff(
        series={
            "book_plans": [{"book": 1}],
            "narrative_setups": [{
                "id": "promise-1",
                "book_introduced": 1,
                "expected_payoff_by_book": 1,
                "status": "unresolved",
            }],
        }
    )[0]
    original = dict(finding)
    card = decision_card_from_diagnostic(finding, story_context="the series")

    assert card.source_rule == "setup_payoff.unresolved"
    assert "link an existing payoff" in card.alternatives
    assert "setup_id=promise-1" in card.evidence
    assert finding == original


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
    assert set(TutorDepth) == set(TutorDepth(card.depth.value) for card in TutorDepth)


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
    assert dumped["author_actions"] == ["choose", "keep_unresolved", "request_alternatives"]


def test_card_construction_is_side_effect_free(tmp_path):
    card = _card()
    card.model_dump_json()
    assert not (tmp_path / "story_identity.yaml").exists()
    assert not (tmp_path / "blueprint.yaml").exists()
    assert not (tmp_path / "structure-proposal.yaml").exists()


def test_adapters_use_the_declared_semantic_identity():
    guidance = tutor_recommend(["superhero"], decision="moral boundary")
    guidance_card = decision_card_from_guidance(guidance)
    diagnostic_card = decision_card_from_diagnostic(
        {"rule": "rule-1", "message": "Review this finding.", "recommendations": ["Repair it"]}
    )
    assert guidance_card.card_id == stable_card_id(guidance_card.semantic_identity_payload())
    assert diagnostic_card.card_id == stable_card_id(diagnostic_card.semantic_identity_payload())
    assert guidance_card.with_depth(guidance_card.depth).card_id == guidance_card.card_id
