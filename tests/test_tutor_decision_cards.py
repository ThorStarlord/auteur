from auteur.story_design_packs.models import DecisionCard, TutorDepth
from auteur.reasoning.setup_payoff import run_setup_payoff
from auteur.story_design_packs.tutor import decision_card_from_diagnostic, decision_card_from_guidance, tutor_recommend


def test_decision_card_preserves_tutor_authority_and_evidence():
    guidance = tutor_recommend(["superhero", "hard_determinism"], decision="moral boundary")
    card = decision_card_from_guidance(guidance, source_subject="story_identity")

    assert isinstance(card, DecisionCard)
    assert card.card_id
    assert card.depth == TutorDepth.RECOMMEND
    assert card.recommendation == guidance.recommendation
    assert card.pack_sources == guidance.pack_sources
    assert card.authority_status == "DERIVED / NOT CANON"
    assert card.author_actions == ["choose", "keep_unresolved", "request_alternatives"]


def test_diagnostic_card_has_explicit_keep_and_reject_actions():
    card = DecisionCard.from_diagnostic(
        rule="setup_payoff.unresolved",
        message="A setup has no linked payoff.",
        story_context="the novel",
        repair_options=["Link a payoff", "Keep it unresolved intentionally"],
        evidence=["setup:promise-1", "revision:3"],
    )

    assert card.decision == "Resolve or intentionally preserve the finding"
    assert card.alternatives == ["Link a payoff", "Keep it unresolved intentionally"]
    assert card.evidence == ["setup:promise-1", "revision:3"]
    assert "reject_finding" in card.author_actions


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
